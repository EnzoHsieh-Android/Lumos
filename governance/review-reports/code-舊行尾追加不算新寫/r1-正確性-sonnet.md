severity: minor

我逐 hunk 讀完整份 diff,並在臨時目錄實跑:
- 子集測試 `ns_append` 65 項、`note_audit` 332 項、`notelines` 10 項全綠。
- 對 `_notelines_parse_added` 與 `_notelines_parse_hunks` 做隨機模糊測試:400 組、內容夾 `++ x`、`@@`、`\ No newline`、`diff --git`,並設 `diff.interHunkContext=5`。新舊行號和文字全部對得上,零不符。

沒找到會讓「一行全新、沒寫來源的現況句」被當成舊行尾補括號而放行的路徑。插在前面、搬位置、改一個字、圍欄進出、`\r` 或尾端空白、重建標記、改名、二進位都照整行查。第一層扣減確實在「新程式檔喚醒」建已報集合之前,放寬帳條數在喚醒之後才定案。六個取判定的呼叫端用的函式也都對:prepare、record、check 用 scoped 版,skip 與 doctor 用合併版。只有下面兩條。

**C1 配對表用 NFC 路徑當鍵,NFC 和 NFD 同名的兩篇會互相借用對方的舊句**
severity: minor
blocking: 否 — 要圖譜裡同時追蹤 NFC 與 NFD 兩種寫法的同名筆記才觸發(Linux 或 CI 建的 repo 可能有),非存心繞過的情境下幾乎碰不到,而且第一層只防疏忽。
引句:「out[nfc(b)] = ok」
1. 輸入:起點版本只有 `Café.md`(NFC 寫法),它的第 4 行是有違規的舊句 O。終點版本把 `Café.md` 的第 4 行補成 O 加括號,同時新增一篇 NFD 寫法的 `Café.md`,它的第 4 行是全新、沒寫來源的違規句。
2. 路徑:`_notelines_append_pairs` 只替 NFC 那篇建出配對,存成 `out[nfc(b)]`,於是以 NFC 路徑為鍵的配對表有一筆 `{4: O}`。`_ns_append_subtract` 對 NFD 那篇查 `pairs.table().get(nfc(p))`,nfc 之後是同一個鍵,拿到 NFC 那篇的 `{4: O}`。
3. 結果:它把 NFD 那篇第 4 行的違規當成「舊行 O 本來就有」扣掉。預期 rc1,實際 rc0。
4. 二層同源:`_note_audit_mark_appended` 也用 `nfc(it["path"])` 查同一張表,NFD 那篇的全新行會被標成「只判尾巴」,判定者只看到 `text[len(o):]` 的一小段。
5. 重現:在臨時 repo 用 `git hash-object -w` 加 `git update-index --add --cacheinfo` 把 NFD 檔名塞進暫存區,設 `core.precomposeunicode=false`,再跑 `lumos note-shape --staged`。
   - 兩篇都有第 4 行違規時,NFC 補括號那一份回 rc0、什麼都沒報。
   - 對照組(NFC 那篇不補括號)回 rc1。
6. 修法方向:配對表改用原始路徑為鍵;或建表時遇到兩個路徑 NFC 相同就整組不配。

**C2 放寬帳裁長度的迴圈是平方時間,補括號的行一多,推送閘會卡很久**
severity: minor
blocking: 否 — 一次推送要有幾千條補括號的行才會明顯變慢,平常的幾百條沒感覺,而且只是變慢、判定不受影響。
引句:「while rows and size() > 4096:」
1. 輸入:一次推送對一篇筆記補括號的行數 N 很大,`relaxed["pairs"]` 就有 N 筆。
2. 路徑:`_gate_event_fit` 每丟一筆就重算一次 `size()`,而 `size()` 要把整個事件(含剩下的 pairs)重新 `json.dumps`。要丟掉約 N 筆,每筆都付 O(N) 的序列化,總共 O(N²)。
3. 預期:裁到 4 KB 內最多線性時間。實際實測(直接呼叫 `_gate_event_fit`,pairs 為 `[路徑, 行號]`):

   | N(pairs) | 耗時 |
   |---|---|
   | 1000 | 0.14 秒 |
   | 5000 | 3.2 秒 |
   | 20000 | 49 秒 |

4. 端到端:一篇筆記 6000 行補括號,`note-shape --diff` 推送模式 6.0 秒,提交前模式 1.3 秒。多出來的就是這段。
5. 修法方向:先估單筆 pairs 的位元組數,一次算出該留幾筆,或用二分法。這個迴圈原本在 `_drift_m1_fit` 裡因為 rows 有上限所以沒事,抽成共用後上限沒跟過來。

**圖譜鏡頭(固定席逐條判)**
- `Systems/lumos-cli-read.md` 的 INVARIANT:search 預設排除 superseded 但不排除 stale。diff 完全沒碰 search,不影響。
- `Systems/bound-tests-gate.md` 的 INVARIANT:code-loop check 對 impact 固定席上綁定的測試逐支真跑。diff 沒改這個閘的邏輯。改了 `scripts/lumos`,所以推送前這些綁定測試要真跑,但這是流程要求,不是破壞合約。不影響。
- `Systems/guard-kill.md` 的兩條 INVARIANT:guard kill 的 rc 優先序,以及 `--json` 恰好一行合法 JSON。diff 沒碰 guard kill,不影響。
- `Systems/授權與歸屬.md` 的兩條 INVARIANT:授權檔不得進 `_VENDORED_TOOLKIT`,以及主程式檔頭要帶 SPDX 兩行與 MIT 全文。diff 沒動檔頭、也沒動白名單,不影響。我另外確認過 `scripts/lumos` 在 py39 目標下語法檢查(`ruff --select E9`)通過。
- `Systems/測試假綠形態.md` 的 INVARIANT:「還原翻紅釘」要配前置斷言證明現場成立。這份 diff 不含測試檔,無法逐條判。補括號相關的測試(例如 `t_ns_append_wake` 的「①照喚醒那一路報」)有先斷言現場再斷言結果,形狀吻合,但不是這份 diff 的內容。不影響。
- `Systems/design-loop.md` 的 INVARIANT:處置閘第五步。diff 沒碰設計審迴圈,不影響。
- `Systems/reversibility-governance-ledger.md` 與 `Systems/pitfalls-code-loop.md` 只列了 ★RISK★ 沒有條文。diff 新增的治理帳事件 `note-shape/relaxed` 走既有的 `_gate_event_or_warn`,閘名 `note-shape` 已在 `_KNOWN_GATES`,不改判定。不影響。
- 超出上限、只列名的節點不必答。

最高嚴重度 minor,blocking 0 條
