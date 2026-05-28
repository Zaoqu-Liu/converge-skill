#!/usr/bin/env python3
"""Build blind response-eval packets for Converge eval cases."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]


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


def scenario_notes(text: str) -> str:
    user_section = section_after(text, "## User Prompt")
    match = re.search(r"```(?:\w+)?\n.*?\n```", user_section, flags=re.DOTALL)
    if not match:
        return ""
    return user_section[match.end() :].strip()


def provided_artifacts(text: str) -> list[tuple[str, str]]:
    block = section_after(text, "## Provided Artifacts").strip()
    if not block:
        return []
    rows: list[tuple[str, str]] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line.startswith("-"):
            continue
        body = line[1:].strip()
        label = f"artifact-{len(rows) + 1}"
        value = body
        if ":" in body:
            label_part, value = body.split(":", 1)
            label = label_part.strip() or label
        match = re.search(r"`([^`]+)`", value)
        artifact_path = match.group(1).strip() if match else value.strip()
        if artifact_path:
            rows.append((label, artifact_path))
    return rows


def copy_artifacts(
    root: Path,
    out: Path,
    case: Path,
    artifact_specs: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    copied: list[tuple[str, str]] = []
    if not artifact_specs:
        return copied
    target_dir = out / "artifacts" / case.stem
    target_dir.mkdir(parents=True, exist_ok=True)
    for label, artifact_ref in artifact_specs:
        source = Path(artifact_ref)
        if not source.is_absolute():
            source = root / artifact_ref
        if not source.is_file():
            raise FileNotFoundError(f"{case.name}: provided artifact not found: {source}")
        target = target_dir / source.name
        shutil.copy2(source, target)
        copied.append((label, str(target.relative_to(out))))
    return copied


def case_paths(root: Path, selected: str | None) -> list[Path]:
    eval_dir = root / "eval-cases"
    if selected:
        case = eval_dir / selected
        if not case.suffix:
            case = case.with_suffix(".md")
        if not case.is_file():
            raise FileNotFoundError(f"eval case not found: {case}")
        return [case]
    return sorted(eval_dir.glob("*.md"))


def prompt_packet(case: Path, skill_path: str, artifact_rows: list[tuple[str, str]]) -> str:
    text = case.read_text(encoding="utf-8")
    user_prompt = first_fenced_block(section_after(text, "## User Prompt"))
    notes = scenario_notes(text)
    notes_section = f"""

## Scenario Notes

{notes}
""" if notes else ""
    artifact_section = ""
    if artifact_rows:
        artifact_lines = "\n".join(f"- {label}: `{path}`" for label, path in artifact_rows)
        artifact_section = f"""

## Provided Artifacts

These files are part of the user's request. Inspect them with available file/image tools before judging the issue.

{artifact_lines}
"""
    return f"""# Converge Blind Eval Prompt - {case.name}

You are the model under test.

Use the Converge skill at:

```text
{skill_path}
```

Important:
- Do not read the eval case file.
- Do not ask for the expected behavior, rubric, or failure tags.
- Answer the user prompt naturally as the active host would allow.
- Use only tools actually available in the host environment.

## User Prompt

```text
{user_prompt}
```{notes_section}{artifact_section}
"""


def result_template(case: Path, prompt_rel: str, skill_path: str) -> str:
    today = date.today().isoformat()
    return f"""# Converge Response Eval Result - {case.stem}

## Metadata

- Case: {case.name}
- Verdict: TODO
- Evaluator:
- Model/Host:
- Date: {today}
- Skill Path: {skill_path}
- Response Artifact: inline or [path/link]

## Prompt Given

{prompt_rel}

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


