severity: major

## 第1問:分層與依賴方向

第1問 對齊。`_ns_git`(scripts/lumos:23529)只包一層 `_lens_git`,`_ns_mainline_refs`(scripts/lumos:23543)只呼叫 `_lens_git`/`_lens_full_sha`,`_ns_regions` 改呼叫全庫共用的 `split_frontmatter`/`TOP_KEY_RE`(低層工具被高層 gate 呼叫,方向沒反),喚醒段改呼叫既有的 `_nodehome_cat_blobs` 批次讀(scripts/lumos:22784)而不是自己另開 git 行程——這正是本輪代碼審把「另開 git grep 再手拆輸出」的跨層直呼折掉、改回既有分層的結果。沒發現新的跨層直呼。
對照:scripts/lumos:22784(`_nodehome_cat_blobs` 定義)、scripts/lumos:23543(`_ns_mainline_refs` 只呼叫底層 git 包裝)。

## 第2問:命名與錯誤處理

第2問 對齊。新函式一律掛 `_ns_` 前綴,跟既有 `_nodehome_`/`_lens_` 家族並列,不撞名。錯誤處理沿用同一種「回 None 就代表失敗」慣例:`_ns_git` 判 `r is None or r.returncode != 0` 回 `None`,跟 `_nodehome_git`(scripts/lumos:22468)逐字同款;`_ns_mainline_refs` 對每個 `_lens_git` 呼叫也都先判 `is not None and returncode == 0` 才取值,跟鄰居寫法一致。doctor 讀設定檔那段(判資料夾捷徑)雖然是另外手刻一次判斷式而不是呼叫 `_nodehome_config`,但這正是本 repo `_nodehome_config`/`_note_lint_config` 兩處已經在用的「同一段防呆各閘自己刻一份」的既有慣例,不算新分歧,純風格差異不列。
對照:scripts/lumos:22468(`_nodehome_git`)、scripts/lumos:5124(`_note_lint_config` 同款防呆已是先例)。

## 第3問:第二種做法

### F1 `_ns_mainline_refs` 是跟既有 `_mainline_ref` 平行的第二套「主線」判法
severity: major
blocking: 是 —— 本 repo 已有 `_mainline_ref`(scripts/lumos:28026)作為「主線 tip」的單一權威判法(本地 main/master 的 upstream 優先,查不到才退本地分支),且已被 `_bound_tests_range`、`_codeloop_guard_verdict` 等至少三處呼叫共用;`_ns_mainline_refs` 完全不呼叫它,另外寫一套「列舉每個遠端、讀 `refs/remotes/<遠端>/HEAD`、查不到再猜 main/master」的獨立演算法。兩套「什麼算主線」的判準各自維護,以後若主線分支改名或 remote 慣例調整,很容易只改到一邊——這正是本計劃自己在 PRIOR-ART 段強調「照名字借,多半借不動」要逐項講清楚借法的那種風險,但這一支新函式完全沒被 PRIOR-ART 段點名討論,也沒有註解交代為什麼不能延伸既有的 `_mainline_ref`。
引句:「各遠端的預設分支參照(refs/remotes/<遠端>/HEAD 指到的那條,沒有就 main、master)。」
佐證 file: scripts/lumos:23544(新函式的 docstring);對照 scripts/lumos:28026(既有 `_mainline_ref` 定義)、scripts/lumos:29767(既有函式的既有呼叫點之一)。

### F2 `_NS_SRC_MARK_RE` 是跟既有 `SRC_REF_RE` 重複的第二支 `[src:…]` 正則
severity: major
blocking: 是 —— 本 repo 已有 `SRC_REF_RE = re.compile(r"\[src:\s*([^\]]+?)(?::(\d+(?:-\d+)?))?\s*\]")`(scripts/lumos:4283),用在 regen 出處驗證(Check J)與 `_refcheck_scan` 共用,匹配的正是同一種 `[src:…]` 標記語法。這裡的用途只是「把整段標記挖掉再掃剩下的文字」,`SRC_REF_RE.sub(" ", text)` 直接就能做到同樣的事,不需要另開一支只差在「不留捕獲群組、字元類寫成 `[^\]]*` 而非 `[^\]]+?`」的近似正則。兩支正則以後若 `[src:]` 語法變動(例如允許逗號、允許巢狀括號),很容易只改到 Check J 那邊而漏掉這一支,造成筆記形狀擋認不出新語法的 `[src:]` 標記,把它誤判成裸碼引用去擋。
引句:「_NS_SRC_MARK_RE = re.compile(r"\[src:[^\]]*\]")」
佐證 file: scripts/lumos:23626;對照 scripts/lumos:4283(既有 `SRC_REF_RE` 定義)、scripts/lumos:4614(既有用法:`for m in SRC_REF_RE.finditer(line)`)。

（`_NS_POINTER_ONLY_RE` 另外查過:本 repo 目前只有 `_SINGLE_WIKILINK_RE`(scripts/lumos:205,判「整個值恰好一個連結」)與到處內嵌的 `\[\[…\]\]` 片段,沒有「一整行只有連結與指路詞、允許多個連結」這種既有正則,而且內嵌 `\[\[[^\]]+\]\]` 片段本身也是本 repo 到處直接手寫、不透過 `WIKILINK_RE` 組字串的既有寫法——這支算新增功能、寫法也對齊既有慣例，不算第二種做法。`_ns_git` 對既有 `_lens_git` 的 `quote` 參數是直接沿用,不是重刻,也不算違規。）

不對齊共 2 條,其中 major 2 條
