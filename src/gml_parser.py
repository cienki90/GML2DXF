"""
Parser GML dla danych mapy zasadniczej (EGiB / GESUT / BDOT500).

Obsluguje typowe geometrie GML 3.x spotykane w eksportach GUGiK:
  gml:Point           -> punkt
  gml:LineString      -> linia lamana
  gml:Curve           -> linia (segmenty LineStringSegment)
  gml:Polygon         -> poligon z obwiednia zewnetrzna i wewnetrznymi
  gml:Surface         -> poligon (PolygonPatch)
  gml:MultiPoint / MultiCurve / MultiSurface -> kolekcje powyzszych

Zakladany porzadek wspolrzednych w GML GUGiK: "X Y" gdzie
X = polnoc (northing), Y = wschod (easting) -- zgodnie z PL-2000/PL-1992.
Konwersja do ukladu DXF (east, north) nastepuje dopiero w zapisie.
"""

from dataclasses import dataclass, field
from lxml import etree


# Przestrzenie nazw GML (obie wersje spotykane w praktyce)
GML_NS = {"http://www.opengis.net/gml/3.2", "http://www.opengis.net/gml"}


@dataclass
class Geometry:
    """Uproszczona reprezentacja geometrii niezalezna od zrodla."""
    kind: str                                  # point | line | polygon
    # dla point: [(x, y)]; line: [(x,y), ...]; polygon: lista pierscieni
    coords: list = field(default_factory=list)
    rings: list = field(default_factory=list)  # tylko dla polygon


@dataclass
class Feature:
    """Pojedynczy obiekt mapy: typ + geometrie + atrybuty opisowe."""
    local_name: str
    geometries: list[Geometry] = field(default_factory=list)
    attributes: dict = field(default_factory=dict)


def _local(tag: str) -> str:
    """Zwraca nazwe lokalna elementu bez przestrzeni nazw."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _ns(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def _is_gml(tag: str) -> bool:
    return _ns(tag) in GML_NS


def _parse_poslist(text: str) -> list[tuple[float, float]]:
    """Parsuje gml:posList / gml:pos: ciag liczb 'X Y X Y ...'."""
    nums = [float(v) for v in text.replace(",", " ").split()]
    return [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]


def _parse_coordinates(text: str) -> list[tuple[float, float]]:
    """Parsuje stary gml:coordinates: 'X,Y X,Y' (separator ts/cs domyslny)."""
    pts = []
    for token in text.split():
        parts = token.split(",")
        if len(parts) >= 2:
            pts.append((float(parts[0]), float(parts[1])))
    return pts


def _extract_points(elem) -> list[tuple[float, float]]:
    """Zbiera wspolrzedne z elementu geometrii (posList/pos/coordinates)."""
    pts: list[tuple[float, float]] = []
    for node in elem.iter():
        name = _local(node.tag)
        if not node.text or not node.text.strip():
            continue
        if name in ("posList", "coordinates"):
            if name == "posList":
                pts.extend(_parse_poslist(node.text))
            else:
                pts.extend(_parse_coordinates(node.text))
        elif name == "pos":
            pts.extend(_parse_poslist(node.text))
    return pts


def _parse_geometry(geom_elem) -> list[Geometry]:
    """Rozpoznaje typ geometrii GML i buduje obiekty Geometry."""
    name = _local(geom_elem.tag)
    out: list[Geometry] = []

    if name in ("Point",):
        pts = _extract_points(geom_elem)
        if pts:
            out.append(Geometry(kind="point", coords=pts[:1]))

    elif name in ("LineString", "Curve", "LineStringSegment"):
        pts = _extract_points(geom_elem)
        if len(pts) >= 2:
            out.append(Geometry(kind="line", coords=pts))

    elif name in ("Polygon", "Surface", "PolygonPatch"):
        rings: list[list[tuple[float, float]]] = []
        for ring in geom_elem.iter():
            rname = _local(ring.tag)
            if rname in ("exterior", "interior", "LinearRing"):
                if rname == "LinearRing":
                    pts = _extract_points(ring)
                    if len(pts) >= 3:
                        rings.append(pts)
        if rings:
            out.append(Geometry(kind="polygon", rings=rings))

    # Kolekcje: zejdz rekurencyjnie po dzieciach bedacych geometriami GML
    elif name in ("MultiPoint", "MultiCurve", "MultiSurface",
                  "MultiGeometry", "MultiLineString", "MultiPolygon"):
        for child in geom_elem.iter():
            if child is geom_elem:
                continue
            cname = _local(child.tag)
            if _is_gml(child.tag) and cname in (
                    "Point", "LineString", "Curve", "Polygon", "Surface"):
                out.extend(_parse_geometry(child))

    return out


def _collect_attributes(feature_elem) -> dict:
    """Zbiera proste atrybuty tekstowe obiektu (elementy lisciaste, nie-GML)."""
    attrs: dict = {}
    for node in feature_elem.iter():
        if _is_gml(node.tag):
            continue
        if len(node) == 0 and node.text and node.text.strip():
            attrs[_local(node.tag)] = node.text.strip()
    return attrs


def _find_geometries(feature_elem) -> list[Geometry]:
    """Znajduje wszystkie geometrie GML wewnatrz obiektu."""
    geoms: list[Geometry] = []
    top_kinds = ("Point", "LineString", "Curve", "Polygon", "Surface",
                 "MultiPoint", "MultiCurve", "MultiSurface",
                 "MultiGeometry", "MultiLineString", "MultiPolygon")
    for node in feature_elem.iter():
        if _is_gml(node.tag) and _local(node.tag) in top_kinds:
            geoms.extend(_parse_geometry(node))
    return geoms


def parse(path: str) -> list[Feature]:
    """Parsuje plik GML i zwraca liste obiektow (Feature).

    Obiektem jest kazdy element poza przestrzenia GML, ktory zawiera
    co najmniej jedna geometrie GML. Elementy opakowujace (featureMember,
    FeatureCollection) sa pomijane jako takie, ale ich dzieci sa badane.
    """
    tree = etree.parse(path)
    root = tree.getroot()

    features: list[Feature] = []
    skip_names = {"FeatureCollection", "featureMember", "featureMembers",
                  "member", "boundedBy"}

    # Kandydaci na obiekty: elementy nie-GML. Aby uniknac zagniezdzen,
    # obiektem jest najplytszy nie-GML element zawierajacy geometrie,
    # ktorego zaden nie-GML przodek takze nie jest obiektem.
    claimed: set = set()

    for elem in root.iter():
        if _is_gml(elem.tag):
            continue
        if _local(elem.tag) in skip_names:
            continue
        # czy ktorys przodek jest juz obiektem?
        anc = elem.getparent()
        is_nested = False
        while anc is not None:
            if anc in claimed:
                is_nested = True
                break
            anc = anc.getparent()
        if is_nested:
            continue

        geoms = _find_geometries(elem)
        if not geoms:
            continue

        claimed.add(elem)
        features.append(Feature(
            local_name=_local(elem.tag),
            geometries=geoms,
            attributes=_collect_attributes(elem),
        ))

    return features
