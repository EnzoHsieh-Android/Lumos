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

## Codex 逐字稿(2026-09-04,Projects/Codex完全支援_計劃 S3)

- 多讀 `--codex-sessions`(預設 `$CODEX_HOME/sessions` 或 `~/.codex/sessions`,遞迴找 `rollout-*.jsonl`);第一行 `session_meta` 的 `cwd` 篩本 repo,`cli_version` 不在 `CODEX_TRANSCRIPT_VERSIONS`(目前 `0.144.1`)就整份跳過、不猜。
- hook 注入在 Codex 稿裡是 `response_item/message role=developer`:主代理稿的「必看——這 N 篇」列成 `PreToolUse:apply_patch` 行;子代理稿(`thread_source=subagent`)的「LUMOS-LENS range=…」列成 `SubagentStart:dispatch-lens` 行(只計筆數,沒有釘住清單可比)。
- 錨定是啟發式:Codex 沒有 toolUseID,取同一輪內離注入最近的 apply_patch 呼叫(先往後找再往前找;實看兩種順序都有),目標檔=其 patch 標頭第一個路徑。
- 「有沒有讀」的判法跟 Claude 行同一支 `classify_bash`(exec 的 `cmd` 字串,有引號/無引號 key 都抽);rows 帶 `harness` 欄,summary 多 `by_harness`/`codex_lens_rows`/`codex_files`。
- 天花板同 Claude 行:只證「注入後有沒有動作碰到釘住的節點」,不證有沒有讀懂。

