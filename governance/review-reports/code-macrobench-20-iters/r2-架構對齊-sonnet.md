severity: clean

我的結論是這份 diff 沒有跟既有做法不一樣的地方。我只讀了 diff 和鄰居函式,沒有跑測試。

**問 1 分層與依賴方向:一樣。**
- 新函式都放在 `_macrobench_*` 這一區,沒有新模組,也沒有跨層直呼。
- 讀結果檔、比對、印出各走原本的層:`_macrobench_read_one` 產出,`_macrobench_read_file` 組裝,`_macrobench_cmp_metrics` 判定,`_macrobench_print` 與 `_macrobench_mode` 輸出。
- 新常數 `MACROBENCH_MAG_ONLY_ITERS` 緊接 `MACROBENCH_ZERO_CROSS` 之後,跟其他 `MACROBENCH_*` 常數的寫法一致(scripts/lumos:39362-39366)。
- 存基準時也印輪數提醒,是在 `_macrobench_mode` 裡呼叫 print 函式。這跟 `_macrobench_update` 自己用 print 輸出文字、不看 `as_json` 的現況相同(scripts/lumos:39702-39712),不算新層。
- `_macrobench_read_one` 的回傳從 3 個值變成 5 個值。我只找到 `_macrobench_read_file` 這一個呼叫端(scripts/lumos:39554),已經同步改了。

**問 2 命名與錯誤處理:一樣。**
- 命名維持 `_macrobench_` 前綴加動詞或名詞的寫法,docstring 也帶審查輪次出處,跟 `_macrobench_stab_unjudged` 同款(scripts/lumos:40177)。
- 函式內才 `import math`、`import statistics`,跟鄰居 `_macrobench_num`(scripts/lumos:39371-39376)和 `_macrobench_read_one` 的 `import json` 一樣,只用標準庫。
- 錯誤處理也跟 `_macrobench_num` 同型:捕捉 `OverflowError` 並回「不合格」,不往外噴例外。`_macrobench_cv` 另外捕捉 `ValueError` 和 `ZeroDivisionError`,同樣回 None。
- 基準檔壞欄位的處理沿用 `_macrobench_entry_ok` 的做法,回 False 讓整份基準當讀不了(scripts/lumos:39657-39672)。
- 輸出結果鍵 `low_iterations` 在 `res` 初始化時就固定存在,符合該處「鍵固定」的註解(scripts/lumos:40200-40204)。

**問 3 有沒有第二種做法:沒有。**
- 數字檢查:輪數用 `_secev_int`(scripts/lumos:8559),runs 內容與 cv 用 `_macrobench_num`。沒有另寫一套 isinstance 檢查。
- 結果欄位組裝:`iterations` 和 `cv` 在 `_macrobench_read_file` 裡條件式加進 entry。`source` 欄同樣是事後才條件式加進 entry(scripts/lumos:39587-39588),形狀相同。
- 標準差和平均直接用標準庫 `statistics`。我搜過,repo 裡沒有鄰居已有的同功能自訂工具函式。
- 提醒輸出只有一支 `_macrobench_print_low_iterations`,文字路徑與存基準路徑共用它。
- 測試:新增三支測試用了既有的 `_mb_entry`、`_mb_startup`、`_mb_run`、`_mb_result_json` 和 `_MB_CFG`,沒有另寫一套輔助函式。

不對齊共 0 條,其中重大 0 條
