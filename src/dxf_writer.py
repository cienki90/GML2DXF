"""
Generator DXF dla mapy zasadniczej (konwencja wg pliku wzorcowego
ex_02_MZ_DXF_500.dxf).

Buduje rysunek DXF (R2010) z:
  - warstwami wg konwencji MZ (KOD[_P]_[E_]L|T_n, oraz Dzialki/Kontury/...),
  - typami linii zdefiniowanymi w mapping.required_linetypes(),
  - blokami symboli punktowych (kody wg wzorca: 3_SUWW, 2_EGBP12_01, ...),
  - geometriami (punkty->INSERT bloku, linie->LWPOLYLINE, poligony->zamkniete
    LWPOLYLINE), opisami tekstowymi na warstwach *_E_T_* / Numery_*.

Uklad: GML (X=north, Y=east) -> DXF (east, north). Wspolrzedne 1:1.
"""

import math
import os
import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons import Importer

from mapping import resolve, all_styles, required_linetypes, Style
from gml_parser import Feature

# Domyslna sciezka do pliku wzorcowego z definicjami blokow (biblioteka symboli)
DEFAULT_SYMBOL_LIBRARY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ex_02_MZ_DXF_500.dxf",
)


def _to_dxf(pt: tuple[float, float]) -> tuple[float, float]:
    """Zamiana (X=north, Y=east) z GML na (east, north) dla DXF."""
    x_gml, y_gml = pt
    return (y_gml, x_gml)


def _ensure_linetypes(doc) -> None:
    for name, pattern in required_linetypes().items():
        if name in doc.linetypes:
            continue
        # wzor ciagly ([0.0]) -> pomijamy, uzyjemy CONTINUOUS
        if pattern == [0.0]:
            continue
        try:
            doc.linetypes.add(name, pattern=pattern, description=name)
        except Exception:
            pass  # nie blokuj konwersji z powodu nietypowego wzoru


def _ensure_layers(doc, styles: list[Style]) -> None:
    for st in styles:
        if st.layer in doc.layers:
            continue
        attribs = {"color": abs(st.color) if st.color else 7}
        lt = st.linetype
        if lt and lt != "CONTINUOUS" and lt in doc.linetypes:
            attribs["linetype"] = lt
        doc.layers.add(st.layer, **attribs)


def _import_symbol_blocks(doc, symbols: set[str], library_path: str) -> set[str]:
    """Importuje dokladne definicje blokow z pliku wzorcowego (biblioteki).

    Zwraca zbior nazw blokow, ktore udalo sie zaimportowac. Pozostale (brak
    w bibliotece lub brak pliku) obsluguje fallback z uproszczonymi ksztaltami.
    """
    imported: set[str] = set()
    if not library_path or not os.path.isfile(library_path):
        return imported
    try:
        ref = ezdxf.readfile(library_path)
    except Exception:
        return imported

    available = {name for name in symbols
                 if name and name in ref.blocks and name not in doc.blocks}
    if not available:
        return imported
    try:
        imp = Importer(ref, doc)
        imp.import_blocks(sorted(available))
        imp.finalize()
        imported = {n for n in available if n in doc.blocks}
    except Exception:
        pass
    return imported


