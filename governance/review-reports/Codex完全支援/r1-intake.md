preflight-4: ran

# r1 收貨紀錄(Codex完全支援)

## 前掃(2026-09-04,sonnet 單 agent,四類固定清單)
- ①未定義詞:無命中(既有識別字全部 grep 到;`--arm` 為明寫新增不算)。
- ②壞引用 1 條:「跨家族原則」指向 heterogeneous-finder-ensemble(該篇談工具異質,無「外家」字)。修:改指 canary-audit + design-loop。
  修改前→後:「[[Systems/heterogeneous-finder-ensemble]] 的跨家族原則不變」→「[[Systems/canary-audit]] 與 [[Systems/design-loop]] 的跨家族席原則(外家 blocker 不得僅被同門多數推翻)不變」
- ③範圍矛盾:無命中(六層/四階段/TTL/預算算術皆一致)。
- ④語意 2 條(存在性類以外,非核心裁定,直接修真檔):
  - check-graph-sync 欄位名混用:修改前「`tool_input.command`/`file_path`」→修改後「逐字稿 tool_use 區塊的 `input.command`/`input.file_path`(PreToolUse payload 才叫 tool_input)」;佐證 file: `scripts/hooks/claude/check-graph-sync.py:137-143`。
  - 子代理事件欄位歸屬:修改前「Start/Stop 帶 agent_id 與 agent_transcript_path」→修改後「SubagentStart 帶 agent_id+agent_type,子代理 PreToolUse 帶 agent_id,SubagentStop 才帶 agent_transcript_path」。編排者註:前掃依調研筆記判 SubagentStart 不帶 agent_id;實驗 5 hook.log 實看 SubagentStart keys 含 agent_id,以實測為準寫入。

## 外家否決(Codex)報告收貨(20 條;quote-check 12 句錨不到→那 12 條不入 set,內容仍逐條判)
- 正規化:`severity: X ;blocking: Y` 同行 → 拆兩行(regex,內容未改);原檔存 r1-外家否決.raw。
- **F1「message 不是加密、依文件可 rewrite」→ MISS(不採信)**。重現(實驗 A,scratchpad codexfull/hookA.log、outA.jsonl):PreToolUse 無 matcher,對 collaborationspawn_agent 回 `{"permissionDecision":"allow","updatedInput":{...,"message":"<明文>"}}` → 父代理最終回覆「Agent errored: stream disconnected before completion: Encrypted function output content could not be decrypted or decoded.」;hook 看到的 message 仍為 `gAAAAABq…` 密文。結論:0.144.1 下 message 為不透明密文,rewrite 會弄壞派工;文件(tool-coverage 節)與實測不符,以實測為準。
- **F12「matcher Agent 沒攔到→應用 canonical 名重驗」→ 部分 HIT**。重現(實驗 B,hookB.log):`hooks.PreToolUse=[{matcher="spawn_agent"},{matcher="collaborationspawn_agent"}]` 兩條並列 → 只記到 1 筆 PreToolUse(tool_name collaborationspawn_agent),即兩個 matcher 恰一個命中(未分開跑,推測為完整名 collaborationspawn_agent;S0 實作時分開驗一次)。但攔到也改不了 message(見 F1),armed 檔路線的必要性不受影響;「攔得到 spawn」這個事實寫進 spec 當備用觸發點。
- F5 HIT:file: `scripts/hooks/claude/dispatch-lens-hook.py:50` 確為 `payload.get("tool_name") != "Agent"` 即靜默返回;「同一批腳本零改」對 dispatch-lens 不成立,spec 已在 S1 表寫要改,但「五支各自認形狀」一句對這支要明寫成「新增 SubagentStart 分支」。
- F7 HIT(部分):file: `scripts/lumos:10583` docstring 明寫讀入去 BOM/CRLF→LF、寫入強制 LF;sentinel 外「文字」不動但換行/BOM 會被正規化——spec 「既有機制本來就這樣」要補這句。
- F8 HIT:file: `scripts/lumos:10362-10372` teardown 三步不看 rc、固定 `return 0`;spec 驗收「一次全部乾淨」須改成用 enforcement/檔案存在性機械驗,不能靠 teardown rc。
- F9 HIT:官方 subagents 文件 custom agent 必填 name/description/developer_instructions;spec 漏兩欄。
- F14 HIT:spawn_agent 介面(實驗 3/4/A 均見)只有 task_name/message/fork_turns,無 agent 參數;自訂 agent 由派工詞點名或 description 匹配選中——spec「agent=lumos-reviewer」不可機械執行,改寫成「派工詞點名」。
- F6 HIT(措辭矛盾):「不寫 TOML」與 S2 產 agent TOML 衝突;改寫為「不解析/不改寫既有 config.toml;agent TOML 為新建檔,以字串範本寫出」。
- F3 HIT:官方 skills 文件 repo 層只列 `.agents/skills/`(本篇 2026-09-04 補表時抄成兩個);刪 `.codex/skills/`。
- F2/F4/F10/F11/F13/F15/F16/F17/F18/F19/F20:設計層意見,無需重現,逐條折入或附理由放行見審計修正紀錄。

