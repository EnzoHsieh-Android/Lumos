preflight-4: ran

# code-android-ui-kind r3 收貨

審材:r3-snapshot.patch(799 行,2bdefa2da714976d1bfa9f0c15e9e55066682e71..e3ea2c16a69f0d7ae7887ece6ad0f6222dbc004e);修補差異 r3-repair.patch(338 行,46773fe6 → e3ea2c16);來源 r3-repair-binding.json(含 r2 fix-check 結果指紋,passed、沒有未執行項);配對案例 r3-behavior-cases.json;pitfalls 清單 r3-manifest.json(6 條內建隱患題,改動行上沒有 lint)。
七席全新:正確性、資源、邊界、整合、通才、架構對齊、資安,全部 sonnet;七席交回後才一起存檔(從逐字稿取原文)。派工詞第三行另寫明不准在工作樹裡跑 checkout、reset、commit;收貨時工作樹分支與 HEAD 都沒變、git status 只有我的帳本與卷證。整合席自述為跑 Linux 容器啟動了 Docker Desktop。
架構對齊席報告有一行縮排的 `severity: minor`,用 report-normalize --write 純格式搬成獨立一行(只差縮排,逐行比對過)。
引句:整合席第 3 條引句不到 10 字錨不到(那條自述「沒有失敗場景、僅記錄核對結果」);通才席第 1 條有一句引的是配對案例檔(不在凍結 patch),同條另一句錨得到;其餘全錨。
圖譜鏡頭:固定席有附,七席都逐條答;「授權與歸屬」的 ★INVARIANT★ 判不受影響(正確性席、整合席在乾淨副本拿掉 .sql 的 SPDX 行驗紅)。

## 逐條重現與去向

| id | 席 | 嚴重度 | 重現 | 結果 | 組 | 去向 |
|---|---|---|---|---|---|---|
| R3C1 | 正確性 | major | `docker run python:3.14-slim`,工作樹唯讀掛進去複製一份,`python3 scripts/test_lumos.py -k android_ui_attribution_receipt` → `✗ 非 UTF-8 環境:中文路徑…`,3 passed 1 failed;同容器 `LC_ALL=C PYTHONUTF8=0` 下 `sys.getfilesystemencoding()` 是 ascii(macOS 永遠 utf-8,本機看不到) | HIT | G3-enc | 折 |
| R3G1 | 通才 | major | 同 R3C1 | HIT | G3-enc | 折 |
| R3I1 | 整合 | major | 同 R3C1;席位另在容器驗過 `exec env PYTHONUTF8=1 python3 -` 後 4 項全綠 | HIT | G3-enc | 折 |
| R3G2 | 通才 | minor | 讀重跑腳本與 reference.md:`sys.stdout.reconfigure` 要 Python 3.7 以上,reference.md 沒寫版本 | HIT | G3-enc | 折 |
| R3B1 | 邊界 | minor | 席位實跑:queries.sql 開頭帶 UTF-8 BOM、兩條查詢、Q1 不符,原本印 BAD Q1 rc1 的收據變成只印 OK Q2 rc0(BOM 讓第一個標頭配不到、標頭數與條數一起少一,假過) | HIT | G3-enc | 折 |
| R3B2 | 邊界 | minor | 席位實跑:manifest.json 帶 BOM → JSONDecodeError Traceback、rc1(不是收據寫錯的 rc2) | HIT | G3-enc | 折 |
| R3R1 | 資源 | minor | 讀重跑腳本:`subprocess.run` 丟例外(分析工具不存在)時 `os.unlink` 沒跑到,暫存查詢檔留在系統暫存目錄,Traceback 回 1 跟比對不符同碼 | HIT | G3-enc | 折 |
| R3B3 | 邊界 | minor | 讀授權守衛:`f.endswith(".sql")` 分大小寫,`x.SQL` 會被要求用 #(方向是多擋) | HIT | G3-lic | 折 |
| R3A1 | 架構對齊 | minor | 讀 scripts/templates/note-audit-*.md 與 scripts/lumos:用 `{{NAME}}` 由程式替換;新範本用 `__PROCESS__` 由 AI 手動替換,兩種佔位字約定沒寫明各自用在哪 | HIT | G3-doc | 折 |
| R3I2 | 整合 | minor | 讀 Systems/macrobenchmark-adapter:寫「預設與 LC_ALL=C 兩種環境各跑一次」,在 Linux 上那支測試是紅的(同 R3C1) | HIT | G3-doc | 折 |
| R3I3 | 整合 | minor | 讀報告:席位自述「沒有失敗場景,僅記錄我核對過的結果,不構成缺陷」;引句不到 10 字錨不到 | MISS(非缺陷) | — | 不成立:席位自述無失敗場景,內容是核對通過的清單 |

資安席:clean。

## 根因分組與統一修法

- G3-enc(7 條):重跑腳本的編碼是逐處補丁(r2 補了五處),漏了傳給子程序的參數、BOM、例外時的清理;macOS 的檔案系統編碼永遠是 UTF-8,本機驗不出 Linux 的問題。修法改成一條統一規則:重跑腳本啟動時一律開 Python 的 UTF-8 模式(`exec env PYTHONUTF8=1 python3 -`,檔案系統編碼、標準輸出入、開檔預設全部變 UTF-8),拿掉 r2 逐處加的 reconfigure 與編碼參數;讀 queries.sql 與 manifest 用 utf-8-sig(BOM 照樣讀得到);呼叫分析工具包在 try/finally 裡刪暫存檔,分析工具不存在時回 2 並說原因;reference.md 寫明需要 python3.7 以上。測試在 Linux 容器另跑一次。
- G3-lic(1 條):副檔名判斷改成不分大小寫。
- G3-doc(2 條):reference.md 寫明兩種佔位字約定(程式替換用 `{{NAME}}`、AI 手動替換用 `__NAME__`);家節點、計劃、驗收紀錄把「LC_ALL=C」的說法改成「開 UTF-8 模式、Linux 與 macOS 都驗過」。

## 三問(席位回答的核對)

- 原問題修復:沒收尾子樹、同分決勝、授權守衛前置三項,七席在 macOS 與 Linux 都驗過成立(整合席在臨時副本逐條拿掉實作各自翻紅);編碼那項只在 macOS 成立,Linux 不成立(R3C1)。
- 未驗:七席都沒有 trace_processor;邊界席在 C、POSIX、空字串、Big5、ISO8859-1 五種語系下驗過重跑腳本(macOS)。

## 修補因果

regression_set:R3C1、R3G1、R3I1(r2 新增的測試在 Linux 紅,修補宣稱的修復在 Linux 不成立)、R3G2(reconfigure 是 r2 加的)、R3I2(家節點那句是 r2 加的);R3B1、R3B2、R3R1、R3B3、R3A1 修前修後行為相同,屬原有漏查。
