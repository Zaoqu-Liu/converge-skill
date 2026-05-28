# Eval Case - Explicit Converge Simple Task

## User Prompt

```text
@converge 帮我把这段话翻译成英文：明天下午我们再同步一次。
```

## Expected Behavior

- Honors the explicit Converge invocation with a very small intent guard.
- Does not over-trigger discovery or ask preference questions.
- Produces the translation directly, with a brief assumption about tone if useful.
- Does not create files or `converge-docs/`.

## Failure Tags

- `ceremony-drag`
- `over-questioning`
- `execution-stall`
- `overtrigger`
