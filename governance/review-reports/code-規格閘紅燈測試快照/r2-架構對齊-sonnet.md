severity: minor

## 問 1:分層與依賴方向

**部分不對齊**,主要見 A1、A2。其餘新碼的層次跟鄰居一致。

- **對齊,寫入端用讀取端的驗證碼。**
  - `_redbase_prev_doc` 呼叫 `_tg_rb_doc`、`_tg_rb_entry`、`_tg_rb_path_ok`,寫入端(規格閘)用讀取端(比對工具)的格式驗證,修前就是這樣。
  - 修前版 `_redbase_branch_state` 已呼叫 `_tg_rb_path_ok`、`_tg_rb_entry`。
  - 這個方向由 `scripts/lumos:49585` 的註解「寫入端在規格閘…讀取端在這裡;格式的單一來源是 Systems/規格閘」背書。
  - 修補把「自己手寫一套讀 JSON 的碼」改成呼叫 `_tg_rb_doc`,方向沒變。
- **對齊,不再跨層呼叫 `_tg_start`。**
  - 修前 `_redbase_branch_rows` 從規格閘層呼叫比對層的 `_tg_start`(修前版 `scripts/lumos:14323`)。
  - 修後直接呼叫共用的底層 `_lens_default_base`,跟 `_rg_fork_point`(`scripts/lumos:48168`)、`_note_reread_fp_base`(`scripts/lumos:51583`)這些呼叫者的做法一致。
  - 這是把跨層直呼拿掉,不是新增。只是 `_tg_start` 的取分岔點邏輯被複製了一份,見 A2。
- **不對齊,比對引擎讀工作目錄。**
  - `_tg_rb_pending` 讓 `_tg_redbase_cands` 的結果取決於工作目錄狀態。
  - 同一引擎 `_tg_rb_load`(`scripts/lumos:49721`)寫著「從終點那一版批次讀…不讀工作目錄」。
  - 其他推送時檢查也有「讀被推的版本、不讀工作目錄」的原則,例如 `scripts/lumos:43715`、`:45100`。
  - 見 A1。
- **對齊,`_tg_read` 加 `max_total` 參數。**
  - 只是把上限往下傳給既有的 `_nodehome_cat_blobs_capped(max_total_bytes=...)`。
  - `_tg_rb_load`(`scripts/lumos:49719`)已有 `consumed` 在 `deadline` 之前的簽名,`_tg_rb_compare`、`_tg_rb_fill` 照這個排法。
  - 沒有跨層。

## 問 2:命名與錯誤處理

**對齊。** 看的是 r2-repair-review.patch 的 `_TG_RB_DIR`、`_TG_RB_VERSION` 改名段、`_redbase_prev_doc`、`_redbase_target_why`、`_tg_rb_pending` 與測試改名段。

- **常數改名。** `_RB_*` 改成 `_TG_RB_*`,跟 `_TG_MAX_BYTES`、`_TG_LIMITS` 同前綴。讀取端函式維持 `_tg_rb_*`,寫入端維持 `_redbase_*`,延續修前的分法。
- **測試名。** `t_tq_guard_redbase_*` 對齊既有 `t_tq_guard_*`(`scripts/test_lumos.py` 有 17 支);`t_spec_gate_redbase_*` 對齊既有 `t_spec_gate_*`(71 支)。
- **錯誤回傳。**
  - 「物件或原因字串」:`_redbase_parse_file`、`_redbase_read_one`,延續 `_tg_rb_doc`、`_tg_rb_entry`、`_tg_rb_locate` 的慣例。
  - 「None 或原因字串」:`_redbase_target_why`,跟 `_repo_path_unsafe_why` 的原因文字風格一致。
- **訊息標頭。** 新增的 stderr 訊息 `[spec-gate] 讀不出…治理帳` 沿用同函式族 `_redbase_attach` 的 `[spec-gate]` 標頭,印 stderr。
- **寫入檔案的守衛。**
  - `_redbase_target_why` 只用 `_note_audit_safe_dir` 擋資料夾,沒有另查檔本身。
  - 這跟 `_note_audit_write_verdict`(`scripts/lumos:51052`)一致,兩者的檔名都帶唯一值。
  - `_secev_append_target`(`scripts/lumos:11854`)才追加檔本身的檢查,但它是往既有檔追加,情境不同,不算不一致。

## 問 3:有沒有第二種做法

**有輕微的複製。** 沒有新的快取或路徑安全檢查,但有兩處小複本(A1 的讀狀態、A3 的 check-ignore)。

