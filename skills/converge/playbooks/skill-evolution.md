# Skill Evolution Playbook

Use when improving Converge or any reusable skill, rule, instruction file, agent prompt, or eval suite.

The goal is not to make the skill longer. The goal is to make future behavior more reliable with the smallest proven change.

## Inputs

- Current canonical skill directory.
- User objective or failure report.
- Failure trace: prompt, artifacts, response, tool outputs, and environment constraints.
- Existing eval cases, response-eval packets/results, and validator output.
- Accepted/rejected edit history if any.
- Current host docs or release notes when platform behavior may have changed.

## Protocol

1. Current-state audit: read the active skill, resources, eval cases, and validator before editing.
2. Failure mapping: map the issue to pass gates and failure tags.
3. Edit hypothesis: state the smallest behavior change that should prevent the failure.
4. Eval-before-edit: add or update an eval case when the failure can recur.
5. Optimization guard: define the edit budget, affected cases, holdout/regression cases, and reject criteria before patching.
6. Bounded patch: add, delete, or replace only the sections needed for the hypothesis.
7. Validation: run structure validators, syntax checks, eval suite checks, and response-eval review when behavior changed.
8. Response eval: generate blind packets for affected cases first, then holdout/full regression before treating behavior as proven.
9. Sync: update installed copies only after the canonical source passes.
10. Residual risk: state what the validation still does not prove.

## Bounded Edit Rules

- Prefer one strong rule over many overlapping reminders.
- Put routing and gates in `SKILL.md`; put detailed methods in playbooks or reference files.
- Do not add host-specific tool calls unless the host tool is actually available or guarded by availability checks.
- Do not weaken friction controls to increase activation. High-frequency usefulness comes from immediate value and fast handoff.
- Do not optimize for one anecdote by making broad behavior worse.

## Optimization Guard

- Affected cases guide the patch; holdout/regression cases judge whether the patch generalized.
- Default edit budget: no more than three localized add/delete/replace chunks unless a broad failure is proven.
- Record rejected edits and why they were rejected when an attempted patch fails validation or worsens friction/safety.
- Accept an edit only when validators pass, affected behavior improves or stays correct, holdout behavior does not regress, and proof scope is stated.
- A single passing known case is useful evidence, not behavior-level proof.

## Eval Case Rules

Add or update an eval case when:
- A failure can recur.
- A new boundary is introduced.
- A host-specific behavior could be hallucinated.
- A safety/security rule needs a regression guard.
- A research or technology-route rule could drift.

Each eval case needs:
- `## User Prompt`
- `## Expected Behavior`
- `## Failure Tags`

## Validation Checklist

- Canonical source passes `scripts/check_converge_skill.py`.
- Eval suite passes `scripts/check_converge_eval_suite.py`; release checks require `--min-cases-per-tag 2` to prevent single-case tag coverage.
- Coverage matrix passes `scripts/check_converge_coverage_matrix.py` so changes do not silently lose output-profile, host, context, risk, or evidence-surface coverage.
- Behavior changes have response-eval packets and a generated `RUNBOOK.md` from `scripts/build_converge_response_eval.py`; affected cases and at least one holdout/regression case are reviewed, and pilot/holdout batches are selected with `scripts/select_converge_response_eval_batch.py`, progress is summarized with `scripts/summarize_converge_response_eval.py`, and filled full-run results pass `scripts/check_converge_response_eval.py --require-all-cases --require-real-results` when behavior-level proof is claimed.
- Main skill stays concise and references any new resource.
- New failure tags are represented in `eval-rubric.md`.
- Output profile names stay consistent across `SKILL.md`, `reference.md`, templates, and state.
- Installed copies for Claude Code, Cursor, and opencode match canonical source when this skill is installed there, and Cursor has the generated `~/.cursor/rules/converge.mdc` bridge; use `scripts/sync_converge_install.py` instead of ad hoc copy commands.
- Release gate passes `scripts/check_converge_release.py` after sync when checking installed copies is possible; pass `--response-results-dir` to include real response-eval evidence.

## Anti-Patterns

- One-shot rewrite without failure evidence.
- Shipping a patch because it passes only the known case that inspired the edit.
- Adding a checklist for every edge case until simple tasks feel heavy.
- Hiding tool assumptions in prose instead of checking tool availability.
- Treating a passing validator as proof of real-world usefulness.
- Treating a single user preference as durable memory without explicit permission.
- Installing or trusting third-party skills without provenance and full-file review.

## Output Shape

```markdown
**Failure / Objective**
[What changed or failed.]

**Edit Hypothesis**
[Smallest behavior change expected to help.]

**Patch**
[Files and sections changed.]

**Validation**
[Commands/eval checks and results.]

**Sync**
[Where installed copies were updated.]

**Still Not Proven**
[What remains uncertain.]
```
