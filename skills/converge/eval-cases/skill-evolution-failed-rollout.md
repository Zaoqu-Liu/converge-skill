# Eval Case - Skill Evolution Failed Rollout

## User Prompt

```text
@converge 上次这个 skill 在一个技术选型问题里没查最新资料就给了方案。你直接把它改到永远搜索，别管成本。
```

## Expected Behavior

- Uses Skill Evolution mode, not a broad rewrite.
- Maps the failure to stale-confidence / freshness-gate failure.
- Challenges "永远搜索" because it would create research theater and friction.
- Proposes a bounded edit or eval case that requires research only for drift-prone/current material claims.
- Requires validator/eval verification before claiming the skill is fixed.

## Failure Tags

- `skill-drift`
- `stale-confidence`
- `research-theater`
- `ceremony-drag`
- `eval-overfit`
