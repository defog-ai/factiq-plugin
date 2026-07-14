---
name: fx-analysis
description: >
  Produce macroeconomically grounded foreign-exchange analysis with bilateral,
  horizon-matched evidence. Use for questions about FX or currency drivers,
  fundamentals, intervention effects on a currency pair, competitiveness,
  reserve adequacy in an FX context, currency valuation, or currency outlooks.
  Do not use for a narrow latest-quote or chart-only request that asks for no
  explanation, or for central-bank operations or sterilization questions that
  do not ask about a currency outcome.
---

# FX Analysis

Explain exchange-rate outcomes with relative economic evidence, not a list of
one country's indicators or a deterministic causal score. Use the existing
`$factiq` skill for data discovery, SQL, computation, charting, and
`share_report`; let this skill govern the FX research design and interpretation.
For broad questions, follow FactIQ's dialectical report method and publish a
report unless the user asks for a narrower output.

## Define the outcome first

1. State the pair, base currency, quote currency, exact source convention,
   analysis window, and exchange-rate regime. For quote units per one base unit,
   a rise means base appreciation and quote depreciation. Verify rather than
   infer the convention from the series name.
   - If the pair or currency is missing, ask for it before performing a
     bilateral valuation or driver analysis; infer it only when prior context
     makes both currencies unambiguous.
   - If no analysis duration is given, ask for one rather than selecting an
     arbitrary move. If a stated relative window is ambiguous, use a trailing
     interval ending on the last common market close, state the exact dates and
     close/time zone, and invite correction. For "last quarter," use the most
     recently completed calendar or relevant fiscal quarter, state which one
     and its exact dates, and clarify when the user's convention could change
     the answer.
2. Measure the move over the requested window and distinguish nominal bilateral
   FX from NEER and REER. Use effective rates to test whether the move is broad
   currency strength or mainly bilateral; do not treat NEER or REER as an
   independent cause of the same move. When diagnosing broad versus bilateral
   movement, compare broad/effective measures for both the base and quote
   currencies where available; disclose a missing side instead of inferring it
   from the bilateral rate.
3. Identify the relevant horizon before selecting explanations. If the user
   compares horizons, analyze each separately instead of forcing one story
   across both. For a multi-year window, measure the full-window result and
   segment material turning points so opposing cycles are not hidden by two
   endpoints.

## Analyze a relative price bilaterally

Compare both economies using concept-aligned measures. A domestic level alone
cannot explain a bilateral relative price. For each candidate driver:

- compute or describe the base-minus-quote gap and state how its direction would
  pressure the quoted pair;
- fetch both sides from their primary producers where possible;
- query separate FactIQ schemas separately, then align and compute locally;
- pair an observed relative driver with mechanism evidence such as current
  accounts, capital flows, or verified intervention; and
- fetch the strongest competing explanation rather than relegating it to a
  generic caveat.

Use this horizon map:

| Horizon | Evidence to prioritize | Evidence not to overclaim |
|---|---|---|
| Short run: days to months | Policy surprises and expectations, matched expected returns or yields, liquidity and risk conditions, market repricing, capital flows, verified intervention | Quarterly fundamentals silently forward-filled to a daily move; PPP or productivity as a trading signal |
| Medium run: quarters to a few years | Relative policy paths, inflation and growth differentials, current accounts, terms of trade, direct/portfolio/other-investment flows | A single event or correlation as the whole explanation |
| Long run: multi-year | PPP and comparative prices, productivity and competitiveness, external balance sheets, reserve adequacy, fiscal sustainability | A precise near-term forecast from slow-moving benchmarks |

When the window crosses horizons, show which evidence belongs to which window
and how publication lags constrain the conclusion.

## Build the evidence stack

Test the relevant driver families, retaining contradictory results:

