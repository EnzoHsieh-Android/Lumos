severity: major

# r3 資安席(資安-r3-sonnet)

範圍:diff 的 scripts/lumos 全部 hunk;重現都在臨時 repo(用 test_lumos 的 `_cr_repo` 造),沒碰真帳、沒改 repo 檔。
查過沒洞的:`--template --write` 的卷證資料夾是捷徑、或 `governance/review-reports` 是捷徑指到 repo 外,都回 2 且外面沒多檔(實跑兩種);`_retro_cmd` 與 `_retro_qpath` 的 shlex.quote 加 `_esc_clean` 截斷後不會產生引號外的可執行片段;`_regular_own_fd`、`_esc_clean`、`_loop_records` 其他呼叫者的行為沒被改壞(`_drift_ledger_append` 有 `_drift_ledger_path_err` 先擋捷徑)。

### F1 治理帳是符號連結時,寫入端照寫、讀取端看不到,人裁紀錄靜默消失(修補引起)
severity: major
blocking: 是 — 指令回「✓ 已記人裁」但擋點與處置閘第八步完全不知道這筆紀錄,等於放行;違反「回報成功一定落盤且被閘看到」(S7、S10)。
- 輸入:`docs/.governance-log.jsonl` 是符號連結(git 會把符號連結原樣提交,所以也能由別人的提交帶進來)。
- 走到哪:`cap-decision` 經 `_gate_event` 以 `open(path, "a")` 追加,跟隨捷徑寫進目標檔並回 True;之後所有讀側經 `_retro_gov_events`,第二輪把它改成走 `_regular_own_fd`(帶 O_NOFOLLOW),捷徑開不了,回 `[]`。
- 壞在哪:`_cap_retro_status` 看到「沒有人裁紀錄」,`canary record` 擋點放行新一輪、第八步印 —、`retro --skip` 回「沒有人裁紀錄」。第二輪之前讀側用 `read_bytes` 會跟隨捷徑,兩邊一致。同一原因,`_ledger_tail_needs_newline` 對捷徑回 False,目標檔尾缺換行時新事件黏行。另外 `_gate_event` 寫入端本身仍跟隨捷徑(既有行為,沒有 `_drift_ledger_path_err` 那種檢查):提交一個指向 repo 外檔案的捷徑,受害者跑 `cap-decision` 就會往那個檔追加一行(內容是 JSON 與使用者的 `--note`)。
- 引句:「raw, _err = _retro_read_bytes(Path(root) / "docs" / GOV_LOG_NAME, limit=None)」
- 引句:「fd = _regular_own_fd(path, os.O_RDONLY, require_owner=False)」
- 佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:1502`(`_gate_event` 的 `open(path, "a", encoding="utf-8")` 不擋捷徑)
- 重現(實跑輸出):
  ```
  c = _cr_repo(); _cr_loop(c)      # LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26
  real = tmp/"gov.jsonl"; real.write_text("")
  (c["docs"]/".governance-log.jsonl").unlink(); (c["docs"]/".governance-log.jsonl").symlink_to(real)
  _cr_decide(c)  ->  rc 0  "✓ 已記人裁:crx extra-round(帳上輪次 r1, r2, r3)"
  real.read_bytes() -> b'{"ts": "2026-10-06T03:22:37+08:00", "commit": ..., "gate": "loop-retro", ...'
  lumos loop retro crx --skip --note <十字以上> -> rc 2 "擋下:crx 沒有人裁紀錄——要先記人裁"
  ```
  修法方向:讀寫兩端對捷徑用同一規則(寫端也走 `_drift_ledger_path_err` 或讀端跟著寫端),讀不到治理帳時對「有迴圈在跑」不要靜默當成零筆。

### F2 `--template` 標準輸出與 `--write` 建的檔把帳上欄位的 8 位元 C1 控制碼與雙向標記原樣帶出
severity: major
blocking: 是 — 終端跳脫注入:第二輪宣稱「印到終端一律過 `_esc_clean`」,但這條出口繞過;`--template`(不帶 `--write`)預設就是印到終端。
- 輸入:審查帳某列 `auditor`(或 `report_path`)含 `\x9d52;c;ZXZpbA==\x9c`(8 位元 OSC 52 寫剪貼簿)、`\x9b31m`(8 位元 CSI)、`‏`;帳可以是別人提交進來的。
- 走到哪:`--template` 把帳上欄位放進 `ctx["reports"]`,`json.dumps(..., ensure_ascii=False)` 只跳脫小於 0x20 的字元,U+0080–U+009F 與雙向標記原樣輸出;再用 `sys.stdout.write(text)` 直接寫到終端(沒過 `_esc_clean`)。`--write` 把同一份位元組寫進回顧檔,之後 `cat` 同樣觸發。
- 壞在哪:xterm 類終端在 UTF-8 模式下把 U+009B/U+009D 當控制序列執行(改標題、寫剪貼簿、清畫面偽造輸出);這正是 `_esc_clean` 的 `"\x7f" <= ch <= "\x9f"` 想擋的那類。
- 引句:「text = _j.dumps(skel, ensure_ascii=False, indent=2) + "\n"」
- 引句:「sys.stdout.write(text)」
- 重現(實跑輸出):
  ```
  rows[0]["auditor"] = "s1-sonnet\x9d52;c;ZXZpbA==\x9c\x9b31m‏"   # 寫回 docs/.canary-log.jsonl
  _cr_decide(c) -> rc 0
  lumos loop retro crx --template  -> stdout 含 ['\x9d', '\x9c', '\x9b', '‏'](rc 0)
  lumos loop retro crx --template --write -> cap-retro.json 內含 0x9d 0x9c 0x9b
  ```
  修法方向:骨架裡來自帳的字串(`context`)在序列化前過清洗,或序列化時把 U+0080–U+009F 與雙向字元跳脫成 `\uXXXX`(JSON 讀回來等值,驗證不看 `context`)。

總結:最嚴重 major,blocking 2 條
