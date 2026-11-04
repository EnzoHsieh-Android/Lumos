severity: minor

結論:這份 diff 的結構與鄰居一致,沒有跨層直呼,也沒有引入第二套解析。我只找到兩條 minor 的不對齊,都不擋推。報告的依據是我讀完 r4-snapshot.patch、r4-repair-review.patch,並對照 scripts/lumos 的鄰居。

**第 1 問:分層與依賴方向**

- 新的 git 小工具 `_git_bool`、`_git_partial_clone` 放在 `_git_is_shallow` 正下方,見 `scripts/lumos:12021`。這跟既有的「git 小工具聚在一區」一致。
- `_git_partial_clone` 走 `_lens_git_dl`(`scripts/lumos:64817`),回 True/False/None 三態。這跟同族的 `_gov_ledger_ignored`(`scripts/lumos:1775`)一樣。
- 回頭條件那支 `_drift_born_env_err`(`scripts/lumos:55700`)原本自己寫一行 `config --get extensions.partialClone`,現在改呼叫共用函式。這是收斂成一份,方向正確。
- `_redbase_on_branch` 內聯寫了 `--is-ancestor` 判斷,是專案內第三份(`_note_reread_own_fps` 在 `scripts/lumos:52862`,`_codeloop_missing_commit` 在 `scripts/lumos:69973`)。專案裡有十幾處內聯的 `--is-ancestor`,沒有共用 helper,所以內聯是慣例。docstring 也寫明三處判不了的方向各不相同,不抽共用。
- 讀帳走既有的 `_gov_rows_at`(`scripts/lumos:61042`)。`rev=None` 讀工作目錄那份,是它本來的設計,沒有另寫一套。
- 有一條不對齊,詳見下方第 1 條。

severity: minor
blocking: 否
引句:「ref = _note_reread_branch(rr, None)   # 同一個 symbolic-ref -q HEAD、同一道控制字元清洗」
不對齊:規格閘的 `_redbase_branch_name` 呼叫了回頭重讀專屬的 `_note_reread_branch`(`scripts/lumos:53383`)。這支原本只在回頭重讀區內使用,呼叫點都在 `scripts/lumos:53305` 一帶,它的 docstring 也是為「事件的 branch 欄」而寫。這次是規格閘跨功能借用它,借的是回頭重讀區的 helper,不是中性區的。對照鄰居:
- 共用給規格閘、比對工具、doctor 的 `_gov_ledger_ignored`,明確放在帳檔那一區。
- 專案裡「取目前分支」本來就各功能各有一份:`_codeloop_git_branch`(`scripts/lumos:64722`)、`scripts/lumos:42160`、`scripts/lumos:65230`。

這次沒有新增第二套 git 呼叫,而是借既有的。diff 也把 `_note_reread_branch` 的 docstring 補上第二個呼叫端,所以耦合有留痕,結構上還算對。但它是功能對功能的直呼,不是呼叫共用層。
- 寫入端(`ref=` 欄)與 android-e2e 的 `scripts/lumos:70748` 同欄名、同短分支名形式,沒有問題。
- 分離 HEAD 時這裡不寫 ref,e2e 是寫字面 `HEAD`。這是刻意的,docstring 有說明。

**第 2 問:命名與錯誤處理**

- 命名一致:`_REDBASE_ANC_BUDGET_SEC`、`_REDBASE_ANC_CAP` 的前綴風格同 `_NOTE_REREAD_FP_RESERVE`、`_TG_MAX_STMTS`。`rr_` 帶底線是本區已有的避撞寫法(`m_`、`r_` 同類)。
- git 失敗與逾時的處理一致:
  - `_git_partial_clone` 的 `r is None or returncode not in (0, 1)` 回 None,同 `_gov_ledger_ignored` 的 `not in (0, 1)` 回 "unknown"。
  - `_drift_born_env_err` 把 None 當「git 跑不起來」,跟它上一步淺層判斷逾時的處理同詞同向。
  - `_redbase_on_branch` 內部的 `_git_timeout(deadline)` 配 `_git_is_shallow(rr, timeout=t)` 與 try/except TimeoutExpired,就是 `scripts/lumos:11135` 與 `scripts/lumos:69881` 那一族的既有寫法。
- 印說明一致:`print(f"[spec-gate] ...", file=sys.stderr)` 與同區的 `_redbase_note_green`、`_redbase_attach` 同形,措辭也同形。
- 一個值得知道但我不列為不對齊的點:`_git_is_shallow` 用 `timeout` 秒數並丟 TimeoutExpired,`_git_partial_clone` 用 `deadline` 並回 None,同一個呼叫點得處理兩種慣例。但兩者各自對齊自己所屬的函式族(裸 subprocess 與 `_lens_git_dl`),不是這份 diff 新造的分歧。
- 測試端:新的 `t_git_partial_clone_keys` 直接重寫 `.git/config` 文字。這是為了寫出裸鍵,`git config` 寫不出來,理由成立。其餘案例沿用 `_nh_git`(`scripts/test_lumos.py:68243`)與巢狀 `git()` 小函式的既有寫法。

**第 3 問:第二種做法**

專案裡沒有既有的「git 設定布林」解析器可以重複。我查過 `--type=bool`、`("true", "yes"`、`"1", "true"` 這幾種形狀,結果如下:
- 命中的 `scripts/lumos:12776`、`scripts/lumos:13483` 判的是 YAML 值,不是 git 設定。
- 環境變數那批一律是 `== "1"`,領域不同。
- 所以 `_git_bool` 不是對既有功能再寫一套。

severity: minor
blocking: 否
引句:「if v in ("false", "no", "off", ""):」
不對齊 ⚠(判不準):`_git_bool` 手寫了 git 的布林規則(false/no/off/空字串/整數),而 git 本身有 `--type=bool` 可以代為正規化。這份 diff 自己的測試就拿它當對照(引句:「"--type=bool", "--get-regexp"」)。鄰居的做法是讓 git 給正規答案:`_git_is_shallow` 吃 `rev-parse --is-shallow-repository` 的輸出,`_gov_ledger_ignored` 吃 `check-ignore` 的回傳碼。判不準的原因是:
- `--get-regexp` 同時抓三種鍵,其中 `partialCloneFilter` 不是布林,`--type=bool` 套不上去,要分兩次呼叫才能用。
- 手寫版 docstring 明講「git 認不得的寫法算真」,是保守方向。

所以這比較像「沒用 git 現成能力」,而不是「與專案既有做法分歧」。我標 minor,不算 major。

不對齊共 2 條,其中 major 0 條

相關檔案:
- `/Users/enzo/harness/lumos-green-scope/scripts/lumos`(`_git_is_shallow` 在 12021 一帶、`_redbase_branch_name`/`_redbase_branch_rows`/`_redbase_on_branch` 在 14413–14526、`_note_reread_branch` 在 53383、`_drift_born_env_err` 在 55700)
- `/Users/enzo/harness/lumos-green-scope/scripts/test_lumos.py`
