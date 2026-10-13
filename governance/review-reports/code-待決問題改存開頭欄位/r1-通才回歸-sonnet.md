severity: minor

整體判斷:既有行為沒被打壞,回退也退得掉。下面三條都只影響新功能自己的邊角,沒有一條會改動原本的輸出或回傳碼。

**既有功能的比對結果**
- **`parse_decisions` / `decisions_items` 既有呼叫者**:所有呼叫點都沒傳新參數,預設 `key="decisions"` 時 `re.escape("decisions")` 還是 `decisions`,正則一字不差。只有 `pq_parse`、`cmd_question_add`、`cmd_question_set` 三處傳了 `pending_questions`。我在 `decision-add`、`set`、`append` 後面做了舊版對照,行為沒變。
- **全圖 lint**:用舊版(a31b2043)與新版對 851 篇筆記各跑一次 `lumos lint`,共 853 份輸出,只有一篇不同,是已遷移的 `Projects/後端工程提問與證據擴充_計劃`。它從「沒見過的鍵」警告變成 0 問題,屬預期,沒有誤報。`doctor` 新舊輸出逐行相同(292 行)。
- **規格閘**:五份沒有 `pending_questions` 的計劃(`spec-gate --no-run`)新舊輸出與回傳碼相同。有欄位的那份只多一行 `待決問題: ✓ — 7 題`,回傳碼仍是 0。
- **`--push-check`**:三個範圍新舊輸出和回傳碼都相同,提醒函式沒有碰回傳碼。
- **`pitfalls --stage`**:三種輸入(有 frontmatter、無 frontmatter、CRLF)乘六個階段乘文字與 JSON,共 36 組新舊逐字相同,包含回傳碼。
- **命名衝突**:`_pq_*`、`pq_parse`、`PQ_STATUSES`、`_strict_*`、`cmd_question_*`、`_nl_rule_pending_questions` 在 `scripts/lumos` 都只定義一次,沒撞名。
- **測試子集**:`-k qfm` 100、`-k decision` 126、`-k spec_gate` 107、`-k stage` 19,全綠,且五個 `[test:t_qfm_*]` 綁定都找得到實作。

**回退**:〈回退〉節的描述成立。用舊版對已有 `pending_questions` 的計劃跑 `decision-add`、`set`、`append`:
- `decision-add` 與 `set` 都成功,新決策插在 `decisions` 區塊內,沒有吞掉後面的欄位。
- `append pending_questions` 回「擋下」,檔案沒動。
- `lint` 只多一條「沒見過的鍵」警告。

**Finding**

1. 題目裡寫了 `_line` 鍵,再加任何一個別的錯,`pq_parse` 就丟 `TypeError`,不是乾淨的整份擋下
severity: minor
   blocking: 否
   引句:「cur[k] = ((ms.group(2) or "").strip(), no)」
   - **輸入**:`pending_questions` 的某題寫了 `    _line: 3`,而且同一題缺 `class`。
   - **路徑**:`_strict_list_scan` 發現 `_line` 已在 `cur` 裡,把「寫了兩次」記進錯誤,但沒有 `continue`,接著仍執行 `cur[k] = (值, 行號)`,內部的 `_line` 整數被蓋成 tuple。之後 `pq_parse` 用 `it["_line"]` 當行號記缺鍵錯誤,最後 `sorted(errs)` 拿 tuple 和 int 比大小。
   - **實測**:在臨時圖譜 `lint`、`spec-gate --no-run`、`pitfalls --stage 需求` 都以 `TypeError: '<' not supported between instances of 'tuple' and 'int'` 結束,堆疊指向 `return present, qs, sorted(errs)`。
   - **連帶影響**:`question-add`、`question-set` 的 `except` 只接 `ValueError`、`RuntimeError`、`OSError`,同樣會噴 traceback。`--push-check` 的 `_pq_push_remind` 沒包 try,推送前的規格閘跟著崩。
   - **只有 `_line` 才會**:其他重複鍵不會崩,因為它們不是內部用的名字。
   - **改動前後**:改動前沒有這條路徑;改動後設計說的「讀不清楚就整份擋」,在這個輸入上變成崩潰。
   - **隨機測試**:我用 3 萬組隨機 frontmatter 片段測 `pq_parse`,55 次丟例外,都和 `_line` 有關。
   - **修法**:重複鍵錯誤後 `continue`,或把內部行號鍵改成使用者寫不出來的名字。

