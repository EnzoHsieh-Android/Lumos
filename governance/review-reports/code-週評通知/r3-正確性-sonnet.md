severity: major

我沒有找到會讓判斷邏輯該叫不叫、不該叫亂叫的 bug。基準不足的退路在 summarize 的語意下與舊規則 `p≠n` 等價。事故週另外照規格一律通知。

我用 `git archive` 取出 `cc137467` 的複本,在 /tmp 下改壞 shell 與 Python 逐條驗,並用抽出的 `run_probe` 在沙盒跑 shell。主要發現是測試有假綠,另有兩個小問題。

## 1. 「否」判定不印 MSG 這個分支沒有任何測試守住
severity: major
blocking: 是
引句:「if alert.startswith("週評通知:是"):」
歸因:有證據的修復回歸。MSG 機制是 r3 修補才加的。
1. 最小重現:在複本的 `scripts/scenario_probe.py` 把該行改成 `if True:`,再跑 `-k weekly_alert`、`-k t_probe_history_records_ids`、`-k t_autoloop_probe_alert`。結果是 26、4、6 全綠。
2. 為什麼沒翻紅:
   - S4 只檢查「是」的情況會印一行 MSG。
   - S5 的 shell 測試用假探針,Python 這一側根本沒跑。
3. 壞處:這個改壞等於每週一律發 LINE,正是這次要修的原問題。shell 見到 MSG 行就送,不看判定行是是還是否。我用沙盒跑了「判定行是『否』且有 MSG 行」這個輸入,LINE 照送。
4. 缺的測試:判定為「否」時,主程式的輸出不含任何 `MSG:` 行。
file: `scripts/test_lumos.py:42500`(約略位置,S4 的 msg 檢查段)

## 2. 沒有判定行時,雜散的 MSG 行仍會被送出
severity: minor
blocking: 否
引句:「msg="$(sed -n 's/^MSG://p' "$LOGDIR/probe-$TODAY.log" | tail -1 || true)"」
歸因:有證據的修復回歸。
1. 輸入:探針 log 是 `8/8 個情境 … 自己敲對了` 加一行 `MSG:hello`,沒有 `週評通知:` 行。
2. 走到哪:`msg` 在判定行判斷之前就先從 MSG 行取值。`[ -z "$verdict" ] && … p≠n` 只在 `p≠n` 時才會覆蓋它。
3. 結果:全過(8/8)卻送出「hello」。註解寫的是「沒有判定行才退回 p≠n」,行為和它不一致。
4. 觸發條件:真實探針只在印了判定行之後才印 MSG,所以只有 log 混進以 `MSG:` 開頭的雜訊行才會發生。
5. 建議:只在 `-n "$verdict"` 時才讀 MSG。
6. 測試缺口:把 `sed` 的 `s/^MSG://p` 改成 `s/^MSG//p`,測試仍全綠,因為只用 `in` 子字串比對。

## 3. MSG 行會被當成總結行,log 的「情境探針結果」顯示錯行
severity: minor
blocking: 否
引句:「local line; line="$(grep -E '個情境 Claude 自己敲對了' "$LOGDIR/probe-$TODAY.log" | tail -1 || true)"」
歸因:有證據的修復回歸。MSG 內含總結行文字,所以 `tail -1` 會取到 MSG 行。
1. 重現:沙盒輸入 `6/8 個情境 Claude 自己敲對了…`、判定行「是」、MSG 行。
2. 結果:log 寫成 `情境探針結果:MSG:情境探針本週要看:6/8 個情境 …`。
3. 影響:只有這行 log 文字不對。有判定行時 `pp`/`tt` 不會被用到,不影響是否通知。

## 4. 其餘測試缺口(未要求通知,單獨列出)
我逐條改壞 `weekly_alert` 相關程式。大部分都會翻紅,包括 runs、grader、同週去重、inconclusive 與 fatal 兩個旗標、基準週數門檻 2 和 4、重複失敗取最近一次、合計 Wilson、`except Exception`、`ids` 取有效場次、訊息組裝。下面這些改壞後測試仍全綠:
1. `arm == "with"` 篩選改成 `True`:沒有任何 `arm` 不是 with 的測試列。
2. `isinstance(r.get("passed"), int)` 改成 `True`:缺 `passed`、有 `total` 的列沒有測試。
3. `cur and base` 的 `cur` 判斷:`total=0` 的列只會在 inconclusive 時出現,屬等價改動。
4. 下面兩項不值得補測。
   - 把 `cur[1] < base[0]` 改成 `<=`,只差等號的邊界。
   - `not g` 改成 `False`,是等價改動。

## 三問
1. **原問題的修復效果**:有行為證據。沙盒跑出的結果:
   - 判定行「否」時不送 LINE。
   - 判定行「是」且有 MSG 時照原樣送出。
   - 有判定行但沒有 MSG 時不送。
   - 沒有判定行時退回 `p≠n`。
   - MSG 內含 `%`、`$(id)`、反引號、`\n` 都原樣轉交,沒有被 shell 展開。
   - `set -euo pipefail` 下全程 rc=0。
2. **修補處的相鄰路徑**:正常、錯誤、相鄰路徑大致成立。例外是第 1 點的「否」分支測試缺口,以及第 2、3 點的 MSG 行處理。
3. **同一案例修前與修後**:修前沒有 MSG 機制,第 2、3 點的案例不會出現。修後第 1 點是測試擋不住的回歸路徑,第 2、3 點如上。

清理:我刪了 /tmp 下自己的工作目錄,以及能確認是自己跑出來的 4 個 `gctl-run-*` 紅燈現場中的一部分。其中 `gctl-run-gi_ao594`、`gctl-run-qeq114h7`、`gctl-run-af0fh0dj`、`gctl-run-_e72l2e2` 因目錄非空沒刪成。其餘 `gctl-run-*` 無法確認是不是我的,所以沒動。

總結:最高等級 major
