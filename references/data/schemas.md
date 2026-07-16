# FactIQ Data Schemas

Static overview. The `get_data_catalog` tool returns the live, authoritative
catalog with full per-dataset descriptions — run it before relying on this
file. Some schemas are admin-only and simply won't appear in your
`get_data_catalog` output (requests to them return 403).

## United States

| Schema | Source | Coverage |
|---|---|---|
| `bls` | Bureau of Labor Statistics | Employment (CES), unemployment (CPS, e.g. `LNS14000000`), CPI, PPI, JOLTS job openings, wages, productivity |
| `oews` | BLS Occupational Employment & Wage Statistics | Wages and employment by occupation and metro area |
| `census` | Census Bureau | International trade (incl. `us_census_hs` — monthly imports/exports by HS commodity and partner country; quantity `_qty` series exist only at the 10-digit level, 6-digit lines are value-only), retail, housing, demographics, business formation applications (BFS; industry detail may be incomplete) |
| `bea` | Bureau of Economic Analysis | GDP and components, personal income/spending, regional accounts |
| `eia` | Energy Information Administration | Petroleum, natural gas, electricity, renewables — production, consumption, prices |
| `ers` | USDA Economic Research Service | Agricultural and food economics |
| `bts` | Bureau of Transportation Statistics | Transportation and freight |
| `sec` | SEC EDGAR (~950 US-listed companies with market cap ≥ $10B) | XBRL segment/product/geography financial detail (`sec_10k`/`sec_10q`/`sec_20f`/`sec_40f`), management's forward guidance (`sec_guidance`), and company-specific operating KPIs like ARR/RevPAR/subscribers (`sec_kpi`) — call `describe_dataset` for series-ID conventions before querying |
| *(not a SQL schema)* | Earnings-call transcripts, decomposed into a claim graph | Management's guidance/comparisons (`claims`), Q&A pressure points (`pressure_points`), disclosure profiles (`disclosure_profile`), and covered tickers/quarters (`coverage`) — searched via the `search_earnings_transcripts` tool (params: `query`, `search_target`, `company_filter` incl. comma-separated multi-ticker, `quarter_filter`, `claim_family`, `section`, `detail`, `limit`), never SQL (the underlying `transcripts` schema has a bespoke structure and no `series` table). See `references/report-patterns/earnings-intelligence.md` for the full workflow |

## China

| Schema | Source | Coverage |
|---|---|---|
| `china` | National Bureau of Statistics | Macro indicators: GDP, industrial production, fixed-asset investment, prices |
| `china_customs` | General Administration of Customs (GACC) | Monthly imports/exports by 8-digit HS line and partner country (incl. rare earths). Data not yet loaded (listed under `schemas_without_data` in `get_data_catalog`) — for China–US trade use the `us_census_hs` mirror in `census` (US imports from China ≈ Chinese exports to the US) |

## India

| Schema | Source | Coverage |
|---|---|---|
| `mospi` | Ministry of Statistics (MOSPI) | CPI (national key: `State: All India`; note the 2012→2024 base change — two separate series families), WPI, IIP, GDP |
| `rbi` | Reserve Bank of India | Banking, credit, money supply, rates, forex reserves |
| `india_trade` | DGCI&S | Monthly imports/exports by HS commodity and partner (6- and 8-digit levels — never sum across levels) |
| `traffic` | TomTom | Indian city traffic flow |

## South Korea

| Schema | Source | Coverage |
|---|---|---|
| `korea_trade` | Korea Customs Service (KCS) | Monthly imports/exports by HS commodity and partner (6-digit international and 10-digit national levels — never sum across levels; values are in US$ thousand and weight is stored as separate kg series) |

## European Union

| Schema | Source | Coverage |
|---|---|---|
| `eu_comext_<iso2>` | Eurostat Comext | One schema per EU member-state reporter; monthly imports and exports by partner and detailed CN8 product, with trade value in euros and separate weight or supplementary-quantity series |

Use the reporter's lowercase ISO2 code: `eu_comext_de` for Germany,
`eu_comext_fr` for France, and `eu_comext_nl` for the Netherlands. All 27
reporters are available: `at`, `be`, `bg`, `hr`, `cy`, `cz`, `dk`, `ee`, `fi`,
`fr`, `de`, `gr`, `hu`, `ie`, `it`, `lv`, `lt`, `lu`, `mt`, `nl`, `pl`, `pt`,
`ro`, `sk`, `si`, `es`, and `se`. There is no `eu_comext` data schema. See the
Comext section of `sql-guide.md` before querying; its large country tables need
exact series IDs rather than dimension searches.

## Global / other

| Schema | Source | Coverage |
|---|---|---|
| `imf` | International Monetary Fund | Cross-country macro indicators |
| `worldbank` | World Bank | Development and macro indicators by country |
| `singstat` | Singapore Department of Statistics | Singapore national statistics |

## Picking schemas

- US labor/inflation → `bls` (plus `oews` for occupation-level wages)
- US GDP/income → `bea`; US trade → `census`
- Energy anything → `eia`
- India macro → check BOTH `mospi` and `rbi`
- Trade-war / commodity-flow stories → `census` + `china_customs` +
  `india_trade` + `korea_trade` + the relevant `eu_comext_<iso2>` schemas cover
  the same flows from each country's own records when those reporters are in scope
- Cross-country comparisons → `imf` / `worldbank`
- Company-specific: consolidated quotes/fundamentals → `get_market_data` tool (not SQL); segment/product/geography detail, forward guidance, or operating KPIs (ARR, RevPAR, ...) → `sec` schema via `run_sql`; what management said live on a call → `search_earnings_transcripts` tool (not SQL)

HS trade schemas (`us_census_hs` in census, `china_customs`, `india_trade`,
`korea_trade`) carry the same trade at multiple HS digit levels — filter to one
level and never sum across levels. Some reporters also store value and physical
quantity/weight as separate series; filter value series explicitly for value
reports.

Comext is the exception to the normal HS discovery method: do not filter its
`dimensions` table by value. Search `eu_comext_lookup.product_codes`, construct
exact series IDs, and query one reporter schema at a time.
