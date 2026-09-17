severity: major

**Finding 1**
`_clause_grammar` 的「在」複合觸發判準沒有把分隔限定在「在」子句本身之內——`_CLAUSE_SEP_RE.search(rest)` 對整段回應段搜尋逗號,只要回應動作本身用逗號列了兩件事(例:「當甲成立,在三秒內系統應回應,並記錄」),就會被誤判成複合觸發而擋下,即使「在」明明是介詞、沒有第二個條件句。實測 `_clause_grammar("當甲成立,在三秒內系統應回應,並記錄")` 回 `(False, 'trigger', '複合觸發…')`,`_clause_grammar("當使用者登入失敗三次,在鎖定期間系統應停用帳號,並寄送通知信")` 同樣誤擋。此洞在 r1 就存在,r2 的 KEY 註記聲稱已把「在」的範圍收窄成「只有後面還有分隔才算條件句」,但實作沒有把分隔限制在緊接「在」的子句內,範圍沒有真的堵住。

引句:「rest.startswith("在") and _CLAUSE_SEP_RE.search(rest)」

severity: major
blocking: 是

---

已讀無 finding(逐項核對,未發現新增或殘留缺陷):

- Y1 停用詞路徑:`"當然"`/`"若是"`/`"若干"` 等在 outer `if not any(rest.startswith(w) for w in _TRIGGER_STOPWORDS)` 仍先判掉,「當甲,當然應丙」不會誤判複合觸發,第二段停用詞邏輯仍有效。
- Y1 「當/若/若啟用」分支:`any(rest.startswith(w) for w in ("若啟用", "當", "若"))` 不再要求逗號,「當甲,當乙成立系統應丙」正確擋下、「當甲,若乙,則應丙」正確擋下,符合設計意圖,無反例。
- Y2 `_rollback_section_chars` 回到純 ATX:`# 回退`(H1)、`### 回退`(H3)、`##回退`(無空白)都不匹配 `_ROLLBACK_H2_RE`,一致落回「沒有這一節」;`## 回退(草案)`因正則允許尾端括號仍正確辨識;移除的 `[-=]{3,}` 排除邏輯是冗餘(該行本就無 `[^\W_]` 字元可計數),拿掉不影響字數統計。
- Y2 擋下訊息:「沒有這一節」與「有節但太短」兩分支維持既有分工(前者才提示標題寫法),此結構是既有設計而非本輪改動引入,亦無具體反例輸入。
- Y3 `_contract_key_matches(with_kind=True)`:內層 `break` 只作用在 kind/rx 迴圈,`return out` 仍在外層 line 迴圈之外(已讀原始碼確認縮排),三個正則彼此互斥不會有一行同時命中兩種 kind 的順序爭議;`_lens_contract_lines` 的 `cap=40` 截斷邏輯未被觸碰,仍生效。
- Y4 `_plan_system_links`:`[[Systems/A|別名]]`、`[[Systems/A#錨]]`、` [[Systems/A]] `(帶空白)剝括號後交給既有的 `split("|")`/`split("#")`/`.strip()` 後續處理,結果與剝括號前的 `related` 行為一致;`lands_in` 純字串(無括號)不受影響。

固定席節點逐條判(不影響,理由):

- Systems/design-loop(處置閘第五步 INVARIANT):本輪只改 `_clause_grammar`/`_rollback_section_chars`/`_plan_system_links`/`_contract_key_matches` 內部邏輯,未改 `_clause_check` 呼叫時機或 `_SPEC_GATE_SINCE` 判斷,處置閘第五步共用檢查器的呼叫路徑未變,不影響。
- Systems/guard-kill(rc 優先序、JSON 純淨):本輪未觸及 guard kill 相關程式碼路徑,不影響。
- Systems/lumos-cli-lifecycle(re-inject sentinel):本輪未觸及 re-inject 相關函式,不影響。
- Systems/lumos-cli-read(search 排除 superseded):本輪未觸及 search/ranked 邏輯,不影響。
- Systems/授權與歸屬(LICENSE vendoring/SPDX):本輪未新增或刪除任何被 vendored 的檔案,亦未動 `_vendor_toolchain`,不影響。
- Systems/pitfalls-code-loop、Systems/loop-convergence-recording:僅因牽連檔案列名(scripts/lumos)被機器列出,本輪未觸及這兩篇涉及的具體函式,不影響。

最嚴重 severity: major、blocking 1 條
