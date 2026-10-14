severity: major

severity: major
blocking: 是 — 單看這份補丁只有一種做法。但另外三個分支要在入口加 `os.environ.setdefault`,三者合併後同一件事就有兩種做法,所以這三個分支合併前要先挑定一種。
引句:「env = _git_env_no_replace() if no_replace else None」
對照:
- `scripts/lumos: 44537` 的 `_git_env_no_replace`。這個環境變數工廠是這份補丁新加的。
- `scripts/lumos: 48454` 的 `_lens_git(no_replace=)`。這個旗標也是新加的。
- `scripts/lumos: 24583` 與 `scripts/lumos: 44698` 是兩處手帶 `env=` 的 subprocess。
- 既有程式裡沒有任何其他 `GIT_*` 環境變數處理,也就是還沒有「git 環境」這個慣例。

判定理由:
- 補丁用逐呼叫處理 git 環境:一支工廠函式,加上 `_lens_git` 的旗標,再加兩處手帶 `env=`。
- 入口的 `setdefault` 是行程層的做法,保護的是同一件事。兩種都留下來,以後讀的人無法判斷某一支 git 呼叫到底靠哪一層保護。
- 兩者語意還不同。`setdefault` 不會蓋掉使用者自己設的 `0`,逐呼叫是強制設成 `1`。
- 建議二選一:
  - 選入口統一:刪掉 `_git_env_no_replace`、`no_replace=` 與那幾處 `env=`。
  - 選逐呼叫:另外三個分支不加 `setdefault`。
- 我較傾向入口統一加強制設值,因為殘留相關的讀取散在 `_lens_git`、`_diff_range_ends`、`_residual_blob_at` 三種寫法。要是漏掉一處,`git replace` 就能偽造那一處的起點。

severity: minor
blocking: 否 — 沒有第二種做法,只是少了鏡頭已有的時間預算慣例,功能上仍會算完。
引句:「_res_part = _lens_residual_section(root, base_sha, head_sha, vault_rel)」
對照:`scripts/lumos: 48743` 的 `_lens_extcode_section(..., deadline)`。
- 它由 `_t0 + _LENS_INNER_BUDGET - _LENS_FALLBACK_RESERVE` 算出 deadline。
- 每次 git 呼叫前先算剩餘秒數,逾時夾在剩餘秒數內,不足 1 秒就回報 truncated。

判定理由:
- 新增殘留段說「形狀照外部碼表補選段」,但沒有接上同一個 deadline。
- 它連續讀索引兩版,每次最長 20 秒。它還讀帳兩版(最長 60 秒)和每筆決策的 `git show`,全都不夾進 45 秒的鏡頭預算。
- 殘留很多或 git 慢時,可能把掛鉤內層預算吃光。
- 建議:把 deadline 傳進 `_lens_residual_section`,逾時回「算不出來」那句固定說明加必答題。這條路徑已經有了,不用新增機制。

severity: minor
blocking: 否 — 本機殘留一族原本就用直接呼叫 subprocess 的寫法,這份補丁還把兩支併成一支。
引句:「def _residual_blob_at(repo_root, rev, rel, timeout=60):」
對照:
- `scripts/lumos: 48908` 的 `_json_at_ref`,和 `scripts/lumos: 44194`、`44300`、`31596` 的 `_lens_git(root, "show", f"{ref}:{rel}", binary=True)`。
- 全檔讀某版檔案的主流寫法是 `_lens_git(..., binary=True)`。

判定理由:
- `_residual_blob_at` 自己用 `subprocess.run` 和 `ls-tree` 分辨 missing 與 unreadable,沒走 `_lens_git`。
- 同一份補丁卻替 `_lens_git` 加了 `no_replace` 旗標,所以出現兩條都帶 replace 防護的 git 讀檔路徑。
- 把兩支殘留讀法併成一支,方向對。
- 若採入口統一(上一條),這支只剩 missing 與 unreadable 的分辨邏輯,自然可以改包 `_lens_git(binary=True)`。
- 不構成第二種做法,因為殘留一族本來就是這樣寫。

捷徑帳路徑檢查不列為不對齊:
- `cmd_guard_audit` 先過 `_retro_gov_path_err`,有錯就不寫帳並印警告,這跟 `scripts/lumos: 15170` 的 `cmd_loop_cap_decision` 同一個順序。
- 讀端 `_gov_vc_gate_events` 也是用同一支函式,見 `scripts/lumos: 14582`。
- 函式名帶 retro,但已是版控帳的共用檢查;改名屬風格偏好,不列。
- 不過 `cmd_loop_cap_decision` 是擋下並回 2,審計這邊是警告後仍回 0。審計戳記是先寫好的,所以這是合理差異。

不對齊 3 條,其中 1 條需修。
