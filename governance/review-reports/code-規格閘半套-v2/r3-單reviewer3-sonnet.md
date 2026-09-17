severity: major

Finding 1: `_SHALL_RE` 用單字元 negative lookbehind 排除「自」,把「自應」整組當複合詞跳過。但「自應」是副詞「自(然)」+ 情態動詞「應」(如「系統自應保留舊資料」= 系統自然應該保留),不是像「反應/效應」那種名詞化固定詞——`shall_index("系統自應保留舊資料")` 實測回 -1,會被 `_clause_grammar` 誤判成「缺應」而擋下一條寫法正確的條款。
引句:「_SHALL_RE = re.compile(r"(?<![反效因適回對相供感響呼順理照接自])應")」
severity: major
blocking: 是

Finding 2: 同一顆正則把「理」也放進排除表,原意是擋「理應」這個固定詞,但 lookbehind 只看緊鄰前一字、不看詞界,連「處理應在三秒內完成」這種「處理(主體)應(情態)…」的正常條款也被一起排除——實測 `shall_index("處理應在三秒內完成")` 回 -1,同樣會被誤判「缺應」擋下。此為與 finding 1 同構的假陰性,根因都是「排除表用字元不用詞邊界」。
引句:「_SHALL_RE = re.compile(r"(?<![反效因適回對相供感響呼順理照接自])應")」
severity: major
blocking: 是

Finding 3: 測試 ⑩ 只鎖三案例——S1「系統反應」(缺應觸發子句分支,line 53)、S2「順應」(複合觸發分支的 idx 計算)、S3「問答應於」(拿掉「答」的無條件分支,line 57)——本輪新增進排除表的「自」「理」「照」「接」四字完全沒有任何案例覆蓋,finding 1/2 的假陰性因此沒被測試網住就直接折入主幹。
引句:`_sg_plan(kg, "缺應", ["- [S1] 當甲成立,系統反應 [test:t_green]", "- [S2] 當甲成立,在為順應法規後,則系統應調整 [test:t_green]", "- [S3] 客服問答應於一日內回覆 [test:t_green]"])`
severity: minor
blocking: 否

已讀無 finding:①「回應/對應」當動詞用——`shall_index("系統應回應 200")` 實測回 2(第一個「應」在複合詞判定前就命中),search 先左後右掃描、遇到真「應」立刻停,行為符合預期,不是 bug。④ 無條件型走停用詞開頭——`shall_index("當然應保留舊資料")` 實測回 2,直接對整段 body 找,不受句首停用詞影響,行為正確。「答」被拿掉的疑慮(如「廠商答應於三天內出貨」實測會被算成有「應」)構造得出失敗輸入,但 grep `docs/lumos-toolchain-knowledge/Projects/*.md` 的 `[S＿]` 條款查無「答應/理應/自應」的真實寫法,依抑噪規則不單獨列 finding。

LUMOS-IMPACT 固定席節點逐條判:design-loop.md、guard-kill.md、lumos-cli-lifecycle.md、lumos-cli-read.md、授權與歸屬.md 這五個 ★INVARIANT★ 節點管的是 pre-push、deinit、CLAUDE.md re-inject、search 排除邏輯、授權檔白名單——這批 diff 只動 `scripts/lumos` 裡的 `_SHALL_RE`/`_shall_index`/`_clause_grammar`(spec-gate 條款文法檢查)與對應測試,完全不觸及上述五個節點牽連的程式路徑,故不影響其宣稱行為。

severity: major
blocking: 2 條
