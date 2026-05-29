#!/usr/bin/env python3
"""Build an IntentBench runpack from the Converge eval suite."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parent.parent
MANIFEST_PATH = REPO_ROOT / "intentbench" / "manifest.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def section_after(text: str, heading: str) -> str:
    if heading not in text:
        return ""
    tail = text.split(heading, 1)[1]
    next_heading = re.search(r"\n## ", tail)
    if next_heading:
        return tail[: next_heading.start()]
    return tail


def first_fenced_block(text: str) -> str:
    match = re.search(r"```(?:\w+)?\n(.*?)\n```", text, flags=re.DOTALL)
    if not match:
        raise ValueError("User Prompt section has no fenced prompt")
    return match.group(1).strip()


def parse_coverage(path: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines()[1:]:
        if not raw_line.strip() or raw_line.startswith("#"):
            continue
        parts = raw_line.split("\t")
        if len(parts) == 3:
            rows.append(tuple(part.strip() for part in parts))
    return rows


def coverage_by_case(rows: list[tuple[str, str, str]]) -> dict[str, dict[str, list[str]]]:
    index: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for case_name, axis, value in rows:
        index[case_name][axis].append(value)
    return index


def coverage_index(rows: list[tuple[str, str, str]]) -> dict[str, dict[str, set[str]]]:
    index: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for case_name, axis, value in rows:
        index[axis][value].add(case_name)
    return index


def case_tags(case_path: Path) -> list[str]:
    tags: list[str] = []
    for raw_line in section_after(case_path.read_text(encoding="utf-8"), "## Failure Tags").splitlines():
        line = raw_line.strip()
        match = re.match(r"^- `([^`]+)`\s*$", line)
        if match:
            tags.append(match.group(1))
    return tags


def selected_cases(manifest: dict[str, Any], rows: list[tuple[str, str, str]], suite_id: str) -> list[str]:
    case_dir = REPO_ROOT / str(manifest["case_source"])
    all_cases = {path.name for path in case_dir.glob("*.md")}
    if suite_id == "core":
        return sorted(all_cases)
    suites = {
        suite["suite_id"]: suite
        for suite in manifest.get("suites", [])
        if isinstance(suite, dict) and "suite_id" in suite
    }
    if suite_id not in suites:
        raise ValueError(f"unknown IntentBench suite: {suite_id}")
    selector = suites[suite_id].get("selector", {})
    if not isinstance(selector, dict):
        raise ValueError(f"suite {suite_id} selector must be an object")
    axis = selector.get("axis")
    values = selector.get("values")
    if axis == "*" and values == ["*"]:
        return sorted(all_cases)
    if not isinstance(axis, str) or not isinstance(values, list):
        raise ValueError(f"suite {suite_id} selector must define axis and values")
    index = coverage_index(rows)
    selected: set[str] = set()
    for value in values:
        if isinstance(value, str):
            selected.update(index.get(axis, {}).get(value, set()))
    return sorted(selected)


def prompt_packet(case_path: Path, skill_path: str, manifest: dict[str, Any]) -> str:
    text = case_path.read_text(encoding="utf-8")
    user_prompt = first_fenced_block(section_after(text, "## User Prompt"))
    return f"""# IntentBench Blind Prompt - {case_path.name}

You are the model under test.

Use the Converge skill at:

```text
{skill_path}
```

Benchmark: {manifest["name"]} ({manifest["benchmark_id"]} {manifest["benchmark_version"]})

Important:
- Do not read the eval case file.
- Do not ask for the expected behavior, rubric, review packet, failure tags, or scoring logic.
- Answer the user prompt naturally as the active host would allow.
- Use only tools actually available in the host environment.

## User Prompt

```text
{user_prompt}
```
"""


def review_packet(case_path: Path) -> str:
    text = case_path.read_text(encoding="utf-8")
    return f"""# IntentBench Review Packet - {case_path.name}

Use this packet only after the model response is captured.

## Expected Behavior

{section_after(text, "## Expected Behavior").strip()}

## Failure Tags

{section_after(text, "## Failure Tags").strip()}
"""


def result_stub(case_name: str, skill_path: str) -> str:
    stem = Path(case_name).stem
    return f"""# Converge Response Eval Result - {stem}

## Metadata

- Case: {case_name}
- Verdict: TODO
- Evaluator:
- Model/Host:
- Date:
- Skill Path: {skill_path}
- Response Artifact: responses/{stem}.response.md

## Prompt Given

prompts/{stem}.prompt.md

## Response

[Paste the model response exactly or link a response artifact.]

## Gate Results

