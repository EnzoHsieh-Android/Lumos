severity: major

1. U+2028、`\x0b`、`\x0c`、`\x85` 這幾個字元能寫進題目文字。寫入指令只擋 `\n`、`\r`、`\t`,這幾個卻被別的讀法當成換行。寫進去之後,規格閘會誤判同一篇計劃裡原本合法的條款。
   - 重現:
     - 指令:`lumos question-add Projects/X_計劃.md $'a\u2028b' --class c --stage 實作`,回 0。
     - 改用手寫的 `text: a<U+2028>b` 也一樣。
     - 對照組是 `text: a b`(不含該字元)。
     - 用 `lumos spec-gate Projects/R1_計劃.md --no-run` 跑含該字元的計劃,輸出:`條款綁定: ✗ — 1 條格式看不懂(不算條款):S1(第 13 行:條款正文是空的)`。
     - 同一份計劃,文字換成 `a b` 的對照組,輸出 `條款綁定: ✓`。
   - 判讀:欄位內多出一個「行」,其他消費端的行號就錯位。`pq_parse` 與 `lint` 都沒察覺(`lint` 只出 lands_in 警告)。這破壞了「寫前驗證就是閘讀到的同一份判定」。
   - 位置:`_pq_fmt` 的 `any(c in v for c in "\n\r\t")`;`\u2028` 與 `\x0b` 的寫入結果各有實跑。
   引句:「    if any(c in v for c in "\n\r\t"):」
severity: major
   blocking: 是

2. 題號超大(超過 4300 位數字)時,`pq_parse` 照收,但後面用 `int(q["id"][1:])` 會丟例外。
   - 重現:
     - 檔案:`  - id: Q99…9`(5000 個 9),其餘必有鍵齊全。
     - 指令:`lumos pitfalls kg/Projects/D_計劃.md --stage 需求`。
     - 輸出:traceback `ValueError: Exceeds the limit (4300 digits)`,回傳碼 1。規格 S5 要求清單有問題時回 2。
     - 指令:`lumos question-add Projects/D_計劃.md 新題 …`,輸出:`擋下:Exceeds the limit (4300 digits) for integer string conversion…`。回 2 且訊息與題號無關,之後永遠加不了題,除非手動改檔。
     - 4400 位數、旁邊再有 Q2 的情況,兩支指令行為相同。
   - 判讀:`_PQ_ID_RE` 沒有位數上限。
   - 位置:`_pq_stage_sort_key` 與 `cmd_question_add` 的 `max(int(q['id'][1:]) …)`。
   引句:「    return (not q.get("blocking"), not q.get("irreversible"), int(q["id"][1:]))」
severity: minor
   blocking: 否

3. 題號的 `\d` 吃 Unicode 數字,「題號重複」判斷會漏。
   - 重現:`Q1٣`(U+0663)與 `Q13` 並存,`pq_parse` 回 `nq=2 errs=[]`。
   - 判讀:`int("1٣")` 是 13,數字上重複,但字串不同所以沒被擋。文法表寫的是「不帶前導零的正整數」。
   - 影響:只有手動輸入才出現,影響小。
   引句:「_PQ_ID_RE = re.compile(r"Q[1-9]\d*")」
severity: minor
   blocking: 否

4. `class`、`text` 要求「非空單行」,但用 `""` 就能過。
   - 重現:`text: ""` 加 `class: ""`、`blocking: true`、`stage: 需求`、`status: 待人`。
   - 結果:`pq_parse` 無錯誤。
   - `spec-gate` 擋下,但列出的是空題目:`• Q1 [需求/待人] `(後面空白)。
   - `lint` 完全沒報這題。
   - 判讀:`_strict_scalar` 對 `""` 與 `''` 直接回空字串;必有鍵檢查只看鍵存不存在,不看值是否為空。
   - 位置:`_strict_scalar` 的 `return inner, None`。
   引句:「            return inner, None」
severity: minor
   blocking: 否

