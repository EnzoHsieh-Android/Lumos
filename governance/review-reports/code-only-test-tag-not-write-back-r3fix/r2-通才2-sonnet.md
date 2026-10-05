severity: minor

# r3fix 驗收 r2 通才席報告

範圍:r2-delta.patch(test-gone 改回整串一致、空白規則改成後面不是英數或中文才吞前面空白),夾具用 `scripts/test_lumos.py:46999` 的 `_nh_tag_repo`,兩道檢查(home check 的 `--diff`、note-shape 的 `--diff`)每個案例都實跑。

## 沒繞過的路(實跑)

- test-gone 前綴夾帶:`[test-gone:python:test_old@abc1234]` 與連字號英文前綴,只要跟上一版 `[test:]` 不是整串一致就擋;整串一致的只是改標記、沒帶新字。
- 新 `[test:]` 的前綴夾帶:`a-now-retries-three-times-then-logs:test_alive`、`a_now_retries_three_times:test_alive`、全形冒號版、合約行版,home 全部 rc1(判定會核對前綴,note-shape 也報 bad-name)。
- 空白規則:標記插在字中間、全形空白、標記後接句號、中文旁加空格、標記夾在句中,都只是空白差異,沒有能多帶出字的形狀;標記後接中文或英數時空白照留,行為跟說明一致。
- 值的路徑:逗號清單裡摻非識別字、`@` 後接非提交編號、`test_alive @abc1234` 這種,都因新名稱要單一識別字而擋。

## Finding 1:設定檔新增平台名,等於免費的任意連字號英文前綴,說明藏得進合約行

severity: minor
blocking: 否——要先在同一範圍改 `.lumos/config.json`(一個會出現在 diff 裡、不尋常的改動);判準:需要額外的、顯眼的前置動作才能開洞,不是單一筆記編輯就能繞。
file: `scripts/lumos:29960`(`_NsTrJudge._plat` 靠 `resolve_test_refs` 認平台前綴,平台名來自設定檔)
引句:「_NODEHOME_TAG_NAME_RE = re.compile(r"(?:[A-Za-z0-9_-]+:)?[A-Za-z_][A-Za-z0-9_]*")」

失敗場景:前綴的字元集允許連字號英文、長度只受 200 字限制;判定只核對「前綴是不是設定檔裡的平台」。把平台名取成一句話,就能讓說明包成合法綁定,兩道都過。
最小重現(臨時 repo,夾具 `_nh_tag_repo`,B 是合約行 `KEY:★INVARIANT★ b 規則 [test:test_alive]`):同一個提交裡
1. `.lumos/config.json` 改成 `{"platforms":{"retries-three-times-then-logs":{"profile":"python","root":"tests"}},"default_platform":"retries-three-times-then-logs"}`
2. 改 `src/a.py`
3. B 的合約行多寫 `[test:retries-three-times-then-logs:test_alive]`

實跑結果:`home check --diff base..HEAD` rc=0(只印「它的家這次沒動」提醒);`note-shape --diff base..HEAD` rc=0、無輸出。對照:同一個案例沒改設定檔時 home rc=1、note-shape 報 bad-name。
補充:同樣設定下 `[test-gone:retries-three-times-then-logs:test_alive@abc1234]` 會被 note-shape 的「test-gone 的測試還在」擋(那是 warn 組,不是 home 擋的),home 本身 rc=1,所以只有 `[test:]` 這條通。
天花板 5 只提到「工作目錄有沒提交的設定改動」不豁免,沒涵蓋「設定改動已在同一範圍提交」。
取捨:要補的話,前綴只收設定檔在上一版(base)就有的平台名,或限制前綴為已知棧名;不補就把它寫進〈天花板〉並附 RETIRE-IF 觸發。

## 結論

兩項本次修正(test-gone 整串一致、空白規則)本身驗過沒有新洞;唯一找到的新路是上面這條需要先改設定檔的前綴夾帶。

總結:全份最高等級 minor
