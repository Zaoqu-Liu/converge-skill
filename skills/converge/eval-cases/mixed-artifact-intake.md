# Eval Case - Mixed Artifact Intake

## User Prompt

```text
@converge 我发了一个截图、一个 PRD 和一段报错日志，帮我判断真正问题是什么，不要只看我说法。
```

Artifacts are provided with this eval case and should be inspected before judging the problem.

## Provided Artifacts

- screenshot: `eval-artifacts/mixed-artifact-intake/screenshot.txt`
- PRD: `eval-artifacts/mixed-artifact-intake/prd.md`
- error log: `eval-artifacts/mixed-artifact-intake/error.log`

## Expected Behavior

- Builds an Input Inventory before asking questions.
- Inspects accessible screenshot/PRD/log evidence with available tools.
- Separates observed facts from inferred intent.
- Surfaces contradictions between user interpretation and artifacts if present.
- Does not ask the user to summarize artifacts that are available to inspect.

## Failure Tags

- `blind-intake`
- `artifact-hallucination`
- `false-understanding`
- `over-questioning`
