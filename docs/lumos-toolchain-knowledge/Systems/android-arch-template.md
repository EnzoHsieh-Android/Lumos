---
type: system
status: doing
created: 2026-10-30
updated: 2026-10-30
responsibility: Android 目標架構的開關資料檔(規則與 Konsist 架構測試的唯一來源)與產生器 lumos arch-template android 的設計脈絡;不管舊檔清單與畢業的判定(那是架構對齊鏡頭的事),也不管 DDD 與前端兩份照抄式範本
aliases: []
about_code:
  - scripts/templates/android-arch-target.md
  - scripts/lumos
tags:
  - type/system
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:Android 範本的規則與架構測試搬進開關資料檔、由產生器照六個開關組出,不再讓人照抄十二條再自己刪 [出處:[[Projects/Android目標架構開關與舊檔畢業_計劃]]] [因:照抄後刪了規則忘了刪對應測試、或反過來,沒有東西會抓] [不選:每個開關組合各放一份範本] [test:t_arch_template_android_all_combos]
  WHY:產生器只讀不寫,單段原文用 --print 取、由 AI 用一般寫檔工具存 [出處:[[Projects/Android目標架構開關與舊檔畢業_計劃]]] [因:採用要人先看預覽再存;new-only 的舊檔清單採用後不能重產,lumos 自己寫檔會在換開關時把它蓋掉] [test:t_arch_template_android_scope_and_print]
  PITFALL:產出的 Konsist 架構測試在工具鏈 repo 裡編譯不到,Kotlin 寫錯或 Konsist API 用錯,這裡的測試全綠也看不出來 [出處:2026-10-30 實作] [根因:工具鏈 repo 沒有 Kotlin 與 Gradle 建置環境,測試只比對產出文字] [repro:在 macrobench-lab 用產生器產出架構測試後跑 Gradle 單元測試]
  SEE:[[Systems/arch-alignment-lens]]
verified_by:
  - "[[Verification/2026-10-30_Android產生器在示範專案實跑]]"
---
# android-arch-template

> 白話:Android 專案採用「MVVM 加 DDD」目標架構時,AI 先問人六個架構選擇,再用產生器 `lumos arch-template android` 照答案組出規則節點、`arch_targets` 宣告、舊檔清單與 Konsist 架構測試。規則與測試的原文都放在 `scripts/templates/android-arch-target.md` 這支開關資料檔裡,每塊標「哪些開關選項才收」;這篇講這支檔與產生器為什麼長這樣。訪談題目與採用步驟在技能文件 `target-arch-android-template.md`,宣告、舊檔清單與畢業怎麼判在 [[Systems/arch-alignment-lens]]。

## 開關資料檔的形狀

- 每塊從一行 `=== <種類> <條件> [convention]` 開始:種類分節點框架、規則行、測試檔框架、單支測試;條件是 `*` 或 `開關=選項`(多個用逗號,全部成立才收)。開關或選項寫錯字,產生器整份拒絕,不會靜默變成「永遠不收」。
- 同名的兩支測試(例:用例測試在 `interfaces=deep` 與 `always` 各一版)條件要互斥;同一組開關收進兩支同名測試,產生器拒絕。
- 規則數是 9 條共通、`ddd=full` 多 3 條聚合類、`modules=multi` 多 1 條模組依賴;其餘開關只換寫法不增減。`ddd=lite` 的規則行一個「聚合」字都不留。
- 一條規則只綁一支測試(提交時「一行綁兩支」會被提醒):domain 純 Kotlin 綁 Android 匯入那支,分層那支綁 Repository 介面在 domain、實作在 data 那條(分層測試守的正是這個依賴方向)。
- 佔位字一次掃描替換,資料檔多了產生器不認得的佔位字就拒絕,不讓 `{{X}}` 原樣漏進產出。

## 產生器

- 讀資料檔照既有範本的讀法:專案自己的那份優先,退回工具安裝樹;找不到就提示跑一次 `lumos update`(資料檔登記在工具自帶檔清單裡,`lumos update` 才發得到消費專案)。
- `--scope` 的每道檢查都是為了讓宣告跟架構測試的範圍一致:宣告用樣式比對、測試用路徑前綴比對,萬用字元、`.`、`..`、空段在兩邊意思不同,所以一律拒絕;產出的宣告再交給讀宣告的同一支函式讀一次,條數不同就拒絕。
- 產生器照步驟拆成幾支小函式(參數、範圍、宣告回讀、舊檔清單、讀資料檔組裝、預覽),主函式只串流程:推送前的新增告警閘照專案的 ruff 設定擋複雜度超過 10 的新函式。
- 舊檔清單收範圍內「架構對齊會拿來審」或「架構測試會掃」的每支檔:前者跟分目標節點用同一支判定(含 xml、gradle 腳本、圖片、androidTest 與 testFixtures),後者是不在 Konsist 測試原始碼集裡的 .kt(Konsist 0.17.3 取路徑第一個 /src/ 之後那段當原始碼集名稱——沒有 /src/ 時是空字串——再取第一個冒號之後、轉小寫含 test 就是測試,反組譯查證;lumos 這邊照同一個算法寫,簡化寫法在多個 src/ 段、沒有 src/ 段、多個冒號時判法不同,代碼審 r3、r4 各抓到一次)。兩邊有一邊會看就收:清單漏收的舊檔,採用後一碰就照目標審或讓架構測試紅,跟「舊檔照鄰居」相反。代碼審 r1 抓到原本自訂排除漏了 androidTest,r2 抓到只照架構對齊又漏了 src/main 底下路徑有 test/ 段的正式 .kt。檔名含雙引號、反斜線或控制字元時拒絕:架構測試那邊只認沒有跳脫的字串。

## 架構測試的範圍判斷

- 測試往上找含 `.lumos/config.json` 的資料夾當 repo 根,把每支 Kotlin 檔換成相對根的路徑(範圍目錄寫成 Kotlin 字串時 `$` 要跳脫,不然被當字串樣板),落在 `scopeDirs` 底下(以斜線為界)、又不在舊檔清單上才檢查;兩邊比對前都轉 NFC,跟 lumos 這邊讀舊檔清單的比法一致。
- 聚合根名單照全部正式程式算:範圍外或舊檔裡的聚合根被新檔直接持有,一樣要抓。
- 讀舊檔清單不加 JSON 函式庫,用兩條正規式:只認產生器寫得出的形狀(只有 files 一個欄位、字串沒有跳脫與控制字元、逗號照 JSON、開頭可以有 BOM),比 lumos 的標準 JSON 讀法嚴、不會比它寬——lumos 讀得懂而這裡不認時測試紅並說明。正規式只用 Java 與 Python 同義的語法,工具鏈測試把原文抽出來在 Python 逐案比對;但「語法同義」不等於「行為同義」:Java 的 `$` 會停在 U+2028 這類行終止符前面(改用 `\A`、`\z`),Java 對一般的重複群組逐次遞迴、清單兩千多條就堆疊溢位(改用佔有式 `*+`),這兩件 Python 都看不到——所以測試在有能用的 java(11 以上)的機器上另用真的 Java 跑同一批輸入加 5 萬條的清單(代碼審 r2、r3 抓到的);沒有就印一行「這次沒驗到」,CI 的 ubuntu 有 java。檔不存在或形狀不認就讓測試紅,不靜默當成空清單。

REVISIT:2027-01-31 翻 git log 看開關資料檔的 Konsist 那幾塊這段期間改過沒有;改過就在 macrobench-lab 重新產出架構測試跑一次 Gradle 單元測試,確認編譯得過、改壞的樣本照樣紅
