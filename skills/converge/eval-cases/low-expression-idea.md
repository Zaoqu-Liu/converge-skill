# Eval Case - Low Expression Idea

## User Prompt

```text
用 $converge 帮我想一个 AI 产品，我想做点很牛的东西，最好能每天都用。
```

## Expected Behavior

- Does not write a PRD immediately.
- Generates multiple intent hypotheses.
- States a default judgment.
- Challenges "很牛" / "每天都用" as insufficient positioning.
- Avoids unverified market or competitor generalizations when justifying the idea.
- Asks 1-3 high-leverage questions.
- Uses structured question UI if available; otherwise markdown fallback.

## Failure Tags

- `premature-docs`
- `false-understanding`
- `over-questioning`
- `no-owner-recommendation`
- `stale-confidence`
