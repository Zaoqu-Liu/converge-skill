# Converge Skill

[![Validate](https://github.com/Zaoqu-Liu/converge-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Zaoqu-Liu/converge-skill/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Owner-mode intent reconstruction for fuzzy, high-ambiguity work across modern AI agent hosts.

Converge turns under-specified human input into a clear understanding, a defensible recommendation, and a directly usable output: a reply, plan, decision brief, technology route, product/architecture document, or implementation handoff.

This repository now contains both the canonical skill and the seed reference implementation for **Converge Protocol v1**.

## Why This Exists

Most agent failures do not start with bad code. They start with a bad read of the user's intent:

- the user has a rough idea but cannot fully articulate it yet
- the agent asks too many low-value questions
- the agent writes a document before the goal is stable
- the agent gives current technical advice from stale memory
- the agent claims cross-host support from install files instead of real evidence

Converge is designed to make an agent useful before the user has perfect wording. It infers, challenges, recommends, researches when facts can drift, and keeps proof boundaries explicit.

## What It Covers

The canonical skill lives at:

```text
skills/converge/SKILL.md
```

It includes:

- an owner-mode intent reconstruction protocol
- Converge Protocol v1 schemas for run state, host capability, host adapter registry, eval results, and compatible manifests
- a reference `converge` CLI/runtime for validation, host doctor checks, install, pack, eval, and release gates
- low-friction modes for simple tasks and deep modes for ambiguous work
- evidence gates for current technical decisions
- high-risk boundaries for medical, legal, financial, security, compliance, and irreversible decisions
- context intake rules for files, screenshots, links, repos, configs, and instruction-bearing artifacts
- cross-host adapter rules for Codex, Claude Code, Cursor, opencode, Cline, Google Antigravity, Gemini CLI, GitHub Copilot, Windsurf, Continue, Aider, and unknown future hosts
- a machine-readable host adapter registry that drives `doctor`, install target selection, release checks, and TSV drift validation
- H3 native interaction proof packets for real native question UI/tool evidence
- IntentBench benchmark manifests and runpacks for before/after pass/fail comparison by coverage axis
- before/after gallery data and a static docs site that make Converge behavior legible before installation
- eval cases, coverage matrix, response-eval tools, release checks, and install sync scripts

## Support Claims

Converge uses proof tiers. The repository intentionally avoids broad support claims unless evidence exists.

| Tier | Meaning | Evidence required |
|---|---|---|
| H0 | Documented rule coverage | Skill docs and eval case cover the host boundary |
| H1 | Installed or bridged | Installed copy or bridge matches canonical source; release check passes |
| H2 | Fallback behavior tested | Real response-eval in CLI/headless/non-interactive mode passes |
| H3 | Native interactive behavior tested | Real host run uses native question UI/tool correctly |
| H4 | Production-like workflow tested | Multiple real tasks pass with scoped proof |

Current release-checked install targets:

- Claude Code: `~/.claude/skills/converge`
- Cursor: `~/.cursor/skills/converge` plus `~/.cursor/rules/converge.mdc`
- opencode: `~/.config/opencode/skills/converge`
- Cline: `~/.cline/skills/converge`
- Google Antigravity: `~/.gemini/antigravity/skills/converge`

Instruction-surface coverage is documented for Gemini CLI, GitHub Copilot, Windsurf, Continue, and Aider, but those are not claimed as native skill installs.

## Install

Fast path:

```bash
git clone https://github.com/Zaoqu-Liu/converge-skill.git
cd converge-skill
python3 scripts/verify.py
python3 skills/converge/scripts/sync_converge_install.py
```

Clone the repository and sync the canonical skill into supported local agent hosts:

```bash
python3 skills/converge/scripts/sync_converge_install.py
```

To sync only selected hosts:

```bash
python3 skills/converge/scripts/sync_converge_install.py --targets claude,cursor,opencode
```

See [docs/install.md](docs/install.md) for host-specific notes.

See [docs/quickstart.md](docs/quickstart.md) for the five-minute setup path.

## Validate

Run the repository validation suite:

```bash
python3 scripts/verify.py
```

Validate only protocol schemas/examples:

```bash
python3 -m converge validate --protocol-only
```

Inspect local host support state:

```bash
python3 -m converge doctor
```

Build H3 native interaction proof packets:

```bash
python3 -m converge native-proof --out /tmp/converge-native-proof
```

Build an IntentBench runpack:

```bash
python3 -m converge benchmark --validate
python3 -m converge benchmark --out /tmp/intentbench
```

For an installed console command:

```bash
python3 -m pip install -e .
converge validate --protocol-only
converge doctor
```

The verifier runs the Converge structural validator, eval-suite checks, coverage matrix, response-eval self-tests, smoke packet generation, script compilation, and release gate without requiring user-local install directories.

Validate the public-facing gallery and static docs site:

```bash
python3 scripts/check_gallery_site.py
```

For local install consistency across supported hosts:

```bash
python3 skills/converge/scripts/check_converge_release.py --source skills/converge --targets all
```

## Repository Layout

```text
.
├── skills/converge/          # canonical skill package
├── protocol/                 # Converge Protocol v1 schemas and examples
├── converge/                 # reference CLI/runtime
├── intentbench/              # IntentBench manifest and benchmark docs
├── gallery/                  # before/after examples and machine-readable data
├── site/                     # static docs site for 30-second product comprehension
├── docs/                     # repository-level install, host, and evaluation docs
├── scripts/verify.py         # repository validation entrypoint
└── .github/workflows/        # CI validation
```

## Gallery And Docs Site

- [gallery/examples.json](gallery/examples.json): machine-readable before/after examples tied to eval cases and proof boundaries.
- [gallery/README.md](gallery/README.md): gallery maintenance notes.
- [site/index.html](site/index.html): static documentation site that renders the examples and links to the protocol, install, host support, and evaluation docs.

Serve the site from the repository root so the browser can load `gallery/examples.json`:

```bash
python3 -m http.server 8765
```

Then open `http://localhost:8765/site/`.

## Evidence Files

Start here when changing support claims:

- `skills/converge/host-adapters.json`
- `skills/converge/host-source-evidence.md`
- `skills/converge/host-capability-contract.tsv`
- `skills/converge/host-adapter-matrix.md`
- `skills/converge/host-support-ledger.md`
- `skills/converge/host-native-interaction-runbook.md`
- `skills/converge/scripts/check_converge_native_proof.py`

Any change to host support should update the adapter registry, source evidence, capability contract, eval coverage, and release checks together. The protocol validator fails if `host-adapters.json` and `host-capability-contract.tsv` drift.

## Protocol And Runtime

- [docs/protocol.md](docs/protocol.md): Converge Protocol v1 object model and compatibility contract.
- [docs/cli.md](docs/cli.md): reference CLI/runtime commands.
- `protocol/schemas/`: JSON schemas.
- `protocol/examples/`: valid example instances.

## Version

Current package version: `0.1.0`. See [CHANGELOG.md](CHANGELOG.md).

## Boundary

Converge is an agent behavior skill, not a separate executable product. It does not grant tools, bypass host permissions, or make private artifacts accessible. It only instructs an agent how to reason, ask, research, act, and scope proof using the tools and permissions that the active host actually provides.

## License

MIT. See [LICENSE](LICENSE).
