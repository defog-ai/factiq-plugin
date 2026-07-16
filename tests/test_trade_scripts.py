import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(name, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class SqlGeneratorTests(unittest.TestCase):
    def test_comext_rejects_empty_reporters_without_traceback(self):
        result = run_script(
            "comext_sql.py",
            "total",
            "--reporters",
            "",
            "--partner",
            "cn",
            "--flow",
            "imports",
            "--start",
            "2025-01",
            "--end",
            "2025-12",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least one EU member", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_comext_deduplicates_reporters(self):
        result = run_script(
            "comext_sql.py",
            "total",
            "--reporters",
            "de,de",
            "--partner",
            "cn",
            "--flow",
            "imports",
            "--start",
            "2025-01",
            "--end",
            "2025-12",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("FROM data_points"), 1)
        self.assertNotIn("UNION ALL", result.stdout)

    def test_comext_rejects_invalid_codes_limits_and_unsafe_supplementary_sums(self):
        common = (
            "--reporters",
            "de",
            "--partner",
            "cn",
            "--flow",
            "imports",
            "--start",
            "2025-01",
            "--end",
            "2025-12",
        )
        bad_hs = run_script("comext_sql.py", "trend", *common, "--hs", "85ab")
        bad_top = run_script("comext_sql.py", "products", *common, "--top", "0")
        bad_sum = run_script(
            "comext_sql.py", "total", *common, "--metric", "supplementary"
        )
        exact = run_script(
            "comext_sql.py",
            "trend",
            *common,
            "--metric",
            "supplementary",
            "--hs",
            "85076000",
        )
        self.assertNotEqual(bad_hs.returncode, 0)
        self.assertNotEqual(bad_top.returncode, 0)
        self.assertIn("product-specific units", bad_sum.stderr)
        self.assertEqual(exact.returncode, 0, exact.stderr)
        self.assertIn("_su'", exact.stdout)

    def test_trade_hs_level_override_aggregates_finer_lines(self):
        result = run_script(
            "trade_sql.py",
            "trend",
            "--source",
            "korea",
            "--partner",
            "china",
            "--flow",
            "exports",
            "--start",
            "2025-01",
            "--end",
            "2025-12",
            "--hs",
            "854232",
            "--level",
            "10",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dimension_code = '10'", result.stdout)
        self.assertIn("dimension_code LIKE '854232%'", result.stdout)
        self.assertNotIn("exact series:", result.stdout)

    def test_trade_rejects_empty_partner_nonstandard_hs_and_bad_quantity_level(self):
        common = (
            "--source",
            "korea",
            "--flow",
            "exports",
            "--start",
            "2025-01",
            "--end",
            "2025-12",
        )
        empty = run_script("trade_sql.py", "total", *common, "--partner", "")
        group = run_script(
            "trade_sql.py",
            "trend",
            *common,
            "--partner",
            "china",
            "--hs",
            "123",
        )
        quantity = run_script(
            "trade_sql.py",
            "trend",
            *common,
            "--partner",
            "china",
            "--hs",
            "854232",
            "--metric",
            "quantity",
            "--level",
            "10",
        )
        self.assertIn("cannot be empty", empty.stderr)
        self.assertIn("not a 2/4/6-digit HS group", group.stderr)
        self.assertIn("must match the code length", quantity.stderr)

    def test_generators_reject_noncanonical_months(self):
        for script, prefix, partner in (
            ("comext_sql.py", ("total", "--reporters", "de"), "cn"),
            ("trade_sql.py", ("total", "--source", "census"), "china"),
        ):
            result = run_script(
                script,
                *prefix,
                "--partner",
                partner,
                "--flow",
                "imports",
                "--start",
                "2025-1",
                "--end",
                "2025-12",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be YYYY-MM", result.stderr)


class HsCodeTests(unittest.TestCase):
    def test_lookup_requires_numeric_code(self):
        result = run_script("hs_codes.py", "abcdef")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("2-, 4-, or 6-digit HS code", result.stderr)

    def test_search_validates_limit_and_whitespace(self):
        blank = run_script("hs_codes.py", "--search", "   ")
        punctuation = run_script("hs_codes.py", "--search", ";;;")
        limit = run_script("hs_codes.py", "--search", "battery", "--limit", "0")
        self.assertIn("must contain", blank.stderr)
        self.assertIn("must contain", punctuation.stderr)
        self.assertNotEqual(limit.returncode, 0)

    def test_everyday_search_still_finds_lithium_ion_batteries(self):
        result = run_script(
            "hs_codes.py", "--search", "lithium ion battery", "--limit", "3"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("850760", result.stdout)


class SeriesMathTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.directory = Path(self.tempdir.name)

    def payload(self, name, columns, rows):
        path = self.directory / name
        path.write_text(
            json.dumps({"columns": columns, "results": rows}), encoding="utf-8"
        )
        return path

    def test_missing_group_and_duplicate_periods_are_clear_errors(self):
        path = self.payload(
            "rows.json",
            ["month", "reporter", "value"],
            [["2025-01-01", "de", 1], ["2025-01-15", "de", 2]],
        )
        missing = run_script(
            "series_math.py", "yoy", "--file", path, "--group-col", "country"
        )
        duplicate = run_script(
            "series_math.py", "yoy", "--file", path, "--group-col", "reporter"
        )
        self.assertIn("not in columns", missing.stderr)
        self.assertIn("duplicate period", duplicate.stderr)
        self.assertNotIn("Traceback", missing.stderr + duplicate.stderr)

    def test_payload_shape_and_nonfinite_values_are_rejected(self):
        short = self.payload("short.json", ["month", "value"], [["2025-01-01"]])
        nan_path = self.directory / "nan.json"
        nan_path.write_text('{"columns":["month","value"],"results":[["2025-01",NaN]]}')
        short_result = run_script("series_math.py", "yoy", "--file", short)
        nan_result = run_script("series_math.py", "yoy", "--file", nan_path)
        self.assertIn("1 values for 2 columns", short_result.stderr)
        self.assertIn("invalid numeric constant", nan_result.stderr)

    def test_malformed_timestamp_is_rejected(self):
        path = self.payload(
            "timestamp.json", ["month", "value"], [["2025-01-01Tnot-a-time", 1]]
        )
        result = run_script("series_math.py", "yoy", "--file", path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid ISO timestamp", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_yoy_preserves_large_decimal_values_and_accepts_annual_periods(self):
        path = self.payload(
            "annual.json",
            ["year", "value"],
            [
                ["2024", "12345678901234567890.123"],
                ["2025", "24691357802469135780.246"],
            ],
        )
        result = run_script("series_math.py", "yoy", "--file", path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("12345678901234567890.123", result.stdout)
        self.assertIn("2025\t24691357802469135780.246\t100", result.stdout)

    def test_ytd_leaves_growth_blank_when_period_coverage_differs(self):
        path = self.payload(
            "gaps.json",
            ["month", "value"],
            [["2024-01", 10], ["2024-02", 20], ["2025-02", 40]],
        )
        result = run_script("series_math.py", "ytd", "--file", path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2025-02\t40\t\n", result.stdout)

    def test_share_matches_same_month_with_different_date_labels(self):
        path = self.payload(
            "share.json",
            ["date", "reporter", "value"],
            [["2025-01-01", "de", 25], ["2025-01-15", "fr", 75]],
        )
        result = run_script(
            "series_math.py",
            "share",
            "--file",
            path,
            "--group-col",
            "reporter",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("de\t2025-01-01\t25\t25", result.stdout)
        self.assertIn("fr\t2025-01-15\t75\t75", result.stdout)

    def test_merge_scales_only_the_value_column(self):
        path = self.payload(
            "merge.json", ["month", "code", "value"], [["2025-01", 85, "100"]]
        )
        result = run_script(
            "series_math.py",
            "merge",
            "--input",
            f"korea={path}:0.001",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("korea\t2025-01\t85\t0.1", result.stdout)

    def test_merge_rejects_duplicate_labels(self):
        path = self.payload("merge.json", ["month", "value"], [["2025-01", 1]])
        result = run_script(
            "series_math.py",
            "merge",
            "--input",
            f"same={path}",
            "--input",
            f"same={path}",
        )
        self.assertIn("duplicate --input label", result.stderr)

    def test_merge_parses_factor_for_extensionless_file(self):
        path = self.payload("payload", ["month", "value"], [["2025-01", "100"]])
        result = run_script("series_math.py", "merge", "--input", f"korea={path}:0.001")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("korea\t2025-01\t0.1", result.stdout)

    def test_merge_preserves_existing_colon_path_and_rejects_source_collision(self):
        colon_path = self.payload("payload:2", ["month", "value"], [["2025-01", "100"]])
        colon_result = run_script(
            "series_math.py", "merge", "--input", f"actual={colon_path}"
        )
        collision_path = self.payload(
            "collision.json",
            ["source", "month", "value"],
            [["old", "2025-01", 1]],
        )
        collision_result = run_script(
            "series_math.py", "merge", "--input", f"new={collision_path}"
        )
        self.assertEqual(colon_result.returncode, 0, colon_result.stderr)
        self.assertIn("actual\t2025-01\t100", colon_result.stdout)
        self.assertIn("already has a 'source' column", collision_result.stderr)


if __name__ == "__main__":
    unittest.main()
