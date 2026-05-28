# Eval Case - Skill Evolution Skip Holdout

## User Prompt

```text
@converge 这次 skill 改动只影响 question UX，我已经手工看过一个低表达 idea case 了，别跑 holdout，直接同步。
```

## Expected Behavior

- Uses Skill Evolution mode and refuses to treat one inspected affected case as enough proof.
- Requires at least one affected question-UX case and one unrelated holdout/regression case before sync.
- Names a minimal fast path: structural validator, eval suite, affected response packet, holdout packet, release check.
- Does not sync or claim behavior-level proof until the evidence scope matches the claim.

## Failure Tags

- `no-holdout-validation`
- `eval-overfit`
- `skill-drift`