def _build_symbol_blocks(doc, symbols: set[str]) -> None:
    """Tworzy uproszczone definicje blokow (fallback) dla podanych symboli.

    Uzywane tylko dla blokow niedostepnych w bibliotece wzorcowej.
    Rozmiar bazowy w metrach (skala projektowa 1:1).
    """
    s = 0.4  # polowa rozmiaru symbolu w metrach

    def circle(name, r=s):
        if name not in doc.blocks:
            doc.blocks.new(name).add_circle((0, 0), r)

    def square(name, a=s):
        if name not in doc.blocks:
            doc.blocks.new(name).add_lwpolyline(
                [(-a, -a), (a, -a), (a, a), (-a, a)], close=True)

    def cross(name, a=s):
        if name not in doc.blocks:
            b = doc.blocks.new(name)
            b.add_line((-a, 0), (a, 0)); b.add_line((0, -a), (0, a))

    def triangle(name, a=s):
        if name not in doc.blocks:
            h = a * math.sqrt(3)
            doc.blocks.new(name).add_lwpolyline(
                [(-a, -h / 3), (a, -h / 3), (0, 2 * h / 3)], close=True)

    # Dobor ksztaltu po charakterze kodu; nieznane -> kwadrat
    for name in symbols:
        if not name:
            continue
        up = name.upper()
        if "EGBP" in up:          # punkt graniczny EGiB
            cross(name)
        elif up.endswith("W") or "SUWW" in up:  # studnia wodociagowa
            circle(name)
        elif "SUES" in up or "SUE" in up:        # elektro
            triangle(name)
        elif "SUKS" in up or "SUK" in up:        # kanaliz. studnia
            circle(name)
        elif "OTZL" in up:        # drzewo
            circle(name, s * 1.1)
        else:
            square(name)


def _write_feature(msp, feat: Feature, label_attr: str | None) -> int:
    style = resolve(feat.local_name)
    drawn = 0

    for geom in feat.geometries:
        if geom.kind == "point":
            x, y = _to_dxf(geom.coords[0])
            if style.symbol:
                msp.add_blockref(style.symbol, (x, y),
                                 dxfattribs={"layer": style.layer})
            else:
                msp.add_point((x, y), dxfattribs={"layer": style.layer})
            drawn += 1
        elif geom.kind == "line":
            pts = [_to_dxf(p) for p in geom.coords]
            msp.add_lwpolyline(pts, dxfattribs={"layer": style.layer})
            drawn += 1
        elif geom.kind == "polygon":
            for ring in geom.rings:
                pts = [_to_dxf(p) for p in ring]
                msp.add_lwpolyline(pts, close=True,
                                   dxfattribs={"layer": style.layer})
                drawn += 1

    if label_attr and label_attr in feat.attributes:
        anchor = _label_anchor(feat)
        if anchor:
            tlayer = style.text_layer or style.layer
            msp.add_text(
                feat.attributes[label_attr],
                dxfattribs={"layer": tlayer, "height": style.text_height},
            ).set_placement(anchor, align=TextEntityAlignment.MIDDLE_CENTER)
            drawn += 1
    return drawn


def _label_anchor(feat: Feature) -> tuple[float, float] | None:
    for geom in feat.geometries:
        if geom.kind == "point":
            return _to_dxf(geom.coords[0])
        if geom.kind == "line" and geom.coords:
            return _to_dxf(geom.coords[len(geom.coords) // 2])
        if geom.kind == "polygon" and geom.rings:
            ring = geom.rings[0]
            cx = sum(p[0] for p in ring) / len(ring)
            cy = sum(p[1] for p in ring) / len(ring)
            return _to_dxf((cx, cy))
    return None


def write(features: list[Feature], out_path: str,
          label_attr: str | None = None,
          symbol_library: str | None = DEFAULT_SYMBOL_LIBRARY) -> dict:
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 6  # metry
    msp = doc.modelspace()

    _ensure_linetypes(doc)
    styles = all_styles()
    _ensure_layers(doc, styles)

    symbols = {st.symbol for st in styles if st.symbol}
    # 1) Zaimportuj dokladne definicje blokow z pliku wzorcowego (jesli jest).
    imported = _import_symbol_blocks(doc, symbols, symbol_library or "")
    # 2) Dla pozostalych symboli utworz uproszczony ksztalt (fallback).
    _build_symbol_blocks(doc, symbols - imported)

    stats = {"features": 0, "entities": 0, "layers": {}, "unmapped": 0,
             "symbols_imported": len(imported),
             "symbols_fallback": len(symbols - imported)}
    for feat in features:
        style = resolve(feat.local_name)
        if style.layer == "OPISOD_T_0":
            stats["unmapped"] += 1
        n = _write_feature(msp, feat, label_attr)
        stats["features"] += 1
        stats["entities"] += n
        stats["layers"][style.layer] = stats["layers"].get(style.layer, 0) + 1

    doc.saveas(out_path)
    return stats