| Gate | Status | Evidence |
|---|---|---|
| Activation | Pass/Fail/N/A | Cite concrete response behavior. |
| Intent reconstruction | Pass/Fail/N/A | Cite concrete response behavior. |
| Owner recommendation | Pass/Fail/N/A | Cite concrete response behavior. |
| Context/evidence handling | Pass/Fail/N/A | Cite concrete response behavior. |
| Risk/challenge quality | Pass/Fail/N/A | Cite concrete response behavior. |
| Output usefulness | Pass/Fail/N/A | Cite concrete response behavior. |

## Failure Tags

- `tag-if-failed`

## Fix Recommendation

[Smallest skill change that would prevent the failure. Use "None." for pass.]
"""


def build_manifest(
    manifest: dict[str, Any],
    cases: list[str],
    rows_by_case: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    return {
        "benchmark_id": manifest["benchmark_id"],
        "benchmark_version": manifest["benchmark_version"],
        "protocol_version": manifest["protocol_version"],
        "case_count": len(cases),
        "cases": [
            {
                "case": case_name,
                "coverage": rows_by_case.get(case_name, {}),
            }
            for case_name in cases
        ],
        "scoring": manifest["scoring"],
    }


def runbook(out: Path, suite_id: str, case_count: int) -> str:
    return f"""# IntentBench Runbook

Suite: `{suite_id}`
Cases: {case_count}

## Procedure

1. Send only the matching file from `prompts/` to the model or host under test.
2. Save the exact answer under `responses/` or paste it into the matching result file.
3. Open the matching `reviews/` packet and judge pass/fail against expected behavior.
4. Fill `results/*.result.md` with concrete gate evidence.
5. Validate and summarize from the repository root:

```bash
python3 -m converge eval --results {out / "results"} --require-real-results
python3 -m converge benchmark --results {out / "results"} --require-real-results
```

For a full benchmark claim, every case in this runpack must be a valid real result with `Verdict: Pass`.
"""


def build(
    manifest_path: Path,
    out: Path,
    suite_id: str,
    skill_path: str,
    with_result_stubs: bool,
) -> None:
    manifest = load_json(manifest_path)
    coverage_rows = parse_coverage(REPO_ROOT / str(manifest["coverage_source"]))
    rows_by_case = coverage_by_case(coverage_rows)
    cases = selected_cases(manifest, coverage_rows, suite_id)
    case_dir = REPO_ROOT / str(manifest["case_source"])

    if out.exists():
        shutil.rmtree(out)
    for directory in ("prompts", "reviews", "responses", "results"):
        (out / directory).mkdir(parents=True, exist_ok=True)

    manifest_out = build_manifest(manifest, cases, rows_by_case)
    (out / "manifest.json").write_text(json.dumps(manifest_out, indent=2) + "\n", encoding="utf-8")
    case_lines = ["case\tfailure_tags\tcoverage"]
    for case_name in cases:
        case_path = case_dir / case_name
        stem = Path(case_name).stem
        (out / "prompts" / f"{stem}.prompt.md").write_text(prompt_packet(case_path, skill_path, manifest), encoding="utf-8")
        (out / "reviews" / f"{stem}.review.md").write_text(review_packet(case_path), encoding="utf-8")
        (out / "responses" / f"{stem}.response.md").write_text(
            "# Response Artifact\n\nPaste the exact model response or link an exported artifact here.\n",
            encoding="utf-8",
        )
        if with_result_stubs:
            (out / "results" / f"{stem}.result.md").write_text(result_stub(case_name, skill_path), encoding="utf-8")
        tags = ",".join(case_tags(case_path))
        coverage = ";".join(
            f"{axis}={','.join(values)}"
            for axis, values in sorted(rows_by_case.get(case_name, {}).items())
        )
        case_lines.append(f"{case_name}\t{tags}\t{coverage}")
    (out / "cases.tsv").write_text("\n".join(case_lines) + "\n", encoding="utf-8")
    (out / "RUNBOOK.md").write_text(runbook(out, suite_id, len(cases)), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--out", type=Path, default=Path("/tmp/intentbench"))
    parser.add_argument("--suite", default="core")
    parser.add_argument("--skill-path", default=str(SKILL_ROOT / "SKILL.md"))
    parser.add_argument("--with-result-stubs", action="store_true")
    args = parser.parse_args()

    try:
        build(
            args.manifest,
            args.out.expanduser().resolve(),
            args.suite,
            args.skill_path,
            args.with_result_stubs,
        )
    except Exception as exc:
        print(f"IntentBench build failed: {exc}")
        return 1
    print(f"Built IntentBench runpack in {args.out.expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
