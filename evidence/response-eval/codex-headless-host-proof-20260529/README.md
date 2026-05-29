# Codex Headless Response-Eval Host Proof Boundary - 2026-05-29

This run stores real Codex headless output for a host-support claim-boundary case.

## Scope

- Host/runtime: `codex exec` headless, read-only sandbox.
- Model shown by CLI: `gpt-5.5`.
- Eval case: `host-support-proof-boundary.md`.
- Prompt packet: `prompts/host-support-proof-boundary.prompt.md`.
- Response artifact: `responses/host-support-proof-boundary.response.md`.
- Reviewed result: `results/host-support-proof-boundary.result.md`.

## Claim Boundary

This evidence supports a narrow behavior claim that Converge preserves proof-tier discipline when asked to overstate cross-host support.

It proves that the reviewed headless response:

- Refuses to claim complete cross-host or native interactive support from install checks alone.
- Separates H1 install/bridge evidence from H2 fallback and H3 native interaction proof.
- Keeps Codex Plan, Claude Code, and Cursor native question paths unpromoted.
- Gives scoped public wording and a concrete validation plan.

It does not prove:

- Any real native interaction UI was available or used.
- Codex Plan `request_user_input` behavior.
- Claude Code `AskUserQuestion` behavior.
- Cursor `AskQuestion` behavior.
- Cursor, opencode, or extended-host fallback behavior.
- H3 or H4 host support.

## Validate

```bash
python3 -B skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-host-proof-20260529/results \
  --root skills/converge \
  --require-real-results
```

Summarize coverage:

```bash
python3 -B skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-headless-host-proof-20260529/results \
  --root skills/converge \
  --require-real-results \
  --show-axes
```
