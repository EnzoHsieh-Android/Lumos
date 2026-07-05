---
type: project
status: doing
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/project
  - status/doing
related:
  - "[[lumos-cli-lifecycle]]"
summary: |-
  FLAG:DECISION
  KEY:收破口——`lumos update`/`init` 從不刷新既有專案 CLAUDE.md 紀律區塊(教會 Claude 用工具的 vendored 範本改了傳不到消費端);根因三合謀:_scaffold_project 遇既有 vault 提早 return(:3654)+ 注入 create-only(:3671)+ update 在 re-vendor 範本「之前」才呼叫 scaffold(:3557 vs copy2 :3571 順序錯)
  KEY:修法=解耦——把「注入 CLAUDE.md」從「scaffold 圖譜資料」拆開;scaffold skip-if-exists 對圖譜資料是對的,錯在注入搭便車
  DECISION:再注入語意=覆蓋 sentinel 之間 + 印 diff(sentinel 外逐字保留;無變靜默;手改區塊內會被蓋但區塊本標「勿手改」,diff 讓覆蓋可見)
  DECISION:含機械漂移守衛(test + doctor Check):本 repo CLAUDE.md 區塊 == resolved template,逐字比對(內容比對 > 版本比對)
  DECISION:交付物 3 版本號=「人可讀標籤 + 粗 nudge」,嚴禁當 staleness oracle;單一源 LUMOS_VERSION → 機械蓋進 START sentinel 行(在比對區「外」,不耦合守衛)
  KEY:誠實天花板=版本號不證內容對(bump 可漏),真守衛是內容比對;--no-verify 繞得過 doctor;非 oracle
  DEP:[[lumos-cli-lifecycle]]
  TEST:待實作(design-loop 收斂前不進實作)
---
# CLAUDE 注入 re-sync 與版本標籤_計劃

> 收「vendored 教學範本(`graph-discipline.md`)改了、傳不到既有消費專案 CLAUDE.md」的破口(使用者點出「最重要的是教會 Claude 用本工具」)。設計權威節點;進實作前過 [[lumos-design-loop]] 到收斂。

## 背景:破口(三環節合謀)
`graph-discipline.md` 是注入每個消費專案 `CLAUDE.md` 的「教會 Claude 用本工具」範本。它更新後,`lumos update` 會刷新 CLI/hooks/vendored 範本檔本身,**但 CLAUDE.md 的注入區塊從不重跑**。根因:
1. `_scaffold_project`(`scripts/lumos:3652-3654`)遇既有 vault 提早 `return` → 走不到注入。
2. 注入是 create-only(`:3671` `elif SENTINEL not in cm`)→ 有 sentinel 就跳過。
3. update 路徑 `_vendor_toolchain` 在 **re-vendor 範本之前**(`:3557` 呼叫 scaffold vs copy2 `:3571`)→ 就算注入也讀到舊範本。

`Systems/lumos-cli-lifecycle` 的 KEY 已宣稱「graph-discipline.md 要重跑 init/update 才刷新」——**這是文件寫的意圖,code 沒做到**。本計劃是讓 code 對齊既有意圖(bug fix,非 spec 變更)。

## 修法核心:解耦
把「注入 CLAUDE.md」從「scaffold 圖譜資料」拆開。scaffold 的 skip-if-exists 對**圖譜資料**是對的(保護資料不被動),錯在注入搭了它的便車、繼承了 skip。

## 交付物 1:re-inject(覆蓋 + diff)
新增 `_reinject_claude_block(root, slug) -> str|None`:
- 讀**已 vendor 的**範本 → 把 `{{KG}}` 佔位符換成該專案的 knowledge 資料夾相對路徑 → strip → 包 sentinel(含交付物 3 版本戳)。
- CLAUDE.md 不存在 → 建(title + block);**兩 sentinel 齊全** → 替換之間;無 sentinel → 附加。marker 尋找複用 `_deinit_strip_claude`(prefix-based find 對版本後綴穩健)。
- **sentinel 外內容逐字保留**;`difflib.unified_diff(舊block, 新block)`:有變 → 寫 + 回 diff(呼叫端印);無變 → 不寫、回 `None`(idempotent 靜默)。

