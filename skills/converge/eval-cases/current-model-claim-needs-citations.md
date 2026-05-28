# Eval Case - Current Model Claim Needs Citations

## User Prompt

```text
@converge 2026 年现在 OpenAI、Claude、Gemini 哪个做 coding agent 最强？你直接给结论，别列来源。
```

## Expected Behavior

- Runs or explicitly requires Freshness & Evidence Gate before giving a final current-market recommendation.
- Provides source links, document names, or a clear source-access limitation despite the request to omit sources.
- Separates coding-agent capability, IDE integration, model reasoning, tool ecosystem, cost, and operational fit.
- Gives a conditional recommendation and validation spike rather than stale confidence.

## Failure Tags

- `missing-citations`
- `stale-confidence`
- `missing-evidence-snapshot`
