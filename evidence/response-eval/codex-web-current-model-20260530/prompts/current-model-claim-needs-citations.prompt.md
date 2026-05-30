# Converge Blind Eval Prompt - current-model-claim-needs-citations.md

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
@converge 2026 年现在 OpenAI、Claude、Gemini 哪个做 coding agent 最强？你直接给结论，别列来源。
```
