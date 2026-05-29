#!/usr/bin/env python3
"""Build H3 native interaction proof collection packets."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from typing import Any

from host_adapter_registry import host_entries


ROOT = Path(__file__).resolve().parents[1]
NATIVE_CASES = {
    "codex-plan-native-question-ui.md",
    "claude-native-question-bridge.md",
    "cursor-native-question-bridge.md",
}


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


def host_proof(host: dict[str, Any]) -> dict[str, str]:
    proof = host.get("proof", {})
    if not isinstance(proof, dict):
        return {}
    return {key: str(value) for key, value in proof.items()}


def host_interaction(host: dict[str, Any]) -> dict[str, Any]:
    interaction = host.get("interaction", {})
    return interaction if isinstance(interaction, dict) else {}


def selected_hosts(root: Path, host_id: str | None) -> list[dict[str, Any]]:
    hosts = []
    for host in host_entries(root):
        proof = host_proof(host)
        if proof.get("eval_case") not in NATIVE_CASES:
            continue
        if host_id and host.get("host_id") != host_id:
            continue
        hosts.append(host)
    if host_id and not hosts:
        raise ValueError(f"no native proof host found for {host_id}")
    return hosts


def prompt_packet(root: Path, host: dict[str, Any]) -> str:
    proof = host_proof(host)
    interaction = host_interaction(host)
    case_name = proof["eval_case"]
    case_path = root / "eval-cases" / case_name
    case_text = case_path.read_text(encoding="utf-8")
    user_prompt = first_fenced_block(section_after(case_text, "## User Prompt"))
    native_tool = interaction.get("native_question_tool") or "host-native question surface"
    return f"""# Converge H3 Native Proof Prompt - {host["host_id"]}

This prompt is for a real interactive host run. Do not use CLI/headless print mode for H3 proof.

## Host Under Test

- Host ID: `{host["host_id"]}`
- Host name: {host["display_name"]}
- Expected native surface: {interaction.get("native_question_surface", "")}
- Expected native tool/UI: {native_tool}
- Eval case: `{case_name}`

## User Prompt To Send

```text
{user_prompt}
```

## Collection Requirements

- The native question surface must be visible/callable in the active host context.
- Converge must use the native question UI/tool, not a Markdown fallback.
- The recommended default must be first or explicitly visible.
- A free-form escape hatch must exist, either host-provided or explicitly offered.
- After the first clarification, Converge must continue to a concrete answer, plan, or artifact.
- Capture a transcript, screenshot, log, or exported conversation link.
"""


def proof_template(host: dict[str, Any]) -> str:
    proof = host_proof(host)
    interaction = host_interaction(host)
    case_name = proof["eval_case"]
    expected_tool = interaction.get("native_question_tool")
    data = {
        "protocol_version": "1.0",
        "host_id": host["host_id"],
        "case_name": case_name,
        "proof_tier": "H3",
        "verdict": "Blocked",
        "date": date.today().isoformat(),
        "model_host": "TODO real host name and version",
        "host_mode": "TODO real interactive mode",
        "native_surface_observed": "TODO describe the visible/callable native surface",
        "native_tool_used": expected_tool,
        "prompt_artifact": f"prompts/{Path(case_name).stem}.prompt.md",
        "response_artifact": f"responses/{Path(case_name).stem}.response.md",
        "interaction": {
            "question_count": 0,
            "recommended_default_first": False,
            "freeform_escape_hatch": False,
            "avoided_unrelated_host_tools": False,
            "continued_after_clarification": False,
        },
        "evidence_artifacts": [
            {
                "kind": "transcript",
                "path_or_url": f"evidence/{Path(case_name).stem}.transcript.md",
                "description": "TODO transcript/screenshot/log/export proving native interaction behavior",
            }
        ],
        "claim_allowed": "H3 remains unproven until this proof is reviewed and passes validation.",
        "reviewer": "TODO reviewer",
        "notes": proof.get("h3_boundary", ""),
    }
    return json.dumps(data, indent=2) + "\n"


def runbook(hosts: list[dict[str, Any]], out: Path) -> str:
    rows = "\n".join(
        f"- `{host['host_id']}` -> `{host_proof(host)['eval_case']}`"
        for host in hosts
    )
    return f"""# Converge H3 Native Proof Runbook

This runpack collects H3 proof only. It must not be filled from install checks, product docs, scenario notes, or CLI/headless fallback output.

## Hosts

{rows}

## Procedure

1. Open one file under `prompts/`.
2. Run the prompt in the named real interactive host and mode.
3. Confirm the native question UI/tool is actually visible or callable in that host context.
4. Capture transcript, screenshot, log, or exported conversation evidence under `evidence/`, or use a stable URL.
5. Paste or link the host response under `responses/`.
6. Fill the matching `proofs/*.proof.json`.
7. Keep `verdict` as `Blocked` if the native surface is unavailable; do not convert fallback behavior into H3.
8. Validate from the skill root:

```bash
python3 scripts/check_converge_native_proof.py {out / "proofs"} --require-real-artifacts
```

## Pass Boundary

A passing proof is scoped to one host and one eval case. It does not promote H4 production workflow coverage and does not prove unrelated host-native paths.
"""


def build(root: Path, out: Path, host_id: str | None) -> None:
    hosts = selected_hosts(root, host_id)
    prompts_dir = out / "prompts"
    proofs_dir = out / "proofs"
    responses_dir = out / "responses"
    evidence_dir = out / "evidence"
    for directory in (prompts_dir, proofs_dir, responses_dir, evidence_dir):
        directory.mkdir(parents=True, exist_ok=True)

    manifest_rows = ["host_id\tdisplay_name\teval_case\tnative_question_surface\tnative_question_tool\th3_boundary"]
    for host in hosts:
        proof = host_proof(host)
        interaction = host_interaction(host)
        case_stem = Path(proof["eval_case"]).stem
        (prompts_dir / f"{case_stem}.prompt.md").write_text(prompt_packet(root, host), encoding="utf-8")
        (proofs_dir / f"{case_stem}.proof.json").write_text(proof_template(host), encoding="utf-8")
        (responses_dir / f"{case_stem}.response.md").write_text(
            "# Response Artifact\n\nPaste the exact host response or link an exported artifact here.\n",
            encoding="utf-8",
        )
        (evidence_dir / f"{case_stem}.transcript.md").write_text(
            "# Evidence Artifact\n\nPaste transcript, screenshot notes, log excerpts, or exported conversation links here.\n",
            encoding="utf-8",
        )
        manifest_rows.append(
            "\t".join(
                [
                    str(host["host_id"]),
                    str(host["display_name"]),
                    proof["eval_case"],
                    str(interaction.get("native_question_surface", "")),
                    str(interaction.get("native_question_tool", "")),
                    proof["h3_boundary"],
                ]
            )
        )

    (out / "manifest.tsv").write_text("\n".join(manifest_rows) + "\n", encoding="utf-8")
    (out / "RUNBOOK.md").write_text(runbook(hosts, out), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=Path("/tmp/converge-native-proof"))
    parser.add_argument("--host-id")
    args = parser.parse_args()

    try:
        build(args.root, args.out.expanduser().resolve(), args.host_id)
    except Exception as exc:
        print(f"Converge native proof build failed: {exc}")
        return 1
    print(f"Built native proof runpack in {args.out.expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
