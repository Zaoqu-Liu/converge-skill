# Evidence

This directory stores claim-supporting artifacts that are safe to commit.

Evidence rules:

- H2 behavior claims require real response-eval results validated with `--require-real-results`.
- H3 native interaction claims require native-proof JSON plus real transcript, screenshot, log, or export artifacts validated with `--require-real-artifacts`.
- Synthetic release-smoke results are useful for checking tooling, but they do not prove behavior.
- Missing cases must stay missing until a real host or headless run is reviewed.

Current stored evidence:

- `response-eval/codex-headless-20260529`: one real Codex headless response-eval pass for `codex-default-no-native-ui.md`.
- `response-eval/codex-headless-choice-20260529`: one real Codex headless response-eval pass for `codex-default-choice-survey-trap.md`.
- `response-eval/codex-headless-host-proof-20260529`: one real Codex headless response-eval pass for `host-support-proof-boundary.md`.
- `response-eval/codex-web-tech-route-20260529`: one real Codex web-assisted response-eval pass for `technology-route-current-stack.md`.
- `response-eval/codex-headless-low-expression-20260529`: one real Codex headless response-eval pass for `low-expression-idea.md`.
- `response-eval/codex-headless-mixed-artifact-20260530`: one real Codex headless response-eval pass for `mixed-artifact-intake.md`.
