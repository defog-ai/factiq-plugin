---
type: llm
focus: last_message
weight: 2
---
The query restricts the result to exactly one HS code level, and the answer says why.

Pass if the SQL has a filter that pins the HS level to a single value (for example the `hs_level` dimension equal to '6', or equal to '8'), and the answer states that the levels contain each other so summing more than one level counts the same trade twice.

Fail if the query sums across HS levels, or if no HS-level filter is present.
