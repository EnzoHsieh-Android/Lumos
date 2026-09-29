severity: major

# 乙代碼審 r2 正確性席(opus)

重現腳本都在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/cy2/probeGczS/`(h.py 是共用載入器,in-process 載 clone-ns 的 scripts/lumos、不寫 bytecode;t1–t7 各一個情境;git 只動該目錄底下自建的 repo)。

## F1 判定變寬了,候選篩選沒跟著變:加 #! 或拿掉包住定義的三引號時,條件翻成立卻不列
severity: major
blocking: 是 — 推送讓條件從不成立變成立卻判成「不是候選、不評估」,推送閘的核心承諾漏掉,而且可以重現
引句:「shape = any(c in ("A", "D", "R", "C") and _drift_probe_code_path(p) for p, c in codes.items())」

1. 規格第 0 節寫「不是候選的行,起點與終點結果一定一樣,不評估」。這份差異把判定改寬了兩處:語料收沒副檔名、開頭是 `#!` 的檔(`corpus` 看內容開頭);Python 改用 ast,字串或 docstring 裡的 def 不算。這兩處都讓「定義在不在」可以在名稱那一行完全沒動的情況下翻轉。可是候選篩選還是舊的兩條路:名稱出現在新增行(`added_text`),或程式檔有 A/D/R/C。兩條都抓不到這兩種翻轉。
   file: `scripts/lumos:26035`
2. 情境甲(t2.py 前半):`src/api.py` 在起點是 `X = 1` / `'''` / `def new_api():` / `    return 1` / `'''`,筆記有 `REVISIT:[when-symbol:new_api][by:2099-12-31] …`。推送只刪掉兩行 `'''`(diff 只有 `-` 行)。實測輸出:
   `base judged: False  tip judged: True`
   `changes: {'renames': {}, 'added_text': '', 'code_shape': False}`
   `check: ([], [], [])`
   起點不成立、終點成立,check 什麼都沒列。
3. 情境乙(t2.py 後半):`bin/tool` 起點內容是 `def MAX_X():…`,沒有 `#!`(不在語料裡)。推送只在第一行加上 `#!/usr/bin/env python3`,檔案狀態是 M。實測輸出:`T3 base judged: False  tip judged: True`、`T3 check: ([], [], [])`。repo 裡已經有同一種判斷:`_ns_became_code` 的說明就寫「加 #!、類型改變都算」,這裡沒有借來用。
   file: `scripts/lumos:24243`
4. 兩個情境 scan 都會列出(終點成立),`[by:]` 到期時 E5 也會唸,所以不是永遠漏掉;漏的是推送當下那一次該處理的提醒。⚠ 發生頻率低(要剛好用「刪行」或「加 #!」讓定義出現),但這個形狀是這次修正帶進來的,上一版用逐行正則加「只收有副檔名的檔」時不會發生。

## F2 路徑先用原文驗、之後才正規化:`..\x.py` 過得了第一層,check 與 scan 卻都不看也不列
severity: minor
blocking: 否 — 條件永遠不會被判,但原本(不正規化)一樣永遠不成立,不是新的漏擋;問題在三處的判法彼此不一致
引句:「conds.append((k, val if err else _probe_norm_value(k, val)))」

1. `_probe_parse` 用原文跑 `_probe_value_err`,原文 `..\x.py` 用 `/` 切不出 `..` 段,所以算合法;接著 `_posix_norm` 把反斜線轉成斜線,存進去的值變成 `../x.py`。`\etc\x.py` 會變成 `/etc/x.py`,`..\a.py::f` 會變成 `../a.py::f`,情形一樣。
   file: `scripts/lumos:25787`
2. t1.py 的實測結果:第一層 `_ns_revisit_violations` 回 `[]`,放行;`_probe_parse` 的 errs 是空的。可是拿正規化後的值再跑一次 `_probe_value_err`,就回「不准 / 開頭、不准 .. 段」。
3. check 在 `scripts/lumos:26052` 用正規化後的值過濾,整行被默默丟掉。scan 在 `scripts/lumos:26146` 跳過問題判定、在 `scripts/lumos:26172` 跳過評估,而 `pr["errs"]` 是空的,所以這一行既不在「回頭條件的問題」裡,也不在發現裡。實測:`scan: ([], [])`、`check from empty: ([], [], [])`。doctor Z 段用 `pr["errs"]` 計數,也把它算成正常的一條。
4. 規格第 2 節第 4 點要第一層擋「形狀不合文法」,第 3 點要 scan 列「寫錯的條件」,這一行兩邊都沒做到。

## F3 第③項改成「看舊狀態」之後,exam 的 status_replay 算出來的連帶待辦跟 lumos set 不一樣
severity: minor
blocking: 否 — 現有考卷的 E1/E2 考的是 Issue,不經過第③項,分數不受影響
引句:「and new_status in (vals := {x.strip() for x in v.partition("=")[2].split("|")}) and old not in vals]」

1. `_drift_status_probe_followups` 現在假設 env 是「改之前」的圖譜(說明裡明寫)。`_drift_exam_replay` 卻先把 targets 改成 done、放進 override,再呼叫 `_drift_plan_followups(tenv, prel, "done")`。這時 old 已經是 done,`old not in vals` 永遠是假,所以第③項在重放裡一律不列。
   file: `scripts/lumos:26626`