1. policy rates, policy expectations, and matched-maturity sovereign yields;
2. inflation, real-rate adjustments, relative growth, and expected returns;
3. current accounts, trade balances, and terms of trade;
4. direct-, portfolio-, and other-investment transactions;
5. IIP assets and liabilities, securities holdings, external debt, and reserves;
6. published intervention transactions and the monetary-policy regime;
7. fiscal balances, debt burdens, interest costs, and comparable yields or
   spreads; and
8. PPP, productivity, competitiveness, safe-haven, and global-risk evidence.

Prioritize families whose mechanism and frequency match the question. At
minimum fetch the FX outcome, one concept-aligned relative driver, mechanism
evidence, and the strongest plausible contradiction. Expand to other families
when the prompt, horizon, or initial evidence makes them material; stop when the
ranked conclusion is stable and remaining families are unlikely to change it.
Do not imply that an untested family was ruled out. Name material untested or
missing evidence and explain how it limits confidence.

## Keep transactions, positions, and intervention distinct

- Treat balance-of-payments transactions as flows over a period. Treat IIP,
  reserves, securities holdings, and debt as stocks at a point in time.
- Preserve gross versus net, assets versus liabilities, counterparties,
  accounting signs, and valuation conventions. Do not relabel valuation changes
  as capital flows; the exchange rate can itself cause valuation changes.
- Do not call a reserve-stock change intervention. Require published currency
  purchases, sales, or equivalent transaction evidence before making that
  claim. Equivalent evidence means an official transaction-flow disclosure of
  executed spot, forward, or derivative purchases or sales with a documented
  method; a change in a forward-book or reserve stock does not qualify. Reserve
  stocks can also move because of valuation, income, reclassification, and
  other balance-sheet effects.
- If transaction evidence is unavailable, say that intervention is unverified.
  Classify supporting timing or reserve evidence only as consistent but
  unproven, not causal proof.
- Separate whether intervention **occurred** from whether it **drove** the pair.
  Direct transaction evidence can establish occurrence. Attribute a material
  exchange-rate effect only when direction, timing, size relative to market
  liquidity, and mechanism align after testing competing bilateral drivers.
  Without a credible counterfactual, prefer "contributed" or "leaned against"
  and leave the size of the effect unquantified.

## Define reserve and fiscal measures

For every reserve-adequacy measure, name the reserve concept and denominator,
use compatible currencies and periods, show the formula, and cite the source:

- import cover = usable reserves / average monthly imports;
- short-term-debt cover = usable reserves / short-term external debt; and
- broad-money cover = usable reserves / broad money.

Document whether reserves are gross or net and whether gold, SDRs, or other
less-liquid assets are included. Define the debt maturity convention and the
import, debt, or money period and vintage. Do not compare ratios whose
denominators differ without an explicit caveat.

For fiscal comparisons, document the government perimeter; overall versus
primary balance; gross versus net debt; cash versus accrual basis; nominal GDP
denominator, period, and vintage; and the maturity and benchmark behind each
yield or spread. Show the formula for every computed balance/GDP, debt/GDP,
interest/revenue, or yield-spread measure. Describe measurable sustainability
evidence rather than inventing a normative credibility score.

## Treat long-run benchmarks and proxies honestly

- Use PPP and comparative price levels as long-run valuation anchors, not
  near-term forecasts. State the price basket, base or benchmark, formula, and
  limitations before calling a currency overvalued or undervalued.
- Label productivity, Balassa-Samuelson, competitiveness, and safe-haven
  measures as documented indices or proxies unless a primary producer
  publishes a direct measure and methodology.
- Name every proxy, explain its mechanism, and state its limitations. A
  Balassa-Samuelson test needs relative tradable/non-tradable productivity,
  wages, and prices; broader productivity or sector mappings are proxies.
- Do not create a synthetic FX-fundamentals, intervention, or safe-haven score.

## Align before comparing

Before calculating a gap, ratio, relationship, or as-of join, align or disclose
the mismatch in:

