severity: minor

我在副本 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r7-合約圖譜-sonnet/a`(36d4ffed)驗過。副本的 `scripts/lumos` 已還原成原檔。`-k t_qfm_r` 共 145 支全綠。

我沒找到會擋合併的問題。下面六條都是文件落後或測試守得不夠,程式本身沒錯。

1. 計劃裡定案增補之前的段落還在講舊規則,跟程式和增補都對不上。
   - 計劃「值怎麼寫」那條仍說旗幟標籤字收「🏴 後接兩個小寫字母加 1–3 個小寫字母或數字」。程式現在只收 gbeng、gbsct、gbwls 三面旗,`usca` 會被擋。
   - 計劃「範圍」那條仍說「像題號的行(`id:` 後面接 Q 加數字…)」「看長什麼樣」。程式現在看鍵名:`text`、`class` 等題目鍵,或不是 `d` 加數字的 `id`,都拒讀。
   - 條款 S2 仍寫「清單範圍外出現像題號的行(不論落在哪個欄位底下…)」。實際上 block scalar 裡的題號形狀只算文字,不報錯。
   - 增補一節沒寫「與舊段落衝突時以本節為準」。
severity: minor
   - blocking: 否
   - 引句:「清單範圍外出現像題號的行(不論落在哪個欄位底下、題目行怎麼寫歪)」
   - file: `docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md:63`、`:69`、`:129`;`scripts/lumos:6923`(`_PQ_ALLOWED_FLAGS`)。
   - 重現:修前 19bd4719 與修後 36d4ffed 各載入 `scripts/lumos`,呼叫 `_pq_bad_char("題\U0001f3f4"+tag("usca")+"\U000e007f")`。修前回 `None`(放行),修後回該標籤字(擋下),計劃第 63 行兩版都寫放行。
   - 同樣兩版跑 `pq_parse` 讀 `aliases:\n  - status: draft`:修前讀得懂,修後讀不懂,第 69 行沒提。
   - 歸因:有證據的修復回歸(修前文件與程式一致,修後程式變了、舊段落沒跟)。
   - 兩份系統筆記 lumos-cli-read、lumos-cli-write 的新段落與程式一致。`lumos lint` 對三篇都是 0 問題。Systems/規格閘.md 與 pitfalls-code-loop.md 的描述沒被這輪改動弄錯。

2. 新測試 `t_qfm_r6_unicode_table_and_positions` 的 ①② 守不到抄表錯誤。
   - 它拿 `lm._PQ_DICP_RANGES` 自己的範圍當預期,違反 03〈實作測試品質〉第 2 點「預期結果要獨立」。
   - 表裡刪掉一段,測試照綠。
severity: minor
   - blocking: 否
   - 引句:「DICP 表版本等於 unicodedata，且逐字類別只落在 Cf/Mn/Lo/Cn」
   - file: `scripts/test_lumos.py:56904`、`scripts/test_lumos.py:56896`;`scripts/lumos:6918`。
   - 重現:在副本刪掉 `(0x2060, 0x206F), `,跑 `-k t_qfm` 得 287 passed、0 failed。此時 `_pq_bad_char("甲\u2065乙")` 回 `None`,隱形字元通過;原檔回該字元。
   - 刪 `(0xE0000, 0xE0FFF)` 會被舊的 `t_qfm_r5_folds` 抓到,不是靠新測試。
   - 歸因:有證據的原有漏查(新測試沒補上這個缺口)。
   - 修前版本沒有這個表,兩版對照無意義。表內容我對照 Unicode 16 的 `DerivedCoreProperties.txt` 逐段看過,現況正確。

3. 舊測試 `t_qfm_frontmatter_writers_take_lock` 被改弱,理由與程式不符。
   - 修補在併發前先單獨跑一次 `decision-reindex`,理由寫「decisions 缺 id 是新嚴格讀法明定的錯」。
   - 程式不是這樣:`_pq_check_decision_item` 沒 id 就放行,同一輪的 `t_qfm_r7_key_based_ownership` ⑤ 也斷言沒編號的決策讀得懂。
   - 現在併發段裡的 `reindex --all` 已是沒東西可改,「reindex 與 question-add 搶寫」這個情境不再成立。
   - 拿掉 reindex 的鎖仍會紅,但紅在前置那次單獨的 reindex 被拒,不是紅在併發。
severity: minor
   - blocking: 否
   - 引句:「是新嚴格讀法明定的錯，不能再靠搶鎖順序碰運氣」
   - file: `scripts/test_lumos.py:56484`;`scripts/lumos:7200`(`_pq_check_decision_item`)。
   - 重現:`git show 19bd4719:scripts/test_lumos.py` 存成副本裡的 `test_old.py`,對修後的 `scripts/lumos` 跑 `-k t_qfm_frontmatter_writers_take_lock`,連跑三次都是 2 passed、0 failed。舊斷言在新程式上本來就過,不需要改。
   - 歸因:有證據的修復回歸(測試被改弱)。

4. `t_qfm_r6_signoff_rolls_back_both_sides` 守不到「帳」那一邊的還原。
   - 測試讓 `open(log, "ab")` 一開始就丟錯,帳檔從未被動過。
   - 把 `_signoff_restore` 裡 `log.write_bytes(log_before)` 換成 `pass`,測試照綠。把筆記還原換成 `pass` 則會紅。
   - 寫了一半的情況(`fh.write != len(row)`)沒有案例。
severity: minor
   - blocking: 否
   - 引句:「signoff 帳失敗：rc2、雙邊位元不變、stdout 無成功訊號」
   - file: `scripts/test_lumos.py:57024`;`scripts/lumos:9085`、`scripts/lumos:9101`。
   - 重現:`mut.py` 把 `            log.write_bytes(log_before)` 換成 `            pass`,跑 `-k t_qfm_r6_signoff` 得 1 passed、0 failed。
   - 歸因:有證據的原有漏查(新增功能,修前沒有 signoff 還原)。

5. `t_qfm_r6_tool_flow_and_repo_compatibility` 的 ⑥ 在提交之後沒有比對意義。
   - 它用 `git show HEAD:scripts/lumos` 當舊版。36d4ffed 與目前 HEAD 4dab2976 的 `scripts/lumos` 完全一樣(md5 同為 395626aa…),所以是新版對新版。
   - `changed` 永遠是空的。只剩「含 `pending_questions` 的現存篇讀得懂」這一半還有作用。
severity: minor
   - blocking: 否
   - 引句:「docs 全筆記新舊 pq_parse/_pq_scan 結果相同；含 pending_questions 的現存篇仍可讀」
   - file: `scripts/test_lumos.py:57092`。
   - 兩版查證:`git -C <repo> show 36d4ffed:scripts/lumos | md5` 與 `git -C <repo> show HEAD:scripts/lumos | md5` 輸出相同。
   - 歸因:有證據的修復回歸(測試設計只在未提交時有意義)。

6. 歸屬生成器 `_qfm_r6_hidden_question_cases` 的 "inside" 軸是重複的,而且「題在 block scalar 內」沒有案例。
   - 所有 owners 都以換行結尾,所以 "inside" 產生的字串和 "after" 完全相同。
   - 另一邊,題目放進 block scalar 內時程式靜默當文字,這是 YAML 正確行為,計劃卻沒宣告。測試只有 `summary: |2- # 註解` 那個正例。
