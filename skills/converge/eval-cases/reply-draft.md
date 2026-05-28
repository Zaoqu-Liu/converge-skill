# Eval Case - Reply Draft

## User Prompt

```text
用 $converge 帮我回客户，他说我们太贵了。
```

## Expected Behavior

- Routes to Conversation Reply, not PRD.
- Infers likely goal: preserve value framing and keep negotiation alive.
- Gives recommended stance before draft.
- Produces a sendable reply.
- Warns against discounting before scope adjustment.
- Does not ask unnecessary broad style questions.

## Failure Tags

- `prd-capture`
- `over-questioning`
- `weak-draft`
- `missing-risk-note`
