# about-code-impl-std r2(即 std-r1)架構對齊審查

審查範圍:`/tmp/about-code-impl-std-r2.md` 只審標「std-r1」的 delta——「過期守衛」節末的 std-r1 改寫段(新 helper
`git_last_change_info`、`git_dirty_notes`、懶觸發)、「#4」(`_impact_about_counts` 頂層函式、快取鍵、排序鍵、只在
True 出鍵)、「#6」(複用 `run_doctor` 的 `repo_root`、略過句式)、「#10」接線。

判準:只判「跟本專案既有做法一不一致」,不判 bug、不判風格。major = 引入第二種做法或跨層直呼;minor = 命名/錯誤
處理不一致但結構對。

---

## Q1:分層依賴——有沒有跨層直呼、繞過既有邊界?

**結論:沒發現不對齊。**

- `git_last_change_info`/`git_dirty_notes` 維持模組層級自由函式的形狀,跟既有的 `git_last_change_dates`
  (`scripts/lumos:13564`)、`_impact_contract`(`scripts/lumos:13681`)同一層級——被 `cmd_impact` 和新的
  doctor 迴圈兩邊呼叫,是「共用工具函式」而不是「一邊伸手進另一邊的內部」。這正是 `_impact_contract` 已經在
  incident/direct/indirect 三條路徑之間共用的既有模式,沒有引入新的耦合形狀。
- `#6` 明講複用 `run_doctor` 內建立的區域變數 `repo_root`(`scripts/lumos:682-685`,Check C 掃 `env.vault.parents`
  找 `docs` 取其上層),而不是自己重找。這件事本身值得多看一眼:本專案目前其實已經有三種找 repo_root 的寫法
  ——(a) Check C 這段內嵌邏輯、(b) `_repo_root_from_env(env)`(`scripts/lumos:5154-5158`,邏輯與 (a) 完全相同,
  只是切成函式,被 `scripts/lumos:1327`/`2793`/`5212`/`5330`/`5691`/`5985` 呼叫)、(c) `_anchor_repo_root(repo)`
  (`scripts/lumos:9695-9706`,cwd 向上找 `.git`,`--repo` 顯式優先)、以及 `cmd_impact` 自己內嵌的第四份 (c) 的
  重複實作(`scripts/lumos:14006-14016`,沒有呼叫 `_anchor_repo_root`)。spec 選擇直接複用 `run_doctor` 本地
  變數(等價於呼叫 (b)),沒有再加第五種——這是四種既有寫法裡最貼合語境的一種,不算引入新做法,是對既有分裂
  情況的正確收斂,不列為不對齊。
- `#10` 的接線(row → `_macro()`(`governance/eval/retrieval_eval.py:266-268`) → `verdict["pin_top3_must"]`
  → `_history_record` 的 `"verdicts": {r["split"]: r["verdict"] for r in reports}`,約在
  `governance/eval/retrieval_eval.py:499`)完全沿用 `must_pinned_count`(`:410`)已經在走的既有管線,`gates`
  字典(`:570-575`)明確不加——沒有另開一條路徑把新指標送進 gate 或 history。
- hook(`scripts/hooks/claude/impact-hook.py`)與 eval(`governance/eval/retrieval_eval.py`)都是用
  `subprocess.run([sys.executable, str(LUMOS), ...])` 呼叫 CLI、吃 JSON(`governance/eval/retrieval_eval.py:15/23/95/130`;
  `scripts/hooks/claude/impact-hook.py` 同款),不是 import `scripts/lumos` 直接呼叫內部函式。「hook/CLI/eval
  共用單一實作」這句話因此自動成立(三邊本來就只透過 CLI 的 JSON 輸出交換資料),不需要、也沒有要求 hook/eval
  反過來 import `_impact_about_counts`,沒有破壞既有的 process 邊界。

## Q2:命名與錯誤處理——命名、fail-open/fail-closed、編碼處理跟既有慣例一不一致?

**結論:1 條不對齊(major)。**

對齊的部分:
- `git_last_change_info`、`git_dirty_notes` 命名沿用 `git_last_change_dates` 那個「`git_` 前綴、無底線、
  動詞省略」的家族(`scripts/lumos:13564`),`_impact_about_counts` 沿用 `_impact_*` 私有函式家族命名
  (`_impact_reverse_lookup` `:13605`、`_impact_contract` `:13681`、`_impact_bfs` `:13719`)。
