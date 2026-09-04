# 主 session 鏡頭利用率——唯讀重算

單源:`docs/lumos-toolchain-knowledge/Projects/主session鏡頭利用率_計劃.md`(第一段:零新元件)。

重跑:
```
python3 governance/eval/lens-utilization/recount.py --repo . [--json] [--out 報表.json]
```
讀 `~/.claude/projects/*/` 下所有逐字稿(主+`subagents/`),用逐字稿行的 `cwd` 篩「在本 repo 或其 worktree 之下」;
只認 `attachment.type == hook_additional_context` 且 `hookName ∈ PreToolUse:Edit|Write|MultiEdit` 的注入;
固定席從注入全文解析(新舊兩種「必看」標頭;事故行沒有 ★TAG★);錨點=toolUseID 對到的那次 tool_use 行序。
★只印分佈,不出單一命中率、不設門檻;不寫任何帳;結果不進 hook、不進 lumos gov★。
逐字稿依 Claude Code 的 cleanupPeriodDays(預設 30 天)會被清,歷史窗有限。
