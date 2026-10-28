severity: major

（本席限制：沒讀上輪席報告；跑過 `-k android_e2e` 共 737 案例，原碼全綠。重現用的假總表和變異副本在我自己的暫存目錄，已刪。）

### F1 `history --flaky` 的 `--last` 改成數原始行，重判行佔走名額，窗口內的不穩被漏掉
severity: major
blocking: yes
引句:「rows = collections.deque(maxlen=last)」
引句補:「         rows.append(r)」
file: `scripts/lumos:41488`（`_e2e_history_cmd`；上面兩句是 snapshot patch 裡同一個函式的相鄰兩行）
歸因:有證據的修復回歸（修前 150ef621 去重在 deque 之前；修後 745721d8 去重在 deque 之後）

1. 輸入：總表依序是 R1(第二次才過)、R2、R3、R4、R5，然後 R5 又被重判兩行（`--history` 重判會多寫一行），執行 `history --flaky --last 5`。
2. 走到 `_e2e_history_cmd`：deque 先收最後 5 行原始行，也就是 R3、R4、R5、R5、R5。R1 被擠掉，之後的 `_e2e_flaky_tally` 再去重也找不回來。
3. 計劃 S 第 3 步寫「最近 `--last` 筆（同一次執行重判的只算一次，數法跟點名同一套）」。點名用的是 20 個不同執行的窗口，兩邊對不上。
4. 兩版重現指令是 `python3.14 lumos.<版> android-e2e history --repo <proj> --flaky --last 5`：
   - 修前：`a.yaml  5 次裡 1 次第二次才過  最近一次證據 .lumos/artifacts/android/R1`
   - 修後：`最近 5 筆紀錄裡沒有第二次才過的 flow`
5. 測試抓不到：`t_android_e2e_flaky_history` 沒有「重判行貼著 `--last` 邊界」的案例，25 案例全綠。
6. 同一案例證據：
   - claim：`--last` 數的是不同執行。
   - input：上面那份總表。
   - expected：R1 仍在內，印 5 次裡 1 次。
   - case_source：我造的總表，一般 `--last 20` 加 2 次重判就會觸發。
   - before：印出 R1。
   - after：印「沒有」。
   - attribution：修復回歸。

