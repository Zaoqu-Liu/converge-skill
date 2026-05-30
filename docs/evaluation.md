# Evaluation

Converge uses structural validation, coverage validation, and response evaluation.

## Repository Verification

```bash
python3 scripts/verify.py
```

This runs:

- `skills/converge/scripts/check_converge_skill.py`
- `skills/converge/scripts/check_converge_eval_suite.py --min-cases-per-tag 2`
- `skills/converge/scripts/check_converge_coverage_matrix.py`
- response-eval validator self-tests
- stored Codex headless response-eval evidence validation with `--require-real-results`
- summary and batch selector self-tests
- native-proof validator self-tests
- IntentBench validator self-tests and manifest validation
- Converge-compatible manifest validator self-test and bundled example validation
- gallery/site validation for before/after examples and docs-site wiring
- release smoke checks with `--skip-installs`

## Local Install Release Check

```bash
python3 skills/converge/scripts/check_converge_release.py --source skills/converge --targets all
```

This additionally compares installed copies for supported H1 install targets.

## Behavior-Level Evidence

Use response-eval packets for behavior claims:

```bash
python3 skills/converge/scripts/build_converge_response_eval.py \
  --root skills/converge \
  --out /tmp/converge-response-eval \
  --case extended-host-capability-boundary.md \
  --skill-path skills/converge/SKILL.md
```

Full behavior-level proof requires real filled result files:

```bash
python3 skills/converge/scripts/check_converge_response_eval.py RESULTS_DIR \
  --root skills/converge \
  --require-all-cases \
  --require-real-results
```

Do not use synthetic release-smoke results as proof of real behavior.

## Stored Response-Eval Evidence

The repository contains scoped real Codex headless evidence runs:

```bash
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-20260529/results \
  --root skills/converge \
  --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-choice-20260529/results \
  --root skills/converge \
  --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-host-proof-20260529/results \
  --root skills/converge \
  --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-web-tech-route-20260529/results \
  --root skills/converge \
  --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-low-expression-20260529/results \
  --root skills/converge \
  --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-mixed-artifact-20260530/results \
  --root skills/converge \
  --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-web-current-model-20260530/results \
  --root skills/converge \
  --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-headless-proof-discipline-20260530/results \
  --root skills/converge \
  --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-web-current-research-20260530/results \
  --root skills/converge \
  --require-real-results
```

These prove only the stored `codex-default-no-native-ui.md`, `codex-default-choice-survey-trap.md`, `host-support-proof-boundary.md`, `technology-route-current-stack.md`, `low-expression-idea.md`, `mixed-artifact-intake.md`, `current-model-claim-needs-citations.md`, `completion-proof-overclaim.md`, `shallow-proof-publish-claim.md`, `latest-library-advice.md`, `benchmark-headline-route-trap.md`, and `researched-answer-citations.md` cases. They are not full benchmark proof and do not promote Cursor, Claude Code, or native question UI paths.

The `codex-web-tech-route-20260529` run is the first stored current-research Technology Route proof. It supports a scoped claim that Converge can attach current source evidence when web access is available; it does not prove the chosen route is universally best.

The `codex-headless-low-expression-20260529` run is the first stored low-expression ideation proof. It supports a scoped claim that Converge can turn a vague high-ambition product idea into an owner default, validation plan, and concise route question.

The `codex-headless-mixed-artifact-20260530` run is the first stored mixed-artifact diagnosis proof. It supports a scoped claim that Converge can inspect available screenshot, PRD, and log artifacts before naming the real problem.

The `codex-web-current-model-20260530` run is the first stored current-model comparison proof. It supports a scoped claim that Converge can keep source traceability for current coding-agent recommendations even when the user asks to omit sources.

The `codex-headless-proof-discipline-20260530` run is the first stored completion-proof discipline proof. It supports a scoped claim that Converge can refuse to inflate lint-only evidence into completion, perfection, full-project verification, or publish-readiness claims.

The `codex-web-current-research-20260530` run adds three stored current-research proofs. It supports a scoped claim that Converge can use official/current sources for frontend route decisions, refuse benchmark-headline migrations, and refuse fabricated citations for unnamed production-readiness targets.

Aggregate multiple stored runs when auditing release readiness:

```bash
python3 skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-headless-20260529/results \
  evidence/response-eval/codex-headless-choice-20260529/results \
  evidence/response-eval/codex-headless-host-proof-20260529/results \
  evidence/response-eval/codex-web-tech-route-20260529/results \
  evidence/response-eval/codex-headless-low-expression-20260529/results \
  evidence/response-eval/codex-headless-mixed-artifact-20260530/results \
  evidence/response-eval/codex-web-current-model-20260530/results \
  evidence/response-eval/codex-headless-proof-discipline-20260530/results \
  evidence/response-eval/codex-web-current-research-20260530/results \
  --root skills/converge \
  --require-real-results \
  --show-axes \
  --show-cases
```

See `docs/v1-readiness.md` for the current aggregate boundary and next proof gates.

## Native Interaction Evidence

Use native-proof packets for H3 claims:

```bash
python3 skills/converge/scripts/build_converge_native_proof.py \
  --root skills/converge \
  --out /tmp/converge-native-proof
```

Fill the generated proof JSON only after a real interactive host run. Then validate:

```bash
python3 skills/converge/scripts/check_converge_native_proof.py \
  /tmp/converge-native-proof/proofs \
  --root skills/converge \
  --require-real-artifacts
```

Do not use install checks, official docs, or CLI/headless fallback output as H3 proof.

## IntentBench

IntentBench packages the eval suite into benchmark runpacks with blind prompts, review packets, result stubs, and coverage metadata:

```bash
python3 -m converge benchmark --validate
python3 -m converge benchmark --out /tmp/intentbench
python3 -m converge benchmark --suite evidence --out /tmp/intentbench-evidence
```

Filled results can be summarized with:

```bash
python3 -m converge benchmark --results /tmp/intentbench/results --require-real-results
```

Use this for before/after comparisons: the benchmark should show which cases, failure tags, and coverage axes improved or regressed. Do not convert it into a numeric quality score.

## Compatible Manifest Evidence

Use the compatible validator for third-party skills, rules, workflows, prompt packs, and host adapters:

```bash
python3 -m converge compatible compatible/examples
python3 scripts/check_converge_compatible.py compatible/examples/research-route-skill
```

This does not prove real behavior. It proves that the artifact declares the Converge Protocol version, entrypoints, host support claims, proof boundaries, eval case coverage, and strict proof policies in a machine-checkable form.

## Gallery And Docs Site

The public-facing gallery is also validated:

```bash
python3 scripts/check_gallery_site.py
```

This verifies that `gallery/examples.json` uses the expected schema, references real eval cases, has explicit proof boundaries, and that `site/index.html` renders the examples while linking to the protocol, install, host support, evaluation, and IntentBench artifacts.
