# Eval Case - Codex Plan Native Question UI

## User Prompt

```text
@converge 我有三个方向都想做，但我说不清楚，你先帮我问几个关键问题，然后直接给我默认路线。
```

Assume the agent is in Codex Plan Mode and `request_user_input` is available.

## Expected Behavior

- Uses Codex `request_user_input` only if the questions materially change the recommendation.
- Asks 1-3 questions, each with 2-3 options, and puts the recommended option first.
- Does not manually add an Other option because Codex provides the free-form escape hatch.
- Gives an owner default before or inside the question framing.
- Does not use Claude `AskUserQuestion`, Cursor `AskQuestion`, or a long markdown survey.

## Failure Tags

- `tool-hallucination`
- `over-questioning`
- `option-bias`
- `ceremony-drag`
