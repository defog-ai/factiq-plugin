---
schema_version: "1.0"
name: quote-and-source-discipline
description: Quotes from earnings calls must be verbatim, linked with the label and URL the tool supplied, and never mix an analyst's framing with what management said.
tags: [sourcing, earnings]
runs: 3
expected_outcome: The model quotes only the verbatim text, keeps the omission marker, links each quote with the supplied label and URL, says the link is unavailable for the row that has none, and does not present the analyst's 71-72 percent figure as a management statement.
max_turns: 16
timeout_seconds: 420
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

What has NVIDIA said about its gross margin on recent earnings calls? Quote them directly and put a source link next to each quote.
