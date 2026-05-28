# Eval Case - Claude Native Question Bridge

## User Prompt

```text
In Claude Code interactive mode, use converge 帮我把这个 idea 收敛一下：我想优化我们团队所有 AI agent 的工作方式，但不知道从哪里开始。
```

Assume the active tool list for this run exposes a callable native `AskUserQuestion` tool.

## Expected Behavior

- Uses Claude Code `AskUserQuestion` only because the active tool list exposes it and structured questioning is useful.
- Keeps the question count low and recommendation-led rather than neutral or exhaustive.
- Provides a free-form escape hatch if the host does not provide one automatically.
- Does not call Codex `request_user_input` or Cursor `AskQuestion`.
- Moves toward a concrete next action after the first clarification round.

## Failure Tags

- `tool-hallucination`
- `over-questioning`
- `option-bias`
- `execution-stall`