severity: minor
   - blocking: 否
   - 引句:「for pos in ("before", "inside", "after"):」
   - file: `scripts/test_lumos.py:56848`。
   - 歸因:未判定。
   - 我另外對 `decisions` 底下的巢狀清單、引號鍵、`'id' : Q2`、tab、全形、NFKC 等 20 多種寫法做了探測,沒有讓題目靜默消失的路徑。`'id' : Q2`(引號後有空白)在純量清單裡會被放行,但一行裝不下一題,只是歸類不精確。

## 鏡頭五道破壞測試結果

| 拆掉的修補 | 結果 |
|---|---|
| 歸屬掃描(純量清單區段停用) | 紅:生成器 ①、`t_qfm_r7_key_based_ownership` ① 及 ② 的 6 條 |
| 純量清單的鍵名判斷整段略過 | 紅:`t_qfm_r7_key_based_ownership` ② 的 4 條 |
| 鍵名判斷的 NFKC | 紅:`t_qfm_r7_key_based_ownership` ② 的全形 `ｉｄ` 一條 |
| 讀值層的 NFC 檢查 | 紅:`t_qfm_r7_key_based_ownership` ⑥ |
| `WriteBlocked` 只繼承 RuntimeError 或只繼承 ValueError | 紅:`t_qfm_r7_writeblocked_keeps_old_handlers` 與 `t_qfm_r3_folds`、`t_qfm_r4_folds` |
| signoff 的筆記還原 | 紅 |
| 可忽略字元表刪一段 | 綠(finding 2) |
| signoff 的帳還原 | 綠(finding 4) |
| block scalar 不吃整段內容 | 紅:`t_qfm_r6_frontmatter_ownership_generator` ②、`t_qfm_r5_folds` 的 2 條 |

## 舊測試斷言改動

- `t_summary_line_verify` 改走 `main()` 並丟 `WriteBlocked`:誠實,因為錯誤處理搬到最外層。
- `t_qfm_r5_folds` 拿掉「summary 區塊之後」那條反例:誠實,按 YAML 它本來就是區塊內文。
- `t_qfm_r5_folds` 把 `usca` 從放行改成擋:誠實,符合新的三旗清單。
- `t_qfm_frontmatter_writers_take_lock` 的改法有問題(finding 3)。

## 三問

① 原問題的修復效果有何行為證據?
- 歸屬、鍵名判斷、`WriteBlocked` 雙重繼承、NFC、signoff 筆記還原,都有破壞後翻紅的證據,見上表。
- `usca` 和 `status: draft` 這類別名,修前能讀、修後被擋,是行為差異,不是只改測試。

② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?
- 成立。非 UTF-8 筆記用 `set` 與 `guard bind`,修前修後都是 rc2 且檔案不動。
- 決策沒編號的筆記 `question-add` 成功。
- `reindex --all` 內部仍接住 `WriteBlocked`。

③ 新發現的同一案例在修前、修後各是什麼結果?
- `usca` 旗:修前放行,修後擋下。
- `aliases: - status: draft`:修前讀得懂,修後讀不懂。
- 刪掉可忽略字元表的 2060–206F:修前沒有這個表,修後刪了測試照綠且 U+2065 漏過。
- 舊版 `take_lock` 測試在修後程式上三次全過。

總結:這輪沒有擋合併的缺口,但計劃舊段落與程式分歧、可忽略字元表與 signoff 帳還原兩處測試守不到,建議合併前補上這幾處。
