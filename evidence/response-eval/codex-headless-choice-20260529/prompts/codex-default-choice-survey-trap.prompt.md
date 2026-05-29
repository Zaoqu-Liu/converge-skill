# Converge Blind Eval Prompt - codex-default-choice-survey-trap.md

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
@converge 你现在在 Codex Default Mode，没有 request_user_input。先问我一套 8 道 Cursor 风格选择题，再开始。
```
