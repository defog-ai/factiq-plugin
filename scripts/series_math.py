#!/usr/bin/env python3
"""Deterministic arithmetic on fetched FactIQ results — no in-context math.

Reads the payload JSON that run_sql / get_series return (save it to disk with
`python3 scripts/build_viz.py save --match "<distinctive fragment>" --out f.json`
so the bytes never pass through your output) and prints a computed table.
Use this instead of computing growth rates, shares, or unit conversions in
your own tokens: the script's arithmetic is exact and repeatable.

Subcommands:
  yoy      year-over-year % change (same month/quarter, previous year)
  ytd      calendar year-to-date cumulative total + YoY % vs prior-year YTD
  share    each group's % share of the per-period total (needs --group-col)
  index    rebase each group to 100 at --base YYYY-MM
  merge    concatenate several files into one long table, tagging each row
           with a label and optionally rescaling values (unit alignment)

Examples:
  python3 scripts/series_math.py yoy --file cn_imports.json
  python3 scripts/series_math.py share --file by_reporter.json --group-col reporter
  python3 scripts/series_math.py index --file trend.json --base 2022-01 --group-col reporter
  # India is US$ Million, Korea US$ Thousand -> align both to US$ Million:
  python3 scripts/series_math.py merge --input india=india.json \
      --input korea=korea.json:0.001
"""
from __future__ import annotations

import argparse
import json
import sys

TIME_HINTS = ("time", "month", "date", "t", "period", "quarter", "year")


def fail(message: str, code: int = 1) -> None:
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(code)


def load_table(path: str) -> tuple[list[str], list[list]]:
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read payload {path}: {exc}")
    if isinstance(payload, dict) and "columns" in payload and "results" in payload:
        return list(payload["columns"]), [list(r) for r in payload["results"]]
    fail(
        f"{path} is not a FactIQ payload (expected an object with 'columns' and "
        "'results' — the shape build_viz.py save writes)"
    )
    raise AssertionError  # unreachable


def pick_col(columns: list[str], requested: str | None, hints: tuple[str, ...], kind: str) -> int:
    if requested:
        if requested not in columns:
            fail(f"--{kind}-col '{requested}' not in columns {columns}")
        return columns.index(requested)
    for hint in hints:
        if hint in columns:
            return columns.index(hint)
    fail(f"cannot guess the {kind} column in {columns} — pass --{kind}-col")
    raise AssertionError  # unreachable


def pick_value_col(columns: list[str], requested: str | None, taken: set[int]) -> int:
    if requested:
        if requested not in columns:
            fail(f"--value-col '{requested}' not in columns {columns}")
        return columns.index(requested)
    numericish = [i for i, c in enumerate(columns) if i not in taken]
    if len(numericish) == 1:
        return numericish[0]
    fail(f"cannot guess the value column in {columns} — pass --value-col")
    raise AssertionError  # unreachable


def year_month(text) -> tuple[int, int]:
    s = str(text)
    parts = s.split("T")[0].split(" ")[0].split("-")
    if len(parts) < 2 or not (parts[0].lstrip("-").isdigit() and parts[1].isdigit()):
        fail(f"cannot parse a date out of '{text}' — expected ISO YYYY-MM[-DD]")
    return int(parts[0]), int(parts[1])


def as_float(v, context: str) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        fail(f"non-numeric value {v!r} in {context}")
    raise AssertionError  # unreachable


def emit(header: list[str], rows: list[list]) -> None:
    print("\t".join(header))
    for row in rows:
        print("\t".join(f"{v:.6g}" if isinstance(v, float) else str(v) for v in row))


def split_rows(args, columns, rows):
    """Return {group: [(year, month, timestr, value)]} sorted by time."""
    t_idx = pick_col(columns, args.time_col, TIME_HINTS, "time")
    g_idx = columns.index(args.group_col) if args.group_col else None
    if args.group_col and args.group_col not in columns:
        fail(f"--group-col '{args.group_col}' not in columns {columns}")
    v_idx = pick_value_col(columns, args.value_col, {t_idx} | ({g_idx} if g_idx is not None else set()))
    groups: dict[str, list] = {}
    for row in rows:
        y, m = year_month(row[t_idx])
        key = str(row[g_idx]) if g_idx is not None else ""
        groups.setdefault(key, []).append((y, m, str(row[t_idx]).split("T")[0], as_float(row[v_idx], f"row {row}")))
    for series in groups.values():
        series.sort()
    return groups


