"""
Tablica mapowan obiektow GML (model danych 2021) na warstwy/style DXF
zgodne z konwencja mapy zasadniczej uzyta w pliku wzorcowym
`ex_02_MZ_DXF_500.dxf`.

Podstawa prawna: Rozporzadzenie Ministra Rozwoju, Pracy i Technologii
z dnia 23 lipca 2021 r. w sprawie bazy danych obiektow topograficznych
oraz mapy zasadniczej (modele danych EGiB / GESUT / BDOT500).

KONWENCJA NAZW WARSTW (odczytana z pliku wzorcowego):
    <KOD><[P]><_E>_<L|T>_<n>
  gdzie:
    KOD   – kod klasy obiektu, np. SUW (siec wodociagowa), EGBB (budynki),
            OTK (komunikacja BDOT500) itd.
    P     – (opcjonalnie) wariant "przewod" dla sieci GESUT, np. SUWP
    E     – (opcjonalnie) etykieta (E_T)
    L|T   – L = geometria liniowa/punktowa, T = tekst
    n     – indeks podwarstwy (priorytet rysowania)
  Warstwy specjalne: Dzialki, Kontury, Punkty, Numery_dzialek,
    Numery_punktow, Numery_konturow.

KOLORY ACI – odczytane bezposrednio z pliku wzorcowego tam, gdzie to mozliwe:
    SUW=5(nieb.) SUE=1(czerw.) SUG=52(oliwka) SUK=36(braz)
    SUC=212 SUT=30(pomar.) EGB*=7(czern) Kontury=96

OZNACZENIA PEWNOSCI w komentarzach:
    [WZORZEC] – kolor/warstwa potwierdzone w pliku ex_02_MZ_DXF_500.dxf
    [ZALOZENIE] – rozwiniecie/dobor przyjety logicznie, do weryfikacji
"""

from dataclasses import dataclass


class ACI:
    """AutoCAD Color Index – wartosci uzyte w pliku wzorcowym."""
    RED = 1          # elektroenergetyka (SUE)
    BLUE = 5         # wodociag (SUW)
    BLACK = 7        # EGiB, BDOT500 (czern na bialym tle)
    NEG_BLACK = -7   # warstwa czarna wylaczona domyslnie (jak we wzorcu)
    OLIVE = 52       # gaz (SUG)
    BROWN = 36       # kanalizacja (SUK)
    CYAN_C = 212     # cieplo (SUC)
    ORANGE = 30      # telekomunikacja (SUT)
    GREEN_K = 96     # kontury/uzytki (Kontury)
    GRAY = 250       # warstwa 0


@dataclass
class Style:
    layer: str                     # nazwa warstwy DXF (wg konwencji MZ)
    color: int = ACI.BLACK
    linetype: str = "CONTINUOUS"
    symbol: str | None = None      # kod bloku symbolu punktowego
    text_layer: str | None = None  # warstwa dla opisu tekstowego
    text_height: float = 1.26      # wys. tekstu wg wzorca (skala 1:500)
    description: str = ""


DEFAULT_STYLE = Style(
    layer="OPISOD_T_0", color=ACI.BLACK,
    description="[ZALOZENIE] Obiekt bez zdefiniowanego mapowania")


# ---------------------------------------------------------------------------
# GESUT – sieci uzbrojenia terenu.
# Wzorzec uzywa wariantu "P" (przewod) jako glownej warstwy liniowej: SUWP_L_0.
# Kolory [WZORZEC].
# ---------------------------------------------------------------------------
_GESUT = {
    "SUW": (ACI.BLUE,    "3_SUWP",   "wodociagowa"),       # [WZORZEC]
    "SUE": (ACI.RED,     "3_SUEP_A", "elektroenergetyczna"),  # [WZORZEC]
    "SUG": (ACI.OLIVE,   "3_SUGP",   "gazowa"),            # [WZORZEC]
    "SUK": (ACI.BROWN,   "3_SUKP",   "kanalizacyjna"),     # [WZORZEC]
    "SUC": (ACI.CYAN_C,  "3_SUCP",   "cieplownicza"),      # [WZORZEC kolor]
    "SUT": (ACI.ORANGE,  "3_SUTP_A", "telekomunikacyjna"),  # [WZORZEC]
    "SUN": (ACI.BLACK,   None,       "niezidentyfikowana"),  # [ZALOZENIE]
    "SUS": (ACI.BLACK,   None,       "specjalna"),         # [ZALOZENIE]
    "SUL": (ACI.BLACK,   None,       "inna (naftowa)"),    # [ZALOZENIE]
}


def _gesut_line(code: str) -> Style:
    color, linetype, _ = _GESUT[code]
    return Style(
        layer=f"{code}P_L_0", color=color,
        linetype=linetype if linetype else "CONTINUOUS",
        text_layer=f"{code}P_E_T_0",
        description=f"[WZORZEC] GESUT – siec {_GESUT[code][2]} (przewod)")


