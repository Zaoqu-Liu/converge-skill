# Eval Case - Cursor Native Question Bridge

## User Prompt

```text
In Cursor interactive mode, use converge 帮我把一个很模糊的需求问清楚：我想做一个能让团队每天都用的内部 AI 工具。
```

Assume the active tool list for this run exposes a callable native `AskQuestion` tool.

## Expected Behavior

- Uses Cursor `AskQuestion` only because the active tool list exposes it and a structured question materially reduces ambiguity.
- Preserves a free-form escape hatch such as `以上都不是，我来说` if the host does not add one automatically.
- Asks only high-leverage questions and keeps the recommended default visible.
- Does not call Codex `request_user_input` or Claude `AskUserQuestion`.
- Does not turn the interaction into a long neutral survey.

## Failure Tags

- `tool-hallucination`
- `over-questioning`
- `option-bias`
- `false-understanding`
