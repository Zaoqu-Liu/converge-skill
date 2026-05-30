# Release Checklist

Use this before publishing a new Converge release.

## Local Checks

```bash
python3 scripts/verify.py
python3 -m converge validate --protocol-only
python3 -m converge doctor --json
python3 -m converge benchmark --validate
python3 -m converge compatible compatible/examples
python3 skills/converge/scripts/check_converge_response_eval.py evidence/response-eval/codex-headless-20260529/results --root skills/converge --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py evidence/response-eval/codex-headless-choice-20260529/results --root skills/converge --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py evidence/response-eval/codex-headless-host-proof-20260529/results --root skills/converge --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py evidence/response-eval/codex-web-tech-route-20260529/results --root skills/converge --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py evidence/response-eval/codex-headless-low-expression-20260529/results --root skills/converge --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py evidence/response-eval/codex-headless-mixed-artifact-20260530/results --root skills/converge --require-real-results
python3 skills/converge/scripts/check_converge_response_eval.py evidence/response-eval/codex-web-current-model-20260530/results --root skills/converge --require-real-results
python3 skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-headless-20260529/results \
  evidence/response-eval/codex-headless-choice-20260529/results \
  evidence/response-eval/codex-headless-host-proof-20260529/results \
  evidence/response-eval/codex-web-tech-route-20260529/results \
  evidence/response-eval/codex-headless-low-expression-20260529/results \
  evidence/response-eval/codex-headless-mixed-artifact-20260530/results \
  evidence/response-eval/codex-web-current-model-20260530/results \
  --root skills/converge \
  --require-real-results \
  --show-axes \
  --show-cases
python3 scripts/check_gallery_site.py
python3 -m converge native-proof --out /tmp/converge-native-proof
python3 skills/converge/scripts/sync_converge_install.py
python3 skills/converge/scripts/check_converge_release.py --source skills/converge --targets all
```

## Evidence Checks

- `skills/converge/host-source-evidence.md` is current for changed host claims.
- `skills/converge/host-adapters.json` contains every supported host and matches install/release behavior.
- `skills/converge/host-capability-contract.tsv` contains every supported host.
- `skills/converge/host-support-ledger.md` uses proof-tiered language.
- `skills/converge/eval-coverage.tsv` covers every required host, context, evidence, risk, trigger, and output surface.
- `intentbench/manifest.json` validates and every suite selector maps to at least one eval case.
- `docs/v1-readiness.md` matches the aggregate behavior evidence and states remaining proof gates.
- `compatible/examples/*/converge-compatible.json` validates and every bundled compatible artifact references real entrypoints and eval cases.
- Stored evidence under `evidence/response-eval/codex-headless-20260529`, `evidence/response-eval/codex-headless-choice-20260529`, `evidence/response-eval/codex-headless-host-proof-20260529`, `evidence/response-eval/codex-web-tech-route-20260529`, `evidence/response-eval/codex-headless-low-expression-20260529`, `evidence/response-eval/codex-headless-mixed-artifact-20260530`, and `evidence/response-eval/codex-web-current-model-20260530` validates with `--require-real-results`.
- `gallery/examples.json` validates, references real eval cases, and renders through `site/index.html`.
- No H2/H3/H4 claim is made without matching response-eval or host-run evidence.
- No H3 claim is made without a passing native-proof JSON validated with `--require-real-artifacts`.

## Repository Checks

- `VERSION` matches the release tag.
- `CHANGELOG.md` has a dated entry.
- Protocol schemas and examples pass `python3 -m converge validate --protocol-only`.
- Compatible manifest validation passes `python3 -m converge compatible compatible/examples`.
- Gallery/site validation passes `python3 scripts/check_gallery_site.py`.
- GitHub Actions `Validate` passes on `main`.
- No generated files such as `__pycache__`, `.pyc`, `.DS_Store`, or swap files are tracked.

## Release Commands

```bash
git tag v$(cat VERSION)
git push origin main
git push origin v$(cat VERSION)
gh release create v$(cat VERSION) --title "Converge Skill $(cat VERSION)" --notes-file CHANGELOG.md
```

Only create a release after CI is green.
