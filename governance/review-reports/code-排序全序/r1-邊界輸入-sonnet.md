severity: minor

# 邊界與輸入審查:`_sort_pins(pins, home_on)`

材料:`governance/review-reports/code-排序全序/r1-code.patch`。

方法:把 `scripts/lumos` 複製到 `/tmp/sortpins-test/lumos_copy.py`,用
`importlib.machinery.SourceFileLoader` 匯入(跟 `test_lumos.py` 的
`_load_lumos_inproc` 同一套手法),直接呼叫 `_sort_pins` 餵各種邊界輸入,
再回頭讀 `scripts/lumos` 裡真正組出 `results`/`pins` 的那幾段(`cmd_impact`
第 23026–23300 行、`_impact_mark_home`、`_impact_mark_about`),確認缺欄位
情境在真實資料流裡到不到得了。沒有修改 repo 內任何檔案,也沒有跑會寫進
`governance/eval/retrieval-eval-history.jsonl` 的指令。

## 實測結果

| 輸入 | 呼叫 | 實際結果 | 判定 |
|---|---|---|---|
| `pins=[]` | `_sort_pins([], True)` / `(False)` | 回 `[]`,無例外 | 正常 |
| 單筆候選 | `_sort_pins([{node,kind,score,pinned,home}], True)` | 回原樣單筆 | 正常 |
| 缺 `kind` | `_sort_pins([{node,score,pinned}], True/False)` | `KeyError: 'kind'`(兩分支皆炸) | 到不了真實路徑(見下方分析) |
| 缺 `home` | `_sort_pins([{node,kind,score,pinned}], True)` | 正常排序,`home` 視為 `False` | 正常(`.get` 已防呆) |
| 缺 `score`、且 `home` 不存在/`False` | `_sort_pins([{node,kind,pinned}], True)` | 正常(不觸發 `r["score"]`) | 正常 |
| 缺 `score`、但 `home=True` | `_sort_pins([{node,kind,pinned,home:True}], True)` | `KeyError: 'score'` | 到不了真實路徑 |
| 缺 `node`(`home_on=True`,`home=False`) | `_sort_pins([{kind,score,pinned,home:False}], True)` | `KeyError: 'node'` | 到不了真實路徑 |
| 缺 `node`(`home_on=False`) | `_sort_pins([{kind,score,pinned}], False)` | `KeyError: 'node'` | 到不了真實路徑,但**這是本次改動新增的依賴**(見發現 2) |
| `score=None`,`home=True` | 同上 | `TypeError: bad operand type for unary -: 'NoneType'` | 到不了真實路徑 |
| `score='abc'`,`home=True` | 同上 | `TypeError: bad operand type for unary -: 'str'` | 到不了真實路徑 |
| `score` 為負數(混合正負) | `[{score:-5,home:True},{score:3,home:True}]` | 正確排出高分在前(`B(3)` 先於 `A(-5)`) | 正常 |
| `node=None` 混排字串 | `[{node:None,...},{node:"B.md",...}]`(True/False 皆同) | `TypeError: '<' not supported between instances of 'str' and 'NoneType'` | 到不了真實路徑 |
| `node` 為 `int` 混排字串 | 同上型態 | `TypeError: '<' not supported between instances of 'str' and 'int'` | 到不了真實路徑 |
| `node=""` | 與正常字串混排 | 正常,空字串排最前 | 正常 |
| `node` 含換行 / 非 ASCII(CJK)/ 極長字串(1 萬字) | 三者混排 | 正常排序,無例外 | 正常 |
| 兩筆完全相同 `node`(重複候選) | `[{node:"DUP.md",...}, {node:"DUP.md",...}]` | 正常回兩筆,順序保留(stable sort),不去重、不增減 | 正常(去重責任本就不在這支函式) |
| `home_on=True` vs `False` 餵同一批混合資料 | 事故+家+一般候選各一筆 | `True` 排出 `[事故,家,一般]`;`False` 排出 `[事故,一般,家]` | 正常(見發現 3,兩分支準則本就不同,屬既有設計) |
| 亂序輸入(7 筆同 `kind`/`score`,`home_on=True`) | 原序 vs `random.Random(7).shuffle` 後 | 排序結果一致(不受輸入序影響) | 修復目標達成 |
| 亂序輸入(同上,`home_on=False`) | 原序 vs 多組隨機 shuffle(10 個亂數種子) | 10 組全部收斂到同一個排列 | 修復目標達成(且擴及未在文件中明講的這條分支) |

## 發現

### 發現 1:直接索引 `kind`/`score`/`node` 缺欄位會炸例外,但真實資料流保證這些欄位一定存在