### F2 組 B 宣稱的「從總表讀出的整行印前過 `_out_clean`」，其中兩處拿掉清理，測試照綠
severity: major
blocking: yes
引句:「print(_out_clean(f"  {mark[x['result']]} UI 流程 {x['flow']}{extra}{rp}", 4000))」
file: `scripts/lumos:42571`（`_e2e_print_runs`）
引句補:「print(_out_clean(f"  ! 不穩帳:{fl} 最近 {n} 次裡 {k} 次第二次才過;先看那幾次第一次的現場」（`_e2e_flaky_notify`）
歸因:有證據的原有漏查（測試缺口早於修補；修補後仍沒補）

1. 變異一：把 `_e2e_print_runs` 的 `_out_clean` 拿掉，改成直接 `print(f"…")`。跑 `python3.14 scripts/test_lumos.py -k android_e2e`，結果 737 passed, 0 failed。
2. 變異二：把 `_e2e_flaky_notify` 的 `_out_clean` 拿掉。跑 `-k android_e2e_flaky`，結果 25 passed, 0 failed。
3. 測試只有 `history` 一般輸出和 `--flaky` 兩處塞了 `\x1b`。UI 結果行（flow 名和現場路徑）與點名行都沒有控制字元案例。
4. 失敗場景：flow 名含 `\x1b[31m`（設定檔寫的外來文字）。拿掉清理後，終端會直接收到 ESC 序列，而且沒有任何測試會紅。
5. 這是修補本身宣稱要擋的錯，也是這兩處的唯一驗證，所以算 major。

### 已驗為成立的（只報事實）
- **`_e2e_flaky_tally` 執行鍵**（以修後版本直接呼叫函式）：
  - `0` 與 `"0"` 併成同一次，結果 (1,1)。
  - `False` 是獨立的一個鍵，不會跟別的合併。
  - `""` 與 `None` 每行各算一次。
  - 同一 run 先 flaky 後 pass，取最後判出的那次，結果是 0 次不穩。
- **窗口與重判**（窗口設 3，總表 R1 flaky、R2–R4 都過）：
  - 重判視窗內的 o3，位置不動，結果 (1,3)。
  - 重判已被擠出窗口的 R1，它會當最新一次進窗口並擠掉 R2，結果 (1,3)。
  - 修前 150ef621 也是這個行為，所以不是回歸，也沒有 file:line 層級的失敗場景；整體屬 minor 觀察，不另立 finding。
- **「只提醒」**：`_e2e_flaky_notify` 在 `_e2e_history_append` 最後呼叫，只 `print`，沒有路徑改判定、回傳碼或 `feature_runs`。`t_android_e2e_flaky_notice` 有斷言 `returncode == 0` 與 `fr.get("result") == "pass"`。
- **欄位改名（d）**：`evidence` 這個鍵在 base 20e1a255 不存在（本分支新增），所以讀舊查證紀錄不會壞。`git grep` 只剩 `scripts/lumos:42569` 一處讀 `fail_evidence`。
- **範本腳本 `after` 拿掉（組 E）**：`step()` 先存過一次，之後補 `evidence` 再存。被中斷時只是缺 `evidence` 欄，`_e2e_ui_evidence` 有用 dict 型別檢查接住。
- **效能（e）**：總表仍逐行讀（`_canary_ledger_rows`）；點名路徑有窗口上限，每支 flow 的 OrderedDict 最多 20 個鍵。`history --flaky` 本來就把最後 `--last` 行放進記憶體，修補沒有新增這個成本。

### 圖譜鏡頭固定席
- `guard-kill`、`lumos-cli-read`、`design-loop`、`測試假綠形態`、`lumos-cli-lifecycle` 的 ★INVARIANT★：不影響。理由是它們的合約講 guard kill 回傳碼、`--json` 純度、`search` 過濾、處置閘、re-inject 的位元組保留，diff 只動 `_e2e_*` 這一族和範本腳本，沒碰這些函式。
- `測試假綠形態`的「還原翻紅釘需前置斷言」：F2 的兩個變異就是它說的假綠，屬於相關但不是違反，已併入 F2。
- `loop-convergence-recording`、`pitfalls-code-loop`、`reversibility-governance-ledger` 的 ★RISK★：不影響，diff 沒改審查迴圈、可逆性帳本的程式。
- 其餘「只列名」的節點：不影響，理由同上。

### 修補鏡頭三問
1. **原問題修復效果**：
   - 空重判行蓋掉真判定：已修，有行為證據。同一 run 先判 flaky、後來一筆空項目，結果仍留 flaky（新測試「R1,R1{},7」綠，我也直接呼叫 tally 驗過）。
   - 數字與字串 `run_id` 算同一次：已修，`0` 與 `"0"` 併成一個鍵。
   - 欄位改名：已完成。
   - 輸出清理：`history` 與 `--flaky` 兩處有測試。UI 結果行與點名行只能說程式有改，行為沒有被測試證實，見 F2。
   - 去重重寫：修掉一個問題，同時引入 F1。
2. **修補處的正常、錯誤與相鄰呼叫路徑**：
   - 點名路徑（窗口 20，不同執行）正常。
   - `history --flaky` 加 `--last` 與重判行的相鄰路徑壞了，見 F1。
   - 一般 `history` 不經 tally，不受影響。
3. **新發現同一案例的修前、修後**：F1 修前印出 R1、修後印「沒有」；F2 兩版都沒有測試守，同樣是未判定回歸、屬原有漏查。

### 未驗範圍
- 沒有跑真的 Maestro 或 adb，範本腳本只靠讀碼與既有假 maestro 測試。
- 窗口內的測試空洞：`od.move_to_end` 與「同 run 保留第一次判定」這兩種改壞，`-k android_e2e_flaky` 25 案例全綠。因為只有「空重判」案例，沒有「先 flaky、後 pass」的案例（我只用函式直接呼叫確認行為正確），這是測試缺口但缺具體失敗場景，不單獨立項。
- 十萬行總表沒有實測，只憑讀碼判斷是逐行讀，沒有量時間與記憶體。

總結:整份最高嚴重度為 major
