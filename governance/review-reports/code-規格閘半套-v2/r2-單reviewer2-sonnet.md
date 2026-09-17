severity: major

**Finding 1 — 補丁引入的 `_shall_index` 與同函式的「缺應」判準不同步,產生假陽性放行**
`_clause_grammar` 用 `_shall_index` 找複合觸發的分界,但緊接著兩處「缺應」判斷(觸發型與無條件型)仍是舊的 `"應" in rest` / `"應" in b` 原始字元比對。實測 `_clause_grammar("當甲,系統反應")` 回傳 `(True, 'trigger', '')`——因為「反應」裡仍含「應」這個字元,原始比對判定「有應」,但 `_shall_index` 對同一段文字回傳 `-1`(全是複合詞、沒有真的回應應),照兩者本該一致的邏輯這條應該被判「缺應」而擋下,結果卻放行,方向確實是漏判放行、不是誤擋。
引句:「if "應" not in rest:」
severity: major
blocking: 是

**Finding 2 — 複合詞字表本身不齊,同方向重現這批要修的 bug**
派工詞的假設有誤:`順應/理應/自應/照應/接應` 這五個詞其實都**不在**表裡(表 `反效因適回對相供答感響呼` 只覆蓋到「呼應」的呼),只有呼應真的有蓋到。用一個結構跟測試 ⑨ 的 S1 完全對稱、只是把「反應」換成「順應」的句子驗證:`_clause_grammar("當甲成立,在為順應法規要求後,則系統應調整")` 回傳 `(True, 'trigger', '')`——本該因為第二個逗號被判複合觸發卻沒有,重現了這批補丁原本要修的同一種漏判。
引句:「_SHALL_COMPOUND_PREV = "反效因適回對相供答感響呼"」
severity: major
blocking: 是

**Finding 3(⚠反方向,無法給出會翻верdict的具體輸入,標低嚴重度僅供留意)**
反方向(主體字尾恰好落在表裡、但那個「應」其實是真的回應應)確實存在字表誤判:`_shall_index("客服問答應於24小時內完成回覆")` 回傳 `-1`,因為「問答」的「答」在表裡、被誤判成複合詞跳過,真正的「應」反而被漏掉。但因為 Finding 1 那個獨立的漏洞(無條件型分支從不呼叫 `_shall_index`,只看原始字元),這個反方向誤判目前不會讓 `_clause_grammar` 給出錯誤的最終判定——它只在 `_shall_index` 內部錯,尚未外溢成可觀察的壞行為,一旦 Finding 1 被獨立修掉就會立刻外溢。
引句:「while i != -1 and i > 0 and text[i - 1] in _SHALL_COMPOUND_PREV:」
severity: minor
blocking: 否

**答④(非 finding,已讀確認,不寫 severity 行)——測試 ⑨ 有真的鎖到**
把 `_shall_index` 換回補丁前的 `rest.split("應", 1)[0]` 重算測試 ⑨ 的 S1,`_clause_grammar` 回傳 `(True, 'trigger', '')`(視為合法、不算複合觸發),但測試期待 `r9.returncode == 1 and "S1(" in r9.stdout`——退回舊寫法會讓 S1 不再被判複合觸發、gate 不會列出 S1(,測試會翻紅,不是空殼。
引句:「- [S1] 當甲成立,在收到用戶反應後,則系統應回覆 [test:t_green]」

**LUMOS-IMPACT 節點逐條判——不影響**
這批只動 `scripts/lumos` 裡 `_clause_grammar`/`_shall_index`(規格閘句式檢查的內部字元掃描)與 `scripts/test_lumos.py` 新增一個測試案例,沒有碰 `pre-push`、`guard kill` 的 rc/JSON 輸出、`lumos-cli-lifecycle` 的 re-inject sentinel 邏輯、`lumos-cli-read` 的 search 過濾、或 `授權與歸屬` 的白名單/SPDX 機制,所列出的 ★INVARIANT★ 節點宣稱的行為與合約都不在這支函式的呼叫路徑上,判「不影響」。

---
severity: major
blocking: 2 條
