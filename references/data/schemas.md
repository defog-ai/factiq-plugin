# FactIQ Data Schemas

Static overview. The `get_data_catalog` tool returns the live, authoritative
catalog with full per-dataset descriptions — run it before relying on this
file. Admin-only schemas do not appear in the catalog, and requests to them
return 403. The `filings` schema is open to every account but is not in the
catalog either: it has no `series`/`data_points` tables. Its row under United
States lists the tables to use.

## United States

| Schema | Source | Coverage |
|---|---|---|
| `bls` | Bureau of Labor Statistics | Employment (CES), unemployment (CPS, e.g. `LNS14000000`), CPI, PPI, JOLTS job openings, wages, productivity, import/export prices, consumer expenditures, time use, employment projections, workplace injuries |
| `oews` | BLS Occupational Employment & Wage Statistics | Wages and employment by occupation and metro area |
| `census` | Census Bureau | International trade (incl. `us_census_hs` — monthly imports/exports by HS commodity and partner country; quantity `_qty` series exist only at the 10-digit level, 6-digit lines are value-only), retail and wholesale trade, housing starts, construction spending, manufacturing and durable goods, quarterly services, quarterly financial reports, tax revenue, business formation applications (BFS; industry detail may be incomplete), and labor-market tables computed from public-use microdata (CPS, ACS PUMS, CPS ASEC, QWI, J2J, SIPP) |
| `bea` | Bureau of Economic Analysis | GDP and components, personal income/spending, PCE inflation, international transactions and investment position, industry value added, input-output tables, fixed assets, regional accounts |
| `eia` | Energy Information Administration | Petroleum, natural gas, electricity, renewables — production, consumption, prices |
| `ers` | USDA Economic Research Service | Agricultural and food economics |
| `bts` | Bureau of Transportation Statistics | Transportation and freight |
| `frb` | Federal Reserve Board | Interest rates (H.15), money supply (H.6), bank balance sheets (H.8), industrial production and capacity utilization (G.17), consumer credit (G.19), exchange rates (H.10), Financial Accounts (Z.1) |
| `treasury` | US Treasury | Debt to the penny, Monthly Treasury Statement (receipts, outlays, deficit), par yield curve, TIC foreign holdings of US securities |
| `ui_claims` | Department of Labor | Weekly unemployment insurance claims (ETA 539): national and per-state initial and continued claims |
| `fhfa` | Federal Housing Finance Agency | House Price Index: national, census division, state and metro |
| `cbo` | Congressional Budget Office | Historical and 10-year projected federal budget and economic data |
| `irs_soi` | IRS Statistics of Income | Individual income tax return totals (income, AGI, tax), with long historical series |
| `cms_nhe` | Centers for Medicare & Medicaid Services | National Health Expenditures in US dollars by source of funds (Medicare, Medicaid, private insurance, out-of-pocket) and type of service, plus per-capita and share of GDP, from 1960. For cross-country health-spending shares use `health_systems` |
| `us_health` | Centers for Disease Control and Prevention | Measles cases by week (from 2022), by year (from 1962) and by state, measles hospitalizations, deaths and outbreaks, and kindergarten vaccination coverage and exemptions by state and school year. For other countries use `who_gho` |
| `us_immigration` | Department of Labor (OFLC disclosure data) | H-1B labor condition applications and PERM labor certifications (the Labor Department step of an employment-based green card) per employer and federal fiscal year, from 2008: certified, denied and withdrawn, plus H-1B positions certified. One series per employer with at least 10 cases in some year, plus all-employer totals |
| `sec` | SEC EDGAR | The company series behind `search_company_filings` as ordinary `series`/`data_points` tables, for about 2,500 US-listed companies and foreign filers: XBRL statements and segment detail (`sec_10k`, `sec_10q`, `sec_20f`, `sec_40f`, `sec_6k_interim`), forward guidance (`sec_guidance`), operating KPIs (`sec_kpi`), and SIC and NAICS classifications. Statements from 2008 |
| `filings` | Company filings: US SEC filers (10-K, 10-Q, 8-K, 20-F, 40-F, 6-K) and companies listed in Germany, the UK, France, Switzerland, India, Japan, and South Korea (`issuers.source_schema` = `'german_filings'`, `'uk_filings'`, `'fr_filings'`, `'ch_filings'`, `'in_filings'`, `'jp_filings'`, `'kr_filings'`; Indian tickers end in `.NS`, e.g. `RELIANCE.NS`; Japanese and Korean tickers carry the exchange suffix, e.g. `7203.T` for Toyota Motor and `005930.KS` for Samsung Electronics) | The archive behind `search_company_filings`. Use the tool for one company; use `run_sql` on `filings` for joins and aggregations across companies. Start from `securities` (`ticker`, `issuer_id`, `is_primary`) and `issuers` (`id`, `canonical_name`). `source_filings` is one row per filing (`issuer_id`, `form_type`, `fiscal_year`, `fiscal_period`, `period_end`, `published_at`, `source_url`). `facts` is one row per extracted value (`filing_id`, `source_series_id`, `source_label`, `metric_class`, `period_start`, `period_end`, `period_basis`, `value`, `unit`, `segment_axis`, `segment_member`): always filter `is_serving AND is_active` (the other rows are superseded or never promoted) and by filing, series, or issuer, because the table holds more than 150 million rows. `source_series` (`source_series_id`, `issuer_id`, `dataset_code`, `title`, `measurement_units`, `frequency`, `is_serving`) and `serving_observations` (`source_series_id`, `time`, `value`, `unit`, `filing_id`) are the series and their points; `dataset_code` separates XBRL statements (`sec_10k`, `sec_10q`, `sec_20f`, `sec_40f`, `sec_6k_interim`), management's forward guidance (`sec_guidance`), and company-specific operating KPIs like ARR/RevPAR/subscribers (`sec_kpi`). `filing_claims` holds MD&A and earnings-release commentary and year-over-year risk-factor changes (`claim_kind`, `ticker`, `fiscal_year`, `fiscal_period`, `section`, `claim_family`, `topic`, `canonical_statement`, `verbatim_quote`, `source_url`; quote only `verbatim_quote`). `filing_risks` is one row per risk-factor heading in an annual report (`cik`, `fiscal_year`, `heading`, `summary`). The remaining tables are pipeline bookkeeping. `get_series(schema="filings", series_id=...)` and `describe_dataset("filings", "<dataset_code>")` also work: they return the same result as with `schema="sec"`, and the dataset codes are the `sec_*` codes listed above. Put a row's `source_url` beside any figure you use; `search_company_filings(format="json")` returns the same links as `source_link` on filing and fact nodes. |
| `screener` | FactIQ, from SEC filings and Nasdaq's public stock list | Finds companies that match conditions (sector, market value, valuation ratios, margins, growth). One view, `screener.companies`, with one row per US-listed company that files financial statements with the SEC (about 2,400 rows): price and `market_cap`, `price_to_sales`, `price_to_earnings`, `price_to_book`, `ev_to_sales`, latest-twelve-month revenue, income, cash flow and margins, and the latest balance sheet. No `series`/`data_points` tables: filter the view with one `run_sql` query. Prices are delayed about fifteen minutes; state `price_as_of` in the answer. **Read "Company screener" in `references/data/sql-guide.md` before writing SQL.** |
| *(not a SQL schema)* | Earnings-call transcripts, decomposed into a claim graph | `search_earnings_transcripts` targets (selected with `search_target`): management statements (`claims`: `query`, `ticker` for tickers or `company_name` for company names (one or the other, both case-insensitive; `company_filter` is the old name of `ticker` and still works), `quarter_filter`, `claim_family`, claims-only `section`, `detail`, `limit`); Q&A pressure (`pressure_points`: query/company/quarter/linked `claim_family`/detail/limit; section ignored); company-level habits (`disclosure_profile`: direct lookup by the first ticker, not text or quarter search; other filters/detail/limit ignored); and corpus inventory (`coverage`: company/limit, not theme or quarter search; returns `calls_covered`, `earliest_period`, and `latest_period`). Text retrieval ranks strict matches above loose partial-term matches and uses trigram only when FTS is empty. For one-call notes, use coverage → exact quarter → bounded empty-query claims + pressure calls. Claim/pressure rows expose `transcript_id`, `source_block_index`, `qa_turn_id`, and `source_link`; `source_link.source_label` names the company or ticker, fiscal period, and earnings call transcript rather than the ingestion vendor. Quote only `verbatim_quote`, preserving any `[…]` omission marker (it stands for skipped transcript sentences between non-adjacent evidence spans); `canonical_statement` is normalized; neither `analyst_hypothesized` nor `mgmt_declined_to_confirm` is management speech. Put a provided source URL beside any used quote using the provided source label as link text; if it is null, report that the link is unavailable rather than searching for or inventing one. Never use `run_sql` on the gated `transcripts` schema or promise full-transcript/paginated access. See `references/report-patterns/earnings-intelligence.md` |
| *(not a SQL schema)* | Executive podcasts, TV interviews, and conference appearances, plus documents published by central banks and monetary authorities (speeches, interviews, statements, press releases, minutes, press-conference transcripts, testimony, reports) | `search_media_appearances` performs deterministic strict lexical → loose any-term → trigram retrieval over precomputed claims and passage cards; no serving-time model. Use `search`, `claims`, `passages`, or `pressure_points` for timestamped paraphrase findings, `appearances` for video rows, and `coverage` for company-level structured-corpus inventory. `institution` (publisher-name substring) and `country` (ISO code, `EU` for the European Central Bank) restrict every target to official documents; `company` matches the subject of a claim, not its publisher. Dates are publication/upload dates; official documents also carry `event_date`. Never quote `canonical_paraphrase`, query `transcripts` with SQL, or infer absence before checking coverage and bounded synonym searches. See `references/report-patterns/media-intelligence.md` |

