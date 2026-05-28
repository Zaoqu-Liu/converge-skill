# Eval Case - Direct Translation No Trigger

## User Prompt

```text
把这句话翻译成英文：我们明天九点开会。
```

## Expected Behavior

- Does not activate Converge, run discovery, or mention intent reconstruction.
- Directly gives the translation with no extra ceremony.
- Does not ask questions, create a plan, browse, or hand off to a broader workflow.
- Keeps the answer proportionate to an obvious one-step task.

## Failure Tags

- `overtrigger`
- `ceremony-drag`
- `execution-stall`
