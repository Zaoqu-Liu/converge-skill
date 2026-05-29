"""Host adapter registry helpers for the Converge Protocol CLI."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "converge"
REGISTRY_PATH = SKILL_ROOT / "host-adapters.json"
HOST_CONTRACT = SKILL_ROOT / "host-capability-contract.tsv"
PROOF_TIER_RE = re.compile(r"^H[0-4]\b")


@dataclass(frozen=True)
class HostDoctor:
    host_id: str
    display_name: str
    current_claim: str
    proof_tier: str
    install_anchor: str
    installed: bool
    missing_install_evidence: list[str]
    native_question_surface: str
    fallback_surface: str
    eval_case: str
    h3_boundary: str


def load_host_registry(skill_root: Path = SKILL_ROOT) -> dict[str, Any]:
    path = skill_root / "host-adapters.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def host_entries(registry: dict[str, Any]) -> list[dict[str, Any]]:
    hosts = registry.get("hosts")
    if not isinstance(hosts, list):
        raise ValueError("host-adapters.json: hosts must be a list")
    return [host for host in hosts if isinstance(host, dict)]


def proof_tier(current_claim: str) -> str:
    return current_claim.split(maxsplit=1)[0]


def expand_path(value: str) -> Path:
    return Path(value).expanduser()


def has_skill_at(path: Path) -> bool:
    return (path / "SKILL.md").is_file() if path.is_dir() else path.is_file()


def bridge_file_path(bridge: dict[str, Any]) -> str:
    value = bridge.get("path")
    if not isinstance(value, str):
        return ""
    return value


def install_evidence(host: dict[str, Any]) -> tuple[bool, list[str]]:
    install = host.get("install", {})
    if not isinstance(install, dict):
        return False, ["install object missing"]

    anchors = [item for item in install.get("anchors", []) if isinstance(item, str)]
    bridges = [item for item in install.get("bridge_files", []) if isinstance(item, dict)]
    required_bridges = [item for item in bridges if item.get("required_for_h1") is True]
    missing: list[str] = []

    anchor_ok = False
    if anchors:
        anchor_ok = any(has_skill_at(expand_path(anchor)) for anchor in anchors)
        if not anchor_ok:
            missing.append("missing skill anchor: " + " or ".join(anchors))

    bridge_ok = True
    for bridge in required_bridges:
        path_value = bridge_file_path(bridge)
        if not path_value or not expand_path(path_value).is_file():
            bridge_ok = False
            missing.append(f"missing bridge file: {path_value or '<unknown>'}")

    if not anchors and not required_bridges:
        return False, ["no local install surface claimed"]
    return anchor_ok and bridge_ok, missing


def doctor_rows(skill_root: Path = SKILL_ROOT) -> list[HostDoctor]:
    registry = load_host_registry(skill_root)
    rows: list[HostDoctor] = []
    for host in host_entries(registry):
        proof = host.get("proof", {})
        install = host.get("install", {})
        interaction = host.get("interaction", {})
        if not isinstance(proof, dict) or not isinstance(install, dict) or not isinstance(interaction, dict):
            continue
        current_claim = str(proof.get("current_claim", "H0 undocumented"))
        installed, missing = install_evidence(host)
        rows.append(
            HostDoctor(
                host_id=str(host.get("host_id", "")),
                display_name=str(host.get("display_name", "")),
                current_claim=current_claim,
                proof_tier=proof_tier(current_claim),
                install_anchor=str(install.get("anchor_label", "")),
                installed=installed,
                missing_install_evidence=missing,
                native_question_surface=str(interaction.get("native_question_surface", "")),
                fallback_surface=str(interaction.get("fallback_surface", "")),
                eval_case=str(proof.get("eval_case", "")),
                h3_boundary=str(proof.get("h3_boundary", "")),
            )
        )
    return rows


def contract_rows() -> list[dict[str, str]]:
    with HOST_CONTRACT.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def registry_contract_row(host: dict[str, Any]) -> dict[str, str]:
    install = host.get("install", {})
    interaction = host.get("interaction", {})
    proof = host.get("proof", {})
    if not isinstance(install, dict) or not isinstance(interaction, dict) or not isinstance(proof, dict):
        return {}
    return {
        "host_id": str(host.get("host_id", "")),
        "display_name": str(host.get("display_name", "")),
        "source_anchor": str(host.get("source_anchor", "")),
        "install_anchor": str(install.get("anchor_label", "")),
        "native_question_surface": str(interaction.get("native_question_surface", "")),
        "fallback_surface": str(interaction.get("fallback_surface", "")),
        "current_claim": str(proof.get("current_claim", "")),
        "eval_case": str(proof.get("eval_case", "")),
        "h3_boundary": str(proof.get("h3_boundary", "")),
    }


def validate_registry(skill_root: Path = SKILL_ROOT) -> list[str]:
    errors: list[str] = []
    path = skill_root / "host-adapters.json"
    if not path.is_file():
        return [f"missing host adapter registry: {path.relative_to(ROOT)}"]

    try:
        registry = load_host_registry(skill_root)
    except Exception as exc:
        return [f"host-adapters.json failed to load: {exc}"]

    if registry.get("protocol_version") != "1.0":
        errors.append("host-adapters.json protocol_version must be 1.0")
    if not isinstance(registry.get("registry_version"), str):
        errors.append("host-adapters.json registry_version must be a string")

    proof_tiers = registry.get("proof_tiers", {})
    if not isinstance(proof_tiers, dict):
        errors.append("host-adapters.json proof_tiers must be an object")
        proof_tiers = {}
    for tier in ("H0", "H1", "H2", "H3", "H4"):
        if tier not in proof_tiers:
            errors.append(f"host-adapters.json missing proof tier: {tier}")

    try:
        hosts = host_entries(registry)
    except ValueError as exc:
        return errors + [str(exc)]

    if len(hosts) < 10:
        errors.append("host-adapters.json should cover mainstream hosts")
    seen: set[str] = set()
    eval_cases = {case.name for case in (skill_root / "eval-cases").glob("*.md")}
    source_evidence = (skill_root / "host-source-evidence.md").read_text(encoding="utf-8")
    contract_by_host = {row["host_id"]: row for row in contract_rows()}

    for host in hosts:
        host_id = str(host.get("host_id", ""))
        if not host_id:
            errors.append("host-adapters.json host missing host_id")
            continue
        if host_id in seen:
            errors.append(f"host-adapters.json duplicate host_id: {host_id}")
        seen.add(host_id)

        for key in ("display_name", "source_anchor", "instruction_surfaces", "install", "interaction", "proof"):
            if key not in host:
                errors.append(f"host-adapters.json {host_id} missing {key}")

        source_anchor = str(host.get("source_anchor", ""))
        if source_anchor != "none" and source_anchor not in source_evidence:
            errors.append(f"host-adapters.json {host_id} source_anchor not in host-source-evidence.md")

        install = host.get("install", {})
        interaction = host.get("interaction", {})
        proof = host.get("proof", {})
        if not isinstance(install, dict) or not isinstance(interaction, dict) or not isinstance(proof, dict):
            errors.append(f"host-adapters.json {host_id} install/interaction/proof must be objects")
            continue

        current_claim = str(proof.get("current_claim", ""))
        tier = proof_tier(current_claim)
        if not PROOF_TIER_RE.match(current_claim):
            errors.append(f"host-adapters.json {host_id} current_claim must start with H0-H4")
        elif tier not in proof_tiers:
            errors.append(f"host-adapters.json {host_id} references unknown proof tier: {tier}")

        eval_case = str(proof.get("eval_case", ""))
        if eval_case not in eval_cases:
            errors.append(f"host-adapters.json {host_id} eval_case missing: {eval_case}")

        if install.get("copy_skill") is True:
            anchors = install.get("anchors")
            target_key = install.get("target_key")
            if not isinstance(target_key, str) or not target_key:
                errors.append(f"host-adapters.json {host_id} copy_skill requires target_key")
            if not isinstance(anchors, list) or not anchors:
                errors.append(f"host-adapters.json {host_id} copy_skill requires anchors")

        contract_row = contract_by_host.get(host_id)
        if contract_row is None:
            errors.append(f"host-capability-contract.tsv missing host from registry: {host_id}")
        else:
            derived = registry_contract_row(host)
            for key, expected in derived.items():
                actual = contract_row.get(key, "")
                if actual != expected:
                    errors.append(
                        f"host-capability-contract.tsv drift for {host_id}.{key}: "
                        f"expected {expected!r}, got {actual!r}"
                    )

    contract_hosts = set(contract_by_host)
    registry_hosts = {str(host.get("host_id", "")) for host in hosts}
    for host_id in sorted(contract_hosts - registry_hosts):
        errors.append(f"host-adapters.json missing TSV host: {host_id}")

    return errors
