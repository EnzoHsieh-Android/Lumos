severity: major

# 鏡頭:正確性——照這段程式跑下去,會不會算出錯的答案?

## 發現 1:污染檢查對大小寫不敏感,會漏掉真正的污染(假陰性)

引句:「hits = sorted(n for n, txt in docs.items() if q in txt)」

`contaminated()` 用 `q in txt` 原樣比對,完全沒有做大小寫正規化。但它要保護的那個機制——
`lumos search` 的「整串片語」判定——是大小寫不敏感的:`scripts/lumos:3034-3035`
`needle = nfc(term).lower()` / `matches = lambda s: needle in nfc(s).lower()`,連決定要不要
觸發拆詞回退的預檢也是同一套(同檔案 `_low = nfc(...).lower()`)。

題庫裡本來就有英文詞的查詢,例如 `governance/eval/multiword/mw-pool.json` 的
M02「canary 收斂 判定」。我實測過落差:

```
query = "canary 收斂 判定"
筆記寫成 "CANARY 收斂 判定"(只是大小寫不同):
  contaminated() 的 q in txt        → False(判定乾淨)
  實際 search 的 needle in lower(txt) → True(片語其實命中,拆詞回退不會觸發)
```

也就是說:只要有人在筆記裡用不同大小寫寫下同一個查詢,這支新加的守衛會回報「沒有污染」,
但實際被測的機制早就已經壞掉了——正是這篇改動一開始要堵的那個洞(「兩臂會量出一樣的數字,
而且不會有任何錯誤訊息」),守衛本身在這個維度上是失效的。

severity: major
blocking: 是

## 發現 2:污染檢查沒有排除程式碼區塊/frontmatter,會誤報乾淨的池子

引句:「docs[str(f.relative_to(vp))] = f.read_text(encoding="utf-8", errors="replace")」

`contaminated()` 把整篇檔案(含 frontmatter、含 fenced code block)當成一個字串去比對。
但實際 `lumos search` 的「整串片語是否存在」判定,不管是主迴圈的候選比對還是多詞回退的
預檢,都是掃 `_search_visible_lines(..., include_code)`(`include_code` 預設 False),★會排除
fenced code block 與 inline code★。這支檔案自己的說明字串裡就有這種寫法示範:
`lumos search("作廢 收回 點數")` 這類「查詢字面出現在範例指令裡」的用法,在本檔開頭的
docstring 與 `scripts/lumos` 的提示訊息裡反覆出現。

我用一個最小夾具重現:一篇筆記把查詢字面「斑馬 條紋 計數」寫在一段 fenced code block 裡
當範例指令(其餘篇幅沒有這個字面),結果:

```
contaminated() 判定: [('M01', '斑馬 條紋 計數', ['Systems/A.md'])]   ← 判定「污染」
但實際兩臂:
  --no-any(整串片語) → 0 候選(片語沒出現在可見文字裡)
  --any(拆詞回退)    → 回退真的觸發,回 1 筆
兩臂結果不同,代表這篇筆記其實★沒有★造成兩臂量出一樣的數字——不是真污染。
```

`--rebuild-pool` 碰到污染會直接 `return 2` 擋下、不寫出檔案(見主程式 `if a.rebuild_pool:
... return 2` 那段)。這代表只要有人把查詢字面寫進範例程式碼區塊(這支工具自己的文件慣例
就是這樣寫查詢範例),重組候選池就會被誤判擋下,即使實際評測機制完全沒受影響。方向雖然是
「寧可誤擋不要漏放」,但誤擋的成本不小——目前這支工具唯一產生候選池的入口就是
`--rebuild-pool`,被誤擋就是做不了事,而且訊息只會說「出現在 Systems/A.md」,不會說明
是在程式碼區塊裡而非正文,不容易判斷是真污染還是誤報。

severity: major
blocking: 是

## 發現 3:「未裁決不當 0 分」的承諾,到了算分那一段其實沒有實現

引句:「未裁決:當成沒標,不當 0 分」

`load_labels()` 把 `final` 是 `None`(未裁決)的節點直接從字典裡剔除,註解明講「不當 0 分」。
但下游唯一消費這份字典的地方——`main()` 的評分迴圈——一律用 `gold.get(x, 0)` 取值:

```
base_lab = [gold.get(x, 0) for x in base]
fb_lab = [gold.get(x, 0) for x in fb]
...
"top1_label": (gold.get(fb[0], 0) if fb else None),
```

