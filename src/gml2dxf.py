#!/usr/bin/env python3
"""
gml2dxf – konwerter GML (mapa zasadnicza: EGiB / GESUT / BDOT500) do DXF
z zachowaniem polskich standardow redakcji mapy (warstwy, kolory, symbole).

Uzycie:
    python gml2dxf.py wejscie.gml -o wyjscie.dxf
    python gml2dxf.py wejscie.gml --label numerDzialki
    python gml2dxf.py wejscie.gml --list-mapping

Autor: szkielet do dalszej rozbudowy wg konkretnego rozporzadzenia.
"""

import argparse
import os
import sys

from gml_parser import parse
from dxf_writer import write, DEFAULT_SYMBOL_LIBRARY
from mapping import MAPPING, DEFAULT_STYLE


def cmd_list_mapping() -> None:
    print("Zdefiniowane mapowania typ obiektu GML -> warstwa DXF:\n")
    print(f"  {'TYP GML':<34} {'WARSTWA DXF':<22} {'KOLOR':>5}  OPIS")
    print("  " + "-" * 88)
    for name, st in MAPPING.items():
        print(f"  {name:<34} {st.layer:<16} {st.color:>5}  {st.description}")
    print(f"\n  {'(domyslny)':<34} {DEFAULT_STYLE.layer:<16} "
          f"{DEFAULT_STYLE.color:>5}  {DEFAULT_STYLE.description}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Konwersja GML (mapa zasadnicza) -> DXF.")
    ap.add_argument("input", nargs="?", help="plik wejsciowy GML")
    ap.add_argument("-o", "--output", help="plik wyjsciowy DXF")
    ap.add_argument("--label", metavar="ATRYBUT",
                    help="nazwa atrybutu obiektu uzywana jako opis tekstowy")
    ap.add_argument("--list-mapping", action="store_true",
                    help="wypisz tablice mapowan i zakoncz")
    ap.add_argument("--symbol-library", metavar="DXF",
                    help="sciezka do pliku wzorcowego z definicjami blokow "
                         "(domyslnie ex_02_MZ_DXF_500.dxf w repo)")
    ap.add_argument("--no-symbol-library", action="store_true",
                    help="nie importuj blokow z wzorca; uzyj uproszczonych "
                         "ksztaltow zastepczych")
    args = ap.parse_args(argv)

    if args.list_mapping:
        cmd_list_mapping()
        return 0

    if not args.input:
        ap.error("brak pliku wejsciowego GML")
    if not os.path.isfile(args.input):
        print(f"Blad: plik nie istnieje: {args.input}", file=sys.stderr)
        return 2

    out = args.output or os.path.splitext(args.input)[0] + ".dxf"

    print(f"Wczytywanie GML: {args.input}")
    features = parse(args.input)
    print(f"  rozpoznano obiektow: {len(features)}")

    if not features:
        print("Ostrzezenie: nie znaleziono zadnych obiektow z geometria.",
              file=sys.stderr)

    if args.no_symbol_library:
        library = None
    else:
        library = args.symbol_library or DEFAULT_SYMBOL_LIBRARY

    print(f"Zapis DXF: {out}")
    stats = write(features, out, label_attr=args.label, symbol_library=library)

    print("\nPodsumowanie konwersji")
    print("  " + "-" * 40)
    print(f"  obiekty:          {stats['features']}")
    print(f"  encje DXF:        {stats['entities']}")
    print(f"  bez mapowania:    {stats['unmapped']}")
    print(f"  bloki z wzorca:   {stats['symbols_imported']}")
    print(f"  bloki zastepcze:  {stats['symbols_fallback']}")
    print("  rozklad warstw:")
    for layer, cnt in sorted(stats["layers"].items(),
                             key=lambda kv: -kv[1]):
        print(f"    {layer:<24} {cnt}")
    print(f"\nGotowe -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
