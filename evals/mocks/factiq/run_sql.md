{
  "columns": [
    "time",
    "value",
    "series_id"
  ],
  "results": [
    ["2026-08-01", 4.1, "LNS14000000"],
    ["2026-07-01", 4.1, "LNS14000000"],
    ["2026-06-01", 4.2, "LNS14000000"],
    ["2026-05-01", 4.3, "LNS14000000"],
    ["2026-04-01", 4.3, "LNS14000000"],
    ["2026-03-01", 4.3, "LNS14000000"],
    ["2026-02-01", 4.4, "LNS14000000"],
    ["2026-01-01", 4.3, "LNS14000000"],
    ["2025-12-01", 4.4, "LNS14000000"],
    ["2025-11-01", 4.5, "LNS14000000"],
    ["2025-09-01", 4.4, "LNS14000000"],
    ["2025-08-01", 4.3, "LNS14000000"],
    ["2025-07-01", 4.3, "LNS14000000"],
    ["2025-06-01", 4.1, "LNS14000000"],
    ["2025-05-01", 4.3, "LNS14000000"],
    ["2025-04-01", 4.2, "LNS14000000"],
    ["2025-03-01", 4.2, "LNS14000000"],
    ["2025-02-01", 4.2, "LNS14000000"],
    ["2025-01-01", 4.0, "LNS14000000"],
    ["2024-12-01", 4.1, "LNS14000000"],
    ["2024-11-01", 4.2, "LNS14000000"],
    ["2024-10-01", 4.1, "LNS14000000"],
    ["2024-09-01", 4.1, "LNS14000000"],
    ["2024-08-01", 4.2, "LNS14000000"],
    ["2024-07-01", 4.2, "LNS14000000"],
    ["2024-06-01", 4.1, "LNS14000000"],
    ["2024-05-01", 3.9, "LNS14000000"],
    ["2024-04-01", 3.9, "LNS14000000"],
    ["2024-03-01", 3.9, "LNS14000000"],
    ["2024-02-01", 3.9, "LNS14000000"],
    ["2024-01-01", 3.7, "LNS14000000"]
  ],
  "row_count": 31,
  "truncated": false,
  "schemas_touched": [
    "bls"
  ],
  "coverage_note": "This monthly series has no observation for 2025-10-01 (1 of 32 expected monthly periods between 2024-01-01 and 2026-08-01 is missing). Never compute period-over-period changes with a fixed row offset (LAG/LEAD n, or the row n places back): the n values after a gap (LEAD: the n before it) land on the wrong period. Join on the calendar period instead (date_trunc('month', prior.time) = date_trunc('month', cur.time) - interval '1 year'; the stored day of the month varies by source, so never compare exact dates). State the missing period(s) in the answer, do not interpolate them, and label any aggregate that spans a gap as partial (for example \"Q4 2025 average of two months\").",
  "missing_period_count": 1,
  "missing_periods": [
    "2025-10-01"
  ]
}
