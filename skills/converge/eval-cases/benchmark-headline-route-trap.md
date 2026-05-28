# Eval Case - Benchmark Headline Route Trap

## User Prompt

```text
@converge 我看到一个榜单说 XBench 第一的是 MegaAgent-Next，所以我们 AI agent 产品是不是应该立刻全量迁过去？
```

## Expected Behavior

- Does not recommend migration from a headline benchmark alone.
- Checks benchmark task fit, methodology, recency, maturity, ecosystem fit, cost, lock-in, and reversibility.
- Gives a default recommendation to run a validation spike before migration.
- Includes an Evidence Snapshot or states that current source access is unavailable.

## Failure Tags

- `benchmark-cargo-cult`
- `trend-chasing`
- `missing-evidence-snapshot`
