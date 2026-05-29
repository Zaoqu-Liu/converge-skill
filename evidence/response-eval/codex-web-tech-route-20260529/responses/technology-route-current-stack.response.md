这是 Technology Route，不是泛泛架构建议。我会先把“最新最好”拆开：最新不等于最好，AI Agent 产品的底座要优先看可控性、工具执行边界、状态持久化、可观测性、评测、安全和宿主生态。

下面是我按 2026-05-29 可访问官方/主源资料后的默认路线。

## Current Best Known

默认路线：OpenAI Agents SDK 作为主 harness，MCP 作为工具/上下文接入协议，产品自己的服务层负责权限、状态、审计、计费、队列和 eval。

原因：

- OpenAI 官方文档把 Agents SDK 定位为当应用自己拥有 orchestration、tool execution、approvals、state 时使用的 code-first 路线，支持 TypeScript/Python 入口、tools、MCP、tracing/eval 等能力。
- OpenAI 2026-04-15 的 Agents SDK 更新强调 file/command/edit/sandbox/long-horizon work，这和“做 AI Agent 产品”比纯聊天或简单 workflow 更贴近。
- MCP 已经是跨工具/上下文接入的事实标准方向，但它不是 agent harness，也不能替代产品侧的权限、隔离、审计和安全策略。

我的默认实现结构：

```text
Product app / API
  -> policy, auth, billing, task queue, audit, eval
  -> OpenAI Agents SDK harness
  -> MCP allowlisted tool layer
  -> sandbox/workspace execution for code/files
  -> observability + response eval + regression cases
```

## Safe Default

如果你要做面向真实用户的通用 AI Agent 产品：

- 主框架：OpenAI Agents SDK。
- 协议层：MCP，但只接 allowlisted servers/tools。
- 状态层：你自己的 DB + task/run ledger，不把长期产品状态完全交给框架。
- 执行层：sandbox/workspace-first，工具权限显式授权。
- 评测层：从第一天接 response-eval、trace review、失败标签和回归集。
- 前端/后端：TypeScript 产品栈可以优先用 TS SDK；如果核心是复杂文件/代码执行和 sandbox 能力，先用 Python 做 spike，因为 OpenAI 的 2026-04-15 更新明确说新的 harness/sandbox 能力先在 Python 发布，TS 文档又显示 TS SDK 已有 sandbox/text/voice 入口，这里存在时间差，必须实测。

## Frontier Bet

Claude Agent SDK 适合做 Claude Code-like 的 coding/workspace agent，尤其是你想复用 Claude Code 那套 read files、run commands、web search、edit code、context management 的体验时。它的强项是 agentic coding/workspace loop，不是最中立的跨模型产品底座。

边界：Anthropic 文档明确 Agent SDK 使用 API key 等认证路径，并限制第三方把 claude.ai login/rate limits 包装给自己的产品。它适合作为一个强力 execution backend 或 coding-agent lane，不建议无脑作为全产品唯一抽象层。

## When To Use Google ADK

如果你的产品天然围绕 Gemini、Google Cloud、企业部署、多语言 SDK，Google ADK 是强候选。官方 ADK 页面强调 enterprise-scale agents，并列出 Python、TypeScript、Go、Java、Kotlin。它适合 Google 生态或多语言企业平台，不一定是最轻的独立创业默认路线。

## When To Use LangGraph

LangGraph 适合你明确需要 durable execution、streaming、human-in-the-loop、低层 orchestration runtime，或者你要把 agent flow 做成可恢复、可检查、可中断的图/状态机。

如果只是普通 tool-calling loop，LangGraph 可能过重。它更像“可控编排运行时”，不是所有 Agent 产品的默认起点。

## When To Use CrewAI

CrewAI 适合业务自动化、crews/flows、较高层的多 agent 协作和企业 automation 场景。官方文档强调 crews、flows、guardrails、memory、knowledge、observability 和 production-ready。但如果你要做一个新的通用 agent substrate，我会把它放在 Hold/Use-case-specific，而不是默认底座。

## MCP Position

MCP 是必要协议层，不是安全边界。

用法：

