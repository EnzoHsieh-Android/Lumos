severity: minor

整體照計劃〈做法〉實作,我找到兩個小問題:一個已實測的崩潰,一個無上限的 git 呼叫數。

## Finding 1:提交寫法下,反引號路徑含 NUL 會讓 dispatch-lens 整個崩掉

severity: minor
blocking: 否 — 要計劃文字裡真的有 NUL 才會踩到,放行也只是退回「沒附固定席」;但這正是計劃要消除的靜默放空。
引句:「if _spec_ls_tree_one(root, commit, cand) is not None:」

問題:`_LENS_SPEC_CODE_BT_RE` 的 `[^`\s]+` 會吃進 NUL(`'\0'.isspace()` 為假)。提交寫法下,這個候選走到 `_spec_ls_tree_one`,再進 `_lens_git` 的 `subprocess.run`。Python 對含 NUL 的參數丟 `ValueError: embedded null byte`,而 `_lens_git` 只接 `OSError` 和 `TimeoutExpired`。同一支程式的 `_spec_commit_has` 已經先擋 NUL,這裡漏了。

失敗情境:計劃(提交寫法)含反引號包起來的 ``scripts/b<NUL>c.py``。`spec-freeze` 本身成功,印出 `LUMOS-SPEC: <編號>:<路徑>`。`dispatch-lens --spec <編號>:<路徑> --repo . --json` 則以 rc 1 加 traceback 崩潰,不印任何 `lens_fail` JSON。掛鉤收到 rc 1 且沒有認得的代碼,`_spec_fail_note` 回空字串,派工詞什麼說明都不附。

對照:

- 同一份計劃用工作樹寫法跑,rc 0。
- 舊版 lumos 的工作樹寫法也是 rc 0。
- 計劃〈做法 3〉明寫「含 NUL 的二進位計劃照常讀、不報錯」。

建議在 `_spec_ls_tree_one` 或 `_lens_spec_code_files` 加 NUL 判斷(同 `_spec_commit_has`),或讓 `_lens_git` 一併接 `ValueError`。

佐證:``file: `scripts/lumos`(補丁 `_lens_spec_code_files` 與 `_spec_ls_tree_one`)``

## Finding 2:提交寫法的 git 呼叫數沒有上限,大計劃會超過掛鉤預算

severity: minor
blocking: 否 — 只有超大計劃才踩到,結果是掛鉤逾時並附逾時說明,仍然放行。
引句:「elif commit and cand not in tried and len(only) < _LENS_SPEC_MAX_FILES:」

問題:`len(only) < 5` 只限制「找到的」數量,「試過但不存在」的每個候選都起一次 `git ls-tree`。`_lens_spec_linked` 對每個不重複、會談目錄沒有的連結各起一次 `git cat-file -e`,也沒有上限。工作樹寫法完全不跑 git。

實測:1MB 以內的計劃,含 1500 個不存在的 `[[Systems/nN]]` 加 1500 個不存在的 `` `scripts/xN.py` ``。`dispatch-lens` 跑超過 41 秒仍沒結束,最後被外部 SIGTERM(rc -15)中止。掛鉤內層預算是 45 秒,`_LENS_SPEC_BUDGET` 的 30 秒只管後面 impact 那段。典型計劃(幾十個連結)不受影響。

建議對候選數量或總耗時設上限(例如最多試 N 個,或沿用 `_t0` 加預算)。

佐證:``file: `scripts/lumos`(補丁 `_lens_spec_linked`、`_lens_spec_code_files`)``

## 已讀,無 finding

- **提交寫法檢查順序**:`not_git` → 編號長度與解析 → 路徑字串 → NFC → vault → 一般檔 → 大小 → 讀內容,與〈做法 2〉一致。
  - 短編號、縮寫、被同名分支搶走的情形都回 `spec_rev_missing`。
  - 空計劃(0 位元組)與剛好 1MB 照常成功;1MB 加 1 回 `spec_too_large`。
- **只讀一般檔、符號連結**:`ls-tree -z -l` 只收 100644/100755 的 blob,目錄、符號連結、子模組都回 `spec_missing`。`spec-freeze` 逐段 `lstat`,`resolve()` 後必須在 repo 內,最終讀檔帶 `O_NOFOLLOW`。
- **`--out` 衝突**:內容不同回 `out_conflict`,實測沒有覆寫;內容相同則重建。1 到 5 步都在建物件之前,拒絕時不建提交。
- **暫存 index 與關掉掛鉤**:
  - 實測在 repo 放 `post-index-change` 掛鉤,執行 `spec-freeze` 後掛鉤沒跑。
  - `git status` 顯示工作樹的其他改動沒有進提交,真的 index 沒動,也沒有新 ref。
  - 從子目錄執行時前綴處理正確。
- **工作樹寫法**:`read-spec_worktree` 的檢查和 stderr 原文與原本一致,只多帶失敗代碼。`code_files` 與 `landing` 的分支重排後,工作樹寫法的輸出與原本一致。
  - 小差異:反引號正則也套用到工作樹寫法,中文檔名現在會被收進來,這是〈S6〉刻意的。
  - 小差異:`--arch-target` 的 vault 由「HEAD 上排序第一」改成 `slugs[0]`。計劃寫「跟現在相同」並不精確,只有在工作樹有 HEAD 沒有的未追蹤 vault 時才不同,影響很小。
- **掛鉤只讀欄位**:只讀 `spec_source`、`lens_fail`,不解析值、不跑 git。`kind`、note 字首和繞法提示的條件都與〈做法 8〉一致。成功不記事件。
- **be-api-compat**:`--json` 只是新增欄位,`_dispatch_lens_fail` 的 `extra` 預設為空,舊讀端不受影響。
- **be-authz**:沒有新增網路端點。提交寫法只在會談 repo 讀物件庫,路徑限定在 `docs/<名>-knowledge/` 底下。

我的實驗目錄已刪除。

最高等級 minor,blocking 0 條。
