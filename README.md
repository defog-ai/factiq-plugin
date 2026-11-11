# FactIQ: financial and economic data for AI agents

FactIQ is an MCP server and plugin that gives Claude, ChatGPT, Claude Code,
and Codex sourced data about companies, markets, and economies. The agent
searches the data, runs read-only SQL, does the calculation, and returns an
answer with links to the sources, a chart, or a report.

One connection covers data that usually needs many separate subscriptions and
scrapers:

- **[Podcasts, TV interviews, and conference talks](#what-executives-and-investors-said-on-podcasts-tv-and-at-conferences)** —
  what executives, investors, and economists said outside earnings calls, with
  a link to the moment in the recording.
- **[Central-bank speeches, minutes, and press conferences](#what-central-banks-said)** —
  the Federal Reserve, the European Central Bank, the Bank of England, the
  Bank of Japan, the Reserve Bank of India, and others.
- **[Earnings calls](#earnings-calls-what-management-said-and-what-analysts-pressed-on)** —
  each management statement as a separate row with its exact quote, plus the
  questions analysts pressed and whether management answered them.
- **[Satellite data](#satellite-data-for-any-country-state-or-map-box)** —
  fires, rainfall, air pollution, crop condition, heat, nighttime lights, and
  reservoir levels for any country, state, or map box.
- **[Shipping](#shipping-through-chokepoints-and-ports)** — daily ship counts
  through 28 chokepoints (Suez, Hormuz, Malacca) and 2,065 ports.
- **[Company filings in eight markets](#company-filings-in-eight-markets)** —
  the US, Germany, the UK, France, Switzerland, India, Japan, and South Korea:
  financial statements, segments, guidance, operating KPIs, IPO prospectuses,
  and the risk factors a company added or changed.
- **[Customs trade data](#trade-from-each-countrys-own-customs-records)** —
  product-level imports and exports from the US, China, India, South Korea,
  Japan, Taiwan, the UK, and all 27 EU member states.
- **[Official statistics](#official-statistics-and-how-forecasts-changed)** —
  BLS, BEA, Census, the Federal Reserve, the US Treasury, EIA, China NBS,
  India MOSPI and RBI, ONS, Eurostat, IMF, World Bank, BIS, WHO, and more.
- **[Market data, a stock screener, and business news](#market-data-stock-screener-and-business-news)**.

You need no code and no database of your own, only a free
[FactIQ account](https://factiq.com). Go to [Install](#install) for Claude,
ChatGPT, Claude Code, and Codex, or connect any MCP client to
`https://api.factiq.com/mcp`.

## What you can ask

Each section below names the data, gives questions you can ask in plain
English, and links the reference file that the agent reads.

### What executives and investors said on podcasts, TV, and at conferences

FactIQ reads podcast episodes, television interviews, and conference talks,
and stores each substantive statement as a separate searchable row. The
speakers are company executives, investors, fund managers, analysts,
economists, and journalists. The statements cover listed companies, unlisted
companies such as OpenAI and DeepSeek, central banks, regulators, and whole
industries.

You can filter by person, company, podcast show, YouTube channel, kind of
appearance, and date. Each result gives the speaker, the publication date, the
show or channel, a short paraphrase of the statement, and a link that opens
the recording at the moment of the statement. A separate target lists the
questions that a speaker declined to answer.

Questions to try:

- "How has Jensen Huang discussed export controls outside earnings calls?"
- "What have podcast guests said about data center power demand this year?"
- "Compare what Nvidia's management said in interviews with what it said on
  its earnings calls about demand from China."

Tool: `search_media_appearances`. Reference:
[`media-intelligence.md`](references/report-patterns/media-intelligence.md).

### What central banks said

The same tool holds documents published by central banks and monetary
authorities: speeches, testimony before legislatures, policy statements,
meeting minutes, press-conference transcripts, press releases, interviews, and
reports. The publishers are the Federal Reserve Board and the regional Reserve
Banks, the European Central Bank and the national central banks of the euro
area, the Bank of England, the Bank of Japan, the Reserve Bank of India, the
People's Bank of China, the Bank of Korea, the Hong Kong Monetary Authority,
and Taiwan's central bank. A document in another language gives English
paraphrases. Each result carries the institution, the speaker, the meeting or
speech date, and a link to the document.

Questions to try:

- "What has Christopher Waller said about rate cuts in his recent speeches?"
- "What has the Bank of Japan said about the inflation outlook at its press
  conferences?"
- "How did the wording on inflation risk change between the last three FOMC
  minutes?"

Tool: `search_media_appearances` with `institution` or `country`. Reference:
[`media-intelligence.md`](references/report-patterns/media-intelligence.md)
and [`monetary-policy.md`](references/report-patterns/monetary-policy.md).

### Earnings calls: what management said and what analysts pressed on

FactIQ does not return a raw transcript. It splits each earnings call into
single statements. Each statement has the speaker, the speaker's role, the
exact quote, the fiscal quarter, a topic, and, where the statement has a
number, the value and unit. This lets the agent search one topic across many
companies and many quarters.

A second kind of row records the question-and-answer part of the call: what
the analyst asked for, which firm asked, and whether management confirmed,
partly answered, deflected, or declined. When management refused to give a
number, the row names that number. A company profile lists what the company
usually discloses and what it usually holds back.

Coverage includes US-listed companies and companies listed in India and
Switzerland. The agent checks the live coverage list before it answers.

Questions to try:

- "What did Micron management say on its latest earnings call?"
- "Which questions about capital expenditure did analysts press Microsoft on,
  and which did management not answer in full?"
- "Compare what Micron and Nvidia said about capacity over the last four
  quarters."

Tool: `search_earnings_transcripts`. Reference:
[`earnings-intelligence.md`](references/report-patterns/earnings-intelligence.md).

### Satellite data for any country, state, or map box

Official statistics arrive weeks or months after the event. Satellite data
arrives in one to five days. FactIQ computes each indicator for the region you
name: any country, a state or province in 17 countries (India, China,
Indonesia, Vietnam, Thailand, Malaysia, the Philippines, Pakistan, Bangladesh,
Sri Lanka, Myanmar, Cambodia, Nepal, South Korea, Japan, Taiwan, and the US),
or a box of latitude and longitude.

| Indicator | Source | Use | History |
|---|---|---|---|
| Fire detections and fire heat output | NASA FIRMS (VIIRS, 375 m) | Crop-residue burning, wildfires, deforestation fires, gas flaring | 2012 onward, one day behind |
| Nitrogen dioxide (NO₂) | Sentinel-5P | Industrial, power-plant, and traffic activity | 2018 onward |
| Sulphur dioxide (SO₂) | Sentinel-5P | Coal power, smelting, refining | 2018 onward |
| Carbon monoxide (CO) and aerosol index | Sentinel-5P | Smoke, dust, and haze episodes | 2018 onward |
| Vegetation index (NDVI) | Sentinel-2 | Crop condition before the harvest statistics | 2017 onward |
| Rainfall | CHIRPS and NASA IMERG | Monsoon, drought, and flood risk | 1981 onward |
| Temperature, soil moisture, wind, humidity | NASA POWER | Heatwaves, electricity demand, sowing conditions | 1981 onward |
| Nighttime lights | Satellite-derived | Economic activity by country and state in 16 Asian economies | 2019 onward, monthly |
| Lake and reservoir water levels | Radar altimetry | Hydropower, irrigation, and drought for about 730 water bodies in 98 countries | 1992 onward |

FactIQ stores every NASA fire detection since 2012, so the agent can compare
the same weeks in every year, draw a map grid, or list exact fire locations.
For example, this is the number of fire detections in Punjab, India, from
1 October to 9 November of each year, the weeks when farmers burn rice
residue:

| Year | 2016 | 2021 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| Fire detections | 75,251 | 50,049 | 19,512 | 4,922 | 3,119 |

Source: NASA FIRMS, VIIRS 375 m active fire detections, through the
`get_geo_data` tool. A detection is one satellite pixel at one overpass, not
one fire.

Questions to try:

- "Compare crop-fire detections in Punjab in October and November for every
  year since 2012."
- "Compare Punjab rainfall and fire activity during the 2024 and 2025 monsoon
  seasons."
- "Map where fires were detected in Indonesia in September."
- "How have nighttime lights changed in Vietnam's provinces since 2019?"

Tool: `get_geo_data`, plus the `satellite` and `nasa_fires` schemas. Reference:
[`satellite.md`](references/data/satellite.md).

### Shipping through chokepoints and ports

FactIQ holds the IMF PortWatch data, which the IMF computes from satellite
ship-tracking signals: daily transits and cargo capacity for 28 chokepoints,
and daily port calls with import and export volume estimates for 196 countries
and 2,065 ports. The data starts in 2019 and is refreshed every week. It
separates tankers, container ships, and dry bulk carriers.

Questions to try:

- "How many tankers passed through the Strait of Hormuz each week this year?"
- "How did Suez Canal container traffic change after the Red Sea attacks
  began?"
- "Which ports had the largest fall in port calls last month?"

Tool: `run_sql` on the `portwatch` schema. Reference:
[`schemas.md`](references/data/schemas.md).

### Company filings in eight markets

FactIQ reads company reports from the US Securities and Exchange Commission
(10-K, 10-Q, 8-K, 20-F, 40-F, and 6-K) and from the regulators or exchanges of
Germany, the UK, France, Switzerland, India, Japan, and South Korea. Every
figure carries a link to the filing it came from. The data goes beyond the
three financial statements:

- **Segment detail**: revenue and profit by business, product, and region.
- **Operating KPIs** that companies define themselves, such as annual
  recurring revenue, subscribers, and revenue per available room.
- **Forward guidance** that the company issued formally.
- **IPO prospectuses** (S-1, F-1, and the final prospectus): the statement
  figures for the years before the first periodic report, and the offering
  price, shares offered, and proceeds.
- **Management commentary** from the MD&A section and the earnings press
  release, each with its exact quote.
- **Risk-factor changes**: the risks that a US company added, changed, or
  removed in its annual report compared with the year before, with the changed
  passage quoted.
- **Revisions**: a figure that a later report restated shows the old value and
  the new value.

Questions to try:

- "Which risk factors did Nvidia add or change in its latest annual report?"
- "Show Toyota's revenue for the last two fiscal years from its filed
  reports."
- "What reasons did management give for the change in gross margin in its
  latest 10-Q?"
- "List the offering price and proceeds from a company's IPO prospectus."

Tool: `search_company_filings`; `run_sql` on the `filings` and `sec` schemas
for comparisons across companies. Reference:
[`schemas.md`](references/data/schemas.md).

### Trade from each country's own customs records

FactIQ holds monthly imports and exports by product code and partner country
from the customs authority of each reporter: the US Census Bureau, China's
General Administration of Customs, India's DGCI&S, the Korea Customs Service,
Japan Customs, Taiwan's International Trade Administration, the UK's HMRC, and
Eurostat Comext for all 27 EU member states. The same trade flow is therefore
available from both sides: what China reports as exports to the US and what
the US reports as imports from China. The plugin bundles a product-code lookup
and a SQL generator, so the agent can go from a product name to the correct
codes.

Questions to try:

- "How has India's trade deficit with China evolved since 2020?"
- "Compare China's reported exports of lithium-ion batteries to the US with
  the US-reported imports from China."
- "Which EU countries import the most solar panels from China?"

Tools: `run_sql`, with the bundled `hs_codes.py` and `trade_sql.py` scripts.
Reference: [`bilateral-trade.md`](references/report-patterns/bilateral-trade.md).

### Official statistics, and how forecasts changed

FactIQ stores the series of each statistical agency in one common table
layout, so one SQL pattern works for all of them. See
[What's in the warehouse](#whats-in-the-warehouse) for the list. Some data
that is hard to get elsewhere:

- **Earlier IMF forecasts.** The IMF replaces its forecast at each release.
  FactIQ keeps the recent earlier releases of the World Economic Outlook, the
  Fiscal Monitor, and the Regional Economic Outlooks, so the agent can show
  how a forecast moved.
- **H-1B and green-card sponsorship by employer**, per US federal fiscal year
  from 2008, from Department of Labor disclosure data.
- **Central-bank policy rates for 49 economies** and credit to households and
  companies, from the Bank for International Settlements.
- **India's retail payments** (UPI, IMPS, and more) and the RBI's banking,
  credit, and forex series.
- **Health data**: WHO indicators for about 240 countries, US national health
  spending from 1960, and US measles cases by week.

Questions to try:

- "How has the IMF changed its forecast of India's 2030 GDP between releases
  of the World Economic Outlook?"
- "How many H-1B applications did Amazon have certified in each year since
  2015?"
- "Compare US inflation and unemployment since 2020 and explain the turning
  points."

Tools: `search_datasets`, `search_series`, `get_series`, `run_sql`. Reference:
[`schemas.md`](references/data/schemas.md) and
[`sql-guide.md`](references/data/sql-guide.md).

### Market data, stock screener, and business news

- **Market data**: quotes, price history, company and ETF profiles, FX, and
  commodities (`get_market_data`).
- **Stock screener**: one SQL view with one row per US-listed company that
  files with the SEC: price, market value, price-to-sales, price-to-earnings,
  margins, and growth. Example: "software companies with price-to-sales above
  10 and market value above $50 billion". Prices are the last US market close.
- **Business news**: recent headlines, short summaries, and links from public
  feeds. Each article carries the listed companies it names and one sentence
  on why the story matters to an investor (`search_news`).

## MCP tools

The FactIQ MCP server is at `https://api.factiq.com/mcp` (Streamable HTTP,
OAuth). Every tool except `send_feedback` only reads data.

| Tool | What it does |
|---|---|
| `get_data_catalog` | Lists the data sources and the shared table layout |
| `search_datasets`, `describe_dataset`, `search_series` | Find a dataset or a series by key word |
| `get_series` | Returns one series, with optional year-over-year and other transforms |
| `run_sql` | Runs one read-only SQL query for joins, pivots, and totals |
| `search_company_filings` | Filed figures, segments, guidance, KPIs, commentary, and risk-factor changes for one company |
| `search_earnings_transcripts` | Earnings-call statements and analyst question-and-answer rows |
| `search_media_appearances` | Statements from podcasts, TV interviews, conference talks, and central-bank documents |
| `get_geo_data` | Satellite indicators for a country, state, or map box |
| `get_market_data` | Quotes, price history, profiles, FX, and commodities |
| `search_news` | Recent business headlines with company tags |
| `get_style_guides` | FactIQ's rules for charts, reports, SQL, and earnings notes |
| `send_feedback` | Sends a short report to the FactIQ team when a result looks wrong |

Want to contribute? The highest-leverage addition is a **domain playbook** that
teaches the agent a whole class of questions — see
[Contributing](#contributing).

## Install

FactIQ supports four client paths. The website guides are canonical for app
setup and plan requirements, which can change faster than this repository:

| Client | Supported surfaces | Setup guide |
|---|---|---|
| Claude | Web, desktop, and Cowork | [factiq.com/claude](https://www.factiq.com/claude) |
| ChatGPT | Web and desktop app (including Codex in the app) | [factiq.com/chatgpt](https://www.factiq.com/chatgpt) |
| Claude Code | CLI, desktop app, and IDE extensions | [factiq.com/claude-code](https://www.factiq.com/claude-code) |
| Codex | CLI | [factiq.com/codex](https://www.factiq.com/codex) |

### Claude (web, desktop, and Cowork)

FactIQ is listed in the official Claude directory. Open
[claude.ai/directory/factiq](https://claude.ai/directory/factiq) while signed
in to Claude, click **Connect**, complete the FactIQ sign-in, and start a new
chat. You can also find it under **Customize → Plugins** by searching for
FactIQ. For the best experience, use Cowork. The plugin requires a paid Claude
plan.

To install from this repository instead, open **Customize → Plugins**, add
`defog-ai/factiq-plugin` as a personal marketplace, install FactIQ, and
complete the browser sign-in. Organizations that approve plugins centrally can
mirror this repository as a private marketplace. See the
[Claude guide](https://www.factiq.com/claude) for the current steps and
organization-policy notes.

### ChatGPT (web and desktop)

FactIQ is listed in the official ChatGPT plugin directory. Open the
[FactIQ listing](https://chatgpt.com/plugins/plugin_asdk_app_6a8fc5639bb88191a76a294a337dade2)
while signed in to ChatGPT, click **Install plugin**, complete the FactIQ
sign-in, and start a new chat. Type `@FactIQ` to select it explicitly. This
works on ChatGPT Plus, Pro, Business, Enterprise, and Edu plans, on the web and
in the desktop app. On Business, Enterprise, and Edu, a workspace admin may need
to allow FactIQ first. The install also covers Codex inside the ChatGPT app;
Codex CLI uses the separate setup below.

To install from this repository instead, open **Plugins** in the ChatGPT
desktop app, add `defog-ai/factiq-plugin` as a marketplace, and install FactIQ
from the Personal tab. This path works only in the desktop app, on a Pro,
Business, Enterprise, or Edu plan. See the
[ChatGPT guide](https://www.factiq.com/chatgpt) for the current plan matrix and
troubleshooting steps.

### Claude Code

```
/plugin marketplace add defog-ai/factiq-plugin
/plugin install factiq@factiq
/reload-plugins
```

Run **`/reload-plugins`** after installing so Claude Code picks up the new
skill and MCP server in the current session (otherwise they only appear the
next time you start Claude Code).

This adds the FactIQ skill (Claude invokes it automatically for
economic/financial data questions) and the bundled FactIQ MCP server. Claude
Code namespaces skills installed from plugins, so its manual invocation is:

| Command | Purpose |
|---|---|
| `/factiq:factiq <question>` | Run an analysis and get a sourced answer, chart JSON, or report |

Finally, authenticate the MCP server:

1. Run **`/mcp`**.
2. Select **factiq** from the list of servers.
3. Choose **Authenticate** (or **Connect**) to open the browser sign-in.
4. Complete the FactIQ login (email, Google, or passkey) and return to Claude
   Code — the FactIQ tools are now authorized.

<details>
<summary>Enable auto-updates</summary>

So you always get the latest skill and MCP tools without
reinstalling, turn on auto-updates for the marketplace:

1. Run **`/plugin`**.
2. Select **Marketplaces**.
3. Select **factiq**.
4. Toggle **auto-updates** on.

Claude Code will then refresh the plugin automatically whenever this
marketplace changes.
</details>

### Codex

```bash
codex plugin marketplace add defog-ai/factiq-plugin
codex plugin add factiq@factiq
```

Then authorize the MCP server:

```bash
codex mcp login factiq
```

Complete the browser sign-in (the same FactIQ login: email, Google, or
passkey). Start a new Codex thread after installation; the skill auto-invokes
for economic/financial data questions.

<details>
<summary>Update an existing Codex install</summary>

To update after this marketplace changes, refresh the configured marketplace
name (`factiq`), then reinstall the plugin:

```bash
codex plugin marketplace upgrade factiq
codex plugin add factiq@factiq
```
</details>

<details>
<summary>Alternative: install as a standalone MCP server (no plugin)</summary>

Add the MCP server directly to your Codex config (`~/.codex/config.toml`):

```toml
[mcp_servers.factiq]
url = "https://api.factiq.com/mcp"
```

Then `codex mcp login factiq`. The skill won't auto-invoke without the plugin,
but the MCP tools are available for manual use.

For Claude Code without the plugin:

```bash
claude mcp add --transport http factiq https://api.factiq.com/mcp
```

Then authorize with `/mcp`.
</details>

### Without a browser: scripts, CI, and headless agents

Every FactIQ tool also works without the browser sign-in. The guide at
[factiq.com/docs/api](https://www.factiq.com/docs/api) explains headless
access for scripts, CI, Claude Code, and Codex.

## What the plugin sends and runs

- **One remote MCP server.** The plugin adds `https://api.factiq.com/mcp`
  (see `.mcp.json`), which you sign in to with OAuth. Each tool call sends its
  arguments (search terms, SQL statements, series IDs, tickers, regions) to
  that server and returns FactIQ data. FactIQ records connector tool inputs
  and outputs for reliability and support, as described in the
  [privacy policy](https://www.factiq.com/privacy).
- **One tool that sends a message.** `send_feedback` sends a short report,
  written by the agent, to the FactIQ team when a FactIQ result looks wrong.
  It changes no data. Every other tool only reads data.
- **Local scripts with no network access.** The skill can run the Python
  scripts in `scripts/` (`hs_codes.py`, `trade_sql.py`,
  `series_math.py`). They read only their arguments, files you pass them, and
  the bundled files in `scripts/data/`, and they print their result. They make
  no network calls.
- **Local outputs only.** Charts and reports are files written in your own
  workspace. The plugin does not publish them anywhere.
- The plugin has no hooks and runs nothing when it is installed.

## Try it

Once installed and authenticated, ask a question:

```
/factiq:factiq How has India's trade deficit with China evolved since 2020?
```

The agent finds the relevant series, runs the SQL, and replies with a sourced
answer, chart JSON, or full report, depending on what you ask for. You
don't need the slash command: any
economic or financial data question in any supported client auto-invokes the
skill.

For an earnings question such as "What did Micron management say on its latest
call?", the skill checks live transcript coverage first, pins the exact fiscal
quarter, and then retrieves bounded management-claim and Q&A-pressure rows for
that same call. It keeps spoken remarks separate from formal guidance and SEC
filed actuals; the tool does not return a raw transcript.

For a media question such as "How has Jensen Huang discussed export controls
outside earnings calls?", the skill checks company-level structured coverage,
runs deterministic lexical retrieval with relevance ordering, and uses explicit
newest ordering only for a timeline. Results are public-safe paraphrases with
timestamped YouTube links, not quotations; the workflow verifies the linked
source when exact wording or tone is material. A dedicated playbook also keeps
media-vs-earnings comparisons aligned by company, person, topic, and date.
The same tool covers documents published by central banks and monetary
authorities (the Federal Reserve, the European Central Bank, the Bank of
England, the Bank of Japan, the Reserve Bank of India, and others): a question
such as "What has the Bank of Japan said about the inflation outlook?" filters
by `institution` or `country` and reports the meeting or speech date that each
document carries.

## How it works

**Your coding agent is the analyst**: it finds the data, does the math, and
authors a local output. Data access uses the **FactIQ MCP server** bundled in
`.mcp.json` over one OAuth connection.

```
┌─────────────────────────────┐
│  Claude / ChatGPT /         │
│  Claude Code / Codex        │
│  + factiq skill (SKILL.md)  │      the agent orchestrates everything
└──────────────┬──────────────┘
               │  MCP over HTTP (one OAuth connection)
┌──────────────▼──────────────┐
│  FactIQ MCP server          │
│                             │
│  discover   search_datasets, describe_dataset, search_series,
│             get_data_catalog
│  fetch      run_sql (read-only), get_series, get_market_data,
│             search_company_filings, search_earnings_transcripts,
│             search_media_appearances, search_news, get_geo_data
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│  FactIQ data warehouse      │      official and derived data sources
└─────────────────────────────┘
```

The reason a single skill can query BLS unemployment, Chinese customs flows,
RBI monetary data, and World Bank indicators with the same SQL idioms: **almost
every statistical source in the backend is normalized into the same three core
tables**, identical in every schema that has them:

| Table | What it holds |
|---|---|
| `series` | The catalog — one row per series: id, title, description, dataset, frequency, units, seasonality, geography, time coverage |
| `data_points` | The values — `(series_id, time, value)`, indexed for fast retrieval |
| `dimensions` | Faceted metadata — `(series_id, dimension_type, dimension_code, dimension_name)`, e.g. `partner`, `flow`, `commodity`, `hs_level` for trade data |

Our ingestion pipelines do the hard work of flattening each source's bespoke
format — BLS flat files, BEA APIs, customs records, RBI releases — into this
shape, so the agent learns the model once and it works everywhere. Discovery,
pivoting, and filtering follow the same patterns across these schemas; the
recipes live in [`references/data/sql-guide.md`](references/data/sql-guide.md).
Company filings and the NASA fire detections have their own tables, described
in [`references/data/schemas.md`](references/data/schemas.md).

### What's in the warehouse

| Region | Data |
|---|---|
| United States | BLS (employment, CPI, PPI, JOLTS, wages by occupation), BEA (GDP, income, PCE), Census (trade by product and partner, retail, housing, business formation), Federal Reserve (interest rates, money, bank balance sheets, industrial production), Treasury (debt, receipts, outlays, yield curve), EIA (energy), USDA ERS, BTS (transportation), weekly unemployment claims, FHFA house prices, CBO budget projections, IRS income statistics, CMS health spending, CDC measles data, H-1B and green-card applications by employer |
| Companies | SEC filings for US-listed companies and foreign filers; reports of companies listed in Germany, the UK, France, Switzerland, India, Japan, and South Korea; a stock screener; earnings-call statements; executive media appearances; live market data (quotes, fundamentals, FX, commodities); business news |
| China | NBS macro indicators, GACC customs trade by product and partner |
| India | MOSPI (CPI, WPI, IIP, GDP, labour force), RBI (banking, rates, forex, retail payments), DGCI&S trade by product and partner, Bengaluru road traffic (2026 onward, that one city only) |
| Japan, South Korea, Taiwan | Customs trade by product and partner |
| European Union | Eurostat and ECB indicators, policy rates, greenhouse-gas emissions and the EU emissions-trading registry; Eurostat Comext monthly trade for all 27 member-state reporters, by CN8 product and partner country |
| United Kingdom | ONS macro series, Bank of England rates and money, HMRC trade, road traffic, air-pollutant emissions and crop yields |
| Global | IMF (including the recent earlier releases of its forecasts, so a revision can be traced), World Bank, BIS policy rates and credit, WHO health indicators, Singapore SingStat and Ministry of Health, IMF PortWatch shipping |
| Central banks | Speeches, testimony, statements, minutes, and press-conference transcripts from the Federal Reserve, the European Central Bank and national central banks, the Bank of England, the Bank of Japan, the Reserve Bank of India, the People's Bank of China, the Bank of Korea, the Hong Kong Monetary Authority, and Taiwan's central bank |
| Satellite | Fire detections, NO₂, SO₂, CO, aerosol, vegetation index, rainfall, temperature, soil moisture, wind, humidity, nighttime lights, lake and reservoir water levels |

`references/data/schemas.md` has the static overview; the `get_data_catalog` tool
returns the live, authoritative version.

## FAQ

**What is FactIQ?** FactIQ is a database of economic, financial, and company
data that an AI agent queries through MCP tools. This repository is the plugin
that connects Claude, ChatGPT, Claude Code, and Codex to it.

**Is FactIQ an MCP server?** Yes. The server is at
`https://api.factiq.com/mcp`. The plugin adds a skill that tells the agent how
to use the tools; the tools also work in any MCP client without the plugin.

**Does FactIQ return full earnings-call or podcast transcripts?** No. It
returns single statements with the speaker, the date, and a link to the
source. Earnings-call statements carry the exact quote.

**Where does the data come from?** From the publishers: statistical agencies,
customs authorities, central banks, securities regulators, NASA and Copernicus
satellites, and the recordings and documents themselves. Each result names its
source, and filing figures and statements carry a link to it.

**Can a script or a CI job use FactIQ?** Yes. See
[factiq.com/docs/api](https://www.factiq.com/docs/api).

## Repo map

Where the behavior lives — the files contributors will touch:

- `skills/factiq/SKILL.md` — the skill definition and single source of truth
  for the workflow. Auto-discovered by supported plugin clients from the
  `skills/` directory
- `references/data/` — the data layer: SQL idioms (`sql-guide.md`) and the
  dataset schema overview (`schemas.md`)
- `references/output/` — local output formats: ChartSpec (`chart-spec.md`) and
  report JSON (`report-spec.md`)
- `references/report-patterns/` — domain playbooks (monetary policy,
  bilateral trade, bilateral economic policy, fiscal-policy revenue, business
  formation, earnings intelligence, media-appearance intelligence).
  `report-patterns/README.md` is the single entry point SKILL.md
  references: it teaches the dialectical method (thesis → antithesis →
  synthesis) all reports follow and routes each domain to its playbook, so
  adding a playbook doesn't touch SKILL.md

Plugin plumbing — you shouldn't need to touch these:

- `.mcp.json` — declares the bundled FactIQ MCP server (Streamable HTTP,
  OAuth). Read by both Claude Code and Codex plugin loaders
- `.claude-plugin/` — Claude and Claude Code plugin + marketplace manifests
- `.codex-plugin/` — ChatGPT and Codex plugin manifest
- `.codex-plugin/plugin.json` uses the registered FactIQ app ID as its plugin
  name for ChatGPT app association
- `.agents/plugins/marketplace.json` — Codex marketplace entry for
  `codex plugin marketplace add defog-ai/factiq-plugin`

## Contributing

Contributions are welcome — this plugin is meant to grow with its community.
Open an issue or a pull request.

### Bespoke skills (domain playbooks) — the highest-leverage contribution

The most valuable thing you can add is a **domain playbook**: a reference file
that teaches the agent how to answer a whole class of questions well. A
playbook is a domain's dialectic written down in advance — the headline
reading a question invites, the contradictions a competent skeptic would
raise against it, and the SQL to fetch both (see the method in
[`references/report-patterns/README.md`](references/report-patterns/README.md)).
The existing ones live in
[`references/report-patterns/`](references/report-patterns/) and are the
pattern to follow:

- [`monetary-policy.md`](references/report-patterns/monetary-policy.md) —
  central bank policy stance, administered rates, OMO, balance-sheet context
- [`bilateral-trade.md`](references/report-patterns/bilateral-trade.md) —
  country-pair trade trends, product drivers, mirror-statistics caveats
- [`fiscal-policy-revenue.md`](references/report-patterns/fiscal-policy-revenue.md)
  — government receipts, tax composition, distributional detail

A good playbook contains:

1. **A trigger** — which question shapes it covers ("latest trend in trade
   between A and B", "explain the Fed's stance"), added as a row to the
   routing table in
   [`references/report-patterns/README.md`](references/report-patterns/README.md)
   so the agent reads the playbook *before* fetching. `SKILL.md` points at
   that router, so it doesn't need to change.
2. **Required coverage** — the domain's canonical antitheses: the
   counter-checks a complete answer must fetch (mirror statistics, real vs
   nominal, composition, the counterparty's ledger), so the agent doesn't
   stop at the first obvious chart.
3. **Ready SQL templates** — tested queries against the three-table schema for
   the key computations (latest-month YoY, YTD comparisons, top-N drivers).
4. **Caveats and guardrails** — unit normalization, base-year changes,
   national-vs-subnational traps, data gaps to disclose explicitly.

Ideas we'd love to see: labor-market health, inflation decomposition, energy
markets, housing, sovereign debt, sector earnings analysis, country
macro-risk snapshots.

### Other welcome contributions

- **SQL idioms and pitfalls** — additions to `references/data/sql-guide.md`
  from real usage.
- **Docs and fixes** — anything that makes the agent's first attempt land.

Test a playbook by running its questions end to end and checking the saved
chart or report output. Include exact before-and-after examples in the PR.

## Security

No secrets belong in this repo, and the plugin holds none — interactive
access goes through the MCP server's OAuth flow, so the coding agent holds the
token and nothing is written here. Headless access is set up outside this repo,
as described at [factiq.com/docs/api](https://www.factiq.com/docs/api). All SQL
runs read-only against FactIQ's data warehouse.

## License

[MIT](LICENSE)
