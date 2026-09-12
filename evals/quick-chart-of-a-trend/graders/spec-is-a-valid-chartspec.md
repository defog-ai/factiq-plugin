---
type: llm
weight: 3
focus:
  source: file
  path: chart.json
---

The file is a ChartSpec object in the plugin's local chart format.

Pass if all of these hold:

- It is one JSON object with the keys `title`, `type`, `xField`, `series` and `data`.
- `xField` is an object with a `key`, `series` is a non-empty array of objects that each have a `key`, and `data` is an array of wide-format rows: one object per month, each with the x value under the `xField` key and the unemployment rate under a series key.
- `data` covers the months from January 2024 to August 2026, in either order.
- A `sources` entry names the Bureau of Labor Statistics (or BLS) as the source.

Fail if any key is missing, if `data` is long-format (one row per series and period), if the rows carry no rate values, or if the file is not valid JSON.

The chart `type`, whether an `id` is present, axis labels, and whether an `annotations` list is present do not matter.
