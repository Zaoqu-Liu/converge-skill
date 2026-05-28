# Eval Case - opencode Capability Adapter

## User Prompt

```text
In opencode, use converge 帮我把一个很模糊的需求收敛一下。当前 opencode 只给了 shell/file tools，没有 native question UI；项目里有 AGENTS.md 和 opencode.json。不要按 Codex 或 Cursor 的工具名来处理。
```

## Provided Artifacts

- project rules: `eval-artifacts/opencode-capability-adapter/AGENTS.md`
- opencode config: `eval-artifacts/opencode-capability-adapter/opencode.json`

## Expected Behavior

- Treats opencode as a capability profile, not as Codex, Claude Code, or Cursor.
- Checks or asks to inspect `AGENTS.md` / `opencode.json` if they are accessible before relying on project-specific rules.
- Does not call or mention Codex `request_user_input`, Claude `AskUserQuestion`, or Cursor `AskQuestion`.
- Uses a concise natural-language or compact textual fallback because no native question UI is available.
- Preserves Converge behavior: intent reconstruction, owner default, one material question or explicit assumptions, and a usable next action.

## Failure Tags

- `tool-hallucination`
- `blind-intake`
- `false-understanding`
- `ceremony-drag`
