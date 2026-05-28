# Eval Case - Dev Handoff After Docs

## User Prompt

```text
@converge 我已经有 converge-docs/01-context.md、02-solution.md、03-execution.md、04-risks.md。现在别再跟我聊愿景了，帮我把它交接给后续 coding agent 直接实现。
```

Assume the referenced files are accessible in the workspace.

## Provided Artifacts

- context doc: `eval-artifacts/dev-handoff-after-docs/01-context.md`
- solution doc: `eval-artifacts/dev-handoff-after-docs/02-solution.md`
- execution doc: `eval-artifacts/dev-handoff-after-docs/03-execution.md`
- risks doc: `eval-artifacts/dev-handoff-after-docs/04-risks.md`

## Expected Behavior

- Uses Dev Handoff rather than restarting product discovery or writing another PRD.
- Inspects the referenced `converge-docs/` files before deriving implementation work.
- Produces implementation-ready scope, interfaces, task dependencies, validation commands, and handoff risks.
- Flags missing or contradictory source docs instead of inventing details.
- States what the handoff proves and what still needs implementation/runtime validation.

## Failure Tags

- `blind-intake`
- `execution-stall`
- `prd-capture`
- `missing-proof`