引句:「out.sort(key=lambda r: (r["kind"] != "incident", not r.get("home", False),」

實測證實:候選字典缺 `kind`、或 `home=True` 時缺 `score`、或缺 `node`,都會讓
`_sort_pins` 直接拋 `KeyError`。但往上追 `cmd_impact` 組裝 `results` 的每一個
來源都在建構當下就明寫這三個欄位:

- 事故:`file: scripts/lumos:23224`(`results.append({"node": x["node"], "kind": "incident", "pinned": True, "score": 1.0, ...})`)
- direct:`file: scripts/lumos:23249`(含 `"node"`, `"kind": "direct"`, `"pinned"`, `"score"`)
- indirect(硬合約保送 / 一般):`file: scripts/lumos:23276`、`scripts/lumos:23285`(同樣三欄齊全)
- 家(`_impact_mark_home` 新增項):`file: scripts/lumos:22855`(`{"node": node, "kind": "home", "pinned": True, "home": True, "home_of": [rel_file], "score": 0.0}`)——新增時一定帶 `score`;對既有項只補 `cur["home"]=True`,不會動到已經存在的 `kind`/`score`。

也就是說,唯一呼叫點 `file: scripts/lumos:23296`(`pins = _sort_pins([r for r in results if r["pinned"]], _home_on)`)餵進去的每一筆,`kind`/`score`/`node` 都在更早的步驟被無條件寫入,沒有任何分支會產出缺這三欄的字典。缺欄位分支到不了真實輸入。

severity: minor
blocking: 否——例外情境已用實測證實在目前唯一的呼叫路徑上到不了,屬於「記錄脆弱性」層級,不是會被真實資料觸發的缺陷。

### 發現 2:`home_on=False` 分支新增了對 `r["node"]` 的依賴,原本這條分支完全不看 `node`

引句:「out.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False), r["node"]))」

比對 patch 刪掉的舊碼:`home_on=False` 分支原本是
`pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))`——
兩元素 tuple,完全不觸碰 `"node"`。新版加了第三個鍵 `r["node"]`,這是本次
「末項一律用節點名斷開」修復的延伸(docstring 只舉了 `home_on=True` 那條分支的
根因,但實際上兩條分支都補上了同一種收斂),實測也證實這條分支現在對亂序
輸入一樣能收斂成單一排列(見上表倒數第二列)。

代價是:這條分支現在多了一個新的失敗面——如果某天有候選缺 `node`,`home_on=False`
時會炸,而過去不會。目前查證下真實候選一律帶 `node`(前一條發現已列出所有
建構點),所以現階段到不了;只是修復把兩條分支的脆弱性從「不對稱」變成
「對稱」,值得記一筆,以防日後有人新增建構路徑時漏帶 `node`。

severity: minor
blocking: 否——目前所有候選建構點都保證帶 `node`,這個新增依賴到不了真實路徑;純粹記錄「修復範圍比 docstring 講的更廣、且引入了對稱的新失敗面」供之後留意。

### 發現 3:`home_on` 兩分支對同一批輸入排序結果不同,但這是既有設計行為,不是本次改動造成的

引句:「旋鈕開著時走「家」這條入口,旋鈕關掉照舊走 about 標記那一套」

實測混合輸入(事故 1 筆、`home=True` 高分 1 筆、`home=False` 低分 1 筆)在
`home_on=True` 排成 `[事故, home筆(Z), 一般筆(A)]`,`home_on=False` 排成
`[事故, 一般筆(A), home筆(Z)]`——因為 `False` 分支根本不看 `home`/`score`,
只看 `about_hit`(此例三筆 `about_hit` 皆為 `False`,退到 `node` 字母序,
`A.md` < `Z.md`)。這個差異在改動前就存在(呼叫端註解見
`file: scripts/lumos:23287`:「旋鈕開著時走『家』這條入口,旋鈕關掉照舊走 about 標記那一套」),
本次 patch 只是把兩段既有邏輯原封不動抽成 `_sort_pins`,並沒有讓兩分支的
判準趨同或惡化(該註解實際位置是 `file: scripts/lumos:23287`,前一段引用的
行號範圍已更正)。

severity: minor
blocking: 否——兩分支排序準則不同是設計選擇(旋鈕語意本來就是切換兩套判準),不是本次改動引入的不一致,記錄供之後若有人誤以為兩分支「應該同序」時查證。

## 結論

本次抽出的 `_sort_pins` 把原本「只有『家』那一類拿節點名斷同分」的偏袒寫法,
改成兩條分支(`home_on` 開/關)都用 `node` 當最終斷開鍵;實測用亂序輸入反覆
驗證,兩分支現在都能把同一批候選收斂成單一、不受輸入序影響的排列,達成
patch 聲稱的目標。缺欄位/型別錯誤只在人為構造的測試輸入下出現,追查真實
唯一呼叫路徑(`cmd_impact` 組裝 `results` 的每一段)後確認候選在建構當下就
保證帶齊 `node`/`kind`/`score`,兩條分支目前都到不了那些例外分支。

全篇最高等級為輕微,阻塞條數為零。