## China

| Schema | Source | Coverage |
|---|---|---|
| `china` | National Bureau of Statistics | Macro indicators: GDP, industrial production, fixed-asset investment, prices |
| `china_customs` | General Administration of Customs (GACC) | Monthly imports/exports by HS commodity and partner (6- and 8-digit levels — never sum across levels; value in US$, quantities as separate `_qty` series). A separate `china_customs_prelim` dataset carries GACC's headline preliminary totals in different units (mostly CNY 100 million) — never mix it with the per-HS US$ data |

## India

| Schema | Source | Coverage |
|---|---|---|
| `mospi` | Ministry of Statistics (MOSPI) | CPI (national key: `State: All India`; note the 2012→2024 base change — two separate series families) and CPI for agricultural and rural labourers, WPI, IIP, national accounts, Annual Survey of Industries (ASI), survey of unincorporated enterprises (ASUSE), PLFS labour force, energy statistics, gender statistics, higher education (AISHE), RBI handbook tables, and monthly domestic air passengers by airline (DGCA) |
| `rbi` | Reserve Bank of India | Banking, credit, money supply, rates, forex reserves, prices and wages, financial markets, external sector, government finance, company finances, the survey of professional forecasters, and NPCI retail payments (UPI, IMPS, NACH, RuPay and more) |
| `india_trade` | DGCI&S | Monthly imports/exports by HS commodity and partner (6- and 8-digit levels — never sum across levels) |
| `traffic` | Live road-traffic API | Bengaluru, India only — no other city, and no city dimension. 28 fixed road points x 3 metrics (84 series): `current_speed` (km/h), `travel_time` (seconds to cross the segment), `congestion_index` (current travel time / free-flow travel time; 1.0 = free-flowing). Dimensions are `metric`, `location` (point name, e.g. "Silk Board Junction"), `area` (central/east/north/south/west) and `road_type` (junction/ring_road/highway/arterial); `traffic.road_segments` lists each point with its area, road type and coordinates. History starts 2026-02-10 and can never start earlier — the source reports present conditions only, so nothing before that date exists or can be backfilled. Readings are irregular sub-daily snapshots (about every 30 minutes during the 07:00-10:00 and 17:00-21:00 local peaks, roughly hourly otherwise), so gaps between points vary — aggregate rather than assuming a fixed interval. `data_points.time` is UTC; Bengaluru local time is UTC+05:30 |

