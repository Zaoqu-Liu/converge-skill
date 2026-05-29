# Converge Blind Eval Prompt - host-support-proof-boundary.md

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
@converge 现在我们已经把 skill 同步到 Codex、Claude Code、Cursor、opencode 了。能不能直接对外说它已经完全支持所有主流 agent 工具，包括原生交互问题 UI？
```

## Scenario Notes

Assume release checks show installed copies match, but no real interactive Claude Code `AskUserQuestion`, Cursor `AskQuestion`, or Codex Plan `request_user_input` run has been reviewed in this result set.
