#!/usr/bin/env python3
"""Run Converge release checks across canonical and installed skill copies."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile

from host_adapter_registry import CURSOR_RULE_TEXT, cursor_rule_path, install_targets, parse_targets


ROOT = Path(__file__).resolve().parents[1]
IGNORED_NAMES = {".DS_Store"}
IGNORED_PARTS = {"__pycache__", ".git"}


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def ignored(path: Path) -> bool:
    return path.name in IGNORED_NAMES or any(part in IGNORED_PARTS for part in path.parts)


def file_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ignored(path.relative_to(root)):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes[str(path.relative_to(root))] = digest
    return hashes


def run_command(command: list[str]) -> CheckResult:
    label = " ".join(command)
    completed = subprocess.run(command, text=True, capture_output=True)
    output = (completed.stdout + completed.stderr).strip()
    return CheckResult(label, completed.returncode == 0, output or "ok")


def run_skill_validators(root: Path) -> list[CheckResult]:
    commands = [
        [sys.executable, str(root / "scripts" / "check_converge_skill.py")],
        [
            sys.executable,
            str(root / "scripts" / "check_converge_eval_suite.py"),
            "--min-cases-per-tag",
            "2",
        ],
        [sys.executable, str(root / "scripts" / "check_converge_coverage_matrix.py")],
        [sys.executable, str(root / "scripts" / "check_converge_response_eval.py"), "--self-test"],
        [sys.executable, str(root / "scripts" / "summarize_converge_response_eval.py"), "--self-test"],
        [sys.executable, str(root / "scripts" / "select_converge_response_eval_batch.py"), "--self-test"],
    ]
    return [run_command(command) for command in commands]


def compile_scripts(root: Path) -> CheckResult:
    try:
        scripts = sorted((root / "scripts").glob("*.py"))
        for script in scripts:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        return CheckResult(f"compile scripts in {root}", True, f"compiled {len(scripts)} scripts")
    except SyntaxError as exc:
        return CheckResult(f"compile scripts in {root}", False, str(exc))


def check_cursor_rule_bridge(source: Path) -> CheckResult:
    path = cursor_rule_path(source)
    if path is None:
        return CheckResult("cursor rule bridge", False, "cursor bridge path missing from host-adapters.json")
    if not path.is_file():
        return CheckResult("cursor rule bridge", False, f"missing: {path}")
    actual = path.read_text(encoding="utf-8")
    if actual != CURSOR_RULE_TEXT:
        return CheckResult("cursor rule bridge", False, f"stale or changed: {path}")
    return CheckResult("cursor rule bridge", True, str(path))


def compare_tree(source: Path, target: Path, name: str) -> CheckResult:
    if not target.is_dir():
        return CheckResult(f"compare {name}", False, f"target missing: {target}")
    source_hashes = file_hashes(source)
    target_hashes = file_hashes(target)
    if source_hashes == target_hashes:
        return CheckResult(f"compare {name}", True, f"{len(source_hashes)} files match")
    missing = sorted(set(source_hashes) - set(target_hashes))
    extra = sorted(set(target_hashes) - set(source_hashes))
    changed = sorted(key for key in source_hashes.keys() & target_hashes.keys() if source_hashes[key] != target_hashes[key])
    details = []
    if missing:
        details.append(f"missing={missing[:5]}")
    if extra:
        details.append(f"extra={extra[:5]}")
    if changed:
        details.append(f"changed={changed[:5]}")
    return CheckResult(f"compare {name}", False, "; ".join(details))


def write_smoke_result(results_dir: Path, case_name: str, prompt_path: Path, skill_path: Path) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(case_name).stem
    (results_dir / f"{stem}.result.md").write_text(
        f"""# Converge Response Eval Result - {stem}

## Metadata

- Case: {case_name}
- Verdict: Pass
- Evaluator: release-smoke
- Model/Host: synthetic
- Date: {date.today().isoformat()}
- Skill Path: {skill_path}
- Response Artifact: inline

## Prompt Given

{prompt_path}

## Response

The response reconstructs intent, makes an owner recommendation, identifies the main risk, and asks only high-leverage follow-up questions.

## Gate Results

