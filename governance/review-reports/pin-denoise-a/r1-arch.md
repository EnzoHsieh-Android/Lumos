# pin-denoise-a r1 架構對齊審查

被審:`/tmp/pin-denoise-a-r1.md`(固定席降噪A層_計劃,94 行)。只判「跟本專案既有做法一不一致」,不找 bug、不評風格。

---

## 問一:分層依賴——新邏輯放的位置、誰讀誰,跟鄰居一樣嗎

**規則 1(間接保送收窄)★對齊★。**
spec 把「`contract in (INVARIANT, IRREVERSIBLE)` 才保送、RISK 類降自由席」放在既有的合約判定/BFS 保送site——`_impact_contract()`(`scripts/lumos:13872`)已經是 INVARIANT/IRREVERSIBLE/`RISK·<tag>`/None 四值的唯一來源,「軸序最低:合約標記存在時仍以合約身分出席」(`scripts/lumos:13900`)本來就寫在同一個函式裡;indirect 的 hop 上限判斷 `if contract and hop <= min(eff_depth, _pin_hop)`(`scripts/lumos:14464`)也已經是 contract-aware 的既有謂詞。規則 1 只是在同一個謂詞上多加一個 contract 值域過濾,分層方向、呼叫關係都沒有另立新路。

**規則 2(about_hit 豁免)——半對齊,層依賴方向被反轉,詳見問三。**
現行 `_impact_mark_about()` 的呼叫序是:先算出 `results` 的 `pinned` 欄(BFS+contract+hop),**之後**才呼叫 `_impact_mark_about(env, results, rel_file)` 幫已定案的候選加 `about_hit` 標記(`scripts/lumos:14476-14478`),再用 `r["pinned"]` 分 `pins`/`free`(`scripts/lumos:14480/14483`)——about 標記只影響 `pins.sort(...)` 的排序 tie-break(`scripts/lumos:14482`),是單向依賴:pinned 判定 → about 標記,不回頭。spec 規則 2 要「被 1 降級的節點若 about_hit → 留固定席」,等於要 about 標記反過來改寫 pinned 判定,把單向依賴變成迴圈。這是分層問題,但它是問三 major finding 的同一件事的另一面,此處不重複計入不對齊條數。

---

## 問二:命名與錯誤處理

**`LUMOS_IMPACT_HARD_PIN` 命名/預設值寫法★對齊★。**
spec:「總開關 `LUMOS_IMPACT_HARD_PIN`(預設?——★開關預設值走考卷:train 掃、held 驗一次★),0=舊制逃生」——這跟 `LUMOS_IMPACT_BASENAME_MATCH`「2026-08-07 轉正預設 1;0=逃生/A 臂」(`scripts/lumos:13815/13830`)、`LUMOS_IMPACT_RESCUE_N`「考卷轉正預設 1」→ 之後水位案改判「考卷轉正 N=3」(`scripts/lumos:14502-14509`)是同一套「先跑 train/held 考卷決定預設值,凍成常數,knob=0 留逃生」流程;`_impact_knob()` docstring 本身也講明「LUMOS_IMPACT_* env 僅供 goldset 網格消融,非使用者旗標」(`scripts/lumos:14134-14135`),跟 `LUMOS_IMPACT_ABOUT`「預設 1;0=整段不跑」(`scripts/lumos:878/14114`)同款「總開關」語意。沒有另立新的預設值決定方式。

**「外家 Codex」——查證後判定對齊,非過期指涉。**
一度懷疑 spec 下一步「design-loop(standard,3席+架構+外家 Codex)」(spec 第 94 行)跟已知的「Codex 到期,外家轉 Gemini」記載(`docs/lumos-toolchain-knowledge/Issues/外家席長期缺席仍照跑loop.md:55`)衝突。但派工紀錄 `governance/review-reports/pin-denoise-a/r1-dispatch.json` 顯示本輪 `ext-codex` 席(`"auditor":"codex exec --sandbox read-only"`)實際被派且已交回 `r1-ext.md` 的實質內容(非缺席)——即本案這一輪外家確實是 Codex,是本專案第二個來源(loop 執行紀錄)反證了單一來源(Issue 筆記)的過期判斷,不列入不對齊(對照 CLAUDE.md「只信一個來源、沒去對第二個」的教訓)。

---

## 問三:第二種做法——有沒有引入專案裡原本沒有的做法

**「硬/軟合約分級」是本案新造,PRIOR-ART 卻誤標成既有語彙★不對齊,major★。**
引句:「合約分級(硬 INVARIANT/IRREVERSIBLE vs 軟 RISK)是圖譜既有語彙」

