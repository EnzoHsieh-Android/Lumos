---
type: system
status: done
created: 2026-09-05
updated: 2026-09-05
aliases: []
about_code:
  - scripts/hooks/claude/check-graph-sync.py
  - scripts/hooks/claude/dispatch-lens-hook.py
  - scripts/hooks/claude/impact-hook.py
  - scripts/merge-claude-settings.py
  - scripts/scenario_probe.py
  - scripts/lumos
tags:
  - type/system
  - status/done
summary: |-
  FLOW:lumos install →(Claude)~/.claude/hooks+settings.json+CLAUDE.md 區塊 /(Codex)~/.codex/hooks+hooks.json(--target codex,matcher 對照:Edit|Write→apply_patch、Agent→SubagentStart)+~/.agents/skills+AGENTS.md 同塊區塊+CODEX_HOME/agents/lumos_reviewer.toml → 使用者開一次互動 codex 按 Trust all → 之後 exec/互動兩模式 hook 都跑
  KEY:同一批 hook 腳本兩家共用,差異全在 --harness codex 旗標與註冊表:SessionStart 入口提醒(additionalContext)、PreToolUse impact-hook 取 apply_patch 的檔、SubagentStart dispatch-lens 領席(armed token)、Stop check-graph-sync 讀 Codex 逐字稿(版本表 0.144.1/0.153.2,不在表略過不猜)
  KEY:★收工擋一次(2026-09-05,[[Projects/Codex行為精修_計劃]];同日套到 Claude,[[Projects/README審視五修_計劃]] d2)★:改了程式碼、筆記沒動 → 兩家都回 decision:block 一次讓模型續做補筆記或一句話說明——名額先佔(~/.cache/lumos/stop-block/<session_id> O_EXCL 建成才擋;目錄整條路徑不得經 symlink、owner 自己、0700)+stop_hook_active 雙護欄,LUMOS_STOP_BLOCK_OFF=1 關;reason ≤1500 字、≤10 檔、檔名消毒包反引號並標明只是檔名。f02 後測 3/3 擋到、模型皆回一句說明;天花板=逼表態不是逼寫對
  KEY:★Codex 當編排者★:loop next 首輪必帶 --orchestrator codex(家族相對化:外家=非編排者那家);派工訊息對 hook 是密文(multi-agent v2 設計,改不了),鏡頭改走 dispatch-lens --arm <range> --seats N → 子代理 SubagentStart 原子領席(TTL 10 分,首行「LUMOS-LENS range=… 第 k/N 席」)→ --disarm;審查席點名 lumos_reviewer(0.153.2 選得中、0.144.1 忽略;唯讀靠父代理 --sandbox read-only,TOML sandbox_mode 不擋)
  KEY:★天生限制(工具補不了,誠實界線)★:①hook 要人按一次信任(綁 hooks.json 命令列,換檔內容不用重按;enforcement 對 Codex hook 只能報「已註冊」)②派工訊息密文③stderr 對 Codex 模型零訊號(只有 additionalContext/decision 兩通道)④codex exec 沒有 --max-turns,擋一次就是上限⑤同 repo 同窗口的無關子代理會搶 armed 席
  KEY:★順帶修的老洞(2026-09-05)★:is_code_file 只認副檔名,本 repo 主程式 scripts/lumos 無副檔名 → Stop 提醒 2026-05 上線起對它從沒生效(兩家皆然);現在 repo 內、無副檔名、一般檔、首行是 #!也算程式碼(先判位置再開檔,FIFO 不開)
  DEP:scripts/lumos(_codex_home/_sync_global_hooks/_install_codex_agent/dispatch-lens/loop next --orchestrator/enforcement Codex 列)/merge-claude-settings.py --target codex/scripts/hooks/claude/{check-graph-sync,impact-hook,dispatch-lens-hook,lumos-entry-hook}.py/scenario_probe.py --runner codex --stop-block/recount.py 讀 Codex 稿
  TEST:t_codex_stop_block_once(23 斷言)/t_codex_s1_graph_sync_codex_transcript/t_codex_s1_r1_fixes/t_codex_s1_lens_arm_claim/t_codex_s3_probe_codex_parser/t_codex_d6_agent_toml/t_codex_sync_global_tristate(python3 scripts/test_lumos.py -k codex 共 164 案例綠)
