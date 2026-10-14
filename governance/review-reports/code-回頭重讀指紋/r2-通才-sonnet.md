severity: major

我跑了 `python3.14 scripts/test_lumos.py -k reread`,367 項全過,但測試沒蓋到下面這條。

severity: major
blocking: 是 — 這次修補要堵的「同一段改動搬到同檔另一個函式、指紋不變」,在 Kotlin、Java、C、C# 等語言仍然堵不住,而本專案(Android、Java、Kotlin 技能)正是這些棧。
引句:「名字取 def/class/function/func/fn 後面那個(前面可帶 async/export/pub 這類修飾字,Go 的方法接收者跳過),都沒有就取第一個識別字」
問題:`_NOTE_REREAD_DEF_RE` 只認 def、class、function、func、fn,沒有 Kotlin 的 `fun`,也不認 Java、C#、C 這類「回傳型別加名稱」的寫法。頂格行沒比中關鍵字時,退而取該行第一個識別字,結果是 `fun`、`int` 這種共通字。縮排的方法行同樣比不中,所以類別內的各個方法也沒有「/方法名」的分辨。
具體失敗情境:我直接呼叫 `_note_reread_hunk_tags` 實測,輸入是兩個前後三行完全相同的函式,作者把 `check(u)` 的改動從公開端點搬到管理員端點。
- Kotlin(`fun publicEndpoint`、`fun adminEndpoint`):兩個 hunk 的標籤都是 `fun`。
- Java(同一個 `public class Api` 裡的 `pub` 與 `admin`):標籤都是 `Api`。
- C(`int pub`、`int admin`):標籤都是 `int`。
- 因此逐檔指紋相同,舊的「已看過」紀錄會替搬過去的改動背書,資安席 r1 的 major 在這些語言重現。Python 與 Go 不受影響。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:_NOTE_REREAD_DEF_RE 與 _note_reread_hunk_tags`

severity: minor
blocking: 否 — 只會多叫人重判(誤擋方向),不會漏判。
引句:「都沒有就取第一個識別字——★參數與簽名不算★:主線改了函式的參數列,作者的改動一字未變,名字不變」
問題:hunk 前一個頂格行如果是模組層的賦值、常數、YAML 或 shell 行,標籤就是那一行的第一個識別字,不是函式名。主線只要在 hunk 前插一行頂格內容,作者一字未改的改動也會換指紋。
具體失敗情境:實測 `A=1 B=2 C=3 D=4 E=5` 的 hunk 標籤是 `B`;主線在 B 與 C 之間插入 `NEW=9` 後,同一段改動的標籤變成 `NEW`。這正是 v2 要擋掉的「主線前進就失效」。程式本體的函式內改動不受影響。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:_note_reread_hunk_tags`

severity: minor
blocking: 否 — 預算不足時才發生,清單上有講明原因。
引句:「判定者材料被縮短" if len(d) > _NOTE_REREAD_DIFF_CAP else None」
問題:`_note_reread_fp_info` 現在對每篇候選多跑一次 `git diff`(`_note_reread_v2_cut`)。check 有 30 秒上限而 prepare 沒有,候選多的時候 check 較容易中途逾時,改用 v1。
具體失敗情境:prepare 已經記了 v2 紀錄,check 卻對這些篇用 v1 比對,比不到,於是被當成「沒有紀錄」而硬擋(`hard`)。輸出會多印逾時說明,但使用者要再跑一次才過。

已讀,無 finding:
- `_nodehome_cat_blobs_capped` 改用 `_git_timeout(deadline, cap=timeout)`,語意與原本的 `min(timeout, deadline-now)` 完全相同,節點認家那條路沒變。
- `_patch_file_changes` 的三個既有呼叫者(資安席用的),預設路徑與原本逐字等價。
- v1 指紋(`_note_reread_contrast_fp`)沒動,v1 舊紀錄仍先比對。這條分支沒有新增或改寫過任何 v2 紀錄檔。
- `_note_reread_git` 在 linked worktree 的 git 目錄加 `--bare` 實測可用。
- `_note_reread_fp_sizes` 與 `_note_reread_tip_names` 的簽名變動,呼叫端都已同步。

最高等級 major,blocking 共 1 條。
