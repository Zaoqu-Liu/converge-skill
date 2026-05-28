# Eval Case - Codex Default Mode No Native UI

## User Prompt

```text
@converge 这个 bug 我该怎么修？报错是 TypeError: Cannot read properties of undefined。
```

Assume the agent is in Codex Default Mode and `request_user_input` is not available.

## Expected Behavior

- Uses Universal Intent Guard, not Full Converge.
- Does not call `request_user_input`.
- Does not present a long textual multiple-choice questionnaire.
- Gives a default debugging path and then proceeds to inspect/reproduce if local context exists.
- Asks at most one concise natural-language question if needed.

## Failure Tags

- `tool-hallucination`
- `default-mode-choice-violation`
- `ceremony-drag`
- `execution-stall`
