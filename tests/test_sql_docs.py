import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "skills/factiq/SKILL.md").read_text(encoding="utf-8")
SQL_GUIDE = (ROOT / "references/data/sql-guide.md").read_text(encoding="utf-8")
CHART_SPEC = (ROOT / "references/output/chart-spec.md").read_text(encoding="utf-8")
REPORT_RULES = (ROOT / "references/report-patterns/README.md").read_text(
    encoding="utf-8"
)
JOIN = "date_trunc('month', prior.time) = date_trunc('month', cur.time) - interval '1 year'"
YOY_TRAP = SQL_GUIDE.split("## Year-over-year on monthly data", 1)[1].split(
    "## HS trade datasets", 1
)[0]


def normalized(text: str) -> str:
    return " ".join(text.lower().split())


class PeriodAlignmentDocumentationTests(unittest.TestCase):
    """A row offset is not a period offset once a month is missing; the docs
    must steer every year-over-year calculation to a date match."""

    def test_sql_guide_states_time_is_the_period_start(self):
        conventions = SQL_GUIDE.split("## Always-true conventions", 1)[1].split(
            "\n## ", 1
        )[0]
        self.assertIn(
            "**Match periods on the calendar month, never on the exact date.**",
            conventions,
        )
        self.assertIn(JOIN, conventions)

    def test_sql_guide_trap_shows_lag_as_bad_and_date_join_as_good(self):
        bad, good = YOY_TRAP.split("Good", 1)
        self.assertIn("Bad", bad)
        self.assertIn("LAG(value, 12) OVER (ORDER BY time)", bad)
        self.assertIn(JOIN, good)
        self.assertNotIn("prior.time = cur.time - interval", good)
        self.assertIn("date_trunc('quarter', ...)", good)
        self.assertIn("generate_series(", good)
        self.assertIn("ON date_trunc('month', d.time) = s.time", good)
        self.assertIn('transform="yoy_pct"', good)

    def test_sql_guide_trap_tells_the_model_to_disclose_gaps(self):
        text = normalized(YOY_TRAP)
        self.assertIn("coverage_note", text)
        self.assertIn("missing_periods", text)
        self.assertIn("partial", text)
        self.assertIn("blank", text)

    def test_sql_guide_pivot_says_a_missing_period_is_absent_not_null(self):
        pivot = SQL_GUIDE.split("## Pivoting to wide format", 1)[1].split(
            "\n## ", 1
        )[0]
        self.assertIn("absent from the pivot, not a null", pivot)

    def test_skill_get_series_row_documents_transform(self):
        row = next(line for line in SKILL.splitlines() if line.startswith("| `get_series`"))
        self.assertIn("`transform?`", row)
        self.assertIn('transform="yoy_pct"', row)
        self.assertIn('"yoy_diff"', row)
        self.assertIn("matched by calendar date", row)
        self.assertIn("`coverage_note`", row)

    def test_skill_workflow_and_subagent_template_forbid_row_offsets(self):
        compute_step = SKILL.split("**Compute deterministically.**", 1)[1].split(
            "\n5. ", 1
        )[0]
        self.assertIn("matched by date", compute_step)
        self.assertIn(JOIN, compute_step)
        self.assertIn("never compare exact", compute_step)
        self.assertIn("never `LAG(value, 12)`", compute_step)
        self.assertIn("`missing_periods`", compute_step)
        template = SKILL.split("You are a FactIQ research agent", 1)[1].split(
            "FINDINGS:", 1
        )[0]
        self.assertIn("never a 12-row offset", template)
        self.assertIn("coverage_note", template)

    def test_skill_errors_section_explains_coverage_note(self):
        errors = SKILL.split("## Errors and limits", 1)[1].split("\n## ", 1)[0]
        self.assertIn("**`coverage_note` on a result**", errors)
        self.assertIn("not an error", errors)
        self.assertIn("matching dates", errors)

    def test_report_rules_disclose_missing_periods(self):
        rules = REPORT_RULES.split("## Rules the method implies", 1)[1]
        self.assertIn("**A missing period is disclosed, not bridged.**", rules)
        self.assertIn("`coverage_note`", rules)

    def test_no_doc_endorses_a_row_offset_yoy(self):
        # `shift(12)` / a bare LAG-by-12 may appear only inside the "Bad" example
        # or in text that names it as the wrong pattern.
        for name, text in (
            ("SKILL.md", SKILL),
            ("chart-spec.md", CHART_SPEC),
            ("README.md", REPORT_RULES),
        ):
            with self.subTest(doc=name):
                self.assertNotIn(".shift(12)", text)
        self.assertNotIn("shift(12)", CHART_SPEC)
        for match in re.finditer(r"LAG\(value, 12\)", SQL_GUIDE):
            window = SQL_GUIDE[max(0, match.start() - 600) : match.start()]
            self.assertTrue(
                "Bad" in window or "spine" in window or "never" in window,
                msg=SQL_GUIDE[match.start() - 120 : match.end() + 40],
            )

    def test_chart_spec_lineage_uses_a_date_matched_calculation(self):
        calc = CHART_SPEC.split('"id": "calc"', 1)[1].split("}", 1)[0]
        self.assertIn('transform=\\"yoy_diff\\"', calc)
        self.assertNotIn("12-month difference", calc)


