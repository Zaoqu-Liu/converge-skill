#!/usr/bin/env python3
"""Validate Converge eval coverage across modes, risks, hosts, and evidence surfaces."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_FILE = "eval-coverage.tsv"
CORE_AXES = ("output_profile", "trigger_surface", "context_surface", "risk_surface")

KNOWN_VALUES = {
    "output_profile": {
        "Universal Intent Guard",
        "Thinking Reply",
        "Direct Answer",
        "Conversation Reply",
        "Expression Draft",
        "Action Plan",
        "Technology Route",
        "Skill Evolution",
        "Decision Brief",
        "Converge Docs",
        "Dev Handoff",
    },
    "trigger_surface": {"explicit", "soft", "no-trigger"},
    "context_surface": {
        "plain-text",
        "local-file",
        "mixed-artifacts",
        "inaccessible-artifact",
        "instruction-bearing-artifact",
        "current-external-info",
    },
    "evidence_surface": {
        "none-needed",
        "local-inspection",
        "current-research",
        "source-citation",
        "command-validation",
        "response-eval",
        "high-risk-review",
        "handoff-validation",
    },
    "risk_surface": {
        "ambiguous-intent",
        "simple-task",
        "current-tech",
        "high-stakes",
        "context-trust",
        "skill-evolution",
        "reply-quality",
        "completion-proof",
        "memory-boundary",
        "research-quality",
    },
    "host_surface": {
        "generic",
        "codex-default",
        "codex-plan",
        "claude-code",
        "cursor",
        "opencode",
        "cline",
        "antigravity",
        "gemini-cli",
        "github-copilot",
        "windsurf",
        "continue",
        "roo-code",
        "aider",
    },
}

REQUIRED_VALUES = {
    "output_profile": KNOWN_VALUES["output_profile"],
    "trigger_surface": KNOWN_VALUES["trigger_surface"],
    "context_surface": KNOWN_VALUES["context_surface"],
    "evidence_surface": KNOWN_VALUES["evidence_surface"],
    "risk_surface": KNOWN_VALUES["risk_surface"],
    "host_surface": KNOWN_VALUES["host_surface"],
}


def eval_cases(root: Path) -> set[str]:
    return {path.name for path in (root / "eval-cases").glob("*.md")}


def parse_rows(root: Path) -> tuple[list[tuple[str, str, str]], list[str]]:
    path = root / COVERAGE_FILE
    if not path.is_file():
        return [], [f"missing {COVERAGE_FILE}"]

    rows: list[tuple[str, str, str]] = []
    errors: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return rows, [f"{COVERAGE_FILE} is empty"]
    if lines[0].split("\t") != ["case", "axis", "value"]:
        errors.append(f"{COVERAGE_FILE}: header must be case<TAB>axis<TAB>value")

    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            errors.append(f"{COVERAGE_FILE}:{lineno}: expected 3 tab-separated fields")
            continue
        case_name, axis, value = parts
        row = (case_name.strip(), axis.strip(), value.strip())
        if not all(row):
            errors.append(f"{COVERAGE_FILE}:{lineno}: empty field")
            continue
        if row in seen:
            errors.append(f"{COVERAGE_FILE}:{lineno}: duplicate row {row}")
            continue
        seen.add(row)
        rows.append(row)
    return rows, errors


def coverage_index(rows: list[tuple[str, str, str]]) -> dict[str, dict[str, set[str]]]:
    index: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for case_name, axis, value in rows:
        index[axis][value].add(case_name)
    return index


def run_checks(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    cases = eval_cases(root)
    if not cases:
        return ["no eval cases found"]

    rows, parse_errors = parse_rows(root)
    errors.extend(parse_errors)
    case_axes: dict[str, set[str]] = defaultdict(set)
    rows_by_case: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for case_name, axis, value in rows:
        if case_name not in cases:
            errors.append(f"{COVERAGE_FILE}: unknown eval case {case_name}")
        if axis not in KNOWN_VALUES:
            errors.append(f"{COVERAGE_FILE}: unknown axis {axis}")
        elif value not in KNOWN_VALUES[axis]:
            errors.append(f"{COVERAGE_FILE}: unknown {axis} value {value}")
        case_axes[case_name].add(axis)
        rows_by_case[case_name].append((axis, value))

    for case_name in sorted(cases):
        if case_name not in rows_by_case:
            errors.append(f"{case_name}: missing all coverage rows")
            continue
        for axis in CORE_AXES:
            if axis not in case_axes[case_name]:
                errors.append(f"{case_name}: missing core coverage axis {axis}")

    index = coverage_index(rows)
    for axis, required_values in REQUIRED_VALUES.items():
        for value in sorted(required_values):
            if not index.get(axis, {}).get(value):
                errors.append(f"{axis} value {value} has no eval-case coverage")
    return errors


def coverage_report(root: Path = ROOT, show_counts: bool = False) -> str:
    cases = eval_cases(root)
    rows, parse_errors = parse_rows(root)
    index = coverage_index(rows)
    lines = [
        "Converge coverage matrix report",
        f"- cases: {len(cases)}",
        f"- rows: {len(rows)}",
        f"- parse errors: {len(parse_errors)}",
    ]
    for axis in sorted(KNOWN_VALUES):
        covered = len(index.get(axis, {}))
        required = len(REQUIRED_VALUES.get(axis, set()))
        lines.append(f"- {axis}: {covered}/{required} required values covered")
        if show_counts:
            for value in sorted(KNOWN_VALUES[axis]):
                count = len(index.get(axis, {}).get(value, set()))
                lines.append(f"  - {value}: {count}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--show-counts", action="store_true")
    args = parser.parse_args()

    errors = run_checks(args.root)
    print(coverage_report(args.root, show_counts=args.show_counts))
    if errors:
        print("Converge coverage matrix validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Converge coverage matrix validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