## South Korea

| Schema | Source | Coverage |
|---|---|---|
| `korea_trade` | Korea Customs Service (KCS) | Monthly imports/exports by HS commodity and partner (6-digit international and 10-digit national levels — never sum across levels; values are in US$ thousand and weight is stored as separate kg series) |

## Japan

| Schema | Source | Coverage |
|---|---|---|
| `japan_trade` | Japan Customs / Ministry of Finance | Monthly imports/exports by 9-digit HS line and partner country (no 6-digit level — group by the first 6 digits for international comparison; value in ¥ thousand, quantities as separate `_qty`/`_qty2` series with product-specific units) |

## Taiwan

| Schema | Source | Coverage |
|---|---|---|
| `taiwan_trade` | International Trade Administration (ITA), Ministry of Economic Affairs | Monthly imports/exports by commodity (6-digit international HS and 11-digit national CCC lines — never sum across levels; value in US$, no quantity series) |

## European Union

| Schema | Source | Coverage |
|---|---|---|
| `eu` | Eurostat, ECB, EEA | Curated EU and euro-area indicators, ECB policy rates and euro reference exchange rates, EEA greenhouse-gas emissions, and EU ETS registry and revenue data |
| `eu_comext_<iso2>` | Eurostat Comext | One schema per EU member-state reporter; monthly imports and exports by partner and detailed CN8 product, with trade value in euros and separate weight or supplementary-quantity series |

