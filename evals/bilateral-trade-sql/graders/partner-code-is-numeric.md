---
type: llm
focus: last_message
weight: 3
---
The query filters the trade partner by China customs' own numeric partner code for the United States, which is `502`.

Pass if the shown SQL matches the partner dimension against `502`.

Fail if the query matches the partner by a name such as 'United States' or 'USA', by an ISO code such as 'US' or 'USA', by any other number, or if there is no partner filter at all. Those are the values a hand-written query uses, and they return nothing or the wrong rows in this schema.
