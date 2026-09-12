# Behaviour evaluations for the FactIQ plugin

These evaluations check what Claude does when the FactIQ plugin is
installed. The unit tests in `tests/` check the wording of the documentation
and the output of the bundled scripts. These evaluations check behaviour: the
answer the user gets, the files that are written, and the tool calls made.

Every case is run twice: once with the full plugin, and once against a
baseline plugin that has the same mocked FactIQ tools but no skill and no
scripts. The difference between the two scores is what the skill and the
scripts add on top of the raw tools.

## How to run

From the plugin root, with the model pinned:

```bash
python3 evals/run_ablation.py --model opus --judge-model sonnet
```

The script runs `claude plugin eval` twice under `--ablation none`: first on
the plugin itself, then on a temporary copy that keeps only the manifest and
the MCP configuration. Both runs use the same mocks, the same judge, and the
same tool grants. Results land in `evals/results/<timestamp>/with/` and
`.../baseline/`, with a `comparison.md` beside them that lists every case and
every grader in both arms. The exit code is 1 when a with-plugin case scores
below `--threshold` (default 0.8).

Useful variants:

```bash
# one or a few cases, one run each, while you change graders
python3 evals/run_ablation.py --model opus --runs 1 --case 'yoy-*'
python3 evals/run_ablation.py --model opus --runs 1 --tag filings --tag charts

# only the with-plugin arm
python3 evals/run_ablation.py --model opus --skip-baseline

# keep each run's sandbox so you can read its trace.jsonl and mock-calls.jsonl
python3 evals/run_ablation.py --model opus --keep-temp
```

`--case` takes one name glob. `--tag` may be repeated and selects every case
that carries any of the tags.

A full run of eight cases at three runs each costs about 25 US dollars across
the two arms and takes about half an hour at four concurrent runs. The GitHub
workflow `behaviour-evals.yml` runs the same script by hand from the Actions
tab and needs an `ANTHROPIC_API_KEY` secret. Nothing in this directory runs
on push or pull request; the unit tests in `tests/` do.

### Why not the built-in with/without comparison

`claude plugin eval --ablation with-without` removes the whole plugin from the
second arm, including its MCP server. That arm then has no FactIQ tools at
all, so every data case fails there for a reason that has nothing to do with
the skill. The baseline built by `run_ablation.py` keeps the tools and drops
only the skill and the scripts, which is the comparison that says what the
plugin's documentation is worth.

### What the sandbox provides

- `Bash`, `Write` and `Edit` are given only when `--allow-tools` names them.
  The script passes `Write,Edit,Bash` by default. `Bash` needs `bubblewrap`
  and `socat` installed; without them the run is refused.
- Inside a run `CLAUDE_PLUGIN_ROOT` is empty, so the model cannot use it to
  find `scripts/`. It can still reach the checked-out plugin at its real path
  on this machine and in practice finds the scripts by searching. On a
  machine where the plugin is not on disk, the checks that require
  `trade_sql.py` or `term_chart.py` fail while the checks on the answer still
  pass.
- Tool names inside the sandbox are `mcp__plugin_factiq_factiq__<tool>`.
  Every `tool_used` grader on a FactIQ tool uses that form.
- `--judge-model` sets the model that grades `llm` checks; each such check is
  voted on three times and passes on two votes. Judged checks can disagree
  with themselves between runs, so a check that must be exact (a link, a
  doubled figure) is written as a `regex` check.

## The data server is mocked

The cases never call `api.factiq.com`. The files in `mocks/factiq/` answer
each FactIQ tool, so the runs need no login, spend no server quota, and see
the same data every time. `mocks/factiq/_tools.json` is the real tool list
with the real descriptions and input schemas (14 tools). Only tools that have
a mock file exist inside a run; `get_market_data`, `get_geo_data`,
`search_media_appearances`, `search_news` and `send_feedback` have none and
are therefore absent.

Two mocks answer according to their arguments:

- `get_series` returns `fixtures/<series_id>.json`. Only `LNS14000000`
  exists, so a request for any other series id gets a "no such fixture" tool
  error, which is the closest stand-in for an unknown series. The
  `transform` argument is ignored: a request for a year-over-year transform
  receives the plain monthly values.
