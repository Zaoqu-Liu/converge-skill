# Converge Response Eval Runbook

Generated for: `2 selected eval cases`

## Purpose

This runpack tests whether Converge behavior works in a real host/model response, not just whether the skill files validate structurally.

## Contents

- Cases: 2
- Case selection: `completion-proof-overclaim.md, shallow-proof-publish-claim.md`
- Skill under test: `skills/converge/SKILL.md`
- Manifest: `manifest.tsv`
- Blind prompts: `prompts/`
- Review packets: `reviews/`
- Results: `results/` when generated

Result stubs were generated in `results/`; fill every stub after collecting the model response.

## Procedure

1. Open `manifest.tsv` or choose a smaller batch with:

```bash
python3 scripts/select_converge_response_eval_batch.py --mode pilot --max-cases 10 --runpack evidence/response-eval/codex-headless-proof-discipline-20260530
```

2. Send only the matching `prompts/*.prompt.md` content to the model under test.
3. Do not show the model the eval case, expected behavior, rubric, review packet, or prior conclusions.
4. Paste the exact model answer into the matching `results/*.result.md` file, or link a response artifact there.
5. Open the matching `reviews/*.review.md` packet and judge the answer against the expected behavior and rubric.
6. For skill changes, keep the affected case separate from at least one unrelated holdout/regression case before accepting the patch.
7. Set `Verdict` to `Pass` or `Fail`.
8. Fill every gate row with `Pass`, `Fail`, `N/A`, `Blocked`, or `Conditional`, plus concrete evidence.
9. Use `- None.` for passing Failure Tags; for failures, list only tags from `eval-rubric.md`.
10. For every failure, write the smallest skill change that would prevent recurrence.
11. After partial progress, select the next coverage batch if needed:

```bash
python3 scripts/select_converge_response_eval_batch.py --mode next-cover --results-dir evidence/response-eval/codex-headless-proof-discipline-20260530/results --require-real-results --runpack evidence/response-eval/codex-headless-proof-discipline-20260530
```

12. Run the progress summary while filling results:

```bash
python3 scripts/summarize_converge_response_eval.py evidence/response-eval/codex-headless-proof-discipline-20260530/results --require-real-results --show-axes
```

13. Run the validator from the skill root:

```bash
python3 scripts/check_converge_response_eval.py evidence/response-eval/codex-headless-proof-discipline-20260530/results --require-all-cases --require-real-results
```

## Release Gate

After all cases are filled and pass the response-eval validator, include the real results in the release check:

```bash
python3 scripts/check_converge_release.py --response-results-dir evidence/response-eval/codex-headless-proof-discipline-20260530/results --require-response-results
```

Do not claim behavior-level proof from generated stubs, synthetic smoke results, or partial case coverage.
