---
type: project
status: doing
created: 2026-08-18
updated: 2026-08-18
tags:
  - type/project
  - status/doing
  - scope/graph-governance
aliases:
  - 循序 tier 錨定
summary: |
  FLOW:守衛 kind-aware 放寬一格(code∧standard∧無 --round 循序=設計行為)→loop next seq 樣式(width=1/cap 沿 3/canary 單值/record_cmd 無 --round)→編制表補 code/standard(sequential)
  KEY:零收緊——code+standard 帶 --round(panel)照舊合法,反向守衛經 r1 三席一致撤除;indeterminate/design/high/light 各格不動,回歸測試逐格釘
  KEY:tier_hint 對 code legacy loop=警告式(補標 --tier standard 會把既有輪數整批計入 cap=3,建議開新 loop id,不邀請補標)
  KEY:修真清單含 skills/lumos-code-loop/SKILL.md 護欄 cap 數字與 _TIER_ROSTER 上方註解、loop status --roster 對循序多 vacuous 屬誠實現狀
  KEY:範圍刀=收斂閘判定式(--gate/--disposal/--panel)一字不動、不回溯舊帳、不為循序發明 dispatch 慣例
  TEST:六組測試見 body 測試策略節(anchor/panel_ok/回歸格含 light/roster 表/cap 行為/tier_hint 警告措辭)
---

> 白話:單 reviewer 循序跑的 code loop,照規矩本來就該標 standard 檔位,但現在的「檔位↔記帳格式一致性守衛」不分 loop 種類,一標 standard 就被當成漏帶 panel 格式擋死(rc2)——結果歷史上三個循序 loop 全被迫掉回最鬆的 legacy 判準(cap 6 而非 3,多燒三輪才被逼停)。本案把守衛改成認得 loop 種類:code 種的 standard=循序是設計行為,放行;其餘象限一格不動。

## 緣起

- 事故單源=[[Issues/loop-next吐不可宣告的tier]](2026-08-04):當時只修了下游症狀(record_cmd 不吐不可宣告值+tier_hint),病根明文留案。
- 2026-08-18 [[Projects/派工編制資料化_計劃]] r1 整合席 CLI 實測重現全鏈:code- loop 記 `--tier standard`(無 --round,循序本格)→ 下一次 `loop next` rc2「tier=standard 要求 panel 格式」;全庫零筆 code loop 成功錨定 standard。編制表 code/standard 列因此被剔出 v1(範圍刀明文另案=本案)。
- 受害帳:`code-slim-python`/`code-teardown-windows`/`code-slim-handoff` tier 全 None;code-slim-python 跑滿 legacy cap 6 才攤人,標得上 standard 的話第 3 輪就停。

PRIOR-ART: ① 最小解層級——非新機制,是既有守衛(cmd_loop_next tier↔格式一致性,code-loop r1 折入)的判斷式加 kind 維度;kind 判定原語 `_roster_kind` 昨日已落地,直接複用。② 世界解過沒——同型=分支保護規則按 repo 類型分流(GitHub rulesets 的 target 條件);概念普通,無需外借。③ 裁定=**borrow-design**(複用自家 `_roster_kind` 三值判)。

## 設計

### S1 守衛判斷式 kind-aware(cmd_loop_next tier↔格式一致性段)

現行(kind-blind):`eff_tier ∈ (standard, high) ∧ 非 panel 格式 → rc2`。改為:

| eff_tier | kind=code(`code-` 前綴) | kind=design 或 indeterminate |
|---|---|---|
| high | panel 格式必須(**不變**) | panel 格式必須(**不變**) |
| standard | **循序 legacy 格式=設計行為,放行**;panel 格式**照舊合法**(今日 kind-blind 守衛本就允許 standard∧panel;★r1 三席一致折入:原擬反向守衛會封死這條合法路,且它想防的「先循序後混輪」早由既有 partial-mix 守衛擋住——反向守衛整條撤除,不加★) | panel 格式必須(**不變**) |
| light | **既有** light↔panel 格式守衛不變(帶 round 即擋;★此為既有守衛,與本案已撤除的那條候選守衛同名不同物,勿混——r1 迷你核對辨義★) | 同左 |

- indeterminate(code 開頭無連字號)走嚴(=design 行,維持現行 rc2 要求 panel)——判不準就不放寬。★勿稱 fail-open(r1 三席折入):此處對 loop 是「擋」(fail-closed);roster 觀測的「跳過」對 loop 是「不擋」——兩者共享『不確定就不做假設』原則,但對 loop 的效果相反,原措辭會被讀反★。
- 守衛放寬僅此一象限(code∧standard∧無round);其餘象限回歸測試逐格釘住。**本案對任何象限零收緊**(r1 折入後成立——放寬一格、不動其餘、不加新擋)。
- `seq` 布林定義=`kind=="code" ∧ eff_tier=="standard" ∧ not panel_fmt`(**panel_fmt 排除是硬規格**,r1 折入:code+standard 的 panel 格式帳照 panel 樣式走,width 照 `_TIER_PARAMS` 的 3;零記錄 loop panel_fmt=False → 預設循序,與 skill「standard 走單 reviewer」一致)。