- `search_company_filings` returns `fixtures/<company>.json`. Only `PKG`
  exists. The same payload is returned for every `search_target`, so a
  coverage query gets the facts result.

The rest are fixed. `run_sql` returns the same 31 unemployment rows whatever
statement it is given, which is why the trade case asks for the query rather
than the numbers.

The fixtures are real payloads taken from the server:

- **US unemployment rate** (BLS series `LNS14000000`), 31 monthly values from
  January 2024 to August 2026, served by `get_series` and `run_sql`. **The
  series has no observation for October 2025.** The live server attaches a
  `coverage_note` that names the gap and warns against row-offset
  arithmetic. The case `yoy-across-a-missing-month` keeps that note; the case
  `yoy-without-a-server-hint` overrides the mocks from its own `mocks/`
  directory with the note removed, so it measures the skill's own rule.
- **Packaging Corporation of America segment revenue** for the quarter ended
  June 2026, served by `search_company_filings`: eight facts in which the
  Packaging segment total appears twice, once as its own series and once
  labelled "(reported line 2)". The live server attaches a note to the
  second copy saying the two must not be added; the fixture has that note
  removed so the case measures the skill's rule, and the only marker left is
  the label.
- **NVIDIA gross-margin statements**, four rows served by
  `search_earnings_transcripts`. **The source link on the third row was
  blanked on purpose** so the case can check that the answer says the direct
  link is unavailable instead of inventing one.

## The cases

| Case | What it checks |
| --- | --- |
| `latest-value-direct-answer` | A one-number question gets a one-sentence answer with the period and the source, and no chart and no report file. |
| `quick-chart-of-a-trend` | A single-trend question writes one valid ChartSpec whose title states a finding, renders it with `term_chart.py`, pastes the preview, leaves the missing month empty, and says so. |
| `yoy-across-a-missing-month` | Year-over-year is computed by calendar date, and the missing month is stated, not filled in. The server note about the gap is present. |
| `yoy-without-a-server-hint` | The same request with the server note removed. |
| `bilateral-trade-sql` | A bilateral-trade query is built with the bundled generator, filters the partner by China customs' numeric code, pins one HS level, and keeps quantity series out of the value total. |
| `filings-duplicate-line` | A figure filed twice in one report is reported once, not doubled, with the filing's own link. |
| `quote-and-source-discipline` | Quotes are verbatim, each carries the exact supplied source link, a missing link is declared, and an analyst's words are not reported as the company's. |
| `unrelated-coding-request` | A plain Python question is answered directly, with no FactIQ tool call and no skill invocation. |

## Adding a case

Make a directory under `evals/` with a `prompt.md` and a `graders/`
directory. The body of `prompt.md` is the user's message; its front matter
sets the run options. Each file in `graders/` is one check; the file name is
the check's name. A case that needs different data puts its own
`mocks/factiq/<tool>.md` beside `prompt.md`; those files override the suite's
mocks one file at a time.

Rules to keep:

1. Grade the answer, not the route to it. A check on which tool was called is
   a weak signal, so give it a low weight.
2. A check only passes if the case allows the tool that produces the thing
   being checked. If a grader looks for a written file, the case must allow
   `Write`, and the prompt must fix the file's path so the grader can read it.
3. A negative tool check needs both `min: 0` and `max: 0`. With `max: 0` alone
   the check reads as "between 1 and 0" and can never pass.
4. A `tool_used` check on a FactIQ tool names it
   `mcp__plugin_factiq_factiq__<tool>`. The short form `mcp__factiq__<tool>`
   never matches inside the sandbox, so a "must not call" check written that
   way passes no matter what happened.
5. Say in the grader what does not matter. A judge that is left to guess about
   layout or wording will disagree with itself between runs.
6. A mock that reads `{{input.<field>}}` must only use fields the tool
   requires. A missing field inside a `{{file:...}}` path is a tool error, and
   an `expect:` guard on a missing field aborts the run with score 0.
