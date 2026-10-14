severity: major

實驗目錄已刪。以下為 3 條 major(都是實際跑出來的)與 1 條 minor。

severity: major
blocking: 是 — 縮窄後類別方法式測試(Java/Kotlin/Swift/Dart/unittest)被弱化時殘留索引不再升 high
引句:「if ln.startswith(("+", "-", "@@")) and rx.search(ln):」
問題:`_residual_diff_touches` 用 `git diff -U0`,只看增刪行和 hunk 標頭有沒有綁定測試名。hunk 標頭的函式名由 git 預設規則取,只認行首(第 0 欄)的行。類別裡縮排的方法,標頭只會帶出 `class FooTest {` 或 `class C(unittest.TestCase):`。修補前這支檔整檔算命中,修補後只有宣告行本身被動到才算。
失敗情境:實驗用 `FooTest.java`,綁定測試是 `t_a`。把方法內文的 `assertEquals(1, x);` 改成註解,diff 的標頭是 `public class FooTest {`,內文不含 `t_a`。`_residual_diff_touches(..., {"t_a"})` 回 False,pitfalls 不升 high。Python unittest 類別形式(`test_c.py`)同樣回 False。這剛好是弱化「殘留合約的鄰居守衛測試」的做法。`PYTHON_TEST_RE` 只收頂層 `def`,所以只有本 repo 自己的 Python 測試不受影響。
佐證:file: `scripts/lumos:44425`(`_residual_diff_touches`);file: `scripts/test_lumos.py:5116`(G8 測試只用頂層 Python 函式,從未涵蓋縮排方法)。

severity: major
blocking: 是 — 反例編號只留字母數字,不同編號被併成同一個,繞過「每個反例都要問第二個代理」
引句:「return "".join(ch for ch in s if ch.isalnum())」
問題:分隔符也被丟掉。`c1.1`、`c1-1`、`c11` 的正規形都是 `c11`。`a-bc` 和 `ab-c` 也撞。
失敗情境:先 `residual-ask --case c1.1` 判 untestable。再問 `--case c11` 被擋,訊息是「已經問過了(記成 c1.1)」,不同的反例被拒絕重問。接著 `guard residual ... --add Projects/a_計劃#d12 --case c11` 回 0 並寫入標記,但 c11 從未被問過。帳上只有一筆 `case: c1.1`。
佐證:file: `scripts/lumos:18843`(`_residual_case_key`);file: `scripts/lumos:18972`(`_residual_check` 用 key 比對)。

severity: major
blocking: 是 — 宣稱指紋去掉所有標點(含小數點、負號、斜線),不同合約撞指紋,問答與索引互相冒用
引句:「clean = "".join(ch for ch in s if not (ch.isspace() or unicodedata.category(ch)[0] in "PZC"))」
問題:`.`、`-`、`/`、括號都屬 P 類,全被刪掉。實測以下各組指紋相同:`上限 1.5 倍` 與 `上限 15 倍`、`回傳 -1` 與 `回傳 1`、`a/b 不得為空` 與 `ab 不得為空`、`v1.2` 與 `v12`、`(a)` 與 `a`。
失敗情境:同一節點有兩條已審計的合約「重試上限 1.5 倍」和「重試上限 15 倍」。只對 1.5 那條做 `residual-ask --case c1`,再對 15 那條 `--add ... --case c1` 回 0 並寫入殘留,15 那條從未被問過。把 1.5 改成 15 也不會讓舊問答失效,與 docstring 所說「改了字詞指紋就變」不符。索引以 `(node, fp)` 為鍵,兩條合約會合併成一格,doctor 的比對跟著失真。
佐證:file: `scripts/lumos:18849`(`_residual_claim_fp`);file: `scripts/test_lumos.py:4895`(只測加句號與換字詞,沒測帶意義的標點)。

severity: minor
blocking: 否 — 整字邊界的測試守不住,把判斷改壞測試仍全綠
引句:「rx = re.compile(r"(?<![\w])(?:" + "|".join(re.escape(n) for n in sorted(names)) + r")(?![\w])")」
問題:`t_a` 與 `t_ab` 的整字邊界,程式本身是對的,但沒有測試守它。我把兩側 `\w` 前後斷言拿掉(改成單純子字串比對),清掉 pycache 後跑 `-k pitfalls_residual_test_file`,6 條全綠。
失敗情境:日後有人簡化這條正則,綁定 `t_a` 的殘留會被 `t_ab` 的改動誤升 high,或反過來漏判,測試不會紅。G8 測試的資料裡沒有互為子字串的兩個測試名,也沒有縮排方法、二進位檔的案例。
佐證:file: `scripts/test_lumos.py:5116`。

已讀,無 finding:
- `--checker` 日期只收半形且驗真日期。全形、`9999-99-99`、`2026-02-30`、`0000-01-01` 都被擋,結尾換行被 fullmatch 擋掉。
- 殘留指標的路徑大小寫與 `.md` 尾巴。`_pq_decision_target` 讓 `--remove` 用大小寫變體仍找得到標記,`--add` 寫成正式路徑。
- 空字串或全標點的編號(`""`、`--`)。key 為空,`by.get("")` 為空,會被報成沒問過,不會誤放行。
- 改名與刪檔。`--no-renames` 加路徑限定,舊路徑會出現含測試名的刪除行,判為命中。
- hunk 標頭帶出前一支頂層測試。只會多升 high,方向安全。
- 二進位測試檔的 diff 沒有測試名,理論上漏判,但測試檔不太可能是二進位,不列 finding。

最高等級 major,blocking 共 3 條。
