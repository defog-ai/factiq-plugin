#!/usr/bin/env python3
"""Generate ready-to-run SQL for the Eurostat Comext schemas (eu_comext_*).

Comext series IDs must be constructed exactly (pattern scans time out; string
ranges return wrong rows — see references/data/sql-guide.md). This emits the
correct exact-ID SQL mechanically: the cn6_total series for all-goods totals,
lookup-table joins for product breakdowns, and UNION ALL across any set of
the 27 reporter schemas. Run the output with the run_sql tool using the
schema printed in the header comment.

ID grammar it encodes:
  eu_comext_{M|X}_{reporter}_{partner}_{te|ti|tl}_p1_cn8_{code}_{eur|kg|su}
  - reporter/partner: lowercase ISO2 (plus Eurostat's `xi` code for Northern
    Ireland); `uk` is an input alias that combines `gb` and `xi` from 2021.
    Trade token: `ti` while the partner is an EU member, `te` while it is
    outside the EU, and `tl` for Northern Ireland from 2021. Date ranges that
    cross an accession or Brexit are split across the exact series.
  - metric: _eur value, _kg weight, _su supplementary quantity — never summed
    together. All-goods totals use the exact `cn6_total` product token.

Examples:
  python3 scripts/comext_sql.py total --reporters all --partner cn --flow imports \
      --start 2025-01 --end 2025-12
  python3 scripts/comext_sql.py total --reporters de,fr,nl --partner us --flow exports \
      --start 2024-01 --end 2025-12 --monthly
  python3 scripts/comext_sql.py products --reporters all --partner cn --flow imports \
      --start 2025-01 --end 2025-12 --group-by 4 --top 25
  python3 scripts/comext_sql.py trend --reporters de --partner cn --flow imports \
      --hs 8507 --start 2020-01 --end 2025-12

Label the HS codes a products/trend query returns with scripts/hs_codes.py.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

EU_MEMBERS = [
    "at",
    "be",
    "bg",
    "hr",
    "cy",
    "cz",
    "dk",
    "ee",
    "fi",
    "fr",
    "de",
    "gr",
    "hu",
    "ie",
    "it",
    "lv",
    "lt",
    "lu",
    "mt",
    "nl",
    "pl",
    "pt",
    "ro",
    "sk",
    "si",
    "es",
    "se",
]

# Comext records trade under the partner's EU status in each month. The data
# starts in 2002, so only accessions within its coverage need a split here.
EU_ACCESSION_MONTH = {
    "cy": "2004-05-01",
    "cz": "2004-05-01",
    "ee": "2004-05-01",
    "hu": "2004-05-01",
    "lv": "2004-05-01",
    "lt": "2004-05-01",
    "mt": "2004-05-01",
    "pl": "2004-05-01",
    "sk": "2004-05-01",
    "si": "2004-05-01",
    "bg": "2007-01-01",
    "ro": "2007-01-01",
    "hr": "2013-07-01",
}
COMEXT_START = "2002-01-01"
GB_EXTRA_EU_MONTH = "2020-02-01"
NORTHERN_IRELAND_START = "2021-01-01"

METRICS = {"value": "eur", "weight": "kg", "supplementary": "su"}
METRIC_UNITS = {"value": "EUR", "weight": "kg", "supplementary": "supplementary units"}


def fail(message: str, code: int = 1) -> None:
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(code)


def parse_month(text: str, name: str) -> tuple[int, int]:
    match = re.fullmatch(r"([0-9]{4})-(0[1-9]|1[0-2])", text)
    if match is None:
        fail(f"--{name} must be YYYY-MM, got '{text}'")
    year, month = map(int, match.groups())
    if year == 0:
        fail(f"--{name} year must be between 0001 and 9999, got '{text}'")
    return year, month


def date_bounds(start: str, end: str) -> tuple[str, str]:
    """Inclusive month range -> [first day of start, first day after end)."""
    sy, sm = parse_month(start, "start")
    ey, em = parse_month(end, "end")
    if (sy, sm) > (ey, em):
        fail(f"--start {start} is after --end {end}")
    if (ey, em) == (9999, 12):
        fail("--end 9999-12 cannot be represented as an exclusive upper date bound")
    ny, nm = (ey + 1, 1) if em == 12 else (ey, em + 1)
    return f"{sy:04d}-{sm:02d}-01", f"{ny:04d}-{nm:02d}-01"


def comext_date_bounds(start: str, end: str) -> tuple[str, str, str]:
    """Return usable Comext bounds and a note when early months are clipped."""
    lo, hi = date_bounds(start, end)
    if hi <= COMEXT_START:
        fail(
            f"Comext data begin in 2002-01; requested range {start}..{end} "
            "ends before coverage"
        )
    if lo < COMEXT_START:
        return (
            COMEXT_START,
            hi,
            "Comext data begin in 2002-01; earlier requested months omitted",
        )
    return lo, hi, ""


def resolve_reporters(text: str) -> list[str]:
    if text.strip().lower() == "all":
        return list(EU_MEMBERS)
    reporters = [r.strip().lower() for r in text.split(",") if r.strip()]
    bad = [r for r in reporters if r not in EU_MEMBERS]
    if bad:
        fail(
            f"unknown reporter(s) {bad}: reporters are the 27 EU members as "
            f"lowercase ISO2 ({', '.join(EU_MEMBERS)}) or 'all'"
        )
    if not reporters:
        fail("--reporters must contain at least one EU member, or 'all'")
    # Repeating a reporter would repeat its UNION branch and double-count it.
    return list(dict.fromkeys(reporters))


def resolve_partner(text: str) -> str:
    partner = text.strip().lower()
    if re.fullmatch(r"[a-z]{2}", partner, flags=re.ASCII) is None:
        fail(
            f"--partner must be a lowercase ISO2 country code (e.g. cn, us, gb, in), got '{text}'"
        )
    return partner


def remove_domestic_reporter(
    reporters: list[str], partner: str
) -> tuple[list[str], str]:
    """Remove an EU partner's own reporter branch; Comext has no self trade."""
    if partner not in reporters:
        return reporters, ""
    remaining = [reporter for reporter in reporters if reporter != partner]
    if not remaining:
        fail(
            f"reporter '{partner}' and partner '{partner}' are the same country; "
            "Comext has no domestic trade series"
        )
    return remaining, f"domestic reporter {partner} omitted (Comext has no self trade)"


