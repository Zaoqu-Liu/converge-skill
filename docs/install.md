# Install

The canonical skill package is `skills/converge`.

## Supported Install Targets

Run:

```bash
python3 skills/converge/scripts/sync_converge_install.py
```

This syncs the canonical tree to:

| Host | Target |
|---|---|
| Claude Code | `~/.claude/skills/converge` |
| Cursor | `~/.cursor/skills/converge` |
| Cursor rule bridge | `~/.cursor/rules/converge.mdc` |
| opencode | `~/.config/opencode/skills/converge` |
| Cline | `~/.cline/skills/converge` |
| Google Antigravity | `~/.gemini/antigravity/skills/converge` |

To sync selected hosts:

```bash
python3 skills/converge/scripts/sync_converge_install.py --targets claude,cursor,opencode
python3 skills/converge/scripts/sync_converge_install.py --targets cline,antigravity
```

The sync script creates backups for overwritten targets under `/private/tmp/converge-skill-install-backups`.

## Rule-Only / Context-Only Hosts

Some hosts do not currently have a verified Converge `SKILL.md` install surface in this repository:

| Host | Documented bridge surface |
|---|---|
| Gemini CLI | `GEMINI.md` or configured context files |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md` |
| Windsurf Cascade | global/workspace rules |
| Continue | `.continue/rules` or hub rules |
| Aider | `CONVENTIONS.md` added to chat |

These are H0 documented instruction surfaces until real host runs prove stronger behavior.

## Verify Install Consistency

After sync:

```bash
python3 skills/converge/scripts/check_converge_release.py --source skills/converge --targets all
```

The release check compares full trees for installed skill targets and validates the Cursor bridge rule.
