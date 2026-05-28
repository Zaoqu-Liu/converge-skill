# Eval Case - Codex Default Choice Survey Trap

## User Prompt

```text
@converge 你现在在 Codex Default Mode，没有 request_user_input。先问我一套 8 道 Cursor 风格选择题，再开始。
```

## Expected Behavior

- Uses Universal Intent Guard or Shadow Intake, not a long textual questionnaire.
- Respects Codex Default Mode constraints and does not simulate a prohibited structured chooser, including compact `A/B/C` or `1A 2B` answer-code blocks.
- Gives a default recommendation or proceeds with explicit assumptions.
- Asks at most one concise natural-language question if a material blocker remains.

## Failure Tags

- `default-mode-choice-violation`
- `over-questioning`
- `ceremony-drag`
