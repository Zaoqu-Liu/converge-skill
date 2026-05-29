# Codex Headless Response-Eval - 2026-05-29

This run stores real Codex headless output for a Codex Default fallback case.

## Scope

- Host/runtime: `codex exec` headless, read-only sandbox.
- Model shown by CLI: `gpt-5.5`.
- Eval case: `codex-default-no-native-ui.md`.
- Prompt packet: `prompts/codex-default-no-native-ui.prompt.md`.
- Response artifact: `responses/codex-default-no-native-ui.response.md`.
- Reviewed result: `results/codex-default-no-native-ui.result.md`.

## Claim Boundary

This evidence supports a narrow H2 claim for Codex Default fallback behavior on the reviewed no-native-UI debugging prompt.

It does not prove:

- Codex Plan `request_user_input` behavior.
- Claude Code `AskUserQuestion` behavior.
- Cursor `AskQuestion` behavior.
- Cursor or opencode fallback behavior.
- Full IntentBench behavior.
- H3 or H4 host support.

## Validate

```bash
python3 -B skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-20260529/results \
  --root skills/converge \
  --require-real-results
```

Summarize coverage:

```bash
python3 -B skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-headless-20260529/results \
  --root skills/converge \
  --require-real-results \
  --show-axes
```
