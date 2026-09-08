severity: blocker

# code-clause-bindings-b r2 — 驗收 r1 折入 9 條(i1–i9)+ 掃 delta 新洞——單reviewer

被審(凍結):`r2-snapshot.patch`(全量,1334 行)+ `r2-delta.patch`(368 行)。前輪留痕:`r1-intake.md`(i1–i9)、三份 r1 席報告。
方法:工作樹 `scripts/lumos`/`scripts/test_lumos.py` 有另一 session 未提交的改動,一律不碰;`git show HEAD:scripts/lumos` 取凍結狀態(blob `e4392cf...`,與 `r2-snapshot.patch`/`r2-delta.patch` 尾狀態的 index 完全一致)複製到 `/tmp/lumos_head.py` 與沙盒 `/tmp/r2review/scripts/`,只在沙盒操作。`python3 test_lumos.py -k clause`(80 passed)、`-k fence`(10 passed)、`-k search`(126 passed、1 skip)沙盒全綠。另用 `_load_lumos_inproc()` 對 `clause_bindings`/`_CLAUSE_LEAD_RE`/`_CLAUSE_LISTLIKE_RE` 純函式寫多組不在測試檔裡出現過的獨立輸入(一次性 repro,驗完即棄),交叉核對測試斷言與規則本身的行為。

LUMOS-IMPACT: Lumos/main..HEAD

## 九條逐一驗

**i1(`a.`/`一、` 短編號進 `_CLAUSE_ENUM` 定義行白名單,`_CLAUSE_LISTLIKE_RE` 也認短編號)修了但引入新洞,見 Finding B、Finding C**。獨立餵 `a) [S1]`/`甲、[S1]`/`十一、[S1]` 三種都被 `_CLAUSE_LEAD_RE` 判定為合法定義行(非靜默跳過),`iii. [S1]`(白名單外三字母)正確落 listlike 擋;`cg-m3`/`cg-m4`/`cg-m5` 沙盒全綠,原倒退已消。
引句:「_CLAUSE_ENUM = r"(?:[A-Za-z一二三四五六七八九十甲乙丙丁]{1,2}[.、)）]\s*)?"」

**i2(雙反引號 span 先剝、未閉合反引號之後一律不信)修了但引入新洞,見 Finding A**。雙反引號包住 `[test:]`/`[manual:]` 都正確被剝成未標(獨立餵 `` `` [test:t_ok] `` `` 得 untagged,不只測試檔裡的 `[manual:]` 案例);但「未閉合之後一律不信」的實作用 `line.split("`",1)[0]` 整行從殘留反引號起砍,當殘留反引號出現在 `[SN]` 之前,整個條款(含 id 本身)會從回傳結果消失,不只是它的證據標記。
引句:「line = line.split("`", 1)[0]」

**i3(`~~~` 也是圍欄,改在全檔共用的 `_visible_lines`)修好**。`fence`/`search` 子集(10+126 案例)沙盒全綠,`~~~` 內文字對 clause/search/refcheck 一致不可見;非成對場景與既有 ``` 未閉合時「整段吞到檔尾」是同一種、非新引入的既有取捨,未發現額外副作用。
引句:「if ln.lstrip().startswith(("```", "~~~")):」

**i4(像清單的未知前綴不論有沒有其他合法條款一律擋)修好**。讀碼確認 `listlike` 判斷與 `return "fail"` 在 `if not clauses:` 之前執行,不再受「零條款」條件保護;獨立餵「已有合法 `[S1]` + 未知前綴 `[S2]`」與 `cg-m6` 一致擋下,繞過路徑已堵住。
引句:「不管有沒有別的條款,格式看不懂就擋」

**i5(單行 HTML 註解剝掉)修好,有未擴大的殘留缺口**。`<!-- [S1] -->` 單行案例(`cg-m7`)沙盒綠,不再被當未知清單擋;⚠ 多行 `<!-- … -->` 因為剝除正則逐行跑、沒有跨行狀態,中段內容仍是可見文字——這不是本輪新增的洞(本輪從未宣稱處理跨行),不列為 blocking finding。
引句:「line = re.sub(r"<!--.*?-->", "", raw)」

**i6(handoff 印重複數)修好**。`cmd_handoff` 的 JSON/人讀兩路都用 `_clause_summary` 統一算 `duplicate` 桶,人讀行只在 `_cc.get("duplicate")` 為真時才加「、編號重複 N」,不影響零重複時的舊格式;delta 測試無對應斷言但程式碼直接確認邏輯正確。
引句:「f"、編號重複 {_cc['duplicate']}" if _cc.get("duplicate") else ""」

**i7(docstring 過時段落改寫)修好**。逐一核對 `_disposal_clause_step` 實際六個 `return "fail"` 出口(ts 讀不動/非 .md/索引建不起來/listlike/重複定義/未標),與 docstring 列的六種一一對應,不多不少;舊的「下一個 [SN] 之前」措辭已不在文中。
引句:「fail 六種:設計審審材不是 .md / 首筆帳 ts 讀不動 / 測試索引建不起來」

