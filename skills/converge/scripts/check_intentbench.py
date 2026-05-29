#!/usr/bin/env python3
"""Validate the IntentBench manifest and benchmark coverage."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parent.parent
MANIFEST_PATH = REPO_ROOT / "intentbench" / "manifest.json"
REQUIRED_MANIFEST_KEYS = (
    "protocol_version",
    "benchmark_id",
    "benchmark_version",
    "name",
    "description",
    "source_skill",
    "case_source",
    "coverage_source",
    "rubric_source",
    "result_schema",
    "required_axes",
    "scoring",
    "suites",
)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
TAG_RE = re.compile(r"^- `([^`]+)`\s*$")


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def section_after(text: str, heading: str) -> str:
    if heading not in text:
        return ""
    tail = text.split(heading, 1)[1]
    next_heading = re.search(r"\n## ", tail)
    if next_heading:
        return tail[: next_heading.start()]
    return tail


def rubric_tags(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return {
        match.group(1)
        for line in section_after(text, "## Failure Tags").splitlines()
        if (match := TAG_RE.match(line.strip()))
    }


def eval_cases(case_dir: Path) -> set[str]:
    return {path.name for path in case_dir.glob("*.md")}


def parse_coverage(path: Path) -> tuple[list[tuple[str, str, str]], list[str]]:
    if not path.is_file():
        return [], [f"missing coverage file: {path}"]
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return [], [f"{path} is empty"]
    errors: list[str] = []
    if lines[0].split("\t") != ["case", "axis", "value"]:
        errors.append("coverage header must be case<TAB>axis<TAB>value")
    rows: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for lineno, raw_line in enumerate(lines[1:], start=2):
        if not raw_line.strip() or raw_line.startswith("#"):
            continue
        parts = raw_line.split("\t")
        if len(parts) != 3:
            errors.append(f"coverage:{lineno}: expected 3 tab-separated fields")
            continue
        row = tuple(part.strip() for part in parts)
        if not all(row):
            errors.append(f"coverage:{lineno}: empty field")
            continue
        if row in seen:
            errors.append(f"coverage:{lineno}: duplicate row {row}")
            continue
        seen.add(row)
        rows.append(row)
    return rows, errors


def coverage_index(rows: list[tuple[str, str, str]]) -> dict[str, dict[str, set[str]]]:
    index: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for case_name, axis, value in rows:
        index[axis][value].add(case_name)
    return index


def selected_cases(suite: dict[str, Any], index: dict[str, dict[str, set[str]]], all_cases: set[str]) -> set[str]:
    selector = suite.get("selector", {})
    if not isinstance(selector, dict):
        return set()
    axis = selector.get("axis")
    values = selector.get("values")
    if axis == "*" and values == ["*"]:
        return set(all_cases)
    if not isinstance(axis, str) or not isinstance(values, list):
        return set()
    selected: set[str] = set()
    for value in values:
        if isinstance(value, str):
            selected.update(index.get(axis, {}).get(value, set()))
    return selected


def check_manifest(path: Path = MANIFEST_PATH) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing IntentBench manifest: {path}"]
    try:
        manifest = load_json(path)
    except Exception as exc:
        return [f"invalid IntentBench manifest: {exc}"]

    for key in REQUIRED_MANIFEST_KEYS:
        if key not in manifest:
            errors.append(f"manifest missing {key}")
    if manifest.get("protocol_version") != "1.0":
        errors.append("manifest protocol_version must be 1.0")
    version = str(manifest.get("benchmark_version", ""))
    if not SEMVER_RE.match(version):
        errors.append("manifest benchmark_version must be semantic x.y.z")

    for rel_key in ("source_skill", "case_source", "coverage_source", "rubric_source", "result_schema"):
        rel = manifest.get(rel_key)
        if not isinstance(rel, str) or not (REPO_ROOT / rel).exists():
            errors.append(f"manifest {rel_key} must point to an existing repository path")

    scoring = manifest.get("scoring", {})
    if not isinstance(scoring, dict):
        errors.append("manifest scoring must be an object")
    elif scoring.get("no_numeric_quality_score") is not True:
        errors.append("manifest scoring.no_numeric_quality_score must be true")

    required_axes = manifest.get("required_axes", [])
    if not isinstance(required_axes, list) or not required_axes:
        errors.append("manifest required_axes must be a non-empty list")
        required_axes = []

    case_dir = REPO_ROOT / str(manifest.get("case_source", ""))
    coverage_path = REPO_ROOT / str(manifest.get("coverage_source", ""))
    rubric_path = REPO_ROOT / str(manifest.get("rubric_source", ""))
    cases = eval_cases(case_dir)
    if len(cases) < 30:
        errors.append(f"IntentBench should expose at least 30 cases, found {len(cases)}")
    if not rubric_tags(rubric_path):
        errors.append("IntentBench rubric source has no parseable failure tags")

    rows, coverage_errors = parse_coverage(coverage_path)
    errors.extend(coverage_errors)
    index = coverage_index(rows)
    for axis in required_axes:
        if not isinstance(axis, str):
            errors.append("manifest required_axes entries must be strings")
            continue
        if axis not in index:
            errors.append(f"required axis has no coverage rows: {axis}")

    covered_cases = {case_name for case_name, _axis, _value in rows}
    missing_coverage = sorted(cases - covered_cases)
    if missing_coverage:
        errors.append("eval cases missing coverage rows: " + ", ".join(missing_coverage[:10]))
    unknown_coverage_cases = sorted(covered_cases - cases)
    if unknown_coverage_cases:
        errors.append("coverage references unknown cases: " + ", ".join(unknown_coverage_cases[:10]))

    suites = manifest.get("suites", [])
    if not isinstance(suites, list) or not suites:
        errors.append("manifest suites must be a non-empty list")
        suites = []
    seen_suites: set[str] = set()
    for suite in suites:
        if not isinstance(suite, dict):
            errors.append("manifest suite entries must be objects")
            continue
        suite_id = str(suite.get("suite_id", ""))
        if not suite_id:
            errors.append("manifest suite missing suite_id")
            continue
        if suite_id in seen_suites:
            errors.append(f"manifest duplicate suite_id: {suite_id}")
        seen_suites.add(suite_id)
        selected = selected_cases(suite, index, cases)
        if not selected:
            errors.append(f"manifest suite {suite_id} selects no cases")

    if "core" not in seen_suites:
        errors.append("manifest must define a core suite")
    return errors


def report(path: Path = MANIFEST_PATH) -> str:
    manifest = load_json(path)
    case_dir = REPO_ROOT / str(manifest["case_source"])
    rows, parse_errors = parse_coverage(REPO_ROOT / str(manifest["coverage_source"]))
    index = coverage_index(rows)
    cases = eval_cases(case_dir)
    lines = [
        "IntentBench manifest report",
        f"- benchmark_id: {manifest.get('benchmark_id')}",
        f"- benchmark_version: {manifest.get('benchmark_version')}",
        f"- cases: {len(cases)}",
        f"- coverage rows: {len(rows)}",
        f"- parse errors: {len(parse_errors)}",
        f"- suites: {len(manifest.get('suites', []))}",
    ]
    for suite in manifest.get("suites", []):
        if isinstance(suite, dict):
            lines.append(f"- suite {suite.get('suite_id')}: {len(selected_cases(suite, index, cases))} cases")
    return "\n".join(lines)


def run_self_test(path: Path = MANIFEST_PATH) -> list[str]:
    errors: list[str] = []
    manifest = load_json(path)
    with tempfile.TemporaryDirectory(prefix="intentbench-selftest-") as tmp:
        valid_path = Path(tmp) / "manifest.json"
        valid_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        valid_errors = check_manifest(valid_path)
        if valid_errors:
            errors.append("self-test valid manifest unexpectedly failed: " + "; ".join(valid_errors[:3]))

        invalid_manifest = dict(manifest)
        invalid_manifest["scoring"] = dict(manifest.get("scoring", {}))
        invalid_manifest["scoring"]["no_numeric_quality_score"] = False
        invalid_path = Path(tmp) / "invalid.json"
        invalid_path.write_text(json.dumps(invalid_manifest, indent=2) + "\n", encoding="utf-8")
        invalid_errors = check_manifest(invalid_path)
        if not any("no_numeric_quality_score" in error for error in invalid_errors):
            errors.append("self-test invalid scoring manifest was not rejected")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test(args.manifest)
        print("IntentBench validator self-test")
        if errors:
            print("Self-test failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Self-test passed.")
        return 0

    errors = check_manifest(args.manifest)
    print(report(args.manifest))
    if errors:
        print("IntentBench validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("IntentBench validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