def _gesut_device(code: str, block: str) -> Style:
    color = _GESUT[code][0]
    return Style(
        layer=f"{code}_L_0", color=color, symbol=block,
        text_layer=f"{code}_E_T_0",
        description=f"GESUT – urzadzenie sieci {_GESUT[code][2]}")


MAPPING: dict[str, Style] = {}

# --- GESUT: przewody (linie) ----------------------------------------------
MAPPING["GES_PrzewodWodociagowy"] = _gesut_line("SUW")
MAPPING["GES_PrzewodElektroenergetyczny"] = _gesut_line("SUE")
MAPPING["GES_PrzewodGazowy"] = _gesut_line("SUG")
MAPPING["GES_PrzewodKanalizacyjny"] = _gesut_line("SUK")
MAPPING["GES_PrzewodCieplowniczy"] = _gesut_line("SUC")
MAPPING["GES_PrzewodTelekomunikacyjny"] = _gesut_line("SUT")
MAPPING["GES_PrzewodNiezidentyfikowany"] = _gesut_line("SUN")
MAPPING["GES_PrzewodSpecjalny"] = _gesut_line("SUS")

# --- GESUT: urzadzenia / armatura (punkty, bloki) -------------------------
# Kody blokow [WZORZEC]: 3_SUWW (studnia wod.), 3_SUES (slup/stacja elektr.),
# 3_SUKS (studnia kanaliz.), 3_SUGS (urzadzenie gaz.) itd.
MAPPING["GES_Wezel"] = _gesut_device("SUW", "3_SUWW")
MAPPING["GES_SzczegolTechniczny"] = _gesut_device("SUE", "3_SUES")
MAPPING["GES_UrzadzenieWodne"] = _gesut_device("SUW", "3_SUWW")
MAPPING["GES_UrzadzenieKanalizacyjne"] = _gesut_device("SUK", "3_SUKS")

# ---------------------------------------------------------------------------
# EGiB – ewidencja gruntow i budynkow.
# Wzorzec: EGBB (budynki, L_0), EGBE (dzialki/granice), warstwy pomocnicze
# Dzialki (ltype GDE) i Kontury (ltype GUK), Numery_* dla opisow.
# Kolory [WZORZEC] = 7 (czern), Kontury = 96.
# ---------------------------------------------------------------------------
MAPPING["EGB_Budynek"] = Style(
    layer="EGBB_L_0", color=ACI.BLACK, linetype="2_EGBU_A",
    text_layer="EGBB_E_T_0",
    description="[WZORZEC] EGiB – kontur budynku")

MAPPING["EGB_DzialkaEwidencyjna"] = Style(
    layer="Dzialki", color=ACI.BLACK, linetype="GDE",
    text_layer="Numery_dzialek",
    description="[WZORZEC] EGiB – granica dzialki ewidencyjnej")

MAPPING["EGB_KonturUzytkuGruntowego"] = Style(
    layer="Kontury", color=ACI.GREEN_K, linetype="GUK",
    text_layer="Numery_konturow",
    description="[WZORZEC] EGiB – kontur uzytku gruntowego")

MAPPING["EGB_KonturKlasyfikacyjny"] = Style(
    layer="Kontury", color=ACI.GREEN_K, linetype="GUK",
    text_layer="Numery_konturow",
    description="[ZALOZENIE] EGiB – kontur klasyfikacyjny")

MAPPING["EGB_PunktGraniczny"] = Style(
    layer="Punkty", color=ACI.BLACK, symbol="2_EGBP12_01",
    text_layer="Numery_punktow",
    description="[WZORZEC] EGiB – punkt graniczny")

# ---------------------------------------------------------------------------
# BDOT500 – obiekty topograficzne.
# Kody OT** z wzorca: OTB* (budowle), OTK/OTD (komunikacja), OTO (ogrodzenia),
# OTW (wody), OTZ (zielen/pokrycie), OTR (rzezba), OTS (szczegoly).
# Kolory [WZORZEC] = 7, OTW=141, OTZ=96.
# ---------------------------------------------------------------------------
MAPPING["OT_BUBD_A"] = Style(
    layer="OTBB_L_0", color=ACI.BLACK,
    text_layer="OTBB_E_T_0",
    description="[WZORZEC] BDOT500 – budowla (powierzchnia)")

MAPPING["OT_SKBU_L"] = Style(
    layer="OTO_L_0", color=ACI.BLACK,
    description="[WZORZEC] BDOT500 – ogrodzenie / mur")

MAPPING["OT_SKJD_L"] = Style(
    layer="OTK_L_0", color=ACI.BLACK, linetype="1_OTKJ",
    text_layer="OTK_E_T_0",
    description="[WZORZEC] BDOT500 – krawedz jezdni (komunikacja)")

MAPPING["OT_PTWP_A"] = Style(
    layer="OTW_L_0", color=141,
    text_layer="OTW_E_T_0",
    description="[WZORZEC] BDOT500 – wody powierzchniowe")

