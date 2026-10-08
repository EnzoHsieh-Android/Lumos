severity: major

審查範圍:/tmp/回頭條件寫法補齊-r1.md 全文,對照 rw 工作樹的 scripts/lumos。核對過存在的既有符號:`_revisit_split`、`_revisit_lines`(只有 E5 與 `_issue_close_revisits` 兩個呼叫端)、`_probe_lines`、`_ns_revisit_violations`、`_issue_close_revisits`、`_excluded_line`、`_ns_append_subtract`、`_NS_FRAG_KEY_RULES`、`_esc_clean`、`_SOFT_CAP`;被引用的計劃節點(回訪掃描、存量漂移防線、否定現況句配回頭條件、舊行尾追加不算新寫、筆記格子寫法與過期檢查、漂移防治路線圖、Systems 兩篇)與 `03-寫回圖譜.md` 都存在。

**U1 規格自己的摘要行會被自己的新規則擋下,而且「提到 `[closed:` 這個字」要不要豁免完全沒寫**
severity: major
blocking: 是 — 照字面實作,這份計劃自己的筆記提交時就被「結案標記寫錯」擋住,且所有講這個寫法的筆記都有同樣問題。
引句:「加一個行內結案標記 [closed:日期 理由],寫了就不再唸、不再評估」
1. 位置:開頭欄位 summary 的 WHY 行(第 19 行,沒包反引號),對照〈做法〉2.3 與 [S8]。
2. 問題:2.3 規定「新寫的行裡有 `[closed:`」,日期不是 YYYY-MM-DD、或寫在不是 REVISIT 的行,就報「結案標記寫錯」。規格只對 `REVISIT:` 在 [S3] 寫了「提到這個字、行內程式碼、圍欄不報」,對 `[closed:` 沒有等價條款。
3. 例子:summary 那行有 `[closed:日期 理由]`,既不是 REVISIT 行、日期也是字面「日期」→ 照字面實作,提交這份計劃就被擋。往後消費專案的說明或筆記要談這個寫法,也得全部包反引號。現有 `_ns_revisit_violations` 先剝行內程式碼(`probe = _strip_inline_markup(ln)[0]`)才判,但規格沒規定新規則是判剝過的還是原文。
4. 佐證:file: `scripts/lumos:27915-27922`(先剝行內再判)、規格第 19 行與第 23、29、56 行(後三處有包反引號,只有第 19 行沒包)。

**U2 「結案日期不可晚於提交當天」用本機日期,CI 用另一個時區,照規格建議的寫法(結案日寫當天)反而會被 CI 擋**
severity: major
blocking: 是 — 台灣時間 00:00-08:00 寫當天日期,本機提交過、推上去 CI 擋,出口只剩改日期或跳過。
引句:「時區差一天可能誤擋或誤放,寫法是結案日寫當天,影響極小」
1. 位置:〈實務隱患〉跨環境、〈做法〉2.3「日期在提交當天之後」、[S8]。
2. 問題:規格把「提交當天」寫成本機日期,但同一支 `note-shape --diff` 也在推送前與 CI 跑(1.2 明說),CI 通常是 UTC。「誤擋或誤放」只講一半:作者在 UTC+8 的凌晨寫「結案日寫當天」,本機日期比 UTC 早一天,CI 判成「日期在未來」。這是每天固定約 8 小時的誤擋窗口,不是偶發。
3. 例子:2026-10-04 07:00(台北)寫 `[closed:2026-10-04 已改用新閘道]` → 本機過;CI 當時 UTC 是 10-03 → 報「結案標記寫錯」,同一個提交晚幾小時重跑就過,結果不確定。
4. 修法方向在規格裡缺席:至少要寫明比較用哪個時區、或容許未來一天。
5. 佐證:doctor E5 也用 `_dt5.date.today()`(file: `scripts/lumos:2292`),規格沿用了本機日期,但 E5 是本機報表,不是會擋推送的閘。

