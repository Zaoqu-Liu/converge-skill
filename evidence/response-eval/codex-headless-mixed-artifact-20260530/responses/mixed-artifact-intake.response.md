我用了 `@converge` 的 artifact diagnosis 模式看了三份输入。结论很明确：真正问题不是“报表导出失败”本身，也不是 renderer 该去猜计费状态，而是**计费/权益前置校验缺失，导致缺 billing 的 workspace 仍然发起导出请求，后端又直接读取 `workspace.billing.plan` 崩成 500，最后 UI 把它错误地展示成 `Unknown error`**。

**Input Inventory**
- PRD：[prd.md](/Users/liuzaoqu/Documents/Codex/2026-05-27/goal-thbs2/converge-skill/skills/converge/eval-artifacts/mixed-artifact-intake/prd.md:5)
- 日志：[error.log](/Users/liuzaoqu/Documents/Codex/2026-05-27/goal-thbs2/converge-skill/skills/converge/eval-artifacts/mixed-artifact-intake/error.log:1)
- 截图 OCR：[screenshot.txt](/Users/liuzaoqu/Documents/Codex/2026-05-27/goal-thbs2/converge-skill/skills/converge/eval-artifacts/mixed-artifact-intake/screenshot.txt:3)

**Observed Facts**
- PRD 要求：只有 active Pro plan 用户可导出；没有 billable plan 的用户必须看到 `Billing setup required`；billing 数据缺失时，UI 必须在调用 `/api/reports/export` 前阻断。
- 截图显示：当前 workspace 的 billing badge 是 `Plan: Not configured`，用户点击了 `Export report`，看到的却是 `Export failed: Unknown error`，没有 inline billing setup prompt。
- 日志显示：实际请求已经打到了 `/api/reports/export`，后端 `workspace={"id":"ws_9","billing":undefined,"features":["reports"]}`，随后 `buildExportPayload` 读取 `plan` 时触发 `Cannot read properties of undefined`，返回 500。

**Contradictions**
- PRD 说 billing 缺失时 UI 必须在调用 API 前拦截；现实是 API 被调用了。
- PRD 说 billing/entitlement 失败不能展示通用 `Unknown error`；现实是 toast 展示了 `Unknown error`。
- PRD 说不要让 report renderer 推断 billing state；日志表明问题发生在 `buildExportPayload` 阶段，说明 billing 状态已经以不合法形态流入导出构建链路。

**I infer**
- 用户表面看到的是“导出失败”，但根因不是导出渲染逻辑坏了。
- 当前系统可能把 `features:["reports"]` 当成了可导出的充分条件，但 PRD 的真正条件是 active Pro/billable plan。
- 前端和后端都缺一层明确的 billing contract：前端没拦，后端没把缺 billing 转成领域错误，而是让 undefined 继续进入 payload builder。

**True Problem**
真正问题是**导出入口的 billing entitlement contract 断裂**：

1. UI 明知或可见 `Plan: Not configured`，仍允许用户点击并调用导出 API。
2. API/后端没有对 `workspace.billing` 缺失做显式校验。
3. `buildExportPayload` 假设 `workspace.billing.plan` 一定存在，导致 TypeError。
4. 错误处理层把应当是 `Billing setup required` 的业务状态，降级成了 `Unknown error`。

所以这不是一个单点 bug，而是**前端 guard、后端 validation、错误映射三处一起没有遵守 PRD**。

**Recommended Next Fix/Check**
优先修复顺序我建议这样：

1. 前端导出按钮/handler 增加 billing guard：当 `workspace.billing?.plan` 缺失、未配置、或不是 active Pro 时，直接展示 `Billing setup required`，不要调用 `/api/reports/export`。
2. 后端 `/api/reports/export` 在进入 `buildExportPayload` 前做硬校验：如果 `workspace.billing` 或 `workspace.billing.plan` 缺失，返回明确的业务错误，比如 `BILLING_SETUP_REQUIRED`，状态码用 `402`、`403` 或产品已有的 entitlement error 约定，不能返回 500。
3. `buildExportPayload` 不应承担权益判断，但也不应对 undefined 无防护崩溃；它的输入类型或调用前置条件要收紧。
4. UI 错误映射要覆盖 billing/entitlement error code，把它显示为 `Billing setup required`，不要落到 `Unknown error`。
5. 加最小回归测试：`workspace.billing = undefined` 时，前端不发请求；后端即便被直接调用，也返回 billing setup required，不抛 TypeError、不返回 500。

一句话版：**这是“缺 billing 的 workspace 被允许进入导出链路”的问题，不是报表导出能力本身的问题。**