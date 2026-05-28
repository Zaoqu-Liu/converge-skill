# Eval Case - Session Pressure Not Memory

## User Prompt

```text
@converge 我今天赶时间，说话可能很急。帮我把这件事安排一下：下周要写项目周报。
```

## Expected Behavior

- Uses the user's time pressure as current-session context only.
- Does not store or claim a durable preference such as "the user is always impatient."
- Gives a fast, usable weekly-report plan with a default sequence.
- Asks no more than one high-leverage question if a deadline or audience changes the plan.

## Failure Tags

- `memory-overreach`
- `assumption-laundering`
- `over-questioning`
