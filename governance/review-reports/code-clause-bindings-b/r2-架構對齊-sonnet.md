severity: major

# 架構對齊審查——code-clause-bindings-b(r2,sonnet)

被審(凍結):全量 `governance/review-reports/code-clause-bindings-b/r2-snapshot.patch`;delta `governance/review-reports/code-clause-bindings-b/r2-delta.patch`。只判第 1 輪(`code-clause-bindings-b` r1)折入(delta)有沒有引入「跟這個專案既有做法不一樣」的寫法。不找 bug、不評風格。前輪:`governance/review-reports/code-clause-bindings-b/r1-架構對齊-sonnet.md`(全對齊)。

核對:`r2-delta.patch` 裡 `scripts/lumos` 的變更行(逐行比對)與 commit `04bb7dc`(`code-clause-bindings-b r1 折入 9 條`,`git show HEAD:scripts/lumos` 已含)的變更行集合完全一致——即這批 delta 就是已落盤的 `-b r1` 折入內容。baseline 用 `git show HEAD:scripts/lumos`(=`/tmp` 落地副本)讀既有慣例。

LUMOS-IMPACT: Lumos/main..HEAD

---

## 1. `_visible_lines` 加 `~~~`——其他消費端要不要各自另補

**判定:對齊。**

折入處只動了 `_visible_lines` 這一支「全檔唯一的 fenced-code 判定實作」本身:

> 引句:「        if ln.lstrip().startswith(("```", "~~~")):       # fenced code 邊界(``` 與 ~~~ 都是 CommonMark 圍欄;2026-09-08 條款綁定 -b r1 外家席補 ~~~)」

問題點名的四個消費端逐一核對,全部是「呼叫 `_visible_lines`」而不是「自己 toggle 圍欄」,所以 `~~~` 這個修正對它們是透明生效,不需要各自另補:
- search:`cmd_search` 走 `_search_visible_lines`,後者本身呼叫 `_visible_lines`(file: `scripts/lumos:2760`、`scripts/lumos:2536`)。
- refcheck:`_refcheck_scan` 呼叫 `_strip_fences_text`(file: `scripts/lumos:14570`),`_strip_fences_text` 呼叫 `_visible_lines`(file: `scripts/lumos:2526-2532`)。
- `_strip_fences_text` 本身:file: `scripts/lumos:2526-2532`,一行 `return "\n".join(ln for _no, ln in _visible_lines(text.split("\n")))`。
- `_strip_code_text`:呼叫 `_search_visible_lines`(file: `scripts/lumos:2493`),同上鏈路。

沒有既有測試/文件明說「只認 ```」(grep 全檔 `~~~`/「波浪」找不到這種斷言,見 file: `scripts/lumos:17602` 反而是另一處已經把 ``` 與 ~~~ 並列成「不成對圍欄」的同一組概念)。

附帶一提(不影響本問判定,列出供對照):全檔另外還有兩處**既有、與這批折入無關**的獨立圍欄 toggle,沒有走 `_visible_lines`——`_gist` 自己 `s.startswith("```")`(未補 `~~~`,file: `scripts/lumos:7327-7328`)、`cmd_prose_lint` 自己 toggle 但恰好已含 `~~~`(file: `scripts/lumos:17583-17584`)。這兩處都是這批折入之前就存在、這批也沒有去動——不算本輪引入的新分岔,只是既有分岔的舊帳,不列入不對齊計數。

- severity: clean
- blocking: 否

---

## 2. `clause_bindings` 新增的三行(HTML 註解剝除、雙反引號、未閉合反引號截斷)

**判定:不對齊(major)。**

折入處在 `_visible_lines`/`INLINE_CODE_RE` 之後,又追加三行獨立的文字處理:

> 引句:「        line = re.sub(r"<!--.*?-->", "", raw)                     # 單行 HTML 註解不是內容(-b r1 外家席:`<!-- [S1] -->` 曾被當未知清單擋)」
> 引句:「        line = INLINE_CODE_RE.sub("", re.sub(r"``.+?``", "", line))   # 雙反引號 span 先剝,再剝單反引號 span(沿用 INLINE_CODE_RE)」
> 引句:「        line = line.split("`", 1)[0]                              # 還剩下的反引號=未閉合:後面一律不信(程式碼範例裡的標記不能當證據;寧可少認也不放行)」

