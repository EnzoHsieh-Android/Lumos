severity: minor

# 邊界與輸入審查——code-標註防污染 r1

審的是 `governance/eval/refresh_labels.py` 這次新增的兩塊:`cmd_delta` 的洗牌段、新的 `cmd_material` 子命令,以及兩者共用的 `_read_goldset`。全部發現都是實際造夾具、跑指令或直接呼叫函式驗出來的,不是只讀程式碼推測。夾具與探針全部放在 `/tmp/rlbench/`,沒有動 repo 裡任何檔,也沒有跑會寫進正式評測歷史帳的指令。

## 一、待標清單洗牌(`cmd_delta`)

### 發現 1:種子綁的是「分組版本常數」,不是題庫本身的內容;程式註解自己講的「不同題庫也不會洗成同一種排法」不成立

引句:「種子綁題庫身分與案例編號,不同案例各自洗、不同題庫也不會洗成同一種排法。」

引句:「_salt = str(gs.get("split_salt") or gs.get("snapshot_commit") or "")」

`_salt` 只取自 `split_salt`(或退而求其次的 `snapshot_commit`),不是把題庫的實際內容(search/edit/labels)算進去。真實題庫裡 `split_salt` 是固定字串 `"lumos-retr-v1"`(file: `governance/eval/retrieval-goldset.json:3`)——這是「標註方案版本」用的常數,不是「這一份題庫」的身分證。只要兩份題庫都設同一個 `split_salt`(這正是它被設計成的用法:同一套標註規範下的題庫共用同一個版本標記),同一個案例編號、同一組候選,就會洗出一模一樣的排法。

實測(直接抓 r1 commit `f6d481c5` 當下的 `cmd_delta` 邏輯來跑,確認測的是這份 patch 的程式碼,不是工作目錄裡後來另外修過的版本):

| 輸入 | 實際輸出 | 判定 |
|---|---|---|
| 題庫甲:`split_salt="lumos-retr-v1"`,案例 C1 候選 `[A,B,C,D,E]` | C1 洗出 `[A, E, D, C, B]` | — |
| 題庫乙:完全不同的查詢字串、不同其他案例、不同 `snapshot_commit`,但同樣 `split_salt="lumos-retr-v1"`,同樣有一題 C1、候選也是 `[A,B,C,D,E]` | C1 洗出 `[A, E, D, C, B]`(與題庫甲逐字相同) | 兩份「完全不同」的題庫,同一案例編號洗出同一種排法——與程式自己的註解矛盾 |

這條洞已被同一批審查裡另一個鏡頭(`r1-外家finder-codex.md` 發現 2)獨立撞到,而且工作目錄裡已經有一份**尚未提交**的修正(把 `_salt` 改成對題庫全文算 SHA256 指紋),可以互相印證這不是我判斷錯誤。降級考量:即使種子撞在一起,「先排序再洗」這一步已經把原始名次序破壞掉了——洩漏名次(S8 要擋的核心風險)並不會因為這個洞重新發生,受損的只是「不同題庫互相獨立」這個較窄的承諾,所以歸類非阻塞。

severity: minor
blocking: 否——先排序已擋住名次外洩(S8 的核心風險),這個洞削弱的是跨題庫獨立性這個較窄的承諾,且已有另一鏡頭獨立發現並在工作目錄提出修正

### 發現 2:`split_salt` 是假值(`0`、空字串)時,`or` 鏈會悄悄放棄它、改用別的欄位

引句:「_salt = str(gs.get("split_salt") or gs.get("snapshot_commit") or "")」

Python 的 `or` 對 `0`、`""`、`None` 一視同仁地當「沒有值」處理。如果題庫的 `split_salt` 剛好合法地被設成 `0`(例如未來改成用整數版本號)或空字串,種子會靜默改用 `snapshot_commit`,而不是照欄位優先序原本要表達的意思。

實測(固定 `snapshot_commit="fallback-commit"`,只改 `split_salt`):

| `split_salt` 值 | 實際洗出的順序 | 判定 |
|---|---|---|
| 完全缺欄位 | `[N02, Gamma, N01, N07, N04, N06, N05, N03, N00]` | 基準 |
| `0`(數字,假值) | 與「完全缺欄位」逐字相同 | `0` 被當成沒設,悄悄退回 `snapshot_commit` |
| `"0"`(字串,真值) | `[N06, N07, N02, N05, N03, N00, N01, N04, Gamma]`(不同) | 字串 `"0"` 才真的被當成種子用 |

不會當機、也不會產生錯誤訊息,只是選錯種子來源而不自知。目前真實題庫的 `split_salt` 是非空字串,不會踩到,所以評為次要、不阻塞。

severity: minor
blocking: 否——現行真實題庫的 split_salt 恆為非空字串,不會觸發;真觸發也只是換一個仍然決定性的種子,不會當機或外洩名次

