severity: clean

這份 diff 是 Kotlin 規則包新增 `rules-unwired/` 目錄(`check.py`、規則 yml、測試、筆記)。我從攻擊者角度逐行看過 `check.py` 和 `test_lumos.py` 的改動,沒找到能被利用的洞,所以沒有任何 `## F<n>` 發現。我也用 grep 掃過信箱、token、secret、curl、wget、`os.system`、`shell=True`、`eval(`、`exec(`,diff 內沒有命中。

**①提示注入:已看,無。**
- diff 沒有新增把自由文字寫進派工詞、hook 附加段或 AI 指令的路徑。
- 新增的 `message_problems` 錯誤句只帶規則 id、目錄名和型錄編號,不帶筆記內容。

**②讀寫與執行越界:已看,無。**
- `sarif_rule_ids` 用 `subprocess.run` 傳 list 引數,沒有 shell 插值,也沒有 `shell=True`。它執行的 `sg` 路徑沿用既有的 `check(sg)` 參數,diff 沒有新增取得 `sg` 的來源。掃描目標固定在 `HERE / "samples" / "bad" / rid`,`rid` 來自寫死的 `SARIF_PROBES` 常數,沒有外來路徑。
- `sgconfig-unwired.yml` 只有 `ruleDirs: - rules-unwired`,是規則目錄內的相對路徑。
- 測試裡的假 `sg` 腳本用 `tempfile.mkdtemp` 建立,內容固定,只用 `_shlex.quote(sg)` 轉接真 `sg`,沒有外部輸入進命令。
- diff 沒有新增密鑰或信箱,也沒有下載網址或環境變數覆蓋。

**③非刻意、一步就能繞過的守衛:已看,無。**
- 新增的 `rules-unwired` 目錄不接推送閘,這是設計意圖。
- 「引用出處不全的型錄列只准放 `rules-unwired/`」這條守衛,在缺 `dir` 鍵時照「不在 unwired」算,會報問題而不是漏過。
- 因為目錄不接閘,有人把規則放進去就能躲掉閘,但這需要刻意搬檔案。`_DIR_SEVERITY` 對 unwired 放寬到全部等級是設計,不是照常操作會意外走過的路徑。四件填不出來,所以不報。
- 本次也沒有為不接閘目錄新增接電的檔案或 hook。

總結:最高等級為 clean,blocking 共 0 條