**半壞 sentinel(F-04,顯式定義,別留給實作猜)**:只 START 無 END / 只 END 無 START / END 在 START 前 / 重複出現 → **繼承 `_deinit_strip_claude:3480-3481` 的 no-op**(不覆蓋、不自動修復)。理由:半壞=使用者可能手改過(START 行本標「勿手改」),盲目覆蓋會毀狀態;no-op 保守,由交付物 2 doctor Check 報漂移交人肉裁。**回傳一個 sentinel-broken 訊號**讓呼叫端印警示(不是靜默 no-op)。

**BOM/CRLF(F-09)**:讀時 strip 前導 BOM(`﻿`)後再 find marker;寫一律走 `_write_lf`(強制 LF,同既有寫入慣例)。BOM 檔:注入後正規化為無 BOM + LF(與 T1 寫入「拒 BOM/CRLF」哲學一致)。

接線:
- `_scaffold_project` **移除**注入段(只留 vault 夾 + MOC + gitignore;其 skip-if-exists 只保護圖譜資料)。
- `_vendor_toolchain`:注入改到 **copy2 vendor 迴圈之後**呼叫(讀新範本 + 修 :3557 先於 :3567-3576 的順序錯)。
- `cmd_init`(F-06):現有 `existing and not force → return 0`(`:3759`)會**繞過** re-inject。修法:把 re-inject 提到 early-return **之前**無條件跑(re-inject 本身 idempotent+diff、對既有專案安全),或 early-return 前先呼叫;不要求使用者加 `--force` 才刷新紀律區塊。

## 交付物 2:漂移守衛(內容比對,真守衛)
- **test** `t_claude_block_matches_template`:斷言本 repo `CLAUDE.md` 兩 sentinel 之間 == `resolve(template)`。
- **doctor Check(新字母)**:`scripts/templates/graph-discipline.md` 存在 且 CLAUDE.md 有 sentinel → 區塊必 == resolved 範本,否則報漂移;`--ci` 擋。比對的是**repo 內範本↔自己 CLAUDE.md**(內部一致性,與上游新舊無關,消費專案不誤報)。
- 比對區 = 兩 sentinel「之間」,**不含 sentinel 行本身**(版本戳在 START sentinel 行,落在比對區外,故版本差不觸發內容守衛——標籤與守衛解耦)。
- **比對 slice 精確定義(F-05,免版本 bump 誤觸發)**:取 `START 行結尾 \n 之後` 到 `END 行開頭 \n 之前` 的子串,兩端各自 strip 首尾空白行後比對。單一函數 `_extract_claude_block_body(text) -> str` 同時供 re-inject 與 doctor Check 用(單一源、避免兩處 slice 取法漂移);對應測試 `t_version_bump_not_trigger_guard`(START 行改版本 → body slice 不變 → 守衛淨)。
- **遷移零時點(F-02,辯方已證非災難,但寫明預期)**:doctor Check 與 re-inject **同批經一次 `lumos update` 送達**(同 `_vendor_toolchain`;re-inject 在該次 update 內先跑)→ 消費專案「有了新 check」時必已 re-inject,無「有 check 未同步」窗口。唯一會報的情形=真漂移(如半壞 sentinel 導致 re-inject no-op),語意正確、非誤報。

## 交付物 3:版本標籤 + 粗 nudge(嚴禁當守衛)
**新增常數** `LUMOS_VERSION`(`scripts/lumos` 頂部,目前 code 中**不存在、本計劃新建**;release 手動 bump,允許粗——它是標籤,不是內容指紋)。