### 發現 3:洗牌前的 `sorted(nodes)` 對候選內容沒有型別防呆,遇到非字串會讓整支指令未攔截地當機

引句:「_shuffled = sorted(nodes)」

這行是這次新加的。改之前,`cmd_delta` 只對 `u["per_case"]` 的外層鍵(案例編號,恆為字串)排序,從不動裡面的候選清單;改之後多了 `sorted(nodes)` 這一步,而 `nodes` 是共用實作 `collect_unjudged`(不在這份 diff 的改動範圍內)回傳的東西,這裡沒有驗證過它的成員型別。

實測(把 `collect_unjudged`換掉、直接餵控制過的候選清單給 `cmd_delta`):

| 候選清單內容 | 實際結果 | 判定 |
|---|---|---|
| 重複節點名 `[A, A, B]` | rc=0,正常洗出三個(含重複) | 乾淨 |
| 空清單 `[]` | rc=0,案例照樣輸出、候選欄位是空陣列 | 乾淨(真實 `collect_unjudged` 本來就不會回傳空候選案例) |
| 單一節點 `[Only]` | rc=0,原樣輸出 | 乾淨 |
| 混入整數 `[A, 123, B]` | `TypeError: '<' not supported between instances of 'int' and 'str'`,未攔截例外,rc 落在 Python 預設值 1 | 當機 |
| 混入 `None` `[A, None, B]` | `TypeError: '<' not supported between instances of 'NoneType' and 'str'` | 當機 |
| 全部同型別的整數 `[1, "A", 2]` | 同上,`TypeError` | 當機 |

目前 `collect_unjudged` 的兩條資料來源(`_touched_search`/`_touched_edit`)理論上只會產出字串(來自 `lumos search --json`/`lumos impact --json` 的 `"node"` 欄位,見 file: `governance/eval/retrieval_eval.py:119`、file: `governance/eval/retrieval_eval.py:192`),所以在現有 lumos 版本下不會自然觸發;但這個假設沒有寫成防呆,一旦上游 JSON 哪天出現 `"node": null` 這種壞資料,`cmd_delta` 會用未攔截的原始 traceback 當掉,而不是走這支檔案自己一貫的 `ERROR: ...` + rc2 慣例。

severity: minor
blocking: 否——需要另一個模組(collect_unjudged 的資料來源)先出錯才會觸發,現有輸入形狀下不可達;失敗方式是當機而非產生誤導性輸出,不會弄壞已標資料

## 二、題目卷(`cmd_material`)

### 發現 4:案例缺 `id`/`query`/`file` 欄位時,直接未攔截地丟 `KeyError`;缺 `delta` 則有安全預設,兩種待遇不一致

引句:「for c in sorted(gs.get("search", []), key=lambda x: x["id"]):」

