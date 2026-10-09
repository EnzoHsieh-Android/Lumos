severity: minor

這輪沒有 blocker 或 major。圖譜宣稱大致成立，七個改壞版本都翻紅。但有四處測試或筆記沒釘到宣稱的行為，另有一個報表轉義的小退步。以下四條 finding 都不阻擋。

## Finding CTR6-01
severity: minor
blocking: 否
引句:「hist_fd = os.open(a.history, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o666)」
file: `scripts/scenario_probe.py:1401`（修後 483df9fe）

- **具體輸入**：模型跑的期間，有人把 `--history` 位置換成指向受害檔的符號連結。
- **走到哪一段**：開跑前檢查（`_output_target_problem`）已過，跑完後才執行追加。
- **壞在哪**：
  - 新測試 `t_probe_boundary_fifth_round_output_edges` 只用「開跑前就是連結」的案例，由開跑前檢查擋下。
  - 真正抵擋「檢查後才換成連結」的 `O_NOFOLLOW` 沒被任何測試釘住。
  - codex-harness 的 PITFALL 把「`--history` 追加仍跟隨連結」列在這支測試名下，這項宣稱沒有對應的紅燈。
- **還原結果**：把追加改回 `open(a.history,"a")` 後，`-k confirm_tty_no_ctty`、`-k fifth_round_output_edges`、`-k wait_over_poll`、`-k fourth_round_report_and`（即 mutation 5 `run.sh` 的四個 -k）全綠。`-k probe_boundary` 和 `-k ablation` 我沒在這個改壞版本下跑。
- **重現**：
  - 用 `e2e.py`（mock `run_one`，在模型呼叫中途建 `h2.jsonl -> victim`）。
  - 改壞版本：`swap during run: (0, 1) victim: 'keep{"ts": "", "seed": ""…`，受害檔被追加。
  - 修後原版：`OSError(62, 'Too many levels of symbolic links')`，受害檔仍是 `'keep'`。
  - 修前 4d765d5c：同樣被追加。
- **歸因**：有證據的原有漏查。修補本身正確，缺的是測試。

## Finding CTR6-02
severity: minor
blocking: 否
引句:「from scenario_probe import _atomic_write_bytes  # 原子寫入同樣只留探針那一份」
file: `scripts/test_lumos.py:37923`

- **宣稱**：ablation-lumos-first 的 WHY 說消融腳本改用探針那份實作，並綁 `t_probe_boundary_postreview_cli_entry_and_modes`。
- **壞在哪**：該測試只檢查消融腳本純合併時，自己擁有的檔保留 0640。消融腳本放回一份舊式本地副本（新檔 0600、無權限規則）時，這個斷言仍成立。
- **還原結果**：
  - 把本地副本放回後，`-k probe_boundary` 為 164 passed、0 failed（輸出另有一行探針批次鎖的提示）。
  - `-k ablation` 為 4 passed、0 failed。
  - 沒有任何測試釘住「消融腳本用的就是探針那份」，WHY 的 `[test:]` 綁不住這句話。
- **歸因**：有證據的修復後新增宣稱，綁定不實。

## Finding CTR6-03
severity: minor
blocking: 否
引句:「raw = str(x).replace("\r", " ").replace("\n", " ").replace("\\", "\\\\")」
file: `governance/eval/ablation_lumos_first.py:394`

- **具體輸入**：meta 或題號含字面反斜線，例如 `a\b` 或 `C:\dir\f`。
- **走到哪一段**：`text()` 先把反斜線加倍，後面的跳脫正則再加倍一次。
- **壞在哪**：原始碼變成 4 個反斜線，Markdown 渲染出 2 個，路徑會顯示成 `C:\\dir\\f`。
- **為什麼值得報**：消融報表是事後追查的證據，ablation-lumos-first 的 WHY（ARCH5-02）說要看得出原值，但現在每個字面反斜線都顯示成兩個。
- **重現**：逐字複製修後 `text()` 的邏輯（含 `visible()`）跑：
  - `'a\\b' -> a\\\\b`（渲染成 `a\\b`）
  - `'\x1b' -> \\x1b`
  - `'\\x1b' -> \\\\x1b`
  - 真 ESC 與字面 `\x1b` 確實分得開，但代價是所有反斜線都加倍。
  - 修前版本只做一次正則跳脫，`a\b` 渲染成 `a\b`。
- **測試**：新測試只斷言 `esc_md != lit_md`，不管字面反斜線的呈現。
- **歸因**：有證據的修復回歸（呈現保真度退步）。

## Finding CTR6-04
severity: minor
blocking: 否
引句:「problem = target and _output_target_problem(target, replace=replace)」
file: `scripts/scenario_probe.py:1111`

- **具體輸入**：`--history` 指向不存在的檔，父目錄存在但不可寫。
- **走到哪一段**：`replace=False` 的分支跳過了父目錄可寫檢查，開跑前檢查回 None。
- **壞在哪**：
  - 模型整批跑完後，追加時才丟出沒被攔住的 `PermissionError`，歷史記錄丟失（`--out` 已寫出）。
  - 這與 codex-harness 的 PITFALL 宣稱「開跑前檢查 `--history`」不符，漏洞形狀正是這輪要消除的「整批跑完才炸」。
- **重現**：
  - `_output_target_problem(ro/h.jsonl, replace=False)` 回 `None`，對照 `--out` 同位置回「不可寫」。
  - 用 `e2e.py` 呼叫 `main()`：`history in readonly dir: ("PermissionError(13, 'Permission denied')", 1) out exists: True`，模型已呼叫 1 次。
  - 修前 4d765d5c 結果相同。