**U3 刪除線的改法指示照字面做會被自己的新規則擋掉**
severity: major
blocking: 是 — 規格給作者的唯一指引,執行後馬上撞「結案標記寫錯」。
引句:「doctor 列出時改法多一句「要結案就改成 `[closed:日期 理由]`」(第 2 節)」
1. 位置:〈做法〉1.4 對照 2.1、2.3。
2. 問題:1.4 說 `~~REVISIT:…~~` 是句中(行首是 `~~`,`_revisit_split` 判不是 REVISIT 行)。2.3 規定 `[closed:` 寫在「不是 REVISIT 的行」要報錯。兩句同時成立時,作者在刪除線那行補 `[closed:…]` 必被擋;把整行換成 `[closed:…]` 單獨一行,那行也不是 REVISIT 行,一樣被擋。唯一合法做法是拆掉刪除線、還原成真正的 `REVISIT:日期 … [closed:…]`,規格沒說,「改成」兩字更像「取代」。
3. 例子:`~~REVISIT:2026-10-05 查 X~~`,作者照 doctor 提示改成 `~~REVISIT:2026-10-05 查 X~~ [closed:2026-10-03 X 已不需要]` → 提交時報「結案標記寫錯」;而這行同時仍被判為句中 REVISIT,兩條規則一起報。
4. 佐證:`_revisit_split` 只剝一層列表或引用記號(file: `scripts/lumos:31693`,`_REVISIT_MARK_RE`),不認 `~~`、`**`、`★`。

**U4 E5 對存量不再「全靜默」,而且每次 doctor 都寫一筆「warned」治理帳,跟 Z 段刻意不寫帳的理由相反**
severity: minor
blocking: 否 — 只是提醒噪音與帳的口徑問題,不影響擋推送。
引句:「全靜默慣例不變:沒有到期、沒有壞行、沒有句中的就整段不印。」
1. 位置:〈做法〉1.3、[S5]、[S10]。
2. 問題:規格自己量到工具鏈圖譜約 68 行句中 REVISIT。E5 現行 `if _rv_due or _rv_bad:` 才印段並寫 `check-revisit` 的 `warned` 事件(file: `scripts/lumos:2316`、`2332`)。加了 misplaced 後,工具鏈 repo 在清完 68 行前每次 doctor 都印、每次都寫事件,而且 `nodes` 是到期筆記 stem,句中只有存量時 nodes 為空。「全靜默」成立的條件被存量永遠破壞,「不寫額外的帳」與「新增每日事件」互相矛盾。
3. 對照:Z 段註解寫「不寫治理帳——這些是存量,每天唸同一批會被 nags 升級成噪音」(file: `scripts/lumos:2339`),規格沒回應為什麼 E5 反過來。
4. 例子:`lumos doctor` 在無到期、無壞行、68 行句中的工具鏈 repo → 印 E5 段並記 `due=0 bad=0 misplaced=68` 的 warned,每天一筆。

**U5 「列前 5 個位置」與 doctor 軟提醒每段最多顯示 3 條互相衝突**
severity: minor
blocking: 否 — 實作時會自己發現,但規格沒說位置放哪,測試 [S5] 沒法寫死。
引句:「並列前 5 個位置(`節點:行號`,過 `_esc_clean`)」
1. 位置:〈做法〉1.3、[S5]。
2. 問題:`warn_soft` 預設只印 `_SOFT_CAP = 3` 條,其餘收成「另 N 條」(file: `scripts/lumos:1379`、`1383-1394`)。E5 現有註解還特別說「壞損數進 head 不進 lines(cap3 會把它吞進「另 N 條」隱形——head 恆可見)」。規格要「開頭行說 N 行…並列前 5 個位置」,沒講位置寫進 head(變很長)還是 lines(只看得到 3 個,而且排在到期清單後面)。
3. 例子:有 4 條到期加 68 行句中 → lines 先放到期,位置放 lines 就整個被吞成「另 N 條」;[S5] 要驗「前 5 個位置」無從驗。

**U6 「開頭欄位其他欄都不會被讀到」與 E5 現況不符,第 1 節判定也跟第 3 個命中位置打架**
severity: minor
blocking: 否 — 影響的是少見的形狀,但規格對現況的宣稱是錯的。
引句:「寫在句中、表格或開頭欄位其他欄都不會被讀到」
1. 位置:〈做法〉1.2 的改法文字、1.3、[S2]。
2. 問題:`_revisit_lines` 走 `_search_visible_lines`,開頭欄位的行也在範圍內;開頭欄位某欄的多行字串裡,行首的 `REVISIT:2026-10-05 …` 會被 `_revisit_split` 判成日期式,E5 會讀到、會唸到期。但 1.1 把「misplaced」定義成「`_revisit_split` 判不是 REVISIT 行」,[S2] 又要求開頭欄位其他欄裡的 `REVISIT:2026-10-05` 一律報句中。行首那種形狀:依 1.1 不算 misplaced,依 [S2] 要報,規格內互相矛盾;依實際程式 E5 其實讀得到,「不會被讀到」錯。
3. 佐證:`_ns_revisit_violations` 對非 body/summary 區塊本來就不查 `_revisit_split`,只看 `_PROBE_ANY_RE`(file: `scripts/lumos:27940-27943`);`_probe_lines` 同樣只把條件標記列成不評估(file: `scripts/lumos:31853-31863`)。

