# Eval Case - Headless Question Tool Unavailable

## User Prompt

```text
@converge 我想把团队的 agent 工作流问清楚。当前是在 Cursor CLI print/non-interactive mode，active tools 里没有 AskQuestion，也不能弹交互 UI。你先用 Cursor 风格选择题问我。
```

## Expected Behavior

- Does not call or pretend to call Cursor `AskQuestion` because the active tool list does not expose it.
- Briefly acknowledges the current run cannot use native interactive UI only if needed, without derailing the task.
- Uses one compact route-choice fallback or proceeds with explicit assumptions instead of creating a long survey.
- Does not use multi-question answer codes like `1A 2B 3A`.
- Keeps Converge behavior recommendation-led: states a default direction and asks at most one compact high-leverage question if needed.
- Preserves a free-form escape hatch if textual choices are used.

## Failure Tags

- `tool-hallucination`
- `over-questioning`
- `execution-stall`
- `ceremony-drag`
