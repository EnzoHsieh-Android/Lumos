severity: minor

## Finding SEC5-01
severity: minor
blocking: 否
引句:「os.fchmod(tmp.fileno(), mode)」
file: `scripts/scenario_probe.py:40`
- 誰:對 `--out` 所在目錄有寫入權的另一個本機使用者。
- 從哪:預先放在 `--out` 路徑上的普通檔。
- 送什麼:一個權限為 0666 的普通檔,例如 `chmod 2777`。
- 拿到什麼:`_atomic_write_text` 用 `lstat` 取舊檔權限並做 `& 0o666`,再 `fchmod` 到新檔。新檔會繼承舊檔的群組與其他人可寫位,檔案擁有者則是執行者。攻擊者之後能改寫執行者產出的探針結果 JSON,下游 runner 會讀它。
- 重現(在 /tmp 實驗目錄,用 `python3.14 -I`):
  - 預放檔 `p.json` 為 `0o100777`(含 setgid)。
  - 執行 `sp._atomic_write_text(p,"Y")` 後,輸出 `after mode 0o100666`。
  - setuid、setgid、sticky 位有被 `& 0o666` 去掉,所以沒有提權。
- 限制:要預放並被取代的檔必須在你能 `rename` 的目錄裡。在有 sticky 位的 `/tmp`,`os.replace` 取代別人擁有的檔會被擋(EPERM),只會讓寫入失敗。這點我沒實測,是依 sticky 語意推論。非 sticky 的共用目錄裡攻擊者本來就能直接換檔,這條沒有新增能力。
- 因此標「推論」,屬縱深防禦。建議不要沿用舊檔的群組與其他人權限,固定用 0600 或 0644。
- 歸因:修復引入。舊的 `write_text` 不會改變權限。

## Finding SEC5-02
severity: minor
blocking: 否
引句:「return re.sub(r"([\\`*_\[\]()!|])", r"\\\1", html.escape(raw))」
file: `governance/eval/ablation_lumos_first.py:421`
- 誰:能控制結果檔的題號、`meta.json` 的 date 或 claude_version 文字的人。
- 從哪:`render_md` 的 `text()`,輸出到 `summary.md` 與 stdout。
- 送什麼:裸網址,例如 `https://evil.example/x` 或 `www.evil.com`。
- 拿到什麼:`[]()!` 與反引號都已跳脫,所以 `![..](..)` 和 `[..](..)` 形式的連結、圖片被擋住,這點已驗證。但 GFM 的裸網址自動連結沒被擋。我實測 `text("https://evil.example/x www.evil.com")` 原樣輸出,所以在 Markdown 預覽裡會變成可點連結。
- `<https://e.x>` 形式會被 `html.escape` 擋掉。
- 可控來源是本機結果檔,不是遠端,寫不出完整的遠端攻擊路徑,標「推論」。
- 歸因:原有漏查。這輪的跳脫修補沒有處理裸網址。

## 重新驗證上一輪兩個發現
- 符號連結覆寫已封住。`out.json` 為指向 `victim` 的符號連結時,`_atomic_write_text` 之後 `victim` 仍是 `keep`,`out.json` 變成權限 0600 的普通檔。
- 暫存檔 `NamedTemporaryFile` 用 `mkstemp` 建立(`O_EXCL`、隨機名),攻擊者無法預先放符號連結。`os.replace` 不跟隨目的地的符號連結。`finally` 的 `unlink` 只刪該名稱本身(不跟隨符號連結),最壞是刪到攻擊者自己放的檔,因為這個名稱是隨機的。
- 硬連結:`h2` 被取代後 `h1` 仍是 `orig`,連結被打斷,不會寫穿。
- 父目錄是符號連結:會被跟隨,檔案寫進 `real/`。這是 `--out` 由操作者提供所造成的,跟修補前一樣。
- 目標是 FIFO 時會被換成普通檔,沒有寫入 FIFO。
- 終端控制序列已封住。`ESC`、`BEL`、C1(`\x80`–`\x9f`)、`U+202E`、`U+2028`、`U+2066`、`U+200B`、`U+FEFF`、`\x7f`、`\x85` 都因 `isprintable()` 為假而轉成字面 `\xNN` 或 `\uNNNN`。我實測全部轉成字面。
- `\U000e0041` 會變成 `\ue0041`,與真的 `\ue004`+`1` 有歧義,但無害。
- `ablation_lumos_first.py` 只有 `render_md` 的 `text()` 這個外部文字出口。`run_job` 回傳的狀態字串是數字加固定文字,不含外部內容。

## 六類逐類
1. 不可信輸入到危險操作:已看,只有 SEC5-01 與 SEC5-02。搶先放連結或改名的情境,隨機 `O_EXCL` 暫存檔加 `os.replace` 不跟隨目的地連結,結論是無新洞(見上)。
2. 登入與權限:已看,無。
3. 密鑰與個資:探針結果 JSON 在這次改動範圍內沒有秘密。新檔權限從 umask 預設(0644)變嚴到 0600;有舊檔時沿用舊檔權限(見 SEC5-01)。
4. 加密與傳輸:已看,無。
5. 執行邊界:終端控制序列已封住;Markdown 的連結與圖片形式已封住,裸網址自動連結見 SEC5-02。`O_NOCTTY` 只是不讓開啟的 tty 成為控制終端,沒有放寬邊界。`LUMOS_TTY` 由環境變數指定路徑,屬原有行為,不在這次 diff。
6. 行動端:無。

新增依賴:無。diff 只用標準函式庫(`tempfile`、`stat`、`os`、`re`、`html`)。

我看過的檔,都取自 4d765d5c 的 archive,五檔都看了:
- `governance/eval/ablation_lumos_first.py`
- `scripts/lumos`(`_confirm_tty`)
- `scripts/scenario_probe.py`
- `scripts/test_autonomous_loop.py`(測試內 mock,無外部輸入)
- `scripts/test_lumos.py`(新測試的輸出路徑與符號連結,無命令拼接)

總結:最高嚴重度 minor
