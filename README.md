# FactIQ - a real-time finance and economy database for AI Agents

Turn your agent into a finance and economy analyst. This plugin for Claude
(web, desktop, and Cowork), ChatGPT (web and desktop), Claude Code, and Codex gives the
agent direct access to
FactIQ's warehouse of official statistics — SEC filings, US, China, India, Korea, IMF,
World Bank, and more — plus live market data, earnings-call transcripts,
executive media appearances, central-bank speeches, minutes, and statements,
and satellite-derived data (fire detections,
air-quality activity signals,
rainfall, nighttime lights, shipping and port activity, reservoir levels).
The agent discovers series, runs read-only SQL, computes derived metrics, and
returns a sourced answer, chart JSON, or report JSON.

No codebase or hosted database is required — only a free
[FactIQ account](https://factiq.com).

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

Every FactIQ tool also works with a personal API key instead of the browser
sign-in. Create the key at [factiq.com/settings/security](https://www.factiq.com/settings/security).
The guide at [factiq.com/docs/api](https://www.factiq.com/docs/api) shows how
to call the REST endpoints and the MCP server with the key, and how to register
the server in Claude Code or Codex without a browser. Keep the key out of
source control. Regenerating it on the settings page revokes the old one
immediately.

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
│             search_media_appearances, search_news
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│  FactIQ data warehouse      │      official and derived data sources
└─────────────────────────────┘
```

The reason a single skill can query BLS unemployment, Chinese customs flows,
RBI monetary data, and World Bank indicators with the same SQL idioms: **every
data source in the backend is normalized into the same three core tables**,
identical in every schema:

| Table | What it holds |
|---|---|
| `series` | The catalog — one row per series: id, title, description, dataset, frequency, units, seasonality, geography, time coverage |
| `data_points` | The values — `(series_id, time, value)`, indexed for fast retrieval |
| `dimensions` | Faceted metadata — `(series_id, dimension_type, dimension_code, dimension_name)`, e.g. `partner`, `flow`, `commodity`, `hs_level` for trade data |

Our ingestion pipelines do the hard work of flattening each source's bespoke
format — BLS flat files, BEA APIs, customs records, RBI releases — into this
shape, so the agent learns the model once and it works everywhere. Discovery,
pivoting, and filtering follow the same patterns across all ~20 schemas; the
recipes live in [`references/data/sql-guide.md`](references/data/sql-guide.md).

### What's in the warehouse

| Region | Schemas |
|---|---|
| United States | SEC filings data, BLS (employment, CPI, JOLTS, OEWS), Census (trade incl. HS-level, retail, housing), BEA (GDP, income), EIA (energy), USDA ERS, BTS (transportation), earnings-call transcripts, executive media appearances, Federal Reserve speeches, testimony, statements, minutes, and press-conference transcripts |
| China | NBS macro indicators, GACC customs (HS-level trade) |
| India | MOSPI (CPI, WPI, IIP, GDP), RBI (banking, rates, forex), DGCI&S trade (HS-level), Bengaluru road traffic (2026 onward, that one city only), RBI speeches and press releases |
| South Korea | KCS customs (HS-level trade) |
| European Union | Eurostat Comext monthly trade for all 27 member-state reporters, by CN8 product and partner country; European Central Bank and national central-bank speeches, interviews, statements, and minutes |
| Global | IMF (including the recent earlier releases of its forecasts, so a revision can be traced), World Bank, Singapore SingStat, live market data (quotes, fundamentals, FX, commodities), central-bank documents from the UK, Japan, China, Korea, Hong Kong, and Taiwan |

`references/data/schemas.md` has the static overview; the `get_data_catalog` tool
returns the live, authoritative version.

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
token and nothing is written here. Headless use relies on a personal API key
that you create on the FactIQ settings page and keep in your own environment;
it is never stored in this repo. All SQL runs read-only against FactIQ's data
warehouse.

## License

[MIT](LICENSE)
