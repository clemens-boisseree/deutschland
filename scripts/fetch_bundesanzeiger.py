#!/usr/bin/env python3
"""Abruf von Bundesanzeiger-Berichten ueber das deutschland-Paket."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import requests
from deutschland.bundesanzeiger import Bundesanzeiger


def _json_default(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ruft Berichte aus dem Bundesanzeiger ab."
    )
    parser.add_argument(
        "company_name",
        nargs="?",
        help="Optionaler Suchbegriff, z. B. Firmenname oder ISIN.",
    )
    parser.add_argument(
        "--company-name",
        dest="company_name_opt",
        help="Optionaler Suchbegriff, alternativ zur positional Angabe.",
    )
    parser.add_argument(
        "--page-limit",
        type=int,
        default=1,
        help="Anzahl Ergebnisseiten (Standard: 1, etwa 20 Berichte pro Seite).",
    )
    parser.add_argument(
        "--location",
        help="Optionaler Standortfilter, z. B. 'Duesseldorf'.",
    )
    parser.add_argument(
        "--area",
        help="Optionaler Bereichsfilter, z. B. 'Amtlicher Teil'.",
    )
    parser.add_argument(
        "--start-date",
        help="Optionales Startdatum (inklusive), z. B. 01.01.2024.",
    )
    parser.add_argument(
        "--end-date",
        help="Optionales Enddatum (inklusive), z. B. 31.12.2024.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optionaler Pfad fuer die JSON-Ausgabe. Ohne Angabe wird auf STDOUT ausgegeben.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.page_limit < 1:
        parser.error("--page-limit muss >= 1 sein.")

    company_name = args.company_name_opt or args.company_name

    client = Bundesanzeiger()

    try:
        reports = client.get_reports(
            company_name,
            page_limit=args.page_limit,
            location=args.location,
            area=args.area,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    except requests.RequestException as exc:
        print(
            "Fehler beim Abruf von www.bundesanzeiger.de. "
            "Bitte Netzwerk/Proxy pruefen und erneut versuchen.",
            file=sys.stderr,
        )
        print(f"Details: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(reports, ensure_ascii=False, indent=2, default=_json_default)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"{len(reports)} Berichte gespeichert in: {args.output}")
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
