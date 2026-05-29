我不会在 Codex Default Mode 里伪造一套 Cursor 风格的 8 道选择题；当前没有可用的原生 `request_user_input` 问答 UI，所以按 Converge 的 Codex 适配规则，我会把它压缩成一个自然语言确认，并带默认推进方向。

我的默认理解是：你想让我用 `@converge` 处理这个场景，同时遵守当前 host 能力边界，不假装有 Cursor/Plan Mode 的结构化选择题界面。默认我会按这个方向开始：做一次轻量 Intent Guard，明确目标、约束、默认假设和下一步，而不是进入问卷流程。

唯一需要你确认的是：你要我接下来产出的是“这个 eval prompt 下的合规响应”，还是“开始改进 `skills/converge/SKILL.md` 本身”？如果你不补充，我默认按前者处理。