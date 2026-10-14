severity: minor

已讀,無 finding 的部分:`_residual_index_write` 改成三元組後,所有呼叫端都跟著改了(`--reindex` 與 `_residual_reindex_tail`)。舊索引多帶 `tests` 欄,pitfalls 與 doctor 都不看,讀得進來。沒有殘留的 repo 裡,`pitfalls --diff` 照舊分級(我在臨時 repo 實測 `HEAD~1..HEAD` 得 standard,`HEAD` 得 light)。guard audit、kill-add 與 `_contract_locate` 沒被動到。`_strip_test_comments` 只是搬位置,沒有重複定義。`-k residual` 跑了 212 個測試全過,`-k guard_audit` 跑了 14 個全過。我沒另外跑 doctor 其他段落、contracts 輸出與逃逸帳,這幾塊只從 patch 判斷沒被動到。

severity: minor
blocking: 否 — 有繞路(換反例編號重問),而且只影響同節點內有多條殘留合約的情形。
引句:「判過 testable 的反例看整個節點、不看指紋」
問題:「判過 testable」改成以節點加反例正規形為準,但反例編號慣例上是每條合約各自從 c1 起算(`--case` 說明的範例就是 `c1`)。同一個節點只要有一條合約的 c1 被判過 testable,同節點其他合約的 c1 就全受牽連。
失敗情境:節點 N 有合約 A 和合約 B。B 先對 c1 記了 untestable,合約行也已寫入 `[residual:]`。之後 A 的 c1 被判 testable(正常流程,補測試就好)。這時 `_residual_check` 的 `verdicts(k)` 對 B 的 c1 多加了 testable。doctor 不帶 cases 的路徑會報「反例 c1 同時有判 testable 與 untestable」,B 的 `ok` 清單也變空,於是 B 的殘留標記整個變紅。B 原本合格的標記要重問第二個代理、換新編號才能修好。反過來先判 A 再問 B 的 c1,也會被 `--add` 擋下,訊息要人換編號。這是「改字換指紋」防堵對編號慣例的副作用,比對的鍵應該帶合約身分,例如 `(節點, 反例)` 加上條款起首或一個固定識別。
佐證:file: `scripts/lumos:18930`(`_residual_testable_cases` 與 `_residual_ask_index`);file: `scripts/lumos:19050` 附近(`verdicts` lambda 的 `hard` 併入)。這條我只靠讀程式推論,沒有實際造 vault 重現。

severity: minor
blocking: 否 — 是刻意的退讓,代價是多升 high,不會漏放行。
引句:「兩種檔都整檔算命中(代碼審 r2 G1:上一輪把測試檔收窄成」
問題:綁定測試所在的檔改成整檔算命中。本 repo 的 `scripts/test_lumos.py` 是單一大檔,而且幾乎每次改動都會碰到它。
失敗情境:一旦圖譜裡出現任何一條帶 `[residual:]` 且綁了 `test_lumos.py` 內測試的合約,之後每次碰到那支測試檔的推送都升 high。這會要求過代碼審,即使改的測試與該合約無關。目前 `governance/residual-index.json` 不存在,所以現在不觸發。
佐證:file: `scripts/lumos:44493`(`_residual_index_view`)。

severity: minor
blocking: 否 — 刪改治理帳的情況少見,誤報只是多升 high。
引句:「只看 -U0 diff 的刪除行(改一列 = 刪一行加一行);新增的問答不算。」
問題:`asks_dropped` 只靠 diff 的刪除行判斷,所以任何會重寫治理帳的操作都會誤判。例如在最後一列沒有結尾換行的帳上續寫,git 會把最後一列顯示成一刪一增。
失敗情境:帳尾那列剛好是 residual-ask,又沒有結尾換行,單純續寫新事件就會被算成「刪掉一筆問答」,推送被升 high。
佐證:file: `scripts/lumos:44520` 附近(`_residual_ask_rows_dropped`)。這條也沒有實際重現。

最高等級 minor,blocking 0 條。
