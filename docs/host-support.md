# Host Support

Converge supports hosts by capability, not by brand. Every claim must map to a proof tier.

## Proof Tiers

| Tier | Claim | Minimum evidence |
|---|---|---|
| H0 | documented rule coverage | official docs, skill rules, eval case |
| H1 | installed or bridged | synced copy or bridge matches canonical source |
| H2 | fallback behavior tested | real response-eval in CLI/headless/non-interactive mode |
| H3 | native interactive behavior tested | real host run with native question UI/tool available and used correctly |
| H4 | production-like workflow tested | multiple real tasks across files/tools/research/editing with scoped proof |

## Current Scope

H1 install coverage is release-checked for Claude Code, Cursor, opencode, Cline, and Google Antigravity.

H0 documented instruction-surface coverage exists for Gemini CLI, GitHub Copilot, Windsurf, Continue, and Aider.

Codex Default and selected fallback paths have H2 response-eval evidence. Codex Plan, Claude Code native `AskUserQuestion`, Cursor native `AskQuestion`, and extended-host native activation paths remain unproven until real interactive runs are reviewed.

H3 evidence must be captured through native-proof packets:

```bash
python3 -m converge native-proof --out /tmp/converge-native-proof
python3 -m converge native-proof --proofs /tmp/converge-native-proof/proofs --require-real-artifacts
```

Native-proof validation checks that the native question UI/tool was actually observed, used correctly, and supported by transcript, screenshot, log, or export evidence. It is separate from response-eval, which judges answer quality.

## Source Of Truth

Use these files before changing host support:

- `skills/converge/host-adapters.json`
- `skills/converge/host-source-evidence.md`
- `skills/converge/host-capability-contract.tsv`
- `skills/converge/host-adapter-matrix.md`
- `skills/converge/host-support-ledger.md`
- `skills/converge/host-native-interaction-runbook.md`

Do not promote a host claim by editing prose only. Update the adapter registry, TSV contract, eval coverage, and validation evidence together. `converge validate --protocol-only` fails if the registry drifts from the TSV contract.