MAPPING["OT_PTZB_A"] = Style(
    layer="OTZ_L_0", color=ACI.GREEN_K, linetype="1_OTZZ",
    text_layer="OTZ_E_T_0",
    description="[WZORZEC] BDOT500 – pokrycie terenu / zielen")

MAPPING["OT_RTPW_P"] = Style(
    layer="OTZ_L_0", color=ACI.GREEN_K, symbol="1_OTZL",
    description="[WZORZEC] BDOT500 – drzewo / roslinnosc (punkt)")

MAPPING["OT_SURT_P"] = Style(
    layer="OTS_L_0", color=ACI.BLACK, symbol="1_OTRN",
    description="[WZORZEC] BDOT500 – urzadzenie / szczegol terenowy")

# ---------------------------------------------------------------------------
# Osnowa geodezyjna – brak dedykowanej warstwy w tym wzorcu;
# mapujemy na warstwe punktow pomiarowych.
# ---------------------------------------------------------------------------
MAPPING["OSG_PunktOsnowy"] = Style(
    layer="Punkty", color=ACI.BLACK, symbol="2_EGBP12_01",
    text_layer="Numery_punktow",
    description="[ZALOZENIE] Punkt osnowy geodezyjnej")


# Dopasowanie przyblizone po slowach kluczowych (gdy brak trafienia dokladnego)
KEYWORD_RULES: list[tuple[str, str]] = [
    ("budynek", "EGB_Budynek"),
    ("dzialka", "EGB_DzialkaEwidencyjna"),
    ("dzialki", "EGB_DzialkaEwidencyjna"),
    ("klasyfik", "EGB_KonturKlasyfikacyjny"),
    ("uzyt", "EGB_KonturUzytkuGruntowego"),
    ("graniczn", "EGB_PunktGraniczny"),
    ("wodoci", "GES_PrzewodWodociagowy"),
    ("kanali", "GES_PrzewodKanalizacyjny"),
    ("gazow", "GES_PrzewodGazowy"),
    ("gaz", "GES_PrzewodGazowy"),
    ("elektro", "GES_PrzewodElektroenergetyczny"),
    ("cieplo", "GES_PrzewodCieplowniczy"),
    ("ciepln", "GES_PrzewodCieplowniczy"),
    ("telekom", "GES_PrzewodTelekomunikacyjny"),
    ("wezel", "GES_Wezel"),
    ("osnow", "OSG_PunktOsnowy"),
    ("ogrodz", "OT_SKBU_L"),
    ("jezdni", "OT_SKJD_L"),
    ("droga", "OT_SKJD_L"),
    ("drzewo", "OT_RTPW_P"),
    ("roslin", "OT_RTPW_P"),
    ("wod", "OT_PTWP_A"),
]


def resolve(local_name: str) -> Style:
    """Zwraca styl dla lokalnej nazwy typu obiektu GML.

    1) trafienie dokladne, 2) slowo kluczowe, 3) styl domyslny.
    """
    if local_name in MAPPING:
        return MAPPING[local_name]
    low = local_name.lower()
    for keyword, key in KEYWORD_RULES:
        if keyword in low:
            return MAPPING[key]
    return DEFAULT_STYLE


# Typy linii uzywane przez style – do zdefiniowania w dokumencie DXF.
# Odwzorowane uproszczone wzory (pelne wzory wg zalacznika do rozporzadzenia).
REQUIRED_LINETYPES: dict[str, list[float]] = {
    "3_SUWP":   [1.0, 0.7, -0.3],
    "3_SUEP_A": [1.0, 0.7, -0.3],
    "3_SUGP":   [1.0, 0.7, -0.3],
    "3_SUKP":   [1.0, 0.7, -0.3],
    "3_SUCP":   [1.0, 0.7, -0.3],
    "3_SUTP_A": [1.0, 0.7, -0.3],
    "2_EGBU_A": [0.0],                 # ciagla (budynek)
    "GDE":      [1.2, 0.8, -0.2, 0.0, -0.2],   # granica dzialki (kreska-kropka)
    "GUK":      [0.8, 0.5, -0.3],      # kontur uzytku (kreskowa)
    "1_OTKJ":   [0.0],
    "1_OTZZ":   [0.6, 0.4, -0.2],
}


def all_styles() -> list[Style]:
    """Unikalne style wg warstwy – do utworzenia warstw w dokumencie."""
    seen: dict[str, Style] = {}
    for st in list(MAPPING.values()) + [DEFAULT_STYLE]:
        seen.setdefault(st.layer, st)
        # dodaj tez warstwy tekstowe jako osobne wpisy
        if st.text_layer and st.text_layer not in seen:
            seen[st.text_layer] = Style(
                layer=st.text_layer, color=st.color,
                description="warstwa opisu (tekst)")
    return list(seen.values())


def required_linetypes() -> dict[str, list[float]]:
    return dict(REQUIRED_LINETYPES)
