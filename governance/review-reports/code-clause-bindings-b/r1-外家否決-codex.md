<!-- 外家否決席 -b r1(Codex gpt-5.6-sol, xhigh, --sandbox read-only);原始逐字稿 r1-codex-raw.txt;正規化:去行尾雙空白、去重複印出的第二份 -->
severity: major

前輪 1 — 沒修好(重現)：單反引號整行與簡單三反引號 fence 已修，但雙反引號、未閉合反引號及 `~~~` 仍能誤判，見 finding 1、2。
引句:「fence 內整段不看;行內反引號的內容剝掉(範例);未閉合的反引號剝不掉」

前輪 2 — 沒修好(重現)：`<!-- [S1] 只是註解 -->` 仍被當未知清單而 FAIL，且已有合法 S1 時，`→ [S2]` 反而被當引用放過，見 finding 3、4。「規格 [S1]:…」會 skip，但明印「視同 opt-in 未啟用」；依凍結材料規定的 lead 語法，不算靜默繞過。
引句:「_CLAUSE_LISTLIKE_RE = re.compile(r"^\W*\[S(\d+)\]")」

前輪 3 — 修好：`- [S1] …詳見 [S2]` 只產生 S1 條款，S2 為 undefined；若把真正編號放到文字後面，會明印 opt-in 未啟用，該寫法不符凍結材料的定義語法。
引句:「seg = line[ms[0].end():]          # 一行一條」

前輪 4 — 修了但引入 finding 3：同一編號一次行首、一次表格列會成為 duplicate 並 FAIL；第二次若用未識別清單前綴，卻會被現有條款遮掉而 PASS。
引句:「dup.setdefault(cid, []).append(no)   # 同編號在兩行都寫成定義」

前輪 5 — 修好：索引錯誤時 `handoff --json` 現在輸出 `total: null` 並保留 `index_error`。
引句:「c["total"] = None if err else len(rows)   # 索引建不起來時各態算不出」

1.
severity: major
blocking: 是 — 程式碼範例能偽造 `[manual:]`／`[test:]` 證據，使未標條款通過硬閘。
引句:「未閉合的反引號剝不掉,但一行只認一條所以」
file: `scripts/lumos:162` `INLINE_CODE_RE` 只處理單個成對反引號；HEAD 函式重現中，S1 後以雙反引號或未閉合單反引號包住 `[manual:人看一次]`，都得到 `state=manual`、`gate=ok`。

2.
severity: major
blocking: 是 — 合法 CommonMark fence 內容會被當真條款，正常設計審因此錯誤失敗。
引句:「fence 內整段不看;行內反引號的內容剝掉(範例)」
file: `scripts/lumos:2518` `_visible_lines` 只辨識三反引號；最小重現 `~~~md\n- [S1] 圍欄範例\n~~~` 得 `S1=untagged`、`gate=fail`，四反引號外層含三反引號內層也會漏出 S1。

3.
severity: major
blocking: 是 — 未識別清單條款只在零個已辨識條款時檢查，加入一條合法條款即可繞過。
引句:「listlike = [b for b in undef if b.get("listlike")]」
file: `scripts/lumos:13460` 最小重現 `- [S1] 已標 [manual:人看一次]\n→ [S2] 真條款沒標` 得 `gate=ok`；把第二行改成 `→ [S1] 第二次定義沒標` 也不會觸發 duplicate。

4.
severity: major
blocking: 是 — 純 HTML comment 被符號前綴規則誤判為未知清單，會硬擋未啟用條款制的計劃。
引句:「_CLAUSE_LISTLIKE_RE = re.compile(r"^\W*\[S(\d+)\]")」
file: `scripts/lumos:4052` 最小重現 `<!-- [S1] 只是註解 -->` 得 `state=undefined、listlike=true`、`gate=fail`。

5.
severity: minor
blocking: 否 — 只誤導接手視圖，不改處置閘結果。
引句:「"duplicate": "編號重複定義(兩行都寫 [SN])"」
file: `scripts/lumos:21007` duplicate 輸入的 `_handoff_clause_counts` 為 `duplicate=1、total=1`，但人讀輸出未列 duplicate，會顯示綁定／靠人／未標／懸空全為 0。

6.
severity: minor
blocking: 否 — 執行結果符合一行一條的新政策，但函式契約仍描述舊切段語意。
引句:「配對範圍=同一行、在它之後、下一個 [SN] 之前」
file: `scripts/lumos:4064` 實作已改為從第一個 `[SN]` 掃到行尾，因此後續引用之後的標記也會歸第一條，與 docstring 的「下一個 `[SN]` 之前」矛盾。

最嚴重 severity: major；blocking 4 條。
