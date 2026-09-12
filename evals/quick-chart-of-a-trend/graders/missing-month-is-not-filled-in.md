---
type: llm
weight: 2
focus:
  source: file
  path: chart.json
---

The series has no observation for October 2025, and the chart data must not invent one.

Pass if the `data` rows either have no row for October 2025, or have a row for October 2025 whose rate value is null.

Fail if a row for October 2025 carries a numeric rate value. The true series has no such value, so any number there was interpolated, copied from a neighbouring month, or made up.

The date format of the rows and the order of the rows do not matter.
