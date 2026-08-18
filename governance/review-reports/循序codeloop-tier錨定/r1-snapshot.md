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
| standard | **循序 legacy 格式=設計行為,放行**;帳面反帶 --round(panel 格式)→ rc2 格式衝突(鏡像 light 的反向守衛) | panel 格式必須(**不變**) |
| light | 反向守衛不變(帶 round 即擋) | 同左 |

- indeterminate(code 開頭無連字號)走嚴(=design 行),與 roster 的 fail-open 跳過方向一致:判不準就不放寬。
- 守衛放寬僅此一象限(code∧standard∧無round);其餘象限回歸測試逐格釘住。

### S2 (code,standard) 的 width/cap 映射

- `loop next` 對 kind=code ∧ eff_tier=standard:width=1(單 reviewer,skill 設計行為)、cap=3(standard 的 cap——本案要買的正是「第 3 輪攤人」取代 legacy 的 6);min_seats 同步 1。
- `canary_type` 吐單值(同 light/legacy 樣式,非 slot dict);`record_cmd` 帶 `--tier standard`、不帶 `--round`。
- **實作落點(pre-flight 修真:單覆寫 width 不夠)**:引入 `seq = (kind=="code" ∧ eff_tier=="standard")` 布林,逐點接線——真 code 有**五個分支點**用 `light or eff_tier=="legacy"` 判單席樣式,seq 須逐點納入:①canary_type 單值/dict 分支(seq→單值)②`rmode` 帶不帶 `--round`(seq→不帶)③disposal_cmd 模板(seq→無 --round)④tier_hint(**維持 legacy-only,seq 不觸發**)⑤cluster_hint(panel 專屬,seq 排除)。width/cap 覆寫=(1,3) 另做;`_TIER_PARAMS` 本體不動(仍是 panel 寬度單源)。

### S3 編制表補列+相關文本修真

- `_TIER_ROSTER` 補 `("code","standard")`:mode=`sequential`,席=單 reviewer(claude,required,佔W)+外家否決(external,note-if-absent,note=standard 退同門+留痕)。防雙真相:mode∈(single,sequential) 佔W=1。
- [[Projects/派工編制資料化_計劃]] 範圍刀「不修 tier↔格式守衛」與「code/standard v1 不入表」段補 supersede 註記(指向本案);spec 該兩段為歷史紀錄不改寫,只加訂正行。
- `tier_hint` 措辭修真:code 循序 loop 修後可補標 standard(格式相容),legacy 分支對 kind=code 的措辭同步改;design loop 措辭不變。測試收口=新斷言:code- 前綴 legacy loop 的 tier_hint 含「可補標 standard」、design legacy loop 措辭不含(既有 t_loop_next_legacy_emits_a_command_that_actually_runs 鎖 design 舊措辭,不動)。
- [[Issues/loop-next吐不可宣告的tier]] 補結案橫幅(修法+實證)。
- 循序 loop 無 dispatch manifest 慣例 → `loop status --roster` 對其多為「無派工快照可對帳」vacuous——誠實現狀,不在本案發明新留痕。

### 範圍刀(明確不做)

- 不動 high 任何行為、不動 design/standard、不動 light、不動收斂閘判定式(`--gate`/`--disposal`/`--panel`)。
- 不做舊帳回溯改寫(三個受害 loop 的 tier=None 維持史實;補標與否留人)。
- 不為循序模式發明 dispatch manifest 新慣例。

## 測試策略(TDD,先紅後綠)

1. `t_seq_code_std_anchor`:code- loop 首筆 record 帶 `--tier standard` 無 --round → `loop next` rc≠2;width=1、cap=3、min_seats=1;record_cmd 帶 --tier standard 且不帶 --round;canary_type 為單值。★前置斷言(翻紅釘現場):同 fixture 的 design loop 標 standard 無 round 照樣 rc2——證明守衛還活著、放行的只有 code 象限★。
2. `t_seq_code_std_panel_conflict`:code+standard 帳面帶 --round → rc2 格式衝突(反向守衛)。
3. 回歸格子:design/standard 無 round rc2 不變;high 無 round rc2 不變(code 與 design 皆然);indeterminate id+standard 無 round rc2(走嚴)。
4. `t_tier_roster_table` 更新(pre-flight 指名兩條必紅斷言):①keys 精確集合相等斷言擴為五組合 ②「無 code/standard(v1 範圍釘)」not-in 斷言**反轉**為存在斷言(v1 範圍釘由本案 supersede);逐格 mode 迴圈(else 分支驗佔W=1)天然涵蓋 sequential 不用改。`t_loop_next_roster` 補 code/standard 吐單 reviewer+否決席案。
5. cap 行為:code+standard 記 3 筆(循序)後 `loop next` → cap-reached(買到「第 3 輪攤人」)。

## 實務隱患

- **通用三問**:併發——守衛純讀帳判斷,無寫入。效能——判斷式 O(1),冷路徑。資源——無新開資源。
- **風險類自答**:碰**守衛面**——放寬一個 rc2 守衛的單一象限,最壞後果=放寬錯格讓 high/design 混進鬆判準;防線=回歸測試逐格釘(測試策略 3)+象限表明文。已排除:金流(無)、對外送出(無)、prod 不可逆(無——判斷式改動,git revert 即回)。
- **indeterminate 的兩難**:歷史非慣例 id 走嚴會繼續擋——刻意選擇(判不準不放寬),與 roster 一致;誤傷面=零(該兩 loop 已收案)。
- **cap 語意變更面**:code+standard 從(掉 legacy 的)6 變 3——這是本案目的非副作用;既有 legacy loop 不受影響(無定錨仍推 legacy)。

## 合約候選(收斂時複核,候選≠已標)

- 「high 恆要求 panel 格式(兩 kind 皆然)」——守衛放寬後的不變邊界。

## 審計修正紀錄

- **pre-flight(2026-08-18,機械排乾,不算 loop findings)**:3 命中全修——①實作落點補「五分支點逐點接線」(canary_type/rmode/disposal_cmd/tier_hint/cluster_hint 均以 light-or-legacy 判樣式,單覆寫 width 兩條斷言必紅)②tier_hint 措辭改動補測試收口③t_tier_roster_table 指名兩條必紅斷言(keys 集合+not-in 反轉)。現況宣稱三條(kind-blind/零筆 standard/三受害 loop)經真帳核實為真。