class ChartSpecRequiredKeysTests(unittest.TestCase):
    """The renderer reads no `id` and no y-axis key, so the docs must not
    require `id` and must name one y-axis label form."""

    def test_id_is_not_a_required_key(self):
        required = CHART_SPEC.split("Required:", 1)[1].split("\n\n", 1)[0]
        self.assertNotIn("`id`", required)
        self.assertNotIn("`id`", SKILL.split("required keys are", 1)[1].split(")", 1)[0])

    def test_y_axis_label_form_is_stated(self):
        optional = CHART_SPEC.split("Optional:", 1)[1].split("\n\n", 1)[0]
        self.assertIn("`yAxisLabel`", optional)
        self.assertIn("not as a\n`yAxis` object", optional)


class HsNamesTableTests(unittest.TestCase):
    TRADE = SQL_GUIDE.split("## HS trade datasets", 1)[1].split("### Eurostat", 1)[0]

    def test_docs_name_the_hs_names_table_and_the_left_join(self):
        for text in (self.TRADE, SKILL):
            self.assertIn("`eu_comext_lookup.hs_names`", text)
            self.assertIn("LEFT JOIN", text)
            self.assertIn("`eu_comext_lookup.partner_aliases`", text)
            self.assertIn("Japan stores 9-digit", text)
            self.assertIn("`census` query cannot join", text)


class CompanyScreenerDocumentationTests(unittest.TestCase):
    """A question such as "technology companies with price-to-sales above 10"
    is answered by one query on the view screener.companies; every doc that
    routes questions must point there, and the guide must carry the rules
    that change the answer."""

    SCHEMAS = (ROOT / "references/data/schemas.md").read_text(encoding="utf-8")
    SECTION = SQL_GUIDE.split("## Company screener", 1)[1].split(
        "## Pivoting to wide format", 1
    )[0]

    def test_schema_table_lists_the_screener_and_points_to_the_guide(self):
        row = next(
            line for line in self.SCHEMAS.splitlines() if line.startswith("| `screener` |")
        )
        self.assertIn("`screener.companies`", row)
        self.assertIn("`price_as_of`", row)
        self.assertIn("references/data/sql-guide.md", row)

    def test_routing_list_sends_condition_questions_to_the_view(self):
        routing = normalized(self.SCHEMAS)
        self.assertIn("companies that match conditions", routing)
        self.assertIn("`run_sql` query on `screener.companies`", routing)

    def test_skill_workflow_names_the_view_and_the_guide_section(self):
        skill = normalized(SKILL)
        self.assertIn("`screener.companies`", skill)
        self.assertIn("**company screener**", skill)

    def test_guide_lists_the_columns_a_condition_needs(self):
        for column in (
            "sector",
            "market_cap",
            "price_to_sales",
            "price_to_earnings",
            "enterprise_value",
            "revenue_ttm",
            "revenue_growth_yoy",
            "reporting_currency",
            "price_as_of",
            "fundamentals_period_end",
        ):
            self.assertIn(f"`{column}`", self.SECTION)

    def test_guide_example_filters_the_view_and_limits_the_result(self):
        example = self.SECTION.split("```sql", 1)[1].split("```", 1)[0]
        self.assertIn("FROM screener.companies", example)
        self.assertIn("ORDER BY", example)
        self.assertIn("LIMIT", example)

    def test_guide_states_the_rules_that_change_the_answer(self):
        rules = normalized(self.SECTION)
        self.assertIn("select sector, count(*) from screener.companies", rules)
        self.assertIn("a ratio is null when its bottom number is zero or negative", rules)
        self.assertIn("`reporting_currency` is not usd", rules)
        self.assertIn("the last us market close, not prices during the session", rules)
        self.assertIn("state `price_as_of` in the answer", rules)
        self.assertIn("`get_market_data`", rules)


if __name__ == "__main__":
    unittest.main()
