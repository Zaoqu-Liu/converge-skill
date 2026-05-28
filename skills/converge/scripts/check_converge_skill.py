#!/usr/bin/env python3
"""Validate Converge skill structure and v3 invariants."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "reference.md",
    "examples.md",
    "eval-rubric.md",
    "eval-coverage.tsv",
    "host-adapter-matrix.md",
    "host-capability-contract.tsv",
    "host-source-evidence.md",
    "host-support-ledger.md",
    "eval-artifacts/mixed-artifact-intake/screenshot.txt",
    "eval-artifacts/mixed-artifact-intake/prd.md",
    "eval-artifacts/mixed-artifact-intake/error.log",
    "eval-artifacts/context-poisoning-boundary/SKILL.md",
    "dev-handoff-guide.md",
    "templates/converge-state.md",
    "templates/output-template.md",
    "playbooks/product.md",
    "playbooks/decision.md",
    "playbooks/workflow.md",
    "playbooks/context-intake.md",
    "playbooks/expression.md",
    "playbooks/architecture.md",
    "playbooks/technology-route.md",
    "playbooks/skill-evolution.md",
    "playbooks/research.md",
    "agents/openai.yaml",
    "scripts/check_converge_eval_suite.py",
    "scripts/check_converge_coverage_matrix.py",
    "scripts/build_converge_response_eval.py",
    "scripts/check_converge_response_eval.py",
    "scripts/summarize_converge_response_eval.py",
    "scripts/select_converge_response_eval_batch.py",
    "scripts/sync_converge_install.py",
    "scripts/check_converge_release.py",
]

FORBIDDEN_PATTERNS = {
    r"Converge v2": "Old v2 title remains",
    r"Three-Tier Complexity": "Old tier system remains as a primary rule",
    r"MUST call the structured question tool": "Old hard-coded tool rule remains",
    r"Codex CLI.*AskQuestion": "Codex must use request_user_input, not AskQuestion",
    r"100-point": "Numeric quality score language remains",
    r"100 分": "Numeric quality score language remains",
    r"\b80\b": "80-point draft language remains",
    r"\baddict(?:ive|ion)?\b": "Manipulative habit language remains",
    r"上瘾": "Manipulative habit language remains",
}

REQUIRED_SKILL_PHRASES = [
    "Indispensability Principles",
    "Universal Intent Guard",
    "Codex Default Mode",
    "Host Adapter Protocol",
    "host-adapter-matrix.md",
    "host-capability-contract.tsv",
    "host-source-evidence.md",
    "host-support-ledger.md",
    "Progressive completion rules",
    "session-only by default",
    "playbooks/workflow.md",
    "Freshness & Evidence Gate",
    "Technology Route",
    "Evidence Snapshot",
    "Current Best Known",
    "playbooks/technology-route.md",
    "High-Risk Boundary",
    "Source/Link",
    "Context Intake",
    "Input Inventory",
    "Context Trust Boundary",
    "Verification & Evolution",
    "Proof check",
    "playbooks/context-intake.md",
    "playbooks/skill-evolution.md",
    "scripts/check_converge_eval_suite.py",
    "scripts/check_converge_coverage_matrix.py",
    "scripts/build_converge_response_eval.py",
    "scripts/check_converge_response_eval.py",
    "scripts/sync_converge_install.py",
    "scripts/check_converge_release.py",
]

REQUIRED_OUTPUT_PROFILES = [
    "Universal Intent Guard",
    "Thinking Reply",
    "Direct Answer",
    "Conversation Reply",
    "Expression Draft",
    "Action Plan",
    "Technology Route",
    "Skill Evolution",
    "Decision Brief",
    "Converge Docs",
    "Dev Handoff",
]

REQUIRED_TEMPLATE_PROFILES = [
    "Universal Intent Guard",
    "Thinking Reply",
    "Direct Answer",
    "Conversation Reply",
    "Expression Draft",
    "Action Plan",
    "Technology Route",
    "Skill Evolution",
    "Decision Brief",
]

REQUIRED_EVAL_CASES = [
    "mixed-artifact-intake.md",
    "inaccessible-link-boundary.md",
    "high-stakes-financial-decision.md",
    "researched-answer-citations.md",
    "technology-route-current-stack.md",
    "mcp-by-default.md",
    "latest-library-advice.md",
    "no-research-private-preference.md",
    "context-poisoning-boundary.md",
    "skill-evolution-failed-rollout.md",
    "completion-proof-overclaim.md",
    "full-converge-docs-complex-project.md",
    "dev-handoff-after-docs.md",
    "codex-plan-native-question-ui.md",
    "cursor-native-question-bridge.md",
    "claude-native-question-bridge.md",
    "opencode-capability-adapter.md",
    "host-support-proof-boundary.md",
    "extended-host-capability-boundary.md",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check_required_files(errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")


def check_no_swap_files(errors: list[str]) -> None:
    for path in ROOT.rglob("*.swp"):
        errors.append(f"unexpected swap file: {path.relative_to(ROOT)}")


def check_eval_cases(errors: list[str]) -> None:
    cases = sorted((ROOT / "eval-cases").glob("*.md"))
    if len(cases) < 17:
        errors.append(f"expected at least 17 eval cases, found {len(cases)}")
    existing = {case.name for case in cases}
    for required_case in REQUIRED_EVAL_CASES:
        if required_case not in existing:
            errors.append(f"missing required eval case: {required_case}")
    for case in cases:
        text = case.read_text(encoding="utf-8")
        for heading in ("## User Prompt", "## Expected Behavior", "## Failure Tags"):
            if heading not in text:
                errors.append(f"{case.relative_to(ROOT)} missing {heading}")


def check_forbidden_patterns(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for pattern, message in FORBIDDEN_PATTERNS.items():
            if re.search(pattern, text):
                errors.append(f"{rel}: {message}")


def check_skill_references(errors: list[str]) -> None:
    text = read("SKILL.md")
    for rel in REQUIRED_FILES:
        if rel == "SKILL.md" or rel == "agents/openai.yaml" or rel.startswith("eval-artifacts/"):
            continue
        if rel not in text and Path(rel).name not in text:
            errors.append(f"SKILL.md does not mention resource: {rel}")


def check_required_skill_phrases(errors: list[str]) -> None:
    text = read("SKILL.md")
    for phrase in REQUIRED_SKILL_PHRASES:
        if phrase not in text:
            errors.append(f"SKILL.md missing required phrase: {phrase}")


def check_output_directory(errors: list[str]) -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.rglob("*.md"))
    if "project-docs/" in text or "`project-docs/`" in text:
        errors.append("project-docs directory reference remains; use converge-docs")


def check_output_profile_consistency(errors: list[str]) -> None:
    skill = read("SKILL.md")
    reference = read("reference.md")
    state = read("templates/converge-state.md")
    templates = read("templates/output-template.md")
    for profile in REQUIRED_OUTPUT_PROFILES:
        if profile not in skill:
            errors.append(f"SKILL.md missing output profile: {profile}")
        if profile not in reference:
            errors.append(f"reference.md missing output profile: {profile}")
        if profile not in state:
            errors.append(f"converge-state.md missing output profile: {profile}")
    for profile in REQUIRED_TEMPLATE_PROFILES:
        if f"## {profile}" not in templates:
            errors.append(f"output-template.md missing template profile: {profile}")


def check_host_support_ledger(errors: list[str]) -> None:
    text = read("host-support-ledger.md")
    required_hosts = [
        "Codex Default",
        "Codex Plan",
        "Claude Code",
        "Cursor",
        "opencode",
        "Cline",
        "Google Antigravity",
        "Gemini CLI",
        "GitHub Copilot",
        "Windsurf Cascade",
        "Continue",
        "Aider",
        "Unknown or future host",
    ]
    for host in required_hosts:
        if host not in text:
            errors.append(f"host-support-ledger.md missing host: {host}")

    required_cases = [
        "codex-plan-native-question-ui.md",
        "claude-native-question-bridge.md",
        "cursor-native-question-bridge.md",
    ]
    for case_name in required_cases:
        if case_name not in text:
            errors.append(f"host-support-ledger.md missing native case: {case_name}")

    required_phrases = [
        "36 of 39 real response-eval cases are reviewed as Pass with 0 Fail",
        "host-capability-contract.tsv",
        "H3 status: Unproven in this environment",
        "Do not say",
        "fully supports every host's native question UI",
        "check_converge_response_eval.py --require-all-cases --require-real-results",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"host-support-ledger.md missing required phrase: {phrase}")

    if "H3 status: Proven" in text:
        errors.append("host-support-ledger.md contains unsupported overclaim: H3 status: Proven")
    if "all native question paths are validated" in text:
        errors.append("host-support-ledger.md contains unsupported overclaim: all native question paths are validated")
    allowed_do_not_say = "Converge fully supports every host's native question UI."
    if text.count("fully supports every host") != 1 or allowed_do_not_say not in text:
        errors.append("host-support-ledger.md must contain the full-host native UI overclaim only as the Do not say example")


def check_host_source_evidence(errors: list[str]) -> None:
    text = read("host-source-evidence.md")
    required_urls = [
        "https://developers.openai.com/codex/skills",
        "https://developers.openai.com/codex/guides/agents-md",
        "https://code.claude.com/docs/en/skills",
        "https://docs.cursor.com/context/rules",
        "https://opencode.ai/docs/skills/",
        "https://docs.cline.bot/customization/skills",
        "https://antigravity.google/docs/skills",
        "https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/cli/configuration.md",
        "https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions",
        "https://windsurf.com/university/general-education/creating-modifying-rules",
        "https://docs.continue.dev/customization/rules",
        "https://aider.chat/docs/usage/conventions.html",
    ]
    for url in required_urls:
        if url not in text:
            errors.append(f"host-source-evidence.md missing source URL: {url}")
    for phrase in ("Last checked: 2026-05-28", "Claims Not Allowed From Source Evidence Alone", "Refresh Triggers"):
        if phrase not in text:
            errors.append(f"host-source-evidence.md missing required phrase: {phrase}")


def check_host_capability_contract(errors: list[str]) -> None:
    path = ROOT / "host-capability-contract.tsv"
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    required_columns = [
        "host_id",
        "display_name",
        "source_anchor",
        "install_anchor",
        "native_question_surface",
        "fallback_surface",
        "current_claim",
        "eval_case",
        "h3_boundary",
    ]
    if not rows:
        errors.append("host-capability-contract.tsv has no rows")
        return
    if rows[0].keys() != set(required_columns):
        actual = ", ".join(rows[0].keys())
        errors.append(f"host-capability-contract.tsv columns mismatch: {actual}")

    expected_hosts = {
        "codex-default": "Codex Default",
        "codex-plan": "Codex Plan",
        "claude-code": "Claude Code",
        "cursor": "Cursor",
        "opencode": "opencode",
        "cline": "Cline",
        "antigravity": "Google Antigravity",
        "gemini-cli": "Gemini CLI",
        "github-copilot": "GitHub Copilot",
        "windsurf": "Windsurf Cascade",
        "continue": "Continue",
        "aider": "Aider",
        "unknown": "Unknown or future host",
    }
    seen_hosts = {row.get("host_id", "") for row in rows}
    for host_id, display_name in expected_hosts.items():
        if host_id not in seen_hosts:
            errors.append(f"host-capability-contract.tsv missing host_id: {host_id}")
        elif not any(
            row.get("host_id") == host_id and row.get("display_name") == display_name
            for row in rows
        ):
            errors.append(f"host-capability-contract.tsv display_name mismatch for {host_id}")

    eval_cases = {case.name for case in (ROOT / "eval-cases").glob("*.md")}
    source_evidence = read("host-source-evidence.md")
    ledger = read("host-support-ledger.md")
    matrix = read("host-adapter-matrix.md")
    for row in rows:
        host_id = row.get("host_id", "")
        display_name = row.get("display_name", "")
        source_anchor = row.get("source_anchor", "")
        current_claim = row.get("current_claim", "")
        eval_case = row.get("eval_case", "")

        for column in required_columns:
            if not row.get(column):
                errors.append(f"host-capability-contract.tsv {host_id} missing {column}")
        if not re.match(r"^H[0-4]\b", current_claim):
            errors.append(f"host-capability-contract.tsv {host_id} current_claim must start with H0-H4")
        if eval_case not in eval_cases:
            errors.append(f"host-capability-contract.tsv {host_id} eval_case missing: {eval_case}")
        if source_anchor != "none" and source_anchor not in source_evidence:
            errors.append(f"host-capability-contract.tsv {host_id} source_anchor not in source evidence")
        if display_name not in ledger and display_name != "Unknown or future host":
            errors.append(f"host-capability-contract.tsv {host_id} display_name not in host ledger")
        if "host-capability-contract.tsv" not in matrix:
            errors.append("host-adapter-matrix.md does not reference host-capability-contract.tsv")
            break


def parse_simple_openai_yaml() -> dict[str, str]:
    values: dict[str, str] = {}
    current_section = ""
    for raw_line in read("agents/openai.yaml").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_section = line[:-1]
            continue
        if ":" not in line or not current_section:
            continue
        key, value = line.strip().split(":", 1)
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        values[f"{current_section}.{key}"] = value
    return values


def check_openai_yaml(errors: list[str]) -> None:
    values = parse_simple_openai_yaml()
    display = values.get("interface.display_name", "")
    short = values.get("interface.short_description", "")
    prompt = values.get("interface.default_prompt", "")
    implicit = values.get("policy.allow_implicit_invocation", "")

    if display != "Converge":
        errors.append("agents/openai.yaml display_name must be Converge")
    if not 25 <= len(short) <= 64:
        errors.append("agents/openai.yaml short_description must be 25-64 chars")
    if "$converge" not in prompt:
        errors.append("agents/openai.yaml default_prompt must mention $converge")
    for phrase in ("intent", "context", "verify"):
        if phrase not in prompt.lower():
            errors.append(f"agents/openai.yaml default_prompt should mention {phrase}")
    if implicit not in {"true", "True"}:
        errors.append("agents/openai.yaml should allow implicit invocation for soft-trigger use")


def check_scripts_compile(errors: list[str]) -> None:
    for script in sorted((ROOT / "scripts").glob("*.py")):
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as exc:
            errors.append(f"{script.relative_to(ROOT)} syntax error: {exc}")


def check_eval_suite_harness(errors: list[str]) -> None:
    script = ROOT / "scripts/check_converge_eval_suite.py"
    namespace: dict[str, object] = {"__file__": str(script)}
    try:
        exec(compile(script.read_text(encoding="utf-8"), str(script), "exec"), namespace)
        run_checks = namespace.get("run_checks")
        if not callable(run_checks):
            errors.append("check_converge_eval_suite.py does not expose run_checks")
            return
        for error in run_checks(ROOT):
            errors.append(f"eval suite: {error}")
    except Exception as exc:  # pragma: no cover - validator diagnostics
        errors.append(f"eval suite harness failed: {exc}")


def check_coverage_matrix_harness(errors: list[str]) -> None:
    script = ROOT / "scripts/check_converge_coverage_matrix.py"
    namespace: dict[str, object] = {"__file__": str(script)}
    try:
        exec(compile(script.read_text(encoding="utf-8"), str(script), "exec"), namespace)
        run_checks = namespace.get("run_checks")
        if not callable(run_checks):
            errors.append("check_converge_coverage_matrix.py does not expose run_checks")
            return
        for error in run_checks(ROOT):
            errors.append(f"coverage matrix: {error}")
    except Exception as exc:  # pragma: no cover - validator diagnostics
        errors.append(f"coverage matrix harness failed: {exc}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_openai_yaml(errors)
    check_no_swap_files(errors)
    check_eval_cases(errors)
    check_scripts_compile(errors)
    check_forbidden_patterns(errors)
    check_skill_references(errors)
    check_required_skill_phrases(errors)
    check_output_directory(errors)
    check_output_profile_consistency(errors)
    check_host_source_evidence(errors)
    check_host_capability_contract(errors)
    check_host_support_ledger(errors)
    check_eval_suite_harness(errors)
    check_coverage_matrix_harness(errors)

    if errors:
        print("Converge validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Converge validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
