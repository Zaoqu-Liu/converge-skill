# Release Checklist

Use this before publishing a new Converge release.

## Local Checks

```bash
python3 scripts/verify.py
python3 skills/converge/scripts/sync_converge_install.py
python3 skills/converge/scripts/check_converge_release.py --source skills/converge --targets all
```

## Evidence Checks

- `skills/converge/host-source-evidence.md` is current for changed host claims.
- `skills/converge/host-capability-contract.tsv` contains every supported host.
- `skills/converge/host-support-ledger.md` uses proof-tiered language.
- `skills/converge/eval-coverage.tsv` covers every required host, context, evidence, risk, trigger, and output surface.
- No H2/H3/H4 claim is made without matching response-eval or host-run evidence.

## Repository Checks

- `VERSION` matches the release tag.
- `CHANGELOG.md` has a dated entry.
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
