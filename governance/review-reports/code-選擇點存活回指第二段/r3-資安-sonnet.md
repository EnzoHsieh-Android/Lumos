severity: clean

我讀了 `r3-snapshot.patch` 的 `scripts/lumos`、`scripts/test_lumos.py`、`scripts/test_quality.py` 三處程式,也看了 `r3-repair.patch`,沒有找到能被利用的洞。鎖 `.warming` 沒有動,照派工詞只做審查。

**①提示注入**
已看,無。這次改的是合批編譯、覆蓋、套件掃描這些機械流程,沒有把作者或外部可控的自由文字拼進給 AI 的派工詞、hook 附加段或指令。筆記與文件的改動只是文字。

**②讀寫與執行越界**
已看,無。
- 寫檔路徑:`_KillCompile.units()` 用 `os.path.realpath(os.path.join(self.c.wt, r["file"]))` 算出目標,再要求它落在 `wt_real + os.sep` 底下。檢查通過後寫的也是這個已解析過的路徑,所以捷徑被跟過去之後仍然在工作樹內,沒有 check-then-use 的空隙。
- 擋 .git:r3 改成路徑每段轉小寫再比,`.GIT`、`.Git` 在不分大小寫的檔案系統上也會被擋。`.git` 在工作樹裡是檔案時,它的路徑同樣有 `.git` 這一段,一樣被擋。
- 還原用 `subprocess.run([...list...])`,沒有 shell 插值,路徑寫成 `":(literal)" + relpath`,不會被當成 pathspec 展開,前面也有 `--`。
- 編譯輸出裡的路徑:`_choice_compile_errors` 先 `urllib.parse.unquote` 再 `realpath`,不在工作樹內的只計入對不回的數量、不採用。
- 套件掃描:`os.walk(followlinks=False)`,只收 `.kt`、`.java`,只讀檔頭 32KB,不會跟捷徑讀到 repo 外。
- 測試:`LUMOS_TEST_GROOVY_JAR` 只在使用者手動設定時才真跑,測試的 HOME 隔離,不讀真家目錄。`shutil.rmtree` 只刪測試自己建的目錄。`_sh_quote_t` 對 `sys.executable` 和路徑都有引號處理。
- 密鑰與信箱:這份 diff 裡沒有新寫進去的。

**③非刻意、一步就能繞過的守衛**
已看,無。一般操作(一個指令或一次編輯)走不過去。
- 壞法行的 `file` 欄位指到工作樹外、指到 `.git` 底下,或經捷徑繞出去,都會在 `units()` 被 `continue` 跳過。
- 還原後內容對不上時,先寫回原文再比一次,還不對就丟 `_KillPrepAbort`,不會靜默留下被改過的檔。
- 輸出被截斷時回傳 `None`,一個都不記無效,方向是失效開放(多跑),不會誤判成有效。

總結:最高等級是 clean。
