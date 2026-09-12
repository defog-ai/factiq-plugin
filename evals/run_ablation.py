#!/usr/bin/env python3
"""Run the behaviour suite twice and compare: the full plugin against a
baseline that keeps the same mocked FactIQ tools but has no skill and no
scripts.

Why not `claude plugin eval --ablation with-without`? That mode removes the
whole plugin from the second arm, including its MCP server. The second arm
then has no FactIQ tools at all, so the comparison is "plugin with data"
against "no data", and every data case fails without the plugin for a
reason that has nothing to do with the skill. This script builds a stripped
copy of the plugin (manifest plus MCP configuration, no `skills/`, no
`scripts/`) and runs both plugins under `--ablation none` with the same
mocks, the same model, the same judge, and the same tool grants. The
difference between the two scores is then what the skill and the bundled
scripts add on top of the tools.

Usage (from the plugin root):

    python3 evals/run_ablation.py --model opus --judge-model sonnet
    python3 evals/run_ablation.py --model opus --case 'yoy-*' --runs 1
    python3 evals/run_ablation.py --model opus --tag filings --tag charts
    python3 evals/run_ablation.py --model opus --skip-baseline

Results land in `evals/results/<timestamp>/{with,baseline}/` with a
`comparison.md` beside them. The exit code is 1 when any with-arm case
scores below `--threshold` (default 0.8; one disagreeing judge vote in a
three-run case is a score of about 0.9, so 1.0 fails on judge noise).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = PLUGIN_ROOT / "evals"


def build_baseline_plugin(dest: Path) -> None:
    """Copy the manifest, the MCP configuration and the eval suite, and
    nothing else. The baseline plugin keeps the plugin's name so the tool
    names inside the sandbox (`mcp__plugin_factiq_factiq__<tool>`) are the
    same in both arms and every `tool_used` grader compares like with like."""
    manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    manifest.pop("skills", None)
    manifest.pop("hooks", None)
    manifest.pop("commands", None)
    manifest.pop("agents", None)
    manifest["description"] = "Baseline for the FactIQ behaviour suite: MCP tools only, no skill."
    (dest / ".claude-plugin").mkdir(parents=True)
    (dest / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")
    shutil.copy(PLUGIN_ROOT / ".mcp.json", dest / ".mcp.json")
    shutil.copytree(
        EVAL_DIR,
        dest / "evals",
        ignore=shutil.ignore_patterns("results", "__pycache__", "*.py"),
    )


def run_eval(plugin_dir: Path, out_dir: Path, args: argparse.Namespace, label: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "aggregate-result.json"
    cmd = [
        "claude", "plugin", "eval", str(plugin_dir),
        "--ablation", "none",
        "--trust-plugin",
        "--no-publish",
        "--threshold", "0",
        "--model", args.model,
        "--judge-model", args.judge_model,
        "--json", str(json_path),
        "--output-dir", str(out_dir),
        "--concurrency", str(args.concurrency),
    ]
    if args.allow_tools:
        cmd += ["--allow-tools", *args.allow_tools.split(",")]
    if args.runs:
        cmd += ["--runs", str(args.runs)]
    if args.case:
        cmd += ["--case", args.case]
    for tag in args.tag:
        cmd += ["--tag", tag]
    if args.max_cost_usd:
        cmd += ["--max-cost-usd", str(args.max_cost_usd)]
    if args.keep_temp:
        cmd.append("--keep-temp")
    print(f"\n=== {label}: {' '.join(cmd)}\n", flush=True)
    proc = subprocess.run(cmd, cwd=plugin_dir)
    if not json_path.exists():
        sys.exit(f"{label}: no result file was written (exit {proc.returncode})")
    return json.loads(json_path.read_text())


def case_table(result: dict) -> dict[str, dict]:
    table: dict[str, dict] = {}
    for case in result["cases"]:
        runs = case["arms"]["with"]
        scores = [r["score"] for r in runs]
        graders: dict[str, list[bool]] = {}
        for run in runs:
            for g in run.get("graders", []):
                graders.setdefault(g["name"], []).append(bool(g.get("passed")))
        table[case["name"]] = {
            "score": sum(scores) / len(scores) if scores else 0.0,
            "runs": len(runs),
            "errors": sum(1 for r in runs if r.get("error") or r.get("aborted")),
            "cost": sum(r.get("costUsd", 0) + r.get("judgeCostUsd", 0) for r in runs),
            "graders": {k: sum(v) / len(v) for k, v in graders.items()},
        }
    return table


def fmt(x: float | None) -> str:
    return "  -  " if x is None else f"{x:.2f}"


def comparison(with_res: dict, base_res: dict | None, args: argparse.Namespace) -> str:
    w = case_table(with_res)
    b = case_table(base_res) if base_res else {}
    lines = [
        "# Plugin against baseline",
        "",
        f"Model `{args.model}`, judge `{args.judge_model}`, Claude Code "
        f"{with_res.get('claudeVersion', '?')}, {with_res.get('startedAt', '')[:10]}.",
        "",
        "The baseline arm has the same mocked FactIQ tools and no skill and no scripts.",
        "",
        "| Case | With plugin | Baseline | Delta | Runs | Aborted or errored |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in sorted(w):
        ws = w[name]["score"]
        bs = b[name]["score"] if name in b else None
        delta = None if bs is None else ws - bs
        err = f"{w[name]['errors']}" + (f" / {b[name]['errors']}" if name in b else "")
        lines.append(f"| `{name}` | {fmt(ws)} | {fmt(bs)} | {fmt(delta)} | {w[name]['runs']} | {err} |")
    wcost = with_res.get("costUsd", 0.0)
    bcost = base_res.get("costUsd", 0.0) if base_res else 0.0
    lines += ["", f"Cost: with plugin ${wcost:.2f}" + (f", baseline ${bcost:.2f}" if base_res else "") + ".", ""]
    lines += ["## Graders (fraction of runs passed)", ""]
    for name in sorted(w):
        lines += [f"### `{name}`", "", "| Grader | With plugin | Baseline |", "| --- | ---: | ---: |"]
        for g in sorted(w[name]["graders"]):
            bg = b[name]["graders"].get(g) if name in b else None
            lines.append(f"| `{g}` | {fmt(w[name]['graders'][g])} | {fmt(bg)} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", required=True, help="model for the agent under test, for example opus or claude-opus-5")
    p.add_argument("--judge-model", default="sonnet")
    p.add_argument("--runs", type=int, default=None, help="runs per case; default is each case's own setting")
    p.add_argument("--case", default=None, help="case name glob, for example 'yoy-*' (one value; use --tag to pick several unrelated cases)")
    p.add_argument("--tag", action="append", default=[], help="case tag; repeatable")
    p.add_argument("--allow-tools", default="Write,Edit,Bash", help="comma-separated operator grant")
    p.add_argument("--concurrency", "-j", type=int, default=2)
    p.add_argument("--threshold", type=float, default=0.8, help="exit 1 if a with-arm case scores below this")
    p.add_argument("--max-cost-usd", type=float, default=None, help="per-arm cost ceiling passed through")
    p.add_argument("--skip-baseline", action="store_true", help="run only the plugin arm")
    p.add_argument("--keep-temp", action="store_true", help="keep each run's sandbox for inspection")
    p.add_argument("--output-dir", default=None, help="default: evals/results/<timestamp>")
    args = p.parse_args()

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    # Absolute: the baseline arm runs inside a temporary plugin directory that
    # is deleted afterwards, so a relative path would be lost with it.
    out_root = (Path(args.output_dir) if args.output_dir else EVAL_DIR / "results" / stamp).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    with_res = run_eval(PLUGIN_ROOT, out_root / "with", args, "with plugin")

    base_res = None
    if not args.skip_baseline:
        tmp = Path(tempfile.mkdtemp(prefix="factiq-baseline-"))
        try:
            build_baseline_plugin(tmp)
            base_res = run_eval(tmp, out_root / "baseline", args, "baseline (tools only)")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    report = comparison(with_res, base_res, args)
    (out_root / "comparison.md").write_text(report + "\n")
    print("\n" + report)
    print(f"\nWritten to {out_root}")

    below = [n for n, c in case_table(with_res).items() if c["score"] < args.threshold]
    if below:
        print(f"\nBelow threshold {args.threshold}: {', '.join(sorted(below))}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
