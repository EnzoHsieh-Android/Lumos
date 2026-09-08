severity: clean

# 架構對齊審查——code-clause-bindings-b(r1,sonnet)

被審(凍結):全量 `governance/review-reports/code-clause-bindings-b/r1-snapshot.patch`;delta `governance/review-reports/code-clause-bindings-b/r1-delta.patch`。只判前一編號(code-clause-bindings)第 3 輪折入(delta)有沒有引入「跟這個專案既有做法不一樣」的寫法,以及前輪本席那條 major(自寫第二份反引號遮蔽正則)折入後對不對齊。不找 bug、不評風格。前輪:`governance/review-reports/code-clause-bindings/r3-架構對齊-sonnet.md`。

LUMOS-IMPACT: Lumos/main..HEAD

---

## 1. 分層與依賴方向

**判定:對齊。**

檢查點——新增的 `duplicate` 狀態偵測有沒有把「決策/印訊息」的活動搬進 `clause_bindings` 這支自稱「唯讀、純函式」的計算層。折入後,偵測到同編號兩行都定義時,`clause_bindings` 只把行號塞進一個純資料結構,不印、不擋:

> 引句:「dup.setdefault(cid, []).append(no)   # 同編號在兩行都寫成定義 → 重複(r3 外家席:第二筆沒標會漏過)」

真正把 `duplicate` 這個狀態翻成「要不要擋」的判斷與印訊息,留在呼叫端 `_disposal_clause_step`:

> 引句:「dups = [b for b in clauses if b["state"] == "duplicate"]」

這跟同一支函式裡既有的 `unt`(untagged)那條——`clause_bindings` 只回傳 state,呼叫端才決定印什麼、回 fail 還是 ok——是同一種「計算與決策分離」的既有分工,沒有新開一條跨層直呼的路。

再對照本專案對「同名/多筆候選」既有的兩種既有慣例:CLI 單筆查詢型(`env.find`,呼叫端需要一個答案才能往下走)是「警告 + 取第一筆」(file: `scripts/lumos:397`);結構性索引/守衛型則是「不靜默取任何一筆,整批列出來擋」——`build_typed_index` 的文件明講「同名無路徑 [[X]] 多篇候選 → ambiguous + 候選清單(嚴禁靜默指第一篇」(file: `scripts/lumos:419-422`),另有 frontmatter 同層欄位重複鍵也是直接判 lint error、不取第一個(file: `scripts/lumos:224`)。`_disposal_clause_step` 是閘(結構性守衛),`duplicate` 折入後選的是後一種既有慣例——`dup_lines` 把所有重複行號都列出來一起印(file: `scripts/lumos:13470`),不是靜默留第一筆、蓋掉第二筆——選對了既有分岔的哪一支。

- severity: clean
- blocking: 否

---

## 2. 命名與錯誤處理

**判定:對齊。**

檢查點①——`_handoff_clause_counts` 的 `c["total"] = None if err else len(rows)`(file: `scripts/lumos:20912`)是不是本專案 --json 輸出裡「算不出就吐 null,不假裝算得準」的既有慣例,還是自己發明的處理法:

> 引句:「c["total"] = None if err else len(rows)   # 索引建不起來時各態算不出,不報 0(r3 外家席 minor)」

同檔已有幾乎同構的既有先例,`loop status` 系列查詢遇到「有的帶輪次、有的不帶」混用資料時,也是回 `None` 而不是硬湊一個數字,理由寫在旁邊註解:「唯讀查詢不該擋,但也不該假裝算得準:混用就回 None」(file: `scripts/lumos:6093-6098`,程式碼:`"rounds": None if _mixed else (len(e["rounds"]) or e["records"])`)。兩處哲學與寫法(`None if <算不準旗標> else <實際算出的值>`,直接塞進之後會被 `json.dumps` 序列化的 dict)幾乎逐字對應,不是新句型。

檢查點②——`duplicate` 這個新狀態值在 `_CLAUSE_STATE_ZH` 裡的措辭風格跟既有幾個狀態是否一致:

> 引句:「"undefined": "非定義(只在範例/引用裡出現,不算條款)", "duplicate": "編號重複定義(兩行都寫 [SN])"}」

