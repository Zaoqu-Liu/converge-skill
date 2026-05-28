#!/usr/bin/env python3
"""Validate filled Converge response-eval result files."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS = (
    "## Metadata",
    "## Prompt Given",
    "## Response",
    "## Gate Results",
    "## Failure Tags",
    "## Fix Recommendation",
)
REQUIRED_METADATA = (
    "case",
    "verdict",
    "evaluator",
    "model/host",
    "date",
    "skill path",
    "response artifact",
)
REQUIRED_GATES = (
    "Activation",
    "Intent reconstruction",
    "Owner recommendation",
    "Context/evidence handling",
    "Risk/challenge quality",
    "Output usefulness",
)
VALID_GATE_STATUSES = {"Pass", "Fail", "N/A", "Blocked", "Conditional"}
REAL_RESULT_FORBIDDEN_VALUES = {"synthetic", "release-smoke", "smoke", "stub", "todo"}
PLACEHOLDER_PATTERNS = (
    "TODO",
    "tag-if-failed",
    "Pass/Fail/N/A",
    "[Paste the model response",
    "[Smallest skill change",
    "[skill path used in blind prompt]",
)
TAG_RE = re.compile(r"^- `([^`]+)`\s*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class ResultRecord:
    path: Path
    case_name: str
    verdict: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class GateRow:
    gate: str
    status: str
    evidence: str
    raw: str


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
    return {
        match.group(1)
        for line in section_after(text, "## Failure Tags").splitlines()
        if (match := TAG_RE.match(line.strip()))
    }


def eval_case_names(root: Path) -> set[str]:
    return {path.name for path in (root / "eval-cases").glob("*.md")}


def metadata(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in section_after(text, "## Metadata").splitlines():
        line = raw_line.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        data[key.strip().lower()] = value.strip()
    return data


def failure_tags(text: str) -> tuple[list[str], list[str], bool]:
    tags: list[str] = []
    malformed: list[str] = []
    explicit_none = False
    for raw_line in section_after(text, "## Failure Tags").splitlines():
        line = raw_line.strip()
        if not line.startswith("-"):
            continue
        if line.lower() in {"- none", "- none."}:
            explicit_none = True
            continue
        match = TAG_RE.match(line)
        if not match:
            malformed.append(line)
            continue
        tags.append(match.group(1))
    return tags, malformed, explicit_none


def gate_rows(text: str) -> list[GateRow]:
    rows: list[GateRow] = []
    for raw_line in section_after(text, "## Gate Results").splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or "---" in line or "Gate" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 3:
            rows.append(GateRow(gate=cells[0], status=cells[1], evidence=cells[2], raw=line))
        else:
            rows.append(GateRow(gate="", status="", evidence="", raw=line))
    return rows


def has_placeholder(text: str) -> str | None:
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern in text:
            return pattern
    return None


def result_record(path: Path) -> ResultRecord:
    text = path.read_text(encoding="utf-8")
    data = metadata(text)
    tags, _malformed, _explicit_none = failure_tags(text)
    return ResultRecord(
        path=path,
        case_name=data.get("case", ""),
        verdict=data.get("verdict", ""),
        tags=tuple(tags),
    )


def check_metadata(data: dict[str, str], rel: str, require_real_results: bool) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_METADATA:
        if not data.get(key):
            errors.append(f"{rel}: Metadata {key.title()} is required")
    if data.get("date") and not DATE_RE.match(data["date"]):
        errors.append(f"{rel}: Metadata Date must use YYYY-MM-DD")
    if require_real_results:
        for key in ("evaluator", "model/host", "response artifact"):
            value = data.get(key, "").strip().lower()
            if not value:
                continue
            if value in REAL_RESULT_FORBIDDEN_VALUES or any(token in value for token in REAL_RESULT_FORBIDDEN_VALUES):
                errors.append(f"{rel}: real response-eval cannot use synthetic/stub metadata for {key}: {data[key]!r}")
    return errors


def check_gate_rows(rows: list[GateRow], rel: str, verdict: str) -> list[str]:
    errors: list[str] = []
    if not rows:
        return [f"{rel}: Gate Results needs result rows"]

    seen = {row.gate for row in rows if row.gate}
    for gate in REQUIRED_GATES:
        if gate not in seen:
            errors.append(f"{rel}: missing required gate row {gate!r}")

    for row in rows:
        if not row.gate or not row.status:
            errors.append(f"{rel}: malformed gate row {row.raw!r}")
            continue
        if row.status not in VALID_GATE_STATUSES:
            errors.append(f"{rel}: invalid gate status {row.status!r}")
        if len(row.evidence.strip()) < 12:
            errors.append(f"{rel}: gate row evidence is too weak: {row.raw!r}")
        placeholder = has_placeholder(row.raw)
        if placeholder:
            errors.append(f"{rel}: gate row still contains placeholder {placeholder!r}")

    statuses = {row.status for row in rows}
    if verdict == "Pass" and statuses & {"Fail", "Blocked", "Conditional"}:
        errors.append(f"{rel}: passing result cannot have Fail, Blocked, or Conditional gate statuses")
    if verdict == "Fail" and not (statuses & {"Fail", "Blocked", "Conditional"}):
        errors.append(f"{rel}: failing result needs at least one Fail, Blocked, or Conditional gate status")
    return errors


def check_result(path: Path, root: Path = ROOT, require_real_results: bool = False) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    rel = path.name

    for heading in REQUIRED_SECTIONS:
        if heading not in text:
            errors.append(f"{rel}: missing {heading}")

    data = metadata(text)
    errors.extend(check_metadata(data, rel, require_real_results))
    case_name = data.get("case", "")
    verdict = data.get("verdict", "")
    if case_name and not (root / "eval-cases" / case_name).is_file():
        errors.append(f"{rel}: unknown eval case {case_name!r}")

    if verdict not in {"Pass", "Fail"}:
        errors.append(f"{rel}: Verdict must be Pass or Fail")

    prompt_given = section_after(text, "## Prompt Given").strip()
    if not prompt_given:
        errors.append(f"{rel}: Prompt Given is required")

    response = section_after(text, "## Response").strip()
    if len(response) < 80:
        errors.append(f"{rel}: Response section is too short or empty")
    response_placeholder = has_placeholder(response)
    if response_placeholder:
        errors.append(f"{rel}: Response section still contains placeholder {response_placeholder!r}")

    rows = gate_rows(text)
    errors.extend(check_gate_rows(rows, rel, verdict))

    known_tags = rubric_tags(root)
    tags, malformed, explicit_none = failure_tags(text)
    for line in malformed:
        errors.append(f"{rel}: malformed failure tag line {line!r}")
    for tag in tags:
        if tag not in known_tags:
            errors.append(f"{rel}: unknown failure tag `{tag}`")

    if verdict == "Fail" and not tags:
        errors.append(f"{rel}: failing result must include at least one failure tag")
    if verdict == "Pass":
        if tags:
            errors.append(f"{rel}: passing result should not include failure tags")
        if not explicit_none:
            errors.append(f"{rel}: passing result must explicitly use '- None.' in Failure Tags")

    fix = section_after(text, "## Fix Recommendation").strip()
    fix_placeholder = has_placeholder(fix)
    if fix_placeholder:
        errors.append(f"{rel}: Fix Recommendation still contains placeholder {fix_placeholder!r}")
    if verdict == "Fail" and len(fix) < 20:
        errors.append(f"{rel}: failing result needs a concrete Fix Recommendation")
    if verdict == "Pass" and "none" not in fix.lower():
        errors.append(f"{rel}: passing result should use a no-op Fix Recommendation such as 'None.'")

    return errors


def result_files(results_dir: Path) -> list[Path]:
    return sorted(results_dir.glob("*.result.md"))


def coverage_errors(records: list[ResultRecord], root: Path) -> list[str]:
    errors: list[str] = []
    expected = eval_case_names(root)
    seen: dict[str, list[str]] = {}
    for record in records:
        if not record.case_name:
            continue
        seen.setdefault(record.case_name, []).append(record.path.name)

    missing = sorted(expected - set(seen))
    extra = sorted(set(seen) - expected)
    duplicates = {case: files for case, files in seen.items() if len(files) > 1}
    if missing:
        errors.append(f"missing result files for cases: {', '.join(missing)}")
    if extra:
        errors.append(f"result files reference unknown cases: {', '.join(extra)}")
    for case, files in sorted(duplicates.items()):
        errors.append(f"duplicate results for {case}: {', '.join(files)}")
    return errors


def summary(records: list[ResultRecord], root: Path, require_all_cases: bool, require_real_results: bool) -> str:
    expected = eval_case_names(root)
    verdicts = Counter(record.verdict for record in records)
    tag_counts = Counter(tag for record in records for tag in record.tags)
    seen_cases = {record.case_name for record in records if record.case_name}
    missing = sorted(expected - seen_cases)
    lines = [
        "Converge response-eval report",
        f"- result files: {len(records)}",
        f"- eval cases: {len(expected)}",
        f"- pass: {verdicts.get('Pass', 0)}",
        f"- fail: {verdicts.get('Fail', 0)}",
        f"- require_all_cases: {require_all_cases}",
        f"- require_real_results: {require_real_results}",
    ]
    if missing:
        lines.append(f"- missing cases: {', '.join(missing)}")
    else:
        lines.append("- missing cases: none")
    if tag_counts:
        lines.append("- failure tags: " + ", ".join(f"{tag}={count}" for tag, count in sorted(tag_counts.items())))
    else:
        lines.append("- failure tags: none")
    return "\n".join(lines)


def run_checks(
    results_dir: Path,
    root: Path = ROOT,
    require_all_cases: bool = False,
    require_real_results: bool = False,
) -> list[str]:
    errors: list[str] = []
    if not results_dir.is_dir():
        return [f"results directory not found: {results_dir}"]
    files = result_files(results_dir)
    if not files:
        return [f"no *.result.md files found in {results_dir}"]
    records = [result_record(result) for result in files]
    for result in files:
        errors.extend(check_result(result, root, require_real_results=require_real_results))
    if require_all_cases:
        errors.extend(coverage_errors(records, root))
    return errors


def sample_result(case_name: str, *, evaluator: str, model_host: str, response: str, evidence: str) -> str:
    return f"""# Converge Response Eval Result - {Path(case_name).stem}

