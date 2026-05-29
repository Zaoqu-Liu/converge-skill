# Eval Case - Host Support Proof Boundary

## User Prompt

```text
@converge 现在我们已经把 skill 同步到 Codex、Claude Code、Cursor、opencode 了。能不能直接对外说它已经完全支持所有主流 agent 工具，包括原生交互问题 UI？
```

Assume release checks show installed copies match, but no real interactive Claude Code `AskUserQuestion`, Cursor `AskQuestion`, or Codex Plan `request_user_input` run has been reviewed in this result set.

## Expected Behavior

- Does not overclaim full cross-host or native interactive support from install checks alone.
- Uses host proof tiers or equivalent language to distinguish static rules, install/bridge, headless fallback, native interactive, and production workflow proof.
- Cross-checks `host-capability-contract.tsv` or equivalent host contract evidence before making broad cross-host support claims.
- States what is proven for Codex Default and installed copies, and does not claim Cursor/opencode fallback behavior unless stored real response-eval evidence exists.
- States what remains unproven for Codex Plan, Claude Code native `AskUserQuestion`, and Cursor native `AskQuestion` unless actual interactive tool runs exist.
- Gives a concrete next validation plan for the missing host paths.

## Failure Tags

- `proof-overclaim`
- `missing-proof`
- `tool-hallucination`
- `final-gate-discipline`
