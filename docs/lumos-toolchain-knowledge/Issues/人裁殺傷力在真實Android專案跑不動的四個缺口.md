---
type: issue
status: open
created: 2026-11-13
updated: 2026-11-13
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - scope/stack-knowledge
summary: |-
  FLAG:TECHNICAL
  PITFALL:人裁把 flatMapLatest 換成 flatMapConcat 驗殺傷力時,換完編譯不過(檔頭只 import 了 flatMapLatest),判成弱證據而拒絕寫回 [出處:2026-11-13 測試品質實驗室 Android 副本實跑 lumos situation-rule] [根因:壞法只能改段內一處字串,碰不到檔頭 import] [repro:副本裡 import 逐一寫明時跑 situation-rule --old flatMapLatest --new flatMapConcat,判 killed_unattributed]
---
# 人裁殺傷力在真實Android專案跑不動的四個缺口

背景:[[Projects/情境題答案要引規格出處與回寫循環_計劃]] 上線後,2026-11-13 第一次在真的 Gradle 專案跑完整循環(測試品質實驗室 Android 子專案的暫存副本,搜尋框 `flatMapLatest` 加兩支測試、計劃不寫「只顯示最後一次」)。循環本身走通:只送一次值的測試判 survived 被拒、連送兩次的判 killed 寫回 S2、規格閘認得人裁條款。下面四件是實驗室假平台測不出、真專案才冒出來的。

## 症狀

1. **(最優先)換運算子的壞法編譯不過。** `--old flatMapLatest {…}` / `--new flatMapConcat {…}` 只換那一行;檔頭逐一寫的 `import kotlinx.coroutines.flow.flatMapLatest` 沒跟著換,壞法版編譯失敗 → `killed_unattributed`(弱證據)→ 人裁拒絕。Android 專案多半逐一寫 import,所以面試題那種情境照常操作就走不通。實跑時把 import 改成 `kotlinx.coroutines.flow.*` 才繞過。
2. **`lumos init` 給 Android 猜的 run_cmd 是壞的**:`./gradlew test --tests '*{method}'`,Android 的 `test` 是總任務、不收 `--tests`(Gradle 報 Unknown command-line option),要 `:app:testDebugUnitTest --tests …`。新接入的 Android 專案殺傷力全部跑不起來。
3. **人裁指令的錯誤訊息指向不存在的旗標**:算不出主線分岔點時印「用 --diff <A..B> 指定」,但 `situation-rule` 沒有 `--diff`(只有 `--branch`)。
4. **殺傷力帳本沒留輸出摘錄**:判 `killed_unattributed` 時 kill-log 的 tail 是空的,看不出是編譯失敗,要自己開工作樹重跑才查得到。

## 根因

1:宣告式壞法只能改段內恰好一處字串(範圍 4 刻意限定在這一段、同一列),import 在段外。2:init 依副檔名猜 kotlin-junit 範本,沒分 Android 與純 JVM。3:錯誤訊息沿用 code-loop 的說法。4:人裁的 kill-log 那筆沒帶執行器輸出。

## 現在怎麼繞

1:被測檔改用整包 import(`kotlinx.coroutines.flow.*`)。2:手改 `.lumos/config.json` 的 run_cmd 成 `./gradlew :app:testDebugUnitTest --tests '*{method}'`。3:在有主線分支的工作樹跑,或帶 `--branch`。4:手動 `git worktree add` 那個版本重跑綁定測試看輸出。

## 什麼條件算修好

- 1:換運算子的人裁在逐一 import 的 Android 檔上判得出 killed(可能做法:壞法允許連帶改 import、或允許多處替換但限定在同一列的觸發字;要先寫計劃、不能放寬「只改這一段」到可以任意改檔),有逐一 import 的端到端測試。
- 2:init 偵測到 Android(com.android.application / library 外掛)時給 `testDebugUnitTest` 版本的 run_cmd,有測試。
- 3:訊息改成指向 `--branch` 或補 `--diff`。
- 4:人裁那筆 kill-log 帶得出失敗原因的摘錄。