全庫檢索「軟」與 RISK/合約分級同時出現的地方,只有本案自己(spec 第 8/43/82 行)。`scripts/lumos` 裡「軟」這個字有明確既有意涵——但那是**另一條軸**:doctor check 的 issue/advisory 二分(「軟提醒:印出但不動 issues」`scripts/lumos:487`、「硬擋」/「軟」`scripts/lumos:3208/3228`),管的是「這個檢查算不算阻擋分」,跟固定席保送用的合約分級(INVARIANT/IRREVERSIBLE/`RISK·<tag>`,`_impact_contract()` `scripts/lumos:13872-13906`)是兩個不相干的系統,`_impact_contract()` 本身、`_RISK_ENUM`(`scripts/lumos:2738`)、`lumos-cli-read.md:20`(「查硬合約 invariant 改=breaking」)全部只講「硬合約」,沒有一處把 RISK 標成「軟」。spec 把 doctor 軸的「硬/軟」詞彙借來套進合約分級軸,再回頭宣稱這是「圖譜既有語彙」——這正是引入一組全庫沒有先例的新分類法,而且用 PRIOR-ART 段落把它包裝成借用既有設計,會讓下一個讀者誤以為這個二分是有憑有據的既有規格,實際查不到出處。

**about_hit 從「只加分不降級」被賦予第二種語意:決定 pinned 歸屬★不對齊,major★。**
引句:「這是 about_code 第一次接上降噪——當豁免證據,不是入口」

`_impact_mark_about()` 的既有明文合約是:「★about_code 只加分不降級★……不改任何 pinned 判定——about 不是第四條入口」(`scripts/lumos:14109-14110`),目前唯一用途是 `pins.sort(...)` 裡的 tie-break(`scripts/lumos:14482`)。spec 規則 2 讓 about_hit 決定「被規則 1 降級的節點要不要留在固定席」——這不是加分,是決定候選最終進不進 `pins` 集合,跟既有合約字面相反。spec 自己也承認「第一次接上降噪」,但沒有提到這條路其實是 `固定席扇出降權_計劃` 三選一裡明確**沒被選中**、需要「重設計豁免再審」的那條:「三選一:甲收窄/**乙恢復降級加豁免(要重設計豁免再審)**/丙擱置」,當時裁定「甲最誠實……硬撐降噪會再走一輪已經兩次翻方向的迴圈」(`docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:22-23`)。本案現在做的「about_hit 豁免」在效果上跟被擱置的「乙」路徑重合,卻沒有引用這個 precedent、也沒有走它要求的「重設計」流程,直接以「不是入口」自我定性帶過。

**保底/安全網走「per-node 豁免+事後棘輪」,未討論是否該沿用既有 `rescued` 第三桶模式⚠(判不準)。**
引句:「主案:硬合約保送 + about 豁免 + 治標籤(三件一起)」

本專案處理「機械規則收窄後會誤傷該留的候選」這個問題,既有先例是 `rescued` 第三桶(`scripts/lumos:14498-14521`):系統性地算出「free 集裡 direct 命中不足 N 席」的缺口、外掛補齊,`pinned` 恆 `false`、不進 threshold/quota。spec 的安全網設計走的是不同機制家族——(a) 對單一節點的 `about_hit` 布林旗標決定要不要豁免降級,(b) `must_in_out` 棘輪在事後(held 驗證)擋下整體倒退——兩者都不是「系統性算出缺口、補一個固定數量的席次」這種 `rescued` 模式。spec 的「已試已殺」段只記了「扇出二元砍除」一個前例,沒有討論過為什麼不比照 `rescued` 幫降級的 RISK indirect 開一個類似的保底桶(例如「RISK indirect 至少保留 N 席」)。兩種問題(direct 被閾值/名額砍 vs. indirect 因合約類型被整體降級)是否真的需要不同機制,是設計判斷而非明顯對錯,故標 ⚠,交編排者裁。

---

## 結論

不對齊共 **2** 條,其中 major **2** 條:
1. 問三之一:PRIOR-ART 段稱「硬/軟合約分級是圖譜既有語彙」,但全庫檢索不到這個二分套用在合約分級軸上的先例——「軟」既有的唯一意涵是 doctor check 的 issue/advisory 分類,是另一條不相干的軸,本案把詞彙跨軸借用後又誤標成既有設計。
2. 問三之二:`about_hit` 現行明文合約是「只加分不降級……不是第四條入口」(`scripts/lumos:14109-14110`),本案規則 2 讓它決定 pinned 歸屬,是第二種語意;且此路徑與 `固定席扇出降權_計劃` d2 決策中明確擱置、需要「重設計豁免再審」的「乙」選項重合,spec 未引用此 precedent 也未走該流程。

另有 **1** 條 ⚠ 交編排者判準:降級後的保底/安全網要不要比照既有 `rescued` 第三桶模式(系統性缺口補齊),還是本案這種「per-node 豁免+事後棘輪」的做法就足夠——兩種問題性質不完全相同,判不準是否構成「另立新法」。

（問一/問二另有 1 處半對齊觀察併入問三計算,不重複列入條數;問二「外家 Codex」一度疑似過期指涉,查證 `r1-dispatch.json` 後確認對齊,不列入不對齊。）
