---
schema_version: "1.0"
name: quick-chart-of-a-trend
description: A single-trend question must produce one ChartSpec file with a claim for a title, an ASCII preview rendered by the bundled script and pasted into the answer, and no invented value for the missing month.
tags: [output-mode, charts, data-gaps]
runs: 3
expected_outcome: The model fetches the unemployment series, writes chart.json as a valid ChartSpec whose title states the change in the rate over the period, renders it with term_chart.py, pastes the ASCII preview into a fenced code block, and says that October 2025 has no observation.
max_turns: 25
timeout_seconds: 420
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

Show me how the US unemployment rate has moved since the start of 2024. Save the chart spec as `chart.json` in the current directory.
