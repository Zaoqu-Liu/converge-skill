# Eval Case - Architecture Ambiguity

## User Prompt

```text
用 $converge 帮我设计一下我们系统的权限架构，之后要给工程师干。
```

## Expected Behavior

- Routes to Architecture playbook.
- If repo is available, explores before asking repo-fact questions.
- Clarifies actors, resources, policies, enforcement points, audit needs, migration constraints.
- Does not invent API contracts before behavior is settled.
- Produces Converge Docs and only then offers Dev Handoff.

## Failure Tags

- `blind-intake`
- `fake-precision`
- `premature-docs`
- `missing-risk-note`
