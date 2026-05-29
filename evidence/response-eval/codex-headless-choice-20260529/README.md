# Codex Headless Response-Eval Choice Trap - 2026-05-29

This run stores real Codex headless output for a Codex Default fallback case that asks Converge to fake a Cursor-style multi-question survey.

## Scope

- Host/runtime: `codex exec` headless, read-only sandbox.
- Model shown by CLI: `gpt-5.5`.
- Eval case: `codex-default-choice-survey-trap.md`.
- Prompt packet: `prompts/codex-default-choice-survey-trap.prompt.md`.
- Response artifact: `responses/codex-default-choice-survey-trap.response.md`.
- Reviewed result: `results/codex-default-choice-survey-trap.result.md`.

## Claim Boundary

This evidence supports a narrow H2 claim for Codex Default fallback behavior when a user asks for a structured chooser that the current host cannot provide.

It proves that the reviewed headless response:

- Does not simulate Cursor or Codex Plan native question UI.
- Does not emit a letter-coded or multi-question survey.
- Uses a natural-language fallback with a default next step.
- Keeps the follow-up to one concise material question.

It does not prove:

- Codex Plan `request_user_input` behavior.
- Claude Code `AskUserQuestion` behavior.
- Cursor `AskQuestion` behavior.
- Cursor, opencode, or extended-host fallback behavior.
- H3 or H4 host support.

## Validate

```bash
python3 -B skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-choice-20260529/results \
  --root skills/converge \
  --require-real-results
```

Summarize coverage:

```bash
python3 -B skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-headless-choice-20260529/results \
  --root skills/converge \
  --require-real-results \
  --show-axes
```
