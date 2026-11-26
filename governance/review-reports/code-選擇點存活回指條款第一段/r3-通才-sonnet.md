severity: minor

固定席判定:`bound-tests-gate`、`guard-kill`、`lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`、`design-loop` 這幾個節點上的合約,這份修補都沒碰。`guard-kill` 的 PITFALL 行已改成「after 固定回 6 項」,和程式一致。`t_choice_cov*` 全跑的那次在背景執行,我沒等到結果,所以沒有跑過的證據,以下全是讀 diff 與呼叫端得出的。

上一輪修的項目大致都修到了:
- **after 的呼叫者**:`_kill_measure_singles` 的呼叫端只有兩個,合併快篩不傳 `after`,準備物件傳 `cb.after`。沒有第三個呼叫端還在讀舊的 5 項形狀。
- **`_choice_cov_parse` 改嚴**:真的分析腳本三個鍵都寫(`scripts/lumos:79657`),所以沒有真實輸入被誤判成失敗。
- **假 Gradle**:改成三鍵都寫,另一條 `omit_keys` 讓它能省略鍵。這兩處不會影響其他測試。

我只找到兩條小問題,沒有 blocker 或 major。

severity: minor
blocking: 否
`scripts/lumos:29294`:`red_rerun` 的 docstring 還寫著「回傳 5 項:第 5 項是兩趟加起來的秒數」,但這次修補後所有路徑都回 6 項,多了「被截斷」。後來的人照 docstring 解 tuple 會少一項,而 `_kill_measure_singles` 的 `b_rc, b_tail, b_el, b_to, spent, cut = after(...)` 是嚴格解包,錯了會直接丟例外。
引句:「紅記基準不綠;連續 _CHOICE_COV_RED_BREAKER 支掛覆蓋才紅就斷路(代碼審 r1 F3)。回傳 5 項:第 5 項是兩趟加起來的秒數,_kill_measure_singles 拿它估剩下的。」

severity: minor
blocking: 否
`scripts/lumos:29297`(`red_rerun`):掛覆蓋逾時現在先 `self.trip(...)`、後才跑不掛的重跑。一支測試本身不掛覆蓋也會逾時(慢測試或會卡住的測試),也會讓整個平台組的覆蓋被永久關掉,訊息還錯寫成「覆蓋設定讓測試卡住」。重跑確認原因之前就斷路了,所以這一支其實是這個平台組多數測試的覆蓋都白白失去,只是回退到逐支跑,不會判錯。重現:用 `_ckc_cb_stub` 讓 `_kill_run` 回 `(1,"",600.0,True)`,對 `red_rerun` 傳 `(1,"",600.0,True), 600.0`,結果是 `tripped` 為真且 `why` 為「基準不綠」。建議等重跑結果、確認不掛也紅才不斷路。
引句:「if res[3] and not self.tripped:   # 掛覆蓋跑滿單支上限:比掛覆蓋紅更強的訊號,當場斷路,不等連續 3 支(代碼審 r2 資源 s2)」

另外檢查過、沒找到失敗場景的點:
- **`_choice_cov_prune` 的 `subs[_CHOICE_COV_KEEP - 1:]`**:這次的 at_sha 先排除,保留數算這次,邊界正確。
- **`robo_zero` 進出快取**:`cached()` 讀回與 `store(keep=...)` 對稱。0 筆的 Robolectric 資料落到 scratch 檔名 `lumos-cov-{len(self.got)}.exec`,`take` 會先加進 `got`,所以不會撞名。
- **`_write_bytes_atomic` 取代手寫 tmp**:簽名吻合,`OSError` 仍被接住。
- **新測試的重點**:`t_choice_cov_groovy_dep` 在沒有本機 Groovy 時只做靜態檢查,拿掉 `*.toString()` 仍會紅。`t_choice_cov_parse_keys` 沒測 `noclasses` 為非布林值(例如 `"false"`)的分支,只是覆蓋度的缺口,不是假綠。

總結:最高等級是 minor
