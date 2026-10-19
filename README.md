# GML2DXF — konwerter GML → DXF (polska mapa zasadnicza)

Konwerter danych **GML** (model danych 2021: **EGiB**, **GESUT**, **BDOT500**)
do formatu **DXF**, z zachowaniem konwencji redakcyjnych mapy zasadniczej:
nazwy warstw, kolory branżowe, typy linii i bloki symboli.

Konwencja warstw/kolorów/linii została wyprowadzona z pliku wzorcowego
[`ex_02_MZ_DXF_500.dxf`](ex_02_MZ_DXF_500.dxf) oraz z **Rozporządzenia Ministra
Rozwoju, Pracy i Technologii z dnia 23 lipca 2021 r. w sprawie bazy danych
obiektów topograficznych oraz mapy zasadniczej**.

## Struktura repozytorium

| Ścieżka | Rola |
|---------|------|
| `src/gml2dxf.py`    | interfejs wiersza poleceń (CLI) |
| `src/gml_parser.py` | parser GML → obiekty `Feature` z geometriami i atrybutami |
| `src/mapping.py`    | tablica mapowań: typ obiektu GML → warstwa, kolor, linia, symbol |
| `src/dxf_writer.py` | generator DXF: warstwy, bloki, zapis geometrii |
| `examples/przyklad.gml` | przykładowy GML (EGiB + GESUT + BDOT500 + osnowa) |
| `ex_02_MZ_DXF_500.dxf`  | **plik wzorcowy** mapy zasadniczej (źródło konwencji) |

## Instalacja

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Użycie

```bash
# Konwersja (wyjście obok wejścia)
python src/gml2dxf.py examples/przyklad.gml

# Własna nazwa pliku wyjściowego
python src/gml2dxf.py examples/przyklad.gml -o wynik.dxf

# Dodanie opisów tekstowych z atrybutu (np. numer działki)
python src/gml2dxf.py examples/przyklad.gml --label numerDzialki

# Podgląd tablicy mapowań
python src/gml2dxf.py --list-mapping
```

## Konwencja odwzorowana z pliku wzorcowego

**Nazwy warstw:** `<KOD>[P]_[E_]<L|T>_<n>` oraz warstwy specjalne
(`Dzialki`, `Kontury`, `Punkty`, `Numery_dzialek`, …).

**Kolory ACI (potwierdzone we wzorcu):**

| Branża / klasa | Warstwa | Kolor ACI |
|---|---|---|
| Wodociąg (GESUT) | `SUWP_L_0` | 5 (niebieski) |
| Elektroenergetyka | `SUEP_L_0` | 1 (czerwony) |
| Gaz | `SUGP_L_0` | 52 (oliwka) |
| Kanalizacja | `SUKP_L_0` | 36 (brąz) |
| Ciepłownictwo | `SUCP_L_0` | 212 |
| Telekomunikacja | `SUTP_L_0` | 30 (pomarańcz) |
| EGiB budynki | `EGBB_L_0` | 7 (czerń) |
| Działki | `Dzialki` | 7, linetyp `GDE` |
| Kontury użytków | `Kontury` | 96, linetyp `GUK` |

## Układ współrzędnych

GML podaje `X=northing, Y=easting` (PL-2000/PL-1992); konwerter zamienia
kolejność na `(easting, northing)` wymaganą przez DXF. Współrzędne przepisywane
1:1 (bez transformacji między układami). Jednostki rysunku = metry.

## Dostosowanie

Cała semantyka redakcyjna jest w `src/mapping.py`. W komentarzach oznaczono:
- `[WZORZEC]` — kolor/warstwa potwierdzone w pliku wzorcowym,
- `[ZALOZENIE]` — rozwinięcie przyjęte logicznie, do weryfikacji.

## Znane ograniczenia / dalsze kroki

- **Symbole punktowe** mają na razie uproszczone kształty pod poprawnymi kodami
  bloków (np. `3_SUWW`, `2_EGBP12_01`). Docelowo można wstawić dokładne
  definicje bloków skopiowane z pliku wzorcowego.
- Brak transformacji między układami (PL-2000 ↔ PL-1992) — do dodania w razie
  potrzeby (np. przez `pyproj`).
- Wzory typów linii są uproszczone; pełne wzory wg załącznika do rozporządzenia.