「標籤 + 括號補一句白話原因」的格式跟同一 dict 裡 `unrecognized`/`mentioned`/`bad-name` 既有幾條的寫法相同,沒有另立一套命名風格;`_disposal_clause_step` 印出的擋下訊息也延續同函式既有的「哪幾條(第 N 行)+ 為什麼要擋」句型(跟 `unt` 那條 `"、".join(f"{b['id']}(第 {b['line']} 行)" ...)` 同構,只是多筆行號改用 `/` 串接,見 file: `scripts/lumos:13470`),不是新句型。

- severity: clean
- blocking: 否

---

## 3. 第二種做法

**判定:對齊(前輪本席 major 已折平;`_CLAUSE_LISTLIKE_RE` 未構成第二套判定)。**

檢查點①——前輪(r3)major:折入前 `clause_bindings` 自己寫了一支 `re.sub(r"`[^`]*`", ...)` 剝反引號,跟全檔唯一的 `_visible_lines`/`INLINE_CODE_RE` 原語各自為政。本輪折入把它換掉:

> 引句:「for no, raw in _visible_lines(text.split("\n"), keep_fenced=False):」
> 引句:「        line = INLINE_CODE_RE.sub("", raw)」

這兩行逐字對照 D1(接手視圖候選收集)既有的同一組合(file: `scripts/lumos:13960-13961`,`for _no, ln in _visible_lines(text.split("\n"), keep_fenced=False): probe = INLINE_CODE_RE.sub("", ln)`)——不只是「精神類似」,是同一組原語、同一種參數、同一種呼叫順序,連變數名的角色都對得上。折入處自己的註解也直接點名這正是在還前輪的債:

> 引句:「★哪些字看得見=沿用全檔唯一那份實作★(_visible_lines 逐行 fence 切換 + INLINE_CODE_RE 剝行內反引號;r3 架構席:自寫第二份正則」

**已對齊。** r3 那條 major 折入後不再是「另立一套」,是回到 `_search_visible_lines`/D1/`cmd_search` 共用的那一份既有原語(file: `scripts/lumos:2502`、`2536-2550`)。

檢查點②——新增的 `_CLAUSE_LISTLIKE_RE`(`^\W*\[S(\d+)\]`,寬鬆)跟既有的 `_CLAUSE_LEAD_RE`(嚴格,列舉合法前綴符號)放在一起,是不是又形成第二套「這行算不算定義」的判定,跟前輪那個坑同類:

實際用法是——`_CLAUSE_LISTLIKE_RE` 只套用在已經被 `_CLAUSE_LEAD_RE` 判定為「不是定義行」(`cid not in defined`)的那個子集合上,只多標一個 `listlike` 布林旗標,不會回頭改變 `defined`/`fallback` 的分桶結果:

> 引句:「                        "listlike": bool(_CLAUSE_LISTLIKE_RE.match(text.split("\n")[no - 1]))})」

真正「算不算條款」的權威判定自始至終只有 `_CLAUSE_LEAD_RE` 一份;`_CLAUSE_LISTLIKE_RE` 只決定「這個已經被判掉的 id,訊息要講成『看不懂的清單寫法,擋』還是『純散文提及,skip』」。本專案已有一模一樣的既有架構:`SYMBOL_RE`(嚴格,白名單式樣、是全檔唯一的符號判定,file: `scripts/lumos:2307`)決定真正的符號分類,`SYMBOLISH_RE`(寬鬆,`^([A-Z]{2,}):`)只在 lint 額外抓「像打錯字」的近似案例、不參與真正分類(file: `scripts/lumos:3578-3579`、`3968-3970`,程式碼 `ms = SYMBOLISH_RE.match(line); if ms and ms.group(1) not in SYMBOL_NAMES: warns.append(...)`)。「嚴格判定 + 寬鬆近似判定專供訊息分流、不回頭動權威分類」是既有慣例的延伸,不是自造第三種。

- severity: clean
- blocking: 否

---

## 小結

不對齊共 0 條,其中 major 0 條。
