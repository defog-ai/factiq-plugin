---
schema_version: "1.0"
name: bilateral-trade-sql
description: A bilateral-trade query must be built with the bundled SQL generator, so the partner code, the HS level and the value/quantity split are right.
tags: [bilateral-trade, sql]
runs: 3
expected_outcome: The model runs the bundled trade_sql.py generator and shows a query that filters the partner by China customs' numeric code 502, restricts to exactly one HS level, and keeps quantity series out of the value total.
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

I need China's monthly goods exports to the United States for 2025, taken from China's own customs data. Show me the exact query you would run, and explain the partner filter and the HS-level filter. I want to check the query before we pull any numbers.
