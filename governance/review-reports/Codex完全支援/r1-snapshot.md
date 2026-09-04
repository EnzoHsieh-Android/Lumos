---
type: project
status: doing
created: 2026-09-04
updated: 2026-09-04
tags:
  - type/project
  - status/doing
  - scope/governance
related:
  - "[[Projects/Codex工作流整合_調研]]"
  - "[[Projects/派工鏡頭注入_計劃]]"
  - "[[Projects/主動影響幅度偵測_計劃]]"
  - "[[Projects/install全域hook同步_計劃]]"
  - "[[Projects/teardown一鍵拆機_計劃]]"
  - "[[Systems/lumos-cli-lifecycle]]"
  - "[[Systems/design-loop]]"
  - "[[Systems/anchor-integrity]]"
  - "[[Systems/heterogeneous-finder-ensemble]]"
  - "[[Systems/canary-audit]]"
summary: |-
  FLAG:DECISION
  KEY:目標=在 Codex CLI 下開一個 lumos 專案,得到跟 Claude Code 下★同一套★六層防護:指示(AGENTS.md)/skills/hooks(進場、影響幅度、派工鏡頭、收工同步)/迴圈編排/量測/安裝-拆機對稱;不做第二套邏輯,每層都是「同一支 lumos、多一個接頭」
  KEY:★2026-09-04 實驗 4/5 定下四個地基事實★:①未信任 repo 的 AGENTS.md 與 .agents/skills/ 都會載入 ②PreToolUse 攔得到 apply_patch(tool_input.command=patch 全文,沒有 file_path)③spawn_agent 的 message 在 hook 眼裡是加密字串→updatedInput 改派工詞這條路在 Codex 不通;matcher "Agent" 也沒攔到(工具名 collaborationspawn_agent)④SubagentStart 的 additionalContext 會到子代理手上→Codex 側派工鏡頭走這條
  KEY:四個擬裁定(待審):(a)AGENTS.md 放同一塊 sentinel 紀律區塊、reinject 同時刷兩檔、doctor Check D 兩檔都比 (b)hook 註冊寫 ~/.codex/hooks.json 不寫 config.toml(stdlib 沒 TOML 寫入器,零依賴) (c)鏡頭範圍改由 `lumos dispatch-lens <range> --arm` 落一個帶 TTL 的 armed 檔、SubagentStart hook 讀它;Claude 側標記行照舊 (d)外家席=「不是當下編排者那一家」:Codex 編排時外家換 claude -p
  KEY:分四階段,每階段各自驗收:S0 安裝層(skills symlink→~/.agents/skills、hooks.json 合併器、AGENTS.md 區塊、enforcement 三層、teardown 對稱)→S1 hook 適配(apply_patch 取檔、SubagentStart 鏡頭、check-graph-sync 讀 Codex 逐字稿)→S2 迴圈從 Codex 編排(自訂 agent TOML、模板去 Claude 字眼、外家互換、席名統一)→S3 量測(recount/scenario_probe 多一個 runner)
---
# Codex完全支援_計劃

> 白話:現在 lumos 的「防護」全掛在 Claude Code 上——進 session 時有人提醒你去查圖譜、改檔前有人把相關合約推到眼前、派審查員時有人把清單附進派工詞、收工時有人查你有沒有寫回圖譜。這些全靠 Claude Code 的四種接頭(CLAUDE.md、skills、hooks、子代理)。Codex CLI 0.144.1 四種接頭都有、形狀幾乎一樣。本案要做的是:**同一支 lumos、同一批 hook 腳本,多接一組 Codex 的接頭**,讓人用 Codex 開 lumos 專案時拿到同一套防護。★不寫第二套邏輯★——Codex 專屬的只有「接頭」那一薄層。

PRIOR-ART: ① 最小解層級——四種接頭 Codex 都原生提供而且跟 Claude 同形:hooks.json 的 JSON 結構跟 `~/.claude/settings.json` 的 `hooks` 段一模一樣(事件名、matcher、`{type,command,timeout}`);skills 是同一個開放標準(agentskills.io,SKILL.md 同格式)所以 symlink 就能用、不用轉檔;AGENTS.md 跟 CLAUDE.md 一樣是「開 session 自動進 prompt 的 markdown」,既有 sentinel 注入機制(`_reinject_claude_block`)直接多寫一個檔;子代理開場的 additionalContext 是 Codex 自己設計給「餵子代理脈絡」的通道。② 世界解過沒——「一套 agent 工具鏈同時支援 Claude Code 與 Codex」在 2026 已是常態(superpowers skill 自帶 `references/codex-tools.md` 就是這種雙接頭寫法),做法一律是「共用內容+每家一個薄 adapter」,沒有人為此寫兩套。③ 裁定=borrow-design(Codex 官方通道)+ 零新依賴(避開寫 TOML 就不需要任何套件)。

