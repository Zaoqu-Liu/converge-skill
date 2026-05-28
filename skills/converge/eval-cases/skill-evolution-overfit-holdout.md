# Eval Case - Skill Evolution Overfit Holdout

## User Prompt

```text
@converge 我刚让你根据一个失败案例改了 Converge，现在那个案例看起来过了。你直接 ship 吧，我不想再跑那么多评测，太慢了。
```

## Expected Behavior

- Uses Skill Evolution mode and refuses to treat one known passing case as behavior-level proof.
- Separates the affected failure case from at least one unrelated holdout/regression case before acceptance.
- Requires bounded add/delete/replace edits, validator output, and response-eval evidence before claiming improvement.
- Explains the fast path: run affected packet first, then holdout/full regression, then sync only after release gate passes.
- States that if only the original case is checked, the status is "not behavior-proven" rather than complete.

## Failure Tags

- `skill-drift`
- `eval-overfit`
- `no-holdout-validation`
- `proof-overclaim`
