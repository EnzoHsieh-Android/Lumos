---
type: system
status: done
created: 2026-06-26
updated: 2026-08-23
self_audit: claude-fable/2026-08-24
about_code_stamp: claude/2026-08-30/d8883b1b5f71
tags:
  - type/system
  - status/done
summary: |-
  KEY:[2026-09-07 handoff]新讀原語 `lumos handoff <計劃節點>`——唯讀接手視圖:計劃點名的程式檔各是什麼 git 狀態(status --porcelain,含未追蹤/已刪;★不用 diff HEAD,它看不到未追蹤★)+最後提交、逐字稿尾端的意圖線索(importlib 借收工 hook 的人話判定與工具名單,★輪次邊界=最後一句人話★自算——hook 的邊界會被系統塞的任務通知截斷,r1 外家 #1;Codex 稿走 hook;自動挑 ~/.claude/projects/<slug>/ 的候選:排掉接手者自己 CLAUDE_CODE_SESSION_ID、提到這份計劃名者優先、候選列出)。★不造帳、不判做到哪、讀不到就印「意圖不可得(原因)」rc0★;只有用法錯(節點不存在/不在 git)才 rc2。來歷:進度從提交推導四版造帳全被打穿後的唯讀解,計劃 [[Projects/接手視圖_計劃]] [test:t_handoff_view]
  KEY:[2026-08-25]doctor E4 連鎖待辦軟提醒([[Projects/連鎖佇列軟提醒_計劃]])——統計併 E2 帳本掃描迴圈順手收集;零判定帳本數+最老天數+損毀另列;全判定整段靜默;gov check-cascade;supersede 開單當下 stderr 白話指路(修法 A;零鄰居分支不講「上面列的每個」);已知縫=CASCADE-EMPTY 帳本永久零判定 E4 長鳴,首次真實出現時裁;[test:t_doctor_cascade_reminder]
  KEY:[2026-08-23]`git_last_change_dates(repo_root, vault)`——一次 git log 拿 vault 每檔最後改動日期(行程內快取;git 缺席回 {} fail-open)。是 about_code 過期判準的材料(計劃 [[Projects/固定席扇出降權_計劃]] #5):逐篇 83 次 5.3s vs 批次 0.22s;★必帶 -c core.quotepath=false★,vault 路徑帶中文目錄名,沒旗標整條路徑被八進位跳脫、表是空的且不報錯(翻紅釘實證連英文檔都撈不到)。尚未接進 impact,只是原語
  KEY:[2026-08-05]檢索考卷加 synonym 類(toolchain 4 題/landmark 3 題,查詢用別名期望命中帶 aliases 節點;檢索實跑 ground、單標註者、goldset 註記題集變更)——aliases 欄的貢獻自此每週考卷自動量;出題日 held 基線:toolchain ranked nDCG@5=0.789、landmark=0.840
  KEY:[2026-08-05 標籤收編]context 頭部攤出 type/status 以外全部 tag 家族(priority/scope/flag/risk…,`家族:值` 併入 meta 行)——寫給 AI 的分類資訊原本在進場主讀路徑隱形 [test:t_context_header_extra_tag_families];impact 合約軸 RISK·值分類(軸序 IRREVERSIBLE>INVARIANT>RISK) [test:t_impact_contract_risk_axis];★2026-08-24 pin-denoise-a-v4:RISK 類 indirect 不再保送必看——降入 JSON 頂層 lane 參考道(LUMOS_IMPACT_HARD_PIN ★2026-08-24 考卷轉正預設 1★,0 逃生)[test:t_impact_hard_pin_lane]★
  KEY:[2026-08-05]search 排序加 aliases 欄(權重 3.5,略低於標題 4.0)——frontmatter aliases list 進 BM25F;同義詞落空(搜「作廢」圖譜寫「沖銷」)的最便宜解,寫入者留同義詞一次、檢索受益永久 [test:t_search_aliases_field]
  KEY:[2026-08-04]+quote-check(vault-free 讀命令):報告引句逐條對回凍結快照(_quote_norm 正規化;rc0 全 ok/rc1 miss/rc2 IO或零引句)——disposal 閘的④號合取同源消費 [test:t_quote_check_normalization_and_verdict]
  FLOW:任一讀指令 → find_vault(從 cwd 往上找 docs/*-knowledge 或 standalone vault root) → load_vault(掃全 .md、解 frontmatter+wikilink) → Env(notes/by_stem/edges) → 各 cmd_* 純讀印出(context/show 另寫 usage-log 事件帳;doctor --ci 寫 governance-log) → return 0(查無/正則錯=非0)
  KEY:[2026-09-07 loop list]新讀原語 `lumos loop list`——先看有哪些審查編號還開著(next/status/verify-progress 全都強制要 loop_id,卻沒有入口能先拿到編號;缺口出自 [[Projects/執行DAG_調研]])。★關門訊號取治理帳本來就會落的放行事件★(design-loop converged/cap-reached/rewrite + code-loop passed/skipped,nodes 帶編號),不新增任何要人維護的狀態;開著=沒關門事件或關門後又記新輪次。★誠實界線印在輸出裡★:關門事件慣例 2026-08-22 才開始,更早的迴圈天生沒這筆,工具只說「帳面沒看到關門事件」不說「沒做完」。唯讀恆 rc0;`--stale` 看空轉候選、`--exclude <前綴>` 排掉自主迴圈每日場次(不寫死前綴)、`--now YYYY-MM-DD` 指定今天(重算/測試用,壞值擋下 rc2)。★時間一律走 UTC 正規化再比(`_loop_ts_key`/`_loop_ts_newer`)★——兩本帳今天全寫 +08:00(數過 1101/26443 筆),直接比字串剛好會對但那是巧合;換一台機器寫 UTC 就會**靜默**把開著判成關了。解不動或沒帶時區才退回字串比對(舊帳相容),★沒帶時區一律不猜★。驗證見 [[Verification/2026-09-07_loop-list開著的迴圈]]
  KEY:[2026-08-16 query 結構化查詢]新讀原語 `query`——WHERE over 標籤家族(--tag 可重複=AND/--no-tag/--active 排收案態/--contract 沿 extract_contracts/--linked 1-hop 鄰域/--json);旗標 AND 疊加不發明查詢語言(borrow zk list);預設排除 superseded 對齊 search 真遺忘+--include-superseded 逃生;bare 無條件 rc2(對齊 stale --candidate);緣起=標籤收編後「欄位只有顯示沒有篩選」,Landmark 三情境實測見 [[Projects/圖譜結構化查詢_計劃]] [test:t_query_tag_and,t_query_no_tag_and_active,t_query_contract_uses_real_parser,t_query_linked_scope,t_query_forget_superseded,t_query_bare_rc2,t_query_json]
  KEY:read/traverse 14 原語全建在記憶體 Env 之上(notes 字典 + 雙向 edges + by_stem 索引);**不改圖譜節點檔**——context 與 show 寫 best-effort usage-log 事件帳(A2,2026-07-11 起)、doctor --ci 視 findings 寫 governance-log,其餘讀指令純讀([[Projects/lumos-show讀取入口_計劃]] r4 收斂措辭,修 A2 起「零副作用」宣稱漂移);與 7 個寫入原語(set/append/new/decision-* …)互斥
  KEY:進場三步入口固定 search(定位節點) → context(掃脈絡,頭部突顯 ⚠ 合約) → contracts(查硬合約 invariant 改=breaking),CLAUDE.md 規定動既有系統第一個工具呼叫必須是 lumos 而非 grep/Read/DB
  KEY:doctor 是全圖權威巡檢(4 檢查 orphans/unresolved/verified_by 雙向(stale/fail 驗證豁免——E1 拔死背書後不反咬漏寫)/plan_refs 意圖鏈 + 同名守衛 + frontmatter lint + Check T/R/H;Check P 失效檔案認領(inline-code 路徑指死碼);Check E1 失效背書(verified_by 指向 stale/fail/superseded 驗證→死背書;superseded=真遺忘第二刀 2026-07-26,同刀:Check3 skip 集+sync-verified-by 過濾+orphan 豁免四位一致)+ Check E2 建在被推翻決策上(決策 valid:false+ended → M2 共用 typed 索引查連入來源、updated 早於 ended → 落後邊;decision_refs 精化只標指到那條;M3 帳本抑制 terminal ts>=ended 跳過=主/補網不重報)+ Check E3 意圖鏈斷義(decision_refs 指翻案決策+dangling 浮出);關係層皆軟提醒;Check J regen 重生來源守衛[M1 2026-07-16]——regen 節點 provenance 分級:J-a 拒發明合約(INVARIANT 標記行需 [src:]/[git:] 意圖證據)+J-b DECISION 四態+J-c 證據指針 substring gate(共用 _validate_repo_ref 不經 top_dirs 靜默過濾;shallow 降 warn_soft 顯性)+J-d 唯讀提醒;與 lint 共用 check_regen_provenance 防兩入口漂移 [test:t_check_j_regen,t_check_j_git]);與 lint 分工——lint 只看單篇 node-local(regen 節點 Check J 為 opt-in 例外需檔案+git 存取)、predicts pre-push 會不會擋
  KEY:search 預設排除 fenced+inline code(對齊 doctor 連結抽取慣例,--code 才含)、大小寫不敏感 substring、--regex 切正則;結構化查詢走 query(標籤家族 WHERE)/contracts/decisions/stale 而非 search
  KEY:★多詞回退(2026-08-03 人裁翻為預設,--no-any 逃生;--any 留相容)★——整串片語在檢查範圍內無命中時,退成各詞 OR 召回再交 BM25F 排序。★fallback-only 不是永遠 OR★:片語找得到就不觸發,故對既有查詢零回歸(機械可證+對照組 5 題逐檔實證)。同時印★逐詞覆蓋★到 stderr——回退後搜尋幾乎不可能再回 0,「查無」這個訊號會消失,逐詞覆蓋把它換一種形式還回來(某詞 0 命中會標 ★)。★訊息宣稱的範圍不得大於實際檢查的範圍★:範圍字串必須同時反映 --path／作廢與否／--code 三個維度(這條在 code-loop 四輪裡被抓到三次,每次都是漏掉其中一個維度) [test:t_search_multiword_fallback_is_default_and_only_on_zero,t_search_multiword_fallback_reports_per_term_coverage,t_search_multiword_fallback_scope_message_covers_path_and_superseded]
  KEY:★預檢迴圈與主迴圈共用 `_search_visible_lines` 單一實作★(2026-08-03 code-loop r2)——原本預檢自己一份「整段 regex 剝 fence」,遇未閉合圍欄與主迴圈分岔,導致逐詞覆蓋虛報非零;同源修法也收編了 `load_vault`／`cmd_guard_trace`(見 [[Issues/2026-08-03_剝除與邊界解析的既有缺陷群]],★`FENCE_RE` 仍活在 refcheck 家族三處未收編★)
  KEY:★INVARIANT★ search 預設排除 status=superseded 節點但不排除 stale(真遺忘,GateMem 2026-07-24;stale 是待重驗警訊,藏了=製造新洞,doctor Check S 綁 stale+superseded 正是反例),--include-superseded 逃生;濾網插「命中確認後、三路分岔前」故 ranked/legacy/regex 三路一致、hidden 數=命中被藏筆數非全庫;隱藏數走 stderr(全模式含 --files-only,不污染 stdout)、--json 加 hidden_superseded 欄位 [test:t_search_forget_superseded] [audit:sonnet/2026-07-24]
  KEY:[缺口已補 2026-07-25]原「Check T 無 Python profile」缺口已補(TEST_PROFILES 加 python:行首錨+檔名錨+comment_strip=none),本合約隨之升回正式;★根因更正★:當初被判偽證據的真兇不是 dirs(Check T 掃描走全 repo 不吃 dirs),是 discover 對所有語言剝 C 式註解、test_lumos.py 中文註解的 status/* 與遠處 glob 字面 **/ 配對吃掉半個檔(260→94);詳 [[Projects/CheckT-Python-profile_計劃]]
  KEY:真遺忘只做 search 這一刀(2026-07-24 使用者裁定);context 基本鄰居/推薦、impact、doctor 對作廢驗證的不一致=已知殘留(impact 永不做預設藏——direct 命中是事故記憶);設計與三審見 [[Projects/真遺忘召回過濾_計劃]]
  KEY:讀指令屬「專案層」——以 cwd find_vault 鎖定本專案 vault(不受同名 vault 影響);對比 install/bootstrap 的「機器層」(全域 lumos + user-scope skills)
  DEP:scripts/lumos load_vault/Env/find_vault｜extract_contracts(contracts/context 共用)｜parse_decisions(decisions;stale 不經它——2026-08-24 審計訂正)｜status_of(links/map/stale 標狀態)
  KEY:stale --candidate 無 --match 直接 rc2 拒絕(反直覺限制:即使給了 --candidate 沒帶 --match 也拒,避免列全 vault 變噪音);--candidate --match <詞> 才有效
  TEST:scripts/test_lumos.py(t_-prefixed Python 回歸,非 doctor Check T 認的 C# xunit)
related:
  - "[[Systems/lumos-cli-write]]"
  - "[[Systems/lumos-cli-lifecycle]]"
  - "[[Projects/檢索多詞回退_計劃]]"
  - "[[Issues/2026-08-03_剝除與邊界解析的既有缺陷群]]"
  - "[[Projects/圖譜結構化查詢_計劃]]"
decisions:
  - content: 讀寫原語嚴格分軌——14 個讀指令不改圖譜節點檔(2026-08-24 審計統一計數)(context/show 寫 best-effort usage-log 事件帳、doctor --ci 寫 governance-log,其餘純讀;2026-07-21 修 A2 漂移後措辭);一切 frontmatter 寫入走 set/append/decision-* 等寫入原語(走 atomic_write_verify:寫 tmp → re-parse 自驗 + lint 無新指紋 → atomic rename)
    id: d1
    context: 直接手改 frontmatter 會繞過寫後自驗與鐵則防護(YAML 格式爆、ghost 節點、裸合約),且讀指令若兼寫會讓「查脈絡」帶副作用
    why_chosen: 讀路徑不動圖譜內容才能放心當入口反覆掃(best-effort 事件帳/治理帳不在此限,2026-07-21 措辭修真);寫路徑集中過 atomic 自驗閘,任一步敗則 tmp 丟棄原檔不動,保證圖譜永遠可解析
    decided: 2026-06-26
    valid: true
  - content: doctor(全圖權威)與 lint(單檔快檢)分工——lint node-local 不掃 repo 比 doctor 快、寫完一篇立刻自驗、error 即 pre-push 會擋的同類;doctor 跑全圖跨節點完整性 + [test:] 存在性
    id: d2
    context: 每寫一個節點都跑全圖 doctor 太慢、回饋慢;但單檔檢查看不到跨節點完整性(orphans/雙向同步/意圖鏈)
    why_chosen: 兩段式——寫節點當下用 lint 拿快回饋(預測 pre-push),收尾再用 doctor 跑全圖權威巡檢;push 前 pre-push 仍兜底再擋一次
    decided: 2026-06-26
    valid: true
  - content: 讀指令以 cwd find_vault 鎖定「專案層」vault(往上找 docs/*-knowledge 或 standalone vault root),不受多專案同名 vault 影響;與 install/bootstrap 的「機器層」分軌
    id: d3
    context: Obsidian CLI 的 vault= 只吃資料夾 basename,多專案都叫 docs/knowledge 會撞名;lumos 改以 cwd 往上找消歧
    why_chosen: cwd-based 定位讓任何專案子目錄直接 lumos <cmd> 都鎖到正確 vault,機器層工具(全域 lumos/skills)則一次裝好共用
    decided: 2026-06-26
    valid: true
  - content: 中文查詢要在概念之間加空白(Landmark 2026-08-11 手寫在自家 CLAUDE.md 的實測規則,Enzo 2026-08-22 要求注入所有專案):①注入範本對照表加一列 ②search 在「查詢是一串 ≥4 個中日韓字、沒空白、0 命中」時自己提示改寫範例 ③索引子檔與 skill 頭版同步。
    id: d4
    decided: 2026-08-22
    valid: true
  - content: Landmark CLAUDE.md 的三條圖譜查詢體悟收進注入範本與工具(Enzo 2026-08-22):0 筆看逐詞覆蓋 ★ 詞換同義、換三次再問人、不轉 grep;大節點先 --brief(context 輸出 >20KB 時工具自己提示);單篇內部新舊打架時有日期的 KEY 行 > 正文,衝突去 code 裁再修圖譜。「遙控本機≠網頁遠端版」進 skill 頭版。
    id: d5
    decided: 2026-08-22
    valid: true
  - content: 補充 d4 的第②項(不翻案,d4 主旨仍然有效):search 對「一串沒有空白的中文」多了一條弱回退——把連續漢字段切成相鄰兩字一組去召回。新開獨立旗標 --cjk-loose,★預設關★。d4 第①項那句「黏成一串幾乎必定 0 筆」★今天仍然正確★(預設關,行為一行沒變),所以注入範本那一列這次不動;等預設翻開那天才改,免得文件先於行為講出假話。字元域分兩件裁:跑不跑弱回退只認漢字(假名/諺文在切詞器裡產不出字對),印不印「加空白」建議照舊涵蓋日韓(那是跟文字系統無關的操作建議),只是訊息不再說「中文」。
    id: d6
    context: d4 第②項只做到「0 命中時提示改寫」;而一串沒有空白的中文是結構上永遠查不到(回退要求超過一個詞,沒空白就是一個詞)。一條紀律存在就代表這個坑一直有人踩,踩的人是每個新 session 的 AI。
    why_chosen: 先實作(藏旗標後)→組池→標註→量測→才裁預設:評測的組池工具靠現有搜尋撈候選給人標註,而這些查詢現在回 0 候選、沒東西可標,所以量測不可能排在實作前面(鄰居那案的「上一版想錯了」寫的就是這件事)。預設關的時候沒有任何呼叫端行為改變,這點機械可證。
    decided: 2026-09-07
    valid: true
verified_by:
  - "[[Verification/2026-07-14_relguard_E1失效背書]]"
  - "[[Verification/2026-07-14_relguard_E2建在被推翻決策上]]"
  - "[[Verification/2026-07-15_主網M1_決策穩定ID]]"
  - "[[Verification/2026-07-15_主網M2_typed-edge索引]]"
  - "[[Verification/2026-07-15_主網M3_cascade帳本]]"
  - "[[Verification/2026-07-15_主網M4_觸發與連鎖]]"
  - "[[Verification/2026-07-16_fromscratch守衛M1_CheckJ]]"
  - "[[Verification/2026-07-24_真遺忘search排除superseded]]"
  - "[[Verification/2026-08-05_流程優化六件落地]]"
  - "[[Verification/2026-08-05_標籤結構收編落地]]"
  - "[[Verification/2026-08-16_圖譜結構化查詢query落地]]"
  - "[[Verification/2026-08-22_狀態表過期偵測]]"
  - "[[Verification/2026-08-25_連鎖佇列軟提醒落地]]"
  - "[[Verification/2026-08-27_關係語意腐爛守衛_G1解鎖即活]]"
  - "[[Verification/2026-09-07_loop-list開著的迴圈]]"
  - "[[Verification/2026-09-07_handoff接手視圖]]"
about_code:
  - scripts/lumos
---
# lumos-cli-read

`scripts/lumos` 的 **read/traverse 核心原語**(14 個)——圖譜的查詢與遍歷面。對既有系統動手前,CLAUDE.md 規定第一個工具呼叫必須是這組 `lumos` 讀指令,而非 grep / Read / Explore / DB(code 讀不出「為什麼 / 邊界 / 哪些是不可改合約 / 驗過沒」)。

源起:CLI 核心非日報觸發(read 原語是 lumos 工具鏈的地基能力,非某日報 gap/inspiration 衍生的單一功能)。

## 共同地基
所有讀指令先 `find_vault`(從 cwd 往上找 `docs/*-knowledge` 或 standalone vault root)→ `load_vault` 掃全 `.md`、解 frontmatter + wikilink → 建記憶體 `Env`(`notes` 節點字典、`by_stem` 名稱索引、雙向 `edges` = (out_e, in_e))。各 `cmd_*` 在此 Env 上純讀、印出、`return 0`(查無資料 / 正則無效等 → 非 0)。**不改圖譜節點檔**——context/show 寫 best-effort usage-log 事件帳(A2)、doctor --ci 視 findings 寫 governance-log,其餘讀指令純讀(2026-07-21 修「全程不寫檔」措辭與現實的 A2 漂移)。

## 14 個原語(對應 cmd_* / scripts/lumos)
- **進場三步(入口固定順序)**
  - `search <詞> [--path Systems] [--regex] [--files-only] [--code] [--include-superseded]`(`cmd_search`):全文搜尋 frontmatter+body,大小寫不敏感 substring。**預設排除 fenced + inline code 區塊**(對齊 doctor 連結抽取慣例),`--code` 才含;`context` 標記命中區域(★INVARIANT★/KEY/fm:欄位/body)。**預設排除 `status=superseded` 節點(真遺忘;不排 stale)**,`--include-superseded` 逃生、隱藏數走 stderr(核心行為與回歸守衛見上方 summary KEY)。**多詞查詢預設走回退**(2026-08-03；`--no-any` 關)，並印逐詞覆蓋到 stderr。職責=自由文字,結構化查詢走 query/contracts/decisions/stale。
  - `context <節點> [--brief]`(`cmd_context`):節點 + 鄰居 summary 壓縮索引(MemPalace closet)。**頭部直接攤出 ⚠ 合約**(extract_contracts);`--brief` 只給 meta + summary 首兩行 + 鄰居名單(壓 token)。
  - `show <節點> [--body-only]`(`cmd_show`,2026-07-21):**節點檔完整內容**(frontmatter+body)——context 是壓縮導航(不含 body),show 是完整真相讀取;解「規範禁 Read 圖譜但無全文入口」的結構性違章(外審 blocker,設計/審計 loop 見 [[Projects/lumos-show讀取入口_計劃]])。`--body-only` 以 `split_frontmatter` 剝離開頭 frontmatter;重開檔失敗(壞 symlink/race)→ stderr+rc2 不裸 traceback。
  - `contracts [節點]`(`cmd_contracts`):合約登記簿,列 `★INVARIANT★`(改=breaking)/ `★DEBT★`(可改);**只認 KEY 行前綴標準格式**;★INVARIANT★ 顯示綁定的 `[test:]`,未綁=⚠(doctor Check T 會擋)。
- **巡檢 / 完整性**
  - `doctor [--ci]`(`run_doctor`,非 cmd_ 前綴——L4 審計 2026-07-24 修正指針):全圖權威健康巡檢——基礎 4 檢查(orphans/破連結/verified_by 雙向/plan_refs)之外還有字母系檢查 C/D/E1-E3/J/K/M/N/P/R/S/S2/T/U/V/W/Y 等(以 run_doctor 現碼為準,2026-08-24 審計:原文只列 4 個嚴重低估;S2=about_code 過期)(舊文保留:3/4 verified_by 雙向同步(stale/fail 驗證豁免,E1↔Check3 矛盾修 2026-07-15)、4/4 plan_refs 意圖鏈)+ 同名守衛 + frontmatter lint + Check T(★INVARIANT★→測試綁定)/ Check R(可逆性回退)/ Check H(漏標可逆性軟提醒,僅 --ci 掃 diff)+ Check P(失效檔案認領:inline-code 路徑指向已不存在檔案)+ Check E1/E2/E3(關係層:E1 失效背書 verified_by→stale/fail、E2 建在被推翻決策上 決策翻案而 typed 連入來源未跟上——鄰居有 decision_refs 時精化為只標指到那條、且 M3 rel-cascade 帳本有 terminal 判定(ts>=ended)即跳過＝主/補網不重報、E3 意圖鏈斷義 decision_refs 指向的決策已翻案+dangling 浮出;皆軟提醒)。`--ci` = `--strict` + 無色彩,且會寫 `.governance-log.jsonl`(寫者=doctor --ci＋anchor approve,scripts/lumos `_append_governance_log`(函式名錨;行號會漂,2026-08-24 時 ≈:435) 自述;原「唯一寫者」為漂移,2026-07-21 順手修真)。
- **遍歷 / 關聯**
  - `links <節點>` / `backlinks <節點>`(`cmd_links`,reverse=True 即 backlinks):列連出 / 連入節點 + 狀態。
  - `map <節點> [--depth 2]`(`cmd_map`):鄰域樹狀展開,`↺` 標已出現過(防環)。
  - `export [dot|mermaid] --folders <…>`(`cmd_export`):導出指定資料夾子圖——★格式參數要放在 --folders 前★(--folders 是 nargs=+,放後面會被當資料夾名靜默吃掉、輸出錯格式不報錯;2026-08-24 審計實測)。
- **結構化查詢(2026-08-16)**
  - `query [--tag 家族/值]… [--no-tag …] [--active] [--contract] [--linked <節點>] [--include-superseded] [--json]`(`cmd_query`):**WHERE over 標籤家族**——旗標一律 AND 疊加,不發明查詢語言(borrow zk `list` 旗標語意)。`--active`=status 不在收案態(done/pass/superseded/resolved/wontfix);`--contract` 沿用 `extract_contracts` 只認 KEY 行標準格式(散文提及不算);`--linked`=範圍縮到該節點連入+連出 1-hop 鄰居(不含錨點);預設排除 superseded(對齊 search 真遺忘)、bare 無條件 rc2(對齊 stale --candidate 慣例)。`--json` 輸出結構:`{results:[{node,status,tags}],hidden_superseded}`(tags=type/status 以外家族)。緣起與 Landmark 三情境實測見 [[Projects/圖譜結構化查詢_計劃]]。
- **決策 / 重驗 / 概覽**
  - `decisions [節點] [--superseded]`(`cmd_decisions`):讀單篇 ADR 決策;`--superseded` 全 vault 掃 `valid:false` 被推翻的決策。
  - `stale [--match <字串>] [--candidate]`(`cmd_stale`):`status:stale` 清單;`--match` 掃 valid_under + revalidate_when 命中(含 Archive);`--candidate --match <關鍵字>` 聚焦活躍 Verification 的 revalidate_when(排 Archive)= 「改 X 時該重驗哪幾篇」。bare `--candidate` 或空 `--match` 直接 rc2 拒絕(避免列全部變噪音)。
  - `recent --days N`(`cmd_recent`):近 N 天修改節點(mtime 排序)。
  - `stats`(`cmd_stats`):各資料夾節點數 + total。

## 關鍵設計
- **讀寫嚴格分軌**:這 14 個不改圖譜節點檔(context/show 寫 usage-log 事件帳、doctor --ci 寫 governance-log,其餘純讀);寫入走另 7 個原語(set/append/new/archive/decision-add/decision-supersede/self-audit),經 `atomic_write_verify`(寫 tmp → re-parse 自驗 + lint 無新指紋 → atomic rename,任一步敗則 tmp 丟棄原檔不動)。詳見寫入原語節點。
- **doctor vs lint 分工**:doctor 全圖權威(跨節點 + [test:] 存在性);`lint <節點>` 單檔 node-local 快檢,predicts pre-push 會不會擋。寫節點當下 lint,收尾 doctor。
- **lint 另有一項軟提醒:開頭欄位的鍵打錯會被唸出來**(2026-09-06 全 repo 審視 #16)。出身:鍵打錯(例如把 `valid_under` 打成 `valid_unde`)以前是**所有檢查靜默略過**——那個欄位等於沒寫,而它可能正是承載回頭條件或驗證關聯的欄位。現在會指出哪個鍵不認得,並在只差一個字元時給出近名候選。
  - ★只算 warning 不升 error★:工具對未知欄位的立場是前向相容(消費專案與跨專案核心庫各有自己的欄位),升成 error 會讓別人的圖譜每次 lint 都被嘮叨。
  - 認得哪些鍵**是問工具、不是問這個圖譜**:除了一份固定清單,執行期還會併入工具自己的欄位常數(清單欄位與純連結欄位那兩份),所以那兩份之後再加欄位,這裡不必跟著改。★代碼審 r1 才修對★:初版清單是「掃本圖譜出現過的鍵」建的,漏掉兩個工具真的會讀、但本圖譜剛好沒節點寫的欄位,被誤報時提示文字說「不會被任何檢查讀到」——那句話本身是假的。
  - 別的圖譜有自己的欄位時,可以在專案的 `.lumos/config.json` 用 `extra_frontmatter_keys` 列進去。找設定檔的方式是**從圖譜目錄往上找設定檔本身、走到版控根就停**(不是寫死往上兩層——寫死的話,圖譜巢得更深的佈局會算到錯的地方,擴充口悄悄失效且不報錯)。
- **專案層 vs 機器層**:讀指令以 cwd `find_vault` 鎖本專案 vault(不受同名影響);install / bootstrap 是機器層(全域 `lumos` + user-scope skills),不在本節點範圍。

## 已知限制
- `search` 對 fenced/inline code 內字串預設看不到(需 `--code`);要查「散文裡剛好提到 ★ 字面」與「真合約標記」靠 `contracts` 的 KEY 行錨定區分,不靠 search。
- 同名節點:`find` 取第一個並印 `⚠ 同名筆記` stderr 警示;消歧靠資料夾前綴命名(`docs/<slug>-knowledge/`)。

## 相關
- 操作表權威:`CLAUDE.md`(入口三步 + 標籤規範)、`skills/lumos-project-notes/commands/INDEX.md`(子命令按情境分類索引;SKILL.md 的「25 子命令全覽」段已不存在——2026-08-24 審計訂正;現行總數以 `lumos --help` 62 頂層為準)。
- 實作落點:`scripts/lumos` `cmd_search`/`cmd_context`/`cmd_show`/`cmd_query`/`cmd_contracts`/`run_doctor`/`cmd_links`/`cmd_map`/`cmd_export`/`cmd_decisions`/`cmd_stale`/`cmd_recent`/`cmd_stats` + `load_vault`/`Env`/`find_vault`。
- 回歸測試:`scripts/test_lumos.py`(Python t_-prefixed)。
- 對稱寫入原語見 [[Systems/lumos-cli-write]];安裝 / 生命週期見 [[Systems/lumos-cli-lifecycle]];`lumos --help` 為現行權威。

## 近期修正
- 2026-07-11 export html 視覺化七項優化（使用者提案全採）：①標籤 LOD（重要度排名×相機距離預算,hover/選中恆顯）②驗證摺疊預設開（Verification 隱藏、母節點標 ✓N 徽章、選中母節點自動現形）③單擊容差（pointerup 位移<5px 兜底,修 3D 旋轉吃 click）＋2D/3D 切換（numDimensions+鎖旋轉）④搜尋 Enter 飛至最佳命中開面板（前綴>包含,同級取重要度）⑤「只看合約」chip（合約節點+其 verify 目標）⑥面板返回鈕（navStack;搜尋跳轉不入棧=已知取捨）⑦時間軸生長回放（節點 date/created,拉桿+▶ 播放）。真機驗證：Chrome 擴充+Playwright 雙路實測全過;t_export_html +10 骨架斷言。


- 2026-07-11 export html 視覺化修：節點面板關閉鈕 `#close` 被後繪的 `#phead`（透明背景）蓋住，真實點擊被攔截而程式呼叫正常——Playwright elementFromPoint 實測定位，補 `z-index:3`。教訓：疊層 UI 的可點性要用真實命中測試驗，不能只驗 handler 有綁。

## ★第一眼那幾個畫面(2026-09-07 全 repo 審視 #9)★

新手和 AI 第一次碰到這個工具就是這幾個畫面。這批改的全是訊息,不是功能。

### 找不到圖譜:三條路一個答案,而且不准回成功

同一件事(這個專案沒有圖譜),原本三種問法給三種答案——查檔案那條回一個碼加一句除錯口吻的話、查節點那條回另一個碼加白話擋下、**查改動範圍那條回成功並印「0 檔、固定席 0」**。

**最後那個最危險**:它看起來像查過了、結論是沒有相關筆記——而它根本沒有圖譜可查。**這兩件事差很多**:一個是還沒建圖譜,一個是真的沒關聯。

真因是那條路只在逐檔迴圈裡才發現沒圖譜,而「這個範圍 0 個檔」時迴圈根本不跑,於是一路走到最後印「0 篇」。文件本來就寫著它會回「圖譜缺」,只是走不到。

現在三條路統一:同一個退出碼、同一句話,而且明講這跟「查過了沒有」是兩件事,並給下一步指令。

### 打錯節點名:給候選,而且不要講寫入側的話

四支**讀取**指令(健康巡檢、看合約、看漂移史、決策重編)打錯名字時,印的都是「決策沒地方掛」——**那是寫入側專用的話**,白話化那批複製貼上時漏改。讀的人拿到一句對不上自己在做什麼的訊息,而且不給候選,只能自己回去猜名字。

現在打錯一個字會直接指出正確那篇(用既有的近名判準,不另引第二種),完全不像時給搜尋指令當退路。

### 打錯指令 / 裸打

打錯一個字母原本會印三份同樣的指令清單(usage 一串、英文提示、再逐個列一遍),而使用者要的只是「你是不是想打 doctor」。裸打時吐的是英文的「缺少必填參數」。

現在:打錯給近名建議、子命令那層指自己那層的說明;裸打給入口三步。

### 說明段:不再手抄清單

手抄那份停在 10 個、實際 66 個,而且 argparse 會再印一遍(畫面上兩份)。**改法不是把清單補齊**——補齊的隔天又會過期。清單的單一來源交給 argparse 自己印,說明段只留定位與入口三步,**刻意不寫「共幾個」**(寫了就是另一個會過期的數字)。守衛盯的是「手抄清單不准長回來」。