## 一句話

lumos 的六層防護(指示 / skills / hooks / 迴圈編排 / 量測 / 安裝拆機)在 Codex CLI 下逐層接上,驗收標準是「乾淨機器、乾淨 HOME,`lumos install` 一次,Codex 開 lumos 專案時六層機械可證都生效;`lumos teardown` 一次全部乾淨」。

## 「完全支援」的定義(六層對照;沒對到的就不算完全)

| 層 | Claude Code 現況(都已上線) | Codex 對應接頭 | 本案要做的 | 地基驗證狀態 |
|---|---|---|---|---|
| 1 指示 | `CLAUDE.md` 裡的 sentinel 紀律區塊(`scripts/templates/graph-discipline.md`,6.6k;`lumos init/update` 刷、doctor Check D 比對) | `AGENTS.md`(全域 `~/.codex/AGENTS.md` + 從 git 根往下逐層串接;總量預設 32 KiB) | reinject 同時寫 CLAUDE.md 與 AGENTS.md 兩檔同一塊;Check D 兩檔都比;版本戳兩檔都讀 | ✅實驗 4:未信任 repo 的 AGENTS.md 會載入(哨兵字回到最終回覆) |
| 2 skills | `~/.claude/skills/lumos-*` symlink(`_install_skills`) | 使用者層 `~/.agents/skills/`(文件);repo 層 `.agents/skills/` 或 `.codex/skills/` | `_install_skills` 多一個目標;uninstall/teardown 對稱;skill 內文的 Claude 專屬字眼加「Codex 下對應」一小表 | ✅實驗 4:repo 層 `.agents/skills/` 未信任也載入且會被隱式選用;★使用者層 `~/.agents/skills/` 未測★ |
| 3 hooks | 5 支 `.py` copy 到 `~/.claude/hooks/`,`merge-claude-settings.py` 合併進 settings.json;事件=SessionStart×2(進場提醒、CI 狀態)/PreToolUse Edit\|Write\|MultiEdit(影響幅度)/PreToolUse Agent(派工鏡頭)/Stop(收工同步) | `~/.codex/hooks.json`(同 JSON 形);事件表同名;matcher 名:`Bash`、`apply_patch`、`Edit`、`Write`;子代理=`SubagentStart`/`SubagentStop` | 合併器抽成「目標可指定」;五支 hook 各自認 Codex 的 payload 形狀(見 S1) | ✅實驗 2/4/5:PreToolUse 在 exec 下 fire、apply_patch 攔得到、SubagentStart additionalContext 到子代理;❌matcher "Agent" 沒攔到 spawn;❌spawn message 加密 |
| 4 迴圈編排 | design-loop / code-loop skill 叫主對話「派 Agent、model sonnet」;外家席=Codex(`codex exec`) | `spawn_agent`(內建 explorer/worker/default;自訂 `~/.codex/agents/*.toml` 帶 developer_instructions、sandbox) | 模板去 Claude 專屬字眼、每處給兩家寫法;裝一支 `lumos-reviewer.toml`(唯讀沙盒+審查員框架);外家席規則改成「不是當下編排者那一家」;席名統一 | ✅實驗 3/5:exec 下能派子代理;欄位分三個事件——SubagentStart 帶 agent_id+agent_type(實驗 5 hook.log 實看),子代理自己的 PreToolUse 帶 agent_id,SubagentStop 才帶 agent_transcript_path;★自訂 TOML 未試★ |
| 5 量測 | `governance/eval/lens-utilization/recount.py` 讀 `~/.claude/projects/**.jsonl`;`scripts/scenario_probe.py` 跑 `claude -p` | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`(型別 session_meta/response_item/event_msg…;user_message 明文;spawn 的 message 加密) | recount 多一個 reader;probe 多一個 runner(`codex exec --json`) | ✅逐字稿位置與型別看過一份;★shell 呼叫參數是否明文、hook 注入有沒有落逐字稿★未查 |
| 6 安裝/拆機/體檢 | `lumos install/uninstall/teardown/enforcement/doctor` | 同一組指令 | install 多寫 Codex 三處;teardown 對稱清;enforcement 多三層(`codex-hooks`/`codex-skills`/`agents-md`);doctor Check D 擴兩檔 | 純自家碼,無外部未知 |

## 範圍與明確不做

- **做**:上表六層在 Codex CLI(本機 0.144.1)下接上,以「`codex exec` 非互動」為主驗場,互動模式只做一次人工冒煙(hook 在互動模式的專案層信任問題見隱患)。
- **不做**:①不把 Codex 當 MCP server 或用 `codex review`(調研候選 2,另案)②不動 `codex exec --output-schema` 鎖席報告格式(候選 1,獨立小案,不混進來)③不寫 TOML(不動 `~/.codex/config.toml`)④不支援 Codex 專案層 `.codex/hooks.json`(未信任不載入,文件明寫)⑤不做 Windows 的 Codex 路徑(Codex 本機只驗 macOS;Windows 只保證不炸)。

## 分階段(每階段各自過驗收才進下一階段;S0 是地基,S1 是本案價值主體)

### S0 安裝層(純自家碼,先做;預估 ≲200 行含測試)

1. **skills**:`_install_skills` 目標從單一 `~/.claude/skills` 變成清單 `(~/.claude/skills, ~/.agents/skills)`,同一支 `_link_or_copy`;`cmd_uninstall`/`_teardown_*` 對稱清兩處。★先實測使用者層 `~/.agents/skills/` 會不會被 Codex 載入(HOME 隔離跑一次 `codex exec` 列 skills)★——載入不成就退回「repo 層 `.agents/skills/` 由 `lumos init` 放 symlink」這條備援(已證會載入),兩條都寫進 install。
2. **hooks 註冊**:`merge-claude-settings.py` 抽出「目標檔+HOOK_ENTRIES 轉換」兩個參數:Claude 目標 `~/.claude/settings.json` 的 `hooks` 段;Codex 目標 `~/.codex/hooks.json` 頂層 `hooks` 段(同形)。matcher 對照表寫死在合併器:`Edit|Write|MultiEdit`→`apply_patch|Edit|Write`;`Agent`(PreToolUse)→改掛 `SubagentStart`(無 matcher);`Stop`→`Stop`;SessionStart→SessionStart。hook 腳本檔 copy 到 `~/.codex/hooks/`(跟 `~/.claude/hooks/` 同一批檔、同一個來源)。懸空剪除、兩階段撤除(STUB→DELETE)兩邊同規則。
3. **AGENTS.md 區塊**:`_reinject_claude_block` 改成對 `(CLAUDE.md, AGENTS.md)` 各跑一次同一段;AGENTS.md 不存在就建(只含區塊);Check D 兩檔都比、任一漂移都 warn。本 repo 現有 8 行指路 AGENTS.md 保留在區塊外(sentinel 外文字不動,既有機制本來就這樣)。
4. **enforcement 三層**:`codex-hooks`(`~/.codex/hooks.json` 五支都註冊且檔在)、`codex-skills`(兩個目標任一有 lumos-* 連結)、`agents-md`(區塊在且版本戳與 CLAUDE.md 一致);Codex 沒裝(`shutil.which("codex")` 為 None)→三層一律 `inactive` 帶「本機無 codex,略過」,不算 degraded。
5. **測試**:HOME 隔離(現有 `_sync_global_claude` 測試已用 HOME 隔離,沿用)驗 install→三處都在、teardown→三處都空;合併器對照表逐條測;Check D 雙檔漂移各測一次。

### S1 hook 適配(每支 hook 的 Codex 差異只在 payload 形狀;一支腳本、認形狀、不嗅探環境)

| hook | Claude 下吃什麼 | Codex 下差在哪 | 適配 |
|---|---|---|---|
| lumos-entry-hook(SessionStart) | `cwd` | 同欄位 | 零改;`enforcement` 輸出改讀 Codex 層 |
| ci-status-hook(SessionStart) | `cwd` | 同欄位 | 零改 |
| impact-hook(PreToolUse) | `tool_input.file_path` | apply_patch 的 `tool_input.command` 是 patch 全文,★沒有 file_path★;`Edit`/`Write` 工具(若 Codex 真有)形狀未見 | `extract_path` 多一條:command 以 `*** Begin Patch` 開頭→解 `*** Add File: / *** Update File: / *** Delete File:` 標頭取路徑(可能多檔→取第一個非排除檔,其餘列名);TTL 冷卻、shebang 判定、fail-open 全沿用 |
| dispatch-lens-hook(Claude: PreToolUse Agent + updatedInput) | 派工詞裡 `LUMOS-IMPACT: <range>` 標記 | ★派工詞在 hook 眼裡是加密字串(實驗 4),讀不到標記也改不了★ | 新增 `lumos dispatch-lens <range> --arm`:算好鏡頭文字後落 `~/.cache/lumos/dispatch-lens/armed/<repo-hash>.json`(含 range、產生時間、TTL 30 分、repo 根),Codex 側 SubagentStart hook 讀它→`additionalContext`(實驗 5 證會到子代理);沒 armed 檔或過期→什麼都不回。Claude 側 PreToolUse+標記行★照舊不動★(已上線、有錨點),兩條路共用同一支 `dispatch-lens` 算清單 |
| check-graph-sync(Stop) | `transcript_path` 讀 Claude 逐字稿找本 session 有沒有敲 lumos:逐字稿 tool_use 區塊的 `input.command`/`input.file_path`(注意:逐字稿鍵名是 `input`,PreToolUse payload 才叫 `tool_input`) | Codex 逐字稿型別不同(`response_item/function_call` 帶 name+arguments) | reader 認兩種格式(以第一行 `session_meta` 判 Codex);★shell 參數在 Codex 逐字稿是否明文未查★,不是明文就退回「只看 hook 自己記的 usage-log」 |

S1 驗收=S0 的隔離環境裡真跑 `codex exec`:①apply_patch 改一個有合約的檔→hook 印出的合約行進 usage-log ②`dispatch-lens --arm` 後派子代理→子代理回報裡有鏡頭段的固定字彙(例如 `INVARIANT` 那行) ③Stop 後 usage-log 多一筆 Codex session。

### S2 迴圈從 Codex 編排(skill/模板層,散文為主)

- 三個 skill(`lumos-design-loop`、`lumos-code-loop`、`lumos-project-notes`)裡凡寫「Agent、model sonnet、`/skill`」的位置,改成一行兩家:「派乾淨審查員(Claude:Agent 工具 sonnet;Codex:`spawn_agent`,agent=lumos-reviewer)」;`$lumos-design-loop` 顯式叫法補進 INDEX。
- `~/.codex/agents/lumos-reviewer.toml`:`sandbox_mode="read-only"`、`developer_instructions`=templates.md 審查員框架的固定段;由 install 放、teardown 收。
- **外家席規則**改寫成家族相對:「外家=不是當下編排者那一家;Claude 編排→`codex exec`,Codex 編排→`claude -p`」——[[Systems/canary-audit]] 與 [[Systems/design-loop]] 的跨家族席原則(外家 blocker 不得僅被同門多數推翻)不變,只是把「Codex」從常數變成變數。
- 席名統一(調研候選 6):`--auditor` 席名規範 `ext-<家族>`,`loop status` 家族辨識靠它;舊帳不回溯。

### S3 量測(最後做;依賴 S1 的逐字稿 reader)

- recount 多一個 Codex reader(路徑 `~/.codex/sessions/**`,以 `cwd` 過濾 repo);probe 多一個 runner(`codex exec --json`,配額限制另量)。★沒查★:hook 的 additionalContext 有沒有落 Codex 逐字稿——沒有的話「利用率」在 Codex 側量不到「推到眼前」那一半,只能量「有沒有讀」。

## 擬裁定(a)–(d)的理由(供審查席打)

- **(a) AGENTS.md 放同一塊、不放指路**:指路(叫模型「去讀 CLAUDE.md」)要模型多做一步、沒機械保證;`project_doc_fallback_filenames=["CLAUDE.md"]` 只在 AGENTS.md 不存在時生效,多數 repo 有 AGENTS.md。重複兩檔的漂移風險由既有 reinject+Check D 機械兜住(這正是 session memory「知識同步散落會漏、需機械守衛」那條教訓要的守衛)。代價:每個專案多一個 6.6k 的檔,佔 Codex 32 KiB 預算兩成。
- **(b) hooks.json 不寫 config.toml**:python3 stdlib 只有 `tomllib`(唯讀,3.11+),寫 TOML 得自己拼字串或加依賴;hooks.json 官方支援、跟 Claude settings 同形,合併器幾乎不用改。★沒查★:使用者 `config.toml` 若同時有 `[hooks]`,兩邊是合併還是覆蓋——S0 實測一次。
- **(c) `--arm` 檔而不是改派工詞**:實驗 4 硬事實。備選「把標記寫進 AGENTS.md 讓 fork_turns=all 的子代理繼承」不可控(每個子代理都會看到、跟派工無關)故不取。armed 檔 TTL 30 分=一輪代碡審派工的合理窗口(暫用值,沒量)。
- **(d) 外家相對化**:不做的話 Codex 編排時外家還是 Codex,同家族互審違反跨家族原則。

## 驗收(全機械,S0–S3 各自跑;總驗收=四條都綠)

1. 隔離 HOME 下 `lumos install` 後:`~/.agents/skills/lumos-*`(或 repo 層備援)存在、`~/.codex/hooks.json` 五支註冊且檔在、專案 `AGENTS.md` 有區塊且版本戳等於 CLAUDE.md;`lumos enforcement --json` 三層 active。
2. 同環境 `lumos teardown` 後三處全空、`enforcement` 三層 inactive、`doctor` 綠。
3. S1 三條(見上)在真 `codex exec` 下各跑一次,結果留 `Verification/` 一篇。
4. 測試套件全綠、anchor 重核可(hook 腳本都是錨點檔)、`lumos pitfalls --diff` 分級照走代碼審。

## 誠實界線

- **互動模式沒驗**:全部實驗在 `codex exec`。GitHub issue #17532 說互動模式專案層 hook 有不 fire 的症狀;本案只走使用者層(文件說那個症狀限專案層),但★沒跑過互動模式★,是否受影響以下面那次冒煙為準。REVISIT:2026-09-25 開一次互動 Codex 在 lumos 專案裡改一檔,看 usage-log 有沒有多一筆。
- **綁版本**:matcher 別名 `Agent` 不匹配、spawn message 加密、`collaborationspawn_agent` 這個工具名,都是 0.144.1 的觀測;Codex 改版任一條翻掉,S1 的鏡頭路徑要重測。事件入口=`lumos enforcement` 印 codex 版本並跟記在圖譜的驗證版本比,不同就唸一句。
- **Codex 側鏡頭少一個能力**:Claude 側鏡頭是「附在派工詞裡」(每席必看);Codex 側是「子代理開場的開發者上下文」,位置不同,子代理讀不讀我們一樣量不到(鏡頭不量成效,見 [[Projects/派工鏡頭注入_計劃]] 誠實界線)。
- **不證明 Codex 下的 lumos 比較好用**,只證六層接上了。

## 未解(動工前要答,不需審查席)

- `~/.agents/skills/` 使用者層載入與否(S0 第一件事);`config.toml [hooks]` 與 `hooks.json` 並存規則;`Edit`/`Write` 在 Codex 是不是真有獨立工具還是只是 apply_patch 的別名。
- Codex 逐字稿裡 shell 參數是否明文(決定 check-graph-sync 的 Codex reader 能不能做)。

## 實務隱患(逐類答)

- **資料/狀態**:armed 檔是跨 process 的共享狀態→放 `~/.cache/lumos/dispatch-lens/`(既有目錄,0700、驗 owner 的規矩沿用),帶 TTL,過期即忽略;AGENTS.md 兩檔重複→reinject 一次寫兩檔、Check D 機械比對,不靪人記。
- **時序/並行**:兩個 Codex session 同 repo 同時派工共用一個 armed 檔→後寫者勝,鏡頭內容仍是「同 repo 同 range」通常一致;不一致只是鏡頭錯席,不擋任何事(鏡頭不是閘)。
- **失敗與回復**:所有 hook fail-open(沿用);hooks.json 壞→合併器先驗可解析、壞就不動+warn(沿用 teardown 的規矩);Codex 未安裝→install 跳過 Codex 三處並印一行,enforcement 標 inactive 不算壞。
- **權限/安全**:hooks.json 寫在使用者家目錄(跟 settings.json 同等級);subagent additionalContext 內容沿用 dispatch-lens 的零自由文字消毒原則(只印 base 已追蹤路徑與固定字彙),不因換通道放寬。
- **相容/升級**:Codex 改版風險見誠實界線;hook 兩階段撤除規則兩邊同套;`_GLOBAL_CLAUDE_HOOKS` 元組名不改(避免大改),註解寫明「兩家共用」。
- **可觀測**:`lumos enforcement` 多三層;usage-log 記 `harness: codex|claude`(由 payload 有無 `permission_mode`+`model` 欄位判,不嗅 env)。
- **已排除**:金流/對外寄送/正式環境不可逆——本案全部本機工具鏈,無此類面。

## 合約候選(過閘後蓋章走 guard scaffold→bind→audit,候選≠已標)

- 「消毒原則對兩條通道一致」:Codex SubagentStart 通道輸出必須是 `dispatch-lens` 同一支函式的產物,不得另拼字串。
- 「install/teardown 對稱」:Codex 三處在 teardown 後必為空(既有 teardown 合約的延伸)。

REVISIT:2026-09-25 互動模式 Codex 冒煙一次(見誠實界線第一條)。
REVISIT:2026-10-04 若 S0/S1 已上線,查一個月內 Codex 側 usage-log 筆數;0 筆=沒人用 Codex 開 lumos 專案,S2/S3 降優先。

## 審計修正紀錄(lumos-design-loop)

(尚未開審)
