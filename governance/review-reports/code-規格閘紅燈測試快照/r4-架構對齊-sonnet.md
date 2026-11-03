severity: minor

行號都對照修後版 `655d6f4a4:scripts/lumos`。修前版 `0fcc214af` 我另外抽出來比對過。

## 問 1 分層與依賴方向:對齊

- `_tg_rb_deleted` 改走 `_lens_git_dl` 並帶 `deadline`,這是同層標準做法。`_tg_changes` 也這樣呼叫(`scripts/lumos:49348`),`_tg_redbase_records` 同樣有 `deadline` 參數(`scripts/lumos:49628`)。
- 讀 blob 大小時用 `_nodehome_cat_sizes(root, specs, max(1, int(_git_timeout(deadline, cap=60))))`(`scripts/lumos:49707`),和 `_tg_rb_load`(`scripts/lumos:49781`)以及 `_tg_changes` 之後的讀取段(`scripts/lumos:49387`)一字不差。
- 失敗改回 `None`,由 `_tg_redbase_cands` 轉成 `(None, 訊息)`(`scripts/lumos:49670-49672`)。這跟 `_tg_redbase_records` 的 `(None, 原因)`(`scripts/lumos:49635`)和 `_tg_rb_load` 的 `(None, None, 訊息, 0)`(`scripts/lumos:49787`)同形。修前吞掉失敗回 `[]` 才是跟鄰居不一樣的地方,這次改回一致。
- `_tg_rb_deleted` 只有 `_tg_redbase_cands` 一個呼叫端。
- `_tg_rb_metas` 裡的 `gone_bad` 是內部函式(`scripts/lumos:49739`)。`_tg_*` 區段沒有別的內部函式,但全檔有先例,例如 `_handoff_files` 裡的 `_git_key`(`scripts/lumos:71567`)。它只是包一層 `_tg_rb_bad`,沒有跨層,我判為對齊。
- `loose` 欄位是 `_tg_rb_load` 用已有的 `sha is None` 算出來的(`scripts/lumos:49803-49804`),沒有新增讀取來源。`_tg_rb_chain` 在 `_tg_rb_*` 家族內自己分兩段,沒有跨層直呼。

引句:「r = _lens_git_dl(root, "log", "--no-renames", "--format=%x00%H", "--name-only", "--diff-filter=D", f"{base}..{head}",」

## 問 2 命名與錯誤處理:大致對齊,有一條 minor

- 對齊的部分:
  - 新錯誤訊息「git 讀不出這條分支刪過哪些規格閘紅燈版(逾時或 git 跑不動)」,句型同 `scripts/lumos:49787` 和 `scripts/lumos:49431`。
  - 原因字串、`_TG_WHY` 的 `(說明, 處置)` 兩段式都沿用。
  - `_tg_rb_deleted`、`_tg_rb_pending` 的修改沒有新增命名。
- 不對齊的部分:見下面 A1。

### A1 `_tg_rb_bad` 新增的參數叫 `key`,跟同家族慣用的字義撞名
severity: minor
blocking: 否 — 只是命名跟鄰居不一致,結構(沿用 `_tg_cand` 的 `ident` 算指紋)是對的。
引句:「def _tg_rb_bad(tok, file, reason, key=None):」
這個參數是「算指紋時代替原因字串的穩定字」。`_tg_cand` 把這個位置叫 `ident`(`scripts/lumos:49334`)。`_tg_rb_*` 家族和候選字典裡的 `key` 另有所指:`_tg_rb_unmatched(last, path, key, reason)`(`scripts/lumos:49947`)裡是測試函式鍵,候選字典的 `"key"` 則是指紋雜湊(`scripts/lumos:49341`)。讀的人會把它當成函式鍵或雜湊。建議改叫 `ident`,或用別的不撞名的字。
歸因:有證據的修復回歸。修前版 `_tg_rb_bad(tok, file, reason)` 沒有這個參數,是 r4 修補新加的。

## 問 3 第二種做法:沒有

- 讀 git 狀態:都走 `_lens_git_dl` 或 `_lens_git`,沒有自己另開 `subprocess`。`_tg_rb_deleted` 用 `log --diff-filter=D --name-only`、文字輸出加 `quote=True`,跟既有的 `_lens_git(... "log","--diff-filter=D","--format=%H","--name-only" ...)`(`scripts/lumos:58958`)同一寫法。
- `--no-renames`:全檔有先例(`scripts/lumos:21690`、`scripts/lumos:41949`、`scripts/lumos:48558`、`scripts/lumos:57716`)。
- `-M` 改動清單:`_tg_changes` 本來就用 `-M`(`scripts/lumos:49348`)。`_tg_rb_metas` 新增把 `R`、`C` 也當新增,只是讀既有 `ch`,沒有另外算一份。
- 工作目錄偵測:`_tg_rb_pending` 仍是自己解 porcelain。這是上一輪就核可的做法(原註解已寫先例是 `_handoff_files`,`scripts/lumos:71576`),這次只放寬條件成 `b"A" in ent[:2]`,沒有新增第二套。
- 路徑安全、快取、找分岔點:修補都沒碰,沿用 `_tg_rb_path_ok` 和 `_tg_start`。
- 測試:`t_tq_guard_redbase_loose` 用 `m._lens_git_dl`、`m._nodehome_cat_sizes` 換掉再還原,跟同檔其他測試(例如 `scripts/test_lumos.py:57079`、`scripts/test_lumos.py:70148`)同一型。`t_` 開頭會被自動收進測試表。

## 修補鏡頭中跟架構有關的部分

修補處相鄰的呼叫路徑仍沿用既有做法。`_tg_rb_deleted` 的 git 呼叫、逾時計算、失敗往上回 `(None, 訊息)`、`_tg_rb_load` 的批次讀取、`_tg_rb_chain` 的候選產生(`_tg_fn_cands`、`_tg_cand`)都沒有改成別的路。看的段落是 `r4-repair-review.patch` 的 `scripts/lumos` 各 hunk。

不對齊共 1 條,其中 major 0 條
