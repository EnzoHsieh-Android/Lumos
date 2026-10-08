severity: clean

我有在派工詞尾端看到「lumos 自動附加」的固定席段,沒看到「圖譜沒有釘到節點」備援段。

固定席逐條判:
- 固定席列的 `測試假綠形態`、`bound-tests-gate`、`canary-audit`、`guard-kill`、`slim-*`、`lumos-cli-read` 這幾篇的 INVARIANT,牽連點只是 `scripts/test_lumos.py` 這個檔名。
- 這份 diff 只動 doctor S20 的 `_ns_tr_manual_clauses`、新測試格 ⑩⑪、兩篇筆記。上述合約綁的測試與這條路徑無關,我沒有發現牽連。
- 「測試假綠形態」要求還原翻紅釘配前置斷言。⑩ 斷言 `len(got)==1`,若該路徑沒走到會是 0 而紅,有前置效力。⑪ 的 `got==[]` 靠修前紅證明(見三問)。

核對方式:在 `/tmp/lumos-seat-work/code-撤除候選也看manual條款-收尾/正確性r2-sonnet/` 下,把修前 81646602(`b`)與修後 c7fa7ee6(`a`)各 clone 一份,用探針腳本呼叫 `_doctor_test_ref_lines` 的 prose 結果對照。

沒有 finding。三問如下。

**① 原問題的修復效果有何行為證據?**

修前會列兩次或誤列,修後都改成只列一次或不列。命令:`python3.14 probe.py <b|a>`。

| 輸入 | 修前(b) | 修後(a) |
|---|---|---|
| 同行 `[manual:]` 加 `[test：test_alive]`(全形冒號) | `[test:]`、`[manual:]` 各列一次,共 2 條 | 只列 `[test:]`,1 條 |
| 同行 `[manual:]` 加 `[test：不存在的名]` | 2 條 | 1 條 |
| 同行 `[manual:]` 加 `[test：已撤除]` | 2 條 | 1 條 |
| 同行 `[manual:]` 加 `[test：a, b]` | 2 條 | 1 條 |
| 開頭欄位 summary 內像條款的行 | 列出 `:6` | 不列 |
| 開頭欄位 decisions 內像條款的行 | 列出 `:5` | 不列 |

- 測試命令 `python3.14 scripts/test_lumos.py -k doctor_s20`,修後 41 passed、0 failed。
- 修前 38 passed,該版本沒有 ⑩⑪ 兩格,所以通過數較少。
- 歸因:這幾條是原有漏查,不是修復造成的。修補範圍限於 `_ns_tr_manual_clauses`。

引句:「        if not _ns_tr_retired(sp) and not any(_test_names_of(sp)[0]):   # 同行的 [test:] 那條路認得(全形冒號等)就讓它列,不重複」

**② 修補處的正常、錯誤與相鄰路徑是否仍成立?**

以下輸入修前修後輸出一致,preserve 沒有回歸。

- 單純 `[manual:]` 加下一層寫撤除:列 1 條(`manual-only`)。
- CRLF 全檔:列 `:8`(`crlf`)。
- 只有正文行是 CRLF:列 `:8`(`crlf-lf-mixed-body`)。
- 開頭欄位沒閉合:不列(`fm-unclosed`)。
- 正文裡有 `---`:列 `:9`(`body-hr`)。
- 條款在圍欄內:不列(`fence`)。
- 同行 `[test:]` 是 `[test:]`(空值):`[manual:]` 路列 1 條(`both-empty-test`)。
- 同行 `[test:無]`:只列 `[test:]` 一條,不重複(`both-fw-placeholder`)。
- 同行有 `[test-gone:舊名]`:`[manual:]` 路列 1 條(`test-gone`)。
- 同行 `[test:]` 在反引號內:`[manual:]` 路列 1 條,沒有被「同行 `[test:]` 認得」誤抑制(`backtick-test`)。
- `[test:]` 在 HTML 註解內:`[test:]` 路列 1 條,且沒有重複(`html-comment-test`)。

沒有發現「修後該列卻漏列」的輸入。

引句:「                or not 0 < no <= min(len(lines), len(regions)) or regions[no - 1] != "body":   # 跟 [test:] 那條路一樣只看正文」

**③ 新發現的同一案例在修前、修後各是什麼結果?**

我補的案例(CRLF、未閉合開頭欄位、正文 `---`、反引號 `[test:]`、HTML 註解 `[test:]`、`[test-gone:]`、多測試名、`[test：已撤除]`)沒有找到修前修後不同、且修後不合理的結果。BOM 開頭的檔兩版都不列,屬同一個既有行為,與本次修補無關。

總結：最高等級 clean。
