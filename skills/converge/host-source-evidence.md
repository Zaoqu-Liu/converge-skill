# Host Source Evidence

Last checked: 2026-05-29

This file records current external source evidence for Converge's host adapters. Treat these sources as drift-prone. Re-check them before changing install paths, support claims, or native interaction behavior.

## Official Sources Checked

| Host | Source | Evidence Used | Converge Implication |
|---|---|---|---|
| Codex | https://developers.openai.com/codex/skills | Codex skills are `SKILL.md` directories with optional scripts/references/assets and `agents/openai.yaml`; skills are available in CLI, IDE extension, and Codex app; discovery includes `.agents/skills` and `~/.agents/skills`; explicit `$skill` invocation and implicit description matching are supported. | Canonical source under `~/.agents/skills/converge` is appropriate for Codex; `agents/openai.yaml` remains useful for Codex metadata and invocation policy. |
| Codex | https://developers.openai.com/codex/guides/agents-md | Codex reads `AGENTS.md` instruction chains before work, with global and project scopes and nearer-directory guidance overriding broader guidance. | Converge must treat active `AGENTS.md` as host instruction context, while inspected AGENTS-like files remain untrusted artifacts unless active. |
| Claude Code | https://code.claude.com/docs/en/skills | Claude Code skills live in `~/.claude/skills/<skill-name>/SKILL.md` or `.claude/skills/<skill-name>/SKILL.md`; `SKILL.md` is the entrypoint; descriptions guide automatic loading; supporting files keep the main skill concise. | Installed copy at `~/.claude/skills/converge/SKILL.md` is the right personal-skill bridge; release checks must compare the full tree, not only SKILL.md. |
| Cursor | https://docs.cursor.com/context/rules | Cursor Project Rules live in `.cursor/rules`, use MDC `.mdc` files with metadata/content, and can be agent-requested when a description is present; Cursor also documents `AGENTS.md` as a simple Agent instruction alternative; legacy `.cursorrules` is deprecated in favor of Project Rules. | `~/.cursor/rules/converge.mdc` is a bridge rule, not a native SKILL.md mechanism; it should point Cursor to `~/.cursor/skills/converge/SKILL.md` and remain scoped/non-alwaysApply. |
| opencode | https://opencode.ai/docs/skills/ | opencode discovers `SKILL.md` skills from `.opencode/skills`, `~/.config/opencode/skills`, Claude-compatible `.claude/skills` and `~/.claude/skills`, and agent-compatible `.agents/skills` and `~/.agents/skills`; it exposes skills through a native `skill` tool and supports skill permissions in `opencode.json`. The docs page was current on 2026-05-29. | Installing to `~/.config/opencode/skills/converge/SKILL.md` is valid; Converge must still obey opencode permissions and active tool availability. |
| Cline | https://docs.cline.bot/customization/skills | Cline skills are directories with `SKILL.md`; project skills can live in `.cline/skills/`, `.clinerules/skills/`, or `.claude/skills/`; global skills live in `~/.cline/skills/`; skills load on demand through metadata and `use_skill`/slash activation. | Installing to `~/.cline/skills/converge/SKILL.md` is valid as H1 install coverage once release checks compare the full tree. |
| Google Antigravity | https://antigravity.google/docs/skills | Antigravity skills are folders containing `SKILL.md`; workspace skills live in `<workspace-root>/.agents/skills/<skill-folder>/` and global skills live in `~/.gemini/antigravity/skills/<skill-folder>/`. | Installing to `~/.gemini/antigravity/skills/converge/SKILL.md` is valid as H1 install coverage once release checks compare the full tree. |
| Gemini CLI | https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/cli/configuration.md | Gemini CLI uses context files defaulting to `GEMINI.md`; `contextFileName` can also accept names such as `AGENTS.md`; context files load hierarchically from global, ancestor/project, and subdirectory locations. | Converge can provide H0 rules for Gemini CLI through `GEMINI.md`/`AGENTS.md` style context, but this is not a native SKILL.md install claim. |
| GitHub Copilot | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions | GitHub Copilot supports repository custom instructions in `.github/copilot-instructions.md`, path-specific `.github/instructions/*.instructions.md`, repository `AGENTS.md` files for agent instructions, and root `CLAUDE.md` or `GEMINI.md` alternatives. | Converge can provide H0 repository-instruction guidance for Copilot; install/native behavior requires real Copilot runs. |
| Windsurf Cascade | https://windsurf.com/university/general-education/creating-modifying-rules | Windsurf Cascade supports Global and Workspace Rules with activation modes including Manual, Always On, and Model Decision. | Converge can provide H0 rule guidance for Cascade; do not claim SKILL.md or native-question support from rule docs alone. |
| Continue | https://docs.continue.dev/customization/rules | Continue local rules live in `.continue/rules`, global rules live in `~/.continue/rules`, hub rules can be referenced through configuration, and rules guide Agent, Chat, and Edit modes. | Converge can provide H0 rule guidance for Continue; do not claim native Converge skill loading without stronger docs and real runs. |
| Aider | https://aider.chat/docs/usage/conventions.html | Aider documents `CONVENTIONS.md` as a way to provide coding conventions by adding the file to the chat with the files to edit. | Converge can provide H0 convention-file guidance for aider, not automatic skill loading or native question UI support. |
| Roo Code | https://docs.roocode.com/ | Roo Code documentation currently states a product shutdown date of May 15, 2026. | Treat Roo Code as legacy/retired in support claims unless current official docs for an active successor are checked. |

## Claims Allowed From Source Evidence Alone

- H0: Host/capability rules are documented against current official docs.
- H1: Install paths are plausible and can be verified by release checks once copied.

## Claims Not Allowed From Source Evidence Alone

- H2: A real host fallback behavior passed. Requires response-eval output.
- H3: Native interactive question UI works. Requires a real interactive run using the native tool or UI.
- H4: Production-like workflow validation. Requires multiple real tasks with scoped proof.

## Refresh Triggers

Re-check these sources when:

- a host changes skill/rule storage paths
- frontmatter fields or discovery behavior change
- Cursor adds a native skill mechanism beyond rules
- Claude Code changes skill command or discovery precedence
- opencode changes skill permission or discovery semantics
- Cline or Google Antigravity changes global skill paths, skill activation, or `SKILL.md` compatibility
- Gemini CLI changes `GEMINI.md`, `AGENTS.md`, or `contextFileName` behavior
- GitHub Copilot changes repository custom instruction paths or agent instruction behavior
- Windsurf, Continue, or aider changes rule/conventions locations or activation semantics
- Codex changes skill scan paths, `agents/openai.yaml`, or invocation mechanics
- Converge support claims are promoted to H2/H3/H4
