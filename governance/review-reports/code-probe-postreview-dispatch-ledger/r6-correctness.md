severity: minor

我跑了兩版的行為,找到兩條發現,都不到 major。`-k probe_boundary` 的 164 個測試和 `-k confirm_tty` 的 8 個、`-k no_ctty` 的 2 個全過。`TestScenarioProbeAblation` 的 32 個裡有 1 個錯,原因是我只取出 `scripts` 與 `governance/eval`,缺 `CLAUDE.md`,與本次修補無關。實驗目錄已 `rm -rf`。

## Finding COR6-01
severity: minor
blocking: 否
引句:「if replace and not os.access(path.parent, os.W_OK | os.X_OK):」
file: `scripts/scenario_probe.py:1112`

- **具體輸入**:`--history ro/h.jsonl`。`ro/` 是存在但不可寫的目錄(mode 555),`h.jsonl` 還不存在。
- **走到哪一段**:`_output_target_problem(path, replace=False)` 在 `st is None` 時只檢查 `path.parent.is_dir()`。父目錄可寫的檢查只在 `replace=True` 才做,所以回 `None`,開跑前放行。整批跑完後,`os.open(a.history, O_WRONLY|O_APPEND|O_CREAT|O_NOFOLLOW)` 才丟 `PermissionError`。
- **壞在哪**:新增這個前置檢查的目的,就是不要整批跑完才炸,而這條路徑正好漏掉。
- **重現**:在修後版本取出的目錄裡執行 `sp._output_target_problem("t/ro/h.jsonl", replace=False)`,輸出 `None`。接著同一路徑的 `os.open(..., O_CREAT)` 丟出 `PermissionError(13, 'Permission denied')`。同一個 `--out t/ro/o.json` 則被擋下,輸出 `t/ro 不可寫,沒辦法在同目錄放暫存檔`,兩者不一致。
- **歸因:有證據的原有漏查**。修前沒有前置檢查,`open(a.history,"a")` 在同一輸入下同樣是跑完才失敗。修後只是沒補到這條。兩版的差別是這次補丁宣稱已涵蓋,所以我把它當成補漏。

## Finding COR6-02
severity: minor
blocking: 否
引句:「if old is not None and (stat.S_ISCHR(old.st_mode) or stat.S_ISFIFO(old.st_mode)):」
file: `scripts/scenario_probe.py:1111`

- **具體輸入**:`--out t/f`,`t/f` 是沒有讀端的 FIFO(`mkfifo`)。`--history` 指到 FIFO 也一樣。
- **走到哪一段**:前置檢查對 FIFO 一律回 `None`。寫入端 `os.open(path, O_WRONLY|O_NOFOLLOW)` 是阻塞式開啟,沒有讀端就永遠卡住。
- **壞在哪**:整批模型都跑完、額度用掉之後,在最後寫報告時掛死,結果全留在記憶體裡丟失。
- **重現**:修後版本,`signal.alarm(3)` 底下呼叫 `sp._atomic_write_text("t/f","x")`,得到 `TimeoutError('HANG')`,前置檢查輸出 `fifo preflight None`。修前版本同一呼叫立刻返回,因為舊碼只對普通檔取 mode,FIFO 被 `os.replace` 換成普通檔。
- **歸因:有證據的修復回歸**。修前能完成、修後會卡死,兩版命令與結果如上。
- **補充**:有讀端的 FIFO(例如行程替換)能正常寫,這是設計意圖。壞的只有沒有讀端的 FIFO。

## 固定席逐條判定
- **lumos-cli-lifecycle**:合約是 re-inject 只覆蓋 sentinel 之間的內容,與探針的輸出寫入無關。TTY 測試新增只動測試與筆記,不影響。
- **codex-harness、測試假綠形態**:新測試 `t_confirm_tty_no_ctty_session_survives` 先斷言現場成立,符合那條還原翻紅釘的規則。`-k no_ctty` 兩項檢查都過。我沒有還原 `O_NOCTTY` 去驗翻紅。
- **design-loop、guard-kill、bound-tests-gate、lumos-cli-read、授權與歸屬**:這次 diff 沒碰它們宣稱的行為,不影響。授權檔白名單與 SPDX 標頭沒動。
- **ablation 相關讀端**:消融腳本的 `glob("*.json")`、`*.pending`、`*.candidate` 不會撞到新暫存檔名 `.probe-out-*.tmp`。腳本裡沒有 `tempfile` 的其他用法,也沒有依賴舊暫存命名的清理。`.failed` 歸檔改走探針的 `_atomic_write_bytes`,位元組內容與修前一致。
- **角色卡 be-api-compat**:報表欄位與 JSON 結構沒變。`summary.md` 內文跳脫變了,但讀端(`test_lumos.py` 的相關檢查)只比對「來源日期未知」這類字面,不受影響。
- **角色卡 be-authz**:沒有新增端點。權限規則「只對自己擁有的檔沿用權限」方向正確。

## 修補三問
1. **原問題的修復效果**:有行為證據。新檔 0644 照 umask、自己擁有的檔保留 0640、唯讀檔仍拒絕、250 字元檔名可寫、`/dev/null` 直接寫,都由 `t_probe_boundary_fifth_round_output_edges` 驗過並通過。分段等待 300 後再 1 也過。「別人擁有的檔」只靠 patch 掉 `geteuid` 模擬,沒有真的第二個帳號。
2. **修補處的相鄰路徑**:
   - 普通檔、目錄、符號連結、父目錄不存在,前置檢查與實際寫入一致。
   - 指向目錄的符號連結被換成普通檔,與既有契約一致。
   - FIFO 從修前的被取代變成阻塞,見 COR6-02。
   - 歷史檔的建立權限漏檢,見 COR6-01。
3. **新發現在修前與修後**:COR6-02 是修前完成、修後卡死。COR6-01 是兩版都跑完才失敗。

## 未驗範圍
- sticky 目錄(如 `/tmp`)裡別人擁有的可寫檔。`os.access` 放行但 `os.replace` 可能 `EPERM`,本機沒有第二個帳號,沒驗。
- `sudo` 下 `st_uid == geteuid` 的實際權限結果。
- 報表 `text()` 的 GFM 實際渲染。我只讀了轉義邏輯與測試,沒有真的用 GFM 渲染。字面反斜線現在會顯示成兩個(例如 Windows 路徑),屬於刻意取捨,我沒有標成發現。
- `ruff` 對兩個檔報 44 條,我只看了結尾幾條,沒有逐一對照是否落在本次 hunk。
- 全套測試未跑。

總結:最高嚴重度 minor
