---
type: llm
weight: 2
focus:
  source: file
  path: chart.json
---

The chart `title` is a claim, not a description.

Pass if the title names the country (US or United States), names the metric (unemployment rate), and states a finding with at least one number: for example a change from one level to another over the period, a peak value with its month, or the latest level compared with the start.

Fail if the title is only a description such as "US unemployment rate, 2024-2026" or "Unemployment rate trend", or if it has no number in it.

Wording, capitalisation, and the exact numbers chosen do not matter as long as they are values from the data.
