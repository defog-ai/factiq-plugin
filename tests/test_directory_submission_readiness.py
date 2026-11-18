import json
import struct
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


RELEASE_EXCLUDE = ROOT / ".github" / "release-exclude.txt"


def release_exclude_paths():
    lines = RELEASE_EXCLUDE.read_text(encoding="utf-8").splitlines()
    return [
        line.strip().rstrip("/")
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def release_files():
    """Tracked files that the release workflow copies to the release branch."""
    output = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8")
    excluded = release_exclude_paths()
    return sorted(
        name
        for name in output.split("\0")
        if name
        and not any(name == p or name.startswith(p + "/") for p in excluded)
    )


class DirectorySubmissionReadinessTests(unittest.TestCase):
    def test_readme_names_all_supported_clients_and_canonical_guides(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for expected in (
            "Claude (web, desktop, and Cowork)",
            "ChatGPT (web and desktop)",
            "https://claude.ai/directory/factiq",
            "https://www.factiq.com/claude",
            "https://www.factiq.com/chatgpt",
            "https://www.factiq.com/claude-code",
            "https://www.factiq.com/codex",
        ):
            self.assertIn(expected, readme)

    def test_manifests_have_complete_factiq_publisher_metadata(self):
        plugin = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        codex = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )

        expected_publisher = {
            "name": "FactIQ",
            "url": "https://www.factiq.com",
        }
        self.assertEqual(plugin["author"], expected_publisher)
        self.assertEqual(codex["author"], expected_publisher)
        self.assertEqual(codex["interface"]["developerName"], "FactIQ")
        self.assertEqual(
            codex["interface"]["websiteURL"], "https://www.factiq.com"
        )
        self.assertEqual(
            codex["interface"]["privacyPolicyURL"],
            "https://www.factiq.com/privacy",
        )
        self.assertEqual(
            codex["interface"]["termsOfServiceURL"],
            "https://www.factiq.com/legal",
        )
        self.assertEqual(
            plugin["repository"], "https://github.com/defog-ai/factiq-plugin"
        )
        self.assertEqual(plugin["license"], "MIT")
        self.assertEqual(plugin["privacyPolicyUrl"], "https://www.factiq.com/privacy")
        self.assertEqual(plugin["icon"], "./assets/factiq-logo.png")
        self.assertTrue((ROOT / plugin["icon"]).is_file())
        self.assertTrue(plugin["keywords"])
        self.assertTrue(marketplace["description"])
        self.assertEqual(marketplace["owner"], expected_publisher)

    def test_marketplace_entry_repeats_the_plugin_description(self):
        plugin = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        (entry,) = marketplace["plugins"]
        self.assertEqual(entry["description"], plugin["description"])

    def test_release_files_meet_the_directory_file_policy(self):
        # The Claude plugin directory reads the `release` branch, which holds
        # main without the paths in .github/release-exclude.txt. From an
        # organization that is not Verified, the directory refuses any file
        # that is not Markdown, text, JSON, YAML or a PNG, JPEG, GIF, WebP or
        # ICO image, any file that starts with #!, and package manager
        # configuration. It holds a version for review when a file is over
        # 256 KiB or the plugin has more than 512 files.
        allowed_suffixes = {
            ".md", ".txt", ".json", ".yaml", ".yml",
            ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
        }
        allowed_names = {"LICENSE", ".gitignore"}
        image_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
        package_manager_files = {
            "package.json", "package-lock.json", "pnpm-workspace.yaml",
            "pnpm-lock.yaml", "yarn.lock", ".npmrc", ".yarnrc.yml",
            "pyproject.toml", "requirements.txt", "uv.lock", "Pipfile",
        }

        files = release_files()
        self.assertTrue(files)
        self.assertLessEqual(len(files), 512)
        for name in files:
            path = ROOT / name
            self.assertFalse(path.is_symlink(), name)
            self.assertNotEqual(path.name, ".DS_Store", name)
            self.assertNotIn(path.name, package_manager_files, name)
            suffix = path.suffix.lower()
            self.assertTrue(
                suffix in allowed_suffixes or path.name in allowed_names,
                f"{name} is not a file type the directory accepts",
            )
            data = path.read_bytes()
            self.assertFalse(data.startswith(b"#!"), f"{name} starts with #!")
            if suffix in image_suffixes:
                continue
            self.assertLessEqual(len(data), 256 * 1024, name)
            self.assertNotIn(b"\x00", data, f"{name} holds a NUL byte")
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                self.fail(f"{name} is not UTF-8 text")

    def test_release_exclude_list_keeps_tests_and_ci_off_the_release_branch(self):
        excluded = release_exclude_paths()
        self.assertIn("tests", excluded)
        self.assertIn(".github", excluded)
        for name in release_files():
            self.assertFalse(name.endswith(".py"), name)

    def test_claude_and_codex_versions_stay_in_sync(self):
        claude = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        codex = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(claude["version"], codex["version"])

    def test_codex_listing_copy_and_assets_fit_directory_constraints(self):
        manifest = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        interface = manifest["interface"]

        expected_long_description = (
            "FactIQ gives ChatGPT and Codex primarily read-only access to sourced "
            "investment and economic data through one normalized warehouse. "
            "Research official statistics across the US, UK, EU, China, India, "
            "Singapore, and international institutions; inspect company filings "
            "and earnings-call intelligence; query market movements, business news, "
            "executive media appearances, trade, and satellite-derived signals "
            "such as rainfall, fires, air quality, nighttime lights, shipping, and "
            "reservoir levels. FactIQ can discover datasets, run read-only SQL, "
            "calculate comparisons, return sourced analysis, and create inline "
            "charts. A FactIQ account is required to connect. FactIQ records "
            "connector tool inputs and outputs for reliability and support as "
            "described in the privacy policy. `send_feedback` is the only write "
            "tool and sends a short issue report to the FactIQ team; it does not "
            "modify research data."
        )
        expected_prompts = [
            "Compare US inflation and unemployment since 2020 and explain the "
            "turning points.",
            "What did Microsoft say about AI spending in its latest earnings call, "
            "and how does that compare with filed results?",
            "Compare Punjab rainfall and fire activity during the 2024 and 2025 "
            "monsoon seasons.",
        ]

        self.assertEqual(
            interface["shortDescription"], "Investment and economic data"
        )
        self.assertEqual(interface["longDescription"], expected_long_description)
        self.assertEqual(interface["defaultPrompt"], expected_prompts)
        self.assertLessEqual(len(interface["shortDescription"]), 30)
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        for prompt in interface["defaultPrompt"]:
            self.assertLessEqual(len(prompt), 128)

        for field in ("composerIcon", "logo"):
            relative_path = interface[field]
            self.assertTrue(relative_path.startswith("./assets/"))
            asset = ROOT / relative_path.removeprefix("./")
            self.assertTrue(asset.is_file())
            self.assertLessEqual(asset.stat().st_size, 5 * 1024 * 1024)
            png = asset.read_bytes()
            self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
            width, height = struct.unpack(">II", png[16:24])
            self.assertEqual(width, height)
            self.assertGreaterEqual(width, 48)
            self.assertLessEqual(width, 4096)

    def test_skill_uses_current_market_contract_without_broad_permissions(self):
        skill = (ROOT / "skills" / "factiq" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("allowed-tools:", skill)
        self.assertIn(
            "`get_market_data` (`asset`, `data_type?`, `frequency?`, `limit?`)",
            skill,
        )
        for legacy_parameter in ("`function`", "`outputsize?`"):
            self.assertNotIn(legacy_parameter, skill)

    def test_setup_covers_terminal_and_terminal_free_auth(self):
        setup = (ROOT / "SETUP.md").read_text(encoding="utf-8")
        for expected in (
            "Claude Code",
            "/mcp",
            "Cowork has no terminal",
            "Customize → Plugins",
            "get_data_catalog",
            "Do not ask",
        ):
            self.assertIn(expected, setup)

    def test_skill_tells_claude_app_users_how_to_connect(self):
        # Adding the plugin in a Claude app does not connect its MCP server, and
        # those apps have no /mcp, so the skill must name the in-app path. The
        # description is the only skill text that is always in context.
        skill = (ROOT / "skills" / "factiq" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        frontmatter = skill.split("---", 2)[1]
        self.assertIn("ask the user to connect FactIQ", frontmatter)
        self.assertIn("Customize → Plugins → FactIQ → Connect", frontmatter)
        # The skill must not stop the host from using its other tools.
        self.assertNotIn("instead of answering", " ".join(frontmatter.split()))
        self.assertIn("A web answer is allowed", " ".join(frontmatter.split()))
        self.assertIn("**Claude web, desktop, and Cowork**", skill)
        self.assertEqual(skill.count("Customize → Plugins → FactIQ"), 3)

    def test_skill_description_fits_the_length_limit(self):
        # Claude rejects a skill description longer than 1024 characters.
        skill = (ROOT / "skills" / "factiq" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        frontmatter = skill.split("---", 2)[1]
        folded = frontmatter.split("description: >", 1)[1]
        self.assertLessEqual(len(" ".join(folded.split())), 1024)


if __name__ == "__main__":
    unittest.main()
