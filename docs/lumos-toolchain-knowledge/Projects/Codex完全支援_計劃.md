---
type: project
status: done
created: 2026-09-04
updated: 2026-09-05
tags:
  - type/project
  - status/done
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
  - "[[Systems/canary-audit]]"
  - "[[Systems/codex-harness]]"
summary: |-
  FLAG:DECISION
  KEY:目標=在 Codex CLI 下開一個 lumos 專案,得到跟 Claude Code 下★同一套★六層防護:指示(AGENTS.md)/skills/hooks(進場、影響幅度、派工鏡頭、收工同步)/迴圈編排/量測/安裝-拆機對稱;不做第二套邏輯,每層都是「同一支 lumos、多一個接頭」
  KEY:★2026-09-04 實驗 4/5 定下四個地基事實★:①未信任 repo 的 AGENTS.md 與 .agents/skills/ 都會載入 ②PreToolUse 攔得到 apply_patch(tool_input.command=patch 全文,沒有 file_path)③spawn_agent 的 message 在 hook 眼裡是加密字串→updatedInput 改派工詞這條路在 Codex 不通;matcher "Agent" 也沒攔到(工具名 collaborationspawn_agent)④SubagentStart 的 additionalContext 會到子代理手上→Codex 側派工鏡頭走這條
  KEY:r1(2026-09-04,3 席+架構+外家 Codex)47 條/blocker 6(3 席各 1–3)/全折、accepted 空;外家 F1「message 可 rewrite」被實驗 A 反證不採信;★新地基事實(實驗 C/D)★:使用者層 hook 不按一次互動 TUI 的 Trust 就不跑,exec 只能靪 --dangerously-bypass-hook-trust,信任存放處沒查出來
  KEY:r2 驗收輪 26 條全折:armed 改 token 原子認領+TTL 先驗;--orchestrator 首輪必帶無預設;reinject 檔頭/無標題/語意衝突三個邊界;skill 掃描含 reference/templates;多檔 impact 上限 5 檔 20 秒
  KEY:S0–S3 全部實作(2026-09-04;S3=recount 讀 Codex 稿+probe --runner codex):S0 安裝層+S1 hook 適配+S2 編排者旗標/家族相對化/skill 兩家字句;★自訂 agent 在 exec 選不中→d5 退路=父代理唯讀+框架進派工詞★
  KEY:四個擬裁定(r1/r2 折入後):(a)AGENTS.md(有 AGENTS.override.md 則寫它)放同一塊 sentinel 區塊、插在檔首、reinject/剝除/Check D 三端雙檔、doctor 估 chain 總量 (b)hook 註冊寫 ~/.codex/hooks.json 不寫 config.toml(stdlib 沒 TOML 寫入器,零依賴) (c)鏡頭範圍改由 `lumos dispatch-lens <range> --arm --seats N` 落 armed 檔(repo key=realpath 的 sha256,TTL 10 分,消耗 N 次即刪,鏡頭文字首行印 range);SubagentStart hook 讀它;Claude 側標記行照舊;架構席判無先例=平台逼出的有意識偏離 (d)外家席=「不是當下編排者那一家」:記帳/問閘加 --orchestrator claude|codex(預設 claude),_roster_family 相對化;席名沿既有 <鏡頭>-<模型> 慣例
  KEY:分四階段,每階段各自驗收:S0 安裝層(skills symlink→~/.agents/skills、hooks.json 合併器、AGENTS.md 區塊、enforcement 三層、teardown 對稱)→S1 hook 適配(apply_patch 取檔、SubagentStart 鏡頭、check-graph-sync 讀 Codex 逐字稿)→S2 迴圈從 Codex 編排(自訂 agent TOML、模板去 Claude 字眼、外家互換、席名統一)→S3 量測(recount/scenario_probe 多一個 runner)
decisions:
  - content: AGENTS 檔放同一塊 sentinel 紀律區塊(該層有 AGENTS.override.md 就寫 override,否則 AGENTS.md),插在檔首;reinject/剝除/Check D 三端共用同一份目標清單;doctor 估每層生效檔總量/32KiB >75% warn。不用指路、不用 project_doc_fallback_filenames
    id: d1
    context: Codex 不讀 CLAUDE.md;指路要模型多做一步沒機械保證;fallback 檔名只在該層無 AGENTS*.md 時生效;32KiB 為整鏈上限且截斷靜默
    why_chosen: 重複兩檔的漂移由既有 reinject+Check D 機械兜住;截斷只能降機率不消滅,誠實界線記
    decided: 2026-09-04
    valid: true
  - content: Codex hook 註冊寫 ~/.codex/hooks.json、不解析不改寫 config.toml;hook 命令列帶 --harness codex 明確旗標,不由 payload 欄位判家族;合併器抽目標參數,失敗回三態 merge-failed
    id: d2
    context: stdlib 只有 tomllib 唯讀;hooks.json 外層與 Claude settings 同形;Codex 與 Claude 的 hook 輸入都有 permission_mode 欄位,靠欄位判不可靠;現碼呼叫端把 False 寫死成探針訊息
    why_chosen: 零新依賴;明確旗標不會因兩家 payload 趨同而失準;三態避免壞 JSON 印假成功
    decided: 2026-09-04
    valid: true
  - content: Codex 側派工鏡頭走 SubagentStart additionalContext;範圍由 lumos dispatch-lens <range> --arm --seats N 落 armed 目錄(key=repo realpath 的 sha256,TTL 10 分,N 個 token 檔原子認領,先驗 TTL 再認領,任一不成立即不回);Claude 側 PreToolUse+標記行照舊。列為有意識偏離(無先例)
    id: d3
    context: 實驗 A:spawn_agent 的 message 在 hook 眼裡是密文,回 updatedInput 換明文即 Encrypted function output content could not be decrypted;matcher Agent 不匹配;實驗 5:SubagentStart additionalContext 到子代理
    why_chosen: 平台限制逼出的唯一可用通道;token 原子認領解重複扣減、TTL 先驗解過期誤注入;餓死與錯席承認為界線,REVISIT 2026-10-04
    decided: 2026-09-04
    valid: true
  - content: 外家席相對化到機械層:loop next 首輪必帶 --orchestrator claude|codex(比照 --tier,持久化到帳,不給新呼叫預設;舊帳缺欄視為 claude),record/status 讀帳缺=擋;_roster_family 改回同門/外家;席名沿 <鏡頭>-<模型> 慣例。Codex 編排時外家=claude -p
    id: d4
    context: _ROSTER_EXTERNAL_KEYS/_ROSTER_CLAUDE_KEYS 靜態關鍵字表無編排者參數;席位對帳是 advisory 觀測、不進合取,失準會讓人放行同門互審
    why_chosen: 跨家族席原則(canary-audit/design-loop)不變,只把 Codex 從常數變變數;預設 claude 會讓 Codex 編排漏旗標時靜默套錯家族
    decided: 2026-09-04
    valid: true
  - content: S2 不裝自訂 agent TOML:Codex 編排時審查席用 spawn_agent,審查員框架寫進派工詞,父代理以 codex exec --sandbox read-only 開讓子代理繼承唯讀;外家席換 claude -p
    id: d5
    context: "進場實驗兩次(檔名 lumos-reviewer 與 lumos_reviewer,放 CODEX_HOME/agents/)派工詞點名後 SubagentStart agent_type 仍是 default、子代理可寫檔;父代理 --sandbox read-only 時子代理 apply_patch 被擋(patch rejected: writing is blocked by read-only sandbox)"
    why_chosen: 0.144.1 的 codex exec 下自訂 agent 選不中,沒證實的接頭不裝;唯讀由父代理沙盒繼承同樣可證;框架進派工詞與 Claude 側同形。REVISIT:2026-09-25 互動模式再試一次自訂 agent
    decided: 2026-09-04
    valid: false
    superseded_by: d6
    ended: 2026-09-05
  - content: S2 補裝 Codex 自訂 agent TOML:install 對 Codex 寫 CODEX_HOME/agents/lumos_reviewer.toml(底線名;name/description/developer_instructions=審查席框架;sandbox_mode=read-only 只當提示),teardown 收;★唯讀仍靠父代理 --sandbox read-only★(TOML 的沙盒欄實測不擋);舊版 codex 選不中時檔案無害、走 d5 退路
    id: d6
    context: 0.153.2 暫存安裝實測:spawn_agent 多 agent_type 參數、SubagentStart agent_type=lumos_reviewer、developer_instructions 到子代理;但 TOML sandbox_mode=read-only 下子代理在父 workspace-write 仍寫成 note.txt;0.144.1 全域版仍選不中
    why_chosen: 身分與框架由 TOML 給是官方通道且新版可證;沙盒不能信 TOML 所以 d5 的唯讀規則保留;版本差異靠 enforcement 印版本+誠實界線
    decided: 2026-09-05
    valid: true
