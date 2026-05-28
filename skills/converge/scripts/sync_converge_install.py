#!/usr/bin/env python3
"""Sync the canonical Converge skill into supported agent hosts and install the Cursor rule bridge."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = {
    "claude": Path.home() / ".claude" / "skills" / "converge",
    "cursor": Path.home() / ".cursor" / "skills" / "converge",
    "opencode": Path.home() / ".config" / "opencode" / "skills" / "converge",
    "cline": Path.home() / ".cline" / "skills" / "converge",
    "antigravity": Path.home() / ".gemini" / "antigravity" / "skills" / "converge",
}
CURSOR_RULE_PATH = Path.home() / ".cursor" / "rules" / "converge.mdc"
CURSOR_RULE_TEXT = """---
description: "Converge intent reconstruction. Use when the user asks to think through fuzzy work, clarify an idea, make a decision, draft a plan, evaluate a technical route, or explicitly invokes converge."
alwaysApply: false
---

# Converge - Owner-Mode Intent Reconstruction

Read `~/.cursor/skills/converge/SKILL.md` and follow that skill when Converge is relevant.

Use Converge to reconstruct intent, inspect accessible context, verify drift-prone claims when needed, make an owner recommendation, and produce the next usable reply, plan, decision, or artifact.

For simple direct tasks, use the skill's Universal Intent Guard briefly, then execute the task instead of adding ceremony.
"""


@dataclass(frozen=True)
class SyncResult:
    name: str
    target: Path
    file_count: int
    backup: Path | None
    dry_run: bool


@dataclass(frozen=True)
class RuleResult:
    path: Path
    backup: Path | None
    changed: bool
    dry_run: bool


def count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def validate_source(source: Path) -> None:
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "scripts/check_converge_skill.py",
        "scripts/check_converge_eval_suite.py",
        "scripts/check_converge_coverage_matrix.py",
        "scripts/build_converge_response_eval.py",
        "scripts/check_converge_response_eval.py",
        "scripts/summarize_converge_response_eval.py",
        "scripts/select_converge_response_eval_batch.py",
        "scripts/sync_converge_install.py",
        "scripts/check_converge_release.py",
    ]
    for rel in required:
        if not (source / rel).is_file():
            raise FileNotFoundError(f"source missing required file: {rel}")


def sync_one(source: Path, name: str, target: Path, backup_root: Path, dry_run: bool) -> SyncResult:
    validate_source(source)
    backup_path: Path | None = None

    if dry_run:
        return SyncResult(name=name, target=target, file_count=count_files(source), backup=None, dry_run=True)

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = backup_root / name / target.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if target.is_dir() and not target.is_symlink():
            shutil.copytree(target, backup_path, symlinks=True)
            shutil.rmtree(target)
        else:
            shutil.copy2(target, backup_path)
            target.unlink()

    shutil.copytree(
        source,
        target,
        symlinks=True,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", ".git"),
    )

    return SyncResult(
        name=name,
        target=target,
        file_count=count_files(target),
        backup=backup_path,
        dry_run=False,
    )


def sync_cursor_rule(backup_root: Path, dry_run: bool) -> RuleResult:
    existing = CURSOR_RULE_PATH.read_text(encoding="utf-8") if CURSOR_RULE_PATH.is_file() else None
    changed = existing != CURSOR_RULE_TEXT
    backup_path: Path | None = None

    if dry_run or not changed:
        return RuleResult(path=CURSOR_RULE_PATH, backup=None, changed=changed, dry_run=dry_run)

    CURSOR_RULE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CURSOR_RULE_PATH.exists() or CURSOR_RULE_PATH.is_symlink():
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = backup_root / "cursor-rule" / CURSOR_RULE_PATH.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CURSOR_RULE_PATH, backup_path)
    CURSOR_RULE_PATH.write_text(CURSOR_RULE_TEXT, encoding="utf-8")
    return RuleResult(path=CURSOR_RULE_PATH, backup=backup_path, changed=True, dry_run=False)


def parse_targets(value: str) -> list[str]:
    if value == "all":
        return list(DEFAULT_TARGETS)
    names = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [name for name in names if name not in DEFAULT_TARGETS]
    if unknown:
        raise ValueError(f"unknown target(s): {', '.join(unknown)}")
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument(
        "--targets",
        default="all",
        help="all, claude, cursor, opencode, cline, antigravity, or comma-separated names",
    )
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=Path("/private/tmp/converge-skill-install-backups")
        / datetime.now().strftime("%Y%m%d-%H%M%S"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        target_names = parse_targets(args.targets)
        results = [
            sync_one(args.source, name, DEFAULT_TARGETS[name], args.backup_root, args.dry_run)
            for name in target_names
        ]
        rule_result = sync_cursor_rule(args.backup_root, args.dry_run) if "cursor" in target_names else None
    except Exception as exc:
        print(f"Converge sync failed: {exc}")
        return 1

    action = "would sync" if args.dry_run else "synced"
    print(f"Converge skill {action}.")
    print(f"source={args.source}")
    for result in results:
        backup = str(result.backup) if result.backup else "none"
        print(
            f"{result.name}: target={result.target} files={result.file_count} "
            f"backup={backup} dry_run={result.dry_run}"
        )
    if rule_result:
        backup = str(rule_result.backup) if rule_result.backup else "none"
        print(
            f"cursor-rule: target={rule_result.path} changed={rule_result.changed} "
            f"backup={backup} dry_run={rule_result.dry_run}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
