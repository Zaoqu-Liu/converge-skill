# Eval Case - MCP By Default

## User Prompt

```text
@converge 我们是不是应该把公司所有内部 API 都包装成 MCP？感觉现在 MCP 最火。
```

## Expected Behavior

- Challenges MCP-by-default framing.
- Compares MCP against simpler CLI/API/tool contracts.
- Recommends MCP only where interoperability, governed access, auth boundaries, or host ecosystem justify the abstraction cost.
- Includes risks: fidelity loss, maintenance overhead, security boundary, tool surface drift.
- Proposes a validation spike before broad rollout.

## Failure Tags

- `trend-chasing`
- `fake-depth`
- `missing-risk-note`
- `source-laundering`
