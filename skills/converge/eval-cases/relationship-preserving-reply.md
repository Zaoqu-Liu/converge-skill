# Eval Case - Relationship Preserving Reply

## User Prompt

```text
@converge 帮我回一个合作方：他们报价太高但我还想留关系，语气要坚定但别撕破脸。
```

## Expected Behavior

- Produces a sendable reply draft immediately.
- Chooses a clear default negotiation stance instead of only listing styles or options.
- Preserves relationship while stating the price concern and a concrete next step.
- Avoids biased options that make the recommended path look artificially superior.

## Failure Tags

- `weak-draft`
- `option-bias`
- `no-owner-recommendation`
