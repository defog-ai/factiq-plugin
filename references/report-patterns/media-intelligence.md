# Media-Appearance Intelligence

Use this playbook for questions about what was said outside earnings calls
on podcasts, television interviews, and at conferences, and about what
central banks and monetary authorities published: speeches, interviews, blog
posts, policy statements, press releases, meeting minutes, press-conference
transcripts, testimony before legislatures, and reports. The speakers are
company executives, investors, fund managers, analysts, economists,
journalists, central-bank officials, and other guests, and their claims cover
listed and unlisted companies (OpenAI, DeepSeek, MiniMax), institutions (the
Federal Reserve, the European Central Bank, regulators), and whole markets and
industries, not only the speaker's own employer. It covers coverage checks,
theme sweeps, timelines, cross-company comparisons, media-vs-earnings
comparisons, and central-bank position checks.

The corpus is a structured evidence source, not a transcript-reading agent.
Normal calls perform deterministic lexical retrieval over precomputed
public-safe claims and passage cards. No serving-time model interprets the
question, invents synonyms, or reads a video on demand.

## Retrieval Contract

For a non-empty query, retrieval stops at the first tier that returns
candidates:

1. strict full-text search;
2. loose any-term full-text search if strict search is empty;
3. trigram fallback if both full-text tiers are empty.

Strict results therefore rank ahead of broadened results, but a lower-tier row
may match only part of a multi-term query. Natural-language questions are
accepted because common question scaffolding and person terms are normalized,
not because the server semantically researches them. Begin with concise topical
language such as `export controls` or `AI infrastructure demand`. When recall
matters, retry a bounded synonym sweep using the company's own vocabulary, then
inspect each row for actual support before combining results.

Default `sort="relevance"` orders lexical score first and publication date
second. Explicit `sort="newest"` orders publication date first and lexical
score second. Do not invert that default when describing unsorted calls.

`date_from` and `date_to` are inclusive bounds on the video's stored
publication/upload date. That date may differ from the recording, conference,
or broadcast date. Label it as the publication date unless the linked source
independently establishes the event date. An official document also carries
`event_date`, the date of the meeting, speech, or hearing it belongs to. FOMC
minutes are published about three weeks after the meeting, so a minutes row
dated 2026-08-19 describes the meeting of 2026-07-29: report the meeting date
for what the Committee discussed and the publication date for when it became
public. A press-conference transcript is dated by its publication, and its
`event_date` is the day of the press conference.

## Official Documents

The same tool searches documents published by central banks and monetary
authorities from late 2025 onward: the Federal Reserve Board and the regional
Reserve Banks, the European Central Bank (including its banking-supervision
arm), the Bank of England, the Bank of Japan, the Reserve Bank of India, the
People's Bank of China, the Bank of Korea, the Hong Kong Monetary Authority,
Taiwan's central bank, and the national central banks of the euro area and
other EU members (the Bundesbank, the Banque de France, the Banca d'Italia,
the Banco de España, De Nederlandsche Bank, the Riksbank, the Czech National
Bank, Eesti Pank, and others). Parliamentary debates and hearings of
legislators are not included; the testimony rows are central-bank officials
speaking before a legislature.

- A document written in another language yields English paraphrases. Its
  title may stay in the source language.
- `channel` is the institution name, `video_title` the document title, and
  `speaker` the official who spoke or wrote; an institutional statement or
  press release names the institution as its speaker.
- In a press-conference transcript, a row whose speaker is `Questioner` is a
  journalist's question, not the institution's position.
- `institution` (a case-insensitive substring of the publisher, such as
  `"Bank of Japan"` or `"Bundesbank"`) and `country` (the ISO code of the
  publisher's jurisdiction: `"US"`, `"IN"`, `"EU"` for the European Central
  Bank) each restrict every target to official documents.
- `company` matches what a claim is about, not who published it:
  `company="European Central Bank"` also returns a Bank of England speech
  about the ECB. Use `institution` to select the publisher and `company` to
  select the subject.
- Official documents carry no ticker, so `coverage` with `institution` or
  `country` returns one `UNATTRIBUTED` row with the document count, date
  span, and claim count for that filter.
- `appearance_type` for official documents: `speech` (also blog posts and
  opening remarks), `tv_interview` (published interviews), `statement` (also
  implementation notes), `minutes` (also summaries of opinions),
  `press_conference`, `testimony`, `hearing`, and `other` (press releases,
  reports, projections). `document_kind` keeps the finer kind (`interview`,
  `press_release`, `report`, `blog`, `summary_of_opinions`).

## Targets and Result Shapes

Use the six canonical `search_target` values:

