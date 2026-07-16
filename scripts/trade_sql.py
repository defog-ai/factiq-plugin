#!/usr/bin/env python3
"""Generate ready-to-run SQL for the national customs trade schemas.

Covers the six reporter datasets that share one series-ID grammar —
`{dataset}_{M|X}_{N}d_{hscode}_{partnercode}[_qty]`:

  source   schema         HS levels      value unit    quantity series
  census   census         6, 10          US$           _qty (10-digit only)
  china    china_customs  6, 8           US$           _qty (unit varies)
  india    india_trade    6, 8           US$ Million   none
  korea    korea_trade    6, 10          US$ Thousand  _qty (kg)
  japan    japan_trade    9              ¥ Thousand    _qty and _qty2 (units vary)
  taiwan   taiwan_trade   6, 11          US$           none

It encodes the traps for you: partner codes are per-source (numeric for
census/china/india/japan, ISO2 for korea/taiwan — resolved from a bundled
map), exactly one HS level per query (levels double-count each other),
value and quantity series never mix, and units differ per source (never sum
India's US$ Million with Korea's US$ Thousand without rescaling).

Run the output with the run_sql tool using the schema in the header comment.
Mirror caveat: each source is that country's own customs view; reporter
views of the same flow differ on valuation, timing, and re-exports.

Examples:
  python3 "{plugin_root}/scripts/trade_sql.py" total --source census --partner China --flow imports \
      --start 2025-01 --end 2025-12 --monthly
  python3 "{plugin_root}/scripts/trade_sql.py" products --source india --partner "united states" \
      --flow exports --start 2025-01 --end 2025-12 --group-by 2 --top 20
  python3 "{plugin_root}/scripts/trade_sql.py" trend --source korea --partner cn --flow exports \
      --hs 854232 --start 2020-01 --end 2025-12

Here {plugin_root} is the absolute directory containing the plugin manifests.
Label the HS codes a products query returns with its bundled hs_codes.py.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

SOURCES = {
    "census": {
        "schema": "census",
        "prefix": "us_census_hs",
        "reporter": "United States",
        "levels": (6, 10),
        "value_unit": "US$",
        "qty_suffixes": ("qty",),
        "qty_levels": (10,),
        "world_partner": "-",
        "dataset_filter": "us_census_hs",
    },
    "china": {
        "schema": "china_customs",
        "prefix": "china_customs",
        "reporter": "China",
        "levels": (6, 8),
        "value_unit": "US$",
        "qty_suffixes": ("qty",),
        "qty_levels": (6, 8),
        "world_partner": None,
        "dataset_filter": "china_customs",
    },
    "india": {
        "schema": "india_trade",
        "prefix": "india_trade",
        "reporter": "India",
        "levels": (6, 8),
        "value_unit": "US$ Million",
        "qty_suffixes": (),
        "qty_levels": (),
        "world_partner": None,
        "dataset_filter": None,
    },
    "korea": {
        "schema": "korea_trade",
        "prefix": "korea_trade",
        "reporter": "South Korea",
        "levels": (6, 10),
        "value_unit": "US$ Thousand",
        "qty_suffixes": ("qty",),
        "qty_levels": (6, 10),
        "world_partner": None,
        "dataset_filter": None,
    },
    "japan": {
        "schema": "japan_trade",
        "prefix": "japan_trade",
        "reporter": "Japan",
        "levels": (9,),
        "value_unit": "¥ Thousand",
        "qty_suffixes": ("qty", "qty2"),
        "qty_levels": (9,),
        "world_partner": None,
        "dataset_filter": None,
    },
    "taiwan": {
        "schema": "taiwan_trade",
        "prefix": "taiwan_trade",
        "reporter": "Taiwan",
        "levels": (6, 11),
        "value_unit": "US$",
        "qty_suffixes": (),
        "qty_levels": (),
        "world_partner": None,
        "dataset_filter": None,
    },
}

PARTNER_MAP_KEY = {  # source -> key in trade_partners.json
    "census": "us_census_hs",
    "china": "china_customs",
    "india": "india_trade",
    "korea": "korea_trade",
    "japan": "japan_trade",
    "taiwan": "taiwan_trade",
}


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
    sy, sm = parse_month(start, "start")
    ey, em = parse_month(end, "end")
    if (sy, sm) > (ey, em):
        fail(f"--start {start} is after --end {end}")
    if (ey, em) == (9999, 12):
        fail("--end 9999-12 cannot be represented as an exclusive upper date bound")
    ny, nm = (ey + 1, 1) if em == 12 else (ey, em + 1)
    return f"{sy:04d}-{sm:02d}-01", f"{ny:04d}-{nm:02d}-01"


def load_partners(source: str) -> tuple[dict[str, str], dict[str, str]]:
    """Return (code -> name, alias -> code) for this source."""
    path = os.path.join(DATA_DIR, "trade_partners.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        key = PARTNER_MAP_KEY[source]
        partners = data["partners"][key]
        aliases = data["aliases"][key]
        if not isinstance(partners, dict) or not isinstance(aliases, dict):
            fail(f"bundled partner map at {path} has an invalid shape")
        if any(
            not isinstance(code, str) or not isinstance(name, str)
            for mapping in (partners, aliases)
            for code, name in mapping.items()
        ):
            fail(f"bundled partner map at {path} has an invalid shape")
        missing_alias_codes = sorted(set(aliases.values()) - set(partners))
        if missing_alias_codes:
            fail(
                f"bundled partner map at {path} has aliases for unknown code(s) "
                f"{missing_alias_codes}"
            )
        return partners, aliases
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        fail(f"cannot read bundled partner map at {path}: {exc}")
    raise AssertionError  # unreachable


def normalize_partner_name(text: str) -> str:
    """Fold punctuation and accidental spacing for partner-name matching."""
    return "".join(char for char in text.casefold() if char.isalnum())


EU_AGGREGATE_QUERIES = {
    "eu",
    "eu27",
    "euro",
    "europeanunion",
    "europeanunion27",
}


def same_name_codes(partners: dict[str, str], name: str) -> list[str]:
    """Return every code whose display name denotes the same partner."""
    normalized_name = normalize_partner_name(name)
    return [
        code
        for code, candidate in partners.items()
        if normalize_partner_name(candidate) == normalized_name
    ]


def grouped_name_hits(
    hits: list[tuple[str, str]],
) -> list[list[tuple[str, str]]]:
    """Group code hits that are historical versions of the same partner."""
    grouped: dict[str, list[tuple[str, str]]] = {}
    for code, name in hits:
        grouped.setdefault(normalize_partner_name(name), []).append((code, name))
    return list(grouped.values())


def resolve_partner(source: str, text: str) -> tuple[list[str], str]:
    """Resolve a partner code or name to (codes, display name).

    A few China partner codes changed in January 2023. The bundled map keeps
    both codes under the same name, so name-based queries must include both to
    work across the boundary. Passing an exact code still selects only that
    code.
    """
    cfg = SOURCES[source]
    query = text.strip()
    if not query:
        fail("--partner cannot be empty")
    if query.lower() in ("world", "all"):
        if cfg["world_partner"] is None:
            hint = (
                " (for China's headline totals use the separate china_customs_prelim "
                "series, e.g. china_customs_prelim_total_export_cny — note they are "
                "CNY, not US$)"
                if source == "china"
                else ""
            )
            fail(
                f"source '{source}' stores no all-partner total rows — query a "
                f"specific partner, or sum per-partner results yourself{hint}"
            )
        query = cfg["world_partner"]
    partners, aliases = load_partners(source)
    # 1. exact code (case-insensitive). Keep this ahead of aliases so an
    # explicit historical code always selects only that code.
    for code, name in partners.items():
        if code.lower() == query.lower():
            return [code], name
    normalized_query = normalize_partner_name(query)
    if not normalized_query:
        fail("--partner must contain at least one letter or number")
    # Do not let an EU/EU-27 request fall through to fuzzy matching. Some
    # national customs maps contain names such as "Other European Territories"
    # but do not publish a European Union aggregate, so a fragment like
    # "euro" could otherwise produce valid-looking SQL for the wrong geography.
    if normalized_query in EU_AGGREGATE_QUERIES:
        eu_codes = same_name_codes(partners, "European Union")
        if not eu_codes:
            fail(
                f"source '{source}' has no European Union aggregate partner — "
                "query EU member countries separately, or use comext_sql.py "
                "for EU-reported trade"
            )
        return eu_codes, partners[eu_codes[0]]
    # 2. curated alias ("united states", "south korea", "uae", ...).
    # Normalize aliases too, so "U.S." and repeated spaces work as expected.
    alias_matches = {
        code
        for alias, code in aliases.items()
        if normalize_partner_name(alias) == normalized_query
    }
    if len(alias_matches) > 1:
        fail(f"bundled aliases for '{query}' resolve to multiple partner codes")
    if alias_matches:
        alias_code = next(iter(alias_matches))
        alias_name = partners[alias_code]
        return same_name_codes(partners, alias_name), alias_name
    # 3. exact normalized name. Multiple codes with the same name are
    # historical versions of one partner and must all be queried.
    exact = [
        (code, name)
        for code, name in partners.items()
        if normalize_partner_name(name) == normalized_query
    ]
    if exact:
        return [code for code, _ in exact], exact[0][1]
    # 4. unique normalized-name substring. Count names rather than codes:
    # two historical codes for Georgia are one partner match, not ambiguity.
    hits = [
        (code, name)
        for code, name in partners.items()
        if normalized_query in normalize_partner_name(name)
    ]
    if not hits:
        fail(f"no partner in '{source}' matches '{text}' — try a shorter name fragment")
    grouped_hits = grouped_name_hits(hits)
    if len(grouped_hits) == 1:
        return [code for code, _ in grouped_hits[0]], grouped_hits[0][0][1]
    listing = "; ".join(
        f"{','.join(code for code, _ in group)}={group[0][1]}"
        for group in grouped_hits[:10]
    )
    fail(
        f"'{text}' is ambiguous in '{source}' ({len(grouped_hits)} matches): {listing}",
        code=2,
    )
    raise AssertionError  # unreachable


def resolve_level(source: str, level: int | None) -> int:
    cfg = SOURCES[source]
    if level is None:
        return cfg["levels"][0]
    if level not in cfg["levels"]:
        fail(f"source '{source}' stores HS levels {cfg['levels']}, not {level}")
    return level


def flow_code(flow: str) -> str:
    return {"imports": "M", "exports": "X"}[flow]


def limited_positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer from 1 to 50") from None
    if not 1 <= value <= 50:
        raise argparse.ArgumentTypeError("must be from 1 to 50")
    return value


def value_filter(source: str) -> str:
    """WHERE fragment that keeps value series only (drops _qty/_qty2)."""
    return f"s.measurement_units = '{SOURCES[source]['value_unit']}'"


def sql_string(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def add_partner_code_note(note: str, partner_codes: list[str]) -> str:
    if len(partner_codes) == 1:
        return note
    codes = ", ".join(partner_codes)
    return f"{note}; combined historical partner codes {codes}"


def dim_join(alias: str, dim_type: str, codes: str | list[str]) -> str:
    code_list = [codes] if isinstance(codes, str) else codes
    if len(code_list) == 1:
        code_condition = f"{alias}.dimension_code = {sql_string(code_list[0])}"
    else:
        code_condition = (
            f"{alias}.dimension_code IN ("
            + ", ".join(sql_string(code) for code in code_list)
            + ")"
        )
    return (
        f"JOIN dimensions {alias} ON {alias}.series_id = s.series_id\n"
        f"  AND {alias}.dimension_type = {sql_string(dim_type)} AND {code_condition}"
    )


def base_joins(
    source: str, flow: str, level: int, partner_codes: list[str]
) -> tuple[str, list[str]]:
    cfg = SOURCES[source]
    parts = [
        "FROM series s",
        dim_join("f", "flow", flow_code(flow)),
        dim_join("l", "hs_level", str(level)),
        dim_join("pa", "partner", partner_codes),
        "JOIN data_points dp ON dp.series_id = s.series_id",
    ]
    where = [value_filter(source)]
    if cfg["dataset_filter"]:
        where.append(f"s.dataset_code = '{cfg['dataset_filter']}'")
    return "\n".join(parts), where


def header(
    source: str,
    args: argparse.Namespace,
    partner_name: str,
    level: int,
    extra: str = "",
) -> str:
    cfg = SOURCES[source]
    lines = [
        f"-- generated by trade_sql.py {args.command}: {cfg['reporter']} {args.flow} "
        f"vs {partner_name}, {args.start}..{args.end}, HS-{level} level",
        f'-- run with the run_sql tool, schema="{cfg["schema"]}"',
    ]
    if getattr(args, "metric", "value") == "quantity":
        lines.append(
            "-- quantities use product-specific units; measurement_units is returned "
            "with each series"
        )
    else:
        lines.append(
            f"-- values in {cfg['value_unit']} ({cfg['reporter']} customs' own view)"
        )
    if extra:
        lines.append(f"-- {extra}")
    return "\n".join(lines)


def sql_total(args: argparse.Namespace) -> str:
    source = args.source
    partner_codes, partner_name = resolve_partner(source, args.partner)
    level = resolve_level(source, args.level)
    lo, hi = date_bounds(args.start, args.end)

    joins, where = base_joins(source, args.flow, level, partner_codes)
    where.append(f"dp.time >= DATE '{lo}' AND dp.time < DATE '{hi}'")
    if args.monthly:
        select, group = (
            "dp.time::date AS month, SUM(dp.value) AS value",
            "\nGROUP BY 1\nORDER BY 1",
        )
    else:
        select, group = "SUM(dp.value) AS value", ""
    conditions = "\n  AND ".join(where)
    body = f"SELECT {select}\n{joins}\nWHERE {conditions}{group};"
    note = add_partner_code_note(
        f"all-goods total = sum over every HS-{level} line for this partner",
        partner_codes,
    )
    return header(source, args, partner_name, level, note) + "\n" + body


def sql_products(args: argparse.Namespace) -> str:
    source = args.source
    partner_codes, partner_name = resolve_partner(source, args.partner)
    level = resolve_level(source, args.level)
    group_digits = int(args.group_by)
    if group_digits > level:
        fail(
            f"--group-by {group_digits} is finer than the HS-{level} lines being queried"
        )
    lo, hi = date_bounds(args.start, args.end)

    joins, where = base_joins(source, args.flow, level, partner_codes)
    joins += "\n" + (
        "JOIN dimensions c ON c.series_id = s.series_id\n"
        "  AND c.dimension_type = 'commodity'"
    )
    where.append(f"dp.time >= DATE '{lo}' AND dp.time < DATE '{hi}'")
    conditions = "\n  AND ".join(where)
    body = (
        f"SELECT LEFT(c.dimension_code, {group_digits}) AS code, SUM(dp.value) AS value\n"
        f"{joins}\n"
        f"WHERE {conditions}\n"
        f"GROUP BY 1\nORDER BY 2 DESC\nLIMIT {args.top};"
    )
    label_hint = (
        "name the codes locally with the bundled hs_codes.py helper"
        if group_digits in (2, 4, 6)
        else "national-line names live in dimensions.dimension_name (dimension_type='commodity')"
    )
    note = add_partner_code_note(
        f"top products by first {group_digits} HS digits; {label_hint}",
        partner_codes,
    )
    return header(source, args, partner_name, level, note) + "\n" + body


def sql_trend(args: argparse.Namespace) -> str:
    source = args.source
    cfg = SOURCES[source]
    partner_codes, partner_name = resolve_partner(source, args.partner)
    code = args.hs.strip()
    if re.fullmatch(r"[0-9]+", code, flags=re.ASCII) is None:
        fail(f"--hs must be an HS code, got '{args.hs}'")
    lo, hi = date_bounds(args.start, args.end)

    if (
        len(code) in cfg["levels"]
        and args.metric == "value"
        and args.level in (None, len(code))
    ):
        # Full-length code at a stored level: the series ID is constructible.
        level = len(code)
        series_ids = [
            f"{cfg['prefix']}_{flow_code(args.flow)}_{level}d_{code}_{partner_code}"
            for partner_code in partner_codes
        ]
        if len(series_ids) == 1:
            body = (
                f"SELECT time::date AS month, value\n"
                f"FROM data_points\n"
                f"WHERE series_id = {sql_string(series_ids[0])}\n"
                f"  AND time >= DATE '{lo}' AND time < DATE '{hi}'\n"
                f"ORDER BY time;"
            )
            note = f"exact series: {series_ids[0]}"
        else:
            id_list = ",\n    ".join(sql_string(series_id) for series_id in series_ids)
            body = (
                f"SELECT time::date AS month, SUM(value) AS value\n"
                f"FROM data_points\n"
                f"WHERE series_id IN (\n    {id_list})\n"
                f"  AND time >= DATE '{lo}' AND time < DATE '{hi}'\n"
                f"GROUP BY 1\n"
                f"ORDER BY 1;"
            )
            note = (
                f"{len(series_ids)} historical partner-code series combined: "
                + ", ".join(series_ids)
            )
        return header(source, args, partner_name, level, note) + "\n" + body

    if args.metric != "value":
        if not cfg["qty_suffixes"]:
            fail(f"source '{source}' stores value series only — no quantity/weight")
        level = len(code)
        if level not in cfg["qty_levels"]:
            fail(
                f"source '{source}' stores quantity only at HS level(s) "
                f"{cfg['qty_levels']} — pass a full-length code at one of those levels"
            )
        if args.level not in (None, level):
            fail(
                "quantity queries require one exact stored HS code; --level must "
                "match the code length or be omitted"
            )
        ids = [
            f"{cfg['prefix']}_{flow_code(args.flow)}_{level}d_{code}_{partner_code}_{sfx}"
            for partner_code in partner_codes
            for sfx in cfg["qty_suffixes"]
        ]
        id_list = ",\n    ".join(sql_string(series_id) for series_id in ids)
        body = (
            f"SELECT s.series_id, s.measurement_units, dp.time::date AS month, dp.value\n"
            f"FROM series s JOIN data_points dp ON dp.series_id = s.series_id\n"
            f"WHERE s.series_id IN (\n    {id_list})\n"
            f"  AND dp.time >= DATE '{lo}' AND dp.time < DATE '{hi}'\n"
            f"ORDER BY s.series_id, dp.time;"
        )
        note = add_partner_code_note(
            "quantity units are product-specific — read measurement_units off "
            "each row and NEVER sum quantities across products",
            partner_codes,
        )
        return header(source, args, partner_name, level, note) + "\n" + body

    # Short (group) code over stored lines: aggregate via the commodity dimension.
    level = resolve_level(source, args.level)
    if len(code) not in (2, 4, 6):
        fail(
            f"--hs '{code}' is not a stored level for '{source}' and is not a "
            "2/4/6-digit HS group"
        )
    if len(code) >= level:
        fail(
            f"--hs '{code}' is not a stored level for '{source}' (levels {cfg['levels']}) "
            "and not shorter than the aggregation level — pass a full-length code, "
            f"or a 2/4/6-digit group with --level {level}"
        )
    joins, where = base_joins(source, args.flow, level, partner_codes)
    joins += "\n" + (
        "JOIN dimensions c ON c.series_id = s.series_id\n"
        f"  AND c.dimension_type = 'commodity' AND c.dimension_code LIKE '{code}%'"
    )
    where.append(f"dp.time >= DATE '{lo}' AND dp.time < DATE '{hi}'")
    conditions = "\n  AND ".join(where)
    body = (
        f"SELECT dp.time::date AS month, SUM(dp.value) AS value\n"
        f"{joins}\n"
        f"WHERE {conditions}\n"
        f"GROUP BY 1\nORDER BY 1;"
    )
    note = add_partner_code_note(
        f"HS group {code}* summed over HS-{level} lines", partner_codes
    )
    return header(source, args, partner_name, level, note) + "\n" + body


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--source", required=True, choices=sorted(SOURCES))
        p.add_argument(
            "--partner",
            required=True,
            help="partner code or name fragment (resolved against the bundled per-source map); "
            "'world' = the all-partner total row (census only)",
        )
        p.add_argument("--flow", required=True, choices=["imports", "exports"])
        p.add_argument(
            "--start", required=True, help="first month, YYYY-MM (inclusive)"
        )
        p.add_argument("--end", required=True, help="last month, YYYY-MM (inclusive)")
        p.add_argument(
            "--level",
            type=int,
            help="HS digit level (default: the source's international level)",
        )

    p_total = sub.add_parser("total", help="all-goods total for one partner")
    add_common(p_total)
    p_total.add_argument("--monthly", action="store_true", help="one row per month")

    p_products = sub.add_parser("products", help="top products for one partner")
    add_common(p_products)
    p_products.add_argument(
        "--group-by",
        default="2",
        choices=["2", "4", "6"],
        help="HS digits to group by (default 2)",
    )
    p_products.add_argument(
        "--top",
        type=limited_positive_int,
        default=25,
        help="rows to return, 1-50 (default 25)",
    )

    p_trend = sub.add_parser("trend", help="monthly trend for one HS code or group")
    add_common(p_trend)
    p_trend.add_argument(
        "--hs",
        required=True,
        help="HS code: full-length = exact series, 2/4/6-digit = summed group",
    )
    p_trend.add_argument(
        "--metric",
        default="value",
        choices=["value", "quantity"],
        help="default: value",
    )

    args = parser.parse_args()
    print(
        {"total": sql_total, "products": sql_products, "trend": sql_trend}[
            args.command
        ](args)
    )


if __name__ == "__main__":
    main()
