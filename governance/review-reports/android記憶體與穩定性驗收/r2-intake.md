preflight-4: ran

# android記憶體與穩定性驗收 r2 收貨

審材 r2-snapshot.md(121 行,LUMOS-SPEC 0cd4d964);四席全新 sonnet:通才、邊界可執行、整合、架構對齊;派工詞第三行寫明不准讀 governance/review-reports 其他檔。四席交回後才一起從逐字稿存檔。邊界可執行席有一行用 report-normalize --write 純格式搬移。quote-check:通才席第 7 條引句不到 10 字錨不到,同一件事邊界可執行席第 7 條引句完整、獨立報到,照樣處理;其餘全錨。
前掃(r2 是修訂輪,沿用 r1 的前掃;r1 前掃之後的改寫由本輪四席全新審)。

## 編排者重現

- 兩次 am instrument 會重啟目標 App(G1、B3、I2):三席引 source.android.com/docs/core/tests/development/instrumentation 與 AOSP --no-restart 那筆變更;實驗室 spike 是從主機用 am start 加 BACK 驅動,沒有用 instrumentation,不能反證 → 採信(HIT,依官方文件)。
- 不存在的套件 exit-info 只印兩行全域標頭(B2):席位唯讀實測;編排者在 r1 實驗時看過 com.example.mblab 的完整輸出格式 → HIT。
- 實機 exit-info 有 USER REQUESTED、FORCE STOP、KILL BACKGROUND 等非崩潰原因(B1、G12):編排者 r1 實驗輸出第二筆就是 reason=10 USER REQUESTED、subreason=21 FORCE STOP → HIT。
- results_dirs 必填(G3、I1、A3):讀 scripts/lumos 的 _macrobench_config,沒有非空 results_dirs 回錯誤 → HIT。
- REVISIT when-file 語意(G4):讀 lumos-project-notes commands/03 的 when-file 定義,樹上有那個路徑就成立 → HIT。
- skill 的 java_heap_dump(A1):讀 skills/lumos-android-evidence/SKILL.md 的 L3 段,用 java_heap_dump 錄快照 → HIT。
- 其餘條目是讀計劃本文與既有程式即可判的缺漏 → 逐條讀過,HIT。

## 根因分組與統一修法

- 行程被殺(G1、I2、I3、G13 的 Maestro 部分):驅動規範改成「UI Automator 要自己測自己、Maestro flow 不停 App、輪數用 -e、從約定起點開始」;收集腳本三次讀 pid。子案二不再說「只要換驅動指令」,改成照驅動規範寫 flow。
- 讀不到當成沒事(G2、G5、G6 數字部分、B2、B3、B4、B5、I6、A4 的回傳碼):統一規則——每個來源分得出「收到了、是零」與「沒收到」;driver 也是一個來源;類別兩份都不在列跳過;幀數 0 列跳過;零筆歷史是 ok、沒有全域標頭才 failed;數字一律走只收有限數。
- 結束紀錄原因(B1、G12):只有五種判不過,其他回報。
- 日誌(G5、B5):串流這個 pid 的日誌,不清共用緩衝,串流中斷記 failed。
- 欄位與設定(G6、B6、I1、I7、A3、A5):七種 check 各自欄位寫成表;scenario 要等於結果檔;device_model 照舊;W、N 至少 1;stability 段在時 results_dirs 可不填;實例上限只宣告在門檻檔;--stability 吃路徑的理由寫明。
- 原生基線(G7、B7):暖機後也掃,判差值。
- 架構(A1、A2、A6、A7、I5):快照沿用 java_heap_dump;收集腳本是第一支接裝置的範本(照實寫);L3 手動快照同檔名同刪除;另開家節點 Systems/android-stability-collector;收集腳本寫明 sh 外殼包 python3、python 逾時、回傳碼 0/2。
- 其他(G4、G8、G9、G10、G11、G14、B8、B9、B10、I4、I8):REVISIT 改日期型;Java 增長預設排除平台型別;保存宣告帶署名日期、裝置暫存刪、代價寫明;查詢測試照 Perfetto 文件建表並由實驗室人工驗收證明真跑;只存有增減與宣告的類別、逾時可調;官方分級表邊界席已另讀核對一致;同名類別加總;遊戲欄用 category;錄製上限與停止方式;統計化計劃補第 6 條。

## 逐條去向

全部 39 條折入計劃 r3 版:G1–G14、B1–B10、I1–I8、A1–A7。沒有放行、沒有不成立。

| id | 嚴重度 | id | 嚴重度 | id | 嚴重度 | id | 嚴重度 |
|---|---|---|---|---|---|---|---|
| G1 | major | B1 | major | I1 | major | A1 | major |
| G2 | major | B2 | major | I2 | major | A2 | minor |
| G3 | major | B3 | major | I3 | major | A3 | minor |
| G4 | major | B4 | major | I4 | major | A4 | minor |
| G5 | major | B5 | major | I5 | minor | A5 | minor |
| G6 | major | B6 | minor | I6 | minor | A6 | minor |
| G7 | minor | B7 | minor | I7 | minor | A7 | minor |
| G8 | minor | B8 | minor | I8 | minor | | |
| G9 | minor | B9 | minor | | | | |
| G10 | minor | B10 | minor | | | | |
| G11 | minor | | | | | | |
| G12 | minor | | | | | | |
| G13 | minor | | | | | | |
| G14 | minor | | | | | | |

## 修補因果

regression_set:G4(r1 修補新增的 REVISIT when-file 寫錯語意)、A1(r1 改寫新增 java_hprof 自己的錄法)、I3(r1 改寫寫進「子案二只要換驅動指令」)、B2(r1 改寫新增「解析不到時 status 是 failed」沒區分零筆)、G6 的 NaN 部分(r1 新增 check 判定路徑沒走有限數檢查);其餘屬 r1 改寫後才浮現的原有缺口或新段落自帶的未查證宣稱。
