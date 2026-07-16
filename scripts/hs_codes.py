#!/usr/bin/env python3
"""Look up Harmonized System (HS) commodity codes and names locally.

Every FactIQ trade schema (us_census_hs, china_customs, india_trade,
korea_trade, japan_trade, taiwan_trade, eu_comext_*) keys its products by HS
code. This resolves codes <-> names from a bundled copy of the UN HS-2022
nomenclature (97 chapters, 1,229 headings, 5,613 subheadings) with zero
server calls — use it instead of exploratory SQL when you need to find the
code for a product or label codes a ranking query returned.

Examples:
  python3 scripts/hs_codes.py 85 8507 850760      # code -> name
  python3 scripts/hs_codes.py --search battery     # name -> codes (all levels)
  python3 scripts/hs_codes.py --search "lithium" --level 6
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "hs_names.json.gz")


def fail(message: str, code: int = 1) -> None:
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(code)


def load_names() -> dict[str, dict[str, str]]:
    try:
        with gzip.open(DATA_PATH, "rt", encoding="utf-8") as f:
            return json.load(f)
    except OSError as exc:
        fail(f"cannot read bundled HS names at {DATA_PATH}: {exc}")
    raise AssertionError  # unreachable


def lookup(names: dict[str, dict[str, str]], code: str) -> None:
    code = code.strip()
    level = str(len(code))
    if level not in names:
        fail(
            f"'{code}' is not a 2-, 4-, or 6-digit HS code. National lines are "
            "longer (US 10, China 8, Japan 9, Taiwan 11, EU CN8) — look up "
            "their first 2/4/6 digits here, and get full national-line names "
            "from the database (`series_title`, `dimensions.dimension_name`, "
            "or `eu_comext_lookup.product_codes.product_name`)."
        )
    name = names[level].get(code)
    if name is None:
        fail(f"HS code '{code}' not found in the HS-2022 nomenclature")
    print(f"{code}\t{name}")


def search(names: dict[str, dict[str, str]], term: str, levels: list[str], limit: int) -> None:
    term_l = term.lower()
    hits = [
        (lvl, code, name)
        for lvl in levels
        for code, name in sorted(names[lvl].items())
        if term_l in name.lower()
    ]
    if not hits:
        fail(f"no HS names contain '{term}' — try a shorter stem", code=2)
    for lvl, code, name in hits[:limit]:
        print(f"{code}\t(HS{lvl})\t{name}")
    if len(hits) > limit:
        print(f"... {len(hits) - limit} more matches; narrow with --level or a longer term", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("codes", nargs="*", help="HS codes to name (2/4/6 digits each)")
    parser.add_argument("--search", help="find codes whose name contains this text")
    parser.add_argument("--level", choices=["2", "4", "6"], help="restrict --search to one level")
    parser.add_argument("--limit", type=int, default=40, help="max --search rows (default 40)")
    args = parser.parse_args()

    if not args.codes and not args.search:
        parser.error("pass HS codes to name, or --search <term>")

    names = load_names()
    for code in args.codes:
        lookup(names, code)
    if args.search:
        search(names, args.search, [args.level] if args.level else ["2", "4", "6"], args.limit)


if __name__ == "__main__":
    main()
