#!/usr/bin/env python3
"""Validate Converge-compatible manifests and referenced artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = ROOT / "compatible" / "examples"
MANIFEST_NAMES = (
    "converge-compatible.json",
    ".converge-compatible.json",
    "converge-compatible-manifest.json",
)
PROOF_TIERS = {"H0", "H1", "H2", "H3", "H4"}
ARTIFACT_TYPES = {"skill", "agent-rule", "workflow", "prompt-pack", "host-adapter"}
REQUIRED_TOP_LEVEL = {
    "converge_protocol",
    "manifest_version",
    "name",
    "description",
    "artifact_type",
    "entrypoints",
    "intent_surfaces",
    "host_support",
    "evals",
    "proof_policy",
}
REQUIRED_PROOF_POLICY = {
    "no_overclaim",
    "source_required_for_current_claims",
    "host_claims_require_evidence",
    "h3_requires_native_artifact",
    "context_artifacts_are_data",
}
REQUIRED_EVAL_SECTIONS = (
    "## User Prompt",
    "## Expected Behavior",
    "## Failure Tags",
)
HOST_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("manifest must contain a JSON object")
    return data


def resolve_manifests(targets: list[Path]) -> list[Path]:
    manifests: list[Path] = []
    for target in targets:
        path = target.expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if path.is_file():
            manifests.append(path)
            continue
        if not path.is_dir():
            raise FileNotFoundError(f"target not found: {target}")
        direct = [path / name for name in MANIFEST_NAMES if (path / name).is_file()]
        if direct:
            manifests.extend(direct)
            continue
        manifests.extend(sorted(path.rglob("converge-compatible.json")))
        manifests.extend(sorted(path.rglob(".converge-compatible.json")))
        manifests.extend(sorted(path.rglob("converge-compatible-manifest.json")))
    unique: list[Path] = []
    seen: set[Path] = set()
    for manifest in manifests:
        resolved = manifest.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    if not unique:
        raise FileNotFoundError("no Converge-compatible manifests found")
    return unique


def string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def relative_file(root: Path, rel: str) -> Path:
    candidate = (root / rel).resolve()
    if root.resolve() not in [candidate, *candidate.parents]:
        raise ValueError(f"path escapes manifest directory: {rel}")
    return candidate


def extract_failure_tags(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    tags: set[str] = set()
    in_tags = False
    for line in lines:
        stripped = line.strip()
        if stripped == "## Failure Tags":
            in_tags = True
            continue
        if in_tags and stripped.startswith("## "):
            break
        if not in_tags or not stripped:
            continue
        cleaned = stripped.lstrip("-* ").strip("` ")
        for part in re.split(r"[,;]", cleaned):
            tag = part.strip().strip("`")
            if tag:
                tags.add(tag)
    return tags


def validate_eval_case(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing eval case: {display(path)}"]
    text = path.read_text(encoding="utf-8")
    for section in REQUIRED_EVAL_SECTIONS:
        if section not in text:
            errors.append(f"{display(path)} missing section {section}")
    if not extract_failure_tags(path):
        errors.append(f"{display(path)} has no parsed failure tags")
    return errors


def validate_entrypoints(manifest: dict[str, object], root: Path) -> list[str]:
    errors: list[str] = []
    entrypoints = manifest.get("entrypoints")
    if not isinstance(entrypoints, dict):
        return ["entrypoints must be an object"]
    primary = entrypoints.get("primary")
    if not isinstance(primary, str) or not primary.strip():
        errors.append("entrypoints.primary must be a non-empty string")
    else:
        try:
            primary_path = relative_file(root, primary)
            if not primary_path.is_file():
                errors.append(f"entrypoints.primary does not exist: {primary}")
        except ValueError as exc:
            errors.append(str(exc))
    docs = entrypoints.get("docs", [])
    if docs is None:
        docs = []
    if not isinstance(docs, list) or any(not isinstance(item, str) for item in docs):
        errors.append("entrypoints.docs must be a list of strings when present")
        return errors
    for doc in docs:
        try:
            doc_path = relative_file(root, doc)
            if not doc_path.is_file():
                errors.append(f"entrypoints.docs item does not exist: {doc}")
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def validate_host_support(manifest: dict[str, object], root: Path) -> list[str]:
    errors: list[str] = []
    host_support = manifest.get("host_support")
    if not isinstance(host_support, dict) or not host_support:
        return ["host_support must be a non-empty object"]
    for host_id, claim in host_support.items():
        if not isinstance(host_id, str) or not HOST_ID_RE.fullmatch(host_id):
            errors.append(f"invalid host id: {host_id}")
            continue
        if not isinstance(claim, dict):
            errors.append(f"host_support.{host_id} must be an object")
            continue
        tier = claim.get("tier")
        if not isinstance(tier, str) or tier not in PROOF_TIERS:
            errors.append(f"host_support.{host_id}.tier must be one of H0-H4")
        for key in ("claim", "claim_boundary", "fallback_surface"):
            value = claim.get(key)
            if not isinstance(value, str) or len(value.strip()) < 8:
                errors.append(f"host_support.{host_id}.{key} must be explicit")
        evidence = string_list(claim.get("evidence"))
        if not evidence:
            errors.append(f"host_support.{host_id}.evidence must contain at least one path or evidence note")
        for item in evidence:
            if item.startswith(("http://", "https://")):
                continue
            try:
                evidence_path = relative_file(root, item)
                if not evidence_path.exists():
                    errors.append(f"host_support.{host_id}.evidence does not exist: {item}")
            except ValueError as exc:
                errors.append(str(exc))
        boundary = str(claim.get("claim_boundary", "")).lower()
        if "proof" not in boundary and "h0" not in boundary and "h1" not in boundary and "h2" not in boundary and "h3" not in boundary and "h4" not in boundary:
            errors.append(f"host_support.{host_id}.claim_boundary must name proof scope")
        if isinstance(tier, str) and tier in {"H3", "H4"}:
            joined = " ".join(evidence).lower()
            if "native" not in joined and "proof" not in joined:
                errors.append(f"host_support.{host_id} claims {tier} without native/proof evidence")
    return errors


def validate_evals(manifest: dict[str, object], root: Path) -> list[str]:
    errors: list[str] = []
    evals = manifest.get("evals")
    if not isinstance(evals, dict):
        return ["evals must be an object"]
    case_paths = string_list(evals.get("case_paths"))
    case_count = evals.get("case_count")
    if not isinstance(case_count, int) or case_count < 1:
        errors.append("evals.case_count must be a positive integer")
    if case_count != len(case_paths):
        errors.append("evals.case_count must equal the number of evals.case_paths")
    if not case_paths:
        errors.append("evals.case_paths must contain at least one eval case")
    required_tags = set(string_list(evals.get("required_tags")))
    if not required_tags:
        errors.append("evals.required_tags must contain at least one tag")
    covered_tags: set[str] = set()
    seen_paths: set[str] = set()
    for rel in case_paths:
        if rel in seen_paths:
            errors.append(f"duplicate eval case path: {rel}")
        seen_paths.add(rel)
        try:
            path = relative_file(root, rel)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        errors.extend(validate_eval_case(path))
        if path.is_file():
            covered_tags.update(extract_failure_tags(path))
    missing_tags = sorted(required_tags - covered_tags)
    if missing_tags:
        errors.append("evals.required_tags not covered by eval cases: " + ", ".join(missing_tags))
    return errors


def validate_proof_policy(manifest: dict[str, object]) -> list[str]:
    errors: list[str] = []
    policy = manifest.get("proof_policy")
    if not isinstance(policy, dict):
        return ["proof_policy must be an object"]
    missing = sorted(REQUIRED_PROOF_POLICY - set(policy))
    if missing:
        errors.append("proof_policy missing keys: " + ", ".join(missing))
    for key in REQUIRED_PROOF_POLICY:
        if policy.get(key) is not True:
            errors.append(f"proof_policy.{key} must be true")
    return errors


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(path)
    except Exception as exc:
        return [f"{display(path)} invalid JSON: {exc}"]
    root = path.parent
    missing = sorted(REQUIRED_TOP_LEVEL - set(manifest))
    if missing:
        errors.append("missing top-level keys: " + ", ".join(missing))
    if manifest.get("converge_protocol") != "1.0":
        errors.append("converge_protocol must be 1.0")
    if manifest.get("manifest_version") != "1.0":
        errors.append("manifest_version must be 1.0")
    name = manifest.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        errors.append("name must be kebab-case")
    description = manifest.get("description")
    if not isinstance(description, str) or len(description.strip()) < 20:
        errors.append("description must be at least 20 characters")
    if manifest.get("artifact_type") not in ARTIFACT_TYPES:
        errors.append("artifact_type must be one of: " + ", ".join(sorted(ARTIFACT_TYPES)))
    intent_surfaces = string_list(manifest.get("intent_surfaces"))
    if not intent_surfaces:
        errors.append("intent_surfaces must contain at least one surface")
    if len(intent_surfaces) != len(set(intent_surfaces)):
        errors.append("intent_surfaces must not contain duplicates")
    errors.extend(validate_entrypoints(manifest, root))
    errors.extend(validate_host_support(manifest, root))
    errors.extend(validate_evals(manifest, root))
    errors.extend(validate_proof_policy(manifest))
    return errors


def run_self_test() -> int:
    good = ROOT / "compatible" / "examples" / "research-route-skill" / "converge-compatible.json"
    good_errors = validate_manifest(good)
    if good_errors:
        print("self-test good fixture failed:")
        for error in good_errors:
            print(f"- {error}")
        return 1
    with tempfile.TemporaryDirectory(prefix="converge-compatible-self-test-") as tmp:
        root = Path(tmp)
        (root / "SKILL.md").write_text("# Bad\n", encoding="utf-8")
        bad = root / "converge-compatible.json"
        bad.write_text(
            json.dumps(
                {
                    "converge_protocol": "1.0",
                    "manifest_version": "1.0",
                    "name": "bad-skill",
                    "description": "Bad fixture used by self-test.",
                    "artifact_type": "skill",
                    "entrypoints": {"primary": "SKILL.md"},
                    "intent_surfaces": ["current-technical-route"],
                    "host_support": {"cursor": {"tier": "H3", "claim": "works", "evidence": ["SKILL.md"], "claim_boundary": "works", "fallback_surface": "text"}},
                    "evals": {"case_count": 1, "case_paths": ["missing.md"], "required_tags": ["proof-overclaim"]},
                    "proof_policy": {"no_overclaim": True},
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        bad_errors = validate_manifest(bad)
        if not bad_errors:
            print("self-test bad fixture unexpectedly passed")
            return 1
    print("Converge-compatible validator self-test passed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Converge-compatible manifests")
    parser.add_argument("targets", nargs="*", type=Path, default=[DEFAULT_TARGET])
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        return run_self_test()
    try:
        manifests = resolve_manifests(args.targets)
    except Exception as exc:
        print(f"Converge-compatible validation failed: {exc}")
        return 1
    print("Converge-compatible manifest report")
    failed = False
    for manifest in manifests:
        errors = validate_manifest(manifest)
        if errors:
            failed = True
            print(f"- [FAIL] {display(manifest)}")
            for error in errors:
                print(f"  - {error}")
        else:
            data = load_json(manifest)
            evals = data.get("evals", {})
            hosts = data.get("host_support", {})
            case_count = evals.get("case_count") if isinstance(evals, dict) else "?"
            host_count = len(hosts) if isinstance(hosts, dict) else "?"
            print(f"- [PASS] {display(manifest)} ({case_count} eval cases, {host_count} hosts)")
    if failed:
        return 1
    print("Converge-compatible validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