def add_note(note: str, extra: str) -> str:
    return f"{note}; {extra}" if extra else note


def limited_positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer from 1 to 50") from None
    if not 1 <= value <= 50:
        raise argparse.ArgumentTypeError("must be from 1 to 50")
    return value


def flow_code(flow: str) -> str:
    return {"imports": "M", "exports": "X", "m": "M", "x": "X"}[flow.lower()]


def trade_periods(
    partner: str, lo: str, hi: str
) -> tuple[list[tuple[str, str, str, str]], str]:
    """Return exact (partner, trade token, lower date, upper date) segments."""
    if partner == "uk":
        periods, gb_note = trade_periods("gb", lo, hi)
        notes = [
            note
            for note in gb_note.split("; ")
            if note and not note.startswith("Northern Ireland is stored separately")
        ]
        if hi > NORTHERN_IRELAND_START:
            periods.append(("xi", "tl", max(lo, NORTHERN_IRELAND_START), hi))
            notes.append(
                "whole UK combines the gb and Northern Ireland xi series from 2021-01"
            )
        return periods, "; ".join(notes)

    if partner == "xi":
        if hi <= NORTHERN_IRELAND_START:
            fail("Comext's Northern Ireland (xi) series begin in 2021-01")
        clipped_lo = max(lo, NORTHERN_IRELAND_START)
        note = (
            "Northern Ireland series begin in 2021-01; earlier requested months omitted"
            if lo < NORTHERN_IRELAND_START
            else ""
        )
        return [(partner, "tl", clipped_lo, hi)], note

    if partner == "gb":
        periods = []
        if lo < GB_EXTRA_EU_MONTH:
            periods.append((partner, "ti", lo, min(hi, GB_EXTRA_EU_MONTH)))
        if hi > GB_EXTRA_EU_MONTH:
            periods.append((partner, "te", max(lo, GB_EXTRA_EU_MONTH), hi))
        periods = [period for period in periods if period[2] < period[3]]
        notes = []
        if len(periods) > 1:
            notes.append(
                "Great Britain trade switches from the intra-EU series to the "
                "extra-EU series in 2020-02"
            )
        if hi > NORTHERN_IRELAND_START:
            notes.append(
                "Northern Ireland is stored separately as partner xi from 2021-01"
            )
        return periods, "; ".join(notes)

    accession = EU_ACCESSION_MONTH.get(partner)
    if accession is not None:
        periods = []
        if lo < accession:
            periods.append((partner, "te", lo, min(hi, accession)))
        if hi > accession:
            periods.append((partner, "ti", max(lo, accession), hi))
        periods = [period for period in periods if period[2] < period[3]]
        note = (
            f"partner {partner} switches from the extra-EU series to the intra-EU "
            f"series in {accession[:7]}"
            if len(periods) > 1
            else ""
        )
        return periods, note

    token = "ti" if partner in EU_MEMBERS else "te"
    return [(partner, token, lo, hi)], ""


