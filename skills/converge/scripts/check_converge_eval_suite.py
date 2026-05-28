#!/usr/bin/env python3
"""Validate Converge eval case quality and failure-tag coverage."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS = ("## User Prompt", "## Expected Behavior", "## Failure Tags")
TAG_RE = re.compile(r"^- `([^`]+)`\s*$")
RUBRIC_TAG_RE = re.compile(r"^- `([^`]+)`\s*$")


def section_after(text: str, heading: str) -> str:
    if heading not in text:
        return ""
    tail = text.split(heading, 1)[1]
    next_heading = re.search(r"\n## ", tail)
    if next_heading:
        return tail[: next_heading.start()]
    return tail


def rubric_tags(root: Path) -> set[str]:
    text = (root / "eval-rubric.md").read_text(encoding="utf-8")
    block = section_after(text, "## Failure Tags")
    return {match.group(1) for line in block.splitlines() if (match := RUBRIC_TAG_RE.match(line.strip()))}


def case_tags(case_path: Path) -> tuple[list[str], list[str]]:
    block = section_after(case_path.read_text(encoding="utf-8"), "## Failure Tags")
    tags: list[str] = []
    malformed: list[str] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line.startswith("-"):
            continue
        match = TAG_RE.match(line)
        if not match:
            malformed.append(line)
            continue
        tags.append(match.group(1))
    return tags, malformed


def coverage_index(root: Path) -> tuple[set[str], list[Path], dict[str, list[str]]]:
    known_tags = rubric_tags(root)
    cases = sorted((root / "eval-cases").glob("*.md"))
    coverage: dict[str, list[str]] = defaultdict(list)
    for case in cases:
        tags, _malformed = case_tags(case)
        for tag in tags:
            coverage[tag].append(case.name)
    return known_tags, cases, coverage


def run_checks(root: Path = ROOT, min_cases_per_tag: int = 1) -> list[str]:
    errors: list[str] = []
    eval_dir = root / "eval-cases"
    cases = sorted(eval_dir.glob("*.md"))
    if not cases:
        errors.append("no eval cases found")
        return errors

    known_tags = rubric_tags(root)
    if not known_tags:
        errors.append("eval-rubric.md has no parseable failure tags")
        return errors

    coverage: dict[str, list[str]] = defaultdict(list)
    for case in cases:
        rel = case.relative_to(root)
        text = case.read_text(encoding="utf-8")
        for heading in REQUIRED_SECTIONS:
            if heading not in text:
                errors.append(f"{rel}: missing {heading}")

        prompt = section_after(text, "## User Prompt")
        if "```" not in prompt:
            errors.append(f"{rel}: User Prompt should be fenced")

        expected = section_after(text, "## Expected Behavior")
        expected_bullets = [line for line in expected.splitlines() if line.strip().startswith("-")]
        if len(expected_bullets) < 3:
            errors.append(f"{rel}: Expected Behavior should contain at least 3 bullets")

        tags, malformed = case_tags(case)
        if malformed:
            errors.append(f"{rel}: malformed failure tag lines: {malformed}")
        if not tags:
            errors.append(f"{rel}: no parseable failure tags")
        for tag in tags:
            if tag not in known_tags:
                errors.append(f"{rel}: unknown failure tag `{tag}`")
            coverage[tag].append(case.name)

    for tag in sorted(known_tags):
        if tag not in coverage:
            errors.append(f"rubric tag `{tag}` has no eval-case coverage")
        elif len(coverage[tag]) < min_cases_per_tag:
            errors.append(
                f"rubric tag `{tag}` has {len(coverage[tag])} eval-case(s), "
                f"below required minimum {min_cases_per_tag}"
            )

    return errors


def coverage_report(root: Path = ROOT, min_cases_per_tag: int = 1, show_tag_counts: bool = False) -> str:
    known_tags, cases, coverage = coverage_index(root)
    covered = [tag for tag in known_tags if tag in coverage]
    weak = sorted(tag for tag in known_tags if 0 < len(coverage.get(tag, [])) < min_cases_per_tag)
    singletons = sorted(tag for tag in known_tags if len(coverage.get(tag, [])) == 1)
    lines = [
        "Converge eval suite report",
        f"- cases: {len(cases)}",
        f"- rubric tags: {len(known_tags)}",
        f"- covered tags: {len(covered)}",
        f"- min cases per tag: {min_cases_per_tag}",
        f"- singleton tags: {len(singletons)}",
    ]
    uncovered = sorted(tag for tag in known_tags if tag not in coverage)
    if uncovered:
        lines.append(f"- uncovered: {', '.join(uncovered)}")
    else:
        lines.append("- uncovered: none")
    if weak:
        lines.append(f"- weak tags: {', '.join(weak)}")
    else:
        lines.append("- weak tags: none")
    if show_tag_counts:
        lines.append("- tag counts:")
        for tag in sorted(known_tags):
            cases_for_tag = ", ".join(sorted(coverage.get(tag, []))) or "none"
            lines.append(f"  - {tag}: {len(coverage.get(tag, []))} ({cases_for_tag})")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--min-cases-per-tag", type=int, default=1)
    parser.add_argument("--show-tag-counts", action="store_true")
    args = parser.parse_args()
    if args.min_cases_per_tag < 1:
        print("--min-cases-per-tag must be >= 1")
        return 1

    errors = run_checks(args.root, min_cases_per_tag=args.min_cases_per_tag)
    print(coverage_report(args.root, args.min_cases_per_tag, args.show_tag_counts))
    if errors:
        print("Converge eval suite validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Converge eval suite validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
