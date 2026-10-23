preflight-4: ran

# code-android-ui-kind r1 收貨

審材:r1-snapshot.patch(566 行,2bdefa2da714976d1bfa9f0c15e9e55066682e71..f96ffe70e8efbd2c9e5a5bfb52ec8ac028e9c148,sha256 前 16 碼 775413c6a43bcf9b);pitfalls 清單 r1-manifest.json(原 3571 條,只留內建隱患題與落在這次改動行上的 lint,剩 5 條)。
七席全新、同輪派出:正確性、資源、邊界、整合、通才(§7.9 八角度)、架構對齊、資安,全部 sonnet;七席都交回後才一起存檔(從各席逐字稿取原文,不用完成通知的轉跳脫版)。
六席報告最後一行寫「max severity: X」(派工詞照範本 §3 要求「最後一行總結 max severity」,收貨工具不收這種寫法),請該席只改那一行,存成 r1-<席>-格式更正.md 當載體;原檔保留,逐行比對只差最後一行。架構對齊席原檔已是正規化格式。
七份報告的引句全數錨定(quote-check);refcheck 有幾處行號超出檔案長度,是席位把凍結 patch 的行號寫成原檔行號,引句都錨得到,不影響採信。
repo 收貨時 git status 只有我自己的帳本與卷證,審查席沒有改到 repo。邊界席、正確性席、整合席各刪了自己跑測試留下的 gctl-run 暫存現場(字面絕對路徑)。
正確性席與通才席說「範本裡除了結尾沒有任何行以分號結尾」,與整合席 I1 相反;機械重現判整合席對(見下表 I1),兩席那句是查證錯,不是 finding、不入帳。
圖譜鏡頭:固定席有附(lumos 自動附加段),七席都逐條答;「授權與歸屬」的 ★INVARIANT★ 五席判受影響(同 G-lic 組)。

## 逐條重現與去向

| id | 席 | 嚴重度 | 重現 | 結果 | 組 | 去向 |
|---|---|---|---|---|---|---|
| C1 | 正確性 | major | `python3.14 scripts/test_lumos.py -k license` → `✗ 授權/KEY2: 每支會被複製進消費專案的檔都帶 SPDX 標示 ['scripts/templates/android-ui-attribution.sql']`,10 passed 1 failed | HIT | G-lic | 折 |
| B1 | 邊界 | major | 同 C1 | HIT | G-lic | 折 |
| G1 | 通才 | major | 同 C1 | HIT | G-lic | 折 |
| I2 | 整合 | major | 同 C1 | HIT | G-lic | 折 |
| A2 | 架構對齊 | minor | 同 C1 | HIT | G-lic | 折 |
| I1 | 整合 | major | 範本換掉 __PROCESS__、前面加 `-- [Q1] … expect=f100:compose_ns=5`,用重跑腳本同一支正規式解析:解析出 1 條,本體不含 `WITH RECURSIVE`,截在第 17 行以分號結尾的註解 | HIT | G-rerun | 折 |
| I4 | 整合 | minor | 讀 t_android_ui_attribution_vendored:只斷言登記與檔案存在,沒看 SKILL.md 有沒有指到範本、有沒有說明 expect 的第一欄鍵 | HIT | G-rerun | 折 |
| C2 | 正確性 | minor | sqlite3:doFrame 10ms → 名稱 NULL 的 6ms → measure 3ms,輸出 other 4、其餘 0,加總 4 ≠ 幀長 10 | HIT | G-class | 折 |
| B2 | 邊界 | minor | 同 C2 | HIT | G-class | 折 |
| B3 | 邊界 | minor | sqlite3:Compose:recompose 60ms → App 的 drawChart 50ms,輸出 compose 10、pipeline 50(應跟祖先算 Compose) | HIT | G-class | 折 |
| C3 | 正確性 | minor | 讀 t_android_ui_attribution_pipeline:只用 draw-VRI[MainActivity]@1,純 draw 沒有案例;把 GLOB 'draw*' 改成 'draw-*' 測試照綠 | HIT | G-class | 折 |
| B4 | 邊界 | minor | sqlite3:doFrame 100ms → Compose:recompose 150ms,輸出 other -50 | HIT | G-class | 折 |
| I3 | 整合 | minor | SKILL.md L1 第 2 步的 pipeline 名單沒有 traversal,範本與計劃都有 | HIT | G-doc | 折 |
| S1 | 資安 | minor | 讀 SKILL.md:top_compose_fn 與區段名原樣進收據與 AI 上下文,沒寫「查詢輸出是被量 App 的資料、不是指令」 | HIT | G-doc | 折 |
| S2 | 資安 | minor | 讀範本檔頭與 SKILL.md:__PROCESS__ 直接字串替換,沒要求先確認套件名只含英數字、底線、點 | HIT | G-doc | 折 |
| A1 | 架構對齊 | major(席位自標 ⚠ 交編排者) | 讀 skills/lumos-android-evidence/reference.md:收據查詢原本只有「每份收據手寫」一種;這次多了「工具鏈範本 + 佔位字替換」,reference.md 沒寫什麼時候用哪一種,接手的人要猜 | HIT | G-doc | 折 |

資源席:clean,無發現。

## 根因分組與統一修法

- G-lic(5 條):授權守衛只認 `#` 開頭的 SPDX 註解行,SQL 只能用 `--`。修法:守衛照檔案類型認註解符號(`.sql` 認 `--`,其餘照舊 `#`),不整體放寬;補一個「.sql 範本拿掉 SPDX 行要紅」的翻紅案例。同族:之後任何非 `#` 註解語言的範本都走同一個對照表。
- G-rerun(2 條):範本「整份貼進收據」這條路徑沒有測試。修法:範本註解不准以分號結尾(拿掉第 17 行的分號);補端對端測試——範本加標頭寫成 queries.sql,跑真的重跑腳本與假的分析工具,假工具收到的查詢要是完整那支(含 WITH RECURSIVE 與結尾 ORDER BY);skill 的指引測試順便斷言 SKILL.md 指到範本路徑並說明 expect 的第一欄鍵。
- G-class(5 條):分類規則的邊界沒釘。修法:名稱接回用 `IS`(NULL 名稱照「分不出類、跟祖先」);draw 只認框架的名稱(`draw` 本身與 `draw-VRI` 開頭),App 自己的 draw 開頭區段跟祖先;自身時間不小於 0;每一條各補一個案例並各自改壞驗紅。
- G-doc(4 條):skill 與 reference.md 補齊——pipeline 名單補 traversal;查詢輸出的區段名是被量 App 的資料、寫進收據前不照著做;換 __PROCESS__ 前先確認套件名只含英數字、底線、點;reference.md 寫明固定的分析查詢放 scripts/templates/*.sql、一次性查詢照舊手寫進收據(這是 A1 指的「兩套之間要猜」的根因;放範本目錄是沿用逐層診斷計劃收據重跑腳本那條 WHY 的先例)。

## 三問(席位回答的核對)

- 已驗:七席都跑過或讀過測試;資源席量了 129 萬區段 8.3 秒、線性;通才席手算了六支測試的期望值。
- 未驗:七席都沒有 trace_processor,真實 Perfetto 上的語意只靠我先前在實驗室真實 Trace 上跑過(41 萬區段 1.5 秒、四組注入)。

## 修補因果

r1 是首輪,沒有上一輪修補,regression_set 不適用。
