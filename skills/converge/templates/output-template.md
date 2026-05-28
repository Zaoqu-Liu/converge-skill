# Converge Output Templates

Use the smallest profile that fully satisfies the user. Do not force every task into files.

## Universal Intent Guard

```markdown
**Real Objective**
[One sentence.]

**Blind Execution Risk**
[What could go wrong if we just do the literal task.]

**Recommended Execution Path**
[How to proceed.]

**Assumptions Carried Forward**
[Only material assumptions.]

**Immediate Next Action**
[Do or hand off now.]
```

## Thinking Reply

```markdown
**Bottom Line**
[Clear judgment.]

**Why**
[Reasoning, tradeoffs, and what most people miss.]

**My Recommendation**
[Owner recommendation.]

**What Would Change This**
[Assumptions or new evidence that would alter the answer.]
```

## Direct Answer

```markdown
[Answer first.]

[Rationale.]

[Caveats/assumptions if needed.]

[Next action if useful.]
```

## Conversation Reply

```markdown
**Read**
[What the other person likely means/wants.]

**Stance**
[Recommended position.]

**Draft**
[Sendable reply.]

**Variant**
[Optional softer/stronger version.]

**Risk**
[Only if wording can backfire.]
```

## Expression Draft

```markdown
**Intent**
[What this piece must accomplish.]

**Audience**
[Who it is for.]

**Structure**
[Short outline.]

**Draft**
[Final-quality draft.]

**Optional Variants**
[Only if useful.]
```

## Action Plan

```markdown
# Action Plan

## Goal
[Specific outcome.]

## Recommended Path
[Owner recommendation and rationale.]

## Phases

### Phase 1 - [Theme]
- [Complete, valuable deliverable]

### Phase 2 - [Theme]
- [Complete, valuable deliverable]

### Phase 3 - [Theme]
- [Complete, valuable deliverable]

## Tasks
| Task | Owner | Depends On | Done When |
|---|---|---|---|
| | | | |

## Risks and Mitigations
| Risk | Why It Matters | Mitigation |
|---|---|---|
| | | |

## Validation
[How to know it worked.]

## Immediate Next Action
[What to do today.]
```

## Decision Brief

```markdown
# Decision Brief

## Decision
[What must be decided.]

## Recommendation
[Pick one, with rationale.]

## Options
| Option | Upside | Downside | Best If |
|---|---|---|---|
| | | | |

## Criteria
[The criteria that actually matter.]

## Why Not the Alternatives
[Specific reasons.]

## Reversibility
[How costly it is to be wrong.]

## Revisit Trigger
[What evidence should cause reconsideration.]

## Proof / Validation
[What evidence makes the recommendation decision-ready, and what remains unproven.]
```


## Skill Evolution

```markdown
# Skill Evolution

## Objective
[What skill or reusable workflow is being improved.]

## Failure Trace / Hypothesis
[Observed failure, user objective, or improvement hypothesis.]

## Failure Tags
- [rubric tag]

## Eval / Validator Change
[New or updated eval case, validator rule, or why no new eval is needed.]

## Bounded Patch
[Specific add/delete/replace scope.]

## Validation Output
[Commands and results.]

## Sync Targets
[Installed copies or downstream tools updated.]

## Remaining Uncertainty
[What is still not proven.]
```

## Technology Route

```markdown
# Technology Route

## Current Best Known Route
[Recommendation and scope.]

## Evidence Snapshot
| Claim | Source Class | Source/Link | Last Verified | Implication |
|---|---|---|---|---|
| | | | | |

## Options Compared
| Option | Fit | Maturity | Ecosystem | Ops Burden | Lock-in | Cost | Security/Risk | Reversibility |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## Recommendation
[Why this path wins for this context.]

## Why Not the Alternatives
[Specific reasons.]

## Validation Spike
[Smallest test that proves/disproves the riskiest assumption.]

## Revisit Trigger
[What should cause this decision to be reopened.]

## Proof / Validation
[Commands, sources, files, or spike results that support this route; mark missing proof explicitly.]
```

## General Converge Docs

Use for non-product complex work:

```text
converge-docs/
  00-understanding.md
  01-output.md
  02-action-plan.md
  03-risks-and-assumptions.md
  04-discovery-log.md
```

### 00-understanding.md

```markdown
# Understanding

## User Said

## Inferred Goal

## Current Blocker

## Desired End State

## Constraints

## User Model

## Owner Recommendation
```

### 01-output.md

```markdown
# [Profile Name]

[Final artifact appropriate to the profile.]
```

### 02-action-plan.md

Use the Action Plan template.

### 03-risks-and-assumptions.md

```markdown
# Risks and Assumptions

## Assumptions
| Assumption | Status | Validation |
|---|---|---|

## Risks
| Risk | Why It Matters | Mitigation |
|---|---|---|

## Open Decisions
| Decision | Needed By | Owner |
|---|---|---|
```

### 04-discovery-log.md

```markdown
# Discovery Log

## Rounds

## Questions and Answers

## Research

## Decisions

## Pressure Tests
```

## Product/Engineering Converge Docs

Use when the work is product, architecture, or implementation-heavy:

```text
converge-docs/
  01-context.md
  02-solution.md
  03-execution.md
  04-risks.md
  05-discovery.md
```

Keep every section traceable to discovery rounds or stated assumptions. Use Mermaid only in final docs, not during discovery.