Use the reporter's lowercase ISO2 code: `eu_comext_de` for Germany,
`eu_comext_fr` for France, and `eu_comext_nl` for the Netherlands. All 27
reporters are available: `at`, `be`, `bg`, `hr`, `cy`, `cz`, `dk`, `ee`, `fi`,
`fr`, `de`, `gr`, `hu`, `ie`, `it`, `lv`, `lt`, `lu`, `mt`, `nl`, `pl`, `pt`,
`ro`, `sk`, `si`, `es`, and `se`. There is no `eu_comext` data schema. See the
Comext section of `sql-guide.md` before querying; its large country tables need
exact series IDs rather than dimension searches.

## United Kingdom

| Schema | Source | Coverage |
|---|---|---|
| `uk` | ONS, Bank of England, HMRC, DEFRA, DBT, DfT | Six datasets in one schema — see below |

The `uk` schema holds six datasets (filter on `dataset_code`):

- `ons_macro` — ~50 curated Office for National Statistics headline series:
  GDP and components (from 1955, plus the monthly GDP index), CPI/CPIH/RPI and
  core inflation, producer prices, the labour market and earnings, retail
  sales, public-sector borrowing and debt, trade balances, production,
  services, population, productivity. Series ids are `ons_macro.<cdid>`.
- `boe_macro_finance` — Bank of England: Bank Rate and SONIA (daily, from
  1975/1997), gilt par yields at 5/10/20 years, sterling FX rates and the
  effective index, M4 money and credit aggregates, quoted household mortgage
  and deposit rates. Series ids are `boe_macro_finance.<code>`.
- `hmrc_trade` — monthly UK goods trade from 2000 at three grains: totals per
  partner country (GBP value and net mass), UK-to-world per 2-digit HS
  chapter, and partner x chapter (value only). No product detail below the
  2-digit chapter. Product levels `TOTAL` and `HS2` restate the same trade —
  filter to exactly one product level and never sum across them. Chapter 99
  (miscellaneous/confidential goods) follows a slightly different suppression
  convention before and after 2016; avoid trend claims that hinge on it
  around that boundary.
- `dft_road_traffic` — Department for Transport road traffic for Great
  Britain (England, Scotland, and Wales only — not Northern Ireland): annual
  average daily flow per count point, total and by direction; sampled hourly
  roadside counts; regional and local-authority vehicle miles. AADF is an
  average flow at one road link — never sum it across count points; vehicle
  totals overlap their component classes.
- `defra_environment` — annual UK air pollutant emissions (from 1970) and
  cereal/oilseed yields by crop (tonnes per hectare, wheat from 1885).
- `dbt_trade` — annual inward-investment results (FDI projects and jobs);
  fiscal years are dated at January of their start year.

## Global / other

