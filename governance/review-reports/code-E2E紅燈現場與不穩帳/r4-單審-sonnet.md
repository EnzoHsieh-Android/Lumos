severity: major

### F1 `history --flaky --last N` 的「丟最舊一次」方向沒有測試釘住
severity: major
blocking: yes
引句:「                if len(runs) > last:
                    runs.popitem(last=False)」
file: `scripts/test_lumos.py:19715`、`scripts/test_lumos.py:19749`
歸因:有證據的修復回歸(`popitem` 是 7b03691f 這次修補新寫的;修前用 `deque(maxlen=last)`,方向由標準庫保證。測試空洞也出在修補新加的那條)

1. 改壞方式:把 `popitem(last=False)` 改成 `popitem(last=True)`。超過 `--last` 次執行時就會丟最新那次、留最舊的,違反 S6「最近 `--last` 次執行」。
2. 現有測試抓不到這個改壞。
   - `--last 1` 那條用 h1(flaky)、h2、h3(flaky),只比對子字串 `"1 次裡 1 次"`。留下最舊的 h1 也印出同樣一句。
   - 新加的 `--last 5` 那條剛好 5 次執行,從沒超過上限,`popitem` 一行都沒走到。
   - 其他 `--flaky` 測試的執行數都小於預設的 20。
3. 兩版查證:
   - 在 `e98debe1` 複本改成 `last=True`,跑 `python3.14 scripts/test_lumos.py -k android_e2e_flaky_history`,結果 `14 passed, 0 failed`(照綠)。
   - 同一份改壞程式跑實際帳:帳是 A(不穩定=否)、B、C(不穩定=是)三次執行,執行 `lumos android-e2e history --flaky --last 2`,印出「最近 2 次執行的紀錄裡沒有第二次才過的 flow」。正確結果應是 `login.yaml  2 次裡 1 次…證據 …/C`。
   - 原版 `e98debe1` 印的是正確結果。修前版 `745721d8` 的 deque 也印出正確的 C。
4. 同一個測試也沒釘 `n_runs`(`len(runs)`)那句「最近 N 次執行」的數字。「沒有」那條只比對子字串 `"沒有第二次才過的 flow"`。這個隨附問題只算 minor。
5. 證據欄位:
   - claim:`--last` 保留最近 N 次執行
   - input:A/B/C 三次執行、`--last 2`
   - expected:列出 C 的不穩
   - case_source:自造的帳,見上
   - before:修前 745721d8 輸出 C 那行
   - after:原版輸出 C 那行;改壞版輸出「沒有」,但測試照綠
   - comparison:實作本身正確,缺的是測試的行為斷言

### F2 judge 終端輸出還有未過 `_out_clean` 的出口(`problems` 行與截圖行)
severity: minor
blocking: no
引句:「         print(f"  ? {p}")」
file: `scripts/lumos:41214`(`_e2e_tool_problems`:`{_e2e_tail(st[-1].get('stderr'), 200)}` 讀 steps.json 指到的 stderr 檔)
歸因:有證據的原有漏查(`_e2e_print_runs` 這幾行修前就是原樣印出,修補沒碰也沒測;修補測試與計劃宣稱的「四個出口都過」只涵蓋 UI 那一行)

1. 輸入:steps.json 的 build 步驟 stderr 檔內容含 ESC 序列或 U+2028,或截圖的 screen 名、reason 含控制字元。
2. 走到 `_e2e_print_runs` 的 `print(f"  ? {p}")` 與 `print(f"  {mark[...]} {label} {x[key]}{extra}")`,都沒過 `_out_clean`。
3. 兩版查證:用 `745721d8` 和 `e98debe1` 各載入 `scripts/lumos`,餵 problems=`["build 回 1:\x1b[31mBOOM\x1b[0m\u2028x"]` 和截圖 screen=`"s\x1b[31m"`。兩版輸出的 repr 都帶原始 ESC 與 U+2028,結果相同。
4. 在 lumos 的威脅模型(單人自用)下只算 minor。但它與本案(d)問的「第五個出口」吻合。

## 圖譜鏡頭(固定席)

- **guard-kill、lumos-cli-read、lumos-cli-lifecycle、design-loop、測試假綠形態的 INVARIANT:不影響。**
  - 這份 diff 只動 `scripts/lumos` 裡 `_e2e_*` 一帶,加上 `android-e2e history` 的 `--flaky` 旗標。
  - 沒碰 guard kill 的 rc 優先序與 `--json` 純度,沒碰 search 的 superseded 濾網,沒碰 re-inject 的 sentinel,沒碰處置閘第五步。
  - 測試假綠形態那條要求「還原修法會翻紅」。F1 正是這條的實例:`popitem` 方向還原了測試仍綠。