def total_series_id(
    flow: str, reporter: str, partner: str, token: str, suffix: str
) -> str:
    return f"eu_comext_{flow}_{reporter}_{partner}_{token}_p1_cn6_total_{suffix}"


def product_id_expr(
    flow: str, reporter: str, partner: str, token: str, suffix: str
) -> str:
    prefix = f"eu_comext_{flow}_{reporter}_{partner}_{token}_p1_cn8_"
    return f"'{prefix}' || lower(p.product_code) || '_{suffix}'"


def header(reporters: list[str], args: argparse.Namespace, extra: str = "") -> str:
    lines = [
        f"-- generated by comext_sql.py {args.command}: "
        f"{args.flow} vs partner '{args.partner}', {args.start}..{args.end}, metric={args.metric}",
        f'-- run with the run_sql tool, schema="eu_comext_{reporters[0]}"',
    ]
    if extra:
        lines.append(f"-- {extra}")
    return "\n".join(lines)


def sql_total(args: argparse.Namespace) -> str:
    reporters = resolve_reporters(args.reporters)
    partner = resolve_partner(args.partner)
    reporters, domestic_note = remove_domestic_reporter(reporters, partner)
    flow = flow_code(args.flow)
    if args.metric == "supplementary":
        fail(
            "supplementary quantities use product-specific units and cannot form an "
            "all-goods total; use value or weight"
        )
    suffix = METRICS[args.metric]
    lo, hi, coverage_note = comext_date_bounds(args.start, args.end)
    periods, period_note = trade_periods(partner, lo, hi)

    # Each reporter schema holds only its own series in data_points, so every
    # reporter needs its own qualified branch — a flat IN list against one
    # schema's table would silently drop the other 26.
    branches = []
    for r in reporters:
        for period_partner, token, period_lo, period_hi in periods:
            table = (
                "data_points" if len(reporters) == 1 else f"eu_comext_{r}.data_points"
            )
            branches.append(
                f"  SELECT '{r}' AS reporter, time AS t, value AS v\n"
                f"  FROM {table}\n"
                f"  WHERE series_id = "
                f"'{total_series_id(flow, r, period_partner, token, suffix)}'\n"
                f"    AND time >= DATE '{period_lo}' AND time < DATE '{period_hi}'"
            )
    union = "\nUNION ALL\n".join(branches)
    if args.monthly:
        select, group = (
            f"t::date AS month, SUM(v) AS total_{suffix}",
            "GROUP BY t\nORDER BY t",
        )
    else:
        select, group = (
            f"reporter, SUM(v) AS total_{suffix}",
            "GROUP BY reporter\nORDER BY 2 DESC",
        )
    body = f"SELECT {select}\nFROM (\n{union}\n) u\n{group};"
    note = f"all-goods total via the exact cn6_total series; values in {METRIC_UNITS[args.metric]}"
    note = add_note(note, domestic_note)
    note = add_note(note, coverage_note)
    note = add_note(note, period_note)
    return header(reporters, args, note) + "\n" + body