---
# Codex完全支援_計劃

> 白話:現在 lumos 的「防護」全掛在 Claude Code 上——進 session 時有人提醒你去查圖譜、改檔前有人把相關合約推到眼前、派審查員時有人把清單附進派工詞、收工時有人查你有沒有寫回圖譜。這些全靠 Claude Code 的四種接頭(CLAUDE.md、skills、hooks、子代理)。Codex CLI 0.144.1 四種接頭都有、形狀相近。本案要做的是:**同一支 lumos、同一批 hook 腳本,多接一組 Codex 的接頭**,讓人用 Codex 開 lumos 專案時拿到同一套防護。★不寫第二套邏輯★——Codex 專屬的只有「接頭」那一薄層。r1 審查(47 條)把「形狀一樣」修正成「外層一樣、內層三處不同」:派工訊息對 hook 不透明、hook 要人按一次信任才跑、AGENTS.md 有 override 檔與 32 KiB 全鏈預算。

PRIOR-ART: ① 最小解層級——四種接頭 Codex 都原生提供:hooks.json 的**外層** JSON 結構跟 `~/.claude/settings.json` 的 `hooks` 段同形(事件名、matcher、`{type,command,timeout}`;★內層語意不同:matcher 名、payload 形狀、輸出欄位要求各自查★);skills 是同一個開放標準(agentskills.io,SKILL.md 同格式)所以 symlink 就能用、不用轉檔;AGENTS.md 跟 CLAUDE.md 一樣是「開 session 自動進 prompt 的 markdown」,既有 sentinel 注入機制(`_reinject_claude_block`)多寫一個檔;子代理開場的 additionalContext 是 Codex 自己設計給「餵子代理脈絡」的通道。② 世界解過沒——「一套 agent 工具鏈同時支援 Claude Code 與 Codex」在 2026 已是常態(superpowers skill 自帶 `references/codex-tools.md` 就是這種雙接頭寫法),做法一律是「共用內容+每家一個薄 adapter」。③ 裁定=borrow-design(Codex 官方通道)+ 零新依賴(避開寫 TOML 就不需要任何套件)。★PRIOR-ART 缺口(架構席 r1 ⚠)★:「armed 檔+SubagentStart 非同步交接」在本 repo 沒有先例(最近的 `_lens_cache_*` 是記憶化、impact-hook TTL 標記是冷卻窗,用途都不同);它是 Codex 派工訊息不透明逼出來的,列為有意識偏離,不當慣例。

## 一句話

lumos 的六層防護(指示 / skills / hooks / 迴圈編排 / 量測 / 安裝拆機)在 Codex CLI 下逐層接上,驗收標準是「乾淨機器、隔離 HOME 與 CODEX_HOME,`lumos install` 一次,Codex 開 lumos 專案時六層機械可證都生效;`lumos teardown` 一次全部乾淨(用檔案存在性與 enforcement 機械驗,不靠 teardown 的回傳碼——它三步不看 rc 固定回 0,file: `scripts/lumos:10362-10372`)」。

## 「完全支援」的定義(六層對照;沒對到的就不算完全)

