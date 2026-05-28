#!/usr/bin/env python3
"""Run repository-level validation for Converge."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "converge"


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    if not (SKILL_ROOT / "SKILL.md").is_file():
        print(f"missing skill: {SKILL_ROOT / 'SKILL.md'}")
        return 1

    python = sys.executable
    run([python, str(SKILL_ROOT / "scripts" / "check_converge_skill.py")])
    run(
        [
            python,
            str(SKILL_ROOT / "scripts" / "check_converge_eval_suite.py"),
            "--min-cases-per-tag",
            "2",
        ]
    )
    run([python, str(SKILL_ROOT / "scripts" / "check_converge_coverage_matrix.py")])
    run([python, str(SKILL_ROOT / "scripts" / "check_converge_response_eval.py"), "--self-test"])
    run([python, str(SKILL_ROOT / "scripts" / "summarize_converge_response_eval.py"), "--self-test"])
    run([python, str(SKILL_ROOT / "scripts" / "select_converge_response_eval_batch.py"), "--self-test"])
    run(
        [
            python,
            str(SKILL_ROOT / "scripts" / "check_converge_release.py"),
            "--source",
            str(SKILL_ROOT),
            "--skip-installs",
        ]
    )
    print("Repository verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
