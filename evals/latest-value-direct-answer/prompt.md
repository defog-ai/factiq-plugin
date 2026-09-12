---
schema_version: "1.0"
name: latest-value-direct-answer
description: A one-number question must get a one-sentence answer with the period and the source, and no chart and no report file.
tags: [output-mode, sourcing]
runs: 3
expected_outcome: The model answers in prose that the latest US unemployment rate is 4.1 percent in August 2026, names the Bureau of Labor Statistics, and writes no chart script and no report file.
max_turns: 12
timeout_seconds: 300
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

What is the latest US unemployment rate?
