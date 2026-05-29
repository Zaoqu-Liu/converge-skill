#!/usr/bin/env python3
"""Sync the canonical Converge skill into supported agent hosts and install the Cursor rule bridge."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import sys

from host_adapter_registry import CURSOR_RULE_TEXT, cursor_rule_path, install_targets, parse_targets


ROOT = Path(__file__).resolve().parents[1]


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
        "host-adapters.json",
        "agents/openai.yaml",
        "scripts/host_adapter_registry.py",
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


def sync_cursor_rule(path: Path, backup_root: Path, dry_run: bool) -> RuleResult:
    existing = path.read_text(encoding="utf-8") if path.is_file() else None
    changed = existing != CURSOR_RULE_TEXT
    backup_path: Path | None = None

    if dry_run or not changed:
        return RuleResult(path=path, backup=None, changed=changed, dry_run=dry_run)

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = backup_root / "cursor-rule" / path.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
    path.write_text(CURSOR_RULE_TEXT, encoding="utf-8")
    return RuleResult(path=path, backup=backup_path, changed=True, dry_run=False)


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
        targets = install_targets(args.source)
        target_names = parse_targets(args.targets, targets)
        results = [
            sync_one(args.source, name, targets[name], args.backup_root, args.dry_run)
            for name in target_names
        ]
        rule_path = cursor_rule_path(args.source)
        rule_result = sync_cursor_rule(rule_path, args.backup_root, args.dry_run) if "cursor" in target_names and rule_path else None
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
