severity: clean

我沒找到會讓照做的人做錯、破壞合約或讓推送擋下的問題。三問的結論如下。

**修到沒?** 修到了。
- `_choice_plan_sections` 現在多收 `clause_lines`,並用 `_choice_reader_lines(text) | set(clause_lines)` 一起扣掉。
- `_choice_plan_view` 傳入 `{r["line"] for r in rows}`。這些行號和 `clauses` 取行時用的 `lines[r["line"]-1]` 是同一套(`_note_lines`,含 frontmatter),沒有偏移。
- 我另外造了一份計劃來驗證:標題是「## 驗收條款(說明)」(讀取器讀不到這一節),節內有條款行、說明句、圍欄,後面再接「## 範圍」。結果是條款定義行(`S1`、縮排的 `S3`)不在正文,其餘內容原樣留在正文。

**修補有沒有引入新問題?** 沒有。
- 重複編號的第二行定義讀取器本來就不當條款,留在正文裡只出現在一邊,所以不違反「每一行只在一邊」。
- 圍欄內的假條款行同理,它在條款表(`clauses`)裡也沒有。

**同類位置還有沒有?** `_choice_plan_view` 是唯一呼叫 `_choice_plan_sections` 的產品碼路徑,沒有別處漏傳。

**合約與圖譜一致性**
- 計劃〈用詞〉的計劃正文新字面「也扣掉條款讀取器認的條款定義行(…說明句照樣留在正文;r7)」,和程式行為一致。
- `_choice_plan_sections` 與 `_choice_plan_view` 的 docstring 和現行行為一致。
- `scripts/lumos` 裡 `_DOOR_RULE_VERSION = 17`,規格閘 KEY 行也寫 17。沿革 `17=2026-11-27 再升 9` 與程式碼註解相符,版本號與沿革此輪一致。
- 規格閘 PITFALL 的 `[test:t_choice_plan_view_body_drops_clause_lines]` 在 `scripts/test_lumos.py` 裡存在。
- 議題第 18、19 條的內容與放行理由合理,「剩…」那句也已補上這兩條。

**我跑的檢查**
- `t_docs_command_count`:4 passed, 0 failed。
- `-k t_choice_plan_`:15 passed, 0 failed。
- `-k t_door_rule`:15 passed, 0 failed。
- `lumos lint Systems/規格閘`:0 問題。
- `lumos drift scan` 輸出裡只點到「Systems/回合結束寫法檢查」(`scripts/lumos` 超過 2 MB 判不了)和「Systems/筆記內容閘」(數量標記寫錯)兩處,以及幾處待裁定的舊筆記,沒有點到這次改的筆記。

沒做的事:我沒有把 `set(clause_lines)` 拿掉再跑測試確認它會翻紅,只確認了測試現況綠、手造語料行為正確。

總結:最高等級是 clean
