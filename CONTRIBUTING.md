# Contributing

Converge changes should be evidence-driven.

## Development Rules

- Start from a failure trace, a user objective, or a clear improvement hypothesis.
- Add or update an eval case when the failure can recur.
- Keep patches bounded; prefer one strong rule over several overlapping reminders.
- Do not promote host support claims without matching source evidence, capability contract updates, eval coverage, and validation output.
- Do not claim behavior-level proof from synthetic smoke results.

## Required Checks

```bash
python3 scripts/verify.py
```

For local host install consistency:

```bash
python3 skills/converge/scripts/sync_converge_install.py
python3 skills/converge/scripts/check_converge_release.py --source skills/converge --targets all
```