def product_branches(
    reporters: list[str],
    flow: str,
    suffix: str,
    periods: list[tuple[str, str, str, str]],
    inner_select: str,
    where_extra: str,
    include_unit: bool = False,
) -> str:
    branches = []
    for r in reporters:
        for period_partner, token, period_lo, period_hi in periods:
            table = (
                "data_points" if len(reporters) == 1 else f"eu_comext_{r}.data_points"
            )
            series_join = ""
            if include_unit:
                series_table = (
                    "series" if len(reporters) == 1 else f"eu_comext_{r}.series"
                )
                series_join = f"  JOIN {series_table} s ON s.series_id = dp.series_id\n"
            branches.append(
                f"  SELECT {inner_select.format(reporter=r)}\n"
                f"  FROM eu_comext_lookup.product_codes p\n"
                f"  JOIN {table} dp\n"
                f"    ON dp.series_id = "
                f"{product_id_expr(flow, r, period_partner, token, suffix)}\n"
                f"{series_join}"
                f"  WHERE p.is_numeric_cn8\n"
                f"    AND p.last_observed >= DATE '{period_lo}' "
                f"AND p.first_observed < DATE '{period_hi}'\n"
                f"    AND dp.time >= DATE '{period_lo}' "
                f"AND dp.time < DATE '{period_hi}'{where_extra}"
            )
    return "\nUNION ALL\n".join(branches)


def sql_products(args: argparse.Namespace) -> str:
    reporters = resolve_reporters(args.reporters)
    partner = resolve_partner(args.partner)
    reporters, domestic_note = remove_domestic_reporter(reporters, partner)
    flow = flow_code(args.flow)
    suffix = METRICS[args.metric]
    if args.metric == "supplementary":
        fail(
            "supplementary quantities use product-specific units and cannot be ranked "
            "across products; use value or weight"
        )
    lo, hi, coverage_note = comext_date_bounds(args.start, args.end)
    periods, period_note = trade_periods(partner, lo, hi)

    group_col = {
        "2": "p.hs2_code",
        "4": "p.hs4_code",
        "6": "p.hs6_code",
        "cn8": "lower(p.product_code)",
    }[args.group_by]
    inner = f"{group_col} AS code, dp.value AS v"
    union = product_branches(reporters, flow, suffix, periods, inner, "")
    body = (
        f"SELECT code, SUM(v) AS total_{suffix}\n"
        f"FROM (\n{union}\n) t\n"
        f"GROUP BY code\n"
        f"ORDER BY 2 DESC\n"
        f"LIMIT {args.top};"
    )
    label_hint = (
        "name the codes locally: python3 scripts/hs_codes.py <codes>"
        if args.group_by in ("2", "4", "6")
        else "CN8 names live in eu_comext_lookup.product_codes.product_name"
    )
    note = (
        f"top products by HS{args.group_by}; values in "
        f"{METRIC_UNITS[args.metric]}; {label_hint}"
    )
    note = add_note(note, domestic_note)
    note = add_note(note, coverage_note)
    note = add_note(note, period_note)
    return header(reporters, args, note) + "\n" + body


