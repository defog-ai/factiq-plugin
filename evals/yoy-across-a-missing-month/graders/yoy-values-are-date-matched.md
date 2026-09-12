---
type: llm
focus: last_message
weight: 4
---
The answer compares each month with the same calendar month one year earlier. Check the reported year-over-year changes, in percentage points, against these correct values:

- November 2025: +0.3
- December 2025: +0.3
- January 2026: +0.3
- February 2026: +0.2
- July 2026: -0.2
- August 2026: -0.2

Pass only if every one of these six months is reported with the correct value (sign and magnitude). Wording may vary: "+0.3pp", "0.3 percentage points higher", "up 0.3" are all acceptable.

Fail if the answer reports November 2025 as +0.4, December 2025 as +0.2, or July 2026 as -0.1. Those are the values produced by counting twelve rows back instead of matching the calendar month, and the series has a missing month that makes the two methods differ.

Fail if any of the six months is absent from the answer.