def runbook(
    out: Path,
    manifest_rows: list[str],
    skill_path: str,
    with_result_stubs: bool,
    selected: str | None,
) -> str:
    case_count = len(manifest_rows)
    results_note = (
        "Result stubs were generated in `results/`; fill every stub after collecting the model response."
        if with_result_stubs
        else "Result stubs were not generated; create result files from the templates in `reviews/`."
    )
    scope = selected or "all eval cases"
    return f"""# Converge Response Eval Runbook

Generated for: `{scope}`

## Purpose

This runpack tests whether Converge behavior works in a real host/model response, not just whether the skill files validate structurally.

## Contents

- Cases: {case_count}
- Skill under test: `{skill_path}`
- Manifest: `manifest.tsv`
- Blind prompts: `prompts/`
- Review packets: `reviews/`
- Results: `results/` when generated

{results_note}

## Procedure

1. Open `manifest.tsv` or choose a smaller batch with:

```bash
python3 scripts/select_converge_response_eval_batch.py --mode pilot --max-cases 10 --runpack {out}
```

2. Send only the matching `prompts/*.prompt.md` content to the model under test.
3. Do not show the model the eval case, expected behavior, rubric, review packet, or prior conclusions.
4. Paste the exact model answer into the matching `results/*.result.md` file, or link a response artifact there.
5. Open the matching `reviews/*.review.md` packet and judge the answer against the expected behavior and rubric.
6. For skill changes, keep the affected case separate from at least one unrelated holdout/regression case before accepting the patch.
7. Set `Verdict` to `Pass` or `Fail`.
8. Fill every gate row with `Pass`, `Fail`, `N/A`, `Blocked`, or `Conditional`, plus concrete evidence.
9. Use `- None.` for passing Failure Tags; for failures, list only tags from `eval-rubric.md`.
10. For every failure, write the smallest skill change that would prevent recurrence.
11. After partial progress, select the next coverage batch if needed:

```bash
python3 scripts/select_converge_response_eval_batch.py --mode next-cover --results-dir {out / "results"} --require-real-results --runpack {out}
```

12. Run the progress summary while filling results:

```bash
python3 scripts/summarize_converge_response_eval.py {out / "results"} --require-real-results --show-axes
```

13. Run the validator from the skill root:

```bash
python3 scripts/check_converge_response_eval.py {out / "results"} --require-all-cases --require-real-results
```

## Release Gate

After all cases are filled and pass the response-eval validator, include the real results in the release check:

```bash
python3 scripts/check_converge_release.py --response-results-dir {out / "results"} --require-response-results
```

Do not claim behavior-level proof from generated stubs, synthetic smoke results, or partial case coverage.
"""


def review_packet(case: Path, rubric: str, prompt_rel: str, result_rel: str | None) -> str:
    text = case.read_text(encoding="utf-8")
    expected = section_after(text, "## Expected Behavior").strip()
    tags = section_after(text, "## Failure Tags").strip()
    result_note = result_rel or "Create a result file from the template below."
    return f"""# Converge Response Review Packet - {case.name}

Use this packet after the model under test has answered the blind prompt.

Blind prompt packet:

```text
{prompt_rel}
```

Result file:

```text
{result_note}
```

## Expected Behavior

{expected}

## Case Failure Tags

{tags}

## Rubric

{rubric.strip()}

## Result File Template

```markdown
{result_template(case, prompt_rel, "[skill path used in blind prompt]").strip()}
```
"""


def build(root: Path, out: Path, selected: str | None, skill_path: str, with_result_stubs: bool) -> list[str]:
    if out.exists():
        shutil.rmtree(out)
    prompt_dir = out / "prompts"
    review_dir = out / "reviews"
    results_dir = out / "results"
    prompt_dir.mkdir(parents=True)
    review_dir.mkdir(parents=True)
    if with_result_stubs:
        results_dir.mkdir(parents=True)
    rubric = (root / "eval-rubric.md").read_text(encoding="utf-8")

    columns = ["case", "prompt_packet", "review_packet"]
    if with_result_stubs:
        columns.append("result_stub")
    manifest = ["\t".join(columns)]
    for case in case_paths(root, selected):
        prompt_file = prompt_dir / f"{case.stem}.prompt.md"
        review_file = review_dir / f"{case.stem}.review.md"
        prompt_rel = str(prompt_file.relative_to(out))
        result_rel = None
        if with_result_stubs:
            result_file = results_dir / f"{case.stem}.result.md"
            result_file.write_text(result_template(case, prompt_rel, skill_path), encoding="utf-8")
            result_rel = str(result_file.relative_to(out))
        artifact_specs = provided_artifacts(case.read_text(encoding="utf-8"))
        artifact_rows = copy_artifacts(root, out, case, artifact_specs)
        prompt_file.write_text(prompt_packet(case, skill_path, artifact_rows), encoding="utf-8")
        review_file.write_text(review_packet(case, rubric, prompt_rel, result_rel), encoding="utf-8")
        row = [case.name, prompt_rel, str(review_file.relative_to(out))]
        if result_rel:
            row.append(result_rel)
        manifest.append("\t".join(row))

    rows = manifest[1:]
    (out / "manifest.tsv").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    (out / "RUNBOOK.md").write_text(
        runbook(out, rows, skill_path, with_result_stubs, selected),
        encoding="utf-8",
    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--case", help="Eval case filename or stem. Defaults to all cases.")
    parser.add_argument("--skill-path", default=str(ROOT / "SKILL.md"))
    parser.add_argument("--with-result-stubs", action="store_true")
    args = parser.parse_args()

    built = build(args.root, args.out, args.case, args.skill_path, args.with_result_stubs)
    print(f"Built {len(built)} response-eval packet(s) in {args.out}")
    print(f"Runbook is at {args.out / 'RUNBOOK.md'}")
    if args.with_result_stubs:
        print(f"Result stubs are in {args.out / 'results'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
