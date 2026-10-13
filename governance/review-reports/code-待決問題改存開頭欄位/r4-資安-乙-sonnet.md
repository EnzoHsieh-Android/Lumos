severity: clean

已看完整份 patch,沒有能被利用的洞。

1. 測試執行與全域狀態:已看,無。
   - 新測試在 `_vault_write_lock` 被換成 `_busy` 後,用 `finally` 同時還原 `lm._vault_write_lock` 與 `sys.argv`,例外也會還原。後面的測試不會在沒鎖的情況下寫到真實 repo。`scripts/test_lumos.py:1265-1281`(patch 行 1265-1281)
   - 子程序只用 `_sp.run([...列表...])`,沒有 `shell=True`,也沒有字串拼接。git 一律用 `-C <臨時 repo>`,身分用 `-c` 帶入,不碰全域 git 設定。
   - 測試裡的 `--no-verify` 只用在 `_mk_spec_gate_repo(mkvault().parent.parent / ...)` 建出的臨時 repo,不是專案 repo。
   - 把 `--output=<檔>..HEAD` 這種惡意範圍傳給 `--push-check`,是在驗不會寫出檔。這是防禦性測試,檢查 `pwn.txt` 不存在。
2. 技能文件與筆記:已看,無。
   - `skills/` 與 `docs/` 的新增內容都在講 `question-add`、`question-set` 和鎖的規則。
   - 裡面沒有叫代理去刪檔、強推、跳過檢查、外送資料或執行外部內容的指示。
3. 密鑰與個資:已看,無。出現的只有 `t@t` 這類假資料。
4. 執行邊界:已看,無。
   - 沒看到寫入 `~` 或 `~/.cache`,也沒看到讀 `os.environ`。
   - 用 `Path("/nonexistent")` 只是當作 `Env.from_texts` 的占位。
   - 臨時路徑都由 `mkvault()` 衍生。
5. 其他類別:已看,無。新增 import 只有標準函式庫的 `io`、`contextlib`、`subprocess`、`re`、`unicodedata`、`json`,沒有新依賴。

總結:這份測試、筆記和技能文件的改動,在命令執行、狀態還原、代理指示、密鑰、執行邊界和依賴六方面都沒有可利用的洞。