2. t4.py 的實測結果:計劃 `Projects/P` 狀態 doing,Issue 裡有 `REVISIT:[when-status:Projects/P=done][by:2099-12-31] …`。用改之前的 env 算(就是 `lumos set` 那條路)會列 `('回頭條件', 'Issues/N.md', '第 9 行的 status 條件因這次收尾成立')`;`_drift_exam_replay(r, par, V, ["Projects/P"])` 回 `set()`。
3. 規格第 3 節說 status_replay 要「算 lumos set 會列的連帶待辦」。這份差異讓重放跟 set 在第③項上分叉;以後考卷只要有一題 status_replay 的題目行是 status 條件,就一定判成漏。

## F4 帶 BOM 的 Python 檔 ast 解析失敗、退回正則,docstring 裡的範例 def 又被當成定義
severity: minor
blocking: 否 — 只影響帶 BOM 的檔,結果退回上一版的行為(正則),不會比上一版更差
引句:「self._text[p] = None if b is None else b.decode("utf-8", errors="replace")」

1. 讀樹與讀磁碟都用 `utf-8` 解碼(`scripts/lumos:25920`、`scripts/lumos:25909`),BOM 會留在字串開頭。在 python3.9(`/usr/bin/python3` 3.9.6)上,`ast.parse("﻿def f(): pass")` 會丟 `SyntaxError invalid non-printable character U+FEFF`,於是退回 `_drift_py_def_re`。
2. t7.py 的實測結果:`src/b.py` 帶 BOM,docstring 裡有 `def ghost():`,判成 `True`;內容相同、沒 BOM 的 `src/c.py` 裡的 `ghost2` 判成 `False`。這正是這次改用 ast 要修的那個坑(說明裡的「推送只加了文件範例就誤擋」),在 BOM 檔上沒修到。筆記讀取器全庫都用 `utf-8-sig`,這裡沒跟上。
3. 同一個原因:沒副檔名、帶 BOM 的腳本,`self._text[p].startswith("#!")` 是假,整支不進語料。

## F5 drift check 的表態提示在兩種都有時印成 `--kind c1|probe`,照貼會變成管線
severity: minor
blocking: 否 — 只是提示文字,不影響判定
引句:「+ ("|".join(sorted(kinds)) if len(kinds) > 1 else next(iter(kinds)))」

1. t6.py 的實測結果:must 同時有 c1 和 probe 時,印出的指令行是 `    lumos drift ack <節點> <行號> --kind c1|probe --reason "<為什麼照留>"`。這一行單獨成行、長得像可以直接貼的指令;照貼時 shell 會把 `|` 當成管線,跑成 `lumos drift ack … --kind c1` 接到一個叫 `probe` 的指令,argparse 那邊則是缺 `--reason`。
   file: `scripts/lumos:26376`
2. 上一版印的是 `<種類>` 佔位字,一看就知道要換掉;這版在只有一種時印真值、兩種時印成看起來像真值的寫法,兩種情況長得不一樣。

## 其他檢查過、無 finding 的部分

- ast 判定對規格第 2 節:已看,無 finding。def、async def、class 在任何層都算(含方法、巢狀函式);指定只算模組層的 `Assign` 與有值的 `AnnAssign`;test 只看函式。解析失敗時接住 `SyntaxError`/`ValueError` 再退回正則,跟上一版的正則同一支。python3.9 上串接十萬項的運算式也不會丟 RecursionError(實測)。
- 路徑正規化與「同一條」:已看,無 finding(F2 那種會變成非法值的除外)。起點的舊行也經過 `_probe_lines` → `_probe_parse`,所以一樣正規化過;候選篩選拿的 `touched` 是 NFC,跟正規化後的路徑對得上。
- `_drift_probe_check` 拆成 old/prepare/judge 三支:已看,無 finding。沒有起點時 old 是 None,一律當新寫的;判不了時照樣進 unknown;預算用完時訊息改成「超過預算」,筆數不變。唯一的行為差異是 status 條件在列不出樹時也判得了,這是規格要的。改名對照改用整庫一次 `-M`,對應方向跟上一版一樣(新→舊、NFC)。
- `_notelines_new` 拆出 `_notelines_range_cand`/`_notelines_rows`:已看,無 finding。keep_other=False 時 net 是 None,逐行條件跟上一版一字不差。keep_other=True 時,淨差異行號只拿來多排除「other」區的行(條件是 AND),不會多收;只多一種失敗情況:淨差異那次 diff 失敗時整支回 None。
- E5 改成餵 `_strip_inline_markup` 剝過的版本:已看,無 finding。現在三處的輸入一致;未閉合反引號截掉的只會是日期後面的摘要,不影響「是不是 REVISIT」的判定與日期解析。
- exam 驗改寫檔:已看,無 finding。回 None 時呼叫端回 2;現有改寫檔 5 題都帶 `[by:]`,會通過。
- `_drift_list` 的記憶:已看,無 finding。只記 40 字提交編號(內容固定),呼叫端不會改到回傳的物件。

總結:最嚴重是 major,會擋的共 1 條(F1),另有 4 條 minor。