`.get(x, 0)` 沒辦法分辨「這個節點根本不在字典裡因為還沒判」跟「這個節點在字典裡、分數就是
0(判過、不相干)」——兩者都回傳 0。我實測過三種輸入的下游結果:

```
A.md: final=None(未裁決)     → gold.get('A.md', 0) = 0
B.md: final=0(判過,不相干)   → gold.get('B.md', 0) = 0
C.md: 從沒出現在標註檔裡       → gold.get('C.md', 0) = 0
```

三者在算 nDCG/MRR/precision、以及印「top1=0 ★」那一行時完全等價。也就是說,如果拆詞回退
的第一名剛好是一個★還沒被任何人判過★的候選,工具會直接印出「★」標成「第一名不相干」——
但事實是根本沒人判過,不是判定不相干。這跟這次改動自己在同一份 diff 加的另一句提醒
(「也可能是這些候選根本還沒標過——標註如果比語料舊,沒標的一律當 0 分」)講的是同一件事,
代表作者其實知道「沒標=當 0 分」這個限制依然存在,只是 `load_labels()` 的註解與實際行為
不一致,把一個沒有實際效果的區分寫成好像已經解決了。

severity: major
blocking: 是

## 發現 4:污染檢查只在 `--rebuild-pool` 才擋下,量測路徑(這支工具的主要跑法)碰到污染照樣往下跑

引句:「★重組候選池時不接受污染★:改乾淨再跑一次。」

`main()` 的順序是:先跑 `contaminated()`,有污染就印 stderr 警告;只有 `a.rebuild_pool`
為真時才 `return 2` 擋下。若是走這支工具原本的主要用途——量測(`--labels` 那條路,見檔案
開頭 docstring 寫的跑法示範,沒有帶 `--rebuild-pool`)——碰到污染一樣只印 stderr 那幾行,
接下來照樣 `load_labels()`、照樣把該題的候選拿去算 nDCG/MRR/precision、照樣併進
`mac()` 算出來的「整體」平均分數印到 stdout,不會中止也不會把那一題排除在整體統計外。

這正好是這支工具的 docstring 一開頭描述的核心危險場景(「兩臂結果一模一樣、測不到任何東西,
而且不會有任何錯誤訊息」)——這次的修法只補了「重組池子時擋下」,但沒有補「量測時是不是還
在默默吃進被污染的分數」。如果量測是排程或別的腳本呼叫、只看退出碼或只轉存 stdout(這支
工具目前 `main()` 對污染案例仍然 `return 0`),污染題目造成的假數字依然會混進整體結果,
跟修法動機描述的失效模式一模一樣,只是換了一個入口沒補到。

severity: major
blocking: 是

## 發現 5(次要):`cooccur_top` 對空字串查詢會直接 crash

引句:「if all(cs): sc[k] = min(cs)」

`cooccur_top(terms)` 裡 `cs = [v.count(t) for t in terms]`;如果 `terms` 是空 list(查詢欄位
是空字串或全空白,`q.split()` 會回 `[]`),`all([])` 在 Python 裡是 `True`(空序列的
all 恆真),於是會執行 `min([])`,實測直接丟 `ValueError: min() iterable argument is empty`。
機率低(要題庫裡有一題 `query` 是空字串或全空白),但一旦發生會讓 `--rebuild-pool` 整個
不可用的方式崩潰,而不是給出「這一題查詢是空的」這種看得懂的訊息。

severity: minor
blocking: 否

## 發現 6(次要):`main()` 裡的迴圈變數 `n` 遮蔽了 `mac()` 用到的同名變數 `n = len(rows)`

引句:「for cid, n in zero:」

`main()` 一開始 `n = len(rows)`,`mac(key)` 這個 closure 用的就是這個 `n` 當分母。這次改動
在後面新增的 `for cid, n in zero:` 迴圈,會把同一個函式作用域裡的 `n` 覆蓋成「候選數
(`fb_n`)」。目前程式碼裡所有 `mac(...)` 呼叫都寫在這個迴圈之前,所以現在還沒有實際印錯
數字。但這是一個脆弱點:往後只要有人在這段迴圈之後再加一次 `mac(...)` 呼叫(例如加一行
新的整體統計),分母就會悄悄變成「最後一題污染候選數」而不是「總題數」,而且不會有任何錯誤
訊息——正是這批改動一直在強調要避免的那種靜默錯誤。

severity: minor
blocking: 否