- **loop-convergence-recording、pitfalls-code-loop、reversibility-governance-ledger 的 RISK:不影響。**
  - 本案沒改它們管的審查帳、凍結或可逆性邏輯。
  - 只改本機總表(history.jsonl)的讀端,沒有新增寫入的紀錄種類。新欄位 `flaky` 舊程式讀到會忽略,新程式讀沒有 `flaky` 的舊行當不穩定=否。
- **「只提醒」保證:成立。**
  - `_e2e_flaky_notify` 在 `_e2e_history_append` 最後一步,只做 print,`OSError` 被接住。
  - `--flaky` 路徑走 `return 0`。
  - 沒有任何路徑回頭改 `runs["result"]`、回傳碼或 `feature_runs`。`case_results` 的 flaky 只加在總表那份(`dict(i, flaky=True)` 是新字典,沒動 `runs["cases"]` 原件)。
- 沒有「這次新增的殘留」段,也沒有帶殘留徽章的合約行,殘留問答不適用。

## 本案特定鏡頭

- **(c) 歸併邊界。**
  - 我實跑了沒有 run_id 的舊行、`--last 1` 和重判重複行,行為正確。
  - 沒有 run_id 的行各算一次。
  - `--case` 篩掉部分行後,同一執行只剩空項目的行仍占一個 `--last` 名額,但這與「最近 N 次執行」的字面一致。
  - 一個 run_id 在窗口外出現後又被重判,會當成新的一次放到最後。這與 `_e2e_flaky_tally` 的「位置照第一次出現」一致,未判定為 bug。
  - 讀端不會產生 `run_id == ""`:寫端用 `steps.get("run_id") or Path(run_dir).name`,空字串會落到後備值。因此 `_e2e_run_key` 拿掉 `rid != ""` 不構成迴歸。
- **(e) 效能。**
  - 十萬行總表(每執行 5 次重判、每行 8 個項目)跑 `history --flaky`,耗時 1.3 秒,最大記憶體 344MB,與只有 3 行的總表同為 344MB(基線是載入腳本本身)。
  - `--last 1000000` 時耗時 2.0 秒,記憶體 719MB。這是呼叫者自己要求保留全部,與修前 deque 同量級。
  - 點名路徑逐行讀,每支 flow 的窗口有界。

## 修補鏡頭三問

1. **原問題的修復效果:有行為證據。**
   - claim:重判多寫的行不再佔 `--last` 名額。
   - input:R1(不穩)、R2~R4、R5 三行,`--last 5`。
   - expected:`5 次裡 1 次`。
   - case_source:自造的帳。
   - before:`745721d8` 印「最近 5 筆紀錄裡沒有第二次才過的 flow」。
   - after:`e98debe1` 印 `5 次裡 1 次…證據 …/R1`。
   - comparison:修前錯、修後對。這條只證明去重,不證明丟最舊的方向(見 F1)。
2. **修補處的正常、錯誤與相鄰路徑:成立,測試有缺口。**
   - 不加 `--flaky` 的一般 `history` 仍走 `deque`,沒變。
   - 點名路徑(`_e2e_flaky_counts`)沒受影響。
   - 空項目重判行不蓋掉判定、數字與字串 run_id 合併,都有測試覆蓋,且我確認這些測試對應的行為是對的。
   - 缺口是 F1。
3. **新發現的同一案例在修前、修後的結果:**
   - F1:修前是 deque 的標準行為(方向正確);修後實作正確,但測試無法偵測方向反轉。屬修補新增的測試缺口。
   - F2:修前修後相同,原有漏查。

未驗範圍:
- 範本腳本內嵌 Python 的實機 adb/maestro 路徑,我只讀程式碼,沒實跑。
- `logcat -T` 用 `.000` 取整到秒,可能把前一次嘗試同一秒內的閃退算進下一次,這點也只讀未跑。
- 「測試通過就代表問題解決」不成立,只有 F1 實跑過的那組。

我在 `/tmp/lumos-seat-work/code-E2E紅燈現場與不穩帳/單審-sonnet/` 的暫存已用字面絕對路徑刪除。

總結:整份最高嚴重度為 major