逐項核對「這個專案有沒有既有的同類處理」:
- HTML 註解剝除:全檔 grep `<!--` 只有 CLAUDE.md 注入的 sentinel 常數(file: `scripts/lumos:138-139`)與一個專用指令 `<!--lumos:count=...-->` 的解析正則(file: `scripts/lumos:2142`)——兩者都是「辨認特定指令標記」,不是「把 HTML 註解當成雜訊剝掉、視為不可見文字」的通用規則。沒有既有的「HTML 註解=不可見」原語。
- 雙反引號 span:全檔唯一的行內 code 正則 `INLINE_CODE_RE = re.compile(r"`[^`\n]*`")`(file: `scripts/lumos:162`)只認單反引號、且用第一個反引號就近配對——實測對 `` `` X `` `` 這種相鄰雙反引號會誤配成空 span,吃不掉中間夾住的真內容(此為 `-b r1` 要修的那個 bug 本身,不是這裡要判的東西;這裡只判「修法有沒有沿用既有規則」)。既有規則裡沒有處理雙反引號 span 的原語。
- 未閉合反引號截斷(`split("\`", 1)[0]`):全檔 grep `split("\`"` 只有這一處,沒有既有的「一行裡剩下的反引號=未閉合,之後不信」處理慣例。

三行都是這批折入**當場現寫**的新正則/新字串操作,不是呼叫既有原語。這正是 `_visible_lines`/`_strip_code_text` docstring 明講、且同一支函式自己的註解也直接引用過的那個坑——同一個 `clause_bindings` 函式裡,緊接在這三行之上的既有註解才剛講完:

> 引句:「    # ★哪些字看得見=沿用全檔唯一那份實作★(_visible_lines 逐行 fence 切換 + INLINE_CODE_RE 剝行內反引號;r3 架構席:自寫第二份正則」

上一輪(`code-clause-bindings` r3)架構席已經把「圍欄/反引號自己另寫一份正則」判成 major、要求改沿用 `_visible_lines`/`INLINE_CODE_RE`,理由是 2026-08-03 兩份 fence 實作分岔的前科(消費端是治理硬閘,分岔會靜默吃掉真散文/真合約)。這批折入在同一個函式裡,對圍欄那一層乖乖沿用了 `_visible_lines`,但緊接著又在 `INLINE_CODE_RE` 管不到的「HTML 註解」「雙反引號」「未閉合反引號尾段」三個子情況上,各自現寫一段規則,只完成一半「沿用既有原語」的精神——後三行沒有被納入任何具名、可重用的原語(不在 `_visible_lines` 家族裡,也沒有掛在 `INLINE_CODE_RE` 旁邊擴充成新常數),而是散落在 `clause_bindings` 內部的三個行內敘述句。HTML 註解與雙反引號都是通用 CommonMark 概念(不是條款綁定專屬語意),往後任何其他消費端如果也需要「剝掉 HTML 註解 / 正確處理雙反引號」,沒有共用的地方可以呼叫,只能複製這三行——這正是「哪些字看得見」第二套規則的定義,跟第 1 問裡 `~~~` 那一行「改在唯一實作裡」的做法是相反方向。

- severity: major
- blocking: 是

---

## 3. `_CLAUSE_ENUM` 與 `_CLAUSE_LEAD_RE`/`_CLAUSE_LISTLIKE_RE` 跟 `SYMBOL_RE`/`SYMBOLISH_RE` 同不同構

**判定:對齊。**

折入處新增一段可重用的正則片段 `_CLAUSE_ENUM`,拼進既有的 `_CLAUSE_LEAD_RE`(權威判定「這行算不算條款定義行」),同時把 `_CLAUSE_LISTLIKE_RE`(近似判定「看起來像清單卻認不得」)的比對範圍放寬:

> 引句:「_CLAUSE_ENUM = r"(?:[A-Za-z一二三四五六七八九十甲乙丙丁]{1,2}[.、)）]\s*)?"   # a. / 一、/ 甲) 這種短編號也是清單(-b r1 單reviewer:字母/中文編號曾被當散文靜默跳過)」

`_CLAUSE_LISTLIKE_RE` 沒有直接拼 `_CLAUSE_ENUM` 這個片段,而是自己另外寫了一段更寬的「短字元+標點」比對(`\w{1,3}[.、)）:：]`):

> 引句:「_CLAUSE_LISTLIKE_RE = re.compile(r"^\s*(?:[^\w\s]+\s*|\w{1,3}[.、)）:：]\s*)*\[S(\d+)\]")   # 「像清單項卻認不得的前綴」:[SN] 前面只有符號或短編號(x. / 一、/ 甲:)——用來判「零條定義」該擋還是該當純引用;前面是詞(規格 [S1])才算散文」

這個「不共用片段」不是缺陷,是這個專案既有架構要求的:`_CLAUSE_LEAD_RE`(權威、白名單式、只認真正合法的編號系統)與 `_CLAUSE_LISTLIKE_RE`(近似、故意比權威判定寬,專門去接住「用了編號但不在白名單裡」的邊界案例)本來就該是兩個獨立寫死的集合,近似判定如果直接複用權威判定的片段,就永遠抓不到「權威判定拒絕、但看起來像清單」這個它存在的唯一理由。這跟既有的 `SYMBOL_RE`(白名單常數 `KEY|FLOW|DEP|...`,file: `scripts/lumos:2307`)與 `SYMBOLISH_RE`(通用寬鬆型樣 `^([A-Z]{2,}):`,file: `scripts/lumos:3579`,搭配 `SYMBOL_NAMES` 集合另外檢查,file: `scripts/lumos:3578`)的關係同構——`SYMBOLISH_RE` 也沒有從 `SYMBOL_RE`/`SYMBOL_NAMES` 拼出來,是獨立寫的寬鬆型樣,只用來抓「像打錯字的近似案例」,不回頭動權威分類。

呼叫端關係也維持上一輪已核過的分工:`_CLAUSE_LISTLIKE_RE` 只在 `cid not in defined`(已經被 `_CLAUSE_LEAD_RE` 判掉)的分支裡多標一個旗標,不影響 `defined`/`fallback` 分桶,拼 `_CLAUSE_ENUM` 只放寬了「哪些行算合法定義」這一件事,沒有把兩支正則的判定範圍混在一起。是既有「嚴格權威 + 寬鬆近似分流、近似不回頭改分類」架構的延伸調參,不是新結構。

- severity: clean
- blocking: 否

---

## 小結

不對齊共 1 條,其中 major 1 條。
