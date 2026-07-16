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
import re
import sys

DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "hs_names.json.gz"
)


def fail(message: str, code: int = 1) -> None:
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(code)


def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer from 1 to 100") from None
    if not 1 <= value <= 100:
        raise argparse.ArgumentTypeError("must be from 1 to 100")
    return value


def load_names() -> dict[str, dict[str, str]]:
    try:
        with gzip.open(DATA_PATH, "rt", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, EOFError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"cannot read bundled HS names at {DATA_PATH}: {exc}")
    if not isinstance(data, dict) or any(
        not isinstance(data.get(level), dict) for level in ("2", "4", "6")
    ):
        fail(f"bundled HS names at {DATA_PATH} have an invalid shape")
    if any(
        not isinstance(code, str) or not isinstance(name, str)
        for level in ("2", "4", "6")
        for code, name in data[level].items()
    ):
        fail(f"bundled HS names at {DATA_PATH} have an invalid shape")
    return data


def lookup(names: dict[str, dict[str, str]], code: str) -> str:
    code = code.strip()
    level = str(len(code))
    if level not in names or re.fullmatch(r"[0-9]+", code, flags=re.ASCII) is None:
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
    return f"{code}\t{name}"


def _stem(token: str) -> str:
    """Fold trivial plurals so 'battery' meets 'batteries'. Applied to both
    sides identically — consistency matters more than linguistic accuracy."""
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if (
        token.endswith("s")
        and len(token) > 3
        and not token.endswith(("ss", "us", "is"))
    ):
        return token[:-1]
    return token


def _tokens(text: str) -> set[str]:
    return {_stem(t) for t in re.split(r"[^a-z0-9]+", text.lower()) if t}


def search(
    names: dict[str, dict[str, str]], term: str, levels: list[str], limit: int
) -> None:
    term_l = term.strip().lower()
    want = _tokens(term)
    if not want:
        fail("--search must contain at least one letter or number", code=2)
    rows = [
        (lvl, code, name, _tokens(name))
        for lvl in levels
        for code, name in sorted(names[lvl].items())
    ]
    # Rank literal fragments and plural-aware token matches together. Keeping
    # them in one pool matters for queries such as "battery": a literal hit on
    # "battery carbons" must not hide the more relevant "batteries" heading.
    # A rare matched word outranks a common one, then concise names win.
    df = {token: sum(1 for *_, toks in rows if token in toks) or 1 for token in want}
    scored = []
    for lvl, code, name, toks in rows:
        literal = term_l in name.lower()
        matched = want & toks
        if not literal and not matched:
            continue
        effective_matches = want if literal else matched
        scored.append(
            (
                len(effective_matches),
                sum(1.0 / df[token] for token in effective_matches),
                len(toks),
                literal,
                lvl,
                code,
                name,
            )
        )
    if not scored:
        fail(f"no HS names match '{term}' — try a shorter stem", code=2)
    scored.sort(
        key=lambda row: (
            -row[0],
            -row[1],
            row[2],
            not row[3],
            row[4],
            row[5],
        )
    )
    best = scored[0][0]
    hits = [
        (lvl, code, name)
        for matched_count, _, _, _, lvl, code, name in scored
        if matched_count == best
    ]
    if best < len(want):
        print(
            f"(no name contains all {len(want)} words — ranked by matches, rarest words first)",
            file=sys.stderr,
        )
    for lvl, code, name in hits[:limit]:
        print(f"{code}\t(HS{lvl})\t{name}")
    if len(hits) > limit:
        print(
            f"... {len(hits) - limit} more matches; narrow with --level or a longer term",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("codes", nargs="*", help="HS codes to name (2/4/6 digits each)")
    parser.add_argument("--search", help="find codes whose name contains this text")
    parser.add_argument(
        "--level", choices=["2", "4", "6"], help="restrict --search to one level"
    )
    parser.add_argument(
        "--limit",
        type=positive_int,
        help="maximum search rows, 1-100 (default 15)",
    )
    args = parser.parse_args()

    if not args.codes and args.search is None:
        parser.error("pass HS codes to name, or --search <term>")
    if args.codes and args.search is not None:
        parser.error("pass either HS codes or --search, not both")
    if args.search is None and (args.level is not None or args.limit is not None):
        parser.error("--level and --limit can only be used with --search")

    names = load_names()
    if args.codes:
        # Validate every code before emitting anything, so a bad later argument
        # cannot leave a caller with a partial result that looks successful.
        lines = [lookup(names, code) for code in args.codes]
        print("\n".join(lines))
    else:
        search(
            names,
            args.search,
            [args.level] if args.level else ["2", "4", "6"],
            args.limit or 15,
        )


if __name__ == "__main__":
    main()
