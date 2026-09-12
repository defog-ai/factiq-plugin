---
type: llm
focus: last_message
weight: 2
---
The query adds up value series only, and keeps quantity series out.

Pass if the SQL restricts the series to the value unit (for example `measurement_units = 'US$'`), or otherwise excludes the quantity series, and the answer names the unit the result is in.

Fail if nothing separates value rows from quantity rows, because the schema holds both for the same partner and code and summing them together is meaningless.
