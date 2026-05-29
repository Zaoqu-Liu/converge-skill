#!/usr/bin/env python3
"""Summarize filled IntentBench runpack results."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parent.parent


@dataclass(frozen=True)
class BenchCase:
    case_name: str
    coverage: dict[str, list[str]]


@dataclass(frozen=True)
class BenchStatus:
    case_name: str
    verdict: str
    result_file: Path | None
    errors: tuple[str, ...]

    @property
    def valid_reviewed(self) -> bool:
        return self.result_file is not None and self.verdict in {"Pass", "Fail"} and not self.errors


def load_checker(root: Path) -> ModuleType:
    checker_path = root / "scripts" / "check_converge_response_eval.py"
    spec = importlib.util.spec_from_file_location("converge_response_eval_checker", checker_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {checker_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def runpack_manifest(results_dir: Path) -> Path | None:
    candidates = [
        results_dir.parent / "manifest.json",
        results_dir / "manifest.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def bench_cases(results_dir: Path, root: Path) -> tuple[str, list[BenchCase]]:
    manifest_path = runpack_manifest(results_dir)
    if manifest_path is None:
        checker = load_checker(root)
        return "all eval cases", [
            BenchCase(case_name=case_name, coverage={})
            for case_name in sorted(checker.eval_case_names(root))
        ]

    manifest = load_json(manifest_path)
    cases: list[BenchCase] = []
    for item in manifest.get("cases", []):
        if not isinstance(item, dict):
            continue
        case_name = str(item.get("case", ""))
        raw_coverage = item.get("coverage", {})
        coverage: dict[str, list[str]] = {}
        if isinstance(raw_coverage, dict):
            for axis, values in raw_coverage.items():
                if isinstance(axis, str) and isinstance(values, list):
                    coverage[axis] = [str(value) for value in values if isinstance(value, str)]
        if case_name:
            cases.append(BenchCase(case_name=case_name, coverage=coverage))
    label = f"{manifest.get('benchmark_id', 'intentbench')} {manifest.get('benchmark_version', '')}".strip()
    return label, cases


def compute_statuses(results_dir: Path, root: Path, require_real_results: bool) -> tuple[str, list[BenchCase], list[BenchStatus], list[Path]]:
    checker = load_checker(root)
    label, cases = bench_cases(results_dir, root)
    files = checker.result_files(results_dir) if results_dir.is_dir() else []
    by_case: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        try:
            record = checker.result_record(path)
        except Exception:
            continue
        by_case[record.case_name].append(path)

    statuses: list[BenchStatus] = []
    for bench_case in cases:
        paths = by_case.get(bench_case.case_name, [])
        if not paths:
            statuses.append(BenchStatus(bench_case.case_name, "", None, ("missing result file",)))
            continue
        path = paths[0]
        data = checker.metadata(path.read_text(encoding="utf-8"))
        errors = list(checker.check_result(path, root, require_real_results=require_real_results))
        if len(paths) > 1:
            errors.append("duplicate result files for case")
        statuses.append(
            BenchStatus(
                case_name=bench_case.case_name,
                verdict=data.get("verdict", ""),
                result_file=path,
                errors=tuple(errors),
            )
        )
    return label, cases, statuses, files


def format_list(items: list[str], limit: int) -> str:
    if not items:
        return "none"
    shown = items[:limit]
    suffix = "" if len(items) <= limit else f" ... +{len(items) - limit} more"
    return ", ".join(shown) + suffix


def scorecard(results_dir: Path, root: Path, require_real_results: bool, show_axes: bool, limit: int) -> str:
    label, cases, statuses, files = compute_statuses(results_dir, root, require_real_results)
    valid = [status for status in statuses if status.valid_reviewed]
    passes = [status for status in valid if status.verdict == "Pass"]
    fails = [status for status in valid if status.verdict == "Fail"]
    missing = [status.case_name for status in statuses if status.result_file is None]
    invalid = [status.case_name for status in statuses if status.result_file is not None and status.errors]
    full_pass = bool(cases) and len(passes) == len(cases) and not fails and not missing and not invalid and require_real_results

    lines = [
        "IntentBench scorecard",
        f"- runpack: {label}",
        f"- expected cases: {len(cases)}",
        f"- result files: {len(files)}",
        f"- valid reviewed: {len(valid)}",
        f"- valid pass: {len(passes)}",
        f"- valid fail: {len(fails)}",
        f"- missing cases: {len(missing)}",
        f"- invalid cases: {len(invalid)}",
        f"- require_real_results: {require_real_results}",
        f"- full pass candidate: {'yes' if full_pass else 'no'}",
        "- next missing cases: " + format_list(missing, limit),
        "- next invalid cases: " + format_list(invalid, limit),
    ]
    if show_axes:
        passed_names = {status.case_name for status in passes}
        totals: dict[str, Counter[str]] = defaultdict(Counter)
        passed: dict[str, Counter[str]] = defaultdict(Counter)
        for bench_case in cases:
            for axis, values in bench_case.coverage.items():
                for value in values:
                    totals[axis][value] += 1
                    if bench_case.case_name in passed_names:
                        passed[axis][value] += 1
        lines.append("- axis pass coverage:")
        if not totals:
            lines.append("  - none")
        for axis in sorted(totals):
            lines.append(f"  - {axis}:")
            for value, total in sorted(totals[axis].items()):
                lines.append(f"    - {value}: {passed[axis][value]}/{total}")
    return "\n".join(lines)


def run_self_test(root: Path = SKILL_ROOT) -> list[str]:
    checker = load_checker(root)
    case_name = sorted(checker.eval_case_names(root))[0]
    with tempfile.TemporaryDirectory(prefix="intentbench-summary-") as tmp:
        runpack = Path(tmp)
        results = runpack / "results"
        results.mkdir(parents=True)
        (runpack / "manifest.json").write_text(
            json.dumps(
                {
                    "benchmark_id": "intentbench-selftest",
                    "benchmark_version": "0.0.0",
                    "cases": [
                        {
                            "case": case_name,
                            "coverage": {"risk_surface": ["ambiguous-intent"]},
                        }
                    ],
                    "scoring": {"unit": "case_pass_fail"},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (results / f"{Path(case_name).stem}.result.md").write_text(
            checker.sample_result(
                case_name,
                evaluator="manual-review",
                model_host="codex-real-host",
                response=(
                    "The response reconstructs intent, gives an owner recommendation, "
                    "handles evidence boundaries, names a risk, and provides a usable next action."
                ),
                evidence="Concrete behavior is cited in the captured response.",
            ),
            encoding="utf-8",
        )
        report = scorecard(results, root, require_real_results=True, show_axes=True, limit=5)
        if "expected cases: 1" not in report or "full pass candidate: yes" not in report:
            return ["self-test scorecard did not recognize the one-case runpack"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", type=Path, nargs="?")
    parser.add_argument("--root", type=Path, default=SKILL_ROOT)
    parser.add_argument("--require-real-results", action="store_true")
    parser.add_argument("--show-axes", action="store_true")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test(args.root)
        print("IntentBench summary self-test")
        if errors:
            print("Self-test failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Self-test passed.")
        return 0

    if args.results_dir is None:
        parser.error("results_dir is required unless --self-test is used")
    print(scorecard(args.results_dir, args.root, args.require_real_results, args.show_axes, args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
