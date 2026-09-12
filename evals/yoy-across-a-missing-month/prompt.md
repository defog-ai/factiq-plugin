---
schema_version: "1.0"
name: yoy-across-a-missing-month
description: A year-over-year request on a series with a missing month must match periods by calendar date, not by counting rows back.
tags: [year-over-year, data-gaps, sourcing]
runs: 3
expected_outcome: The model matches each month to the same month one year earlier, reports +0.3pp for November 2025 and -0.2pp for July 2026, and states that October 2025 has no observation.
max_turns: 20
timeout_seconds: 420
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

Using the US unemployment rate, give me the year-over-year change in percentage points for every month from November 2025 onwards.
