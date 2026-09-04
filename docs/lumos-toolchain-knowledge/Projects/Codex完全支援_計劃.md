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
  KEY:r1(2026-09-04,3 席+架構+外家 Codex)47 條/blocker 6(3 席各 1–3)/全折、accepted 空;外家 F1「message 可 rewrite」被實驗 A 反證不採信;★新地基事實(實驗 C/D)★:使用者層 hook 不按一次互動 TUI 的 Trust 就不跑,exec 只能靪 --dangerously-bypass-hook-trust,信任存放處沒查出來
  KEY:四個擬裁定(r1 折入後):(a)AGENTS.md(有 AGENTS.override.md 則寫它)放同一塊 sentinel 區塊、插在檔首、reinject/剝除/Check D 三端雙檔、doctor 估 chain 總量 (b)hook 註冊寫 ~/.codex/hooks.json 不寫 config.toml(stdlib 沒 TOML 寫入器,零依賴) (c)鏡頭範圍改由 `lumos dispatch-lens <range> --arm --seats N` 落 armed 檔(repo key=realpath 的 sha256,TTL 10 分,消耗 N 次即刪,鏡頭文字首行印 range);SubagentStart hook 讀它;Claude 側標記行照舊;架構席判無先例=平台逼出的有意識偏離 (d)外家席=「不是當下編排者那一家」:記帳/問閘加 --orchestrator claude|codex(預設 claude),_roster_family 相對化;席名沿既有 <鏡頭>-<模型> 慣例
  KEY:分四階段,每階段各自驗收:S0 安裝層(skills symlink→~/.agents/skills、hooks.json 合併器、AGENTS.md 區塊、enforcement 三層、teardown 對稱)→S1 hook 適配(apply_patch 取檔、SubagentStart 鏡頭、check-graph-sync 讀 Codex 逐字稿)→S2 迴圈從 Codex 編排(自訂 agent TOML、模板去 Claude 字眼、外家互換、席名統一)→S3 量測(recount/scenario_probe 多一個 runner)
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
| 2 skills | `~/.claude/skills/<全部 8 支>` symlink(`_install_skills` 用 `_skills_list()` 掃 `skills/` 下所有含 SKILL.md 的目錄——含 3 支語言慣例 skill,不只 lumos-*) | 使用者層 `~/.agents/skills/`(文件);repo 層 `.agents/skills/`(★官方只列這一個,`.codex/skills/` 不存在,r1 外家 F3★) | `_install_skills` 多一個目標;uninstall/teardown 對稱清;★新目標是開放共用目錄:遇到既有「非我方 symlink 的真目錄」一律跳過+warn,不得沿用 `_link_or_copy` 的 rmtree(邊界 F2)★;五支 lumos skill 的 Claude 專屬字眼全部處理(不只三支,整合 F5) | ✅實驗 4:repo 層 `.agents/skills/` 未信任也載入且被隱式選用;★使用者層 `~/.agents/skills/` 未測★ |
| 3 hooks | 5 支 `.py` copy 到 `~/.claude/hooks/`,`merge-claude-settings.py` 合併進 settings.json;事件=SessionStart×2/PreToolUse Edit\|Write\|MultiEdit/PreToolUse Agent/Stop | `~/.codex/hooks.json`(外層同形);matcher 名:`Bash`、`apply_patch`(`Edit`/`Write` 只是它的別名,tool_name 仍回 apply_patch);子代理=`SubagentStart`/`SubagentStop`;★hook 要在互動 TUI 按一次「Trust」才會跑,exec 下只能帶 `--dangerously-bypass-hook-trust`;沒有 CLI 能標信任,信任存放處沒查出來(實驗 C/D)★ | 合併器抽成「目標可指定+對照表」;註冊命令列帶明確 `--harness codex`(不嗅 payload 欄位);install 結尾印「開一次互動 codex 按 Trust」;enforcement 的 codex hook 層最多到「已註冊、信任狀態本機讀不到」,不單獨綠 | ✅實驗 2/4/5:帶旗標時 PreToolUse fire、apply_patch 攔得到、SubagentStart additionalContext 到子代理;❌matcher "Agent" 沒攔到 spawn(完整名 collaborationspawn_agent 攔得到,實驗 B);❌spawn message 為密文,rewrite 直接弄壞派工(實驗 A);❌不帶旗標 hook 0 筆(實驗 C/D) |
| 4 迴圈編排 | design-loop / code-loop skill 叫主對話「派 Agent、model sonnet」;外家席=Codex;★家族判定是靜態關鍵字表(`_ROSTER_EXTERNAL_KEYS`/`_ROSTER_CLAUDE_KEYS`,file: `scripts/lumos:5711-5712`),`_roster_family(auditor)` 沒有「編排者」參數★ | `spawn_agent`(介面只有 task_name/message/fork_turns,★沒有 agent 參數★;自訂 agent 靠派工詞點名或 description 匹配);自訂 `~/.codex/agents/*.toml`(必填 name/description/developer_instructions) | 模板去 Claude 專屬字眼、每處給兩家寫法;裝一支 `lumos-reviewer.toml`;★記帳/問閘加 `--orchestrator claude\|codex`(預設 claude),家族判定相對化(整合 F3 blocker)★;席名沿既有 `<鏡頭>-<模型>` 慣例(架構 #2) | ✅實驗 3/5:exec 下能派子代理;SubagentStart 帶 agent_id+agent_type、子代理 PreToolUse 帶 agent_id、SubagentStop 帶 agent_transcript_path;★自訂 TOML 未試★ |
| 5 量測 | `governance/eval/lens-utilization/recount.py` 讀 `~/.claude/projects/**.jsonl`;`scripts/scenario_probe.py` 跑 `claude -p`;★`.usage-log.jsonl` 唯一寫入者是 `lumos show/context` 的 `_usage_log`(schema `{ts,node,cmd}`),hook 不寫任何檔★ | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`(user_message 明文;spawn 的 message 密文;★官方明示逐字稿格式不是穩定介面★) | recount 多一個 reader(帶版本 fixture,認不得就跳過並記一行);probe 多一個 runner | ✅逐字稿位置與型別看過一份;★shell 呼叫參數是否明文、hook 注入有沒有落逐字稿★未查 |
| 6 安裝/拆機/體檢 | `lumos install/uninstall/teardown/enforcement/doctor`;★`_sync_global_claude` 不看合併器 returncode、無條件 return True(file: `scripts/lumos:11084-11087`)★ | 同一組指令 | install 多寫 Codex 三處並檢查合併器 rc;teardown 對稱清(含剝除端 `_deinit_strip_claude` 雙檔,file: `scripts/lumos:10653`);enforcement 多層(見 S0);doctor Check D 目標清單化 | 純自家碼,r1 抓到兩個既有吞錯點,見左欄 |

## 範圍與明確不做

- **做**:上表六層在 Codex CLI(本機 0.144.1)下接上;主驗場=隔離 HOME+CODEX_HOME 下的 `codex exec`(★只在這個隔離環境、且 hooks.json 只含 lumos 五支時才帶 `--dangerously-bypass-hook-trust`★);互動模式做一次人工信任冒煙(見驗收)。
- **不做**:①不把 Codex 當 MCP server、不用 `codex review`(調研候選 ②;候選 ① `--output-schema` 另開小案)②★不解析、不改寫既有 `~/.codex/config.toml`★(S2 的 agent TOML 是新建檔,用字串範本寫出、不需 TOML 寫入器)③不支援 Codex 專案層 `.codex/hooks.json`(未信任不載入,文件明寫)④不做 Windows 的 Codex 路徑(只保證不炸)⑤不替使用者按信任、不寫信任存放處(那是 Codex 的安全控制)。

## S0 進場條件(r1 折入:未解四題先答,答不出不開工)

1. `~/.agents/skills/` 使用者層 Codex 會不會載入(隔離 HOME 跑一次列 skills)。不載入→備援=`lumos init` 在 repo 層放 `.agents/skills/` symlink(已證載入),兩條都寫進 install。
2. `config.toml [hooks]` 與 `hooks.json` 並存時的規則(合併/覆蓋)。
3. 分開驗 matcher `spawn_agent` 與 `collaborationspawn_agent` 哪個命中(實驗 B 兩條並列只記到一筆,未分開)。
4. Codex 逐字稿裡 shell 參數是否明文(決定 check-graph-sync 的 Codex reader 可不可做;不可做→該層只做「認不得就跳過」)。

## 分階段(每階段各自過驗收才進下一階段)

### S0 安裝層(純自家碼;預估 ≲300 行含測試)

1. **skills**:`_install_skills` 目標從單一 `~/.claude/skills` 變成清單 `(~/.claude/skills, ~/.agents/skills)`;★對新目標:dst 若是既有真目錄(非 symlink/junction、非我方複製物)→跳過+印一行 warn,不刪★(`_link_or_copy` 的 rmtree 只保留給 `~/.claude/skills` 既有行為);`cmd_uninstall`/`_teardown_*` 對稱清兩處,且只清 symlink。明列會被連過去的是全部 8 支(5 支 lumos-*+3 支語言慣例),3 支語言慣例無 Claude 專屬工具引用、照連。
2. **hooks 註冊**:`merge-claude-settings.py` 抽出「目標檔+對照表」參數。Codex 對照表:`Edit|Write|MultiEdit`→`apply_patch`;PreToolUse `Agent`→改掛 `SubagentStart`(無 matcher);`Stop`→`Stop`;SessionStart→SessionStart。註冊命令列一律 `python3 ~/.codex/hooks/<hook>.py --harness codex`(Claude 側維持無旗標=claude)。hook 檔 copy 到 `~/.codex/hooks/`。★`_sync_global_*` 檢查合併器 returncode:非 0→印 warn+return False,呼叫端不印成功(邊界 F5)★。懸空剪除、兩階段撤除(STUB→DELETE)兩邊同規則;常數改名 `_GLOBAL_HOOKS`(保留 `_GLOBAL_CLAUDE_HOOKS` 別名給測試,架構 #1)。install 結尾印:「Codex 的 hook 要你開一次互動 `codex`,在 Hooks need review 畫面按 Trust all;exec 不會問」。
3. **AGENTS.md 區塊**:`_reinject_claude_block(root, slug, targets)`——目標清單=`[CLAUDE.md, AGENTS.override.md 若存在否則 AGENTS.md]`;四個呼叫點(`_vendor_toolchain`、`cmd_update` 來源分支、`cmd_init` 的 `_do_reinject`、Check D)訊息與比對全部目標清單化(整合 F2);剝除端 `_deinit_strip_claude` 同一清單(整合 F1)。AGENTS 檔的 absent 路徑把區塊插在第一個標題行之後(不是尾端);注意既有機制對整檔正規化 BOM/CRLF→LF(file: `scripts/lumos:10583`),AGENTS.md 也會被同樣正規化,寫進 init 訊息。doctor Check D 對每個目標各比一次;另加一行估算「git 根到本層各 AGENTS*.md 總 bytes/32768」,>75% warn。
4. **enforcement 層**:每支 Codex hook 一列(與 Claude 側 `session-entry-hook` 等同粒度,架構 #3):`codex-hook:<名>` 狀態值域 `registered-trust-unknown|inactive|unknown`(★不出 active——信任狀態本機讀不到★);`codex-skills`、`claude-skills`(對稱補,整合 F6);`agents-md`(區塊在、版本戳與 CLAUDE.md 一致、有 override 時標明寫在 override)。`shutil.which("codex")` 為 None→Codex 各層 inactive 帶「本機無 codex」。
5. **測試**:HOME+CODEX_HOME 隔離(沿用 `t_install_skills_unix`/`_sync_global_claude` 測試的 HOME 隔離寫法)驗 install→三處都在、teardown→三處都空;既有真目錄不被刪;合併器 rc 非 0 時不印成功;對照表逐條;Check D 三目標各測漂移;override 存在時寫 override。

### S1 hook 適配(一支腳本、認形狀、由 `--harness` 旗標分支,不嗅 payload)

| hook | Claude 下吃什麼 | Codex 下差在哪 | 適配 |
|---|---|---|---|
| lumos-entry-hook(SessionStart) | `cwd` | 同欄位 | `--harness` 只影響輸出裡的 enforcement 摘要 |
| ci-status-hook(SessionStart) | `cwd` | 同欄位 | 零改 |
| impact-hook(PreToolUse) | `tool_input.file_path` | apply_patch 的 `tool_input.command` 是 patch 全文,★沒有 file_path★ | `extract_paths` 回清單:command 以 `*** Begin Patch` 開頭→解 `*** Add File:`/`*** Update File:`/`*** Delete File:`/★`*** Move to:`★(邊界 F7)取全部路徑;★逐檔跑 impact 合併輸出(外家 F10),上限沿 cap★;TTL 冷卻、shebang、fail-open 沿用 |
| dispatch-lens-hook(Claude: PreToolUse Agent + updatedInput 改派工詞) | 派工詞裡 `LUMOS-IMPACT: <range>` | ★派工訊息對 hook 是密文,讀不到也改不了(實驗 A)★;現碼 `tool_name != "Agent"` 即返回(file: `scripts/hooks/claude/dispatch-lens-hook.py:50`) | 新增 SubagentStart 分支(`--harness codex` 時走):讀 armed 檔→`additionalContext`。armed 檔由 `lumos dispatch-lens <range> --arm --seats N` 寫:路徑 `~/.cache/lumos/dispatch-lens/armed/<key>.json`,★key=`git rev-parse --show-toplevel` 的 realpath 取 sha256,寫讀兩端共用同一支 `_lens_repo_key`(邊界 F4)★,內容=range/產生時間/repo 根/剩餘席數;TTL 10 分;每次注入 seats−1,歸零即刪;`--disarm` 立即刪。★鏡頭文字首行印「LUMOS-LENS range=<base>..<head> 第 k/N 席」讓錯席可見(外家 F11/F20、邊界 F3);承認界線:同 repo 同窗口內非審查用的子代理也會收到,靠 seats 計數與短 TTL 縮小,量不到就不宣稱消滅★。PreToolUse 攔 `collaborationspawn_agent` 攔得到但無用處,不掛 |
| check-graph-sync(Stop) | `transcript_path` 讀 Claude 逐字稿 tool_use 區塊 `input.command`/`input.file_path` | Codex 逐字稿型別不同且官方說非穩定介面 | reader 以第一行 `session_meta` 判 Codex 並讀 `cli_version`;★帶一份 0.144.1 的 fixture 逐字稿,型別對不上或版本未在 fixture 表→跳過本 session 判定並印一行「Codex 逐字稿格式未知,收工同步略過」(外家 F13)★;shell 參數非明文(S0 進場 4)→此層只做跳過 |

S1 驗收(隔離 HOME+CODEX_HOME 真跑 `codex exec` 帶旗標,hook 命令列包一層把 stdout/stderr 落到測試暫存檔——★不發明新帳,usage-log 不是 hook 寫的(整合 F4)★):①apply_patch 改一個有合約的檔→hook stdout 含該檔合約行 ②`dispatch-lens --arm --seats 1` 後派子代理→子代理回報含「LUMOS-LENS range=」首行 ③Stop 後 check-graph-sync 對 Codex 逐字稿印出「已判/略過」其一,不炸。

### S2 迴圈從 Codex 編排

- 五支 lumos skill(design-loop、code-loop、project-notes、★core-knowledge、pitfalls-gapfill★)凡寫「Agent tool / model sonnet / `/skill`」處改成一行兩家:「派乾淨審查員(Claude:Agent 工具 sonnet;Codex:`spawn_agent`,派工詞點名 lumos-reviewer)」;`pitfalls-gapfill/SKILL.md` 第 27 行「用 Agent tool 派乾淨 refuter」是已知一處(整合 F5)。`$lumos-<skill>` 顯式叫法補進 INDEX。
- `~/.codex/agents/lumos-reviewer.toml`:`name`、`description`(何時用它)、`developer_instructions`(templates.md 審查員框架固定段)、`sandbox_mode="read-only"`;install 用字串範本寫出、teardown 收。
- **外家席相對化(整合 F3/通才 F3 blocker)**:`canary record`/`loop next`/`loop status` 加 `--orchestrator claude|codex`(預設 claude,舊帳不變);`_roster_family(auditor, orchestrator)` 回「同門/外家」而不是「claude/external」;`_TIER_ROSTER` 的 `external` 改讀成「非編排者家族」。Codex 編排時外家=`claude -p`。[[Systems/canary-audit]] 與 [[Systems/design-loop]] 的「外家 blocker 不得僅被同門多數推翻」不變。
- 席名沿既有 `<鏡頭>-<模型>` 慣例(file: `docs/lumos-toolchain-knowledge/Projects/收斂閘殘餘估計降級_計劃.md:65`),不另立 `ext-<家族>`;調研候選 ⑥「9 種寫法」改為在 `loop status` 印正規化建議,不改帳。

### S3 量測(進場條件:S1 進場 4 答「明文」且 additionalContext 有落逐字稿;否則本階段只做 probe runner,recount 不做並在誠實界線記一行)

- recount 多一個 Codex reader(路徑 `~/.codex/sessions/**`,以 `cwd` 過濾 repo,fixture 版本守衛同 S1);probe 多一個 runner(`codex exec --json`,配額另量)。

## 擬裁定(a)–(d)的理由

- **(a) AGENTS 檔放同一塊、不放指路;有 override 就寫 override;插檔首**:指路要模型多做一步、沒機械保證;`project_doc_fallback_filenames` 只在該層無 AGENTS*.md 時生效。重複的漂移由 reinject+Check D 兜(三端同一清單);★32 KiB 是全鏈上限、截斷靜默,Check D 管不到截斷★——所以插檔首+doctor 估總量,只降機率不消滅,誠實界線記。代價:每專案多 6.6k。
- **(b) hooks.json 不寫 config.toml**:stdlib 只有 `tomllib`(唯讀);hooks.json 官方支援、外層同形。並存規則=S0 進場 2。★但「同形」只到外層:Codex `PreToolUse` 的 `updatedInput` 文件要求同時回 `permissionDecision:"allow"`(外家 F2,未驗;本案 Codex 側不用 updatedInput,列為 S1 實作備註)★。
- **(c) armed 檔而不是改派工詞**:實驗 A 硬事實(rewrite 即「Encrypted function output content could not be decrypted」)。備選「標記寫進 AGENTS.md 讓 fork_turns=all 的子代理繼承」不可控,不取。無先例=有意識偏離(見 PRIOR-ART 缺口)。TTL 10 分+seats 計數為暫用值,沒量。
- **(d) 外家相對化到機械層**:只改散文,`_roster_family` 仍把 Codex 席判 external,Codex 編排時同門互審會被判「外家到齊」而放行——這是 code-high `required-fail-closed` 閘失效,必須動機械層。

## 驗收(全機械;S0–S3 各自跑;總驗收=四條都綠)

1. 隔離 HOME+CODEX_HOME 下 `lumos install` 後:`~/.agents/skills/` 8 支連結在(或 repo 層備援)、`~/.codex/hooks.json` 五支註冊且檔在且命令列含 `--harness codex`、專案 AGENTS 目標檔有區塊且版本戳等於 CLAUDE.md;`lumos enforcement --json`:codex hook 五列 `registered-trust-unknown`、skills 兩層 active、agents-md active;★另跑一次真 `codex exec`(帶旗標)冒煙,五支 hook 至少各 fire 一次(外家 F17)★。
2. 同環境 `lumos teardown` 後三處全空(檔案存在性驗,不看 rc)、enforcement 各層 inactive、`doctor` 綠;預放的既有真目錄與使用者自寫的 hooks.json 項目原樣保留。
3. S1 三條在真 `codex exec` 下各跑一次,結果留 `Verification/` 一篇。
4. 測試套件全綠、`lumos anchor verify` 綠(★錨點只罩 `dispatch-lens-hook.py` 一支,其餘四支 hook 不在 `ANCHOR_FILES`,file: `scripts/lumos:11409-11416`;本案不擴錨點清單,改動由測試罩★)、`lumos pitfalls --diff` 分級照走代碼審。
5. **互動信任冒煙(人工一次)**:真機開互動 `codex` 於 lumos 專案,按 Trust,改一檔,看 hook 輸出。REVISIT:2026-09-25 做這條;沒做完 S1 不算驗收。

## 誠實界線

- **hook 信任是使用者的一次手動動作**,lumos 不替按、不寫信任存放處(沒查出來在哪);enforcement 永遠只能說「已註冊」。
- **綁版本**:matcher 別名 `Agent` 不匹配、spawn message 密文、`collaborationspawn_agent` 工具名、hook 信任閘行為,都是 0.144.1 觀測;`lumos enforcement` 印 codex 版本並跟圖譜記的驗證版本比,不同就唸一句。
- **Codex 側鏡頭的位置與收件人都比 Claude 側弱**:附在子代理開場上下文而非派工詞;同 repo 同窗口的其他子代理也可能收到;首行印 range 只讓錯席可見,不消滅。鏡頭不量成效(見 [[Projects/派工鏡頭注入_計劃]])。
- **AGENTS 鏈 32 KiB 截斷靜默**,本案只降機率(插檔首+估總量)。
- **不證明 Codex 下的 lumos 比較好用**,只證六層接上了。

## 實務隱患(逐類答)

- **資料/狀態**:armed 檔是跨 process 共享狀態→`~/.cache/lumos/dispatch-lens/`(0700、驗 owner 沿用),TTL 10 分+seats 計數,過期即忽略;AGENTS 目標檔與 CLAUDE.md 重複→三端同一清單+Check D;`~/.agents/skills/` 是開放共用目錄→既有真目錄不刪。
- **時序/並行**:同 repo 多 session 同時 arm→後寫者勝,且非審查子代理也可能收到鏡頭——★答案:靠首行 range 可見+seats 歸零即刪+短 TTL 縮小,不宣稱消滅★(邊界 F3 指出原答「不擋任何事」不成立:錯鏡頭會誤導審查席,已改)。
- **失敗與回復**:hook 全 fail-open;hooks.json 壞→合併器 return 1,★呼叫端檢查 rc、不印成功★;Codex 未安裝→跳過並印一行;`_link_or_copy` 不對新目錄 rmtree。
- **權限/安全**:hooks.json 在使用者家目錄(同 settings.json 等級);★`--dangerously-bypass-hook-trust` 只在隔離 CODEX_HOME、hooks.json 只含 lumos 五支的測試裡用;install、日常、任何自動 loop 一律不帶(它會連使用者自己的 hook 一起免審跑,邊界 F9)★;additionalContext 沿零自由文字消毒原則。
- **相容/升級**:Codex 改版→enforcement 版本比對唸一句;逐字稿 reader 帶 fixture 版本表,認不得就跳過;兩階段撤除兩邊同套。
- **可觀測**:enforcement 每 hook 一列;harness 由 `--harness` 旗標決定,★不由 payload 欄位判(Codex 與 Claude 的 hook 輸入都有 permission_mode)★;S1 驗收用測試端包裝落檔,不新增帳。
- **已排除**:金流/對外寄送/正式環境不可逆——本案全部本機工具鏈。

## 合約候選(過閘後蓋章走 guard scaffold→bind→audit,候選≠已標)

- 「消毒原則對兩條通道一致」:Codex SubagentStart 通道輸出必須是 `dispatch-lens` 同一支函式的產物,不得另拼字串。
- 「install/teardown 對稱」:Codex 三處在 teardown 後必為空;既有非我方目錄與使用者自寫 hooks 項目必原樣保留。
- 「bypass 旗標只在隔離測試」:repo 內任何非測試碼不得出現 `--dangerously-bypass-hook-trust`。

REVISIT:2026-09-25 互動模式 Codex 信任冒煙(驗收第 5 條)。
REVISIT:2026-10-04 若 S0/S1 已上線,查一個月內 Codex 側 enforcement/probe 有無真實使用;0 筆=沒人用 Codex 開 lumos 專案,S2/S3 降優先。

## 審計修正紀錄(lumos-design-loop)

- r1(2026-09-04,3 席+架構+外家 Codex):47 條(20+8+7+9+3)/blocking 36(19+5+3+9+0)/全折、accepted 空(blocker 輪)。外家 20 條(12 句引句錨不到,內容仍判、不入 set;F1「message 可 rewrite」實驗 A 反證不採信;F12 部分成立),整合 8(blocker=家族判定寫死),通才 7,邊界 9(blocker=hook 信任閘、`_link_or_copy` rmtree、AGENTS.override.md),架構 3 minor+1 ⚠。席報告與重現紀錄:`governance/review-reports/Codex完全支援/r1-*.md`、`r1-intake.md`。