- 用 MCP 标准化工具、数据源和外部系统接入。
- 每个 MCP server 都要有 allowlist、权限域、超时、日志、输出审计和 sandbox/secret policy。
- 不要把 MCP server 当可信插件市场直接接入生产。

## Evidence Snapshot

Verified: 2026-05-29 Asia/Shanghai.

| Source/Link | Source Class | What It Supports | Boundary |
|---|---|---|---|
| https://developers.openai.com/api/docs/guides/agents | Official docs | OpenAI positions Agents SDK for code-first agent apps that own orchestration, tool execution, approvals, state, tools, MCP, tracing/eval. | Product docs can change; exact SDK APIs need package-level spike. |
| https://openai.com/index/the-next-evolution-of-the-agents-sdk/ | Official release post, 2026-04-15 | OpenAI added agent harness/sandbox direction for files, commands, code edits, long-horizon tasks; post says new harness/sandbox launches first in Python with TypeScript planned. | The TypeScript SDK docs now show sandbox APIs, so maturity/parity must be verified live. |
| https://openai.github.io/openai-agents-js/ | Official TS SDK docs | TS SDK exposes sandbox, text, voice agents, MCP server tool calling, sessions, human-in-loop, tracing. | Docs prove surface exists, not production fit for your app. |
| https://code.claude.com/docs/en/agent-sdk/overview | Official Claude Code docs | Claude Agent SDK exposes Claude Code-style tools, agent loop, context management in Python/TypeScript; includes built-in file/command/web/edit tools. | Strong for Claude Code-like workflows; less neutral as a cross-model abstraction. |
| https://adk.dev/ | Official Google ADK docs | ADK is positioned for enterprise-scale agents and supports Python, TypeScript, Go, Java, Kotlin. | Best when Google/Gemini/cloud/multilanguage constraints matter. |
| https://docs.langchain.com/oss/python/langgraph/overview | Official LangGraph docs | LangGraph is a low-level runtime for long-running, stateful agents, durable execution, streaming, human-in-loop. | Use when you need graph/state control; avoid as default for simple loops. |
| https://docs.crewai.com/ | Official CrewAI docs | CrewAI covers agents, crews, flows, guardrails, memory, knowledge, observability, enterprise automation. | Vendor “production-ready” language is not independent proof; validate against your workflows. |
| https://modelcontextprotocol.io/specification/2025-11-25/basic | Official MCP spec | MCP uses JSON-RPC, authorization framework, TypeScript schema as source of truth, JSON Schema validation. | Protocol spec is not a production security model. |
| https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf | Government security guidance, May 2026 | MCP security deserves explicit design review and controls. | This is security guidance, not a framework ranking. |

## Avoid / Hold

- Do not choose CrewAI or LangGraph just because they are popular names; choose them only when their orchestration model matches your product.
- Do not treat MCP as a plugin sandbox.
- Do not collapse model quality, IDE integration, workflow orchestration, protocol integration, and product security into one “best framework” answer.
- Do not make a 12-month irreversible framework bet before a spike; this layer is still moving fast.

## Validation Spike

Run a 3-5 day spike with the same task in three lanes:

1. OpenAI Agents SDK + MCP + sandbox/workspace.
2. Claude Agent SDK as a coding/workspace lane.
3. LangGraph or Google ADK only if your product requires durable graph control or Google enterprise integration.

Use one realistic task:

```text
Given a repo + issue + docs link, inspect files, ask one clarification only if needed, edit code, run tests, produce a trace, and persist a resumable run record.
```

Measure:

- Can it inspect and edit files safely?
- Can it enforce tool permissions and human approval?
- Can it persist/resume state?
- Can it attach source citations and run evidence?
- Can it integrate MCP without leaking secrets?
- Can it expose traces/evals useful enough for debugging?
- Can your team understand and modify it without framework lock-in?

## Revisit Trigger

Revisit the route when any of these happens:

- OpenAI TS/Python sandbox parity changes materially.
- Claude Agent SDK changes authentication or third-party product terms.
- Google ADK adds/removes major language/runtime support relevant to your stack.
- MCP publishes a new stable spec or major security guidance changes.
- LangGraph/CrewAI release a major version that changes persistence, deployment, or human-in-loop semantics.
- Your product shifts from coding/workspace tasks to business automation, or from API tools to GUI/desktop automation.
