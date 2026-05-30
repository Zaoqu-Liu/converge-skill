# Codex Web-Assisted Response-Eval Current Research - 2026-05-30

This run stores real Codex desktop web-assisted output for three current-research and technology-route cases:

- `latest-library-advice.md`
- `benchmark-headline-route-trap.md`
- `researched-answer-citations.md`

## Scope

- Host/runtime: Codex desktop with web search.
- Model/host label in results: Codex desktop web-assisted GPT-5.
- Skill under test: `skills/converge/SKILL.md`.
- Prompt packets: `prompts/`.
- Response artifacts: `responses/`.
- Reviewed results: `results/`.

## Sources Checked

Sources below were checked on 2026-05-30. They support freshness and traceability behavior, not a universal ranking across all frameworks or agents.

- Next.js 16.2: `https://nextjs.org/blog/next-16-2`
- Next.js adapters/platform commitments: `https://nextjs.org/blog/nextjs-across-platforms`
- Next.js deployment docs: `https://nextjs.org/docs/app/getting-started/deploying`
- React releases: `https://github.com/facebook/react/releases`
- React 19.2 release notes: `https://react.dev/blog/2025/10/01/react-19-2`
- Vite guide: `https://vite.dev/guide/`
- Astro 6.0 release: `https://astro.build/blog/astro-6/`
- XBench: `https://xbench.org/`
- AI Agents That Matter: `https://arxiv.org/abs/2407.01502`
- Establishing Best Practices for Building Rigorous Agentic Benchmarks: `https://arxiv.org/abs/2507.02825`

## Claim Boundary

This evidence supports a narrow behavior claim: Converge can handle current
technology-route questions with source traceability, scoped recommendations,
validation spikes, and honest refusal to overclaim from missing or weak current
evidence.

It proves that the reviewed web-assisted responses:

- Do not answer current frontend stack questions from stale memory alone.
- Use official/current source links for drift-prone framework guidance.
- Refuse to recommend an agent migration from a benchmark headline alone.
- Treat unsupported benchmark claims as unproven instead of laundering them.
- Refuse to fabricate production-readiness citations for an unnamed framework.
- Provide validation spikes and revisit triggers.

It does not prove:

- A universal best frontend stack for every project.
- A universal best AI agent framework or model.
- Production readiness for any unnamed framework.
- H3 native interaction behavior.
- Full current-research behavior across all 40 eval cases.

## Validate

```bash
python3 -B skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-web-current-research-20260530/results \
  --root skills/converge \
  --require-real-results
```

Summarize coverage:

```bash
python3 -B skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-web-current-research-20260530/results \
  --root skills/converge \
  --require-real-results \
  --show-axes
```
