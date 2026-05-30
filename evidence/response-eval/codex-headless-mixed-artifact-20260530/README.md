# Codex Headless Response-Eval Mixed Artifact Intake - 2026-05-30

This run stores real Codex headless output for the `mixed-artifact-intake.md` case.

## Scope

- Host/runtime: `codex exec` headless, read-only sandbox.
- Model shown by CLI: `gpt-5.5`.
- Eval case: `mixed-artifact-intake.md`.
- Prompt packet: `prompts/mixed-artifact-intake.prompt.md`.
- Provided artifacts: `artifacts/mixed-artifact-intake/`.
- Response artifact: `responses/mixed-artifact-intake.response.md`.
- Reviewed result: `results/mixed-artifact-intake.result.md`.

## Claim Boundary

This evidence supports a narrow behavior claim: Converge can handle a mixed artifact diagnosis request by locating and inspecting the available screenshot/PRD/log evidence, separating observed facts from inference, surfacing artifact contradictions, and naming the strongest current diagnosis before asking the user to summarize anything.

It proves that the reviewed headless response:

- Does not ask the user to summarize available artifacts.
- Builds an input inventory.
- Uses evidence from the PRD, screenshot OCR, and error log.
- Separates observed facts from inferred meaning.
- Surfaces contradictions between intended behavior, UI state, and backend logs.
- Gives a direct root-cause diagnosis and fix order.

It does not prove:

- Full behavior across all mixed image, PDF, repo, browser, or private-link artifact workflows.
- Native structured question UI behavior.
- H3 or H4 host support.
- Correctness on real production report-export code outside the supplied artifact fixture.

## Validate

```bash
python3 -B skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-mixed-artifact-20260530/results \
  --root skills/converge \
  --require-real-results
```

Summarize coverage:

```bash
python3 -B skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-headless-mixed-artifact-20260530/results \
  --root skills/converge \
  --require-real-results \
  --show-axes
```
