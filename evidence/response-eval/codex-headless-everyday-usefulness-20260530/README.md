# Codex Headless Response-Eval Everyday Usefulness - 2026-05-30

This run stores real Codex headless output for four everyday-usefulness cases:

- `messy-decision.md`
- `everyday-work-plan.md`
- `reply-draft.md`
- `relationship-preserving-reply.md`

## Scope

- Host/runtime: Codex CLI headless via `codex exec`.
- Model/host label in results: `codex exec headless gpt-5.5`.
- Skill under test: `skills/converge/SKILL.md`.
- Prompt packets: `prompts/`.
- Response artifacts: `responses/`.
- Reviewed results: `results/`.

## Claim Boundary

This evidence supports a narrow behavior claim: Converge can produce useful
everyday decision, planning, and reply outputs without turning ordinary fuzzy
requests into PRDs, surveys, or generic motivation.

It proves that the reviewed headless responses:

- Separate "quit job now" from "pursue the venture" in a high-stakes career decision.
- Provide a reversible validation sprint instead of a simplistic yes/no answer.
- Treat overload as operating-cadence failure, not motivation failure.
- Rank work lanes and protect minimum viable maintenance for health.
- Draft directly sendable customer and partner replies.
- Preserve negotiation value and relationship while stating budget/price boundaries.

It does not prove:

- Universal career, productivity, or negotiation advice.
- Long-term user adherence.
- Final negotiation outcomes.
- Native structured question UI behavior.
- Full behavior coverage across all everyday-usefulness prompts.

## Validate

```bash
python3 -B skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-everyday-usefulness-20260530/results \
  --root skills/converge \
  --require-real-results
```

Summarize coverage:

```bash
python3 -B skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-headless-everyday-usefulness-20260530/results \
  --root skills/converge \
  --require-real-results \
  --show-axes
```
