severity: major

第三輪「邊界可執行」席。我只看第二輪折入後新寫或改寫的內容,實驗用的臨時目錄已刪,reread-fp 工作樹沒有改動。

**git 邊界實測結果**
- `--literal-pathspecs` 加 `--` 分隔可用。含 `[`、`*`、開頭 `-` 的檔名都能抓到,`:(literal)` 前綴確實讓輸出變空。
- `--raw` 單帶 `--full-index` 仍是縮寫物件編號,要 `--no-abbrev` 才完整,計劃這兩處寫對了。
- `-c` 全域選項放在 `diff` 之前、`-C` 之後,可正常執行。
- 「分岔點的樹裡沒有那支紀錄檔」最便宜的查法,是對分岔點呼叫現成的 `_note_reread_tip_names(root, base)` 一次。它就是一次 `ls-tree --name-only`,本 repo 61 份紀錄只要 0.03 秒,不必逐檔 `cat-file -e`。
- 計劃沒寫這次 `ls-tree` 失敗時怎麼辦,建議當成「不是分支自己的」,也就是只認 `v1`。

---
severity: major
blocking: 是 — 「內容同時記 `contrast_fp_v1`」的資料來源沒有交代,照字面實作不出來,實作者只能猜怎麼補。
引句:「這樣分支本機快轉進 main 再推 main(分岔點等於頂端、只算」
問題:`reread-record` 只讀項目檔檔頭與報告,不重算指紋。檔頭欄位表 `_NOTE_REREAD_HEAD` 現在只有一個「對照指紋」,`_note_reread_parse_item` 又要求所有欄位都在,缺一個整份拒收。要寫出 `contrast_fp_v1`,項目檔檔頭得新增一個 v1 指紋欄位。這欄位必須是可有可無的,否則升級前已派工、升級後才記的項目檔會被拒收。計劃沒提這件事。
另外,S12 後半「只有 `v2` 紀錄、改用 `v1` 判不應被當成已對照」跟新規則衝突:帶 `contrast_fp_v1` 的 v2 紀錄,現在 v1 判就會命中。
具體失敗情境:實作者只改紀錄內容、不改檔頭,`contrast_fp_v1` 永遠是空的,S19 的快轉路徑沒有任何東西可命中。S12 後半的測試也不知道該造有欄位還是沒欄位的紀錄。
file: `scripts/lumos:36287`(`_note_reread_parse_item`)、`scripts/lumos:36800`(`reread-record` 組 doc)、`scripts/lumos:36009`(`_NOTE_REREAD_HEAD`)

severity: major
blocking: 是 — 「分岔點只看遠端主線」跟 S4、S19 與「已知會變的情形」互相矛盾,測試寫不出來。
引句:「已知會變的情形(都是多列方向,不擋正確性):另一個工作樹把本機 main 快轉到含頂端時,分岔點變成頂端本身」
問題:傳 `include_local=False` 之後,本機 main 不再是主線候選。
- 推送前檢查時 `origin/main` 還是舊值。推本機 main(含還沒推的提交)時,分岔點是舊 `origin/main`,不是頂端,所以 `v2` 照算。
- 這跟〈做法〉5 的「推的是主線 → 分岔點就是頂端 → `v1`」不符,S4「推主線 → 指紋等於 `v1`」的 fixture 做不出來。
- S19 的「只算 `v1`」也不成立。快轉後推 main 時,分支自己的 `v2` 紀錄不在分岔點樹裡,算分支自己的,不靠 `contrast_fp_v1` 就會命中。S19 在沒有該欄位的實作下也綠,抓不到欄位漏寫。
- 「另一個工作樹把本機 main 快轉」那句是第一輪留下的過期說法。
具體失敗情境:照 S4 寫「推 main」的測試,實作出來拿到 `v2`,測試紅;改測試遷就實作,S4 守衛就失去意義。S19 無法證明 `contrast_fp_v1` 有被讀。
file: `scripts/lumos:50959`(`_codeloop_default_base` 現行把本機 main 一起收)、`scripts/lumos:47244`(`_push_mainlines`)

severity: major
blocking: 是 — 4 MB 上限直接讓 `scripts/test_lumos.py` 的所有筆記永遠退回 `v1`,計劃還宣稱最大的檔在上限內。
引句:「避免一支大檔先整份讀進記憶體」
問題:計劃只量了 `scripts/lumos`(3,214,451 位元組),漏了 `scripts/test_lumos.py`,它是 5,508,784 位元組。about_code 列了它的筆記有 9 篇(Systems/test-quality-handbook、授權與歸屬、arch-alignment-lens、測試假綠形態、Codex外審吸收_計劃等),另有 104 篇列 `scripts/lumos`。
上限看的是 blob 大小,不是 diff 輸出大小。實測一支 3 MB 檔對舊提交的 diff 只要 0.05 秒、幾 MB 輸出,不是問題。
具體失敗情境:改過 `test_lumos.py` 的分支,那 9 篇筆記一律退回 `v1`,rebase 照樣全部重派。這正是本計劃要解的問題,在最常被改的測試檔上完全不生效。S1 如果用真實檔大小的 fixture 會測不出來,因為 fixture 檔很小。`scripts/lumos` 離上限只剩約 0.8 MB,也會在幾個月內撞到。
file: `scripts/test_lumos.py`(5.5 MB)

severity: major
blocking: 是 — 傳 NFD 原樣路徑當 pathspec,在 macOS 預設設定下 diff 是空的,結果隨平台而變,S10 的預期值寫不出來。
引句:「路徑用 git 原樣路徑、前面加」
問題:實驗(用 `hash-object` 加 `update-index --cacheinfo` 造 NFD 樹):
- `core.precomposeunicode=true`(macOS 預設)時,傳 NFD 路徑,輸出 0 位元組;傳 NFC 也是 0。
- `false` 時,傳 NFD 路徑有輸出(135 位元組),傳 NFC 是 0。
- Linux 沒有這個轉換,行為等於 `false`。
全域選項清單沒有 `-c core.precomposeunicode=false`。結果是同一份樹在 macOS 上走「diff 空 → `v1`」,在 Linux 上走 `v2`,兩台機器指紋不同。
具體失敗情境:S10 在 macOS 本機要求「不被記成未改」,斷言 `v2` 會紅、斷言 `v1` 在 Linux CI 又紅。S16 後半「清單有檔、diff 卻空 → `v1`」也沒有可攜的造法。補 `-c core.precomposeunicode=false` 到全域選項,對原樣位元組路徑永遠正確,而且兩個平台一致。
file: 計劃自己測試段已寫 `-c core.precomposeunicode=false` 造 fixture,卻沒放進指紋用的全域選項。

severity: major
blocking: 是 — 「被縮短」沒定義,而且判斷與 diff 範圍互相依賴,實作者只能猜。
引句:「給判定者的 diff 因超過字數上限被縮短時,那篇改用」
問題:`_note_reread_diff` 回傳的 `trunc` 旗標有兩種觸發:上下文從 3 行縮到 1 或 0 行,或某檔超過字數被截掉並印出「[截斷:」標記。判定者在前者仍看得到所有改動行,後者才真的沒讀完。計劃沒說哪種算,第一種大分支幾乎必中,等於把大分支全退 `v1`。
另外是順序循環:`v2` 用「分岔點..頂端」的範圍,`v1` 用現在的範圍。是否縮短要先組出 `v2` 的 diff 才知道,縮短了還要回頭改組 `v1` 範圍的 diff。計劃沒寫這個順序。
具體失敗情境:兩個實作者一個把上下文縮減也算縮短、一個只算「[截斷:」,同一份 repo 算出不同的 prepare 指紋。S15 的「被縮短」fixture 也不知道該造多大。
file: `scripts/lumos:36211`(`_note_reread_diff` 回傳 `u != 3`)、`scripts/lumos:36248`(`_note_reread_item`)

severity: minor
blocking: 否 — 失敗方向是退回 `v1`,不會漏判,但會讓每個新增或刪除的檔都白退。
引句:「看清單裡那支檔兩邊的物件大小」
問題:新增檔的舊側、刪除檔的新側,物件編號是全零。`git cat-file -s 000…` 回 128,「could not get object info」;子模組(mode 160000)的編號在本 repo 查不到。實測 `cat-file --batch-check` 對全零編號輸出 `missing`。計劃沒說全零要跳過、子模組怎麼算。
具體失敗情境:實作者把非零退出碼當 git 失敗,每個 A 或 D 狀態的檔都退 `v1`。
file: 實驗輸出:`fatal: git cat-file: could not get object info`,rc=128。

severity: minor
blocking: 否 — 只多列,不漏判,但少了釘死的設定,兩台機器的指紋會不同。
引句:「diff 帶 `--full-index`;`_patch_file_changes` 本來就對」
問題:
- 〈做法〉1 的二進位那條要求 `--full-index`,可是〈選項的來源〉那條逐項列出的 diff 選項裡沒有它。照後者實作,`index` 行是縮寫,長度隨 `core.abbrev` 與物件數而變,二進位檔指紋不穩。
- 子模組:`diff.submodule=log` 時輸出變成一行「Submodule sub 1111111...2222222」,沒有 `diff --git` 頭,`_patch_file_changes` 解不出任何檔。另外 `diff.ignoreSubmodules=all` 會讓連 `--raw` 清單都沒有子模組那一行,等於被當成未改。
- 兩者都需要 `--submodule=short --ignore-submodules=none`。S5 的本機設定清單沒涵蓋它們。

severity: minor
blocking: 否 — 測試注入方式與現況不符,但改用既有的覆寫手法就能做。
引句:「S14 用既有的 `deadline` 參數注入」
問題:`_note_reread_judge` 的 `deadline` 是函式內部算出來的區域變數,沒有可注入的參數。`_note_reread_fps(scan)` 也沒有 `deadline` 參數。既有測試是覆寫模組全域 `_NOTE_REREAD_BUDGET_SEC`(見 `scripts/test_lumos.py:68534`)。
覆寫成負值時,`_note_reread_scan` 內部的 `_tick` 先丟出逾時,走不到指紋那一步。要造「剩不到 3 秒」,得把預算設成小於 3 秒的正數。
file: `scripts/lumos:36875`、`scripts/test_lumos.py:68531`

severity: minor
blocking: 否 — 帳上單行可能超過 4096 位元組,只是政策值,但寫法沒對上既有機制。
引句:「的那幾篇的筆記路徑與兩種指紋,最多 20 篇」
問題:`covered` 與 `none` 的帳(`_note_reread_ledger`)不走 `_gate_event_fit`。`v2_only` 最多 20 筆,每筆是路徑加兩個 16 位十六進位指紋,估計約 3.4 KB,再加其他欄位可超過 4096。`_gate_event_fit` 的丟棄清單只認 `rows` 與 `layer1_fps`。
具體失敗情境:實作者沿用 `covered` 現在的單行呼叫,`v2_only` 寫滿時整行過長。

severity: minor
blocking: 否 — 純文字錯誤,不影響實作。
引句:「照 RETIRE-IF 數一次 `note-reread` 事件的 `covered_by` 與 `fp` 欄位」
問題:事件欄位在第二輪已改名為 `fp_counts`,REVISIT 還寫 `fp`。另外〈做法〉3 說「代碼審判定唯一的呼叫點與 7 支既有測試照舊」,實際只有一支測試 `t_codeloop_default_base_prefers_newest_mainline`,裡面有 7 個 `check` 斷言。

severity: minor
blocking: 否 — 兩個實作者會算出不同指紋,但同一份程式內自洽。
引句:「那篇 about_code 每一項配上「它在分岔點..頂端的改動指紋」」
問題:v1 對不在頂端的項寫「無」。v2 沒寫「未改」的項要雜湊什麼字串。若比照 v1 放頂端 blob 編號,S6「主線改了未動的第二支檔,指紋不應變」會紅。計劃沒寫死是放常數,還是整項略過。

----
- 〈做法〉2(全部未改退 `v1`)、〈做法〉5 中「兩邊樹都找不到」的判法:已讀,無 finding。只有「不在清單」且「不在頂端樹」的項才需要這個判斷,不必多一次對分岔點樹的查詢。
- `_patch_file_changes` 加「只用 `\n` 切行」:已讀,無 finding。實測 `"+a\x0cb\n-x".splitlines()` 會切成 `['+a', 'b', '-x']`,後半段 `b` 會被丟掉,對症。S16 前半在現行程式下確實先紅。
- 子模組 `160000` 在預設設定下的 diff 輸出是「Subproject commit」增刪行,`_patch_file_changes` 能照算:已讀,無 finding。
- 型別變更(`T`)退 `v1`:已讀,無 finding。同路徑兩段 `diff --git` 會讓 `files[name]` 後蓋前,這個退路有必要。
- `_lens_default_base` 搬家與薄包裝:已讀,無 finding。呼叫點只有 `scripts/lumos:51024` 一處,測試只有 `t_codeloop_default_base_prefers_newest_mainline` 一支(含「沒有遠端追蹤時用本機 main」、「沒有共同祖先回 None」等斷言),`include_local` 預設 `True` 的包裝能保住它們。
- 新條款 S16–S19 能否寫成先紅的測試:
  - S16 前半、S17、S18:可,新函式不存在就先紅。
  - S16 後半:沒有可攜的造法(見第 4 條 finding)。
  - S19:在沒有 `contrast_fp_v1` 的實作下仍綠,不能證明欄位有被讀(見第 2 條 finding)。

**最高等級 major,共 5 條 blocking。**