### S2 (code,standard) 的 width/cap 映射

- `loop next` 對 kind=code ∧ eff_tier=standard:width=1(單 reviewer,skill 設計行為)、cap=3(standard 的 cap——本案要買的正是「第 3 輪攤人」取代 legacy 的 6);min_seats 同步 1。
- `canary_type` 吐單值(同 light/legacy 樣式,非 slot dict);`record_cmd` 帶 `--tier standard`、不帶 `--round`。
- **實作落點(pre-flight 修真:單覆寫 width 不夠)**:`seq` 布林(定義見 S1,含 not panel_fmt)逐點接線——真 code 有**五個以 light/legacy 判單席樣式的分支點(各點條件式不盡相同,以逐點為準)**:①canary_type 單值/dict 分支(seq→單值)②`rmode` 帶不帶 `--round`(seq→不帶)③disposal_cmd 模板(**隨②的 rmode 自動跟動,無獨立 code 改點——列出防誤加**,r1 s1 折入)④tier_hint(**僅判 legacy,seq 不觸發**;措辭修真見 S3)⑤cluster_hint(panel 專屬,seq 排除)。**width 覆寫=1;cap 不另覆寫**(沿 `_TIER_PARAMS["standard"][1]`=3——cap 分量本來就對,另開覆寫路徑=分岔風險,r1 s3 折入);「第 3 輪攤人」語意不變。
- **canary_type 欄語意澄清(r1 外家席折入)**:該欄=植入協議停用後的歷史殘留樣式欄,只描述記帳樣板形狀,**不承載席位角色**——編制資訊(單 reviewer+外家否決)由 roster 欄承載(loop next 昨日已吐),單值不缺資訊。

### S3 編制表補列+相關文本修真

- `_TIER_ROSTER` 補 `("code","standard")`:mode=`sequential`,席=單 reviewer(claude,required,佔W)+外家否決(external,note-if-absent,note=standard 退同門+留痕)。防雙真相:mode∈(single,sequential) 佔W=1。
- [[Projects/派工編制資料化_計劃]] 範圍刀「不修 tier↔格式守衛」與「code/standard v1 不入表」段補 supersede 註記(指向本案);spec 該兩段為歷史紀錄不改寫,只加訂正行。
- `tier_hint` 措辭修真(★r1 s2 折入:原擬「邀請補標」是陷阱——補標會把帳面既有輪數**整批算進** cap=3,已跑 ≥3 筆的舊 loop 一補標下一步就 cap-reached,零輪 standard 品質審查即被逼停,比留在 legacy 更糟★):legacy 分支對 kind=code 的措辭改為**警告式**——「格式相容可補標 standard,但既有輪數整批計入 cap=3(可能當場 cap-reached);要走分級判準仍建議開新 loop id」;design loop 措辭不變。測試收口=code- 前綴 legacy loop 的 tier_hint 含「整批計入」警告字樣、design legacy loop 措辭不含。
- [[Issues/loop-next吐不可宣告的tier]] 補結案橫幅(修法+實證)。
- **skill 護欄數字修真(r1 s3 折入,本案最典型的知識同步散落格)**:`skills/lumos-code-loop/SKILL.md` 護欄「cap＝6 筆(循序)/3 輪(panel)」→「cap=6 筆(循序無定錨 legacy)/3 筆(錨定 standard 循序)/3 輪(panel)」——不改=skill 教 6、系統第 3 輪停,同一件事兩個答案。
- **code 註解修真(r1 s1 折入)**:scripts/lumos `_TIER_ROSTER` 定義正上方「code/standard(循序)v1 刻意不入表」註解,補列後即假話,同 diff 改掉。
- 循序 loop 無 dispatch manifest 慣例 → `loop status --roster` 對其多為「無派工快照可對帳」vacuous——誠實現狀,不在本案發明新留痕。

### 範圍刀(明確不做)

- 不動 high 任何行為、不動 design/standard、不動 light、不動收斂閘判定式(`--gate`/`--disposal`/`--panel`)。
- 不做舊帳回溯改寫(三個受害 loop 的 tier=None 維持史實;補標與否留人)。
- 不為循序模式發明 dispatch manifest 新慣例。

## 測試策略(TDD,先紅後綠)

