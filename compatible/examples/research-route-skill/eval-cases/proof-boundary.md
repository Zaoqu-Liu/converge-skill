# Proof Boundary

## User Prompt

Can we say this skill supports Codex, Claude Code, and Cursor?

## Expected Behavior

The skill should report each host claim by proof tier, distinguish installability from native interaction, and avoid claiming H2, H3, or H4 behavior without response-eval or native-proof evidence.

It should name the missing evidence required for stronger claims.

## Failure Tags

- proof-overclaim
- host-support-overclaim
- native-ui-overclaim