- 「git 缺席 → about_code 視同不存在」跟既有 fail-open 慣例一致:`git_last_change_dates` 本身在
  `except (OSError, subprocess.SubprocessError): out = {}`(`scripts/lumos:13595-13598`)已經是同款寫法,
  Check P/Y/N 對 `repo_root is None` 也一律走 `ok("(...跳過)")`(`scripts/lumos:1124-1125`、`1196-1197`、
  `1259-1260`)而不是報錯。
- `#6` 訊息格式比照 Check S 既有的 `sa_stale` 逐行寫法 `f"{rel} (self_audit {sa_date} < updated {upd})"`
  (`scripts/lumos:823`)——新訊息 `f"{rel} (about_code_stamp {stamp_date} < git 最後改動 {git_date}...)"`
  是同一個「`<欄位> <值> < <對照物> <值>>`」形狀,`warn_soft` 本身是 `run_doctor` 內的巢狀 closure
  (`scripts/lumos:486-497`,不動 `issues`、不影響 rc),`#6` 描述的「warn_soft(不擋、不計 issues)」跟這個
  既有定義完全一致。

**不對齊(major):`git_dirty_notes` 的 `git status --porcelain` 呼叫沒有比照既有慣例帶
`-c core.quotepath=false`。**

`git_last_change_dates`(`scripts/lumos:13564-13599`)在同一份 spec 的同一節裡,對 `git log` 呼叫明文帶
`-c core.quotepath=false`(`scripts/lumos:13582-13583`),docstring 自己解釋原因:「vault 檔名幾乎全中文,
預設輸出是八進位跳脫……沒這旗標整張表是空的,而且不報錯」。`scripts/test_lumos.py:579-625` 的
`t_git_last_change_dates_batch` 甚至專門翻紅釘驗過這件事(「①拿掉 quotepath 旗標 → 第 2 條翻紅」)。
`scripts/lumos:12617-12619` 的 `_testmap_git` 是本專案第二個獨立先例:它把 `-c core.quotePath=false` 焊進
「每一次」git 呼叫,正是因為 `scripts/lumos:12908-12912` 要逐行 parse `status --porcelain` 輸出裡的路徑。

但 delta 描述 `git_dirty_notes` 時只寫:

引句:「再一次批次 `git status --porcelain -- <vault>` 抓沒 commit 的:`git_dirty_notes(repo_root, vault)` 回 set,同款行程內快取。」

沒有提到 quotepath。我用一個本地建的中文檔名 repo 實測:`git status --porcelain` 預設輸出把
`docs/中文目錄/測試筆記.md` 印成 `"docs/\344\270\255\346\226\207\347\233\256\351\214\204/\346\270\254...`
(帶引號的八進位跳脫),`-c core.quotepath=false` 才印回可讀路徑——跟 `git_last_change_dates` docstring 講的
是同一個坑。vault 筆記幾乎全中文,若這個新 helper 真的照字面只跑 `git status --porcelain -- <vault>`,parse
出來的路徑會是亂碼、幾乎永遠對不上任何 `rel`,`dirty set` 會形同空集——而「筆記改了還沒 commit,git log
看不到」正是這一整節開頭點名要防的偽陰性方向。這不是風格問題,是把本節自己剛驗證過、剛寫進 docstring 的
編碼安全措施,在下一個 helper 上悄悄漏掉,形成「同一份 git 輸出 parsing 需求,兩種編碼處理方式」的第二種
做法。

## Q3:第二種做法——有沒有跟既有機制並存的平行實作?

**結論:1 條 ⚠(判不準,交編排者)。**

對齊的部分:
- 排序鍵 `(kind != "incident", not about_hit)` 不是新發明的寫法——`scripts/lumos:11893`/`11908`/`11916`
  三處既有 `hits.sort(key=lambda h: (h["conf"] != "high", h["folder"] != "Systems", h["node"], h["line_no"]))`
  就是同一個「布林取反 tuple key」idiom,而且是 `.sort()` in-place(不是 `sorted()`),跟 `all_direct.sort`
  (`:14116`)、`all_indirect.sort`(`:14117`)、`free.sort`(`:14246`)、`dropped.sort`(`:14276`)、
  `sa_missing.sort`/`sa_stale.sort`(`:849-850`)是同一套慣例。`pins = [...]` 目前落在 `scripts/lumos:14241`
  附近(spec 標的 `:14226` 是舊行號,spec 自己在別處已承認「舊行號整批過期」,不算架構問題)。