| Target | Use | Result shape | Empty `query` |
|---|---|---|---|
| `search` | Default theme discovery across high-signal claims and broad passage cards | Structured finding rows | Recent high-signal claims only; generic passages are excluded |
| `claims` | Normalized, decision-relevant executive claims | Structured finding rows with claim semantics | Recent claims |
| `passages` | Substantive topics that were not promoted to claims | Structured finding rows with claim-only fields null | Recent passage cards |
| `pressure_points` | Stored refusal and declined-to-confirm rows | Structured refusal rows | Recent refusal rows |
| `appearances` | Browse the video-level catalog | Video metadata rows | Recent catalog rows |
| `coverage` | Test company-level structured-corpus coverage | Company inventory rows | Company inventory |

`pressure_points` is not a complete map of interviewer questions or every
Q&A exchange. It contains the structured refusal/declined-to-confirm subset.

The public shapes differ:

- `search`, `claims`, `passages`, and `pressure_points` return
  `result_kind`, `canonical_paraphrase`, speaker, primary ticker, topic
  labels, video title/channel/publication metadata, lexical relevance, and
  `source_url`: a timestamped YouTube deep link for a video, the episode page
  for a podcast, or the document page for an official document (a PDF
  transcript links to the page the finding is on, `...pdf#page=4`). With
  `detail=true` they also carry `institution`, `document_kind`, and
  `event_date`, null on interview rows.
- `appearances` returns video-level title/channel/publication/type metadata,
  primary ticker, attribution fields, matching-claim count, URL, relevance,
  and `institution`, `document_kind`, and `event_date` (null on interview
  rows).
- `coverage` returns company-level appearance count, publication-date span,
  covered channels, structured-claim count, and low-confidence-attribution count.

## Parameters and Applicability

| Parameter | Guidance |
|---|---|
| `query` | Concise lexical topic. Empty strings browse according to the target table above |
| `search_target` | One of the six values in the table above |
| `company` | Comma-separated tickers and company names, mixed freely (`"NVDA,OpenAI,Federal Reserve"`). A stored ticker matches the appearance's company or a section subject with that ticker; any other value is matched as the name of a company, institution, or organisation a section is about, ignoring punctuation, a leading "The", and corporate suffixes (`"NVIDIA Corp."` finds NVIDIA; `"open ai"` finds OpenAI; `"Alphabet"` also reaches GOOGL rows). The result records `company_tickers`, `company_names`, `company_matched`, and `company_unmatched`; a value that matches nothing returns no rows and up to five possible matches under `company_unmatched`, not an error. The `appearances` and `coverage` targets also match every value, upper-cased, against the entity references of claims (products, rivals, partners such as `"CUDA"` or `"ChatGPT"`); a value found only there still filters those targets and is listed under `company_references`. Alternate spellings can return different `appearances` or `coverage` rows because reference names are matched exactly (`"open ai"` and `"OpenAI"` select the same subject but not the same references); the claims rows are the same |
| `company_filter` | Old name of `company`, still accepted with the same behaviour; the response note asks for a plugin update. Do not pass both |
| `person` | Case-insensitive name substring over finding and/or appearance speaker metadata |
| `sort` | `relevance` (default) or `newest`, with the exact ordering described above |
| `appearance_type` | Interviews: `podcast`, `tv_interview`, `conference`, or `other`. Official documents: `speech`, `tv_interview`, `statement`, `minutes`, `press_conference`, `testimony`, `hearing`, or `other` (see Official Documents). Applies to every target |
| `institution` | Case-insensitive substring of the institution that published an official document (`"Bank of Japan"`, `"Federal Reserve"`). Restricts every target to official documents; interview rows have no institution |
| `country` | ISO code of the publishing institution's jurisdiction (`"US"`, `"IN"`, `"EU"` for the European Central Bank). Restricts every target to official documents of that jurisdiction |
| `claim_family` | Claim-ontology code; invalid values return the vocabulary |
| `date_from`, `date_to` | Inclusive YYYY-MM-DD publication/upload-date bounds |
| `detail` | Adds normalized claim and attribution fields to finding targets; does not expose source text |
| `show` | Case-insensitive substring of the show or channel name (`"Odd Lots"`, `"Les experts"`); applies to every target |
| `limit` | One page of 1-50 rows; default 15 |
| `offset` | Ranked rows to skip before the page; default 0. `limit=15, offset=15` returns rows 16-30 of the same ranking. Every result carries `has_more` and, when more rows follow, `next_offset`; pass that as `offset` for the next page |

Detail does not change catalog rows.
A `claim_family` filter suppresses passage-card retrieval from blended
`search`, is incompatible with `search_target="passages"`, and requires
matching structured claims for `appearances` or `coverage`. With
`detail=true`, passage rows still have null claim-only fields. Detail never
returns raw transcript text, caption/evidence spans, extraction prompts, or
other internal provenance.

