# Codex Web-Assisted Response-Eval Technology Route - 2026-05-29

This run stores a real Codex desktop, web-assisted response for the `technology-route-current-stack.md` case.

## Scope

- Host/runtime: Codex desktop with web source access.
- Model: GPT-5.
- Eval case: `technology-route-current-stack.md`.
- Prompt packet: `prompts/technology-route-current-stack.prompt.md`.
- Response artifact: `responses/technology-route-current-stack.response.md`.
- Reviewed result: `results/technology-route-current-stack.result.md`.

## Source Access

The response used current official or primary sources available on 2026-05-29:

- OpenAI Agents SDK guide: `https://developers.openai.com/api/docs/guides/agents`
- OpenAI Agents SDK update post: `https://openai.com/index/the-next-evolution-of-the-agents-sdk/`
- OpenAI Agents SDK TypeScript docs: `https://openai.github.io/openai-agents-js/`
- Claude Agent SDK overview: `https://code.claude.com/docs/en/agent-sdk/overview`
- Google ADK docs: `https://adk.dev/`
- LangGraph docs: `https://docs.langchain.com/oss/python/langgraph/overview`
- CrewAI docs: `https://docs.crewai.com/`
- MCP specification: `https://modelcontextprotocol.io/specification/2025-11-25/basic`
- NSA MCP security guidance: `https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf`

## Claim Boundary

This evidence supports a narrow behavior claim: Converge can produce a source-backed Technology Route answer for a drift-prone agent-framework decision when source access is available.

It does not prove:

- The recommended stack is universally best for every AI Agent product.
- Any framework's production readiness in the user's environment.
- H3 native host interaction behavior.
- Full IntentBench behavior.

## Validate

```bash
python3 -B skills/converge/scripts/check_converge_response_eval.py \
  evidence/response-eval/codex-web-tech-route-20260529/results \
  --root skills/converge \
  --require-real-results
```

Summarize coverage:

```bash
python3 -B skills/converge/scripts/summarize_converge_response_eval.py \
  evidence/response-eval/codex-web-tech-route-20260529/results \
  --root skills/converge \
  --require-real-results \
  --show-axes
```
