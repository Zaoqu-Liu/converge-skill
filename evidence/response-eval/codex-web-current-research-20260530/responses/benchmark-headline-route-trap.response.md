不要立刻全量迁。我的默认建议是：**冻结“全量迁移”决策，只做一个受控 validation spike**。

这个问题的真实风险不是 XBench 第一名本身，而是你把“榜单第一”误读成“适合我们的生产系统”。Agent 产品的迁移成本、工具协议、记忆/权限/安全边界、失败恢复、成本、延迟和可观测性，通常不会被一个 headline score 完整覆盖。

## Evidence Snapshot

我做了当前来源检查：

- 访问到 [xbench.org](https://xbench.org/)；公开摘要称它是面向 AI agents 的 evergreen benchmark，但这本身只说明有一个 benchmark surface，不等于你的产品 workload 已被覆盖。
- 本轮没有找到足够的 primary evidence 证明 “MegaAgent-Next 在 XBench 第一” 这个具体说法可以直接支撑生产全量迁移；因此不能把它当作已验证事实。
- arXiv 论文 [AI Agents That Matter](https://arxiv.org/abs/2407.01502) 指出 agent benchmark 常见问题包括只看 accuracy、忽略成本、混淆模型开发者和下游开发者的评测需求、holdout 不足导致 overfit、复现标准不统一。
- arXiv 论文 [Establishing Best Practices for Building Rigorous Agentic Benchmarks](https://arxiv.org/abs/2507.02825) 进一步指出 agentic benchmark 的任务设置和奖励设计问题会显著高估或低估能力，并提出 Agentic Benchmark Checklist。

## Decision

现在不迁。正确路线是：

1. **先验证 benchmark 是否相关**：XBench 的任务分布、工具环境、评分函数、运行次数、成本统计、失败样本，是否贴近你的 agent 产品。
2. **再做小范围替换**：选 10-30 个你们真实用户任务，跑现有方案 vs MegaAgent-Next，同样 prompt、同样工具、同样权限、同样时间预算。
3. **最后看迁移账**：成功率、成本/成功任务、P95 延迟、人工接管率、失败可恢复性、日志可观测性、供应商锁定、回滚成本。

## Validation Spike

一周内做：

- 20 个真实任务 replay。
- 每个任务至少 3 次运行，记录 variance，不只看 best run。
- 加入 5 个“脏数据/权限不足/工具失败/中途变更目标”的 adversarial tasks。
- 对比指标：task success、cost per success、manual intervention、latency、tool error recovery、policy violations、trace clarity。
- 迁移门槛：新方案至少在核心指标上赢 20% 以上，且没有安全/成本/锁定重大倒退。

## Revisit Trigger

只有这些成立时才考虑迁：

- XBench/MegaAgent-Next 发布可审计 methodology、任务样本或足够详细的 scoring notes。
- 你的内部 replay 显示稳定提升，而不是偶然跑赢。
- 回滚路径清楚，迁移可以按模块灰度，不要求大爆炸替换。
- 成本、延迟、安全、权限和可观测性都通过生产前门槛。

一句话：**榜单可以决定“值得试”，不能决定“立刻全量迁”。**
