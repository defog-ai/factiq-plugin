---
type: llm
weight: 1
focus: last_message
---

Every link in the answer is one the data supplied.

Pass if the only link or links in the answer point to the 10-Q document at `https://www.sec.gov/Archives/edgar/data/75677/000119312526339405/pkg-20260630.htm`, or if the answer has that link and no other.

Fail if the answer includes any other URL: a company investor-relations page, a different EDGAR path, a news article, or a generic search page.

Whether the link is written as bare text or as a Markdown link, and its link text, do not matter.