| 層 | Claude Code 現況(都已上線) | Codex 對應接頭 | 本案要做的 | 地基驗證狀態 |
|---|---|---|---|---|
| 1 指示 | `CLAUDE.md` 裡的 sentinel 紀律區塊(`scripts/templates/graph-discipline.md`,6.6k;`lumos init/update` 刷、doctor Check D 比對) | `AGENTS.md`;★同層若有 `AGENTS.override.md` 則只讀它★;全域 `~/.codex/AGENTS.md` + 從 git 根往 cwd 逐層串接;★32 KiB 是整條鏈的合併上限,超過靜默截斷★ | reinject/剝除/Check D 三端都改成「目標清單」:CLAUDE.md + (該層有 override 就 override,否則 AGENTS.md);區塊插在檔首(第一個標題之後)而不是尾端,降低被截斷機率;doctor 多估一行「本 repo 各層 AGENTS 檔總量/32 KiB」 | ✅實驗 4:未信任 repo 的 AGENTS.md 會載入 |
| 2 skills | `~/.claude/skills/<全部 8 支>` symlink(`_install_skills` 用 `_skills_list()` 掃 `skills/` 下所有含 SKILL.md 的目錄——含 3 支語言慣例 skill,不只 lumos-*) | 使用者層 `~/.agents/skills/`(文件);repo 層 `.agents/skills/`(★官方只列這一個,`.codex/skills/` 不存在,r1 外家 F3★) | `_install_skills` 多一個目標;uninstall/teardown 對稱清;★新目標是開放共用目錄:既有真目錄只有帶我方 `.lumos-managed` 標記檔才重建,否則跳過+warn,不得沿用 `_link_or_copy` 的無條件 rmtree(邊界 F2/r2 N1)★;五支 lumos skill 的 Claude 專屬字眼全部處理(不只三支,整合 F5) | ✅實驗 4:repo 層 `.agents/skills/` 未信任也載入且被隱式選用;★使用者層 `~/.agents/skills/` 未測★ |
| 3 hooks | 5 支 `.py` copy 到 `~/.claude/hooks/`,`merge-claude-settings.py` 合併進 settings.json;事件=SessionStart×2/PreToolUse Edit\|Write\|MultiEdit/PreToolUse Agent/Stop | `~/.codex/hooks.json`(外層同形);matcher 名:`Bash`、`apply_patch`(`Edit`/`Write` 只是它的別名,tool_name 仍回 apply_patch);子代理=`SubagentStart`/`SubagentStop`;★hook 要在互動 codex 裡審過(啟動時的 Hooks need review 畫面或 `/hooks`)才會跑,信任綁 hook 定義的內容 hash——lumos 每次更新 hook 檔都要再審一次;exec 下只能帶 `--dangerously-bypass-hook-trust`;沒有 CLI 能標信任,信任存放處沒查出來(實驗 C/D;綁 hash 與 `/hooks` 是文件宣稱)★ | 合併器抽成「目標可指定+對照表」;註冊命令列帶明確 `--harness codex`(不嗅 payload 欄位);install 與 update 結尾都印「開互動 codex 審一次 hook(信任綁命令列,只換檔內容不用重審)」;enforcement 的 codex hook 層最多到「已註冊、信任狀態本機讀不到」,不單獨綠 | ✅實驗 2/4/5:帶旗標時 PreToolUse fire、apply_patch 攔得到、SubagentStart additionalContext 到子代理;❌matcher "Agent" 沒攔到 spawn(完整名 collaborationspawn_agent 攔得到,實驗 B);❌spawn message 為密文,rewrite 直接弄壞派工(實驗 A);❌不帶旗標 hook 0 筆(實驗 C/D) |
| 4 迴圈編排 | design-loop / code-loop skill 叫主對話「派 Agent、model sonnet」;外家席=Codex;★家族判定是靜態關鍵字表(`_ROSTER_EXTERNAL_KEYS`/`_ROSTER_CLAUDE_KEYS`,file: `scripts/lumos:5711-5712`),`_roster_family(auditor)` 沒有「編排者」參數★ | `spawn_agent`(介面只有 task_name/message/fork_turns,★沒有 agent 參數★;自訂 agent 靠派工詞點名或 description 匹配);自訂 `~/.codex/agents/*.toml`(必填 name/description/developer_instructions) | 模板去 Claude 專屬字眼、每處給兩家寫法;裝一支 `lumos-reviewer.toml`;★記帳/問閘加 `--orchestrator claude\|codex`(預設 claude),家族判定相對化(整合 F3 blocker)★;席名沿既有 `<鏡頭>-<模型>` 慣例(架構 #2) | ✅實驗 3/5:exec 下能派子代理;SubagentStart 帶 agent_id+agent_type、子代理 PreToolUse 帶 agent_id、SubagentStop 帶 agent_transcript_path;★自訂 TOML 未試★ |
| 5 量測 | `governance/eval/lens-utilization/recount.py` 讀 `~/.claude/projects/**.jsonl`;`scripts/scenario_probe.py` 跑 `claude -p`;★`.usage-log.jsonl` 唯一寫入者是 `lumos show/context` 的 `_usage_log`(schema `{ts,node,cmd}`),hook 不寫任何檔★ | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`(user_message 明文;spawn 的 message 密文;★官方明示逐字稿格式不是穩定介面★) | recount 多一個 reader(帶版本 fixture,認不得就跳過並記一行);probe 多一個 runner | ✅逐字稿位置與型別看過一份;★shell 呼叫參數是否明文、hook 注入有沒有落逐字稿★未查 |
| 6 安裝/拆機/體檢 | `lumos install/uninstall/teardown/enforcement/doctor`;★`_sync_global_claude` 不看合併器 returncode、無條件 return True(file: `scripts/lumos:11084-11087`)★ | 同一組指令 | install 多寫 Codex 三處並檢查合併器 rc;teardown 對稱清(含剝除端 `_deinit_strip_claude` 雙檔,file: `scripts/lumos:10653`);enforcement 多層(見 S0);doctor Check D 目標清單化 | 純自家碼,r1 抓到兩個既有吞錯點,見左欄 |

## 範圍與明確不做

- **做**:上表六層在 Codex CLI(本機 0.144.1)下接上;主驗場=隔離 HOME+CODEX_HOME 下的 `codex exec`(★只在這個隔離環境、且 hooks.json 只含 lumos 五支時才帶 `--dangerously-bypass-hook-trust`★);互動模式做一次人工信任冒煙(見驗收)。
- **不做**:①不把 Codex 當 MCP server、不用 `codex review`(調研候選 ②;候選 ① `--output-schema` 另開小案)②★不解析、不改寫既有 `~/.codex/config.toml`★(S2 的 agent TOML 是新建檔,用字串範本寫出、不需 TOML 寫入器)③不支援 Codex 專案層 hook(文件明寫專案層 `.codex/` 要信任才載入;實驗 1 測的是 `.codex/config.toml` 的 `[hooks]`,`.codex/hooks.json` 這個檔沒單獨測,兩檔並存規則見 S0 進場 2)④不做 Windows 的 Codex 路徑(只保證不炸)⑤不替使用者按信任、不寫信任存放處(那是 Codex 的安全控制)。

## S0 進場條件(r1 折入:未解四題先答,答不出不開工)——★2026-09-04 四題全答(隔離 HOME 實驗,scratchpad entry/)★

答案:1 `~/.agents/skills/` 使用者層★會載入★(HOME 指隔離目錄,哨兵 skill 被列出並帶識別碼)→ 不需 repo 層備援,install 直接連。2 `config.toml [hooks]` 與 `hooks.json` ★兩邊都跑★(各記到一筆,合併不覆蓋)→ 寫 hooks.json 不會蓋掉使用者自己在 toml 裡的 hook。3 matcher ★只有完整名 `collaborationspawn_agent` 命中★(`spawn_agent`、`Agent` 各 0 筆,三次分開跑)。4 逐字稿 shell 呼叫★明文★:型別 `custom_tool_call`、name `exec`、input 是一段 JS `tools.exec_command({"cmd":"cat alpha.py",…})`——可正規式抽 cmd,但不是 Claude 那種 `input.command` 結構。

1. `~/.agents/skills/` 使用者層 Codex 會不會載入(隔離 HOME 跑一次列 skills)。不載入→備援=`lumos init` 在 repo 層放 `.agents/skills/` symlink(已證載入),兩條都寫進 install。
2. `config.toml [hooks]` 與 `hooks.json` 並存時的規則(合併/覆蓋)。
3. 分開驗 matcher `spawn_agent` 與 `collaborationspawn_agent` 哪個命中(實驗 B 兩條並列只記到一筆,未分開;S1 表「攔得到」指的是實驗 B 這一筆,哪個名字命中仍是推測)。
4. Codex 逐字稿裡 shell 參數是否明文(決定 check-graph-sync 的 Codex reader 可不可做;不可做→該層只做「認不得就跳過」)。

## 分階段(每階段各自過驗收才進下一階段)

### S0 安裝層(純自家碼;預估 ≲300 行含測試)

1. **skills**:`_install_skills` 目標從單一 `~/.claude/skills` 變成清單 `(~/.claude/skills, ~/.agents/skills)`;★對新目標:dst 若是既有真目錄→只有目錄內有我方標記檔 `.lumos-managed`(fallback 複製時一併寫入)才 rmtree 重建,否則跳過+印一行 warn,不刪★(`~/.claude/skills` 沿既有行為,但 fallback 複製同樣寫標記檔,兩邊判法一致);`cmd_uninstall`/`_teardown_*` 對稱清兩處,且只清 symlink。明列會被連過去的是全部 8 支(5 支 lumos-*+3 支語言慣例),3 支語言慣例無 Claude 專屬工具引用、照連。
2. **hooks 註冊**:`merge-claude-settings.py` 抽出「目標檔+對照表」參數。Codex 對照表:`Edit|Write|MultiEdit`→`apply_patch`;PreToolUse `Agent`→改掛 `SubagentStart`(無 matcher);`Stop`→`Stop`;SessionStart→SessionStart。註冊命令列一律 `python3 ~/.codex/hooks/<hook>.py --harness codex`(Claude 側維持無旗標=claude)。hook 檔 copy 到 `~/.codex/hooks/`。★`_sync_global_*` 檢查合併器 returncode:非 0→印「hooks 設定檔損毀/合併失敗」的 warn 並回第三態 `merge-failed`(現碼 False 只代表探針擋下、呼叫端訊息寫死 LUMOS_PROBE,file: `scripts/lumos:10235-10238`,不能共用一顆布林),呼叫端三態各印各的(邊界 F5/r2 N2)★。懸空剪除、兩階段撤除(STUB→DELETE)兩邊同規則;常數改名 `_GLOBAL_HOOKS`(保留 `_GLOBAL_CLAUDE_HOOKS` 別名給測試,架構 #1)。install 與 update 結尾印:「Codex 的 hook 要你開互動 `codex`,在 Hooks need review 畫面(或 `/hooks`)審一次;命令列變了才要重審(只換檔內容不用);exec 不會問」。
3. **AGENTS.md 區塊**:`_reinject_claude_block(root, slug, targets)`——目標清單=`[CLAUDE.md, AGENTS.override.md 若存在否則 AGENTS.md]`;四個呼叫點(`_vendor_toolchain`、`cmd_update` 來源分支、`cmd_init` 的 `_do_reinject`、Check D)訊息與比對全部目標清單化(整合 F2);剝除端 `_deinit_strip_claude` 同一清單(整合 F1)。AGENTS 檔的 absent 路徑把區塊插在第一個標題行之後;★找不到任何 `#` 標題行→插在檔案最前★(不是尾端);created 路徑的檔頭依目標名寫(現碼寫死 `"# CLAUDE.md\n\n"`,file: `scripts/lumos:10609-10610`,要參數化);注意既有機制對整檔正規化 BOM/CRLF→LF(file: `scripts/lumos:10583`),AGENTS 檔也會被同樣正規化,寫進 init 訊息。★語意衝突機器判不了★:既有 AGENTS 檔可能寫著跟紀律區塊相反的話(本 repo 的指路檔第 4 條「不要改 docs/*-knowledge」vs 鐵則一「當次寫回」就是現成例子)——init/update 對既有 AGENTS 目標檔印前 8 行叫人看一眼;本 repo 的指路檔第 4 條改成角色條件句(「被派成唯讀審計員時不改圖譜;當協作者時照 CLAUDE.md」)。doctor Check D 對每個目標各比一次;另加一行估算「git 根到本層每層生效的那一個 AGENTS 檔(有 override 只算 override)總 bytes/32768」,>75% warn。
4. **enforcement 層**:每支 Codex hook 一列(與 Claude 側 `session-entry-hook` 等同粒度,架構 #3):`codex-<Claude 側同名列>`(如 codex-session-entry-hook)狀態值域 `registered-trust-unknown|degraded|inactive|unknown`(degraded=已註冊但 hook 檔不在,沿 Claude 側 2026-07-07 事故守衛,file: `scripts/lumos:12113`;★不出 active——信任狀態本機讀不到★;`mark` 圖示字典補新鍵);`codex-skills`、`claude-skills`(對稱補,整合 F6);`agents-md`(區塊在、版本戳與 CLAUDE.md 一致、有 override 時標明寫在 override)。`shutil.which("codex")` 為 None→Codex 各層 inactive 帶「本機無 codex」。
5. **測試**:HOME+CODEX_HOME 隔離(沿用 `t_install_skills_unix`/`_sync_global_claude` 測試的 HOME 隔離寫法)驗 install→三處都在、teardown→三處都空;既有真目錄不被刪;合併器 rc 非 0 時不印成功;對照表逐條;Check D 三目標各測漂移;override 存在時寫 override。

### S1 hook 適配(一支腳本、認形狀、由 `--harness` 旗標分支,不嗅 payload)

| hook | Claude 下吃什麼 | Codex 下差在哪 | 適配 |
|---|---|---|---|
| lumos-entry-hook(SessionStart) | `cwd` | 同欄位 | `--harness` 只影響輸出裡的 enforcement 摘要 |
| ci-status-hook(SessionStart) | `cwd` | 同欄位 | 零改 |
| impact-hook(PreToolUse) | `tool_input.file_path` | apply_patch 的 `tool_input.command` 是 patch 全文,★沒有 file_path★ | `extract_paths` 回清單:command 以 `*** Begin Patch` 開頭→解 `*** Add File:`/`*** Update File:`/`*** Delete File:`/★`*** Move to:`★(邊界 F7)取全部路徑;★逐檔跑 impact 合併輸出(外家 F10);既有碼沒有「處理檔數」上限(`cap_tokens`/`cap_chars` 限的是單檔查詢字串長度),本案新定:最多處理 5 檔、其餘只列名、總時間預算 20 秒(hook 外層 30 秒),超預算就印「多檔 patch 只算前 k 檔」後 fail-open★;TTL 冷卻、shebang、fail-open 沿用 |
| dispatch-lens-hook(Claude: PreToolUse Agent + updatedInput 改派工詞) | 派工詞裡 `LUMOS-IMPACT: <range>` | ★派工訊息對 hook 是密文,讀不到也改不了(實驗 A)★;現碼 `tool_name != "Agent"` 即返回(file: `scripts/hooks/claude/dispatch-lens-hook.py:50`) | 新增 SubagentStart 分支(`--harness codex` 時走):讀 armed 檔→`additionalContext`。armed 檔由 `lumos dispatch-lens <range> --arm --seats N` 寫:路徑 `~/.cache/lumos/dispatch-lens/armed/<key>.json`,★key=`git rev-parse --show-toplevel` 的 realpath 取 sha256,寫讀兩端共用同一支 `_lens_repo_key`(邊界 F4)★,內容=range/產生時間/repo 根,席數以 N 個 token 檔表示(`<key>/<ts>-<i>.token`);hook 每次★先驗 TTL 10 分(過期→整個目錄刪掉、什麼都不回)★,再用 `os.rename` 原子認領一個 token(認領不到→什麼都不回;沒 armed 目錄→什麼都不回),同時多個 SubagentStart 不會重複扣或重複標號;`--disarm` 立即刪。★承認界線(通才 r2 F1):token 不分收件人,同 repo 同窗口的無關子代理會搶走席位,讓真正要派的審查席收不到、且無錯誤訊號——緩解=`--arm` 只在派工前一刻下、`lumos dispatch-lens --status` 印剩餘席、`--seats` 可多給緩衝;量不到就不宣稱消滅,REVISIT 併入 2026-10-04★。★鏡頭文字首行印「LUMOS-LENS range=<base>..<head> 第 k/N 席」讓錯席可見(外家 F11/F20、邊界 F3);承認界線:同 repo 同窗口內非審查用的子代理也會收到,靠 seats 計數與短 TTL 縮小,量不到就不宣稱消滅★。PreToolUse 攔 `collaborationspawn_agent` 攔得到但無用處,不掛 |
| check-graph-sync(Stop) | `transcript_path` 讀 Claude 逐字稿 tool_use 區塊 `input.command`/`input.file_path` | Codex 逐字稿型別不同且官方說非穩定介面 | reader 以第一行 `session_meta` 判 Codex 並讀 `cli_version`;★帶一份 0.144.1 的 fixture 逐字稿,型別對不上或版本未在 fixture 表→跳過本 session 判定並印一行「Codex 逐字稿格式未知,收工同步略過」(外家 F13)★;shell 參數非明文(S0 進場 4)→此層只做跳過 |

S1 驗收(隔離 HOME+CODEX_HOME 真跑 `codex exec` 帶旗標,hook 命令列包一層把 stdout/stderr 落到測試暫存檔——★不發明新帳,usage-log 不是 hook 寫的(整合 F4)★):①apply_patch 改一個有合約的檔→hook stdout 含該檔合約行 ②`dispatch-lens --arm --seats 1` 後派子代理→子代理回報含「LUMOS-LENS range=」首行 ③Stop 後 check-graph-sync 對 Codex 逐字稿印出「已判/略過」其一,不炸。

### S2 迴圈從 Codex 編排

- 五支 lumos skill 目錄下★全部 .md(SKILL.md、reference.md、templates.md、commands/*)★凡寫「Agent tool / model sonnet / `/skill`」處改成一行兩家(整合 r2 F10 已點名 code-loop/design-loop/project-notes 的 reference.md 五處):「派乾淨審查員(Claude:Agent 工具 sonnet;Codex:`spawn_agent`,派工詞點名 lumos-reviewer)」;`pitfalls-gapfill/SKILL.md` 第 27 行「用 Agent tool 派乾淨 refuter」是已知一處(整合 F5)。`$lumos-<skill>` 顯式叫法補進 INDEX——前提是 S0 進場 1 證實載入,且隱式觸發不亂咬(調研候選 7 的前提,未驗)。
- `~/.codex/agents/lumos-reviewer.toml`:`name`、`description`(何時用它)、`developer_instructions`(templates.md 審查員框架固定段)、`sandbox_mode="read-only"`;install 用字串範本寫出、teardown 收。★S2 進場實驗:派工詞點名 lumos-reviewer 後,SubagentStart 的 agent_type 是不是它、子代理內寫檔是否被沙盒擋——沒證實前 S2 不算驗收(外家 r2 #23)★。
- **外家席相對化(整合 F3/通才 F3 blocker)**:`loop next` 首輪必帶 `--orchestrator claude|codex`(比照 `--tier` 首輪必帶,持久化到帳),`canary record` 存欄、定錨後不一致才擋(零記錄時不擋——比照 `--tier` 選配慣例,首輪必帶那一刀在 `loop next`);`loop status` 讀帳、舊迴圈帳面缺欄時視為 claude 並印一句、兩筆不同即報矛盾(只補舊帳,不給新呼叫預設——預設 claude 會讓 Codex 編排漏旗標時靜默套錯家族,外家 r2 #24);`_roster_family(auditor, orchestrator)` 回「同門/外家」而不是「claude/external」;`_TIER_ROSTER` 的 `external` 改讀成「非編排者家族」。Codex 編排時外家=`claude -p`。[[Systems/canary-audit]] 與 [[Systems/design-loop]] 的「外家 blocker 不得僅被同門多數推翻」不變。
- 席名沿既有 `<鏡頭>-<模型>` 慣例(file: `docs/lumos-toolchain-knowledge/Projects/收斂閘殘餘估計降級_計劃.md:65`),不另立 `ext-<家族>`;調研候選 ⑥「9 種寫法」改為在 `loop status` 印正規化建議,不改帳。

### S3 量測(進場條件:S0 進場 4 答「明文」且 additionalContext 有落逐字稿;否則本階段只做 probe runner,recount 不做並在誠實界線記一行)

- recount 多一個 Codex reader(路徑 `~/.codex/sessions/**`,以 `cwd` 過濾 repo,fixture 版本守衛同 S1);probe 多一個 runner(`codex exec --json`,配額另量)。

## 擬裁定(a)–(d)的理由

- **(a) AGENTS 檔放同一塊、不放指路;有 override 就寫 override;插檔首**:指路要模型多做一步、沒機械保證;`project_doc_fallback_filenames` 只在該層無 AGENTS*.md 時生效。重複的漂移由 reinject+Check D 兜(三端同一清單);★32 KiB 是全鏈上限、截斷靜默,Check D 管不到截斷★——所以插檔首+doctor 估總量,只降機率不消滅,誠實界線記。代價:每專案多 6.6k。
- **(b) hooks.json 不寫 config.toml**:stdlib 只有 `tomllib`(唯讀);hooks.json 官方支援、外層同形。並存規則=S0 進場 2。★但「同形」只到外層:Codex `PreToolUse` 的 `updatedInput` 文件要求同時回 `permissionDecision:"allow"`(外家 F2,未驗;本案 Codex 側不用 updatedInput,列為 S1 實作備註)★。
- **(c) armed 檔而不是改派工詞**:實驗 A 硬事實(rewrite 即「Encrypted function output content could not be decrypted」)。備選「標記寫進 AGENTS.md 讓 fork_turns=all 的子代理繼承」不可控,不取。無先例=有意識偏離(見 PRIOR-ART 缺口)。TTL 10 分+seats 計數為暫用值,沒量。
- **(d) 外家相對化到機械層**:只改散文,`_roster_family` 仍把 Codex 席判 external,Codex 編排時同門互審會被印成「外家到齊」——★席位對帳是觀測、不進合取(`_roster_tail` 明寫 advisory 不動 rc;code-loop SKILL 也寫 high 缺外家不硬擋),所以這不是「閘失效」而是「觀測失準」★,但觀測是人判收斂的依據,失準會讓人放行同門互審,所以仍動機械層。

## 驗收(S0–S3 各自跑;總驗收=四條機械都綠+第 5 條人工必過)

1. 隔離 HOME+CODEX_HOME 下 `lumos install` 後:`~/.agents/skills/` 8 支連結在(或 repo 層備援)、`~/.codex/hooks.json` 五支註冊且檔在且命令列含 `--harness codex`、專案 AGENTS 目標檔有區塊且版本戳等於 CLAUDE.md;`lumos enforcement --json`:codex hook 五列 `registered-trust-unknown`、skills 兩層 active、agents-md active;★另跑一次真 `codex exec`(帶旗標)冒煙,五支 hook 至少各 fire 一次(外家 F17)★。
2. 同環境 `lumos teardown` 後三處全空(檔案存在性驗,不看 rc)、enforcement 各層 inactive、`doctor` 綠;預放的既有真目錄與使用者自寫的 hooks.json 項目原樣保留。
3. S1 三條在真 `codex exec` 下各跑一次,結果留 `Verification/` 一篇。
4. 測試套件全綠、`lumos anchor verify` 綠(★錨點只罩 `dispatch-lens-hook.py` 一支,其餘四支 hook 不在 `ANCHOR_FILES`,file: `scripts/lumos:11409-11416`;本案不擴錨點清單,改動由測試罩★)、`lumos pitfalls --diff` 分級照走代碼審。
5. **互動信任冒煙(人工一次)**:真機開互動 `codex` 於 lumos 專案,按 Trust,改一檔,看 hook 輸出。回頭日期見文末索引行;沒做完 S1 不算驗收。

## 誠實界線

- **hook 信任是使用者的一次手動動作**,lumos 不替按、不寫信任存放處(沒查出來在哪);enforcement 永遠只能說「已註冊」。★2026-09-05 已按★(Enzo 授權,用 pty 開互動 codex 0.153.2:畫面「Hooks need review / 5 hooks are new or changed」三選項,選「2. Trust all and continue」;重開不再問;之後 `codex exec` 不帶旗標,入口 hook 的提醒被模型原文抄回、逐字稿 6 處)——驗收第 5 條的「信任冒煙」完成;★互動模式裡 hook 本身的行為(在 TUI 對話中改檔/派子代理)仍沒驗★,REVISIT 2026-09-25 只剩這一項與 SubagentStart 領席。
- **綁版本**:matcher 別名 `Agent` 不匹配、spawn message 密文、`collaborationspawn_agent` 工具名、hook 信任閘行為,都是 0.144.1 觀測;`lumos enforcement` 印 codex 版本並跟圖譜記的驗證版本比,不同就唸一句。
- **Codex 側鏡頭的位置與收件人都比 Claude 側弱**:附在子代理開場上下文而非派工詞;同 repo 同窗口的其他子代理也可能收到;首行印 range 只讓錯席可見,不消滅。鏡頭不量成效(見 [[Projects/派工鏡頭注入_計劃]])。
- **AGENTS 鏈 32 KiB 截斷靜默**,本案只降機率(插檔首+估總量)。
- **不證明 Codex 下的 lumos 比較好用**,只證六層接上了。

## 外部佐證(2026-09-05 網搜,Enzo 問「天生限制是否確有其事」)

三條限制都有上游文件或 issue 對應,兩條要修正措辭、兩條新增待驗:
- **hook 信任閘**:官方文件寫「hook trust before it will run a registered hook——`--dangerously-bypass-hook-trust` 每次帶、或互動 `/hooks` 標一次」;issue [#24093](https://github.com/openai/codex/issues/24093)(0.131–0.133 旗標在 TUI 被忽略,PR #24317 修)、PR [#26434](https://github.com/openai/codex/pull/26434)(exec 執行緒保留旗標)。★措辭修正★:信任綁的是設定檔裡那一條命令列(zenn「Codex hooks 六坑」:trust の対象は config のエントリ),只換 hook 檔內容不用重審——lumos update 只 copy 檔、命令列不變,所以不會進「再 trust 地獄」;S0 那句「hook 檔更新後要再審」改掉。
- **派工訊息密文**:issue [#32753](https://github.com/openai/codex/issues/32753)「Multi-agent V2 regression: subagent instructions no longer observable」——PR #26210 起 spawn_agent/send_message/followup_task 的 message 加密、rollout 只存密文,PreToolUse 不覆蓋 collaboration 工具、SubagentStart 只給識別欄不給任務;★closed as not planned★=設計如此,不是 bug;另有 [#36494](https://github.com/openai/codex/issues/36494) 在要「加密參數的可驗證摘要」。d3 的退路成立。
- **自訂 agent exec 選不中**:issue [#26363](https://github.com/openai/codex/issues/26363)(0.137.0 起 spawn_agent 只剩 fork_context/message,沒有 agent_type,子代理一律 generic 並繼承父模型)★已 closed、連到 PR #26599★——本機 0.144.1 仍選不中,可能修在更新版(知識庫提到 0.148.0 已存在);另兩張 [#14579](https://github.com/openai/codex/issues/14579)、[#15250](https://github.com/openai/codex/issues/15250) 同症。REVISIT:2026-09-25 升級 codex 再試自訂 agent(選得中就把 d5 退路改回裝 TOML)。
- **★2026-09-05 直接驗(Enzo:「直接驗吧」)★**:①SessionStart additionalContext 在 0.144.1 exec 下★到得了★(哨兵 SESSIONSTART-CANARY 被原文抄回)——zenn 那條沒重現;②`approval_policy="never"` 與 `--full-auto` 下 PreToolUse ★照 fire、注入也到★(第一次問法太窄模型答「沒看到」,換成「列出所有含 CANARY 的字串」就抄出,逐字稿 5 處)——沒重現;③把最新版 0.153.2 裝進暫存目錄(不動全域):★自訂 agent 選得中★(spawn_agent 多了 `agent_type` 參數、SubagentStart agent_type=lumos_reviewer、developer_instructions 到子代理),★但 TOML 的 `sandbox_mode="read-only"` 沒擋住寫檔★(子代理在父 workspace-write 下照樣建了 note.txt)——唯讀仍要靠父代理 `--sandbox read-only`;hook 信任閘(不帶旗標 0 筆/帶 1 筆)與 spawn message 密文在 0.153.2 照舊。→ d6 翻 d5 一半:裝 TOML 給身分與指示(名字用底線 `lumos_reviewer`,模型會把連字號正規化),唯讀規則不變。
- **2026-09-05 全域 Codex 升級 0.153.2**(Enzo 裁「先升級」;npm -g),真機 `lumos install --force` 接上 Codex 三處;所有「0.144.1 實測」的結論從此只當歷史,現行以 0.153.2 為準——三條限制中前兩條(信任閘、密文)在 0.153.2 重驗不變,第三條(自訂 agent)已解、唯讀仍靠父代理沙盒。
- **新增待驗(zenn 六坑)**:①SessionStart 的 additionalContext 在 Codex 到不了模型(建議寫進 AGENTS.md)——本案 S0 只驗到 lumos-entry-hook「有 fire」,沒驗它印的提醒有沒有進模型;②`approval_policy="never"` 時走審批管線的 hook(PreToolUse/PermissionRequest)不 fire——Codex 以 `--full-auto`/never 跑時影響幅度 hook 會靜默;③payload 的工作目錄欄位位置隨情境變(cwd/workdir/巢狀)。REVISIT:2026-09-25 互動冒煙時一併驗 ①②;enforcement 對 Codex hook 的「不出 active」多了一條理由。

## 實務隱患(逐類答)

- **資料/狀態**:armed 檔是跨 process 共享狀態→`~/.cache/lumos/dispatch-lens/`(0700、驗 owner 沿用),TTL 10 分+seats 計數,過期即忽略;AGENTS 目標檔與 CLAUDE.md 重複→三端同一清單+Check D;`~/.agents/skills/` 是開放共用目錄→既有真目錄不刪。
- **時序/並行**:同 repo 多 session 同時 arm→後寫者勝;非審查子代理可能收到鏡頭、也可能搶走席位——★答案:token 原子認領解決重複扣減;TTL 先於認領解決過期誤注入;錯席與餓死靠首行 range 可見+短 TTL+派工前一刻才 arm 縮小,不宣稱消滅★(邊界 F3 指出原答「不擋任何事」不成立:錯鏡頭會誤導審查席,已改)。
- **失敗與回復**:hook 全 fail-open;hooks.json 壞→合併器 return 1,★呼叫端回三態 `merge-failed`、印「設定檔損毀」而不是探針訊息、不印成功★;Codex 未安裝→跳過並印一行;`_link_or_copy` 不對新目錄 rmtree。
- **權限/安全**:hooks.json 在使用者家目錄(同 settings.json 等級);★`--dangerously-bypass-hook-trust` 只在隔離 CODEX_HOME、hooks.json 只含 lumos 五支的測試裡用;install、日常、任何自動 loop 一律不帶(它會連使用者自己的 hook 一起免審跑,邊界 F9)★;additionalContext 沿零自由文字消毒原則。
- **相容/升級**:Codex 改版→enforcement 版本比對唸一句;逐字稿 reader 帶 fixture 版本表,認不得就跳過;兩階段撤除兩邊同套。
- **可觀測**:enforcement 每 hook 一列;harness 由 `--harness` 旗標決定,★不由 payload 欄位判(Codex 與 Claude 的 hook 輸入都有 permission_mode)★;S1 驗收用測試端包裝落檔,不新增帳。
- **已排除**:金流/對外寄送/正式環境不可逆——本案全部本機工具鏈。

## 合約候選(過閘後蓋章走 guard scaffold→bind→audit,候選≠已標)

- 「消毒原則對兩條通道一致」:Codex SubagentStart 通道輸出必須是 `dispatch-lens` 同一支函式的產物,不得另拼字串。
- 「install/teardown 對稱」:Codex 三處在 teardown 後必為空;既有非我方目錄與使用者自寫 hooks 項目必原樣保留。
- 「bypass 旗標只在隔離測試」:repo 內任何非測試碼不得出現 `--dangerously-bypass-hook-trust`。

REVISIT:2026-09-25 互動模式(TUI 對話中)改檔/派子代理看 hook 行為;信任冒煙 09-05 已做。
REVISIT:2026-10-04 若 S0/S1 已上線,查一個月內 Codex 側 enforcement/probe 有無真實使用(0 筆=沒人用 Codex 開 lumos 專案,S2/S3 降優先);同日抽看 armed token 有沒有被無關子代理搶走(通才 r2 F1 界線)。

## 實作紀錄 S0(2026-09-04,r2 過閘、四條裁定記入後同日動工)

- **合併器**(`scripts/merge-claude-settings.py`):`--target codex` → 寫 `~/.codex/hooks.json`、hook 目錄 `~/.codex/hooks/`;對照表 `_codex_entries`(Edit|Write|MultiEdit→apply_patch;PreToolUse Agent→SubagentStart 無 matcher;其餘同名);命令列尾帶 `--harness codex`;懸空剪除只認自家子目錄;壞 JSON 回 1 且訊息講「設定檔壞、修好再跑」。
- **lumos 本體**:`_GLOBAL_HOOKS` 別名、`_SKILL_MARKER`、`_HARNESS_HOME`;`_sync_global_hooks(src, harness)` 三態 ok/probe/merge-failed/absent(`_sync_global_claude` 留包裝回 bool)、`_sync_msg` 三態各印各的(Codex ok 附「開互動 codex 審一次,hook 檔更新要再審」);`_teardown_global_hooks` 兩家;`_install_skills` 多連 `~/.agents/skills`(`_link_or_copy_shared`:非我方真目錄跳過+warn;fallback 複製寫 `.lumos-managed`);`cmd_uninstall` 只清 symlink/帶標記目錄;`_agents_target`/`_reinject_targets`/`_reinject_all`,`_reinject_claude_block(..., target=)` 檔頭依目標名、AGENTS 檔插第一個標題後(無標題→檔首)、既有 AGENTS 檔首次注入印前 8 行;`_deinit_strip_claude` 兩檔;doctor Check D 目標清單化+預算估算(該層生效檔/32768,>75% warn);enforcement 加 9 列(見 [[Projects/enforcement儀表板_計劃]] KEY),`registered-trust-unknown` 不進 summary 分母,沒 `~/.codex` 的機器 Codex 列全 unknown(★偏離 spec 原文「inactive」:inactive 會讓入口 hook 對沒裝 Codex 的機器每 session 唸;偵測只看 `~/.codex` 目錄不看 PATH,結果才跟 HOME 隔離測試一致★)。
- **本 repo AGENTS.md** 第 4 條改角色條件句(r2 整合 F12);`install.sh`/`ARCHITECTURE.md` 同步字句。
- **測試**(+6,-0,改 2):`t_codex_merge_target`/`t_codex_sync_global_tristate`/`t_codex_teardown_global`/`t_codex_skills_shared_dir`/`t_codex_reinject_agents_targets`/`t_codex_enforcement_rows`;enforcement 列數 12→21、unknown 2→10 兩測改釘值。
- **驗收**:[[Verification/2026-09-04_Codex完全支援S0安裝層驗收]]——隔離 HOME+CODEX_HOME 真跑 `codex exec`(帶旗標)五支 hook 各 fire 一次;init 後 AGENTS/CLAUDE 各一區塊、agents-md active、Check D 兩檔綠;teardown 後三處全空、AGENTS 自有內容留。
- **代碼審 r1(code-codex-s0,standard:單reviewer+架構+外家 Codex,2026-09-04)**:17 條(6+4+7,含 1 blocker)全折——CODEX_HOME 環境變數(`_codex_home()` 單源,合併器命令列改絕對路徑)、使用者同名 symlink 不換、strip 掃三個候選檔、merge-failed 時 install 回 2、`--target` 值域檢查、Codex 存在判準單一化(只看家目錄)、`~/.codex` 是檔案不炸(`home-not-dir` 態)、hooks.json schema 錯不炸、junction 以 realpath 認我方、teardown 收 .bak、Codex 列名改 `codex-<Claude 同名列>`、測試永真斷言改釘值+突變。卷證 `governance/review-reports/code-codex-s0/`。
- ~~沒做(留 S1)~~ → 見下節實作紀錄 S1。

## 實作紀錄 S1(2026-09-04,S0 代碼審過閘後同日動工)

- **進場實驗**:matcher `Edit`/`Write`/`apply_patch` 三個各自都攔到同一個 apply_patch 呼叫(tool_name 仍回 apply_patch)→ 確認是別名,合併器對照表只掛 `apply_patch` 一條不會少也不會重;改名 patch 形狀 `*** Update File: a\n*** Move to: b`。
- **impact-hook**:`EDIT_TOOLS` 加 apply_patch;`extract_patch_paths`(Add/Update/Delete/Move to 四種標頭,去重保序)、`extract_paths`、`_decide_one`、`hook_decide_paths`(最多 `APPLY_PATCH_MAX_FILES=5`,其餘只列名);main 改多檔迴圈、總預算 `APPLY_PATCH_BUDGET_SEC=20`(hook 外層 30),逐檔 `_impact_for_file` 回文字、一次印合併的 additionalContext;Claude 單檔路徑逐字等價(既有 81 測全綠)。
- **dispatch-lens(lumos 端,d3)**:`--arm <range> --seats N`(算好鏡頭文字落 `~/.cache/lumos/dispatch-lens/armed/<key>/meta.json`+N 個 token 檔,key=repo realpath 的 sha256 前 32 位,目錄 0700 驗 owner)、`--claim --json`(★先驗 TTL 600 秒,過期整夾刪、不回★;`os.rename` 原子認領一個 token;認領不到不回;歸零即刪;文字首行 `LUMOS-LENS range=… 第 k/N 席`)、`--disarm`、`--status`;`lens_range` 改選配。5 個並發認領 3 席實測恰 3 ok、席次不重複。
- **dispatch-lens-hook(錨點檔,已重核可)**:payload `hook_event_name == SubagentStart` → `_claim_codex_seat`:叫 `lumos dispatch-lens --claim --repo <cwd> --json`,有文字就回 SubagentStart additionalContext;Claude 的 PreToolUse 路徑一字不動;Codex 的 PreToolUse spawn payload(tool_name 非 Agent)原樣放行。
- **check-graph-sync**:第一行 `session_meta` 即 Codex 逐字稿 → `collect_codex_turn_actions`:`cli_version` 不在 `CODEX_TRANSCRIPT_VERSIONS={"0.144.1"}` → stderr 一行「格式未知,略過」回空(不猜);從最後一個 `event_msg/user_message` 起,`custom_tool_call name=exec` 的 input(一段 JS)抽 `"cmd":"…"` 當 bash、抽任何含 `*** Begin Patch` 的 JS 字串字面值解標頭當改檔(★實看 Codex 會先 `const patch = "…"` 再呼叫,不是直接傳字串★),相對路徑接 session_meta 的 cwd(is_code_file 要「在 repo 之下」的絕對路徑)。
- **skill 文件**:templates.md §3 鏡頭 3 加第 ④ 條(Codex 編排:派前一刻 arm、派完 disarm)、code-loop SKILL 步驟 2 一句、commands/06 加一列。
- **測試** +3(`t_codex_s1_impact_apply_patch`/`t_codex_s1_lens_arm_claim`/`t_codex_s1_graph_sync_codex_transcript`)。
- **驗收**:[[Verification/2026-09-04_Codex完全支援S1hook適配驗收]]——隔離 clone+CODEX_HOME 真跑 codex exec:①apply_patch 改帶合約的檔 → hook 注入 1030 字「必看——這 9 篇帶著不能破壞的合約或出過事故」;②arm 1 席後派子代理 → 子代理原文回報 `LUMOS-LENS range=Lumos/main..HEAD 第 1/1 席`;③Stop → 用當場抓下的真 payload+逐字稿餵修正後 hook 印出「改了 1 個程式碼檔但筆記沒動」(第一次真跑沒印:安裝副本是修正前的,抓 payload 重餵才對上;變數型 patch 是那次抓到的)。
- **代碼審 r1(code-codex-s1,standard:單reviewer+架構+外家 Codex,2026-09-04)**:14 條(5+3+6,4 條兩席重疊)全折——Codex 逐字稿 shell 呼叫一半是 `{cmd:` 無引號(同日 61 份逐字稿 31:30)、輪次邊界兩型都認(`event_msg/user_message` 與 `response_item/message role=user`)、席號改用 token 編號(remaining 推算會撞號)、四個模式旗標互斥、Claude 單檔路徑 timeout 維持 30、hook 失敗分支補 _debug、`_lens_cache_path` 改 realpath 與 armed key 同法、armed 目錄補 group/other 不可寫檢查;驗證筆記改寫「只證當時那一份逐字稿的形狀」。鏡頭這輪沒附固定席:base 是未推 commit 不在主線,hook 照設計放行。卷證 `governance/review-reports/code-codex-s1/`。
- ~~沒做(留 S2/S3)~~ → S2 見下節;S3 未做。

## 實作紀錄 S2(2026-09-04,S1 代碼審過閘後同日動工)

- **進場實驗(自訂 agent)**:`CODEX_HOME/agents/` 放 `lumos-reviewer.toml`(name/description/developer_instructions/sandbox_mode=read-only),派工詞點名 → SubagentStart `agent_type=default`、子代理 apply_patch 成功寫檔;改成底線名 `lumos_reviewer`(模型 spawn 時 task_name 用的形)再試一次,同樣 default、可寫。★0.144.1 的 codex exec 下自訂 agent 選不中★(文件說靠名字選,沒說 exec 限制;互動模式沒試,REVISIT 2026-09-25)。退路實測:父代理 `--sandbox read-only` 時子代理寫檔被擋(「patch rejected: writing is blocked by read-only sandbox」)→ **d5:不裝 agent TOML,審查員框架寫進派工詞、父代理唯讀讓子代理繼承**。
- **`--orchestrator`(d4)**:`canary record --orchestrator claude|codex` 存欄(帳面定錨後中途換家 rc2);`loop next` 零記錄時必帶(不預設,訊息講「外家=不是編排者那一家」),定錨後讀帳、說另一家 rc2;輸出多 `orchestrator` 欄、`record_cmd` 帶旗標、應派席印「同門[誰]/外家(不是誰那一家)」。`_roster_family(auditor, orchestrator)` 相對化(codex 編排:codex/gpt=同門,sonnet/opus/claude/gemini/qwen=外家;字串仍回 "claude"/"external" 讓 `_TIER_ROSTER` 的 family 欄同義=同門席/外家席);`_roster_observe` 讀帳面編排者,舊帳沒欄→視為 claude 並印一句「舊帳相容」;外家席名沒模型尾碼印「建議 <鏡頭>-<模型>」提示(調研候選 ⑥,只提示不改帳)。既有 27 個測試呼叫補 `--orchestrator claude`。
- **skill 文字**:五支 skill 11 處 Agent tool/`model: sonnet` 全加 Codex 對照(spawn_agent、父代理唯讀、外家換 `claude -p`、首輪 `--orchestrator codex`);design-loop/code-loop SKILL 進場行與 commands/05 加旗標。
- **測試** +1(`t_codex_s2_orchestrator`:首輪必帶/定錨一致/相對家族/舊帳相容/席名提示),舊 roster 測試字樣更新;★首輪必帶是破壞性規則★——既有 27 個 CLI 形呼叫與入口栓測試 4 個行程內呼叫都要補 `orchestrator=claude`(第一次全套 1 紅沒看清就 commit,補 commit 修;教訓:全套結果要看 failed 數不是只看 exit code)。
- **代碼審 r1(code-codex-s2,standard:單reviewer+架構+外家 Codex,2026-09-04)**:23 條(6+7+10,4 條重疊)全折——disposal_cmd 也帶旗標、舊帳(沒欄)在 loop next 與 record 兩端都擋非 claude(不回溯改分家)、帳面兩筆不同編排者 loop next 擋/roster 報矛盾、`--orchestrator` 沒 `--loop` 擋、`loop next` 改用 `_loop_records(strict=True)`(讀帳單源)、`LOOP_ORCHESTRATORS` 命名對齊、JSON roster 加 `relative_family`/`orchestrator`、席名提示每名一次、skill 四處改「不能逐席指定模型」、reference.md 凍結段還原、SKILL 級註記指向 templates.md §3 ④ 單源、計劃 d4 文字改成實作語意。卷證 `governance/review-reports/code-codex-s2/`。
- **驗收**:[[Verification/2026-09-04_Codex完全支援S2迴圈編排驗收]]。
- ~~沒做(留 S3)~~ → 見下節。

## 實作紀錄 S3(2026-09-04,S2 代碼審過閘、8 個 commit 推上遠端後動工)

- **進場條件**:S0 進場 4 答「shell 參數明文」;本輪再驗「hook 的 additionalContext 有沒有落逐字稿」→ 有:記成 `response_item/message role=developer`(主代理稿「必看——」、子代理稿「LUMOS-LENS」),S1 驗收那四份稿 grep 到 9 處。
- **recount.py**:`scan_codex_file`——`session_meta.cwd` 篩 repo、`cli_version` fixture 守衛、developer 訊息辨識、錨=同輪最近 apply_patch 呼叫(前後都找)+目標檔、`classify_bash` 同一支判讀(含 lumos show/context 的詞對 stem)、子代理稿 LUMOS-LENS 行;`--codex-sessions` 旗標;rows 加 `harness`,summary 加 `by_harness`/`codex_lens_rows`/`codex_files`。真跑:本機 `~/.codex/sessions` 346 份稿、本 repo 0 筆 Codex 行(今天真機的 Codex session 都是唯讀審查,沒 apply_patch);隔離驗收目錄 4 筆(3 筆 apply_patch 全錨到、目標檔皆 `scripts/merge-claude-settings.py`、9 篇釘住、注入後都沒讀=0/3;1 筆子代理鏡頭)。
- **scenario_probe.py**:`--runner codex` → `run_one_codex`(`codex exec --json --sandbox workspace-write -C <沙盒>`,LUMOS_PROBE=1,★不帶 bypass 旗標★——探針測的是「會不會自己敲 lumos」不靠 hook);`tool_calls_from_codex_json` 解 `item.completed` 的 command_execution(剝 zsh -lc 單/雙引號外殼)/file_change/agent_message;結果多 `harness`,`limit_hit` 恆 False(Codex 側沒對應訊號)。真跑 `--only s03-query-status`:通過,34 秒,第一動作是讀 skill 檔、第二動作就敲 `lumos query --tag status/doing`。
- **測試** +2(`t_codex_s3_recount_codex`、`t_codex_s3_probe_codex_parser`)。
- **代碼審 r1(code-codex-s3,standard:單reviewer+架構+外家 Codex,2026-09-04)**:15 條(5+5+5,4 條重疊)全折——錨改「兩方向各取最近一個 apply_patch 比距離」、同輪無 apply_patch 不錨(不進分母)、一個 apply_patch 只當一次錨、帶路徑節點名精確比對不降裸 stem(同名不同目錄不撞)、python 前綴 basename 恰為 lumos、codex runner 超時/非零退出=儀器例外不判過、Codex 解析核心改向 check-graph-sync 借(版本表單源)、命名/空行計數/版本略過訊息對齊、run_one 加 harness 欄、README 改「developer 訊息是實測落點非唯一來源」。Claude 側更正數字在這些修正後不變(2/16、24)。卷證 `governance/review-reports/code-codex-s3/`。
- **驗收**:[[Verification/2026-09-04_Codex完全支援S3量測驗收]]。
- **沒做**:Codex 側的 probe 用量/速率上限偵測(沒對應訊號,遇到再補);子代理鏡頭「有沒有讀」(子代理稿沒有釘住清單可對,只計筆數)。

## 後續:行為精修(2026-09-05)

f01/f02 兩個功能實驗跑完後的精修另開 [[Projects/Codex行為精修_計劃]]:Codex 收工 Stop hook 在「改了碼、筆記沒動」時擋一次讓模型續做補筆記(Claude 側不變),與紀律範本一句「先跑相關子集」。

## 實作紀錄 d6(2026-09-05,直接驗後翻 d5 一半)

- `_install_codex_agent`/`_remove_codex_agent`:Codex 同步時寫 `CODEX_HOME/agents/lumos_reviewer.toml`(字串範本,帶 `# lumos-managed` 標記;name/description/developer_instructions=審查席框架;sandbox_mode 只當提示),重跑 unchanged、外方同名檔不覆蓋、teardown 只收帶標記的、無 Codex 家目錄不建;測試 `t_codex_d6_agent_toml`。skill 三處改「派工詞點名 lumos_reviewer;唯讀靠父代理沙盒」。
- 驗收:隔離 CODEX_HOME 跑 `lumos install` 寫出 TOML,用暫存的 0.153.2 派 `lumos_reviewer` → SubagentStart `agent_type=lumos_reviewer`(見 S2 驗證筆記補驗段)。0.144.1 全域版忽略此檔(無害)。
- 誠實界線補:TOML 的 sandbox_mode 實測不擋寫檔,唯讀規則不變;新版 codex 是否已修在別的版本沒逐版驗(只驗 0.144.1 與 0.153.2 兩點)。
- **代碼審 r1(code-codex-d6,standard:單reviewer+架構+外家 Codex,2026-09-05)**:15 條(3+6+6,1 條重疊)全折——agents 路徑是檔案不炸(`skipped-not-dir`)、測試 tomllib 精確比、「0.153+」全改「0.153.2 實測、0.144.1 忽略」、enforcement 加 `codex-agent` 列(每樣裝的東西都有一列)、skill 三處統一「框架單源=TOML 的 developer_instructions,派工詞給審材與鏡頭」並引 d6、三態改 created/unchanged/skipped-*、docstring/步驟註解補④⑤、第三種標記機制加註解、merge-failed 時不寫 TOML 為刻意(補註解)、測試刪 PATH 誤導行。卷證 `governance/review-reports/code-codex-d6/`。

REVISIT:2026-09-25 互動 Codex 信任冒煙時一併看 SubagentStart 領席在互動模式下是否照常(本輪只驗 exec)。

## 審計修正紀錄(lumos-design-loop)

- r1(2026-09-04,3 席+架構+外家 Codex):47 條(20+8+7+9+3)/blocking 36(19+5+3+9+0)/全折、accepted 空(blocker 輪)。外家 20 條(12 句引句錨不到,內容仍判、不入 set;F1「message 可 rewrite」實驗 A 反證不採信;F12 部分成立),整合 8(blocker=家族判定寫死),通才 7,邊界 9(blocker=hook 信任閘、`_link_or_copy` rmtree、AGENTS.override.md),架構 3 minor+1 ⚠。席報告與重現紀錄:`governance/review-reports/Codex完全支援/r1-*.md`、`r1-intake.md`。
- r2(2026-09-04,3 席+架構+外家 Codex,驗收輪):26 條(外家 6+整合 7+邊界 7+通才 5+架構 1)/blocking 14(4+3+5+2+0)/全折、accepted 空;r1 36 條 blocking 逐條驗收通過(通才席逐條對照);新洞集中在修補處:token 認領競態、TTL 優先序被重寫時掉了、`--orchestrator` 預設值 fail-open、reinject 檔頭寫死、本 repo AGENTS 指路檔與紀律區塊語意衝突、skill 掃描漏 reference/templates、多檔 impact 沒有既有 cap。卷證:`r2-*.md`、`r2-intake.md`。
