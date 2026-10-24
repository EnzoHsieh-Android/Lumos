preflight-4: ran

# code-readme-android-e2e r3 收貨

審材:主線 17a0d393 到 f3b5876f 的完整改動 r3-snapshot.patch(316 行),加最近一次修補 r3-repair.patch(d6eeccd0 → f3b5876f,54 行)。
兩席全新:單審(sonnet,要求逐句對出處、不准整批判)、架構對齊(sonnet),都交回後才一起存檔;席報告從對話紀錄取最後一則回答原文。
引句:架構對齊全錨;單審 F2 的引句裡又包了「」被截斷、F7 引的是替代文字(程式裡分多行字串,換行位置不同),兩條錨不到;請該席只改這兩行引句重出,存成 r3-單審-sonnet-格式更正.md(原檔保留),更正版全錨。
修補因果:F1 是上一輪修補寫錯(r2 把 StrictMode 那句改成「沒打開就列成跳過」,實際只看設定檔宣告);其餘是前兩輪沒人逐句看的角落。

## 機械重現

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | major | 讀計劃第 37 行代價欄「宣告了卻沒真的開,零筆照樣判通過」與收集腳本沒宣告回 unsupported;README 寫「沒打開就列成跳過」 | HIT | 折:改成兩件事都要做(打開並宣告)、沒宣告列跳過、宣告了沒打開會被誤判成通過 |
| F2 | minor | grep:Macrobenchmark退步提醒_計劃 的 REVISIT 2026-12-21 才重訂容差;README 寫「正在用實機資料重新校正」 | HIT | 折:改成暫定值(預設 10%、下限 1 毫秒)、之後用多次實機重跑重訂 |
| F3 | minor | 讀 SKILL 版本表:skill、Perfetto、NDK 各自不同版本 | HIT | 折:改成「各自固定在一個版本」 |
| F4 | minor | 讀逐層診斷計劃 PRIOR-ART「全借用,skill 只串流程與收據」,沒有「官方沒涵蓋」的清單 | HIT | 折:改成「負責官方 skill 以外的串接」並列出要不要往下、串各層工具 |
| F5 | minor | 讀 SKILL L0 第 3 步記的是 APK 雜湊、原始檔只留本機 | HIT | 折:改成「用檔案指紋比對」、「拿到同一批原始資料重跑」、原始資料不進版控 |
| F6 | minor | 讀計劃第 21 行驅動由專案自己寫、scripts/lumos 只判門檻檔寫了 check 的項目、第一項只量原生 | HIT | 折:改主詞為專案的操作測試加收集腳本加 lumos macrobench,補「每一項要在標準檔寫一條」、第一項加「C/C++ 那一側」 |
| F7 | minor | grep 產生器:中文 L2 徽章「官方工具」、英文輸入框沒提閃退、中文替代文字還有「判人裁門檻」「盲測」「捷徑」 | HIT | 折:徽章改「Android 工具」、英文改 memory, crashes、兩版替代文字改白話 |
| F8 | minor | 讀 README:Maestro、幀、simpleperf 沒解釋,MainActivity.kt 沒說是實驗 App | HIT | 折:四處都當場補一句解釋 |
| A1 | minor | 讀 README:圖放在 details 外;地圖與 drift 兩章的圖也在外面 | HIT | 放行:專案裡兩種放法都有,章首主圖放在外面跟地圖、drift 同型 |
| A2 | minor | 讀 README.en:鄰居 summary 以 See 開頭、語言標記寫 (Chinese) | HIT | 折:改 See …、(Chinese) |
| A3 | minor | 讀 validate:swiss-cheese 有結構斷言,android-e2e 沒有 | HIT | 折:補四層順序與三個群組各一的斷言;改壞一層編號 --check 回 1 |

折 10、放行 1(A1)、駁回 0。