引句:「lines.append(f"- {c['id']}｜查詢:」

實測:

| 題庫內容 | 實際輸出 | rc | 判定 |
|---|---|---|---|
| `search` 缺整個鍵(只給 `edit`+`labels`) | `ERROR: goldset 讀取/結構失敗: 'search'` | 2 | 乾淨(這一層由共用的 `_read_goldset` 擋住) |
| `edit` 缺整個鍵 | `ERROR: goldset 讀取/結構失敗: 'edit'` | 2 | 乾淨 |
| `search`/`edit` 都是空陣列 | `material: 搜尋題 0、編輯題 0 → ...` | 0 | 乾淨 |
| 某 search 案例缺 `id` | 未攔截 `KeyError: 'id'`(在 sort 的 `lambda x: x["id"]` 裡) | 1 | 當機 |
| 某 search 案例缺 `query` | 未攔截 `KeyError: 'query'` | 1 | 當機 |
| 某 edit 案例缺 `file` | 未攔截 `KeyError: 'file'` | 1 | 當機 |
| 某 edit 案例缺 `delta` | `material: 搜尋題 0、編輯題 1 → ...`,`delta` 欄位印成 `(未記)` | 0 | 乾淨(唯一有 `.get(..., 預設值)` 的欄位) |

同一個函式裡,`delta` 欄位用 `c.get('delta', '(未記)')` 有預設值、其他三個欄位直接 `c['...']` 或 `x["id"]` 硬取,待遇不一致。這類欄位缺漏最可能發生在題庫手動編修、案例先建骨架再補內容的過程中——不是惡意輸入,是操作失誤就會踩到。失敗方式是當機(印原始 Python traceback、rc 落在 Python 預設的 1),不是靜默印出 `None` 或吃進不該吃的答案,所以不會弄壞防污染這件事本身要保護的東西,只是體驗差、rc 語意跟這支檔案其他地方(`_read_goldset`/`_orphans` 等一律乾淨 rc2)不一致。

severity: minor
blocking: 否——當機是安全失敗(不產生檔案、不外洩任何東西),只是報錯體驗跟本檔案其餘部分的慣例不一致

### 發現 5:輸出路徑異常(本身是目錄、父目錄不存在、無寫入權限)同樣未攔截,直接當機

引句:「out.write_text("\n".join(lines), encoding="utf-8")」

實測(`--goldset` 用合法的空題庫,只換 `--out`):

| `--out` 情境 | 實際結果 | rc |
|---|---|---|
| 指到一個已存在的目錄 | 未攔截 `IsADirectoryError: [Errno 21] Is a directory` | 1 |
| 父目錄不存在 | 未攔截 `FileNotFoundError: [Errno 2] No such file or directory` | 1 |
| 目錄存在但無寫入權限(`chmod 555`) | 未攔截 `PermissionError: [Errno 13] Permission denied` | 1 |

這三種都印出完整 Python traceback(含本機檔案的絕對路徑),而不是這支檔案別處慣用的一行 `ERROR: ...` 訊息。順帶查證:`cmd_delta` 寫輸出檔那行(file: `governance/eval/refresh_labels.py:220`,`Path(out + "-sheet.md").write_text(...)`)在這份 diff 之前(`git show c01d8372:governance/eval/refresh_labels.py` 已存在同寫法)就長這樣、不是這次新增的,同樣情境下也一樣未攔截當機——所以這是這支檔案既有的寫檔慣例,`material` 只是照抄了同一種寫法,不是這次新引入的退步。

severity: minor
blocking: 否——沿用既有檔案一貫(未做防呆)的寫檔方式,不是本次新增的退化,且失敗方式不會產生半成品或誤導內容

### 發現 6:候選/欄位內容含換行或反引號,會弄壞「一案例一行」的排版假設,但不會把後面的內容吃掉

引句:「lines.append(f"- {c['id']}｜改到的檔:`{c['file']}`｜改動:{c.get('delta', '(未記)')}")」

`query`/`delta` 這兩個欄位是自由文字,沒有做逸出處理就直接嵌進單行輸出。實測連續兩個案例、其中第一個的內容帶換行:

```
輸入:S01 query="有換行\n的題目"、S02 query="正常題目"
輸出第 8-10 行:
- S01｜查詢:「有換行
的題目」
- S02｜查詢:「正常題目」
```

| 情境 | 是否當機 | 後續案例內容是否被吃掉 | 排版是否壞掉 |
|---|---|---|---|
| `query`/`delta` 含換行 | 否 | 否(S02/E02 逐字完整,驗證過) | 是——該案例被拆成兩行,第二行沒有 `-` 項目符號 |
| `file` 含反引號 `` src/app`.py`` | 否 | 否 | 是——`` `{c['file']}` `` 這組 code span 被提前截斷 |

沒有資料被吞掉,只是視覺上跟下游若真的按「每行一案例」去切割解析的假設會對不上。`file` 欄位在正常操作下來自真實 repo 路徑,不太會出現反引號;`delta`/`query` 是人工撰寫的自然語言描述,出現反引號或換行是有可能的(例如描述改動時貼一段程式碼)。

severity: minor
blocking: 否——純排版失真,已驗證不會遺失或錯置任何案例內容,也不涉及答案外洩

## 三、共用讀檔邊界(`_read_goldset`,`delta`/`material` 皆走這條路)

實測(`--goldset` 分別指向以下檔案,`delta`/`material` 兩邊都各跑一次):

| 輸入 | `delta` 實際結果 | `material` 實際結果 |
|---|---|---|
| 檔案不存在 | `ERROR: goldset 讀取/結構失敗: [Errno 2] No such file or directory: ...` rc=2 | 同左,rc=2 |
| 內容是壞掉的 JSON(`{not valid json`) | `ERROR: ...: Expecting property name enclosed in double quotes...` rc=2 | 同左,rc=2 |
| 空檔案 | `ERROR: ...: Expecting value: line 1 column 1` rc=2 | 同左,rc=2 |
| 頂層是陣列 `[1,2,3]` | `ERROR: ...: list indices must be integers or slices, not str` rc=2 | 同左,rc=2 |
| 頂層是字串 `"hello"` | `ERROR: ...: string indices must be integers, not 'str'` rc=2 | 同左,rc=2 |
| 頂層是數字 `42` | `ERROR: ...: 'int' object is not subscriptable` rc=2 | 同左,rc=2 |
| 頂層是 `null` | `ERROR: ...: 'NoneType' object is not subscriptable` rc=2 | 同左,rc=2 |

七種輸入、兩個子命令共十四次實跑,全部乾淨地印出一行可讀訊息並回 rc2,沒有任何一種當機或印出 `None`。這條共用邊界做得紮實。

severity: clean
blocking: 否——七種壞輸入 × 兩個子命令全部乾淨處理,沒有找到問題

---

全篇跑下來,最高等級落在次要,總共 0 條會擋這份 diff 推出去;最值得後續留意的是洗牌種子那條(發現 1),已經有另一位審查獨立驗到同一個洞、也已經在工作目錄提了修正,只是還沒進這份 patch。