2. 所有筆記的 lint 多了一條對「長空白行」平方級的正則
severity: minor
   blocking: 否
   引句:「elif re.sub(r"""^["']|["']?\s*:.*$""", "", s).lower().startswith(key[:-1].lower()):」
   - **輸入**:任何筆記的 frontmatter 有一行頂格文字,中間夾連續空白,例如 `x` 加 4 萬個空格再加 `y`,不需要 `pending_questions`。
   - **路徑**:`_nl_rule_pending_questions` 對每篇筆記都呼叫 `pq_parse`,`_strict_list_scan` 對每個頂格行跑這條 `re.sub`。
   - **實測**:同一篇筆記 `lumos lint`,舊版 1.05 秒,新版 3.70 秒。直接測正則,2 萬空白 0.7 秒、4 萬 2.8 秒、8 萬 11 秒。
   - **影響**:這規則掛在全圖每一篇筆記,不只是有該欄位的計劃,所以任何一篇的長空白行都會拖慢。
   - **修法**:先用 `s.partition(":")` 取鍵名再比對,就不會回溯。

3. 推送前提醒在「刪掉整份計劃」時把每一題都報成「不見了」,且比對基準不是合併基準
severity: minor
   blocking: 否
   引句:「base, head = m.group(1), (m.group(2) or "HEAD")」
   - **輸入**:範圍內刪除一份有題的計劃。我在臨時 git repo 刪掉有 7 題的 `後端工程提問與證據擴充_計劃`。
   - **路徑**:`touched` 含已刪檔,`_pq_git_show(head)` 回空字串,於是 `nq` 為空,`oq` 的 Q1 到 Q7 各印一行「在 HEAD~1 那一版有、這一版不見了」。
   - **只提醒**:這些是提醒,回傳碼不變。
   - **基準問題**:規格閘.md 寫「合併基準那版有這版不見」,程式拿範圍左端字面值當基準。範圍是 `A...B` 且 A 已前進時,拿到的是 A 尖端而不是 merge-base。
   - **圖譜用語不一致**:這是筆記說合併基準、程式碼用範圍左端。依專案規則以程式碼為準,並該立 Issue 記下筆記的說法不準。
   - **修法**:被刪或改名的檔不比對,或基準改成 `git merge-base`。

**圖譜鏡頭**
- **`Systems/lumos-cli-read.md`**:新增段落描述 lint 規則與 `pq_parse` 單一入口,和程式相符。但「讀不懂時逐處報行號」沒涵蓋 Finding 1 的崩潰。
- **`Systems/lumos-cli-write.md`**:`question-add`/`question-set` 的描述與程式一致,其中「`[]` 上加題」與沿用 `decisions_items` 的說法屬實。「已知限制」一節仍只寫 decision-*,沒寫新指令對 CRLF/BOM 檔拒寫的限制,這點我判不準。⚠
- **`Systems/規格閘.md`**:「回傳碼 1、風險高低都擋」與程式相符,沒欄位時輸出不變也實測屬實。「合併基準那版」是 Finding 3 的不一致。
- **`Systems/pitfalls-code-loop.md`**:「不帶欄位時輸出不變、`--json` 有題才多 `questions`」實測屬實。
- **`Systems/bound-tests-gate.md`**:diff 沒有改它;新增的 `[test:t_qfm_*]` 綁定都找得到,沒有懸空。
- **只列名未查**:guard-kill、lumos-cli-lifecycle、design-loop、loop-convergence-recording。

三條都是 minor 且不擋,結論是可以上線;Finding 1 建議先修。
