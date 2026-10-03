severity: minor

# 架構對齊審查 第 2 輪(sonnet)

## 三問逐問答

1. 分層與依賴方向:對。`_revisit_dead_place` 放在 `_revisit_quote_states` 之後、`_revisit_misplaced_lines` 之前,與同族的 `_revisit_split`、`_revisit_closed`、`_revisit_misplaced` 同區;三個呼叫端(第一層 `_ns_revisit_violations`、Z 段 `_revisit_misplaced_lines`、`_probe_lines`)都是往同層的純判定函式呼叫,沒有跨層直呼,也沒有反向依賴。對照:file: `scripts/lumos:31816`、file: `scripts/lumos:31830`、file: `scripts/lumos:31983`、file: `scripts/lumos:27938`。
2. 命名與錯誤處理:大致對。`_revisit_dead_place(probe, reg)` 的 `probe`、`reg` 參數名與鄰居 `_ns_revisit_violations(ln, reg, visible)`、`_probe_lines` 的 `regs[i - 1]` 一致;函式回傳 bool,與 `_revisit_misplaced` 回清單的慣例不同但名稱是「判定式」,可接受。結案文法改成只在 body/summary 且非表格才查,與同段 `kind == "cond"` 的 `_ns_revisit_cond_viol` 同範圍,對齊了上輪的架構對齊發現。對照:file: `scripts/lumos:27929`。
3. 第二種做法:沒有新增。「寫在不評估的地方」的判定條件原本三處各寫一份,現在三處都呼叫 `_revisit_dead_place`;我用 grep 確認 `_PROBE_ANY_RE` 在 `scripts/lumos` 只剩 `:31725` 定義與 `:31819` 一處使用,沒有漏改的第四份。引號判定仍只有 `_revisit_quote_states` 一支(`_REVISIT_QUOTES` 只在這支與其常數定義用),沒有第二套。唯一的結構小疑點:`_ns_revisit_violations` 開頭仍自己算 `table`(給第一個分支用),`_revisit_dead_place` 內部又算一次,屬同一行判定算兩次,不是第二種做法,不列。

## Findings

**Z1 落單半形引號修法只擋了「後面完全沒有引號」,後面另有成對引號時仍把句中 REVISIT 當範例放過**
severity: minor
blocking: 否 — 結構與分層是對的(同一支函式的判定邊界沒收乾淨),屬行為洞不是第二種做法;窄輸入、放過的後果是死條件而非擋錯。
引句:「out.append((straight and last['"'] > i) or any(v and last[_REVISIT_QUOTES[o]] > i for o, v in open_.items()))」
1. 輸入:`長 5" 管。REVISIT:2026-10-05 x 他說"好"`(前面一個落單的 `5"`,後面又有一對成對的 `"好"`)。
2. 走到:`_revisit_quote_states` 掃到 REVISIT 位置時 `straight` 已被前面的 `5"` 翻成 True;`last['"']` 是行尾那個 `"` 的位置,大於命中位置,於是 `straight and last['"'] > i` 為真,判成「在引號裡」。
3. 壞在哪:上輪 r1 的修法目標(落單的 `5"` 不算引號)只用「後面有沒有任何 `"`」判斷,後面只要碰巧還有別的 `"`,落單引號又被當成開引號;句中 REVISIT 被放過,提交不擋、Z 段也列不到。
4. 當場重現(唯讀,載入 repo 內 `scripts/lumos` 後呼叫):`m._revisit_misplaced('長 5" 管。REVISIT:2026-10-05 x 他說"好"')` 回 `[]`,期望 `[位置]`;對照組 `'長 5" 管。REVISIT:2026-10-05 x'` 回非空(新測試 ① 只釘了這一種)。同形的全形引號版沒有這個洞(`「甲」REVISIT… 「乙」` 實測回 `[3]` 正確),因為全形有開收配對、半形沒有,所以只有半形路徑受影響。
5. 這條屬計劃〈天花板〉第 1 項「刻意用引號框住的認不到」之外的新漏洞(那項講的是作者故意用引號框住,不是落單引號後面又有別的引號);天花板沒涵蓋,也沒有測試釘。

## 沒問題的項目

- `_ns_revisit_violations` 把 `kind == "bad"` 的 `return` 改成 `out.append` 後往下走:壞損行不再提早結束,`_revisit_misplaced` 的 `head` 用 `_revisit_split` 非 None 判定,壞損行行首那處不會被重報(實測 `REVISIT: 2026-10-05 x` 形狀行首被排除),測試 ④ 與此一致。
- 結案文法範圍縮到 body/summary 非表格後,開頭欄位清單項與表格行不再報「結案標記寫錯」:表格行實測只報「回頭條件寫在句中」,與測試 ⑤ 的宣稱一致。
- `_revisit_dead_place` 與三處原條件逐字等價(表格或非 body/summary,且有 `[when-`),`_probe_lines` 的 `dead` 清單、Z 段「不重算」跳過、第一層 `dead` 旗標三者行為不變。
- Z 段「處」改「行」:`mis` 的單位確實是行(`_revisit_misplaced_lines` 每行最多一筆),用詞正確;同一句旁邊「寫在不評估的地方 N 處」的單位也是行,用詞不統一,但被測試 ③ 逐字釘住且沒有具體失敗場景,不列。
- 新測試名 `t_revisit_misplaced_review_r1` 與既有 `t_escape_review_r1_fixes`、`t_m1_codeloop_r1_fixes` 同一命名慣例。
- 計劃 [S9] 加綁 `t_doctor_revisit_reminder`、審計修正紀錄補 r1 一條,與卷證路徑寫法一致。

## 固定席節點

- bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、lumos-cli-read、design-loop、lumos-cli-lifecycle 等為機器附加的牽連節點;這份 diff 只動 `scripts/lumos` 的 REVISIT 判定段與對應測試,與其中 ★INVARIANT★ 的綁定測試無直接牽連,我沒有逐支重跑(派工詞限唯讀且不跑全套)。

最高 severity: minor
