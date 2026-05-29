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
- summary and batch selector self-tests
- native-proof validator self-tests
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
