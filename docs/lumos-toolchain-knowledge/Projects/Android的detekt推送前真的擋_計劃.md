---
type: project
status: todo
created: 2026-11-04
updated: 2026-11-04
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
related:
  - "[[Issues/推送閘對Android的detekt只記錄不擋]]"
  - "[[Projects/Android的detekt規則說實話_計劃]]"
  - "[[Projects/detekt協程規則真的在跑_計劃]]"
  - "[[Systems/pitfalls-lint-adapter]]"
lands_in:
  - Systems/pitfalls-lint-adapter
---
# Android的detekt推送前真的擋_計劃

> 白話:Android 專案的 detekt 告警現在推送前從來不擋(見 [[Issues/推送閘對Android的detekt只記錄不擋]])。這案要讓它真的擋:新寫進去的協程錯誤,推送時被攔下。立案筆記;動手前要走完整設計審(會改到推送閘)。

## 要解的三件事

1. **多檔怎麼交給 detekt**:新增告警檢查把要檢查的檔用空白串起來,detekt 只收逗號分隔。候選:在唯一那支替換函式裡依工具決定串法,或宣告檔另給一種逗號串的佔位符。兩種都要過「全程式只准一處替換佔位符」那條守衛。
2. **型別資訊從哪來**:Android 專案的依賴 jar 散在 Gradle 快取、路徑帶雜湊,手寫 `--classpath` 走不通;Gradle 的 `detekt<Variant>` 任務自帶型別,但它在推送檢查的兩份快照目錄裡跑不起來(要整個專案能建置)。候選:讓專案用一個 Gradle 任務把 classpath 寫進檔案,宣告裡讀那個檔。
3. **怎麼證明規則真的在跑**:沿用已作廢那案([[Projects/detekt協程規則真的在跑_計劃]])的探針想法,但要先解決它第一輪審查列出的判定細節(規則名帶前綴、探針沒產出結果的第三種狀態、沒用協程函式庫的專案誤判、詞法判定)。卷證在 governance/review-reports 底下 detekt協程規則真的在跑 資料夾。

REVISIT:2026-11-30 說實話那案推上去之後,回來寫這篇的設計並開設計審;到期還沒動就寫明延後理由。