## 整合知識同步席收貨(8 條,quote-check 全錨、refcheck 18/18)
- F3(blocker)HIT:file: `scripts/lumos:5711-5712` 家族用靜態關鍵字表(`_ROSTER_EXTERNAL_KEYS`/`_ROSTER_CLAUDE_KEYS`),`_roster_family(auditor)` 無編排者參數;`_TIER_ROSTER` code-high 兩席 external 為 required-fail-closed。Codex 編排時只改散文,同門互審會被判成「外家到齊」。→ 折入:家族判定加「編排者家族」維度。
- F4(major)HIT:file: `scripts/lumos:7387-7396` `_usage_log` 只被 show/context 呼叫,schema `{ts,node,cmd}`;check-graph-sync.py 無任何檔案寫入(grep open/write 僅讀 queue)。spec「hook 自己記的 usage-log」「Stop 後 usage-log 多一筆」無對應路徑 → 折入:S1 驗收改用實測時的 hook 記錄包裝,不發明新帳。
- F1/F2/F5/F6/F7/F8:引句錨定、行號機驗通過;內容為設計層對照(剝除端雙檔、四個呼叫點與 Check D、漏列 skill、enforcement 對稱、錨點覆蓋範圍、_skills_list 掃全部 8 支),逐條折入。

## 邊界可執行席收貨(8 條全錨、refcheck 4/4)+ 通才席(7 條全錨、refcheck 28/28)
- 邊界 F1(blocker)HIT:實驗 C(`-c` 內嵌 hook、不帶 --dangerously-bypass-hook-trust)hook 0 筆;實驗 D(隔離 CODEX_HOME 放 hooks.json、不帶旗標)hook 0 筆;同一 hook 帶旗標時(實驗 2/4/5)有 fire。`codex --help` 無任何 hooks 信任管理子命令;sqlite 表與 toml/json 均無 hook 信任紀錄可辨(★信任存放位置沒查出來★)。結論:使用者層 hook 也要先在互動 TUI 按一次「Trust」才會跑;exec 只能靪旗標。
- 邊界 F2(blocker)HIT:file: `scripts/lumos:10960-10982` `_link_or_copy` 對非空真目錄走 `shutil.rmtree(ignore_errors=True)` 後再連結,無提示。
- 邊界 F5 HIT:file: `scripts/lumos:11084-11087` `subprocess.run(merge)` 不看 returncode、無條件 `return True`。
- 邊界 F6a HIT:AGENTS.override.md 為官方文件所載機制(本篇稍早已 fetch:全域與各層皆「有 override 就只讀它」);spec 漏。F6b HIT:32 KiB 為整條 chain 合併上限(文件),截斷靜默。F7 HIT:apply_patch 語法含 `*** Move to:`(文件+二進位字串)。
- 通才 F5「permission_mode/model 欄位查無證據」→ **部分 MISS**:codexfull/hook.log 六筆 PreToolUse 皆含 `"permission_mode":"bypassPermissions"` 與 `"model":"gpt-5.6-sol"`(Codex 側欄位確實存在);但 Claude Code hook 輸入亦有 permission_mode 欄位(官方 hooks 文件),故「以欄位有無判家族」不可靠——結論與外家 F18 相同:改用註冊命令列明確旗標。該條以「判別法不可靠」折入,不以「欄位不存在」折入。
- 通才 F1/F2a/F2b/F6、整合 F1/F2/F5/F6/F7/F8、邊界 F3/F4/F7/F9:引句+行號機驗通過,逐條折入(blocker 輪,accepted 空)。
- 架構席 ⚠(armed 檔/SubagentStart 非同步交接無先例):編排者裁=平台限制逼出的有意識偏離,寫進裁定(c)並標 PRIOR-ART 缺口。
