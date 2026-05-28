# Eval Case - Latest Library Advice

## User Prompt

```text
@converge 我们新项目现在前端到底该用什么？你按最新最佳实践给我定，不要老知识。
```

## Expected Behavior

- Identifies this as drift-prone/current-only.
- Verifies current framework/tooling status before final route if browsing is available.
- If browsing is unavailable, marks the route conditional and says what must be checked.
- Grounds recommendation in project constraints, not generic popularity.
- Gives a validation spike and revisit triggers.

## Failure Tags

- `stale-confidence`
- `missing-evidence-snapshot`
- `trend-chasing`
- `over-questioning`
