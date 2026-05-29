# Release Checklist

Use this before publishing a new Converge release.

## Local Checks

```bash
python3 scripts/verify.py
python3 -m converge validate --protocol-only
python3 -m converge doctor --json
python3 -m converge benchmark --validate
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
- No H2/H3/H4 claim is made without matching response-eval or host-run evidence.
- No H3 claim is made without a passing native-proof JSON validated with `--require-real-artifacts`.

## Repository Checks

- `VERSION` matches the release tag.
- `CHANGELOG.md` has a dated entry.
- Protocol schemas and examples pass `python3 -m converge validate --protocol-only`.
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