- **快取。** `parsed`、`cache` 是呼叫內的區域 dict,延續修前 `idx` 的做法,不是新的快取機制。
- **路徑安全。**
  - 寫入側逐層擋符號連結走 `_note_audit_safe_dir`(`scripts/lumos:51029`)。
  - 讀取側走 `_repo_path_unsafe`(`scripts/lumos:50996`)。
  - 都是共用碼,沒有另寫一套。
- **內嵌測試檔路徑的合法性檢查。** `_tg_rb_entry` 內聯的 `any(x in ("", ".", "..") ...)` 是全檔常見的寫法(`scripts/lumos:7447`、`:60118`、`:66840`),跟相鄰的 `_tg_rb_path_ok`(`scripts/lumos:49644`)同款。不列為 finding。

### A1 比對引擎自己手寫一套讀工作目錄 git 狀態
severity: minor
blocking: 否 — 結構上仍走 `_lens_git`,是同功能的第二份解析,但不是跨層直呼,也不是新機制。
引句:「r = _lens_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", _TG_RB_DIR, binary=True)」
歸因:有證據的修復回歸。修前版沒有 `_tg_rb_pending`,`_tg_redbase_cands` 只在「治理帳或紅燈版有被改動」時才讀。

對照的既有做法,⚠ 請編排者裁:

- `scripts/lumos:67886` 的 `_porcelain_z_paths` 註解寫明改名條目要處理兩個片段。
- `scripts/lumos:21331` 的 `_dirty_non_bookkeeping(rr, untracked=True)` 已被規格閘自己用在 `scripts/lumos:15187`。`governance/redbase/` 不在 `_BOOKKEEPING_DIRS`(`scripts/lumos:37893`),可以直接用它再按前綴過濾。
- 新碼需要「`??` 或 `A`」的狀態碼,`_porcelain_z_paths` 不給。`scripts/lumos:71513` 的 `_handoff_files` 也是自己帶狀態碼解析,所以有先例。
- 因此我判 minor,不判「第二種做法」的 major。如果編排者認為「帶狀態碼讀 porcelain」本身不該有第三份,可升 major。
- 另一點:`_tg_rb_load` 與推送時檢查的「讀被推的版本、不讀工作目錄」宣告(`scripts/lumos:49721`)沒有跟著改。`_tg_rb_pending` 用 `head == HEAD` 把範圍收窄,這是明確例外,先例是 note-shape 的測試綁定那組(`scripts/lumos:49963` 附近的說明)。

### A2 `_redbase_branch_rows` 複製了 `_tg_start` 的「遠端優先、再本機」兩段式
severity: minor
blocking: 否 — 底層仍是共用的 `_lens_default_base`,只是呼叫端的兩段式回退寫了第二份。
引句:「fork = _lens_default_base(rr, tip=head, include_local=False) or _lens_default_base(rr, tip=head, include_local=True)」
歸因:有證據的修復回歸。修前版是 `fork = _tg_start(rr, None, head) if head else None`(修前版 `scripts/lumos:14323`),修補為了讓「分岔點等於頂端」的情境不同才改寫。

- 對照:`_tg_start`(`scripts/lumos:49413`)是同一個兩段式。
- 新增的分支名判斷(`symbolic-ref`,`main`、`master`、空字串)是這裡才有的規則,別處沒有。
- 這不是新機制,只是同一個兩段式有了兩份。

### A3 `_redbase_target_why` 新增一份原生 `subprocess` 的 `git check-ignore`
severity: minor
blocking: 否 — 同檔相鄰的 `_redbase_parse_file` 已經是同樣寫法,新增的是同寫法的第二份,不是新機制。
引句:「ign = _sp.run(["git", "-C", str(rr), "check-ignore", "-q", "--", rel], capture_output=True, timeout=30)」
歸因:有證據的原有漏查。原寫法在修前版 `scripts/lumos:14279`,修補新增了一份複本。

- 對照:全檔 git 呼叫的慣例是 `_lens_git`(`scripts/lumos:64890`,吞錯、逾時);`_local_ledger_doctor_msgs`(`scripts/lumos:1764`)就用 `_lens_git(..., "check-ignore", "-q", ...)`;還有 `_git_ignored`(`scripts/lumos:36814`)。
- `_git_ignored` 判不了時回空集合(放行),而這裡判不了時擋下。語意不同,所以不能直接套用,但仍可抽成共用 helper。

不對齊共 3 條,其中 major 0 條
