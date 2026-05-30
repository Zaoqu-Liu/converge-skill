# Converge Blind Eval Prompt - researched-answer-citations.md

You are the model under test.

Use the Converge skill at:

```text
skills/converge/SKILL.md
```

Important:
- Do not read the eval case file.
- Do not ask for the expected behavior, rubric, or failure tags.
- Answer the user prompt naturally as the active host would allow.
- Use only tools actually available in the host environment.

## User Prompt

```text
@converge 帮我判断某个框架现在是不是还适合上生产，按最新资料给我结论。
```
