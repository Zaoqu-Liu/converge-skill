# Host Native Interaction Runbook

Use this runbook only for H3 proof in `host-adapter-matrix.md`: real native interactive question behavior. Do not use it for H0 static coverage, H1 install checks, or H2 headless fallback response-eval.

## Non-Negotiable Rule

Native interaction proof requires a real run where the active host exposes the native question surface and Converge uses it correctly. A scenario note, product documentation, installed skill copy, CLI print mode, screenshot of a rule file, or headless fallback answer is not H3 proof.

If native interaction cannot be tested, record:

```text
H3 status: Unproven in this environment.
Reason: [native tool absent / host is headless / print mode / no interactive session / permission boundary]
Fallback evidence: [H1 install / H2 fallback result path]
Claim allowed: [installed / fallback-tested], not native-interactive-tested.
```

## Evidence To Capture

For each native interaction run, capture:

- host name and version when available
- date
- active mode, for example Codex Plan Mode, Claude Code interactive, or Cursor Agent interactive
- prompt sent to the host
- native tool or UI actually used
- question count
- options shown, including recommended option first
- free-form escape hatch behavior
- whether unrelated host tools were avoided
- follow-up answer after the first clarification round
- screenshot, transcript, log, or exported conversation link if the host supports it

## Codex Plan H3

Prerequisites:

- The run is in Codex Plan Mode.
- `request_user_input` is present in the active tool list.
- The user prompt materially benefits from structured clarification.

Expected behavior:

- Call `request_user_input`.
- Ask 1-3 questions.
- Use 2-3 options per question.
- Put the recommended option first and suffix its label with `(Recommended)`.
- Do not add a manual `Other` option because Codex adds a free-form option automatically.
- After the user's first clarification, move toward a concrete answer, plan, or artifact.

Fail if:

- It renders a long Markdown survey instead of using `request_user_input`.
- It uses Claude or Cursor tool names.
- It asks low-value questions whose answers do not change the recommendation.
- It stalls after the first clarification round.

## Claude Code H3

Prerequisites:

- The run is an interactive Claude Code session, not `claude -p` print mode.
- `AskUserQuestion` is visible as callable in the active tool list or host tool manifest.
- The installed skill at `~/.claude/skills/converge/SKILL.md` matches canonical source.

Expected behavior:

- Use `AskUserQuestion` only when it is actually callable.
- Keep question count low.
- Put Converge's recommended default in the question framing or first option.
- Include a free-form escape hatch if the host does not provide one automatically.
- Continue to a concrete next action after the first answer.

Fail if:

- It treats a scenario note or docs page as proof the tool exists.
- It calls Codex `request_user_input` or Cursor `AskQuestion`.
- It produces a neutral survey with no owner recommendation.
- It claims native Claude Code support from `claude -p` output alone.

## Cursor H3

Prerequisites:

- The run is an interactive Cursor Agent session, not only a CLI or rule-file inspection.
- `AskQuestion` is visible as callable in the active tool list or host tool manifest.
- The installed skill at `~/.cursor/skills/converge/SKILL.md` matches canonical source.
- The bridge rule at `~/.cursor/rules/converge.mdc` is present.

Expected behavior:

- Use `AskQuestion` only when it is actually callable.
- Preserve a free-form escape hatch such as `以上都不是，我来说` if Cursor does not add one automatically.
- Keep the recommendation visible.
- Ask only questions that materially reduce ambiguity.
- Continue toward a concrete next action after the first answer.

Fail if:

- It calls Codex or Claude question tools.
- It assumes a native question tool exists from product brand alone.
- It turns the interaction into a long neutral survey.
- It claims Cursor native question support from install checks or headless fallback alone.

## Result File Mapping

When a native run is reviewed, create a normal response-eval result file for the matching case:

- `codex-plan-native-question-ui.md`
- `claude-native-question-bridge.md`
- `cursor-native-question-bridge.md`

Use `Model/Host` to name the real host and mode, for example:

```text
Model/Host: OpenAI Codex / Codex Plan Mode interactive
Model/Host: Claude Code 2.1.145 / interactive
Model/Host: Cursor 3.2.16 / Agent interactive
```

Do not fill these cases with Codex headless fallback output. If the host cannot expose the native tool in the current environment, leave the case missing and report H3 as unproven.
