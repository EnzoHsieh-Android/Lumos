severity: minor

這份修補大體沿用既有寫法,沒有引入第二套切段做法,也沒有跨層直呼。只有兩處值得記:判「會被 diff 的檔」的條件在兩處各寫一份,以及 `_diff_git_same_name` 的位置。

先回答你特別點名的三件事:

- **`_diff_git_starts`**:有取代所有「切 `diff --git` 行首」的寫法。對全檔搜 `diff --git` 加 `re.`、`split`、`find(` 只剩這一處用正則找行首,舊的 `re.split(r"(?m)^(?=diff --git )", d)` 已被取代。其餘出現 `diff --git` 的地方(`_delguard_parse_diff` 等)是逐行 `startswith`,不是切段,不算同一類。
- **`_diff_git_same_name`**:放進 `_patch_file_changes` 的方式合理。它先取兩半相同的檔名,不同才退回原本的 `rfind(" b/")`,所以只多一個前置判斷,既有路徑原樣保留。
- **`_note_reread_fp_diff_batch`**:拆成獨立函式,批次大小與參數長度上限沿用同一組 `_NOTE_REREAD_FP_DIFF_BATCH` 與 `_NOTE_REREAD_FP_DIFF_ARGLEN`,沒有另立一套。

severity: minor
blocking: 否 — 同一條規則寫在兩處,目前語意相同,只是日後改一處可能漏另一處
引句:「return e["status"] != "T" and all(o in sizes and sizes[o] <= _NOTE_REREAD_FP_MAX for o in oids)」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:36539`(`_note_reread_fp_file` 內 `ent["status"] == "T"`、`o not in sizes`、`sizes[o] > _NOTE_REREAD_FP_MAX` 三段判斷)
判定理由:`_note_reread_fp_file` 本來就用這三條決定「diff 之前退回 v1」,新增的 `wanted()` 在 batch 函式裡又寫了一份相同條件。這不是第二種做法,而是同一規則複製。上限常數是共用的,所以不會立刻分歧,但日後在 `_note_reread_fp_file` 加退回條件(例如新增一種狀態)時,batch 會把不會被要求的檔收進來,又回到 r5 併發 1 的問題。建議抽成一個 `_note_reread_fp_skip_reason(ent, sizes)` 兩邊共用。

severity: minor
blocking: 否 — 只是放置與命名不一致,行為無差
引句:「def _diff_git_same_name(line):」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:26033`(`_diff_git_starts` 就放在 `_patch_file_changes` 正上方);另有既有的檔頭路徑還原 `_diff_header_path`,在 `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:48750` 一帶
判定理由:`_diff_git_same_name` 被共用的 `_patch_file_changes`(約 26088 行)呼叫,卻定義在約 36654 行,夾在回頭重讀區塊的 `_note_reread_split_diff` 與 `_note_reread_fp_tags` 之間。同一輪新增的 `_diff_git_starts` 則放在 `_patch_file_changes` 旁,兩個同層共用的 diff 檔頭小工具位置分裂,讀的人要翻一萬多行。它另自帶一套「兩半相同」的引號還原,跟 `_diff_header_path` 對 `---`/`+++` 行的還原是同類但各寫一份;不過兩者吃的行不同,不算第二種做法。建議把它搬到 `_diff_git_starts` 旁。

最高等級 minor,blocking 0 條。
