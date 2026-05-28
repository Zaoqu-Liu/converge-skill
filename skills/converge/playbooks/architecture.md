# Architecture Playbook

Use for system design, technical strategy, implementation planning, API/data design, migration planning, and dev handoff.

## Architecture Reconstruction

Clarify:
- Business/user outcome.
- Existing system shape.
- Actors, tenants, roles, and ownership boundaries.
- Resources, actions, policies, and data-scope rules.
- Constraints and non-negotiables.
- Interfaces and ownership boundaries.
- Data flow.
- Enforcement points: UI, API, service layer, database, background jobs, and admin tooling.
- Failure modes.
- Migration/compatibility needs.
- Observability and validation.

## Ambiguity Gate

For broad architecture requests, especially when the user says another engineer or agent will build it, do not jump straight to an implementation spec. First produce an architecture discovery package or `converge-docs/`-style plan that settles:

- actors and trust boundaries
- resources and lifecycle states
- allowed actions and denied actions
- policy ownership and override rules
- enforcement points
- audit, observability, migration, and rollback needs
- open questions that would materially change the design

If these are not settled, keep concrete schemas, endpoint contracts, class names, migrations, and task assignments at sketch level. Label them as candidate shapes, not implementation-ready contracts.

## Explore Before Asking

When a repo is available, inspect files before asking:
- manifests and configs
- entrypoints
- schemas/types
- API routes
- existing patterns
- test setup

Do not ask the user where things are if the repository can answer.

## Technology Route Boundary

If the architecture decision depends on current framework, model, cloud, database, protocol, library, or platform capability, load `playbooks/technology-route.md` and run the Freshness & Evidence Gate before recommending.

Do not ask the user to supply facts that official docs, release notes, repo manifests, changelogs, or current research can answer. Inspect the repo first, then search if the decision depends on current external facts.

## Output Routing

- If the user wants design only: Decision Brief, Technology Route, or Action Plan.
- If implementation is next: Converge Docs.
- If another engineer/agent must build it: Dev Handoff.
- If the user asks for architecture "for engineers" and no repo or product context is available, output the Converge Docs skeleton in chat and ask only the highest-leverage missing question. Do not present the response as an implementation-ready handoff.

## Handoff Gate

Do not write detailed API contracts until the product behavior and ownership boundaries are settled. A fake precise spec is worse than an honest open question.

Before Dev Handoff, require:
- a settled architecture recommendation
- a recorded assumption ledger
- a risk ledger
- acceptance criteria
- at least one validation spike
- explicit notes for which API/data examples are still placeholders
