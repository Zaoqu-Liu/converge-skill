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
