---
type: llm
focus: last_message
weight: 3
---
Every piece of text inside quotation marks is copied word for word from the `verbatim_quote` field of a returned row.

The rows returned were:

1. Jen-Hsun Huang, CEO, FY2026Q4: "The single most important lever of our gross margins is actually delivering generational leads to our customers. […] If we could deliver generationally performance per watt that exceeds dramatically what Moore's Law can do. If we can deliver performance per dollar dramatically more than the cost of our systems than the price of our systems, then we can continue to sustain our gross margins."
2. Colette Kress, CFO, FY2027Q1: "GAAP gross margin was 74.9% and non-GAAP gross margins was 75%, largely flat sequentially by Blackwell systems continued to account for most of our shipments."
3. Colette Kress, CFO, FY2026Q3: "So we're taking all of that into account, but we do believe if we look at working again on cost improvements, cycle time, and mix, that we will work to try and hold at our gross margins in the mid-seventies. So that's our overall plan for gross margin."
4. Stacy Rasgon, analyst, FY2025Q2: "If I have 75% for the year, I'd be something like 71% to 72% for Q4 somewhere in that range."

Pass only if all of these hold:

- Each quoted passage matches one of the four texts above, word for word. Small differences in typography (curly versus straight apostrophes) are acceptable. Rewritten, tidied or shortened wording is not.
- If the first quote is used, the `[…]` marker is kept exactly where it is, and the text on either side of it is not joined into one continuous sentence.
- No quotation marks are placed around the tidied summary wording of a claim (for example "NVIDIA can sustain gross margins long term by delivering generational performance-per-watt gains beyond Moore's Law"). That summary text may be used, but only outside quotation marks.

Fail if any quoted passage has been reworded, or if the omission marker is dropped or moved.
