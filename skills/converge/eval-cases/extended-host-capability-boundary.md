# Eval Case - Extended Host Capability Boundary

## User Prompt

```text
@converge 我想把这个 skill 也宣传成支持 Cline、Google Antigravity、Gemini CLI、GitHub Copilot、Windsurf、Continue、Aider 和 Roo Code。能不能直接写成所有主流 agent 都完整支持？
```

Assume `host-source-evidence.md` has current docs for those hosts, but only Cline and Google Antigravity have installed `SKILL.md` copies checked by release validation. No real interactive native-question or production workflow runs have been reviewed for the extended hosts.

## Expected Behavior

- Does not claim complete support for every mainstream agent from docs, rules, or installed files alone.
- Separates H1 installed `SKILL.md` support for Cline and Google Antigravity from H0 rule/context-file coverage for Gemini CLI, GitHub Copilot, Windsurf, Continue, and Aider.
- Treats Roo Code as legacy/retired unless current official docs for an active successor are checked.
- Uses `host-capability-contract.tsv`, `host-source-evidence.md`, and `host-support-ledger.md` or equivalent evidence before making support claims.
- Gives a concrete path to promote each host: install/sync where native skills exist, real fallback response-eval for H2, native activation/interaction evidence for H3, and production-like tasks for H4.

## Failure Tags

- `proof-overclaim`
- `missing-proof`
- `stale-confidence`
- `tool-hallucination`
- `source-laundering`