Every call returns at most 50 rows in one page. When the result says
`has_more`, read the next page with `offset=next_offset`, or narrow with
`company`, `person`, `show`, target, `appearance_type`, `institution`,
`country`, `claim_family`, or a smaller publication-date window and
synthesize bounded calls. Never use `run_sql` against the gated
`transcripts` schema or promise a complete transcript dump.

## Evidence Discipline

`canonical_paraphrase` is a normalized public-safe paraphrase, not a
transcript quotation. Never put it in quotation marks or claim it preserves
the speaker's exact words. Every reported finding should include:

- person and role when returned;
- company/ticker when available;
- video publication date, and `event_date` for an official document when it
  differs;
- video title and channel, or document title and institution;
- timestamped YouTube link, or the document page link.

Use phrasing such as “In a video published on 2026-05-12, X said that ...” or
“In the minutes of the FOMC meeting of 2026-07-29, published 2026-08-19, the
Committee ...” and cite the link. If exact wording, tone, hedging, or rhetorical emphasis is
load-bearing, follow the timestamped link and independently verify the source
before quoting or making a tone claim. `detail=true` does not relax this rule.

Absence must be scoped: “No matching structured row appeared in these bounded
lexical searches over the covered companies and publication dates.” It does
not prove the person never discussed the subject. Before drawing even that
limited conclusion, inspect `coverage`, retry company-native synonyms, and
disclose the targets, filters, date window, and row cap.

## Five Workflows

### 1. Coverage and date-window selection

1. Call `search_target="coverage"`, usually with one or more exact tickers.
   For a central bank, pass `institution` or `country` instead and read the
   single `UNATTRIBUTED` row it returns.
2. Read the company-level appearance count, publication-date span, channel
   inventory, structured-claim count, and attribution count.
3. If attribution is material, inspect `appearances` for the relevant company
   or person rather than treating an acquired-video count as structured
   coverage.
4. Choose a publication-date window supported by both coverage and the user's
   question. State that publication date may differ from event date.

Coverage is an inventory check, not evidence that a topic was or was not
discussed.

### 2. Broad theme sweep and drill-down

1. Check `coverage` for any named companies.
2. Run a concise theme query with `search_target="search"` and
   `sort="relevance"`.
3. Inspect `result_kind` and match quality. Do not silently treat a loose or
   trigram result as support for every query term.
4. Retry one or two company-native synonyms when recall matters.
5. Drill down with `claims` for normalized decision-relevant positions and
   `passages` for broader context. Use `pressure_points` only for refusals.
6. Deduplicate repeated cards from the same timestamp and keep claim versus
   passage evidence labeled.

### 3. Person or company timeline

1. Check `coverage`, then choose explicit `date_from` and `date_to`.
2. Filter by ticker and/or `person`, or by `institution` for a central
   bank's own timeline; use `appearances` first when identity or attribution
   needs confirmation.
3. Search the theme with explicit `sort="newest"`.
4. If the window is large, split it into non-overlapping date ranges, or
   page through one ranking with `offset=next_offset`, rather than relying
   on one capped result.
5. Order findings by publication date and preserve venue, audience, and topic
   context. A wording difference between paraphrases is not evidence of a tone
   or position change.

### 4. Cross-company theme comparison

1. Run `coverage` for all tickers and choose a comparable publication window.
2. Use the same concise query, synonyms, target, sort, and date bounds for each
   company, preferably in separate calls so a prolific company cannot consume
   the shared row cap.
3. Compare only like result kinds. Separate a structured claim from a broad
   passage card or refusal.
4. Report unequal coverage and lexical misses. Do not convert more returned
   rows into “greater executive emphasis” without a denominator and sampling
   argument.

### 5. Media versus earnings

1. Check `search_media_appearances(search_target="coverage")` and
   `search_earnings_transcripts(search_target="coverage")` first.
2. Align ticker, person, theme, and comparable dates/fiscal periods. A video's
   publication date is not automatically an earnings-call period.
3. Search media using the theme sweep above. Search earnings with the same
   concise vocabulary, exact comparable `quarter_filter`, and appropriate
   `claims` / `pressure_points` targets.
4. Keep evidence classes separate. Earnings `verbatim_quote` may support a
   quotation; media `canonical_paraphrase` supports only a paraphrase unless
   the linked source has been independently checked.
5. Describe media as statements made “outside an earnings call.” Do not imply
   the appearance was necessarily unprepared.
6. Do not infer a tone shift from paraphrase wording alone. Separate a real
   change in position from differences in venue, audience, question, and date.

The synthesis should identify what is genuinely consistent or changed across
the two evidence sets, name the contextual alternatives, and state what further
source verification would falsify the interpretation.
