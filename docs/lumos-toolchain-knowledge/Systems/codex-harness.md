---
type: system
status: done
created: 2026-09-05
updated: 2026-09-05
responsibility: 負責 lumos 的防護怎麼接到 Claude 與 Codex 兩家 CLI 上:進場提醒、改檔前推波及、派審查員附鏡頭、收工點名這四個時點的 hook 腳本,以及情境探針這支量「AI 有沒有自己去查脈絡」的儀器;不負責這些 hook 推出來的內容對不對(那是各機制自己的節點),也不負責 lumos 本體的讀寫語意
aliases: []
about_code:
  - scripts/hooks/claude/check-graph-sync.py
  - scripts/hooks/claude/dispatch-lens-hook.py
  - scripts/hooks/claude/impact-hook.py
  - scripts/merge-claude-settings.py
  - scripts/scenario_probe.py
  - scripts/lumos
  - scripts/hooks/claude/lumos-entry-hook.py
tags:
  - type/system
  - status/done
  - scope/platform
summary: |-
  KEY:[2026-09-25 prompt 稽核]進場 hook 開場白改成跟紀律範本一致:改檔前筆記會自動推、想自己查才敲 impact(拿掉「至少一行、被催也一樣」的舊補丁);對不上怎麼裁指回紀律區塊第 3 條,不再一刀切「以程式碼為準」。派工鏡頭超時說明是附在審查席派工詞上的,改成只叫它照派工詞審、★不附可照跑的補算指令★(審查席會照跑)。框外指示的規矩見 [[Systems/hook信任邊界]] [test:t_dispatch_lens_hook_timeout_notice_and_spec_marker]
  FLOW:lumos install →(Claude)~/.claude/hooks+settings.json+CLAUDE.md 區塊 /(Codex)~/.codex/hooks+hooks.json(--target codex,matcher 對照:Edit|Write→apply_patch、Agent→SubagentStart)+~/.agents/skills+AGENTS.md 同塊區塊+CODEX_HOME/agents/lumos_reviewer.toml → 使用者開一次互動 codex 按 Trust all → 之後 exec/互動兩模式 hook 都跑
  KEY:同一批 hook 腳本兩家共用,差異全在 --harness codex 旗標與註冊表:SessionStart 入口提醒(additionalContext)、PreToolUse impact-hook 取 apply_patch 的檔、SubagentStart dispatch-lens 領席(armed token)、Stop check-graph-sync 讀 Codex 逐字稿(版本表 0.144.1/0.153.2,不在表略過不猜)
  KEY:★收工擋一次(2026-09-05,[[Projects/Codex行為精修_計劃]];同日套到 Claude,[[Projects/README審視五修_計劃]] d2)★:改了程式碼、筆記沒動 → 兩家都回 decision:block 一次讓模型續做補筆記或一句話說明——名額先佔(~/.cache/lumos/stop-block/<session_id> O_EXCL 建成才擋;目錄整條路徑不得經 symlink、owner 自己、0700)+stop_hook_active 雙護欄,LUMOS_STOP_BLOCK_OFF=1 關;reason ≤1500 字、≤10 檔、檔名消毒包反引號並標明只是檔名。f02 後測 3/3 擋到、模型皆回一句說明;天花板=逼表態不是逼寫對
  KEY:★審查席三席,點哪一席看你在審什麼(2026-09-08 Enzo 裁;★2026-09-11 Enzo 裁三席模型一律降到 gpt-5.6-sol,推理強度照舊——額度常撞上限,決策見 decisions★))★ — 散文審(設計審/文件)`lumos_reviewer`=sol+medium(預設)/ 程式碼審(一般)`lumos_reviewer_code`=sol+xhigh / 程式碼審(tier=high)`lumos_reviewer_max`=sol+xhigh。三席 developer_instructions 完全相同(框架單源),差別只在模型與推理強度。★散文審只給 medium 的理由=實測 xhigh 審 8k 字元 README 語感慢到使用者喊停;推理強度要配題目,它的成本是牆鐘時間,審查慢到讓人不想派就等於沒有這道防線★。★推翻舊宣稱「Codex 不能逐席指定模型」★——TOML 的 model / model_reasoning_effort 實測有效(反證法:指定帳號會 400 的模型→席位啟動失敗)。astra 只給高風險的理由=Plus 額度緊,全用會一輪吃光→退回沒有外家席。單源 [[Verification/2026-09-08_Codex席位可指定模型_兩席分流]]
  KEY:★三席之外還有一刀,而且可能比推理強度更重要(2026-09-08,另一 session 實測回饋)★ — 外家席跑在唯讀沙盒裡,★建不了暫存檔=造不出現場=跑不了實驗★,所以它的報告會全部標「讀碼推論,未實跑」。實例:某輪六條裡兩條 blocker 實測全中,但一條 major 它高估了——它說無上限掃描會把看門狗耗死,實際把檔案養到 68MB 跑起來只要 0.9 秒,而那個檔每天只長 1KB。★處置:席位跑不動實驗時,它的 severity 要當成「待查證」不是「已成立」,查證成本落在編排者身上★。推論:給 code 席一個可寫的沙箱,效益可能比再調高一階推理強度更大(未做,列為候選)
  KEY:★Codex 當編排者★:loop next 首輪必帶 --orchestrator codex(家族相對化:外家=非編排者那家);派工訊息對 hook 是密文(multi-agent v2 設計,改不了),鏡頭改走 dispatch-lens --arm <range> --seats N → 子代理 SubagentStart 原子領席(TTL 10 分,首行「LUMOS-LENS range=… 第 k/N 席」)→ --disarm;審查席點名 lumos_reviewer(0.153.2 選得中、0.144.1 忽略;唯讀靠父代理 --sandbox read-only,TOML sandbox_mode 不擋)
  KEY:★天生限制(工具補不了,誠實界線)★:①hook 要人按一次信任(綁 hooks.json 命令列,換檔內容不用重按;enforcement 對 Codex hook 只能報「已註冊」)②派工訊息密文③stderr 對 Codex 模型零訊號(只有 additionalContext/decision 兩通道)④codex exec 沒有 --max-turns,擋一次就是上限⑤同 repo 同窗口的無關子代理會搶 armed 席
  KEY:★順帶修的老洞(2026-09-05)★:is_code_file 只認副檔名,本 repo 主程式 scripts/lumos 無副檔名 → Stop 提醒 2026-05 上線起對它從沒生效(兩家皆然);現在 repo 內、無副檔名、一般檔、首行是 #!也算程式碼(先判位置再開檔,FIFO 不開)
  PITFALL:[2026-09-21]★拿 git worktree 當探針來源,三道隔離會全部寫進本體★——worktree 的 `.git` 是一行指回本體的檔,rsync 原樣複製後,沙盒裡的拔遠端與設 hooks 路徑都落在真 repo 上,防護層靜默失效(推不上去才會發現)。已加前提檢查:來源的 `.git` 是檔就停手。單源 [[Issues/探針以工作樹為來源會改到本體]] [test:t_probe_sandbox_refuses_worktree_source]
  RULE:[since:2026-09-21][confirmed:2026-09-21][retire:連續兩季零腐爛,或誤報多過真報]跑探針之前先驗每題的目標還在不在,不在就整輪停手回 rc3(跟行為不及格分開),要照跑得明寫 `--allow-stale-targets`。兩層:題目裡提到的路徑要存在、`target` 欄位宣告的字串要找得到。★比對前先剝整行註解★:本 repo 移除東西時的慣例是留一句提到舊名字的註解,不剝的話那句註解會被當成「東西還在」——防線對原始事故本身失效(2026-09-21 審查席 blocker)。路徑判準是「每一段都要含字母」,所以版本對照 `0.144.1/0.153.2` 不會被誤當路徑,而沒有副檔名的推送前那支掛鉤([[Systems/bound-tests-gate]] 管的那支)與圖譜節點名抓得到。誠實界線:只擋得住整行註解,名字留在字串字面值或檔名裡仍會判成健在。驗一條 target 的邏輯拆在 `_check_one_target`,不是為了好看——合在一起會超過本專案的複雜度上限、被新增告警閘擋。[test:t_probe_detects_rotten_targets]
  PITFALL:[2026-09-21]★探針題目會跟著程式碼腐爛,腐爛之後量到的東西跟題目想量的無關,而且看起來像規矩失效★——d01 叫 AI 改提交前那道閘([[Systems/每支檔有家]] 管的那支)裡的 sync_nudge,那段 2026-09-11 就移除了;AI 查了波及、讀了碼、發現前提不成立就停下來問,這是正確行為,卻因為「沒寫回圖譜」被判不及格。新舊定位各跑三次都 0/3,一度被誤判成定位改壞了寫回紀律。挑題目的條件:①目標現在真的存在 ②改了會影響行為 ③它的家有筆記在講它。重現:`python3 scripts/scenario_probe.py --scenarios governance/scenarios/discipline.jsonl --only d01-writeback-after-code --runs 3 --timeout 700`
  PITFALL:[2026-09-29]★探針把「撞回合上限/逾時」記成 AI 沒照規矩★——9 月週抽四個失敗裡三個其實是被砍在半路(結果事件 subtype=error_max_turns),過去三次都靠加步數事後解。現在 claude 執行器跟 Codex 執行器一樣標成截斷、理由以「儀器例外」開頭、不算分;總結分母只算有效場次,有效不到一半時分母退回整批(自主迴圈靠總結行 p≠n 發通知,不退回會 0/0 安靜全過)。單源 [[Projects/探針判準對齊程式碼為主_計劃]] [test:t_probe_truncated_run_not_scored] [test:t_probe_flags_truncation_heavy_batches]
  WHY:[2026-09-29 [[Projects/探針判準對齊程式碼為主_計劃]]]★題庫拿掉讀碼類禁令★(Grep/Read/grep/cat/ls/find/git log 等不再「先做就不及格」),寫入與替代類禁令保留(Edit/Write/sed/mv/gh run/git push);唯一的純程式碼題 v04 改成期望「有讀程式碼」、lumos 可敲可不敲。理由:2026-09-21 起紀律第一步是先讀程式碼,舊判準會把符合新定位的行為量成退步。判準版本寫進週抽歷史(`GRADER_VERSION`),09-29 前後的通過率不可直接比 [test:t_probe_scenarios_allow_code_first] [test:t_probe_code_question_regrade]
  FACT:[2026-09-21 以程式碼為準]SessionStart 進場提醒(`scripts/hooks/claude/lumos-entry-hook.py`)的開場句跟著紀律範本改定位改寫了:從「第一個工具呼叫是 lumos,不是 grep」改成「程式碼是現況的依據,圖譜補程式碼看不出的脈絡」。這句話同時硬編在八個入口檔,漏改任一處就會有兩套互斥的第一步,由 `scripts/test_lumos.py` 的 `t_entry_points_agree_with_code_first` 擋。★另有兩支既有測試把訊息文字寫死在斷言裡★(`t_entry_hook_index_and_lag`、`t_entry_hook_enforcement_failopen`):它們釘的是「核心提醒有沒有被吃掉」,所以改訊息時要一起改斷言裡那個指令名,現在釘的是 `lumos impact`。2026-09-21 就是漏跑這兩支、被推送前的全套閘擋下來才發現的。現值查:`grep -n 'msg = ' scripts/hooks/claude/lumos-entry-hook.py`
  FACT:[2026-09-21 以程式碼為準]情境探針消融組要拔掉的那一節,邊界常數跟著紀律範本改定位一起改名了(原本抓「第一個工具呼叫是 lumos」那一節,現在抓「怎麼用」到「寫筆記時」之間);拔錯範圍會讓「不帶查詢指引」那組的前提失效,所以 `scripts/scenario_probe.py` 拔不到邊界時直接停手、不跑。現值查:`grep -n 'RULE_HEAD\|RULE_END' scripts/scenario_probe.py`
  DEP:scripts/lumos(_codex_home/_sync_global_hooks/_install_codex_agent/dispatch-lens/loop next --orchestrator/enforcement Codex 列)/merge-claude-settings.py --target codex/scripts/hooks/claude/{check-graph-sync,impact-hook,dispatch-lens-hook,lumos-entry-hook}.py/scenario_probe.py --runner codex --stop-block/recount.py 讀 Codex 稿
  TEST:t_codex_stop_block_once(23 斷言)/t_codex_s1_graph_sync_codex_transcript/t_codex_s1_r1_fixes/t_codex_s1_lens_arm_claim/t_codex_s3_probe_codex_parser/t_codex_d6_agent_toml/t_codex_sync_global_tristate(python3 scripts/test_lumos.py -k codex 共 164 案例綠)
  WHY:[2026-09-29 [[Projects/代碼審前後端角色鏡頭_計劃]]]派工鏡頭掛鉤認 `LUMOS-ROLE-CARDS: on` 就多傳 --role-cards;lumos 超時或回非零碼(沒有圖譜、base 不在主線)時,回傳裡若有 role_text 照附(角色不需要圖譜,消費專案還沒建圖譜時才拿得到卡)。掛鉤是複製進使用者目錄的,舊掛鉤只在成功路徑附得到,要重跑安裝;預算:lumos 先算角色、再算圖譜,角色從掛鉤給的同一份期限裡先扣,最多 3 秒且不超過期限五分之一,最多讀 300 支檔內容(一次批次讀取),掛鉤外層上限不變
  WHY:[2026-09-29 [[Projects/最低Python版本改3.14_計劃]]]Claude/Codex 掛鉤註冊寫進設定的直譯器改成跑註冊那支程式的 sys.executable(POSIX 加 shell 引號);原本 which("python3") 常是系統內建 3.9。merge-claude-settings.py 被舊版叫起時問同目錄的 lumos python-path、改用 3.14 重跑,舊版的更新程式叫新版的它時註冊照樣寫成 3.14 [test:t_hook_cmd_uses_running_python]
