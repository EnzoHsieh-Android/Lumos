severity: clean

這份最終版 diff 我沒找到能被利用的洞。diff 做的事有五件:把規則檔從 `rules-hints/` 搬到新的 `rules-unwired/`、新增 `sgconfig-unwired.yml`、在 `check.py` 加 SARIF 自檢、補測試,以及改幾篇筆記和型錄。

**①提示注入:已看,無。** diff 裡沒有任何路徑把筆記內容、檔名、分支名、帳本欄位或席報告寫進給 AI 的派工詞、hook 附加段或指令。`check.py` 新增的 `sarif_gate_rule_ids` 只回傳規則 id 集合,錯誤訊息只含固定字串和例外類別名。`SARIF_PROBES` 是寫死的常數,不吃外來文字。

**②讀寫與執行越界:已看,無。**
- `sarif_gate_rule_ids` 呼叫 `lm._lint_run_and_parse`,`argv` 的各段都是程式內組出來的:`sg` 來自既有的 `_ktpack_sg()`,設定檔和樣本路徑來自 `HERE`,樣本資料夾名取自規則 id。規則 id 要由工具鏈作者提交進 repo,而且 `message_problems` 還要求它以 `kt-` 開頭,所以沒有 shell 插值,也沒有外來路徑。
- `rules-unwired` 加進 `CONFIGS` 後,走的還是同一套 `HERE / d` 規則目錄讀取。它只在 repo 內讀,沒有新的寫入、下載或環境變數覆蓋點。
- 新增的測試會在 `tempfile.mkdtemp` 建的暫存目錄裡寫假 `sg` 腳本並執行。腳本內容是測試內嵌的字面常數,沒有外部輸入。清理用的 `shutil.rmtree` 只刪自己建的暫存目錄,而且帶 `ignore_errors=True`。
- 測試的 `_ugood` 路徑由 `rglob` 找到的壞例檔算出,都在複本的 `HERE` 裡,不會跑出 repo。
- diff 裡沒有新寫進程式、範本或公開文件的密鑰、token 或信箱。

**③非刻意、一步就能繞過的守衛:已看,無。** 我逐項檢查過下面幾種意外情況,都沒有讓守衛被走過去:
- 逾時旗標:`_TIMED_OUT` 沒有被意外重設,`check()` 開頭才重設。
- 載入失敗:`load_lumos` 失敗時回 `(None, "lumos:…")`,呼叫端報問題後 `break`,不會靜默通過。
- 缺 `dir` 鍵:`catalog_problems` 用 `r.get("dir") != "rules-unwired"`,缺鍵時走「報問題」,不會被放行。
- 出處不全的規則放進 `rules-unwired/`:這是計劃上明講「不接閘」的設計,不算被繞過。

總結:最高等級為 clean,blocking 共 0 條