**i8(spec-trace 重複編號印 ✗ 不是 ⚠)修好**。`cmd_spec_trace` 的 `mark` 運算式把 `"duplicate"` 併進 `"✗"` 分支(不再只判 `"untagged"`),rc 早已正確(`untagged` 清單本就含 duplicate),現在圖示跟 rc 語意一致了。
引句:「mark = "✓" if (b and b["state"] in ("bound", "manual")) else ("✗" if (b and b["state"] in ("untagged", "duplicate")) else "⚠")」

**i9(listlike 只看該行第一個 [SN])修好**。`fallback.setdefault` 用 `i == 0` 限定只有列舉裡第一個 match 才算 listlike 候選,獨立餵「- [S1] 甲,詳見 [S2] 那段」(S2 非首個)與測試 `S31`/`cg-p` 一致不再被誤判為像清單。
引句:「fallback.setdefault(int(m.group(1)), (no, line[m.end():], i == 0 and bool(_CLAUSE_LISTLIKE_RE.match(line))))」

## delta 引入的新洞

### Finding A
severity: blocker
blocking: 是——一個未閉合(或行內奇數個)反引號若出現在 `[SN]` 之前,`line.split("`", 1)[0]` 會把整行從殘留反引號起全部砍掉、連 `[SN]` 本身都消失,若這是文件裡唯一一次出現則 `clause_bindings` 回傳 `[]`、`_disposal_clause_step` 前置的 `SPEC_CLAUSE_RE.search(text)` 仍認得原文有 `[SN]` 卻拿到空 rows,落進「視同 opt-in 未啟用」分支靜默 `skip`,整條款不印任何錯誤地完全沒被查核,直接違反本輪自己記的 ★INVARIANT★。
引句:「line = line.split("`", 1)[0]」
file: `scripts/lumos:4080`(砍尾邏輯)、消費端 `scripts/lumos:13468-13470`(空 rows 落「opt-in 未啟用」分支,靜默 skip)
最小重現(沙盒已實跑):`clause_bindings("- \`意外反引號 [S1] 真條款 [manual:對帳一次]\n", ...)` 與行內三反引號版本 `clause_bindings("- 說明 \`\`\`範例文字 [S7] 真條款 [manual:對帳一次]\n", ...)` 均回傳 `[]`,而 `SPEC_CLAUSE_RE.search` 掃原文仍找得到 `[S1]`/`[S7]`,證明條款是被解析器吃掉而非本來就沒有。

### Finding B
severity: major
blocking: 是——`_CLAUSE_ENUM` 允許任意 1–2 個 ASCII 字母加分隔符、不限常見枚舉字母,中英混排文件裡常見的拉丁縮寫(`cf.`/`vs.`/`no.` 這類兩字母+句點)出現在行首時會被 `_CLAUSE_LEAD_RE` 誤判成新的條款定義行,若該編號在別處已有真定義,這一行就被記成 `dup.setdefault`、`_disposal_clause_step` 判「條款編號重複定義」FAIL,一句無關的引註句子就能擋下整份合法計劃。
引句:「同編號在兩行都寫成定義 → 重複(r3 外家席:第二筆沒標會漏過)」
file: `scripts/lumos:4051`(`_CLAUSE_ENUM` 定義過寬)、`scripts/lumos:4089`(誤判觸發 duplicate 分支)
最小重現(沙盒已實跑):`clause_bindings("- [S1] 甲 [manual:人看一次]\n- cf. [S1] 前述已定義,詳見上文\n", ...)` 回傳 `[{'id': 'S1', ..., 'state': 'duplicate', 'dup_lines': [1, 2]}]`,第二行純屬引註句,`cf.` 不是刻意造字而是真實可能出現的拉丁縮寫。

### Finding C
severity: major
blocking: 是——`_CLAUSE_LISTLIKE_RE` 的 `\w{1,3}[.、)）:：]` 分支用 `\w` 而非限定枚舉字元,任何 1–3 字中文詞加冒號(「詳見:」「備註:」這類常見文件寫法)直接接一個從沒真正定義過的 `[SN]`,都會被判 listlike 而讓 `_disposal_clause_step` FAIL 整個閘,即使那行明明是散文引用,docstring 自己寫的「前面是詞才算散文」只涵蓋空格分隔、沒涵蓋冒號直接黏著的變體。
引句:「_CLAUSE_LISTLIKE_RE = re.compile(r"^\s*(?:[^\w\s]+\s*|\w{1,3}[.、)）:：]\s*)*\[S(\d+)\]")」
file: `scripts/lumos:4053`
最小重現(沙盒已實跑):`clause_bindings("詳見:[S9] 上述已定義過(但 S9 從沒真的定義)\n", ...)` 回傳 `[{'id': 'S9', ..., 'state': 'undefined', 'listlike': True}]`,同樣文字改成空格版「詳見 [S9] …」則 `listlike=False`(與測試 `S31` 一致),差別只在冒號有沒有貼著。

## 總結

最嚴重 severity:blocker(Finding A)。blocking 條數:3(Finding A/B/C)。