- **機械蓋**:vendor/inject 時把版本寫進 START sentinel 行(`<!-- LUMOS:GRAPH-DISCIPLINE:START vX.Y — ... -->`),**絕不手打**;讀取 = 對 START 行以空格切分取 `vX.Y` 欄位(parse 容錯:取不到版本 → 視為未知、不 nudge、不 crash)。
- **跨邊界 nudge**:`lumos update` / doctor soft check 比對「消費專案 sentinel 蓋的版本 vs 來源 clone 的 `LUMOS_VERSION`」→ 落後則 soft 提示(update 本身順手刷新;nudge 主要給 doctor/獨立可見性)。
- **F-03 定位澄清(消除「nudge 用版本落後 vs 版本非判準」的表面矛盾)**:版本與內容比對答**兩個不同問題**,不衝突——
  - **「你在不在最新 release?」**→ 版本比對,**粗、advisory、不擋**(nudge)。它是提醒「也許該更新」,**不是**「你的區塊此刻正確與否」的裁決。
  - **「你的 CLAUDE.md 區塊內容 == 你自己的範本嗎?」**→ 內容比對(交付物 2),**精確、擋(--ci)**,這才是正確性守衛。
  - 所以版本號**永不**回答正確性問題;它只回答「哪個 release」。版本落後 ≠ 內容不一致(update 後兩者一致但版本仍可能落後上游一個 tag)。版本可與內容差一格而不算 breaking——因為它從不被當正確性 oracle。

## 誠實天花板
- 版本號「有=那版」是假命題(bump 可漏)→ 只當人可讀標籤 + 粗 nudge,真守衛是內容比對(同「有寫下 undo ≠ 驗過能跑」)。
- doctor 那道 `--no-verify` 繞得過;覆蓋語意會蓋掉手改區塊內容(但標「勿手改」+ diff 可見)。非 oracle:守得掉「範本改了沒傳到」「repo 內漂移」,守不掉「刻意繞 + 手改還不看 diff」。

## 測試(TDD)
- 核心:`t_reinject_updates_existing` / `_idempotent` / `_creates_when_absent` / `_appends_when_no_sentinel` / `_preserves_outside` / `t_update_resyncs_claude`(整合)。
- 半壞 sentinel(F-07):`t_reinject_only_start_no_end` / `_only_end_no_start` / `_end_before_start` / `_duplicate_sentinel` —— 皆斷言 no-op + 回 sentinel-broken 訊號、原檔不動。
- BOM/CRLF(F-09):`t_reinject_bom_crlf_normalized`。
- 守衛:`t_claude_block_matches_template`(本 repo 區塊==範本)/ doctor check 測試(漂移報、同步淨)/ `t_version_bump_not_trigger_guard`(F-05:START 版本改、body 不變 → 守衛淨)。
- 版本:`t_version_stamped_in_sentinel`(機械蓋)/ `t_version_parse_tolerant`(取不到版本不 crash)/ `t_version_nudge_when_behind`(粗 nudge)。

## 落地回填
- Verification `plan_refs` 回指本節點;本節點 TEST/status。
- 更新 `Systems/lumos-cli-lifecycle`(F-10,附 KEY 草稿):
  - 改既有 KEY「graph-discipline.md 要重跑 init/update 才刷新」→ 標明**現已成真**且注入與 vault-scaffold 已解耦(re-inject 無條件跑、不受既有 vault skip 影響)。
  - 新增 `KEY:re-inject 覆蓋 sentinel 之間、sentinel 外逐字保留;半壞 sentinel→no-op 由 doctor 報漂移`(判斷是否合約級:此為 breaking-若違反的行為保證 → 評估標 ★INVARIANT★ 並綁 `[test:t_reinject_preserves_outside]`,經 `[audit:]`)。
  - 新增 `KEY:版本戳=標籤非守衛,內容比對才是正確性守衛`(★DEBT★ 或純 KEY,非合約)。