5. 決策連結的節點解析太寬鬆,可能讓「結了」誤判。
   - 原因:`env.resolve` 在路徑對不上時退回只比短名,同名多篇時取 `hits[0]`。`_pq_decision_state` 直接信它。這個解析器是既有的,但新的「結了」判定倚賴它。
   - 重現一:
     - 設定:`Projects/Foo.md` 的 d1 有效,`Systems/Foo.md` 的 d1 已作廢。
     - 一題 `status: 已決`、`blocking: true`、`decision: Zzz/Foo#d1`(`Zzz/` 這個目錄根本不存在)。
     - 結果:`spec-gate` 顯示 `待決問題: ✓ — 1 題,沒有擋進實作的`,`lint` 沒有任何待決問題的警告。
   - 重現二:`decision: Foo#d1`(兩篇同名)也通過,選到哪一篇取決於內部順序。
   - 判讀:「指到存在、有效的決策」可被錯誤路徑或撞名滿足,這是漏擋(fail-open)。
   - 位置:`_pq_decision_state` 的 `node = env.resolve(pr[0])`。
   引句:「        node, did = env.resolve(pr[0]), pr[1]」
severity: minor
   blocking: 否

6. ⚠ 選填鍵縮排掉到頂格,會被當成別的頂格鍵,阻塞標記靜默消失。
   - 重現:
     ```
     pending_questions:
       - id: Q1 … status: 待人
     blocking: true
     ```
   - 結果:`_PQ_TOP_KEY_RE` 把 `blocking: true` 當作範圍結束。`spec-gate` 輸出 `待決問題: ✓ — 1 題,沒有擋進實作的`。
   - `lint` 只出一條「沒見過的鍵『blocking』」警告(`note_lint.gate` 為 warn,不擋)。
   - 同樣,`pending-questions:`(連字號)被當成沒有這個欄位,不是讀不懂。
   - 判讀:這符合文法表字面(範圍止於下一個頂格鍵),但編輯器重存弄丟縮排時,閘會靜默放行。我不確定這是設計取捨還是漏洞,所以標 ⚠。
   - 位置:`_strict_list_scan` 內 `if _PQ_TOP_KEY_RE.match(raw): break`。
   引句:「            if _PQ_TOP_KEY_RE.match(raw):」
severity: minor
   blocking: 否

沒找到問題的部分(我逐項實跑過):
- 縮排 1、3、5、6 格、tab 夾中間、NBSP 開頭都被擋。
- CRLF、BOM、行尾空白、註解行、空行放行。
- `Pending_Questions` 與 `pending_question_count` 被擋,與規格一致。
- 合併衝突標記被擋。
- 各種引號與 `: `、`# `、`-`、`?`、`*`、`&`、`!`、`%`、`@`、`` ` ``、`null`、`~`、`yes`、純數字、日期開頭都被正確擋。
- `question-set` 的 `=` 切分、重複鍵、空值拿掉選填鍵、布林刪行都正確。
- `question-add` 在 `[]` 上、欄位後接其他頂格鍵、欄位在最後、題間有空行、區塊尾有註解等位置,插入點都對。
- 並行鎖在這次實跑中沒出問題。
- 圖譜四篇(`lumos-cli-read`、`lumos-cli-write`、`規格閘`、`pitfalls-code-loop`)的敘述與程式行為一致,只有「同級照題號數字」這句在題號超大時不成立,見第 2 條。
- 其餘牽連(測試假綠形態、節點範圍與索引守衛、design-loop)沒有檢視。

總結:有 1 條 major(U+2028 等行界字元能寫入題目文字,之後規格閘誤判條款),另有 4 條 minor 與 1 條 ⚠ minor,主要是超大題號丟例外、空字串通過必有鍵、決策連結解析太寬鬆。文法表本身的縮排、引號、拼寫等逐條輸入大致與程式一致。

臨時檔案在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/邊界輸入-sonnet/`,重現腳本是 `e2e.py`、`w.py`、`mk.py`。