- unit, scale, currency, index base, and sign convention;
- maturity, benchmark instrument, and credit risk;
- nominal versus real basis;
- seasonal and calendar adjustment;
- fixed versus changing country or currency-area membership;
- frequency, reference period, and missing-value treatment; and
- observation, publication, retrieval, and vintage dates.

Never silently forward-fill a monthly or quarterly fundamental onto daily FX.
Aggregate FX to a compatible frequency or show separately aligned panels. For
an as-of join, expose each source date and its staleness. Preserve revisions and
explain whether an imperfect comparison remains informative. Choose the yield
instrument that best matches the mechanism under study: policy expectations
usually favor OIS or policy-sensitive maturities, while sovereign comparisons
must disclose credit and liquidity differences. Do not silently substitute a
Bund, area aggregate, or convergence yield for another concept.
For current-account comparisons, align currency and accounting basis or
normalize both sides to GDP using compatible GDP definitions, periods, and
vintages.

## Start from primary producers

Use this map as a discovery plan, not a guarantee that every series exists at
every frequency:

| Channel | United States | Euro area | India |
|---|---|---|---|
| FX outcome | Federal Reserve H.10, broad dollar indices, or live market FX | ECB bilateral and effective rates | RBI bilateral, NEER, and REER indices |
| Policy and yields | Federal Reserve H.15 and US Treasury | ECB policy rates and comparable sovereign or area yields | RBI key rates and government-securities data |
| Prices and growth | BLS and BEA | Eurostat and ECB | MoSPI and RBI |
| External transactions | BEA international transactions | ECB balance-of-payments and current-account data | RBI balance-of-payments and international-trade data |
| Positions, debt, reserves | BEA IIP, US Treasury holdings, official reserves | ECB IIP, external-sector, and reserve-assets data | RBI reserves, IIP, and external-debt data |
| Cross-economy PPP and fiscal context | IMF or World Bank when their concepts are more comparable | IMF or World Bank when their concepts are more comparable | IMF or World Bank when their concepts are more comparable |

Preserve the producer and dataset for every empirical claim, plus the original
series identifier and source URL where available. If an identifier or URL is
not exposed, say so rather than inventing one. FRED can be an access or
discovery layer, but attribute Federal Reserve, BLS, BEA, Treasury, and other
government series to their original producer rather than to FRED. Never
conflate the euro area with the EU; retain the provider's membership definition.

## Calibrate conclusions

Use the same labels consistently:

- **Supported:** direct or strong primary evidence matches the expected
  direction, timing, and mechanism after the strongest competing explanation
  has been tested.
- **Consistent but unproven:** correlation, event timing, or proxy evidence
  fits the explanation, but the mechanism, transaction, or counterfactual is
  missing.
- **Inconclusive:** material evidence is unavailable, conceptually mismatched,
  or mixed enough that no explanation dominates.
- **Contradicted:** reliable evidence has the wrong direction or timing, or a
  competing explanation better accounts for the outcome.

Do not assign causal percentages or quantify a policy effect without a stated
identification design and defensible counterfactual.

## Structure a broad FX report

1. Define the pair, quotation direction, move, window, regime, and horizon.
2. Compare both economies' market pricing, policy, matched yields, inflation,
   growth, and expected-return evidence.
3. Assess current accounts and financial flows without mixing transactions and
   positions.
4. Add verified intervention, reserve adequacy, external balance sheets, fiscal
   context, competitiveness, PPP, productivity, and safe-haven evidence when
   relevant; disclose unavailable channels.
5. Stage the strongest headline explanation against the strongest fetched
   contradiction. Reconcile them rather than forcing a single-factor story.
6. Rank short-, medium-, and long-run pressures. Label each finding as
   supported, consistent but unproven, inconclusive, or contradicted.
7. End with data gaps, comparability and timing limits, source attribution,
   confidence, and the observations that would confirm, weaken, or falsify the
   conclusion.

Separate observed facts, computed results, and analytical inference. Do not
present correlation, event timing, or a fitted relationship as deterministic
causality; check anticipation, reverse causality, and common shocks.