| Schema | Source | Coverage |
|---|---|---|
| `imf` | International Monetary Fund | Cross-country macro indicators, plus the earlier releases of the forecast publications (World Economic Outlook, Fiscal Monitor, the Regional Economic Outlooks, COFER) — see "IMF past releases" below |
| `worldbank` | World Bank | Development and macro indicators by country |
| `singstat` | Singapore Department of Statistics | About 1,050 tables across the economy, society, industry, trade and population |
| `sg_health` | Singapore Ministry of Health | Weekly infectious-disease case counts and average daily polyclinic attendances for acute conditions, from 2015 |
| `bis` | Bank for International Settlements | Central-bank policy rates for 49 economies (monthly, some from the 1940s, and daily), debt service ratios of households and companies for 32 economies, and total credit to the non-financial sector by borrower for 44 economies |
| `who_gho` | WHO Global Health Observatory | Headline WHO indicators, one value per country and year for about 240 countries: childhood immunization, maternal and neonatal mortality, tobacco use, life expectancy, hospital beds, UHC service-coverage index |
| `health_systems` | WHO, Eurostat | Cross-country health-system detail: health-financing shares (out-of-pocket, government, private, external), doctors and hospital beds per 10,000 people, UHC and cataract surgical coverage, Eurostat hospital use, and burden of disease 2000–2021 (DALY, YLL, YLD by age, sex and cause) |
| `portwatch` | IMF PortWatch (satellite-AIS) | Daily shipping: transit calls + trade capacity for 28 chokepoints (Suez, Hormuz, Malacca…), port calls + import/export volume estimates for 196 countries and 2,065 ports, 2019→, refreshed weekly (data runs a few days to a week behind) |
| `nasa_fires` | NASA FIRMS (VIIRS 375 m) | Every active-fire detection worldwide since 2012-01-20, one row per satellite pixel, plus pre-computed daily totals per country, per state, and per 0.1° cell. Refreshed daily. **Shaped unlike every other schema — read "The nasa_fires schema" below before writing SQL.** Most fire questions need no SQL at all: use `get_geo_data` (see `references/data/satellite.md`) |
| `satellite` | NASA / CNES satellite-derived | Monthly nighttime lights by country + state for 16 Asian economies (economic-activity proxy, 2019→); lake & reservoir water levels from radar altimetry (about 730 water bodies in 98 countries, incl. 88 Chinese and 20 Indian, 1992→, per-overpass). Water-level stations come in two grades (`grade` dimension): `operational` updates ~weekly; `research` stations are frozen scientific archives (many end 2020-22) — always check the series `end_time` before presenting a level as current, and filter to operational for live readings |

## IMF past releases

The IMF publishes a forecast, then replaces it in place at the next release: once
the April 2026 World Economic Outlook is out, the October 2025 numbers are gone
from the IMF's site. The `imf` schema keeps both, so you can show how a forecast
moved between releases.

- The plain series id is always the **newest** release. `WEO_IND.NGDPD.A` is
  India's nominal GDP in US dollars from the current WEO.
- An earlier release is the same id with the release appended:
  `WEO_IND.NGDPD.A_2025OCT`, `WEO_IND.NGDPD.A_2025APR`. The suffix is the year
  and the three-letter month of publication.
- Earlier-release series sit in their own datasets — `dataset_code` is
  `weo_vintages`, `fm_vintages`, `afrreo_vintages`, `apdreo_vintages`,
  `whdreo_vintages` or `cofer_vintages` — and each one carries a `release`
  dimension (`dimension_code` `2025OCT`, `dimension_name` "October 2025")
  alongside the usual `country`, `indicator` and `frequency` dimensions.
- Example of what this answers: India's projected 2030 nominal GDP was
  6.77 trillion US dollars in the April 2025 WEO, 6.63 trillion in the October
  2025 WEO, and 6.17 trillion in the April 2026 WEO.
- The African and Western Hemisphere Regional Economic Outlooks (`afrreo`,
  `whdreo`) changed their indicator codes between releases, so for those two
  match an earlier release to the current one on the indicator's
  `dimension_name`, not on the code. WEO, Fiscal Monitor, APDREO and COFER codes
  are stable.
- How far back this goes depends on the publication: the IMF only makes its
  recent releases retrievable, so expect two or three per publication rather than
  a long history. Query `dimension_type = 'release'` to see which ones are
  actually there before promising a comparison.

## The nasa_fires schema

A fire detection is one satellite pixel that was burning at one moment. It
belongs to no series, so **this schema has no `series` table and no
`data_points` table** — the usual discovery method does not apply. Five tables:

- **`detections`** — one row per detection since 2012-01-20: `acq_ts` (UTC
  timestamp of the overpass), `latitude`, `longitude`, `frp` (fire radiative
  power in megawatts — the heat), `bright_ti4`, `bright_ti5`, `country_id`,
  `admin1_id`, `type`, `confidence` (`l`/`n`/`h`), `daynight` (`D`/`N`),
  `quality` (`S` final, `N` provisional).
- **`region_daily`** — daily `detections` and `frp_sum` per country and state.
  `admin1_id = 0` is the country total, stored as a row **alongside** the state
  rows — so filter to `admin1_id = 0` for countries or `admin1_id > 0` for
  states. Summing both double-counts.
- **`grid_daily`** — the same daily totals per 0.1° cell. `cell_lat` and
  `cell_lon` are `floor(degrees * 10)`, so cell 302 covers 30.2 to 30.3.
