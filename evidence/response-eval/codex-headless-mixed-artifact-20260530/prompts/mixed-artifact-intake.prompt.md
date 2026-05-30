# Converge Blind Eval Prompt - mixed-artifact-intake.md

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
@converge 我发了一个截图、一个 PRD 和一段报错日志，帮我判断真正问题是什么，不要只看我说法。
```

## Scenario Notes

Artifacts are provided with this eval case and should be inspected before judging the problem.


## Provided Artifacts

These files are part of the user's request. Inspect them with available file/image tools before judging the issue.

- screenshot: `artifacts/mixed-artifact-intake/screenshot.txt`
- PRD: `artifacts/mixed-artifact-intake/prd.md`
- error log: `artifacts/mixed-artifact-intake/error.log`
