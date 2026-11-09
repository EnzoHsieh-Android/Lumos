severity: minor

這份 diff 大致沿用型錄原有的做法。內容放的位置都對。主要偏差是三處寫法不一致,另有一處驗證紀錄欄位不齊。沒有引入新的欄位或新的判定值。

## 1. 分層與依賴方向
放置都對:
- 型錄改寫只動 `skills/kotlin-idioms/checks-catalog.md` 的主表、〈待查證〉、〈接電證據〉、〈統計〉。
- 三支樣本放在既有的 `configs/ast-grep/kotlin-android/samples/lint-wiring/`,副檔名 `.kt.txt`,跟既有 UI-16 等一致。
- 逐列核對的過程與結論放 `Verification/`。
- 一條 WHY 放家筆記 `Systems/kotlin規則包`,並補進 `verified_by`。這條 WHY 的內容是「型錄現成規則欄要實跑或有原文」,屬於這份型錄的家。
- `scripts/test_lumos.py` 的統計錨點與改壞範例跟著新數值一起改。這跟 `_KT_STATS_LINES` 既有的做法一致。

唯一的層級小問題是 A3(驗證紀錄的欄位)。

## 2. 命名與寫法
A1、A2 是現成規則欄與通電批次欄的寫法,A3 是驗證紀錄的欄位,A4 是來源欄。
- 接電證據新增 6 列的欄位、理由寫法、`〔真跑 日期:樣本檔〕` 都跟既有列一致。
- 統計行與 WHY 行的形狀(出處、因、不選)也一致。
- 兩處沿用既有做法,不算偏差。UI-61 標(出處不全)沿用 UI-103、TEST-31 的先例(查到跟官方相反就維持出處不全)。拿掉 TEST-12 的出處不全也合口徑。

## 3. 第二種做法
- 接電證據沒有新判定值,仍是「擋得到」「擋不到」,級別沿用 Error、Warning、Hint、detekt。
- 現成規則欄出現兩種新寫法:一是 `無:原因` 與 `無現成規則;…`、`無現成 Kotlin 規則:…` 這類冒號和前綴變體,二是 `X 不列:原因`。見 A1、A2。

## 發現

A1. 「無」的寫法有第二種
severity: minor
blocking: 否
引句:「無:Android 官方 custom-modifiers 頁明寫可以用 composable modifier factory」
- 既有「現成規則=無」的寫法是裸 `無`(基準版 221 次),或 `無(原因)`(基準版 33 次)。`無:` 在基準版 0 次。
- 這份 diff 用了三種變體:`無:`(UI-47、UI-61、DATA-18、DATA-30、PERF-9)、`無現成規則:` 或 `;`(ARCH-49、DATA-24、DATA-43、DATA-71、PERF-23)、`無現成 Kotlin 規則:`(TEST-27)。
- 全部改成 `無(原因)` 就跟 API-14 對齊了。
- file: `skills/kotlin-idioms/checks-catalog.md:166`(API-14 的 `無(IntelliJ 有 Redundant 'async' call 檢查…)`)

A2. UI-61 的通電批次沒跟著現成規則改
severity: minor
blocking: 否
引句:「| 告警帶寫法 | 告警帶寫法=批四(現成規則) | 未測 | CMP-API〔併:研M五8〕」
- UI-61 的現成規則改成「無」並標(出處不全),通電批次卻仍寫「批四(現成規則)」。
- 同樣「現成規則=無、出處不全」的既有列(API-14、UI-103)都寫「告警帶寫法=未接(還沒有規則)」。
- 批四在〈輸入與口徑〉的定義是現成規則消費專案接 CI 後才擋。現在這列沒有規則,通電批次欄會誤導。
- file: `skills/kotlin-idioms/checks-catalog.md:430`(UI-103)
- 小註:UI-61 的級仍是 A+B,API-14 也是,屬先例,不算偏差。⚠ 我沒有確認自檢會不會抓這種「批四但現成規則=無」的組合。

A3. 驗證紀錄的欄位不如鄰居齊
severity: minor
blocking: 否
引句:「plan_refs:
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"」
- 鄰居驗證紀錄 `2026-11-09_Android現成檢查範本在兩個公開專案實跑` 同時寫 `plan_refs` 與 `system_refs`。
- 這篇只有 `plan_refs`,沒有 `system_refs`(家 `Systems/kotlin規則包`)。
- 型錄的逐列查證卷證是 `Projects/Android寫法型錄逐列查證_計劃`(型錄〈統計〉寫的),這篇的 `plan_refs` 卻指向別的計劃。⚠ 我沒有讀過那篇計劃,不確定哪個才是這次核對的計劃。
- file: `docs/lumos-toolchain-knowledge/Verification/2026-11-09_Android現成檢查範本在兩個公開專案實跑.md:12-15`

A4. 來源欄的查證標記有一半沒補
severity: minor
blocking: 否
引句:「來源欄補〔查證 2026-11-09:網址〕」
- 這句是驗證紀錄的聲稱(引句抄自 patch)。
- patch 改寫的 47 個主表列裡,來源欄有 `〔查證 2026-11-09:…〕` 的只有 25 列。
- 其餘 22 列沒有,例如 CO-2、STATE-4、STATE-5、UI-3、UI-98、ARCH-4、ARCH-28、DATA-15。它們把「2026-11-09 讀…」寫在現成規則欄內文,來源欄沒網址。
- 做法有兩種(欄內日期、來源欄標記),不是型錄原本的單一慣例。〈統計〉的「逐列查證」計數只算來源欄標記,這 22 列不會進去。
- file: `skills/kotlin-idioms/checks-catalog.md:279`(CO-1 來源欄的 `〔查證 日期:網址〕` 形式)

A5. 「不列:原因」是新句式
severity: minor
blocking: 否
引句:「Slack lint 的 RawDispatchersUse 不列:它是 slack-lints 專用」
- 基準版 `不列` 0 次。型錄原本沒有在現成規則欄裡逐條交代「為何不採用某候選」的句式。
- 基準版處理不涵蓋的辦法是直接寫「查不到實作」(API-2)或在括號寫範圍(API-14)。
- 新句式出現 7 次:CO-1、CO-2 等。內容有價值,但是一種新慣例。
- 另外,同一格內 Slack 的標籤也變了:舊寫法是 `Slack lint:RawDispatchersUse`,新寫法是 `Slack lint 的 RawDispatchersUse`。
- ⚠ 這條屬邊界:不列的原因是必要資訊,可以接受,但建議在〈輸入與口徑〉補一句寫法。
- file: `skills/kotlin-idioms/checks-catalog.md:15`

不對齊共 5 條,其中 major 0 條
