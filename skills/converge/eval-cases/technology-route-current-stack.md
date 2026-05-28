# Eval Case - Technology Route Current Stack

## User Prompt

```text
@converge 我现在要做一个 AI Agent 产品，2026 年最新最好的技术路线怎么选？OpenAI Agents SDK、Claude Agent SDK、Google ADK、LangGraph、CrewAI、MCP 都要考虑。
```

## Expected Behavior

- Uses Technology Route, not generic Action Plan.
- Runs or explicitly requires Freshness & Evidence Gate before making a final recommendation.
- Checks current official docs/release notes/radar-style references when available.
- Separates Current Best Known, Safe Default, Frontier Bet, and Avoid/Hold.
- Includes Evidence Snapshot, validation spike, and revisit trigger.
- Preserves exact maturity labels from sources instead of upgrading preview/pre-GA/beta into GA or production-ready.
- Does not recommend a framework only because it is newest or most hyped.

## Failure Tags

- `stale-confidence`
- `trend-chasing`
- `missing-evidence-snapshot`
- `benchmark-cargo-cult`
- `source-laundering`
- `fake-precision`
