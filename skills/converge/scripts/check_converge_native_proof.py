#!/usr/bin/env python3
"""Validate Converge H3 native interaction proof artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

from host_adapter_registry import host_entries


ROOT = Path(__file__).resolve().parents[1]
NATIVE_CASES = {
    "codex-plan-native-question-ui.md",
    "claude-native-question-bridge.md",
    "cursor-native-question-bridge.md",
}
REQUIRED_TOP_LEVEL = (
    "protocol_version",
    "host_id",
    "case_name",
    "proof_tier",
    "verdict",
    "date",
    "model_host",
    "host_mode",
    "native_surface_observed",
    "native_tool_used",
    "prompt_artifact",
    "response_artifact",
    "interaction",
    "evidence_artifacts",
    "claim_allowed",
    "reviewer",
    "notes",
)
REQUIRED_INTERACTION = (
    "question_count",
    "recommended_default_first",
    "freeform_escape_hatch",
    "avoided_unrelated_host_tools",
    "continued_after_clarification",
)
PLACEHOLDER_TOKENS = {
    "",
    "todo",
    "tbd",
    "placeholder",
    "synthetic",
    "example",
    "stub",
    "unknown",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class ProofRecord:
    path: Path
    host_id: str
    case_name: str
    verdict: str


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def rel_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def host_by_id(root: Path) -> dict[str, dict[str, Any]]:
    return {str(host.get("host_id", "")): host for host in host_entries(root)}


def is_placeholder(value: object) -> bool:
    if value is None:
        return True
    text = str(value).strip().lower()
    return text in PLACEHOLDER_TOKENS or any(token in text for token in ("todo", "placeholder", "synthetic", "stub"))


def local_or_url_exists(path_or_url: str, base_dir: Path) -> bool:
    if path_or_url.startswith(("http://", "https://")):
        return True
    path = Path(path_or_url)
    if not path.is_absolute():
        path = base_dir / path
    return path.is_file()


def host_eval_case(host: dict[str, Any]) -> str:
    proof = host.get("proof", {})
    return str(proof.get("eval_case", "")) if isinstance(proof, dict) else ""


def host_native_tool(host: dict[str, Any]) -> str | None:
    interaction = host.get("interaction", {})
    if not isinstance(interaction, dict):
        return None
    tool = interaction.get("native_question_tool")
    return str(tool) if isinstance(tool, str) and tool else None


def check_proof(path: Path, root: Path = ROOT, require_real_artifacts: bool = False) -> list[str]:
    errors: list[str] = []
    rel = rel_path(path, root)
    try:
        data = load_json(path)
    except Exception as exc:
        return [f"{rel}: invalid JSON proof: {exc}"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"{rel}: missing required key {key}")

    if data.get("protocol_version") != "1.0":
        errors.append(f"{rel}: protocol_version must be 1.0")
    if data.get("proof_tier") != "H3":
        errors.append(f"{rel}: proof_tier must be H3")
    verdict = str(data.get("verdict", ""))
    if verdict not in {"Pass", "Fail", "Blocked"}:
        errors.append(f"{rel}: verdict must be Pass, Fail, or Blocked")
    date_value = str(data.get("date", ""))
    if date_value and not DATE_RE.match(date_value):
        errors.append(f"{rel}: date must use YYYY-MM-DD")

    hosts = host_by_id(root)
    host_id = str(data.get("host_id", ""))
    host = hosts.get(host_id)
    if host is None:
        errors.append(f"{rel}: unknown host_id {host_id!r}")
    else:
        expected_case = host_eval_case(host)
        if data.get("case_name") != expected_case:
            errors.append(f"{rel}: case_name must match registry eval case {expected_case!r}")
        if expected_case not in NATIVE_CASES:
            errors.append(f"{rel}: {expected_case!r} is not an H3 native interaction case")
        expected_tool = host_native_tool(host)
        if verdict == "Pass" and expected_tool and data.get("native_tool_used") != expected_tool:
            errors.append(f"{rel}: native_tool_used must be {expected_tool!r} for a passing H3 proof")

    if data.get("case_name") and not (root / "eval-cases" / str(data["case_name"])).is_file():
        errors.append(f"{rel}: case_name does not exist under eval-cases")

    for key in ("model_host", "host_mode", "native_surface_observed", "prompt_artifact", "response_artifact", "claim_allowed", "reviewer"):
        if is_placeholder(data.get(key)):
            errors.append(f"{rel}: {key} must be concrete, not placeholder/synthetic")

    interaction = data.get("interaction", {})
    if not isinstance(interaction, dict):
        errors.append(f"{rel}: interaction must be an object")
    else:
        for key in REQUIRED_INTERACTION:
            if key not in interaction:
                errors.append(f"{rel}: interaction missing {key}")
        question_count = interaction.get("question_count")
        if not isinstance(question_count, int):
            errors.append(f"{rel}: interaction.question_count must be an integer")
        elif verdict == "Pass" and not 1 <= question_count <= 3:
            errors.append(f"{rel}: passing H3 proof must ask 1-3 native questions")
        for key in REQUIRED_INTERACTION[1:]:
            value = interaction.get(key)
            if not isinstance(value, bool):
                errors.append(f"{rel}: interaction.{key} must be a boolean")
            elif verdict == "Pass" and value is not True:
                errors.append(f"{rel}: passing H3 proof requires interaction.{key}=true")

    artifacts = data.get("evidence_artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        errors.append(f"{rel}: evidence_artifacts must be a non-empty list")
    else:
        for index, artifact in enumerate(artifacts, start=1):
            if not isinstance(artifact, dict):
                errors.append(f"{rel}: evidence_artifacts[{index}] must be an object")
                continue
            for key in ("kind", "path_or_url", "description"):
                if is_placeholder(artifact.get(key)):
                    errors.append(f"{rel}: evidence_artifacts[{index}].{key} must be concrete")
            path_or_url = str(artifact.get("path_or_url", ""))
            if require_real_artifacts and path_or_url and not local_or_url_exists(path_or_url, path.parent):
                errors.append(f"{rel}: evidence artifact not found: {path_or_url}")

    if verdict == "Pass":
        claim = str(data.get("claim_allowed", ""))
        if "H3" not in claim or "native" not in claim.lower():
            errors.append(f"{rel}: passing proof claim_allowed must make a scoped H3 native claim")
    if verdict == "Blocked" and "unproven" not in str(data.get("claim_allowed", "")).lower():
        errors.append(f"{rel}: blocked proof claim_allowed should state H3 remains unproven")
    return errors


def proof_files(proof_dir: Path) -> list[Path]:
    return sorted(proof_dir.glob("*.proof.json"))


def result_record(path: Path) -> ProofRecord:
    data = load_json(path)
    return ProofRecord(
        path=path,
        host_id=str(data.get("host_id", "")),
        case_name=str(data.get("case_name", "")),
        verdict=str(data.get("verdict", "")),
    )


def summary(records: list[ProofRecord]) -> str:
    verdicts = Counter(record.verdict for record in records)
    hosts = sorted({record.host_id for record in records if record.host_id})
    cases = sorted({record.case_name for record in records if record.case_name})
    lines = [
        "Converge native proof report",
        f"- proof files: {len(records)}",
        f"- hosts: {', '.join(hosts) if hosts else 'none'}",
        f"- cases: {', '.join(cases) if cases else 'none'}",
        f"- pass: {verdicts.get('Pass', 0)}",
        f"- fail: {verdicts.get('Fail', 0)}",
        f"- blocked: {verdicts.get('Blocked', 0)}",
    ]
    return "\n".join(lines)


def run_checks(proof_dir: Path, root: Path = ROOT, require_real_artifacts: bool = False) -> list[str]:
    if not proof_dir.is_dir():
        return [f"proof directory not found: {proof_dir}"]
    files = proof_files(proof_dir)
    if not files:
        return [f"no *.proof.json files found in {proof_dir}"]
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    for path in files:
        errors.extend(check_proof(path, root=root, require_real_artifacts=require_real_artifacts))
        try:
            record = result_record(path)
        except Exception:
            continue
        key = (record.host_id, record.case_name)
        if key in seen:
            errors.append(f"{rel_path(path, root)}: duplicate proof for {record.host_id}/{record.case_name}")
        seen.add(key)
    return errors


def sample_proof(base_dir: Path, host_id: str = "cursor", verdict: str = "Pass") -> Path:
    evidence_dir = base_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "cursor-native-question-bridge.transcript.md").write_text(
        "Transcript shows AskQuestion, one recommended option first, free-form escape hatch, and follow-up answer.",
        encoding="utf-8",
    )
    proof_path = base_dir / "cursor-native-question-bridge.proof.json"
    proof_path.write_text(
        json.dumps(
            {
                "protocol_version": "1.0",
                "host_id": host_id,
                "case_name": "cursor-native-question-bridge.md",
                "proof_tier": "H3",
                "verdict": verdict,
                "date": "2026-05-29",
                "model_host": "Cursor Agent interactive",
                "host_mode": "Agent interactive session",
                "native_surface_observed": "AskQuestion was visible in the active tool manifest.",
                "native_tool_used": "AskQuestion",
                "prompt_artifact": "prompts/cursor-native-question-bridge.prompt.md",
                "response_artifact": "responses/cursor-native-question-bridge.response.md",
                "interaction": {
                    "question_count": 1,
                    "recommended_default_first": True,
                    "freeform_escape_hatch": True,
                    "avoided_unrelated_host_tools": True,
                    "continued_after_clarification": True,
                },
                "evidence_artifacts": [
                    {
                        "kind": "transcript",
                        "path_or_url": "evidence/cursor-native-question-bridge.transcript.md",
                        "description": "Transcript with native question UI usage and follow-up behavior.",
                    }
                ],
                "claim_allowed": "Cursor native interactive question path is H3-tested for this case only.",
                "reviewer": "manual-reviewer",
                "notes": "Self-test fixture.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return proof_path


def run_self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="converge-native-proof-selftest-") as tmp:
        valid_dir = Path(tmp) / "valid"
        valid_dir.mkdir()
        sample_proof(valid_dir)
        valid_errors = run_checks(valid_dir, root=root, require_real_artifacts=True)
        if valid_errors:
            errors.append("self-test valid proof unexpectedly failed: " + "; ".join(valid_errors[:3]))

        weak_dir = Path(tmp) / "weak"
        weak_dir.mkdir()
        proof_path = sample_proof(weak_dir)
        data = load_json(proof_path)
        data["native_tool_used"] = "request_user_input"
        data["interaction"]["recommended_default_first"] = False
        proof_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        weak_errors = run_checks(weak_dir, root=root, require_real_artifacts=True)
        if not any("native_tool_used" in error or "recommended_default_first" in error for error in weak_errors):
            errors.append("self-test weak proof was not rejected")

        blocked_dir = Path(tmp) / "blocked"
        blocked_dir.mkdir()
        proof_path = sample_proof(blocked_dir, verdict="Blocked")
        data = load_json(proof_path)
        data["native_tool_used"] = None
        data["interaction"]["question_count"] = 0
        data["claim_allowed"] = "H3 remains unproven; only H1/H2 scoped claims are allowed."
        proof_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        blocked_errors = run_checks(blocked_dir, root=root, require_real_artifacts=True)
        if blocked_errors:
            errors.append("self-test blocked proof unexpectedly failed: " + "; ".join(blocked_errors[:3]))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof_dir", type=Path, nargs="?")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-real-artifacts", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test(args.root)
        print("Converge native proof validator self-test")
        if errors:
            print("Self-test failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Self-test passed.")
        return 0

    if args.proof_dir is None:
        parser.error("proof_dir is required unless --self-test is used")

    files = proof_files(args.proof_dir) if args.proof_dir.is_dir() else []
    records: list[ProofRecord] = []
    for path in files:
        try:
            records.append(result_record(path))
        except Exception:
            continue
    errors = run_checks(args.proof_dir, root=args.root, require_real_artifacts=args.require_real_artifacts)
    print(f"Checked native proof artifacts in {args.proof_dir}")
    print(summary(records))
    if errors:
        print("Converge native proof validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Converge native proof validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