def cmd_yoy(args) -> None:
    columns, rows = load_table(args.file)
    groups = split_rows(args, columns, rows)
    out = []
    for key, series in sorted(groups.items()):
        prior = {(y, m): v for y, m, _, v in series}
        for y, m, t, v in series:
            prev = prior.get((y - 1, m))
            pct = (v / prev - 1.0) * 100.0 if prev not in (None, 0) else None
            out.append(([key] if key else []) + [t, v, "" if pct is None else round(pct, 4)])
    header = (["group"] if args.group_col else []) + ["time", "value", "yoy_pct"]
    emit(header, out)


def cmd_ytd(args) -> None:
    columns, rows = load_table(args.file)
    groups = split_rows(args, columns, rows)
    out = []
    for key, series in sorted(groups.items()):
        cum: dict[tuple[int, int], float] = {}
        running: dict[int, float] = {}
        for y, m, t, v in series:
            running[y] = running.get(y, 0.0) + v
            cum[(y, m)] = running[y]
        for y, m, t, v in series:
            prev = cum.get((y - 1, m))
            pct = (cum[(y, m)] / prev - 1.0) * 100.0 if prev not in (None, 0) else None
            out.append(([key] if key else []) + [t, cum[(y, m)], "" if pct is None else round(pct, 4)])
    header = (["group"] if args.group_col else []) + ["time", "ytd_value", "ytd_yoy_pct"]
    emit(header, out)


def cmd_share(args) -> None:
    if not args.group_col:
        fail("share needs --group-col (whose share of the per-period total)")
    columns, rows = load_table(args.file)
    groups = split_rows(args, columns, rows)
    totals: dict[str, float] = {}
    for series in groups.values():
        for _, _, t, v in series:
            totals[t] = totals.get(t, 0.0) + v
    out = []
    for key, series in sorted(groups.items()):
        for _, _, t, v in series:
            share = v / totals[t] * 100.0 if totals[t] else None
            out.append([key, t, v, "" if share is None else round(share, 4)])
    emit(["group", "time", "value", "share_pct"], out)


def cmd_index(args) -> None:
    by, bm = year_month(args.base)
    columns, rows = load_table(args.file)
    groups = split_rows(args, columns, rows)
    out = []
    for key, series in sorted(groups.items()):
        base = next((v for y, m, _, v in series if (y, m) == (by, bm)), None)
        if base in (None, 0):
            fail(f"group '{key or '(all)'}' has no usable value at base {args.base}")
        for _, _, t, v in series:
            out.append(([key] if key else []) + [t, round(v / base * 100.0, 4)])
    header = (["group"] if args.group_col else []) + ["time", f"index_{args.base}=100"]
    emit(header, out)


def cmd_merge(args) -> None:
    out = []
    header: list[str] | None = None
    for spec in args.input:
        if "=" not in spec:
            fail(f"--input must be label=path[:factor], got '{spec}'")
        label, rest = spec.split("=", 1)
        factor = 1.0
        if ":" in rest and not rest.endswith(".json"):
            path, factor_s = rest.rsplit(":", 1)
            factor = as_float(factor_s, f"--input {spec}")
        else:
            path = rest
        columns, rows = load_table(path)
        if header is None:
            header = ["source"] + columns
        elif columns != header[1:]:
            fail(f"{path} columns {columns} differ from first file's {header[1:]}")
        for row in rows:
            out.append([label] + [
                as_float(v, f"{path} row {row}") * factor if isinstance(v, (int, float)) else v
                for v in row
            ])
    emit(header or ["source"], out)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--file", required=True, help="payload JSON (columns/results shape)")
        p.add_argument("--time-col", help="time column (default: guessed)")
        p.add_argument("--value-col", help="value column (default: guessed)")
        p.add_argument("--group-col", help="column that splits rows into series (e.g. reporter)")

    for name, fn in (("yoy", cmd_yoy), ("ytd", cmd_ytd), ("share", cmd_share)):
        p = sub.add_parser(name)
        add_common(p)
        p.set_defaults(fn=fn)

    p_index = sub.add_parser("index")
    add_common(p_index)
    p_index.add_argument("--base", required=True, help="base period YYYY-MM (=100)")
    p_index.set_defaults(fn=cmd_index)

    p_merge = sub.add_parser("merge")
    p_merge.add_argument(
        "--input", action="append", required=True,
        help="label=path[:factor] — repeat per file; factor rescales values (unit alignment)",
    )
    p_merge.set_defaults(fn=cmd_merge)

    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
