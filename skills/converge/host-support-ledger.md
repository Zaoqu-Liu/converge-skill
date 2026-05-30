# Host Support Ledger

Last reviewed: 2026-05-30

This ledger records what Converge can honestly claim for each host. Use it with `host-adapters.json`, `host-adapter-matrix.md`, and `host-native-interaction-runbook.md`.

## Current Global Evidence

- Static coverage: `SKILL.md`, `host-adapter-matrix.md`, `host-native-interaction-runbook.md`, and host-specific eval cases cover Codex, Claude Code, Cursor, opencode, Cline, Google Antigravity, Gemini CLI, GitHub Copilot, Windsurf, Continue, Aider, and unknown hosts.
- Source coverage: `host-source-evidence.md` records the current official host documentation checked for Codex, Claude Code, Cursor, opencode, Cline, Google Antigravity, Gemini CLI, GitHub Copilot, Windsurf, Continue, Aider, and Roo Code status boundaries.
- Adapter registry coverage: `host-adapters.json` machine-checks install target keys, skill anchors, bridge files, interaction surfaces, proof tiers, and eval hooks.
- Contract coverage: `host-capability-contract.tsv` machine-checks each host profile against source anchors, install surfaces, native question surfaces, fallback behavior, current claim tier, eval case, and H3 boundary.
- Install coverage: release checks compare canonical source against installed copies for Claude Code, Cursor, opencode, Cline, and Google Antigravity.
- Artifacted behavior coverage: 7 of 40 real response-eval cases are stored across Codex evidence runs and reviewed as Pass with 0 Fail: `evidence/response-eval/codex-headless-20260529`, `evidence/response-eval/codex-headless-choice-20260529`, `evidence/response-eval/codex-headless-host-proof-20260529`, `evidence/response-eval/codex-web-tech-route-20260529`, `evidence/response-eval/codex-headless-low-expression-20260529`, `evidence/response-eval/codex-headless-mixed-artifact-20260530`, and `evidence/response-eval/codex-web-current-model-20260530`.
- Missing behavior evidence: the remaining 33 cases are not yet stored as real response-eval results; native interactive question UI cases must not be filled from CLI/headless fallback output.

## Host Ledger

| Host | Highest Current Claim | Evidence | H3 Native Interaction Status | Claim Boundary |
|---|---|---|---|---|
| Codex Default | H2 fallback-tested | `evidence/response-eval/codex-headless-20260529/results/codex-default-no-native-ui.result.md` and `evidence/response-eval/codex-headless-choice-20260529/results/codex-default-choice-survey-trap.result.md` validate with `--require-real-results` | Not applicable; default mode has no `request_user_input` | Can claim Codex Default fallback behavior for the two reviewed headless cases, not full Codex coverage. |
| Codex Plan | H0 documented | `codex-plan-native-question-ui.md`, `host-native-interaction-runbook.md` | H3 status: Unproven in this environment | Can claim documented Plan Mode rules only until a real Plan Mode run uses `request_user_input`. |
| Claude Code | H1 installed | Installed copy matches canonical source; `claude-native-question-bridge.md` documents expected native behavior | H3 status: Unproven in this environment | Can claim Claude Code install/bridge coverage, not native `AskUserQuestion` behavior. |
| Cursor | H1 installed | Installed copy and `~/.cursor/rules/converge.mdc` match canonical bridge; no stored real Cursor fallback result is present in this repository | H3 status: Unproven in this environment | Can claim Cursor install/bridge coverage, not fallback behavior or native `AskQuestion` behavior. |
| opencode | H1 installed | Installed copy matches canonical source; no stored real opencode fallback result is present in this repository | No specific native question tool claimed | Can claim opencode installed skill coverage, not behavior-level fallback validation. |
| Cline | H1 installed | Installed copy matches canonical source after release check; `extended-host-capability-boundary.md` covers claim boundaries | H3 status: Unproven in this environment | Can claim Cline installed skill coverage, not activation/native question behavior. |
| Google Antigravity | H1 installed | Installed copy matches canonical source after release check; `extended-host-capability-boundary.md` covers claim boundaries | H3 status: Unproven in this environment | Can claim Antigravity installed skill coverage, not activation/native question behavior. |
| Gemini CLI | H0 documented | `host-source-evidence.md` records `GEMINI.md`/context-file docs; `extended-host-capability-boundary.md` covers claim boundaries | H3 status: Unproven in this environment | Can claim documented context-file bridge rules only. |
| GitHub Copilot | H0 documented | `host-source-evidence.md` records repository instruction docs, including `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` alternatives; `extended-host-capability-boundary.md` covers claim boundaries | H3 status: Unproven in this environment | Can claim documented repository-instruction bridge rules only. |
| Windsurf Cascade | H0 documented | `host-source-evidence.md` records rule docs; `extended-host-capability-boundary.md` covers claim boundaries | H3 status: Unproven in this environment | Can claim documented rule bridge rules only. |
| Continue | H0 documented | `host-source-evidence.md` records local, global, and hub rule docs; `extended-host-capability-boundary.md` covers claim boundaries | H3 status: Unproven in this environment | Can claim documented rule bridge rules only. |
| Aider | H0 documented | `host-source-evidence.md` records `CONVENTIONS.md` docs; `extended-host-capability-boundary.md` covers claim boundaries | H3 status: Unproven in this environment | Can claim documented convention-file bridge rules only. |
| Unknown or future host | H0 capability model | `host-adapter-matrix.md` capability map | H3 status: Unproven until a native tool is observed | Can claim capability-based rules, not brand-specific support. |

## Native Cases Still Open

These must remain missing until reviewed in a real interactive host:

- `codex-plan-native-question-ui.md`
- `claude-native-question-bridge.md`
- `cursor-native-question-bridge.md`

Cursor, opencode, and extended hosts such as Cline, Google Antigravity, Gemini CLI, GitHub Copilot, Windsurf, Continue, and Aider also need stored real host or headless/fallback runs before any H2/H3/H4 claim.

## Reporting Language

Use scoped claims:

```text
Converge is installed and release-checked for Claude Code, Cursor, opencode, Cline, and Google Antigravity. It has seven stored real Codex response-eval passes: two Codex Default fallback cases, one host proof-boundary discipline case, two web-assisted current-tech route cases, one low-expression ideation case, and one mixed-artifact diagnosis case. Native interactive question paths for Codex Plan, Claude Code, and Cursor remain H3-unproven until real interactive runs capture the native question UI being used correctly.
```

Do not say:

```text
Converge fully supports every host's native question UI.
```

## Promotion Rule

To promote a host from H1/H2 to H3:

1. Run the matching native case in a real interactive host.
2. Capture the native UI/tool evidence listed in `host-native-interaction-runbook.md`.
3. Create a normal response-eval result file for the matching case.
4. Run `scripts/check_converge_response_eval.py --require-all-cases --require-real-results` against the complete result set.
5. Only then update this ledger from `H3 status: Unproven` to a scoped H3 claim.
