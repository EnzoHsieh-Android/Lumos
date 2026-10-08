severity: major

## F1 --settled 結論文字含全形分號或 —— 時,c6 修法寫入後自己判「沒處理到」並卡死
severity: major
blocking: 是

引句:「+    return any(w in cl for w in _DRIFT_PENDING_WORDS) and not _DRIFT_SETTLED_MARK_RE.search(cl)」
file: `/home/user/Lumos/scripts/lumos:32195`(_drift_pending_clause;_drift_clause_end 與 handled 都吃它)

失敗場景(已在臨時 vault 實跑):
1. 正文一行:`甲 待裁定 [[Projects/Done_計劃]] 落地`,目標已 done。
2. 跑 `drift fix <節點> <行> --kind c6 --settled "先做A；還沒做B"`。
3. 括號補在行尾,寫成 `…落地(已裁定:日期 先做A；還沒做B,見 [[Projects/Done_計劃]])`。
4. 子句切點在括號內的「；」再切一刀。後半 `還沒做B,見 [[Projects/Done_計劃]])` 有待定詞「還沒做」、沒有「(已裁定:」、有連結,於是 _drift_pending_clause 判為待定。
5. handled 看到目標還在這一行的待定連結裡,回 False。實跑結果 rc=2「寫入後內容跟預期不同(或這一筆還沒處理掉)」。筆記已被改寫、修復帳沒記,工作樹是髒的,工具要人手動 git checkout。
6. 舊程式(整行有括號就算處理)這個輸入會成功。這是第 ③ 點改成逐子句判帶進來的回歸。
7. 最小重現:跑 `/tmp/c6-cr2/exp.py` 的 E1。
8. 結論文字出現 ；或 —— 是常見寫法,新增的測試格(⑥⑦)只測了括號外的分號,沒有測括號內帶切點的結論。

## F2 單行 summary 值被列為 c6 後,c6 修法把括號補在引號外面,弄壞 summary
severity: minor
blocking: 否

引句:「+                out.append((i + 1, ln, "summary"))        # 單行值:值就在這一行(代碼審 r1 正確性席)」
file: `/home/user/Lumos/scripts/lumos:32193`(_drift_pending_lines 新增的單行分支);`/home/user/Lumos/scripts/lumos:32225`(_drift_clause_end 子句在行尾就補在 len(line.rstrip()))

失敗場景(已實跑):
1. 筆記開頭欄位寫 `summary: "KEY:單行 待裁定 [[Projects/Done_計劃]]"`(引號字串)。
2. 第 ④ 點修法讓這一行進入 c6 候選。對它跑 `drift fix --kind c6 --settled "已經好了呢"`,rc=0。
3. 結果是 `summary: "KEY:單行 待裁定 [[Projects/Done_計劃]]"(已裁定:… ,見 [[Projects/Done_計劃]])`,括號落在收尾引號之後。lumos lint 不報,但嚴格的 YAML 解析器會拒。
4. 修前這一行根本不是候選,所以是新帶進來的問題。
5. 另一個小處:`summary: # 註解` 這種值是註解的行,同一規則判成有值而被收進去。實測它的下一行區塊內容仍照常列,影響只是多看一行註解。

## F3 同一行有兩個子句都連到同一個目標時,一次修法補不完而卡死
severity: minor
blocking: 否

引句:「+        return target + ".md" not in _drift_pending_links(env2, txt.split("\n")[line - 1])」
file: `/home/user/Lumos/scripts/lumos:32225`(_drift_clause_end 只回第一個命中子句)

失敗場景(已實跑):
1. 一行 `甲 待裁定 [[Projects/Done_計劃]];還沒做 [[Projects/Done_計劃]] 的另一半`。
2. 跑 `drift fix … --kind c6 --settled "已經全做完了"`。括號只補在第一個子句結尾。
3. handled 檢查發現第二個子句還連到同一目標,於是回 False。實測 rc=2,筆記已改、帳沒記。
4. 因為乾淨檢查,不先 checkout 就沒辦法再跑一次補第二個子句。舊的整行判法這個輸入會通過。

## 已走過沒問題的範圍
引句:「+_DRIFT_SETTLED = frozenset(_DRIFT_CLOSED) | _ISSUE_CLOSED_STATUSES      # 計劃的收尾值加 Issue 的結案值,不另寫一份」
- _DRIFT_SETTLED:`_ISSUE_CLOSED_STATUSES` 定義在 16805 行、早於 32015 行,載入順序沒問題。內容 {done, superseded, resolved, wontfix} 與舊 tuple 相同。全檔只有三處用法(32150、32243、32255 的 `in` 與 47049),都不排序、不輸出,行為不變。
- _closing_revisits 與 _closing_pending_decisions:set 路徑各呼叫一次,drift fix --close 路徑只呼叫 _closing_revisits 一次,待定決策行已在寫入前被擋,沒有重複列也沒有漏列。
- --keep-revisits:行號改成在加了橫幅之後的 `new` 上算,條件是 `o.get("keep_revisits") is not None`。_drift_close_gates 保證這時 live 非空,所以 kept 非空,與舊行為一致。
- _drift_print_backrefs:decision-add 與 decision-supersede 的四個呼叫處現在共用同一個 fail-open 防護。外層 except 沒有改。未攔 AttributeError、TypeError 這類程式錯誤,我認為這是對的。
- 單行 summary 的判斷:`|2-`、`>-` 開頭的歸區塊,走 in_sum;引號字串與純文字值列入,連續行也走 in_sum。
- 子句切點正則與 _drift_clause_end、_drift_pending_links 用同一個 _DRIFT_CLAUSE_SPLIT_RE 與同一個 _drift_pending_clause,對沒有括號的行切法一致。
- 新測試 ④⑤⑥⑦ 與 --decision 新句那一格,在修前程式上都會翻紅,我沒有找到假綠。缺口是沒有測括號內含切點的結論(F1)與同目標雙子句(F3)。

總結:逐子句判這一改在結論文字含切點時會讓修法自己卡死,是這份差異最要處理的一處;其餘八處修法大致站得住。
