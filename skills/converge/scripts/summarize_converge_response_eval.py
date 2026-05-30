#!/usr/bin/env python3
"""Summarize Converge response-eval progress, validity, failures, and coverage."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from collections import Counter, defaultdict
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_FILE = "eval-coverage.tsv"
AXES = (
    "output_profile",
    "trigger_surface",
    "context_surface",
    "evidence_surface",
    "risk_surface",
    "host_surface",
)


@dataclass(frozen=True)
class CaseStatus:
    case_name: str
    result_file: Path | None
    verdict: str
    errors: tuple[str, ...]
    tags: tuple[str, ...]
    gate_statuses: tuple[str, ...]

    @property
    def reviewed(self) -> bool:
        return self.result_file is not None and self.verdict in {"Pass", "Fail"} and not self.errors


@dataclass(frozen=True)
class EvalSummary:
    expected_cases: int
    result_files: int
    valid_reviewed: int
    valid_pass: int
    valid_fail: int
    invalid_or_unreviewed: int
    missing_cases: tuple[str, ...]
    todo_cases: tuple[str, ...]
    duplicate_cases: tuple[str, ...]
    invalid_cases: tuple[str, ...]
    failure_tags: Counter[str]
    gate_statuses: Counter[str]
    reviewed_cases: tuple[str, ...]
    pass_cases: tuple[str, ...]
    coverage: dict[str, tuple[int, int, dict[str, int]]]
    require_real_results: bool


def load_checker(root: Path) -> ModuleType:
    checker_path = root / "scripts" / "check_converge_response_eval.py"
    spec = importlib.util.spec_from_file_location("converge_response_eval_checker", checker_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {checker_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def coverage_rows(root: Path) -> dict[str, dict[str, set[str]]]:
    index: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    path = root / COVERAGE_FILE
    if not path.is_file():
        return index
    for raw_line in path.read_text(encoding="utf-8").splitlines()[1:]:
        if not raw_line.strip() or raw_line.startswith("#"):
            continue
        parts = raw_line.split("\t")
        if len(parts) != 3:
            continue
        case_name, axis, value = (part.strip() for part in parts)
        index[axis][value].add(case_name)
    return index


def expected_values(root: Path) -> dict[str, set[str]]:
    index = coverage_rows(root)
    return {axis: set(index.get(axis, {})) for axis in AXES}


def normalize_result_dirs(results_dirs: Path | Sequence[Path]) -> tuple[Path, ...]:
    if isinstance(results_dirs, Path):
        return (results_dirs,)
    return tuple(results_dirs)


def compute_statuses(
    results_dirs: Path | Sequence[Path],
    root: Path,
    require_real_results: bool,
) -> tuple[list[CaseStatus], list[Path]]:
    checker = load_checker(root)
    expected = sorted(checker.eval_case_names(root))
    files: list[Path] = []
    for results_dir in normalize_result_dirs(results_dirs):
        if results_dir.is_dir():
            files.extend(checker.result_files(results_dir))
    files = sorted(files)
    by_case: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        record = checker.result_record(path)
        by_case[record.case_name].append(path)

    statuses: list[CaseStatus] = []
    for case_name in expected:
        paths = by_case.get(case_name, [])
        if not paths:
            statuses.append(
                CaseStatus(case_name, None, "", ("missing result file",), tuple(), tuple())
            )
            continue
        path = paths[0]
        text = path.read_text(encoding="utf-8")
        data = checker.metadata(text)
        tags, _malformed, _explicit_none = checker.failure_tags(text)
        gates = tuple(row.status for row in checker.gate_rows(text) if row.status)
        errors = list(checker.check_result(path, root, require_real_results=require_real_results))
        if len(paths) > 1:
            errors.append("duplicate result files for case")
        statuses.append(
            CaseStatus(
                case_name=case_name,
                result_file=path,
                verdict=data.get("verdict", ""),
                errors=tuple(errors),
                tags=tuple(tags),
                gate_statuses=gates,
            )
        )
    return statuses, files


def compute_summary(
    results_dirs: Path | Sequence[Path],
    root: Path = ROOT,
    require_real_results: bool = False,
) -> EvalSummary:
    statuses, files = compute_statuses(results_dirs, root, require_real_results)
    coverage_index = coverage_rows(root)
    expected = expected_values(root)

    reviewed = [status for status in statuses if status.reviewed]
    pass_cases = [status.case_name for status in reviewed if status.verdict == "Pass"]
    fail_cases = [status.case_name for status in reviewed if status.verdict == "Fail"]
    missing = tuple(status.case_name for status in statuses if status.result_file is None)
    todo = tuple(
        status.case_name
        for status in statuses
        if status.result_file is not None and status.verdict not in {"Pass", "Fail"}
    )
    duplicates = tuple(
        status.case_name for status in statuses if any("duplicate" in error for error in status.errors)
    )
    invalid = tuple(status.case_name for status in statuses if status.result_file is not None and status.errors)
    failure_tags = Counter(tag for status in reviewed for tag in status.tags)
    gate_statuses = Counter(gate for status in statuses for gate in status.gate_statuses)

    coverage: dict[str, tuple[int, int, dict[str, int]]] = {}
    reviewed_names = {status.case_name for status in reviewed}
    for axis in AXES:
        counts = {
            value: len(cases & reviewed_names)
            for value, cases in coverage_index.get(axis, {}).items()
        }
        covered = sum(1 for count in counts.values() if count > 0)
        coverage[axis] = (covered, len(expected.get(axis, set())), counts)

    return EvalSummary(
        expected_cases=len(statuses),
        result_files=len(files),
        valid_reviewed=len(reviewed),
        valid_pass=len(pass_cases),
        valid_fail=len(fail_cases),
        invalid_or_unreviewed=len(statuses) - len(reviewed),
        missing_cases=missing,
        todo_cases=todo,
        duplicate_cases=duplicates,
        invalid_cases=invalid,
        failure_tags=failure_tags,
        gate_statuses=gate_statuses,
        reviewed_cases=tuple(status.case_name for status in reviewed),
        pass_cases=tuple(pass_cases),
        coverage=coverage,
        require_real_results=require_real_results,
    )


def format_list(items: tuple[str, ...], limit: int) -> str:
    if not items:
        return "none"
    shown = list(items[:limit])
    suffix = "" if len(items) <= limit else f" ... +{len(items) - limit} more"
    return ", ".join(shown) + suffix


def progress_report(summary: EvalSummary, show_axes: bool, show_cases: bool, limit: int) -> str:
    full_pass_candidate = (
        summary.expected_cases > 0
        and summary.valid_pass == summary.expected_cases
        and summary.invalid_or_unreviewed == 0
        and summary.valid_fail == 0
        and summary.require_real_results
    )
    lines = [
        "Converge response-eval progress report",
        f"- expected cases: {summary.expected_cases}",
        f"- result files: {summary.result_files}",
        f"- valid reviewed: {summary.valid_reviewed}",
        f"- valid pass: {summary.valid_pass}",
        f"- valid fail: {summary.valid_fail}",
        f"- invalid or unreviewed: {summary.invalid_or_unreviewed}",
        f"- require_real_results: {summary.require_real_results}",
        f"- full pass candidate: {'yes' if full_pass_candidate else 'no'}",
        f"- missing cases: {len(summary.missing_cases)}",
        f"- TODO/invalid verdict cases: {len(summary.todo_cases)}",
        f"- duplicate cases: {len(summary.duplicate_cases)}",
        f"- invalid filled cases: {len(summary.invalid_cases)}",
    ]
    if summary.failure_tags:
        lines.append(
            "- failure tags: "
            + ", ".join(f"{tag}={count}" for tag, count in sorted(summary.failure_tags.items()))
        )
    else:
        lines.append("- failure tags: none")
    if summary.gate_statuses:
        lines.append(
            "- gate statuses: "
            + ", ".join(f"{status}={count}" for status, count in sorted(summary.gate_statuses.items()))
        )
    else:
        lines.append("- gate statuses: none")

    lines.append("- next missing cases: " + format_list(summary.missing_cases, limit))
    lines.append("- next TODO cases: " + format_list(summary.todo_cases, limit))
    lines.append("- next invalid cases: " + format_list(summary.invalid_cases, limit))

    if show_axes:
        lines.append("- reviewed coverage:")
        for axis in AXES:
            covered, required, counts = summary.coverage[axis]
            lines.append(f"  - {axis}: {covered}/{required}")
            for value, count in sorted(counts.items()):
                if count:
                    lines.append(f"    - {value}: {count}")

    if show_cases:
        lines.append("- valid reviewed cases: " + format_list(summary.reviewed_cases, limit))
        lines.append("- valid pass cases: " + format_list(summary.pass_cases, limit))
    return "\n".join(lines)


def run_self_test(root: Path = ROOT) -> list[str]:
    checker = load_checker(root)
    case_name = sorted(checker.eval_case_names(root))[0]
    valid_response = (
        "The captured response reconstructs intent, gives an owner recommendation, "
        "handles context evidence, names a concrete risk, and gives a usable next action."
    )
    valid_evidence = "Concrete response behavior is cited in the evaluator notes."
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="converge-response-eval-summary-") as tmp:
        tmp_path = Path(tmp)
        other_path = tmp_path / "other"
        other_path.mkdir()
        (tmp_path / "one.result.md").write_text(
            checker.sample_result(
                case_name,
                evaluator="manual-review",
                model_host="codex-real-host",
                response=valid_response,
                evidence=valid_evidence,
            ),
            encoding="utf-8",
        )
        summary = compute_summary(tmp_path, root, require_real_results=True)
        if summary.valid_reviewed != 1 or summary.valid_pass != 1 or summary.invalid_or_unreviewed != summary.expected_cases - 1:
            errors.append("self-test progress counts are wrong for one valid result")
        if case_name not in summary.reviewed_cases:
            errors.append("self-test valid case was not listed as reviewed")

        case_names = sorted(checker.eval_case_names(root))
        if len(case_names) > 1:
            second_case = case_names[1]
            (other_path / "second.result.md").write_text(
                checker.sample_result(
                    second_case,
                    evaluator="manual-review",
                    model_host="codex-real-host",
                    response=valid_response,
                    evidence=valid_evidence,
                ),
                encoding="utf-8",
            )
            aggregate_summary = compute_summary(
                [tmp_path, other_path],
                root,
                require_real_results=True,
            )
            if aggregate_summary.valid_reviewed != 2 or aggregate_summary.valid_pass != 2:
                errors.append("self-test aggregate progress counts are wrong for multiple dirs")

        (tmp_path / "bad.result.md").write_text(
            checker.sample_result(
                case_name,
                evaluator="release-smoke",
                model_host="synthetic",
                response=valid_response,
                evidence="ok",
            ),
            encoding="utf-8",
        )
        strict_summary = compute_summary(tmp_path, root, require_real_results=True)
        if case_name not in strict_summary.invalid_cases:
            errors.append("self-test did not flag synthetic duplicate/invalid case")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dirs", type=Path, nargs="*")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-real-results", action="store_true")
    parser.add_argument("--show-axes", action="store_true")
    parser.add_argument("--show-cases", action="store_true")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test(args.root)
        print("Converge response-eval summary self-test")
        if errors:
            print("Self-test failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Self-test passed.")
        return 0

    if not args.results_dirs:
        parser.error("at least one results_dir is required unless --self-test is used")
    if args.limit < 1:
        parser.error("--limit must be >= 1")

    summary = compute_summary(args.results_dirs, args.root, require_real_results=args.require_real_results)
    print(progress_report(summary, args.show_axes, args.show_cases, args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