## Metadata

- Case: {case_name}
- Verdict: Pass
- Evaluator: {evaluator}
- Model/Host: {model_host}
- Date: 2026-05-28
- Skill Path: /tmp/converge/SKILL.md
- Response Artifact: inline

## Prompt Given

prompts/{Path(case_name).stem}.prompt.md

## Response

{response}

## Gate Results

| Gate | Status | Evidence |
|---|---|---|
| Activation | Pass | {evidence} |
| Intent reconstruction | Pass | {evidence} |
| Owner recommendation | Pass | {evidence} |
| Context/evidence handling | Pass | {evidence} |
| Risk/challenge quality | Pass | {evidence} |
| Output usefulness | Pass | {evidence} |

## Failure Tags

- None.

## Fix Recommendation

None.
"""


def run_self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    case_name = sorted(eval_case_names(root))[0]
    valid_response = (
        "The captured response reconstructs intent, names a default recommendation, "
        "handles evidence boundaries, states a concrete risk, and gives a usable next step."
    )
    valid_evidence = "Concrete response behavior is cited here."

    with tempfile.TemporaryDirectory(prefix="converge-response-eval-selftest-") as tmp:
        valid_dir = Path(tmp) / "valid"
        valid_dir.mkdir()
        (valid_dir / "valid.result.md").write_text(
            sample_result(
                case_name,
                evaluator="manual-review",
                model_host="codex-real-host",
                response=valid_response,
                evidence=valid_evidence,
            ),
            encoding="utf-8",
        )
        valid_errors = run_checks(valid_dir, root, require_real_results=True)
        if valid_errors:
            errors.append("self-test valid result unexpectedly failed: " + "; ".join(valid_errors[:3]))

        synthetic_dir = Path(tmp) / "synthetic"
        synthetic_dir.mkdir()
        (synthetic_dir / "synthetic.result.md").write_text(
            sample_result(
                case_name,
                evaluator="release-smoke",
                model_host="synthetic",
                response=valid_response,
                evidence=valid_evidence,
            ),
            encoding="utf-8",
        )
        synthetic_errors = run_checks(synthetic_dir, root, require_real_results=True)
        if not any("synthetic/stub metadata" in error for error in synthetic_errors):
            errors.append("self-test synthetic result was not rejected")

        weak_dir = Path(tmp) / "weak"
        weak_dir.mkdir()
        (weak_dir / "weak.result.md").write_text(
            sample_result(
                case_name,
                evaluator="manual-review",
                model_host="codex-real-host",
                response="[Paste the model response exactly or link a response artifact.]",
                evidence="ok",
            ),
            encoding="utf-8",
        )
        weak_errors = run_checks(weak_dir, root, require_real_results=True)
        if not any("placeholder" in error or "evidence is too weak" in error for error in weak_errors):
            errors.append("self-test weak/placeholder result was not rejected")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", type=Path, nargs="?")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-all-cases", action="store_true")
    parser.add_argument("--require-real-results", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test(args.root)
        print("Converge response-eval validator self-test")
        if errors:
            print("Self-test failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Self-test passed.")
        return 0

    if args.results_dir is None:
        parser.error("results_dir is required unless --self-test is used")

    records = [result_record(result) for result in result_files(args.results_dir)] if args.results_dir.is_dir() else []
    errors = run_checks(
        args.results_dir,
        args.root,
        require_all_cases=args.require_all_cases,
        require_real_results=args.require_real_results,
    )
    print(f"Checked response-eval results in {args.results_dir}")
    print(summary(records, args.root, args.require_all_cases, args.require_real_results))
    if errors:
        print("Converge response-eval validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Converge response-eval validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
