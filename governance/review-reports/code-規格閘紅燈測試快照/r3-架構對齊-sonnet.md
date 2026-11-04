severity: minor

這輪修補整體跟既有做法一致,只有一處小的錯誤處理差異。我對照的是 `0fcc214af`;`c5c97585c` 沒有改 `scripts/lumos`,所以下面的行號兩版通用。

## 問 1:分層與依賴方向

對齊。

- **`_lens_fork_point`**:定義在 `scripts/lumos:49404`,緊鄰唯一的 `_tg_` 呼叫者 `_tg_start`(`:49411`)。規格閘一側的 `_redbase_branch_rows`(`:14343`)改呼叫它,原本是直接呼叫 `_lens_default_base`(`:64892`)。呼叫方向是規格閘到比對工具區的共用函式再到 `_lens_default_base`。
  - 這個方向前一輪就存在。`test-guard.md` 已有一條 WHY 明講紅燈版寫入端共用 `_tg_*`。補丁引句:「def _lens_fork_point(root, head, deadline=None):」。
  - `_lens_` 前綴的函式放在別的區也有先例:`_lens_trusted_ref` 在 `:59670`,跟著它的常數放。
  - 「遠端主線優先,沒有才用本機」這對呼叫,檔內剩下的 `_lens_default_base` 呼叫(`:48166`、`:51618`、`:70042`)都是單一語意(只看本機或只看遠端),沒有重複的成對寫法。
- **`_tg_rb_deleted`**(`:49685`):在比對工具區用 `_lens_git` 跑 `log`,再用 `_nodehome_cat_sizes`(`:44357`)確認終點沒有那支檔。`_tg_rb_load`(`:49750`)已經是這兩層組合,沒有跨層直呼。
  - 解析寫法跟 `:59061` 的 `\x01%H` 標記加 `--name-only`、以及 `:58930` 的 `log --diff-filter=D --name-only` 同一型。
  - `quote=True` 的用法跟 `:48541` 一致。
- **`_tg_rb_load` 多回傳讀取量**(`:49750`):`nread` 是 blob 位元組數。`_tg_analyze`(`:49453`)算 `consumed` 的單位也是位元組,最後在 `_tg_redbase_cands`(`:49679`)相加後傳給 `_tg_rb_compare`。
- **孤兒檔與被刪檔 sha 為 None**:`_tg_rb_doc`(`:49782`)多一個 `sha is not None` 判斷,孤兒檔與被刪檔沿用同一支驗證函式,沒有另寫一套讀取。`_tg_rb_metas` 把「讀哪一版」放進第四欄,`_tg_rb_load` 只吃 spec。
- **check-ignore 改走 `_lens_git`**(`:14298`、`:14408`):回傳碼的判法 `ign is None or ign.returncode not in (0, 1)` 跟 `:36817`、`:1764` 同一套,前一輪的原始 subprocess 呼叫(`_sp.run`)已移除。
- **`_redbase_branch_state`**:共用 `_tg_rb_entry` 的 `cache`,快取鍵是 (路徑, 文字),跟 `_tg_rb_load` 同一套,不會跨文件串錯。
- **`_tg_rb_pending`**:補丁只加了一行註解,說明自己解 porcelain 的原因,並指向 `_handoff_files`(`:71519`)這個先例。我驗過 `_handoff_files` 確實也自己解 `status --porcelain -z` 的狀態碼。

## 問 2:命名與錯誤處理

大體對齊,有一條 minor(A1)。

- **命名與訊息**:`_tg_rb_deleted`、`_lens_fork_point`、`nread` 的命名跟鄰居一致。新訊息仍走 `_tg_rb_bad`(`:49654`),標頭「規格閘紅燈版 {tok}:…」不變,token 用 `_out_clean(Path(n).stem, 40)`,跟 `_tg_rb_metas` 既有寫法一致。
- **`_tg_rb_fill` 的 UNREADABLE**:改成當空檔去查搬家,註解講明這個路徑不是從改動清單來的。`_tg_analyze`(`:49430` 一帶)的改動清單路徑仍列 `tq/unreadable`。兩邊語意不同,各自有理由,不算不一致。
- **不一致處見 A1**。

## 問 3:第二種做法

沒有。

- **讀 git 狀態**:`_tg_rb_deleted` 用 `_lens_git`,check-ignore 的兩處也從原始 subprocess 改走 `_lens_git`,全程沒有新增的原始 subprocess。
- **路徑安全**:`_redbase_prev_doc` 沿用 `_repo_path_unsafe`(`:51031`)和 `_tg_rb_path_ok`。新增的 `_tg_rb_path_ok(ln.strip())` 與 `_tg_rb_path_ok(n)` 也是同一支。
- **找分岔點**:收斂成 `_lens_fork_point`,規格閘一側與 `_tg_start` 共用。
- **快取與比對**:沿用既有的 `_tg_rb_entry` 快取,孤兒檔與被刪檔也走同一條 `_tg_rb_compare`。

**相鄰呼叫路徑是否仍沿用既有做法:是。**

- 寫入端:`_redbase_branch_rows`、`_redbase_target_why`、`_redbase_parse_file`、`_redbase_branch_state` 都走 `_lens_git`、`_lens_fork_point`、`_tg_rb_entry`。
- 讀取端:`_tg_redbase_cands`、`_tg_rb_metas`、`_tg_rb_load`、`_tg_rb_doc`、`_tg_rb_fill` 一路沿用既有函式。

### A1 `_tg_rb_deleted` 不帶截止時間、git 失敗時靜默回空
severity: minor
blocking: 否 — 結構沒有分岔,只是錯誤處理跟同區多數鄰居不同,屬於日誌與錯誤處理差異。
引句:「_lens_git(root, "log", "--format=%x00%H", "--name-only", "--diff-filter=D"」
歸因:有證據的修復回歸。`_tg_rb_deleted` 是這次修補新加的,修前版本 `c627b3874` 沒有這支函式。同款的無截止時間寫法在修前就有的 `_tg_rb_pending` 出現過,修前版本 `c627b3874` 就是這個樣子,所以這個寫法本身有部分是沿用原有的。
差異點有兩個:
- `_tg_rb_deleted`(`scripts/lumos:49685`)沒有 `deadline` 參數,用的是 `_lens_git` 而不是 `_lens_git_dl`(`:64468`),後面的 `_nodehome_cat_sizes` 也是用預設的 60 秒,不像 `_tg_rb_load`(`:49755`)那樣用 `max(1, int(_git_timeout(deadline, cap=60)))`。同區帶截止時間的鄰居是 `_tg_changes`(`:49344`)、`_tg_read`、`_tg_rb_load`、`_tg_rb_fill`、`_tg_redbase_records`。
- git 失敗時回 `[]`(等於「沒有被刪的檔」),而 `_tg_changes` 失敗時回 `None`,由上層記成「比對沒跑完」。`_tg_rb_pending`(`:49703`)也是回空集合,所以這點同區內有兩種寫法。

不對齊共 1 條,其中 major 0 條