| Gate | Status | Evidence |
|---|---|---|
| Activation | Pass | Explicit Converge invocation is present in the prompt packet. |
| Intent reconstruction | Pass | Synthetic response includes intent reconstruction. |
| Owner recommendation | Pass | Synthetic response includes an owner recommendation. |
| Context/evidence handling | N/A | No external artifacts are provided in this smoke case. |
| Risk/challenge quality | Pass | Synthetic response identifies a framing risk. |
| Output usefulness | Pass | Synthetic response gives a usable next step. |

## Failure Tags

- None.

## Fix Recommendation

None.
""",
        encoding="utf-8",
    )


def response_eval_smoke(root: Path, case_name: str, workdir: Path) -> list[CheckResult]:
    out_dir = workdir / "packets"
    results_dir = workdir / "results"
    build_script = root / "scripts" / "build_converge_response_eval.py"
    check_script = root / "scripts" / "check_converge_response_eval.py"
    build = run_command(
        [
            sys.executable,
            str(build_script),
            "--root",
            str(root),
            "--out",
            str(out_dir),
            "--case",
            case_name,
            "--skill-path",
            str(root / "SKILL.md"),
        ]
    )
    results = [build]
    prompt_path = out_dir / "prompts" / f"{Path(case_name).stem}.prompt.md"
    review_path = out_dir / "reviews" / f"{Path(case_name).stem}.review.md"
    runbook_path = out_dir / "RUNBOOK.md"
    if build.ok and prompt_path.is_file() and review_path.is_file() and runbook_path.is_file():
        results.append(CheckResult("response-eval packet files", True, "prompt, review packet, and runbook exist"))
        write_smoke_result(results_dir, case_name, prompt_path, root / "SKILL.md")
        results.append(run_command([sys.executable, str(check_script), str(results_dir), "--root", str(root)]))
    elif build.ok:
        results.append(CheckResult("response-eval packet files", False, "prompt, review packet, or runbook missing"))
    return results


def response_eval_results_check(root: Path, results_dir: Path | None, require_results: bool) -> list[CheckResult]:
    if results_dir is None:
        if require_results:
            return [CheckResult("real response-eval results", False, "--response-results-dir is required")]
        return [CheckResult("real response-eval results", True, "not provided; behavior-level proof not claimed")]
    script = root / "scripts" / "check_converge_response_eval.py"
    command = [
        sys.executable,
        str(script),
        str(results_dir),
        "--root",
        str(root),
        "--require-all-cases",
        "--require-real-results",
    ]
    return [run_command(command)]


def release_checks(
    source: Path,
    targets: list[str],
    skip_installs: bool,
    smoke_case: str,
    response_results_dir: Path | None,
    require_response_results: bool,
) -> list[CheckResult]:
    results: list[CheckResult] = []
    results.extend(run_skill_validators(source))
    results.append(compile_scripts(source))
    with tempfile.TemporaryDirectory(prefix="converge-release-check-") as tmp:
        results.extend(response_eval_smoke(source, smoke_case, Path(tmp) / "source"))
    results.extend(response_eval_results_check(source, response_results_dir, require_response_results))

    if not skip_installs:
        installed_targets = install_targets(source)
        for name in targets:
            target = installed_targets[name]
            results.append(compare_tree(source, target, name))
            if target.is_dir():
                results.extend(run_skill_validators(target))
                results.append(compile_scripts(target))
            if name == "cursor":
                results.append(check_cursor_rule_bridge(source))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--targets", default="all")
    parser.add_argument("--skip-installs", action="store_true")
    parser.add_argument("--smoke-case", default="low-expression-idea.md")
    parser.add_argument("--response-results-dir", type=Path)
    parser.add_argument("--require-response-results", action="store_true")
    args = parser.parse_args()

    try:
        targets = parse_targets(args.targets, install_targets(args.source))
        results = release_checks(
            args.source,
            targets,
            args.skip_installs,
            args.smoke_case,
            args.response_results_dir,
            args.require_response_results,
        )
    except Exception as exc:
        print(f"Converge release check failed to run: {exc}")
        return 1

    failures = [result for result in results if not result.ok]
    print("Converge release check report")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- [{status}] {result.name}: {result.detail}")
    if failures:
        print(f"Converge release check failed: {len(failures)} failure(s)")
        return 1
    print("Converge release check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
