# Evaluations for the FactIQ plugin

These evaluations check what Claude actually does when the FactIQ plugin is
installed. The unit tests in `tests/` check the wording of the documentation.
These evaluations check behaviour.

Every case runs three times with the plugin installed and three times without
it. The difference between the two sides shows what the plugin adds.

## How to run

From the plugin root:

```bash
claude plugin eval . --ablation with-without --judge-model sonnet \
  --allow-tools Write,Edit,Bash
```

A quick single-pass run while you change graders:

```bash
claude plugin eval . --runs 1 --ablation with-without --no-scaffold --no-publish \
  --judge-model sonnet --allow-tools Write,Edit,Bash
```

One case only:

```bash
claude plugin eval . --case bilateral-trade-sql --ablation with-without \
  --no-scaffold --no-publish --judge-model sonnet --allow-tools Write,Edit,Bash
```

A case's `allowed_tools` is only a request. The tool is given to the model only
if `--allow-tools` also names it, so keep the two lists in step.

**About the shell.** `Bash` is given only on a machine that can confine it. That
needs both `bubblewrap` and `socat` installed. Without them the whole run is
refused with an error, not a warning. If your machine lacks either package,
drop `Bash` from `--allow-tools`; the trade case then loses its one tool check
but still grades the SQL it produces.

**About the plugin directory.** Inside the sandbox `CLAUDE_PLUGIN_ROOT` is
empty, so the model cannot use that variable to find `scripts/`. It can still
reach the checked-out plugin at its real path on this machine, and in practice
it finds `trade_sql.py` by searching. On a machine where the plugin is not on
disk, the trade case's `used-the-bundled-generator` check will fail while the
SQL checks still pass.

**About the models.** No case pins a model, so the runs use whatever model the
`claude` command is set to. The results in the pull request that added these
cases came from Opus 5. The `--judge-model sonnet` flag sets the model that
grades the answers; each judged check is voted on three times. Judged checks
can disagree with themselves between runs, so a check that must be exact — a
link target, for example — is written as a `regex` check instead.

Results are written to `evals/results/<timestamp>/`. Read
`aggregate-result.json` for the per-run scores and the judge's evidence, or
open `report.html`.

## The data server is mocked

The cases never call `api.factiq.com`. The files in `mocks/factiq/` give a
canned answer for each FactIQ tool, so the runs need no login, cost no server
quota, and give the same data every time.

`mocks/factiq/_tools.json` holds the real tool names, descriptions and input
schemas. Without it, the run without the plugin would see tools with no
descriptions and would look worse than it really is.

Two fixtures carry the data the cases are built on.

**US unemployment rate** (BLS series `LNS14000000`), 31 monthly values from
January 2024 to August 2026, served by `get_series` and `run_sql`. This is a
real payload taken from the live server. **The series has no observation for
October 2025.** That gap is what makes the year-over-year case meaningful:
matching each month to the same month a year earlier gives one answer, and
counting twelve rows back gives a different one.

**NVIDIA gross-margin statements**, four real rows served by
`search_earnings_transcripts`: a CEO answer whose quote contains a `[…]`
omission marker, a CFO prepared remark, a CFO forward-looking answer, and an
analyst's own framing marked `analyst_hypothesized`. Three rows carry their real
source links. **The source link on the third row was blanked on purpose** so
the case can check that the answer says the direct link is unavailable instead
of inventing one.

## Known limits of the mocks

- A canned answer cannot react to its arguments. If the model asks
  `get_series` for a year-over-year transform, it still receives the plain
  monthly values and has to do the arithmetic itself. That is the exact place
  where the row-offset mistake appears, so the case still tests what it means
  to test — but a model that asks the server to do the work may be marked wrong
  for reporting the raw values. Check the trace before you trust a failure of
  this kind.
- `run_sql` returns the same 31 unemployment rows whatever statement it is
  given. This is why the trade case asks for the query rather than the numbers:
  the answer under test is the SQL text, so the wrong rows are never fetched.
- `get_style_guides` returns a short neutral stand-in, not the guides the live
  server returns.
- The run directory does not contain the plugin's `term_chart.py`, so the model
  cannot draw a terminal chart in the run directory. The chart checks therefore
  only prove that the model did not try.

## The cases

| Case | What it checks |
| --- | --- |
| `latest-value-direct-answer` | A one-number question gets a one-sentence answer with the period and the source, and no chart and no report file. |
| `yoy-across-a-missing-month` | Year-over-year is computed by calendar date, and the missing month is stated, not filled in. |
| `bilateral-trade-sql` | A bilateral-trade query uses China customs' numeric partner code, one HS level, and value series only, and is built with the bundled generator. |
| `quote-and-source-discipline` | Quotes are verbatim, each carries the exact supplied source link and label, a missing link is declared, and an analyst's words are not reported as the company's. |
| `unrelated-coding-request` | A plain Python question is answered directly, with no FactIQ tool call. |

## Adding a case

Make a directory under `evals/` with a `prompt.md` and a `graders/`
directory. The body of `prompt.md` is the user's message; its front matter sets
the run options. Each file in `graders/` is one check; the file name is the
check's name.

Four rules to keep:

1. Grade the answer, not the route to it. A check on which tool was called is
   a weak signal, so give it a low weight.
2. A check only passes if the case allows the tool that produces the thing
   being checked. If a grader looks for a written file, the case must allow
   `Write`.
3. A negative tool check needs both `min: 0` and `max: 0`. With `max: 0` alone
   the check reads as "between 1 and 0" and can never pass.
4. Say in the grader what does not matter. A judge that is left to guess about
   layout or wording will disagree with itself between runs.
