#!/usr/bin/env python3
"""Run repository-level validation for Converge."""

from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "converge"
REQUIRED_ROOT_FILES = [
    "README.md",
    "pyproject.toml",
    "LICENSE",
    "VERSION",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/quickstart.md",
    "docs/protocol.md",
    "docs/cli.md",
    "docs/install.md",
    "docs/host-support.md",
    "docs/evaluation.md",
    "docs/release.md",
    "protocol/schemas/converge-run.schema.json",
    "protocol/schemas/host-capability.schema.json",
    "protocol/schemas/host-adapter-registry.schema.json",
    "protocol/schemas/native-interaction-proof.schema.json",
    "protocol/schemas/eval-result.schema.json",
    "protocol/schemas/converge-compatible-manifest.schema.json",
    "protocol/examples/converge-run.example.json",
    "protocol/examples/host-capability.example.json",
    "protocol/examples/host-adapter-registry.example.json",
    "protocol/examples/native-interaction-proof.example.json",
    "protocol/examples/eval-result.example.json",
    "protocol/examples/converge-compatible-manifest.example.json",
    "converge/__init__.py",
    "converge/__main__.py",
    "converge/cli.py",
    "converge/hosts.py",
    "intentbench/README.md",
    "intentbench/manifest.json",
    "gallery/README.md",
    ".github/workflows/validate.yml",
]
GENERATED_PATTERNS = {
    "__pycache__",
    ".DS_Store",
    ".pytest_cache",
}
GENERATED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".swp",
}


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(command, cwd=ROOT, env=env)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def check_repository_hygiene() -> None:
    missing = [rel for rel in REQUIRED_ROOT_FILES if not (ROOT / rel).is_file()]
    if missing:
        raise SystemExit(f"missing repository file(s): {', '.join(missing)}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re_match_version(version):
        raise SystemExit(f"VERSION must be semantic x.y.z, got: {version}")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {version} " not in changelog and f"## {version} -" not in changelog:
        raise SystemExit(f"CHANGELOG.md missing entry for {version}")

    generated: list[str] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.name in GENERATED_PATTERNS or path.suffix in GENERATED_SUFFIXES:
            generated.append(str(path.relative_to(ROOT)))
    if generated:
        raise SystemExit("generated files present: " + ", ".join(sorted(generated)))


def re_match_version(value: str) -> bool:
    parts = value.split(".")
    return len(parts) == 3 and all(part.isdigit() for part in parts)


def main() -> int:
    if not (SKILL_ROOT / "SKILL.md").is_file():
        print(f"missing skill: {SKILL_ROOT / 'SKILL.md'}")
        return 1

    check_repository_hygiene()
    python = sys.executable
    run([python, "-m", "converge", "validate", "--protocol-only"])
    run([python, "-m", "converge", "doctor", "--json"])
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
    run([python, str(SKILL_ROOT / "scripts" / "check_converge_native_proof.py"), "--self-test"])
    run([python, str(SKILL_ROOT / "scripts" / "check_intentbench.py"), "--self-test"])
    run([python, str(SKILL_ROOT / "scripts" / "summarize_intentbench.py"), "--self-test"])
    run([python, "-m", "converge", "benchmark", "--validate"])
    run(
        [
            python,
            str(SKILL_ROOT / "scripts" / "check_converge_release.py"),
            "--source",
            str(SKILL_ROOT),
            "--skip-installs",
        ]
    )
    check_repository_hygiene()
    print("Repository verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
