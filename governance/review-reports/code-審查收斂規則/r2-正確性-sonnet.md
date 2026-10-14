severity: major

主要問題有兩條。第一條是改動綁定測試的內容時,升高風險的判斷會漏掉。第二條是合約指紋的正規化把語意不同的合約當成同一條。

severity: major
blocking: 是 — 殘留守的測試被改弱時,該升高的推送判成不升
引句:「if ln.startswith(("+", "-", "@@")) and rx.search(ln):」
問題:帶 tests 欄的索引改成「diff 碰到綁定測試名才算命中」。偵測只看三種行:增刪行本身、hunk 標頭、行裡出現的測試名。但 git 預設的 hunk 標頭只取第 0 欄起首的行。Python class 內的方法、Kotlin、Java、Swift 的測試方法都有縮排,標頭只會顯示 `class T {` 或 `class TestA:`,不會顯示測試方法名。只改測試本體(例如把斷言換掉)而不碰簽章行時,三處都對不到名字。這條合約的殘留代表「這類壞法測試抓不到」,測試被削弱正是最該過代碼審的情形。
失敗情境:合約綁 `checksX`(Kotlin),`K.kt` 在 `tests` 欄裡。推送只把 `assertEquals(1,a)` 改成 `assertTrue(true)`。我在臨時目錄實測 `git diff -U0`,標頭是 `@@ -4 +4 @@ class T {`,增刪行不含 `checksX`。`_residual_diff_touches` 回 False,這個檔不算命中,tier 不升 high。Python class 式測試實測也一樣,標頭是 `class TestA:`。只有「測試是模組層級的 col-0 `def`」的專案(例如本 repo 的 `t_*`)才靠得住。
修法:不看增刪行與標頭,改成把該檔在起點與終點兩版的內容各自抽出「綁定測試名那個方法的本體」再比對。做不到這點就退回整檔算命中。或者只在測試名由 col-0 定義的語言才用這條收窄,其他一律整檔算。
佐證:``file: `scripts/lumos`(修補差異的 _residual_diff_touches,約在 _residual_tier_hits 之前)``

severity: minor
blocking: 否 — 只會在合約文字被小改後讓舊問答沿用,且需要作者手動改合約
引句:「clean = "".join(ch for ch in s if not (ch.isspace() or unicodedata.category(ch)[0] in "PZC"))」
問題:宣稱指紋去掉所有標點(P 類),連語意載重的符號都去掉了。減號/連字號(Pd)、小數點(Po)、括號(Ps/Pe)、底線(Pc)、斜線(Po)都被去掉。計劃文字說「改了字詞指紋就變」,但這些改動指紋不變。
失敗情境:我實測了三組輸入,指紋都相同。「回傳 -1」對「回傳 1」。「(a 或 b) 且 c」對「a 或 (b 且 c)」。「rc 0.5」對「rc 05」。合約原本問答過 c1 判 untestable。作者把合約改成語意不同的另一句後,舊問答仍算數,`--add` 與 doctor 都放行。「合約宣稱改過字也要重問」的保護在這類改動上失效。
修法:只剝句末標點與全形/半形空白差異(例如尾端的 。.;,),保留括號、符號、數字之間的 `-` 與 `.`。
佐證:``file: `scripts/lumos`(_residual_claim_fp)``

severity: minor
blocking: 否 — 只在手改問答帳時才會觸發,且崩潰在檢查端,不是放行
引句:「elif not any(n in content for n in checkers(k)):」
問題:`checkers(k)` 只收 `verdict == "untestable"` 的問答。某個反例在帳裡有事件、但 verdict 既不是 testable 也不是 untestable(帳被手改、舊格式)時,`verdicts(k)` 不含 testable,`checkers(k)` 是空清單。下一行 `checkers(k)[0]` 會丟 IndexError,`guard residual --add` 沒有擋下訊息就直接崩潰。doctor 的呼叫端有 try 包住,只會變成「殘留檢查算不出來」。
失敗情境:帳裡有 `{"case":"c1","verdict":"x"}`,執行 `--add ... --case c1`,traceback 結束,rc 不是 2。
佐證:``file: `scripts/lumos`(_residual_check 的 cases 分支)``

已讀,無 finding 的部分:

- `_residual_case_key`:NFKC、casefold 加只留字母數字,在 ask 的 ASCII 限制下,c1、C1、c1.、c-1 同一鍵。`--case` 傳進來的空鍵不會碰到帳裡的案例。
- `_residual_ref_key` 與 `_pq_decision_target`:只有 `#dN` 簡寫時 rel 為空,回原文。`--add` 前面已被 `_residual_ref_problem` 擋下短名。`--remove` 對解析不了的指標回 NFC 原文,與合約行上的原文一致,可以移除。
- `_residual_tier_hits` 的範圍寫法:`A..B`、`A...B`(經 `_diff_range_ends` 取 merge-base)、單一版本(終點讀工作目錄)的起點與頂端對得上。索引檔被刪或形狀壞掉,會走 `removed` 或 `head_bad`,不會靜默放行。頂端把 residuals 清空也被 `removed` 抓到。
- 舊索引沒有 `tests` 欄時回到整檔算,方向是多升不少升。
- 資料狀態:repo 內沒有 residual-ask 帳,也沒有 residual-index.json,舊指紋問題不會實際發生。
- 共用驗證函式:三個呼叫點(--add 帶 cases、--reindex 與 doctor 不帶)的語意差異合理。

總結:最高 major,blocking 1 條(測試本體被改而不升 high);minor 2 條,不擋。
