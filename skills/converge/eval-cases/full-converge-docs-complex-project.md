# Eval Case - Full Converge Docs Complex Project

## User Prompt

```text
$converge 我想做一个企业知识库 AI 协作平台，涉及产品定位、权限、RAG、Agent 工作流、团队协作、商业化和 3 个月落地计划。你直接帮我完整理清楚，最好能给后续团队开干。
```

## Expected Behavior

- Uses Full Converge / Converge Docs because the work is multi-stakeholder, multi-phase, and handoff-worthy.
- Produces a useful understanding snapshot and owner recommendation before expanding into documents.
- Creates or proposes the `converge-docs/` artifact structure only after the output scope is clear.
- Separates product assumptions, technical route assumptions, evidence needs, risks, and validation spikes.
- Does not ask a broad survey; asks only the few questions that materially change scope, audience, or execution.
- Marks drift-prone technology or market claims for Freshness & Evidence Gate before final recommendation.

## Failure Tags

- `premature-docs`
- `fake-depth`
- `no-owner-recommendation`
- `over-questioning`
- `missing-evidence-snapshot`
