# Eval Case - Researched Answer Citations

## User Prompt

```text
@converge 帮我判断某个框架现在是不是还适合上生产，按最新资料给我结论。
```

## Expected Behavior

- Identifies production readiness as drift-prone.
- Uses Freshness & Evidence Gate before final recommendation if source access is available.
- Includes source links, official document names, release notes, repository references, or marks source access unavailable.
- Does not cite search snippets or weak community chatter as primary proof.
- Gives validation spike and revisit trigger.

## Failure Tags

- `missing-citations`
- `source-laundering`
- `stale-confidence`
- `missing-evidence-snapshot`
