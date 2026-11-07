severity: clean

三類都已看過,沒有發現可利用的洞。

①提示注入:已看,無。r2 修補只在 check.py 內部自檢和測試中使用。sg 的輸出只用來比對 `ruleId`、檔案位置和訊息是否存在,不會被送進 AI 的派工詞或 hook 附加段。探針的規則 id 和樣本路徑來自 `SARIF_PROBES` 這個寫死的常數,不是外部文字。

②讀寫與執行越界:已看,無。
- `load_lumos()` 載入的路徑是 `HERE.parents[2]/scripts/lumos`,也就是工具鏈 repo 自己的檔。它是 r2 之前就有的函式,載入時設了 `dont_write_bytecode`。這次只多了一個呼叫端,沒有新增載入來源。
- `_lint_run_and_parse(..., argv=[sg, "scan", ...])` 走 argv 模式,不開 shell。各參數都是 `str(Path)` 或寫死的常數,沒有插值。
- 該函式會用 `mkstemp` 建暫存檔,並且有被 SIGTERM 時的清理登記。
- 測試端的 `shutil.rmtree(str(fake.parent))` 刪的是自己用 `mkdtemp(prefix="gctl-ktsg-")` 建的目錄,範圍沒有越界。
- patch 沒有新增密鑰、信箱或下載網址。

③非刻意、一步就能繞過的守衛:已看,無。
- 「SARIF 探針借閘的解析函式」這一步,在載不到 `scripts/lumos` 時會報問題並 `break`,不會靜默放行。
- 探針規則不在預期目錄時也會報問題,不會意外變綠。
- `except Exception` 把例外轉成「跑不起來」,走的是報錯路徑。
- 一個正常操作下走不到的角落:探針的 sg 工具名要出現在 `claims` 裡。若換版本拿掉位置,`c.get("file")` 會過濾掉那筆,結果是報問題,這是安全方向。
- 我沒有找到「誰、從哪裡、送什麼、拿到什麼」四件都填得出的繞過路徑。

總結:最高等級為 clean,blocking 共 0 條