1. `t_seq_code_std_anchor`:code- loop 首筆 record 帶 `--tier standard` 無 --round → `loop next` rc≠2;width=1、cap=3、min_seats=1;record_cmd 帶 --tier standard 且不帶 --round;canary_type 為單值。★前置斷言(翻紅釘現場):同 fixture 的 design loop 標 standard 無 round 照樣 rc2——證明守衛還活著、放行的只有 code 象限★。
2. `t_seq_code_std_panel_ok`(r1 折入反轉):code+standard 帳面帶 --round **不 rc2**、照 panel 樣式吐(canary_type 為 slot dict、record_cmd 帶 --round、width=3)——釘「零收緊」承諾。
3. 回歸格子:design/standard 無 round rc2 不變;high 無 round rc2 不變(code 與 design 皆然);indeterminate id+standard 無 round rc2(走嚴);**light 兩格(code 與 design)帶 round rc2 不變**(既有 light 守衛,補足「逐格」承諾——r1 迷你核對)。
4. `t_tier_roster_table` 更新(pre-flight 指名兩條必紅斷言):①keys 精確集合相等斷言擴為五組合 ②「無 code/standard(v1 範圍釘)」not-in 斷言**反轉**為存在斷言(v1 範圍釘由本案 supersede);逐格 mode 迴圈(else 分支驗佔W=1)天然涵蓋 sequential 不用改。`t_loop_next_roster` 補 code/standard 吐單 reviewer+否決席案。
5. cap 行為:code+standard 記 3 筆(循序)後 `loop next` → cap-reached(買到「第 3 輪攤人」)。
6. `t_seq_tier_hint_warning`:code- 前綴 legacy loop 的 tier_hint 含「整批計入」警告字樣;design legacy loop 措辭不含(S3 測試收口正式編號,r1 迷你核對補列)。

## 實務隱患

- **通用三問**:併發——守衛純讀帳判斷,無寫入。效能——判斷式 O(1),冷路徑。資源——無新開資源。
- **風險類自答**:碰**守衛面**——放寬一個 rc2 守衛的單一象限,最壞後果=放寬錯格讓 high/design 混進鬆判準;防線=回歸測試逐格釘(測試策略 3)+象限表明文。已排除:金流(無)、對外送出(無)、prod 不可逆(無——判斷式改動,git revert 即回)。
- **indeterminate 的兩難**:歷史非慣例 id 走嚴會繼續擋——刻意選擇(判不準不放寬),與 roster 一致;誤傷面=零(該兩 loop 已收案)。
- **cap 語意變更面**:code+standard 從(掉 legacy 的)6 變 3——這是本案目的非副作用;既有 legacy loop **不補標則**不受影響(無定錨仍推 legacy)。**途中補標時間線(r1 s2 折入)**:補標會使既有輪數整批計入 cap=3——tier_hint 警告式措辭即為此而設,spec 不邀請補標。

## 合約候選(收斂時複核,候選≠已標)

- 「high 恆要求 panel 格式(兩 kind 皆然)」——守衛放寬後的不變邊界。

## 審計修正紀錄

- **r1(2026-08-18,panel:3 sonnet(通才/守衛象限/整合)+Gemini Flash 外家席;收貨三道全過,外家 1 條短引句機械補長後全錨定)**:去重後 10 條,major×4/minor×6,**9 折 1 駁**。①[major,三席一致]反向守衛會封死今日合法的 code+standard 全 panel 用法,且其目標場景已由既有 partial-mix 守衛蓋住→**整條撤除**,seq 定義補 not panel_fmt,測試反轉為 panel_ok 零收緊釘。②[major]補標邀請=cap 陷阱(既有輪數整批計入 cap=3,舊 loop 一補標即 cap-reached)→tier_hint 反轉為警告式,實務隱患補時間線。③[major]skill 護欄「cap＝6 筆(循序)」漏排修真清單(知識同步散落同型)→補列。④canary_type 單值 vs 編制兩席→澄清歷史殘留樣式欄,編制由 roster 欄承載。⑤[駁回]「否決席可缺席=無否決權」——辯方反證:skill 既有能力宣告制(standard=退同門+留痕)明文如此,整合席獨立核證一致,非本案引入。⑥走嚴誤稱 fail-open(三席)→措辭改明擋/不擋相反。⑦tier_hint 兩處描述矛盾→統一「僅判 legacy」。⑧_TIER_ROSTER 上方 code 註解修真補列。⑨disposal_cmd 隨 rmode 跟動標明防誤加。⑩cap 不另覆寫(沿 _TIER_PARAMS)。
- **r1 折入迷你核對(2026-08-18,便宜席,3 命中全修,不算 loop findings)**:①light 兩格補回歸測試(兌現「逐格」)②tier_hint 警告措辭測試正式編為第 6 組③S1 表「反向守衛」同名不同物加辨義註記。
- **pre-flight(2026-08-18,機械排乾,不算 loop findings)**:3 命中全修——①實作落點補「五分支點逐點接線」(canary_type/rmode/disposal_cmd/tier_hint/cluster_hint 以 light/legacy 判樣式★各點條件式不盡相同,tier_hint 僅判 legacy——r1 修正本行原「均以 light-or-legacy」的過度概括★,單覆寫 width 兩條斷言必紅)②tier_hint 措辭改動補測試收口③t_tier_roster_table 指名兩條必紅斷言(keys 集合+not-in 反轉)。現況宣稱三條(kind-blind/零筆 standard/三受害 loop)經真帳核實為真。
