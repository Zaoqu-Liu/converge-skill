#!/usr/bin/env python3
"""Select Converge response-eval case batches for pilot, holdout, and coverage runs."""

from __future__ import annotations

import argparse
from collections import defaultdict
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
PILOT_SEEDS = (
    "low-expression-idea.md",
    "explicit-converge-simple-task.md",
    "technology-route-current-stack.md",
    "mixed-artifact-intake.md",
    "context-poisoning-boundary.md",
    "codex-default-no-native-ui.md",
    "codex-plan-native-question-ui.md",
    "claude-native-question-bridge.md",
    "cursor-native-question-bridge.md",
    "skill-evolution-overfit-holdout.md",
)


@dataclass(frozen=True)
class Selection:
    cases: tuple[str, ...]
    covered: int
    required: int
    uncovered: tuple[str, ...]
    mode: str


def load_module(root: Path, script_name: str, module_name: str) -> ModuleType:
    script_path = root / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def eval_cases(root: Path) -> set[str]:
    return {path.name for path in (root / "eval-cases").glob("*.md")}


def coverage_by_case(root: Path) -> dict[str, set[str]]:
    cases = eval_cases(root)
    path = root / COVERAGE_FILE
    coverage: dict[str, set[str]] = {case: set() for case in cases}
    if not path.is_file():
        return coverage
    for raw_line in path.read_text(encoding="utf-8").splitlines()[1:]:
        if not raw_line.strip() or raw_line.startswith("#"):
            continue
        parts = raw_line.split("\t")
        if len(parts) != 3:
            continue
        case_name, axis, value = (part.strip() for part in parts)
        if case_name in coverage and axis in AXES:
            coverage[case_name].add(f"{axis}:{value}")
    return coverage


def target_items(coverage: dict[str, set[str]], axes: set[str] | None = None) -> set[str]:
    items = set().union(*coverage.values()) if coverage else set()
    if axes is None:
        return items
    return {item for item in items if item.split(":", 1)[0] in axes}


def reviewed_cases(root: Path, results_dir: Path | None, require_real_results: bool) -> set[str]:
    if results_dir is None:
        return set()
    summary_module = load_module(root, "summarize_converge_response_eval.py", "converge_response_eval_summary")
    summary = summary_module.compute_summary(results_dir, root, require_real_results=require_real_results)
    return set(summary.reviewed_cases)


def failed_or_invalid_cases(root: Path, results_dir: Path | None, require_real_results: bool) -> tuple[str, ...]:
    if results_dir is None:
        return tuple()
    summary_module = load_module(root, "summarize_converge_response_eval.py", "converge_response_eval_summary")
    summary = summary_module.compute_summary(results_dir, root, require_real_results=require_real_results)
    return tuple(sorted(set(summary.invalid_cases) | set(summary.todo_cases) | set(summary.missing_cases)))


def greedy_cover(
    coverage: dict[str, set[str]],
    required: set[str],
    candidates: set[str] | None = None,
    seed_cases: tuple[str, ...] = tuple(),
    max_cases: int | None = None,
) -> Selection:
    available = set(coverage) if candidates is None else set(candidates)
    selected: list[str] = []
    covered: set[str] = set()

    for case_name in seed_cases:
        if case_name in available and case_name not in selected:
            selected.append(case_name)
            covered |= coverage.get(case_name, set()) & required
            if max_cases is not None and len(selected) >= max_cases:
                break

    while covered < required:
        if max_cases is not None and len(selected) >= max_cases:
            break
        remaining = available - set(selected)
        if not remaining:
            break
        ranked = sorted(
            remaining,
            key=lambda case: (-len((coverage.get(case, set()) & required) - covered), case),
        )
        best = ranked[0]
        gain = (coverage.get(best, set()) & required) - covered
        if not gain:
            break
        selected.append(best)
        covered |= coverage.get(best, set()) & required

    uncovered = tuple(sorted(required - covered))
    return Selection(
        cases=tuple(selected),
        covered=len(covered),
        required=len(required),
        uncovered=uncovered,
        mode="",
    )


def limit_cases(cases: tuple[str, ...], max_cases: int | None) -> tuple[str, ...]:
    if max_cases is None:
        return cases
    return cases[:max_cases]


def select_batch(
    root: Path = ROOT,
    mode: str = "minimal-cover",
    results_dir: Path | None = None,
    require_real_results: bool = False,
    axes: set[str] | None = None,
    max_cases: int | None = None,
) -> Selection:
    coverage = coverage_by_case(root)
    required = target_items(coverage, axes)
    reviewed = reviewed_cases(root, results_dir, require_real_results)

    if mode == "all":
        cases = limit_cases(tuple(sorted(coverage)), max_cases)
        covered = set().union(*(coverage[case] for case in cases)) & required if cases else set()
        return Selection(cases, len(covered), len(required), tuple(sorted(required - covered)), mode)

    if mode == "failed-or-invalid":
        cases = limit_cases(failed_or_invalid_cases(root, results_dir, require_real_results), max_cases)
        covered = set().union(*(coverage.get(case, set()) for case in cases)) & required if cases else set()
        return Selection(cases, len(covered), len(required), tuple(sorted(required - covered)), mode)

    if mode == "next-cover":
        already_covered = set().union(*(coverage.get(case, set()) for case in reviewed)) & required if reviewed else set()
        required = required - already_covered
        candidates = set(coverage) - reviewed
        selection = greedy_cover(coverage, required, candidates=candidates, max_cases=max_cases)
        return Selection(selection.cases, selection.covered, selection.required, selection.uncovered, mode)

    if mode == "pilot":
        selection = greedy_cover(coverage, required, seed_cases=PILOT_SEEDS, max_cases=max_cases)
        return Selection(selection.cases, selection.covered, selection.required, selection.uncovered, mode)

    selection = greedy_cover(coverage, required, max_cases=max_cases)
    return Selection(selection.cases, selection.covered, selection.required, selection.uncovered, mode)