def sql_trend(args: argparse.Namespace) -> str:
    reporters = resolve_reporters(args.reporters)
    partner = resolve_partner(args.partner)
    reporters, domestic_note = remove_domestic_reporter(reporters, partner)
    flow = flow_code(args.flow)
    suffix = METRICS[args.metric]
    lo, hi, coverage_note = comext_date_bounds(args.start, args.end)
    periods, period_note = trade_periods(partner, lo, hi)

    code = args.hs.strip().lower()
    if (
        len(code) not in (2, 4, 6, 8)
        or re.fullmatch(r"[0-9]+", code, flags=re.ASCII) is None
    ):
        fail(
            f"--hs must be a 2/4/6-digit HS code or an 8-digit CN8 code, got '{args.hs}'"
        )
    if len(code) == 8:
        where_extra = f"\n    AND lower(p.product_code) = '{code}'"
    else:
        col = {2: "p.hs2_code", 4: "p.hs4_code", 6: "p.hs6_code"}[len(code)]
        where_extra = f"\n    AND {col} = '{code}'"
    if args.metric == "supplementary" and len(code) != 8:
        fail(
            "supplementary quantities use product-specific units and can only be "
            "queried for one exact 8-digit CN8 code"
        )

    include_unit = args.metric == "supplementary"
    inner = (
        "s.measurement_units AS unit, dp.time AS t, dp.value AS v"
        if include_unit
        else "dp.time AS t, dp.value AS v"
    )
    union = product_branches(
        reporters,
        flow,
        suffix,
        periods,
        inner,
        where_extra,
        include_unit=include_unit,
    )
    if include_unit:
        body = (
            f"SELECT unit AS measurement_units, t::date AS month, SUM(v) AS total_{suffix}\n"
            f"FROM (\n{union}\n) u\nGROUP BY unit, t\nORDER BY t, unit;"
        )
        note = f"monthly trend for HS {code}; units returned with each row"
    else:
        body = (
            f"SELECT t::date AS month, SUM(v) AS total_{suffix}\n"
            f"FROM (\n{union}\n) u\nGROUP BY t\nORDER BY t;"
        )
        note = f"monthly trend for HS {code}; values in {METRIC_UNITS[args.metric]}"
    note = add_note(note, domestic_note)
    note = add_note(note, coverage_note)
    note = add_note(note, period_note)
    return header(reporters, args, note) + "\n" + body


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--reporters",
            required=True,
            help="comma-separated lowercase ISO2 EU members, or 'all'",
        )
        p.add_argument(
            "--partner",
            required=True,
            help="partner country ISO2; xi = Northern Ireland, uk = whole UK (gb + xi from 2021)",
        )
        p.add_argument("--flow", required=True, choices=["imports", "exports"])
        p.add_argument(
            "--start", required=True, help="first month, YYYY-MM (inclusive)"
        )
        p.add_argument("--end", required=True, help="last month, YYYY-MM (inclusive)")
        p.add_argument(
            "--metric",
            default="value",
            choices=sorted(METRICS),
            help="default: value (EUR)",
        )

    p_total = sub.add_parser(
        "total", help="all-goods totals via the exact cn6_total series"
    )
    add_common(p_total)
    p_total.add_argument(
        "--monthly",
        action="store_true",
        help="one row per month instead of one per reporter",
    )

    p_products = sub.add_parser(
        "products", help="top products via the lookup-table join"
    )
    add_common(p_products)
    p_products.add_argument(
        "--group-by",
        default="4",
        choices=["2", "4", "6", "cn8"],
        help="HS grouping level (default 4)",
    )
    p_products.add_argument(
        "--top",
        type=limited_positive_int,
        default=25,
        help="rows to return, 1-50 (default 25)",
    )

    p_trend = sub.add_parser("trend", help="monthly trend for one HS group or CN8 line")
    add_common(p_trend)
    p_trend.add_argument(
        "--hs", required=True, help="2/4/6-digit HS code or 8-digit CN8 code"
    )

    args = parser.parse_args()
    print(
        {"total": sql_total, "products": sql_products, "trend": sql_trend}[
            args.command
        ](args)
    )


if __name__ == "__main__":
    main()