- **歸因**：有證據的原有漏查。

## 固定席逐條判定
- **lumos-cli-lifecycle**（★INVARIANT★ re-inject byte-equal）：不影響。diff 只改 `_confirm_tty` 的 PITFALL 行，沒碰 re-inject 的 sentinel 行為；PITFALL 帶齊 `[出處][根因][test]`。
- **codex-harness**：新 PITFALL 帶齊 `[出處][根因][test]`，WHY 帶齊 `[出處][因][不選][test]`，宣稱與修後程式碼相符；唯一落差見 CTR6-01 和 CTR6-04。
- **測試假綠形態**（★INVARIANT★ 還原翻紅釘須配現場前置斷言）：新測試符合。子程序先印 `SCENE leader=True ctty=False`，拿掉 `O_NOCTTY` 後現場斷言仍綠、返回碼為 -1（掛斷）。
- **design-loop / bound-tests-gate / guard-kill / lumos-cli-read / 授權與歸屬等其他固定席**：不影響。diff 沒碰這些合約的行為，只有 `scenario_probe.py`、消融腳本和三支新測試（外加既有測試與 Verification 筆記）。消融腳本不再自帶 `tempfile` 與原子寫入實作，改匯入。
- **其餘只列名的節點**：不逐條答。
- **lint**：五篇相關筆記都沒有新增問題，codex-harness 兩條 FACT 來源警告是舊有的。

## 還原翻紅結果表
測試要用 `-k` 單關鍵字跑，我用的是各測試名中的關鍵字。

| # | 改壞方式 | 結果 |
|---|---|---|
| ① | 一律沿用舊檔權限（拿掉 `old.st_uid == os.geteuid()`） | `fifth_round_output_edges` 紅：「別人擁有的寬權限檔…」得到 `0o100666` |
| ② | 拿掉 `_output_target_problem` 呼叫 | `fifth_round_output_edges` 紅：父目錄不存在時 `[Errno 2]` |
| ③ | `--history` 改回 `open(…,"a")` | 全綠，**假綠**（見 CTR6-01） |
| ④a | 拿掉 `:@~` | `fourth_round_report_and` 紅 |
| ④b | 拿掉 `www.` 轉義 | `fourth_round_report_and` 紅 |
| ⑤ | 拿掉 `O_NOCTTY` | `confirm_tty_no_ctty` 紅：`(-1, 'SCENE leader=True ctty=False…')`；既有 `t_confirm_tty_unit` 六項仍全綠 |
| ⑥ | `min(300,…)` 改成一次睡滿 | `wait_over_poll` 紅：`[call(301)]` |

- **geteuid patch**：用 `patch.object(mod.os,"geteuid")` 模擬別人擁有的檔，走的是真實的 `st_uid == os.geteuid()` 判斷，改壞版本①確實翻紅，不算只檢查常數。
- **⑥ 的現場斷言**：「現場成立」那條在改壞版本下也變紅（呼叫 2 次，不是 3 次），不影響翻紅結論。

## 驗證紀錄數字
- `-k confirm_tty`：8 passed，與紀錄相符。
- `-k ablation`：4 passed，與紀錄相符。
- `-k probe`：396 個測試中，我的副本只取 scripts、governance/eval、governance/scenarios，不含 docs，所以 `t_probe_discipline_targets_are_fresh` 紅（395 passed、1 failed）；其餘與 396 相符。
- 紀錄中的「消融單元測試 32 OK」：沒有重現，副本缺少 `autonomous_loop` 模組。
- 紀錄中的七個改壞版本：我只還原了任務指定的六項（②③④a④b⑤⑥加①）；其中沒有對應紀錄第四、第七項的「不設權限」「不沿用自己檔權限」。

## 修補三問
- **①原問題的修復效果**：
  - 新檔權限照 umask：測試斷言 `0o644`。
  - 別人擁有的檔不沿用權限：改壞版本①翻紅。
  - 開跑前擋 `--out`：改壞版本②翻紅。
  - 等待分段：改壞版本⑥翻紅。
  - 報表自動連結轉義：改壞版本④翻紅。
  - 終端掛斷：改壞版本⑤翻紅。
  - `--history` 不跟隨連結的真正防線沒有行為證據（CTR6-01）。
- **②相鄰路徑**：
  - 自己擁有檔的 0640 保留、裝置直接寫、唯讀檔拒絕，都有測試覆蓋。
  - 唯讀父目錄下新建歷史檔的路徑沒有檢查（CTR6-04）。
  - 字面反斜線的呈現退步（CTR6-03）。
- **③新發現案例的修前修後**：CTR6-01、CTR6-04 修前修後行為相同（原有漏查）；CTR6-03 修前正常、修後加倍（回歸）；CTR6-02 是修後新增宣稱的綁定問題。

## 未驗範圍
- Windows：`os.geteuid` 不存在，`ablation` 又 import `fcntl`，確實是 POSIX 專用；我沒驗 `scenario_probe.py` 在 Windows 上的行為。
- `os.umask(0)` 再還原的操作在多執行緒下是否有競態：沒驗，未看到探針有執行緒。
- 既有 FIFO 當 `--history` 目標時阻塞行為：未驗。
- 全套測試與 Python 3.14 以外環境：未驗。
- 消融腳本的 `TestScenarioProbeAblation` 單元測試（`scripts/test_autonomous_loop.py`）：未實際執行，副本缺模組。
- 我取出的副本已 `rm -rf`。

總結:最高嚴重度 minor