def format_selection(selection: Selection, root: Path, out_dir: Path | None = None) -> str:
    lines = [
        "Converge response-eval batch selection",
        f"- mode: {selection.mode}",
        f"- cases: {len(selection.cases)}",
        f"- coverage items: {selection.covered}/{selection.required}",
    ]
    if selection.uncovered:
        lines.append("- uncovered: " + ", ".join(selection.uncovered[:20]))
        if len(selection.uncovered) > 20:
            lines.append(f"- uncovered remaining: {len(selection.uncovered) - 20}")
    else:
        lines.append("- uncovered: none")
    lines.append("- selected cases:")
    for index, case_name in enumerate(selection.cases, start=1):
        prompt = f"{Path(case_name).stem}.prompt.md"
        review = f"{Path(case_name).stem}.review.md"
        result = f"{Path(case_name).stem}.result.md"
        if out_dir:
            lines.append(
                f"  {index}. {case_name} | "
                f"{out_dir / 'prompts' / prompt} | "
                f"{out_dir / 'reviews' / review} | "
                f"{out_dir / 'results' / result}"
            )
        else:
            lines.append(f"  {index}. {case_name}")
    return "\n".join(lines)


def write_manifest(selection: Selection, out: Path, runpack: Path | None) -> None:
    columns = ["case"]
    if runpack:
        columns.extend(["prompt_packet", "review_packet", "result_file"])
    lines = ["\t".join(columns)]
    for case_name in selection.cases:
        row = [case_name]
        if runpack:
            stem = Path(case_name).stem
            row.extend(
                [
                    str(runpack / "prompts" / f"{stem}.prompt.md"),
                    str(runpack / "reviews" / f"{stem}.review.md"),
                    str(runpack / "results" / f"{stem}.result.md"),
                ]
            )
        lines.append("\t".join(row))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_axes(value: str | None) -> set[str] | None:
    if not value:
        return None
    axes = {item.strip() for item in value.split(",") if item.strip()}
    unknown = axes - set(AXES)
    if unknown:
        raise ValueError(f"unknown axes: {', '.join(sorted(unknown))}")
    return axes


def run_self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    minimal = select_batch(root, mode="minimal-cover")
    if not minimal.cases:
        errors.append("minimal-cover selected no cases")
    if minimal.uncovered:
        errors.append("minimal-cover left uncovered items")

    pilot = select_batch(root, mode="pilot", max_cases=10)
    if len(pilot.cases) > 10:
        errors.append("pilot max_cases was not respected")
    for seed in PILOT_SEEDS[:3]:
        if seed not in pilot.cases:
            errors.append(f"pilot missed expected seed {seed}")

    with tempfile.TemporaryDirectory(prefix="converge-batch-selector-") as tmp:
        tmp_path = Path(tmp)
        checker = load_module(root, "check_converge_response_eval.py", "converge_response_eval_checker_for_selector")
        first_case = sorted(coverage_by_case(root))[0]
        (tmp_path / f"{Path(first_case).stem}.result.md").write_text(
            checker.sample_result(
                first_case,
                evaluator="manual-review",
                model_host="codex-real-host",
                response=(
                    "The captured response reconstructs intent, makes an owner recommendation, "
                    "handles evidence, names a risk, and gives a usable next action."
                ),
                evidence="Concrete response behavior is cited.",
            ),
            encoding="utf-8",
        )
        next_cover = select_batch(root, mode="next-cover", results_dir=tmp_path, require_real_results=True)
        if first_case in next_cover.cases:
            errors.append("next-cover selected an already valid reviewed case")

        limited_failed = select_batch(
            root,
            mode="failed-or-invalid",
            results_dir=tmp_path,
            require_real_results=True,
            max_cases=1,
        )
        if len(limited_failed.cases) > 1:
            errors.append("failed-or-invalid max_cases was not respected")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--mode",
        choices=("minimal-cover", "pilot", "next-cover", "failed-or-invalid", "all"),
        default="minimal-cover",
    )
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--require-real-results", action="store_true")
    parser.add_argument("--axes", help="Comma-separated subset of coverage axes")
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--runpack", type=Path, help="Optional runpack directory for prompt/review/result paths")
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test(args.root)
        print("Converge response-eval batch selector self-test")
        if errors:
            print("Self-test failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Self-test passed.")
        return 0

    if args.max_cases is not None and args.max_cases < 1:
        parser.error("--max-cases must be >= 1")

    try:
        axes = parse_axes(args.axes)
    except ValueError as exc:
        parser.error(str(exc))

    selection = select_batch(
        args.root,
        mode=args.mode,
        results_dir=args.results_dir,
        require_real_results=args.require_real_results,
        axes=axes,
        max_cases=args.max_cases,
    )
    print(format_selection(selection, args.root, args.runpack))
    if args.write_manifest:
        write_manifest(selection, args.write_manifest, args.runpack)
        print(f"- wrote manifest: {args.write_manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
