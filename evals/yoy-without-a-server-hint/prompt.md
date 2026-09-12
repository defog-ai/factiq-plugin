---
schema_version: "1.0"
name: yoy-without-a-server-hint
description: The same year-over-year request as yoy-across-a-missing-month, but the mocked server sends no note about the missing month, so the calendar-date matching and the statement of the gap must come from the skill alone.
tags: [year-over-year, data-gaps, sourcing, no-server-hint]
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
