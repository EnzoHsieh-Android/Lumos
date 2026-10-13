severity: clean

已逐類看過 r9 的 patch(測試檔與三篇圖譜筆記),沒有可利用的洞。

1. **測試執行面:已看,無。**
   - 子程序:`Popen` 的參數是 `sys.executable`、`GRAPHCTL` 和固定字串,沒有 `shell=True`,也沒有拼接的命令。這輪改成 `communicate()`,12 個程序都會等到結束,管線讀乾。
   - 全域狀態還原:`_os.open` 與 `_os.write` 的替換、`lm._vault_write_lock` 的替換、`sys.argv` 都在 `finally` 裡還原。唯一的小缺口是 `_signoff_with` 裡 `patch()` 在 `try` 外面。但它只是賦值,不會丟例外,不構成漏洞。
   - 符號連結:`(gv / "Systems" / "Sym\x1b[31mRED.md").symlink_to(greal.name)` 指向同目錄的相對名稱,在 `mkvault()` 的暫存目錄內,沒有指到測試目錄外。
   - 檔名裡的 ESC 序列是測試資料,用來驗證輸出會被清洗。
2. **筆記內容:已看,無。** 三篇筆記只有文件說明。我搜過 `curl`、`wget`、`rm -`、`sudo`、`--no-verify`、「請執行」、「忽略」,沒有要代理做危險動作的指示。patch 裡的零寬字元、雙向覆寫字元、BOM,只出現在測試用的 Unicode 字串中,屬於刻意的測試資料。筆記正文沒有藏看不見字元。
3. **密鑰與個資:已看,無。**
4. **執行邊界:已看,無。** 沒有寫 `~/.cache`、使用者全域設定,或 repo 外的路徑。我用 `os.open` 等關鍵字搜過,沒有 `expanduser`、`HOME`、`/tmp` 的硬編碼。檔案讀寫都在 `mkvault()` 建的暫存 vault 內。
5. **其他與新依賴:已看,無。** 沒有新增依賴。

總結:這份 patch 在命令拼接、全域狀態還原、符號連結範圍、筆記注入與秘密這幾面都沒有可利用的洞。