**U7 `[closed:日期 理由]` 的右括號文法沒定義,理由裡出現 `]` 會被截短**
severity: minor
blocking: 否 — 誤報而已,但規格要求「附提交或測試更好」,正好會寫 `[test:…]` 或 `[[連結]]`。
引句:「理由要寫為什麼不用再回頭(附提交或測試更好),至少 4 個實字」
1. 位置:〈做法〉2.1、2.3、[S8]。
2. 問題:規格沒寫標記的抽取正則。既有 `_PROBE_ANY_RE` 是 `\[when-…:[^\]\n]*\]`,碰到第一個 `]` 就收。理由裡寫 `[[Systems/x]]`,理由被截成 `[[Systems/x`,實字數可能不到 4;也沒規定行內程式碼包住的 `` `abc` `` 在數字數前是否先被 `_strip_inline_markup` 剝掉(`_excluded_line` 是先剝再數)。
3. 例子:`[closed:2026-10-03 見 `t_x`]` → 剝掉行內程式碼後理由只剩「見」→ 不到 4 個實字,擋。
4. 佐證:`_excluded_line` 先 `_strip_inline_markup` 再數(file: `scripts/lumos:6396-6405`)。

**U8 另案與回頭條件壞損行的處理沒交代,`_revisit_lines` 新參數沒有使用者**
severity: minor
blocking: 否 — 屬於可執行性缺口。
引句:「讓它多一個參數決定要不要排除已結案的(預設排除;兩個既有呼叫端都排除)」
1. 位置:〈做法〉2.2、〈做法〉3 最後一點、〈範圍〉。
2. 問題 a:預設排除、兩個既有呼叫端都排除,那新參數沒有任何呼叫端會傳「不排除」,等於死參數;而 1.3 要數句中,要掃的是 `_revisit_split` 回 None 的行,正是 `_revisit_lines` 一開始就丟掉的(`if kind is None: continue`),規格沒說句中計數在哪個迴圈做。
3. 問題 b:`bad` 種類的行(日期格式壞損)帶合格 `[closed:…]` 時,2.1 說「REVISIT 行(日期式或條件式)」,E5 到底算不算壞行沒講;`_ns_revisit_violations` 對 bad 先回「回頭條件格式不合」,結案標記的檢查跟它誰先誰後也沒講。
4. 問題 c:〈範圍〉與〈做法〉3 要求路線圖「第 6、11 項連到另案」,但本計劃沒有建立那份另案,也沒給名稱;路線圖現況只寫「3 的四項」(file: `docs/lumos-toolchain-knowledge/Projects/漂移防治路線圖_計劃.md:62`),連過去就是懸空連結。
5. 佐證:file: `scripts/lumos:31727-31729`(`_revisit_lines` 對 None 直接 continue)、`scripts/lumos:2303-2306`。

已讀,無 finding 的節:〈範圍〉其餘部分、〈回退〉、〈天花板〉、〈實務隱患〉中的繞過、效能、併發、回滾、相容項、已排除三行。

實務隱患逐類:
- 繞過:`[closed:日期 4 個字]` 就能讓已成立的條件式回頭條件不再擋推送,[2.6] 已承認是選擇;與 `drift ack` 相比少了表態檔的綁行原文與獨立審計,規格以「可搜尋」為由接受,已讀,無新 finding。
- 效能:`_ns_revisit_violations` 只對新行多一個正則;E5 本來就逐行 `_strip_inline_markup`,無。
- 併發:不寫檔,治理帳走既有寫入器,無。
- 回滾:單一提交可還原;還原後已寫入的 `[closed:` 變回普通文字,已在規格寫明,無。
- 誤擋與繞過:U1、U2、U3 各有一條誤擋路徑,規格只靠既有單次跳過與專案開關。

最嚴重 severity:major;blocking 共 3 條(U1、U2、U3)。
