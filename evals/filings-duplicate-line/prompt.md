---
schema_version: "1.0"
name: filings-duplicate-line
description: When a company files the same figure twice in one report, the copy labelled "reported line 2" must not be added to the first, and the figure must carry the filing's own source link.
tags: [filings, sourcing]
runs: 3
expected_outcome: The model reports Packaging segment revenue of 2,311.3 million US dollars for the quarter ended June 2026, links the 10-Q at sec.gov, and does not report a doubled figure of 4,622.6 million.
max_turns: 15
timeout_seconds: 300
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

What revenue did Packaging Corporation of America (ticker PKG) report for its Packaging segment in the quarter that ended in June 2026, according to its own filing? Give me the figure and a link to the filing.
