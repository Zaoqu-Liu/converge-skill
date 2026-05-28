# Technology Route Playbook

Use for current technical path decisions: stack, framework, model, agent framework, library, protocol, database, cloud service, architecture pattern, deployment route, build-vs-buy, migration, or platform choice.

## Route Reconstruction

Clarify:
- Objective and user/business outcome.
- Greenfield or brownfield context.
- Existing stack, repo constraints, team skill, deployment environment.
- Non-negotiables: cost, latency, privacy, compliance, offline, self-hosting, scale, integration.
- Time horizon: prototype, production, migration, long-term platform.
- Reversibility and migration cost.

## Freshness Workflow

1. Inspect local context first: manifests, lockfiles, configs, existing architecture, tests, deployment files.
2. Identify drift-prone claims: version support, maturity, GA/preview status, pricing, benchmarks, model capability, ecosystem health, security posture.
3. Verify with the strongest available sources before recommending.
4. Separate options into:
   - Current Best Known: best fit now for this context.
   - Safe Default: mature path if reliability matters most.
   - Frontier Bet: promising but higher uncertainty.
   - Avoid/Hold: attractive but not worth it now.

## Evidence Snapshot

Every non-trivial Technology Route must include:

```markdown
## Evidence Snapshot
| Claim | Source Class | Source/Link | Last Verified | Implication |
|---|---|---|---|---|
```

Source Class examples: official docs, release notes, source repo, standard/spec, primary paper, independent radar, benchmark with method, security advisory, vendor blog, community report.

If a source link is unavailable, name the document, repository, local file, or command output used as evidence.

Maturity/status discipline:
- Preserve exact source labels such as GA, beta, preview, pre-GA, experimental, deprecated, unsupported, production-ready, or version-specific.
- Do not convert `pre-GA`, `preview`, `beta`, `experimental`, or search-snippet wording into `GA`, `stable`, or `production-ready`.
- If only a search result snippet was checked, say `snippet-level evidence` and keep the recommendation conditional until the source page or release note is inspected.

## Comparison Matrix

```markdown
| Option | Fit | Maturity | Ecosystem | Ops Burden | Lock-in | Cost | Security/Risk | Reversibility |
|---|---|---|---|---|---|---|---|---|
```

## Recommendation Shape

```markdown
**Current Best Known Route**
[Recommendation.]

**Why This Beats Alternatives**
[Context-specific rationale.]

**Why Not the Trendier Option**
[Explain if relevant.]

**Validation Spike**
[1-5 day proof that tests the riskiest assumption.]

**Revisit Trigger**
[What event, release, cost, scale, or requirement should reopen the decision.]
```

## Anti-Patterns

- Newest equals best.
- MCP by default: use MCP when interoperability, governed access, or tool contracts justify it; otherwise a CLI/API with structured output may be simpler and more faithful.
- Benchmark cargo cult: do not choose a model/framework from a headline benchmark without task-specific eval.
- Vendor gravity: do not pick a platform only because its docs are polished.
- Fake portability: claiming portability while relying on provider-specific auth, tracing, storage, or deployment behavior.
- Infinite optionality: list fewer options, but make the tradeoffs sharper.
