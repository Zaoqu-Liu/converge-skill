# Converge Blind Eval Prompt - codex-default-no-native-ui.md

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
@converge 这个 bug 我该怎么修？报错是 TypeError: Cannot read properties of undefined。
```

## Scenario Notes

Assume the agent is in Codex Default Mode and `request_user_input` is not available.