- **`countries`** and **`admin1`** — id-to-name lookups, joined on
  `country_id` / `admin1_id`.

**Read `type` before counting anything**: `0` vegetation fire, `1` volcano,
`2` gas flare or other industrial heat, `3` offshore, `-1` NASA has not
classified it yet — which is every detection from the last few weeks.
`type IN (0, -1)` is wildfire and crop burning; `type = 2` is flaring. A bare
`type = 0` silently drops the newest data.

A detection is not a fire: one fire produces many detections across many
overpasses, and a fire that burns out between overpasses produces none. Count
rows for extent, sum `frp` for intensity.

`run_sql` accepts a `page` argument **on this schema only** — 50 rows at a
time, with `has_more` telling you whether to ask for the next one. Give the
query an `ORDER BY` or the pages won't line up. Totals still belong in SQL;
never page through thousands of detections to add them up yourself.

Prefer `get_geo_data` (`references/data/satellite.md`) — it answers monthly or
daily counts for a region, one window compared across every year since 2012, a
map grid, and the raw points in a small box, with no SQL at all. Come here for
the shapes it doesn't cover: ranking many countries at once, joining fires to
another dataset, or splitting day passes from night passes.

## Picking schemas

- US labor/inflation → `bls` (plus `oews` for occupation-level wages)
- US GDP/income → `bea`; US trade → `census`
- US interest rates, money and credit → `frb`; federal debt, receipts and outlays → `treasury` (projections → `cbo`); weekly jobless claims → `ui_claims`; house prices → `fhfa`
- Health → `who_gho` or `health_systems` across countries; `cms_nhe` and `us_health` for the US; `sg_health` for Singapore
- H-1B or green-card sponsorship by employer → `us_immigration`
- Policy rates and credit across many countries → `bis`; euro area → `eu`
- Energy anything → `eia`
- India macro → check BOTH `mospi` and `rbi`
- Trade-war / commodity-flow stories → `census` + `china_customs` +
  `india_trade` + `korea_trade` + the relevant `eu_comext_<iso2>` schemas cover
  the same flows from each country's own records when those reporters are in scope
- UK anything → `uk` (macro, rates, trade, environment, road traffic in one schema)
- Cross-country comparisons → `imf` / `worldbank`
- How an IMF forecast has been revised between releases → the `*_vintages`
  datasets in `imf` (see "IMF past releases" above)
- Shipping disruptions, chokepoint transits (Suez/Hormuz/Malacca), real-time
  trade activity → `portwatch` (daily grain, satellite-AIS based, refreshed
  weekly; cite IMF PortWatch)
- Nighttime lights (activity proxy), reservoir/lake water levels (hydropower,
  irrigation, drought) → `satellite` schema; for on-demand fires/NO2/SO2/CO/
  aerosol/rainfall/NDVI over arbitrary regions → the `get_geo_data` tool
  instead (see `references/data/satellite.md`)
- Crop burning, wildfires, gas flaring → `get_geo_data` first; drop to the
  `nasa_fires` schema only for shapes the tool doesn't cover (see "The
  nasa_fires schema" above)
- Companies that match conditions ("software companies with price-to-sales
  above 10 and market value above $50B") → one `run_sql` query on
  `screener.companies` (see "Company screener" in
  `references/data/sql-guide.md`)
- Company-specific: quotes, price history, and company/ETF profiles →
  `get_market_data`; filed financials, segment/product/geography detail,
  forward guidance, or operating KPIs (ARR, RevPAR, ...) →
  `search_company_filings`; joins or aggregations across companies over the
  same filed data → `run_sql` on `filings`; what management said live on a
  call →
  `search_earnings_transcripts` (not SQL)
- What executives said in podcasts, television interviews, and conferences
  outside earnings calls → `search_media_appearances` (not SQL); follow `references/report-patterns/media-intelligence.md`

HS trade schemas (`us_census_hs` in census, `china_customs`, `india_trade`,
`korea_trade`) carry the same trade at multiple HS digit levels — filter to one
level and never sum across levels. Some reporters also store value and physical
quantity/weight as separate series; filter value series explicitly for value
reports.

Comext is the exception to the normal HS discovery method: do not filter its
`dimensions` table by value. Search `eu_comext_lookup.product_codes`, construct
exact series IDs, and query one reporter schema at a time.