---
# codex-harness

> 白話:lumos 原本的「防護」全掛在 Claude Code 上——進場提醒、改檔前推波及、派審查員附鏡頭、收工點名沒補的筆記。這篇講的是同一套東西怎麼接到 OpenAI 的 Codex CLI 上、哪些地方兩家行為刻意不同、哪些是 Codex 平台補不了的限制。程式碼只告訴你現在長怎樣;為什麼這樣接、哪裡踩過雷,看這裡和下面兩份計劃。

## 六層對照(裝一次接兩家)

| 層 | Claude Code | Codex CLI |
|---|---|---|
| 紀律區塊 | `CLAUDE.md` | `AGENTS.md`(同一組 sentinel 區塊,`lumos update` 兩邊同刷) |
| skills | `~/.claude/skills/` symlink | `~/.agents/skills/`(開放共用目錄,只動帶 `.lumos-managed` 標記的) |
| hook 註冊 | `~/.claude/settings.json` | `~/.codex/hooks.json`(合併器 `--target codex`) |
| hook 腳本 | `~/.claude/hooks/*.py` | `~/.codex/hooks/*.py`(同一批檔 copy,命令列多 `--harness codex`) |
| 審查席身分 | 派工詞自帶框架 | `CODEX_HOME/agents/lumos_reviewer.toml`(developer_instructions 是框架單源) |
| 逐字稿 | `~/.claude/projects/**/*.jsonl` | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`(首行 session_meta 帶 cli_version) |

## 收工擋一次為什麼兩家一致

先做 Codex 的理由:Codex 側 stderr 對模型完全看不見,唯一能把「你漏了」送到模型面前的通道就是 `decision:block`(它會把 reason 當下一個提示續做)。同日 README 審視發現 Claude 側也一樣——Claude Code 官方文件明講 exit 0 的 stderr 只進除錯日誌,所謂「軟提醒」從沒有人看到過。2026-07-06 撤的是每回合刷屏的 nag;這裡同 session 只擋一次、只在改了碼沒寫回時,不是重開 nag,所以套成兩家一致([[Projects/README審視五修_計劃]] d2);實驗設計與三輪代碼審抓到的坑(名額白燒、symlink、反引號跳出 code span)都在 [[Projects/Codex行為精修_計劃]]。

## 單源與卷證

- 落地四階段 S0–S3 與裁定 d1–d6:[[Projects/Codex完全支援_計劃]];驗證 [[Verification/2026-09-04_Codex完全支援S0安裝層驗收]]、[[Verification/2026-09-04_Codex完全支援S1hook適配驗收]]、[[Verification/2026-09-04_Codex完全支援S2迴圈編排驗收]]、[[Verification/2026-09-04_Codex完全支援S3量測驗收]]。
- 行為精修(擋停一次、範本通用句、shebang):[[Projects/Codex行為精修_計劃]];驗證 [[Verification/2026-09-05_Codex行為精修f02後測]]。
- 收工檢查本體:[[Systems/graph-sync-coverage]];安裝生命週期:[[Systems/lumos-cli-lifecycle]];設計/代碼迴圈的 Codex 席位規則:[[Systems/design-loop]]、[[Systems/pitfalls-code-loop]]、[[Systems/cross-family-audit]]。

## 回頭條件

- REVISIT:2026-09-08 Enzo 裁代碼審 r3 之後那 3 行(父層 symlink)要不要補一輪 delta 審。
- REVISIT:2026-09-25 互動模式(codex TUI)下的擋停與 SubagentStart 領席;抽 5 場真實 Codex 對話看擋停後的說明合不合理。
- REVISIT:2026-10-04 有沒有人真的用 Codex 開 lumos 專案(0 筆=S2/S3 備而不用);armed 席被無關子代理搶走的頻率。
