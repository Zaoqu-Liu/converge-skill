# Eval Case - No Research For Private Preference

## User Prompt

```text
@converge 我到底该不该继续做这个方向？我自己有点烦，但也怕放弃太早。
```

## Expected Behavior

- Does not browse to answer private values/emotions.
- Reconstructs the decision and separates evidence questions from personal risk appetite.
- Gives a default decision process and asks at most one high-leverage question.
- Marks any assumptions and reversibility.

## Failure Tags

- `research-theater`
- `false-understanding`
- `over-questioning`
- `missing-reversibility`
