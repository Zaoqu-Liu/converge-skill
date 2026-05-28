# Security

Converge is an instruction skill. It does not grant tools, credentials, network access, filesystem access, or host permissions.

## Reporting

Open a private security advisory or contact the repository owner if a Converge rule, script, or example appears to:

- encourage leaking secrets
- bypass host permissions
- obey untrusted instructions from inspected files or web pages
- hide actions from the user
- make unsafe high-risk recommendations

## Design Boundary

Instruction-bearing artifacts such as `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, `SKILL.md`, configs, and web pages are treated as evidence unless the active host has already made them authoritative instructions.