verified_by:
  - "[[Verification/2026-09-08_Codex席位可指定模型_兩席分流]]"
  - "[[Verification/2026-10-03_修復穩定性試行第1案]]"
  - "[[Verification/2026-10-03_修復穩定性試行第1案續辦]]"
  - "[[Verification/2026-10-04_修復穩定性試行第1案例外續修]]"
  - "[[Verification/2026-10-04_探針隔離與清理收斂]]"
decisions:
  - content: 外家審查席三席(lumos_reviewer / _code / _max)模型一律降到 gpt-5.6-sol,推理強度照舊(散文審 medium、程式碼審 xhigh);Claude 編排直接叫 codex exec 時也帶 -m gpt-5.6-sol
    id: d1
    context: 外家席額度常撞上限:2026-09-11 代碼審第二輪 Codex 席跑到一半「You've hit your usage limit」,換 Sol 也被擋到額度重置(額度整個帳號共用);舊分配是散文/程式碼 terra、高風險 astra
    why_chosen: 降一級模型讓同一段額度撐更多席;三個席名保留,派工詞與範本不用改,之後要拉開只改 _CODEX_SEAT_MODEL
    decided: 2026-09-11
    valid: true
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
| 審查席身分 | 派工詞自帶框架 | ★三席★ `CODEX_HOME/agents/` 下 `lumos_reviewer`(sol+medium,散文審,預設)、`lumos_reviewer_code`(sol+xhigh,程式碼審)、`lumos_reviewer_max`(sol+xhigh,tier=high);三席 `developer_instructions` 相同=框架單源,差別只在模型與推理強度。2026-09-08 實測 TOML 的 `model` / `model_reasoning_effort` 欄位有效 |
| 逐字稿 | `~/.claude/projects/**/*.jsonl` | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`(首行 session_meta 帶 cli_version) |

**只對 Claude 有意義的 hook 也照樣兩家都註冊**(2026-09-14,記憶過期清掃):註冊表兩家共用一份、不另開例外,Codex 那邊命令列帶 `--harness codex`,hook 進場讀到就安靜退出(記憶是 Claude Code 自己的機制)。所以 Codex 的 `hooks.json` 從五支變六支;代價是 Codex 每次開場多一個進場就結束的 Python 行程。現況與設計見 [[Systems/記憶過期清掃]]。

## 收工擋一次為什麼兩家一致

先做 Codex 的理由:Codex 側 stderr 對模型完全看不見,唯一能把「你漏了」送到模型面前的通道就是 `decision:block`(它會把 reason 當下一個提示續做)。同日 README 審視發現 Claude 側也一樣——Claude Code 官方文件明講 exit 0 的 stderr 只進除錯日誌,所謂「軟提醒」從沒有人看到過。2026-07-06 撤的是每回合刷屏的 nag;這裡同 session 只擋一次、只在改了碼沒寫回時,不是重開 nag,所以套成兩家一致([[Projects/README審視五修_計劃]] d2);實驗設計與三輪代碼審抓到的坑(名額白燒、symlink、反引號跳出 code span)都在 [[Projects/Codex行為精修_計劃]]。

## 單源與卷證

- 落地四階段 S0–S3 與裁定 d1–d6:[[Projects/Codex完全支援_計劃]];驗證 [[Verification/2026-09-04_Codex完全支援S0安裝層驗收]]、[[Verification/2026-09-04_Codex完全支援S1hook適配驗收]]、[[Verification/2026-09-04_Codex完全支援S2迴圈編排驗收]]、[[Verification/2026-09-04_Codex完全支援S3量測驗收]]。
- 行為精修(擋停一次、範本通用句、shebang):[[Projects/Codex行為精修_計劃]];驗證 [[Verification/2026-09-05_Codex行為精修f02後測]]。
- 收工檢查本體:[[Systems/graph-sync-coverage]];安裝生命週期:[[Systems/lumos-cli-lifecycle]];設計/代碼迴圈的 Codex 席位規則:[[Systems/design-loop]]、[[Systems/pitfalls-code-loop]]、[[Systems/cross-family-audit]]。

## 探針修復的歷史脈絡（2026-10-03）

PITFALL: 首次修復穩定性試行重審 2db51cc4 時，讀 README 會冒充讀碼、Claude 非零退出混入有效樣本、逐題與整體分母不一致；前者來自判準放寬，退出碼缺口原已存在，分母矛盾在新增排除規則後暴露。出處 [[Verification/2026-10-03_修復穩定性試行第1案]]；後兩項防回歸測試 t_probe_repair_nonzero_exit、t_probe_repair_per_question_cli；讀碼問題尚未修好，重現與重啟條件見 [[Issues/探針讀碼證據不足]]。

WHY: 本次曾試把讀碼正則收窄到目標程式檔，但第二輪證明仍把搜尋路徑文字當讀碼，且誤傷先切目錄再讀檔；因此撤回這一候選，不把 shell 解析或工具結果關聯塞進同一修復。出處為該案 r2-correctness 與 r2-classification.json；下次處理讀碼判準，先依 [[Issues/探針讀碼證據不足]] 重估資料來源再實作。

## 回頭條件

WHY: 第1案續辦改從成功工具回傳辨識目標片段，避免繼續解析shell字串；標記若加在既有快照後會被收工hook當作模型改碼，所以此題每次嘗試建立含標記的獨立乾淨副本，結束刪除。代價是多一次複製；只限此題，正式探針首次部署與runner格式升級時重驗耗時及截斷。出處 [[Projects/探針讀碼結果證據_計劃]] 的設計審M1及 [[Verification/2026-10-03_修復穩定性試行第1案續辦]]；第三輪仍未收斂，候選未放行，後續先交使用者裁決。

PITFALL: 設計審B1重現建立副本後Git定位環境變數被runner重新繼承，cwd不保證隔離；沿用既有清洗函式延伸到runner與清理。防回歸 t_probe_source_probe_git_env 在兩個暫存repo驗證外側內容不變；清理失敗停批由 t_probe_source_probe_main 驗證。來源同續辦驗證，不把未跑真模型的fixture當生產觀測。

PITFALL: 第三輪證明上項測試只覆蓋兩種定位環境，不能保證 Git 設定注入與 absolute gitfile 的隔離；出處及可重現步驟見 [[Issues/探針Git隔離的設定與絕對路徑缺口]]。讀碼證據仍有缺 ID 事件計分的反例，見 [[Issues/探針讀碼證據不足]]；兩項 Issue 都是下次重啟的必讀入口，現有綠測試不構成放行證據。

WHY: 2026-10-04 使用者授權例外續修三項缺口；Git只關閉父程序command/global/system設定來源，保留HOME與非Git環境，避免改變被測CLI的skills/hooks來源。代價是不再採用使用者全域Git偏好；來源設定不寫入，副本local設定仍使用。出處 [[Verification/2026-10-04_修復穩定性試行第1案例外續修]]，防回歸t_probe_repair4_git_config；未來改Git設定來源時從該驗證入口重驗。

PITFALL: 單驗副本gitdir仍可能漏掉共用資料、core.worktree或refs等中繼資料符號連結；本輪臨時fixture在補最後一道前確實改動外側refs。選擇在Git寫入前拒絕中繼資料符號連結，即使連結目標在副本內也拒絕；普通clone與安全相對gitfile保持可用。出處同例外續修驗證，重現及防回歸t_probe_repair4_copied_git_paths；若要支援這類連結，先從該測試與Issue重估，不能直接移除拒絕條件。

PITFALL: 第四輪把副本頂層的綠測試誤擴成整棵Git樹安全會漏兩種配置：local include/worktree scope可恢復有效remote並蓋掉防推勾子，子模組仍有自己的remote及Git資料。另有共用沙盒清理失敗卻繼續下一題，以及Claude空ID工具回傳被當成功的反例。出處 [[Verification/2026-10-04_修復穩定性試行第1案例外續修]]；成對重現r4-parent-reproduction.json及r4-boundary.md，後續防回歸入口為 [[Issues/探針Git隔離的設定與絕對路徑缺口]]、[[Issues/探針共用沙盒清理失敗仍繼續評分]] 與 [[Issues/探針讀碼證據不足]]。第4輪處置閘FAIL，不能把t_probe_repair4_*的局部綠燈當成放行。

WHY: 2026-10-04 另開 [[Projects/探針隔離與清理收斂_計劃]] 處理第4輪的四組阻擋行為，不改寫原案四輪FAIL。保留可見Git歷史，但將繼承設定改為封閉重建、批次凍結後每場複製；這比單次清遠端或共用副本清理更容易界定失敗。代價是副本建立時間與磁碟用量增加；每週探針的 `sandbox_secs` 與 `model_secs` 是重評入口。證據見 [[Verification/2026-10-04_探針隔離與清理收斂]]。

PITFALL: 探針的Git hook僅擋意外push，不是網路隔離；模型若主動指定URL、停hook或用其他網路工具仍可能外送。外指符號連結與巢狀Git也不能用「頂層副本安全」推論安全，故本案採前置拒絕。重現入口與回歸測試為 [[Projects/探針隔離與清理收斂_計劃]] S1–S3 的 `t_probe_boundary_nested_git`、`t_probe_boundary_worktree_links`、`t_probe_boundary_git_config`；正式模型題目若要求HOME或網路操作，先依 [[Issues/探針沙盒改動真全域機器狀態]] 重驗外層隔離。

PITFALL: 本案實作首輪證明「找 `.git`」漏掉大小寫變體與 bare repo，且 `GIT_TRACE` 可讓儀器自己的 Git 呼叫把 log 寫進來源；白名單設定若漏 `user.*`，模型提交還會退用本機身分。出處 [[Verification/2026-10-04_探針隔離與清理收斂]] 及其 `probe-boundary-remediation/r1-*` 卷證；回歸測試 `t_probe_boundary_review1_git_shapes`、`t_probe_boundary_review1_trace_identity`。下次調整 `_git_env` 或 `_check_worktree_entries` 時重跑兩測試及 `probe_`，不能只看頂層 remote/hook 空值。

PITFALL: 第二輪代碼審在凍結版 730b06fe 證出主 Git 資料的 `worktrees/*/gitdir` 文字外指不受符號連結檢查保護，模型可把真 linked worktree 的 `.git` 改指向臨時副本；同輪證出 `GIT_AUTHOR_*`／`GIT_COMMITTER_*` 會蓋過 local 假身分，`git config user.*` 綠燈不能證明實際提交作者。另由編排者重現健康檢查讀取失敗被誤當普通題失敗。出處 [[Verification/2026-10-04_探針隔離與清理收斂]] 及 `probe-boundary-remediation/r2-*`；防回歸 `t_probe_boundary_review2_linked_worktree`、`t_probe_boundary_review2_effective_identity`、`t_probe_boundary_review2_health_unreadable`。下次改 Git 副本、runner 環境或 skills 健康檢查時以這三項重驗。

PITFALL: 第三輪證明健康檢查「回 fatal」仍可能假安全：runner 在模型後拋錯會跳過當場檢查、先跑下一題；最終檢查拋錯時 JSON 整批標不可判，但消融消費端仍按逐場 `reason=ok` 合併，`needed=0`。出處 [[Verification/2026-10-04_探針隔離與清理收斂]]、[[Issues/探針健康檢查不可判資料仍被重用]] 與 `probe-boundary-remediation/r3-reproduction.json`；目前沒有防回歸測試，代碼審第三輪 FAIL，不能拿251項綠燈放行。使用者裁決續修後，以 Issue 的臨時 repo 重現及實際 `load_results`／`needed`／`merge` 作紅綠入口，再審修補差異。

- REVISIT:2026-10-16 ★等 Enzo 裁,2026-09-16 確認仍未裁★:代碼審最後一輪之後補的那 3 行修法(父層是符號連結時的同類傷害)沒有席位審過,要不要補一輪只審這段差異的審查——或接受「同類修法第三次、而且測試反向驗證會翻紅」當作已經夠。
- REVISIT:2026-09-25 互動模式(codex TUI)下的擋停與 SubagentStart 領席;抽 5 場真實 Codex 對話看擋停後的說明合不合理。
- REVISIT:2026-10-04 有沒有人真的用 Codex 開 lumos 專案(0 筆=S2/S3 備而不用);armed 席被無關子代理搶走的頻率。