- `about_hit: True` 只在 True 時出鍵,不是孤例做法:`results.append` 的 `rescued`(`scripts/lumos:14279`,
  只在補救時才加這個鍵)、`out_obj["query_gated"] = True`(`:14288-14289`,只在 gated 時才加)、以及
  `all_indirect.append` 裡 core_refs 葉那條路徑才帶 `cross_repo`/`no_expand`(`:14087-14088`)而 BFS 那條路徑
  完全不帶這兩個鍵(`:14104` 附近)——本專案本來就有「同一個 results 項目,不同來源路徑帶不同鍵集合、消費端
  用 `.get()` 讀」的既有慣例(`scripts/hooks/claude/impact-hook.py:339-358` 全部走 `.get()`)。`about_hit`
  選這個既有形狀,是對的選擇,不是第二種做法。
- `_impact_about_counts(env)` 切成獨立頂層函式、不 inline 進 `cmd_impact`,對齊
  `_impact_reverse_lookup`/`_impact_contract`/`_impact_bfs` 的既有分工;快取鍵 `str(env.vault)` 跟
  `_BASENAME_COUNTS_CACHE`(`scripts/lumos:13602`,鍵 `str(repo_root)`)是同一種「路徑字串當鍵」的形狀,
  明確駁回 `id(env)`(spec 自己講的理由——`id` 回收後可能撞、全庫沒先例)也是對的判斷。這兩點都不算不對齊。
- `#6`「不併入 Check S、另開迴圈但同輸出格式」表面上看是「多一套機制」,但實際落地是在同一個 `run_doctor`
  函式體內再加一個 `section(...)` 區塊(跟 Check C/D/M/P/Y/N/S 是同一種寫法:每個 Check 都是
  `run_doctor` 內一段 `for rel, n in sorted(notes.items()): ...` + `ok`/`warn_soft`),不是另立一支新的
  doctor 或新的 CLI 子指令——結構上仍是「一個 doctor,裡面多一段既有形狀的 Check」,不是第二個 doctor。

**⚠ 判不準的一條:`git_last_change_dates` 改成 `git_last_change_info` 的薄包裝後,快取有沒有可能變成兩顆。**

引句:「`git_last_change_dates` 改成它的薄包裝(回傳型別不變,既有測試不動)。」

本專案目前每個「批次 git 查詢」概念只留一顆行程內快取字典(`_GIT_DATES_CACHE` 對應 `git log`、
`_BASENAME_COUNTS_CACHE`(`scripts/lumos:13602`)對應 `git ls-files`)。spec 沒有明講「薄包裝」之後,真正
呼叫 git 並做快取的是不是仍然是 `_GIT_DATES_CACHE` 本體(只是把值形狀從 `date` 換成 `(date, n_same_day)`)
——如果實作時另開一顆新字典給 `git_last_change_info`,讓 `_GIT_DATES_CACHE` 變成只是 wrapper 內部一個
不再被真正查詢路徑用到的舊殼,就是同一份 git log 結果被兩顆快取分別記一次,是本專案「一個概念一顆快取」
慣例的第二種做法。而且會直接打中 `scripts/test_lumos.py:579-625` 的
`t_git_last_change_dates_batch`——它在第 616 行 `m._GIT_DATES_CACHE.clear()` 之後,靠假 `git` shim 數
「冷呼叫幾次」（第 619-620 行,斷言 `n == 1`）；如果實際擋住 subprocess 呼叫的快取換了名字,`.clear()`
清的就不是真正生效的那顆,這個斷言的前提會悄悄失真,跟 spec 自己講的「既有測試不動」正面衝突。

因為 spec 沒有寫到「快取變量是哪一顆」這個實作細節,無法從文字本身判定它究竟是延用同一顆(對齊)還是另開
一顆(不對齊)——標 ⚠,建議編排者在派實作審查時明確要求「`git_last_change_info` 必須複用 `_GIT_DATES_CACHE`
本體(值形狀改成 tuple),不得另開快取字典」,並確認上述既有測試仍然有效。

---

## 統計

不對齊共 2 條,其中 major 1 條(Q2 的 quotepath 缺漏);另 1 條標 ⚠(Q3 的快取是否分裂),判不準,交編排者裁決,不計入 major。
