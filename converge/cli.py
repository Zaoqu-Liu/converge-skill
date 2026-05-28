#!/usr/bin/env python3
"""Converge Protocol reference CLI."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "converge"
PROTOCOL_ROOT = ROOT / "protocol"
SCHEMA_ROOT = PROTOCOL_ROOT / "schemas"
EXAMPLE_ROOT = PROTOCOL_ROOT / "examples"
HOST_CONTRACT = SKILL_ROOT / "host-capability-contract.tsv"

REQUIRED_SCHEMAS = {
    "converge-run.schema.json": ["protocol_version", "intent", "context", "decision", "evidence", "interaction", "output", "proof"],
    "host-capability.schema.json": ["protocol_version", "hosts"],
    "eval-result.schema.json": ["protocol_version", "case", "verdict", "host", "evidence", "failure_tags"],
    "converge-compatible-manifest.schema.json": [
        "converge_protocol",
        "name",
        "description",
        "intent_surfaces",
        "host_support",
        "evals",
        "proof_policy",
    ],
}

EXAMPLE_TO_SCHEMA = {
    "converge-run.example.json": "converge-run.schema.json",
    "host-capability.example.json": "host-capability.schema.json",
    "eval-result.example.json": "eval-result.schema.json",
    "converge-compatible-manifest.example.json": "converge-compatible-manifest.schema.json",
}

INSTALL_HOST_IDS = {
    "claude-code",
    "cursor",
    "opencode",
    "cline",
    "antigravity",
}
INSTALL_ALIASES = {
    "codex-default": [Path("~/.agents/skills/converge").expanduser(), Path("~/.codex/skills/converge").expanduser()],
    "codex-plan": [Path("~/.agents/skills/converge").expanduser(), Path("~/.codex/skills/converge").expanduser()],
}


@dataclass(frozen=True)
class HostDoctor:
    host_id: str
    display_name: str
    current_claim: str
    install_anchor: str
    installed: bool
    eval_case: str
    h3_boundary: str


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def validate_required_keys(data: dict[str, object], required: list[str], label: str) -> list[str]:
    return [f"{label}: missing required key {key}" for key in required if key not in data]


def validate_protocol_files() -> list[str]:
    errors: list[str] = []
    for schema_name, required in REQUIRED_SCHEMAS.items():
        path = SCHEMA_ROOT / schema_name
        if not path.is_file():
            errors.append(f"missing schema: {path.relative_to(ROOT)}")
            continue
        schema = load_json(path)
        errors.extend(validate_required_keys(schema, ["$schema", "$id", "title", "type", "required", "properties"], schema_name))
        declared_required = schema.get("required")
        if not isinstance(declared_required, list):
            errors.append(f"{schema_name}: required must be a list")
            continue
        for key in required:
            if key not in declared_required:
                errors.append(f"{schema_name}: required does not include {key}")

    for example_name, schema_name in EXAMPLE_TO_SCHEMA.items():
        path = EXAMPLE_ROOT / example_name
        if not path.is_file():
            errors.append(f"missing example: {path.relative_to(ROOT)}")
            continue
        example = load_json(path)
        required = REQUIRED_SCHEMAS[schema_name]
        errors.extend(validate_required_keys(example, required, example_name))

    rows = read_host_contract()
    if len(rows) < 10:
        errors.append("host capability contract should cover mainstream hosts")
    for row in rows:
        claim = row.get("current_claim", "")
        if not claim.startswith(("H0", "H1", "H2", "H3", "H4")):
            errors.append(f"{row.get('host_id', '<unknown>')}: current_claim must start with H0-H4")
    return errors


def read_host_contract() -> list[dict[str, str]]:
    with HOST_CONTRACT.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def expand_anchor(anchor: str) -> Path | None:
    for fragment in anchor.replace(" or ", " plus ").split(" plus "):
        fragment = fragment.strip()
        if fragment.startswith("~/"):
            return Path(fragment).expanduser()
    return None


def has_installed_skill(path: Path) -> bool:
    return (path / "SKILL.md").is_file() if path.is_dir() else path.is_file()


def doctor_rows() -> list[HostDoctor]:
    rows: list[HostDoctor] = []
    for row in read_host_contract():
        host_id = row["host_id"]
        install_anchor = row["install_anchor"]
        install_path = expand_anchor(install_anchor)
        installed = False
        if install_path is not None:
            installed = has_installed_skill(install_path)
        if not installed:
            installed = any(has_installed_skill(path) for path in INSTALL_ALIASES.get(host_id, []))
        rows.append(
            HostDoctor(
                host_id=host_id,
                display_name=row["display_name"],
                current_claim=row["current_claim"],
                install_anchor=install_anchor,
                installed=installed,
                eval_case=row["eval_case"],
                h3_boundary=row["h3_boundary"],
            )
        )
    return rows


def run(command: list[str]) -> int:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(command, cwd=ROOT, env=env)
    return completed.returncode


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate_protocol_files()
    if errors:
        print("Converge protocol validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Converge protocol validation passed.")
    if args.protocol_only:
        return 0
    return run([sys.executable, str(ROOT / "scripts" / "verify.py")])


def cmd_doctor(args: argparse.Namespace) -> int:
    rows = doctor_rows()
    if args.json:
        print(json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True))
        return 0
    print("Converge host doctor")
    for row in rows:
        marker = "installed" if row.installed else "not-installed"
        print(f"- {row.host_id}: {row.current_claim}; {marker}; eval={row.eval_case}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    command = [sys.executable, str(SKILL_ROOT / "scripts" / "sync_converge_install.py"), "--targets", args.targets]
    if args.dry_run:
        command.append("--dry-run")
    return run(command)


def cmd_pack(args: argparse.Namespace) -> int:
    out_dir = args.out.expanduser().resolve()
    target_dir = out_dir / f"converge-{args.target}"
    if args.dry_run:
        print(f"would pack {SKILL_ROOT} -> {target_dir}")
        return 0
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL_ROOT, target_dir, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", ".git"))
    print(f"packed {target_dir}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    if args.results:
        command = [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "check_converge_response_eval.py"),
            str(args.results),
            "--root",
            str(SKILL_ROOT),
        ]
        if args.require_all_cases:
            command.append("--require-all-cases")
        if args.require_real_results:
            command.append("--require-real-results")
        return run(command)

    out_dir = args.out.expanduser().resolve()
    command = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "build_converge_response_eval.py"),
        "--root",
        str(SKILL_ROOT),
        "--out",
        str(out_dir),
        "--case",
        args.case,
        "--skill-path",
        str(SKILL_ROOT / "SKILL.md"),
    ]
    return run(command)


def cmd_release_check(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "check_converge_release.py"),
        "--source",
        str(SKILL_ROOT),
        "--targets",
        args.targets,
    ]
    if args.skip_installs:
        command.append("--skip-installs")
    return run(command)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="converge", description="Converge Protocol reference CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate protocol files and optionally the repository")
    validate.add_argument("--protocol-only", action="store_true")
    validate.set_defaults(func=cmd_validate)

    doctor = subparsers.add_parser("doctor", help="inspect host install and proof-tier state")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=cmd_doctor)

    install = subparsers.add_parser("install", help="install the skill to supported local hosts")
    install.add_argument("--targets", default="all")
    install.add_argument("--dry-run", action="store_true")
    install.set_defaults(func=cmd_install)

    pack = subparsers.add_parser("pack", help="pack the canonical skill for a target host")
    pack.add_argument("--target", default="generic")
    pack.add_argument("--out", type=Path, default=Path("dist"))
    pack.add_argument("--dry-run", action="store_true")
    pack.set_defaults(func=cmd_pack)

    eval_parser = subparsers.add_parser("eval", help="build or validate response-eval artifacts")
    eval_parser.add_argument("--case", default="low-expression-idea.md")
    eval_parser.add_argument("--out", type=Path, default=Path("/tmp/converge-response-eval"))
    eval_parser.add_argument("--results", type=Path)
    eval_parser.add_argument("--require-all-cases", action="store_true")
    eval_parser.add_argument("--require-real-results", action="store_true")
    eval_parser.set_defaults(func=cmd_eval)

    release_check = subparsers.add_parser("release-check", help="run the release gate")
    release_check.add_argument("--targets", default="all")
    release_check.add_argument("--skip-installs", action="store_true")
    release_check.set_defaults(func=cmd_release_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
