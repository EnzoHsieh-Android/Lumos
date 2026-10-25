preflight-4: ran

# code-macrobench-20-iters r1 收貨

審材:主線 3175444b 到 f1c32a67 的改動 r1-snapshot.patch(503 行)。兩席:單審、架構對齊(都是 sonnet),都交回後才一起存檔。架構對齊引句全錨,當處置清單載體;單審 F1 的引句寫成「cv = {}」不到 10 字、錨不到,內容由測試機械重現(見下)。

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | major | 測試 ⑤f、⑤g:runs [1e300,-1e300,5e-324×3] 算出 cv=inf 寫進基準後整份讀不回來;runs [1e308,1e308] 讓 fmean 溢位、整檔讀不了;修前改壞(拿掉 isfinite / 溢位不接)兩條都紅 | HIT | 折:_macrobench_cv 溢位、平均 0、非有限一律回 None;補 ⑤f ⑤g ⑥;功能筆記補 PITFALL |
| F2 | major | 讀測試:沒有平均為 0、平均為負的情境 | HIT | 折:補 ⑤d(平均 0 不記 cv、照樣存)⑤e(平均為負用絕對值,手算 0.163299);改壞(拿掉除以零保護)紅 |
| F3 | minor | 讀碼:--update-baseline 直接 return,不印 low_iterations | HIT | 折:存基準後也印提醒;補 ⑥⑦,改壞(拿掉提醒)紅 |
| F4 | minor | 讀測試:⑤ 用子字串 "5" 判,15、25 也過 | HIT | 折:改比對「只跑了 5 輪」 |
| F5 | minor | 讀條款 S4:「那一項」可讀成情境或指標;⑤b 沒驗 cv | HIT | 折:條款下補一行說明兩層單位(條款本身不改,免得規格閘留痕失效);補 ⑤c |
| A1 | major | 讀碼:整數加排除布林的檢查內嵌兩處,既有 _secev_int 同功能 | HIT | 折:改用 _macrobench_iters_ok(包 _secev_int) |
| A2 | minor | 讀碼:_macrobench_iterations 另走一遍 metrics 與 sampledMetrics | HIT | 折:併進 _macrobench_read_one,刪掉 _macrobench_iterations |
| A3 | minor | 讀碼:low_iterations 在 _macrobench_mode 內嵌組 | HIT | 折:抽成 _macrobench_low_iterations,印出抽成 _macrobench_print_low_iterations |

折 8、放行 0、駁回 0。改壞實驗 8 道(無限大照記、溢位不接、平均 0 不擋、存基準不提醒、永遠兩道、壞 runs 照記輪數、不驗輪數、平均不取絕對值)全紅。
