# Converge Protocol v1 Readiness

Last reviewed: 2026-05-30

This page is the release-readiness ledger for Converge Protocol v1. It keeps
the public claim smaller than the ambition until evidence proves more.

## Current Launch Boundary

Converge can currently be described as a reusable, installable, and
release-checked owner-mode intent reconstruction protocol with scoped real
behavior evidence.

Do not describe it as fully proven across every host, every interaction mode, or
every eval case yet.

## Requirement Audit

| Requirement | Current evidence | Status | Remaining gate |
|---|---|---|---|
| Protocol boundary is clear | `docs/protocol.md`, `protocol/schemas/*`, `python3 -m converge validate --protocol-only` | Structurally ready | Keep schemas stable while adding more real behavior proof. |
| Skill implementation is coherent | `skills/converge/SKILL.md`, `check_converge_skill.py`, `scripts/verify.py` | Ready for scoped release | Continue behavior eval before broad quality claims. |
| Host adapters are explicit | `host-adapters.json`, `host-capability-contract.tsv`, `host-support-ledger.md` | H0/H1/H2 boundaries are clear | H3 native runs for Codex Plan, Claude Code, and Cursor remain missing. |
| Install and sync are verifiable | `sync_converge_install.py`, `check_converge_release.py --source skills/converge --targets all` | Release-checked for H1 targets | Keep installed copies synced before any release. |
| IntentBench exists | `intentbench/manifest.json`, `python3 -m converge benchmark --validate` | Structural benchmark ready | Fill more real response-eval results before claiming broad behavior coverage. |
| Before/after gallery exists | `gallery/examples.json`, `site/index.html`, `scripts/check_gallery_site.py` | Validated with everyday-usefulness examples | Add production-workflow examples after H4 evidence exists. |
| Current technical routes use evidence | `codex-web-tech-route-20260529`, `codex-web-current-model-20260530`, `codex-web-current-research-20260530` | Five scoped web-assisted passes | Add production-like route runs with user repo constraints and real validation spikes. |
| Low-expression intent converges | `low-expression-idea.md`, `mixed-artifact-intake.md`, Codex Default fallback cases, `codex-headless-everyday-usefulness-20260530` | Stronger scoped pilot | Add overbroad product, research plan, and architecture ambiguity runs. |
| Completion and proof boundaries hold | `host-support-proof-boundary.md`, `completion-proof-overclaim.md`, `shallow-proof-publish-claim.md`, proof-tier docs | Three scoped passes | Add dev-handoff, extended-host, and production-like proof-boundary runs. |
| Public trust story is defensible | README, quickstart, install docs, release checklist, support ledger | Defensible for scoped claims | Needs external user install trial and H4 production-like workflow evidence. |

## Aggregate Behavior Evidence

Use the multi-directory summary to audit all stored real response-eval evidence:

```bash
python3 -B skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-headless-20260529/results \
  evidence/response-eval/codex-headless-choice-20260529/results \
  evidence/response-eval/codex-headless-host-proof-20260529/results \
  evidence/response-eval/codex-web-tech-route-20260529/results \
  evidence/response-eval/codex-headless-low-expression-20260529/results \
  evidence/response-eval/codex-headless-mixed-artifact-20260530/results \
  evidence/response-eval/codex-web-current-model-20260530/results \
  evidence/response-eval/codex-headless-proof-discipline-20260530/results \
  evidence/response-eval/codex-web-current-research-20260530/results \
  evidence/response-eval/codex-headless-everyday-usefulness-20260530/results \
  --root skills/converge \
  --require-real-results \
  --show-axes \
  --show-cases
```

Current aggregate result:

- 40 expected cases.
- 16 stored real results.
- 16 valid Pass.
- 0 Fail.
- 24 missing real results.
- Covered output profiles: Action Plan, Conversation Reply, Decision Brief, Direct Answer, Expression Draft, Technology Route, Thinking Reply, Universal Intent Guard.
- Covered host surfaces: Codex Default and generic only.
- L2 count threshold is reached and everyday-usefulness is now covered by scoped pilots, but native interaction and production-workflow coverage are still incomplete.

## Next Evidence Ladder

Use these gates in order. Do not skip a lower gate when making public claims.

| Gate | Purpose | Minimum evidence |
|---|---|---|
| L0 Structural | Repository is internally consistent | `python3 scripts/verify.py` and CI green. |
| L1 Install | Supported local host copies match source | `sync_converge_install.py` plus `check_converge_release.py --source skills/converge --targets all`. |
| L2 Behavior Pilot | Core behavior works in real responses | At least 12 real response-eval passes covering intent, current research, proof boundaries, mixed artifacts, direct reply, and planning. |
| L3 Native Interaction | Native question UI paths are real | Passing native-proof JSON plus response-eval result for Codex Plan, Claude Code, and Cursor. |
| L4 Production Workflow | It helps on real work, not just prompts | Multiple scoped real tasks with files, research, execution, validation, and review notes. |
| L5 Public Release | Strangers can install, understand, and trust it | Green CI, release checklist, docs-site review, external install trial, and claim boundary review. |

## Highest-Leverage Next Runs

The next response-eval runs should target gaps that affect public trust:

1. `dev-handoff-after-docs.md`, `extended-host-capability-boundary.md`, and `full-converge-docs-complex-project.md` to harden handoff and broad support boundaries.
2. `architecture-ambiguity.md`, `research-plan.md`, and `overbroad-product.md` to prove larger planning and discovery behavior.
3. `context-poisoning-boundary.md`, `context-poisoning-rule-review.md`, and `inaccessible-link-boundary.md` to harden context-trust boundaries.
4. `codex-plan-native-question-ui.md`, `claude-native-question-bridge.md`, and `cursor-native-question-bridge.md` only in real interactive hosts with native proof artifacts.

## Claim Policy

Allowed today:

```text
Converge Protocol v1 is structurally validated, release-checked, installed for
multiple local agent hosts, and backed by 16 scoped real Codex response-eval
passes.
```

Not allowed yet:

```text
Converge is fully proven across Codex, Cursor, Claude Code, and every supported
host, or complete across all 40 IntentBench cases.
```
