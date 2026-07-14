# Earnings-Intelligence Report Pattern

Company and earnings analysis from what management said live
(`search_earnings_transcripts`), what the company filed (`sec` schema), what
it formally guided (`sec_guidance`), how the market priced it
(`get_market_data`), and — FactIQ's edge — whether the macro data agrees.

The dialectic here: the **thesis** is the story management tells on the call
and the consensus narrative around it. The **antithesis** is the variant
perception fetched from data management doesn't control — filed actuals,
disclosure behavior (what they stopped breaking out, what they refused to
quantify), the analyst pressure map, and the government statistics behind
every macro claim. The **synthesis** is the claim that explains both: what
the narrative gets right, where it flatters, and what would falsify it.

## Trigger Phrases

"What did <company> say", "summarize the earnings call", "earnings note on
X", "did they guide up or down", "what is the Street worried about",
"compare what <A> and <B> said about <theme>", "is management's story
consistent with the data", "who mentioned <theme> this quarter".

## Before Anything Else: Coverage

`search_earnings_transcripts(search_target="coverage")` — with
`company_filter` when the question names companies. Coverage is per-ticker
and mostly the **latest call only**. If the ticker isn't covered, say so and
fall back to `sec` + `get_market_data`; never silently substitute. Absence
of a claim is never evidence management didn't say it — only that it isn't
in covered calls.

## The Five Workflows

### 1. Single-call earnings note ("what did MU say?")

1. Coverage check, then the claim spine: empty `query` +
   `company_filter="MU"` (add `quarter_filter` if multiple calls exist),
   `limit=50`, `detail=true` — rows come back in spoken order.
2. Same call's Q&A dynamics: `search_target="pressure_points"`, same
   filters. The `response_quality` distribution and any `refused_number`
   rows are the "what the Street couldn't get" section.
3. `search_target="disclosure_profile"` — what this company routinely breaks
   out vs. withholds, so you can flag anything volunteered off-pattern (a
   company suddenly quantifying something it usually withholds is a story).
4. Antithesis pass: pair the 3–5 most checkable claims with filed data —
   `sec` XBRL for actuals, `sec_kpi` for operating metrics, `sec_guidance`
   for the formal targets — and the call-window price move
   (`get_market_data`, TIME_SERIES_DAILY around `calendar_date`).
5. Report: summary (the synthesis, not a recap) → guidance table → quote
   panels for the load-bearing verbatim statements → verification charts →
   watch-list from the refusals.

### 2. Claim-vs-data verification (the FactIQ edge)

Management routinely makes macro claims — "the consumer is trading down",
"freight costs have eased", "power constraints gate datacenter builds".
Every such claim names a government series FactIQ has:

| Claim family heard on calls | Verify against |
|---|---|
| Consumer health / trading down / cohort behavior (`cohort_behavior`) | `census` retail sales, `bls` CPI + real earnings, `frb` G.19 consumer credit |
| Input costs, freight, energy (`cost_margin_bridge`, `stated_risk_constraint`) | `bls` PPI, `eia` energy prices, `bts` freight, `portwatch` shipping |
| Demand magnitude / industry TAM (`demand_magnitude`) | `census` shipments/orders, trade schemas for the import/export view, sector KPIs across `sec_kpi` peers |
| Hiring, wage pressure (`labor_org`) | `bls` payrolls/JOLTS/ECI |
| Tariffs, policy, regulation (`regulatory_policy`) | customs/trade schemas, `policy` communications |

Chart the claim and the series together; title the chart with the verdict
("Gasoline demand supports WMT's consumer-stress read"). Say plainly when
the data contradicts or cannot yet test the claim.

### 3. Guidance scorecard (beat/miss/follow-through)

1. Spoken targets: `claim_family="forward_conviction"` and
   `claim_family="prior_view_revision"` for the ticker (revisions carry
   `vs_prior` — the delta is the payload).
2. Formal targets: `sec_guidance` series
   (`{TICKER}_{metric}[_growth]_guidance_{period}_{bound}_*`) — check
   whether the spoken and filed guidance agree.
3. Actuals as they land: `sec` XBRL / `get_market_data` INCOME_STATEMENT.
4. Output: one table — metric, guided value/range, vs-prior, spoken vs
   formal, actual, verdict. `falsifiable=true` claims (in `detail` output)
   are the rows this table is made of.

### 4. Cross-company theme sweep ("who's saying what about <theme>?")

1. One query, no ticker filter: `query="<theme terms>"`, `limit=50`. All
   query terms must match — sweep synonyms in separate calls ("capex",
   "capital expenditure", "capacity investment") and merge.
2. Group hits by `reporting_ticker` and `claim_family`; split
   `company_asserted` from `analyst_hypothesized` (the latter is the
   Street's framing, not the companies').
3. Disclosure asymmetry is its own finding: for the central tickers, pull
   `disclosure_profile` — who breaks the theme out vs. who withholds it.
4. `section` matters: a theme confined to `qa` is one analysts force;
   a theme in `prepared_remarks` is one management leads with.

### 5. Q&A pressure analysis ("what is the Street trying to find out?")

`search_target="pressure_points"` for the ticker or theme. Read it as a
map of information asymmetry: `topic_pressed` × `response_quality`. The
`declined`/`deflected` rows with a `refused_number` are the known unknowns —
list them as the watch-list ("what would resolve this: next quarter's
disclosure of X"). `linked_claim_id` ties a refusal back to the claim it
guards. `tone_note` (in `detail` output) is subjective — attribute it as a
reading if used at all.

## Data Source Ladder

1. `search_earnings_transcripts` — spoken claims, Q&A, disclosure habits.
2. `sec` via `run_sql` — filed XBRL segment/product/geo detail, `sec_guidance`
   formal targets, `sec_kpi` operating metrics.
3. `get_market_data` — consolidated statements (faster than XBRL), quotes,
   price history for reaction windows.
4. Macro schemas (`bls`/`census`/`eia`/`frb`/trade/`policy`) — the
   verification layer for any macro claim.
5. Never `run_sql` on the `transcripts` schema — it is bespoke and gated;
   the tool is the only supported access.

## Default Report Shape

Summary states the synthesis with numbers. Then: (1) what management said —
guidance table + quote panels; (2) what the data says — verification charts,
filed vs. spoken; (3) what the Street pressed on — pressure points and
refusals; (4) watch-list — the falsifiers and when they print (next earnings
date, next macro release). Fetch the `earnings` style guide
(`get_style_guides(["earnings"])`) and follow it: verbatim-only quotes with
speaker/role/ticker/period, spoken-vs-filed source labels, quote panels not
quote-filled text panels.

## Guardrails

- `assertion_status` is load-bearing: `analyst_hypothesized` belongs to the
  analyst; `mgmt_declined_to_confirm` is a refusal, and often the finding.
- Retrieval is lexical. Two empty searches ≠ silence — sweep the company's
  own vocabulary first (their term for capex, their segment names).
- A % claim without its `denominator` doesn't go in a table.
- Spoken ≠ filed ≠ formal guidance: label each, and when two disagree, that
  disagreement is content, not noise.
- Don't build a scorecard from one quarter of coverage — say what the
  coverage window is.

## Methodology Language To Include

"Earnings-call claims are extracted from live-call transcripts into
quote-anchored structured rows; quotes are verbatim, attributed to speaker
and fiscal period. Spoken statements are distinguished from filed financials
(SEC XBRL) and formally issued guidance (sec_guidance). Coverage:
<tickers/quarters from the coverage call>."
