---
schema_version: "1.0"
name: unrelated-coding-request
description: A plain coding request must be answered directly, without loading the FactIQ skill or calling any FactIQ data tool.
tags: [should-not-fire]
runs: 3
expected_outcome: The model answers the Python question itself and calls no FactIQ tool.
max_turns: 8
timeout_seconds: 240
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

In Python, what is the difference between `list.sort()` and `sorted(list)`?
