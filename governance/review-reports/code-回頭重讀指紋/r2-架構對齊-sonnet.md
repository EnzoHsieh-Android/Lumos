severity: major

**架構對齊席報告:裸庫 git、批次讀頂端、算函式名三件事的對照**

先講沒問題的部分:
- `_note_reread_git` 是疊在既有的 `_lens_git_dl` 上(`-C` 指到 git 目錄),不是另開 subprocess。`_NOTE_REREAD_GITDIR` 這種模組級快取在 `scripts/lumos` 已有先例(`_NODE_FLAVOR_CACHE`、`_DRIFT_LS_CACHE`)。
- 全域選項常數 `_NOTE_REREAD_FP_GIT` 現在只有一份。原本 `_note_reread_diff` 自己另寫的 precomposeunicode 已被收掉。
- `_note_reread_tip_names` 改走 `_lens_git_dl`,跟鄰居一致。
- `_patch_file_changes` 多一個 `hunk_tag` 旗標,跟既有的 `headers`、`lf_only` 同一種做法。
- 「從原始碼算 hunk 所在函式名」在專案裡沒有既有的可借。`_drift_py_def_re`、`_DRIFT_M1_TEXT_DEF_RE`、`_NS_WD_DEF_RE`、`_affected_test_keys` 都只認 Python、而且只抽「有哪些定義名」,不做「某一行落在哪個定義裡」。`when-symbol:` 是看定義存不存在,也不是位置解析。這裡不算第二種做法。

severity: major
blocking: 是 — 批次讀頂端內容時,另寫了一套「先比大小、再用無上限的讀取」,繞過專案已經定好、而且註明由架構對齊席要求放在批次層的有上限讀取;合計大小也沒有上限。
引句:「_NOTE_REREAD_FP_PREFETCH_MAX = 1024 * 1024   # 頂端內容一次批次讀進來的單支上限」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:31360`(`_nodehome_cat_blobs_capped`,docstring 寫明「上限放在批次讀取這一層,不另起查法」,另有 `max_total_bytes` 與 `deadline`)、`/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:31391`(`_nodehome_cat_blobs`)
判定理由:`_note_reread_fp_prefetch` 自己用 `base["sizes"]` 篩出不超過單支上限的物件,再呼叫無上限的 `_nodehome_cat_blobs`。同一件事(有大小上限的批次讀取)現在有兩種寫法。新寫法沒有合計上限:候選 about_code 列到的小檔加起來最多是「檔數乘 1 MB」,會整批讀進記憶體。`_nodehome_cat_blobs_capped` 已有 `max_total_bytes`,不用就是繞過。建議給 `_nodehome_cat_blobs_capped` 加一個選填的「已知大小」參數,或直接用它並傳 `max_total_bytes`,不要在呼叫端另做一套上限。`_note_reread_fp_tags` 裡逐支的 fallback 讀取已經查過 32 MB 上限,那一處可以接受。

severity: minor
blocking: 否 — 只是把同一個 hunk 標頭正規式再抄一份,不改變行為。
引句:「_NOTE_REREAD_HUNK_RE = re.compile(」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:32237`(`_NOTELINES_HUNK_RE`,已能解析 `@@ -a,b +c,d @@` 四個數字)
判定理由:專案已有一個解析 `@@ -a,b +c,d @@` 的共用正規式,新增的這個只是少取兩個群組。再多一份,日後改 hunk 標頭格式時要多改一處。可以直接用既有的那個,取 group(3) 和 group(4)。

severity: minor
blocking: 否 — 只有判斷條件寫了兩處,目前兩邊結果一致。
引句:「if len(d) > _NOTE_REREAD_DIFF_CAP else None」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:36747`(`_note_reread_diff` 的「0 行上下文仍超過 cap 才截斷」判斷)
判定理由:「什麼情況下判定者材料會被截掉」現在由 `_note_reread_v2_cut` 和 `_note_reread_diff` 各判一次。取 diff 的參數已共用 `_note_reread_diff_once`,但「超過上限就算截掉」這條規則沒有共用。日後有人調整截斷規則,只改一處就會讓 prepare 與 check 的指紋再度分岔,而這正是這次修補要消除的問題。建議把「是否截斷」抽成一支小函式,兩邊共用。

總結:不對齊共 3 條,其中 major 1 條(批次讀頂端繞過 `_nodehome_cat_blobs_capped`)。
