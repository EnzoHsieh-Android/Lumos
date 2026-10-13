severity: clean

已看四類,沒有找到可利用的洞。

1. 測試執行與全域狀態:已看,無。
   - 新測試只用 `subprocess.run` 的串列參數,沒有 `shell=True`,也沒有拼接字串後交給 shell。
   - `git init`、`add`、`commit` 都在臨時庫(`mkvault()` 與 `_mk_spec_gate_repo` 建的)裡跑。commit 用 `-c user.email=t@t -c user.name=t` 並加 `--no-verify`,只影響那個臨時庫,不碰使用者的全域 git 設定或 hook。
   - 符號連結 `_os.symlink(ext, v / "Projects" / "x_計劃.md")` 的目標 `ext` 是 `v.parent` 底下自己寫的假檔,不是敏感檔,也不指向使用者目錄。
   - `_vault_write_lock` 與 `sys.argv` 被換掉後,都在 `finally` 裡還原(`lm._vault_write_lock, sys.argv = real, old`)。
   - `tempfile.mkdtemp(prefix="gctl-qfm5-")` 建在系統暫存區,權限預設是 0700。
   - 測試 ⑥ 用 `--push-check=--output=…` 驗證 `-` 開頭的範圍不會被當成 git 選項,輸出路徑 `d2/pwn.txt` 在臨時庫內。它是防禦性測試,不是利用碼。
2. 技能文件與筆記裡的危險指示:已看,無。`skills/lumos-project-notes/SKILL.md`、`commands/03-寫回圖譜.md` 和 `reference.md` 的改動,只是把寫題目的方式從手寫正文改成 `lumos question-add` 與 `question-set` 指令。沒有教代理跳過檢查、改權限、送資料到外部,或執行來路不明的內容。
3. 密鑰與個資:已看,無。diff 裡只有測試用的假內容和假 email `t@t`。
4. 執行邊界:已看,無。CI 沒有因這些改動去執行不可信位置的檔,也沒有寫 `~/.claude` 或 `~/.cache`。所有寫入都限在臨時目錄。
5. 其他類別與新依賴:已看,無。diff 沒有新增依賴,也沒有反序列化(pickle、yaml.load、eval)。

總結:這個 patch 沒有可被利用的資安問題。
