severity: minor

## F1 生效那份讀不到時,被誤說成「讀不到本工作目錄的」
severity: minor
blocking: 否
引句:「add(layer, "degraded", det + f";讀不到本工作目錄的 {fn},對不出跟生效那份是否相同")」
file: `scripts/lumos:26010-26023`(對應 diff 新增的 `except OSError` 區塊)

失敗場景:
- 輸入:附加工作樹裡 `core.hooksPath` 指向主工作目錄的 scripts/hooks。生效那份 `pre-commit` 是 mode 0111(可執行但不可讀)。本工作目錄那份可讀,而且大小跟生效那份相同。
- 路徑:`ok = eff.is_file() and os.access(eff, X_OK)` 為真。`_enforcement_prepush_ungated` 對 OSError 回 None,所以關卡判斷放行。接著 `filecmp.cmp(f, eff, shallow=False)` 在大小相同時會去開 `eff`,丟出 PermissionError。這個 PermissionError 被 `except OSError` 接住,輸出「讀不到本工作目錄的 pre-commit」。
- 實測輸出:`⚠️ git-pre-commit degraded ...;讀不到本工作目錄的 pre-commit,對不出跟生效那份是否相同`。
- 這個歸因是錯的:實際讀不到的是生效那份。我用 git 實際提交驗證,hook 會報 `/bin/sh: ...pre-commit: Permission denied`,提交被擋。所以真實狀態是生效那份跑不起來,該列 inactive。
- 嚴重度較低的原因:這是罕見的權限組合,而且使用者仍看得到 degraded。
- 「讀不到本工作目錄的」這句話只在 `f` 讀不到時才對。`except OSError` 沒分是哪一邊丟的。

歸因:有證據的修復回歸(新增的 degraded 分支引入的誤歸因)。
- 修前(f3c49207):`unknown`,訊息 `[Errno 13] Permission denied: '.../main/scripts/hooks/pre-commit'`。這句至少點出正確的路徑。
- 修後(baa034d1):degraded,訊息歸因成本工作目錄的檔案。
- 查證命令:在臨時 repo 的附加工作樹裡,執行 `python3.14 <兩版 scripts/lumos> enforcement | grep git-pre-commit`。
- 修前版也有「生效那份可執行但不可讀」卻判成 active 的老問題。主工作目錄本身就會這樣,不是這次引入的。

建議修法:不要共用同一個 `except`。分別 `open` 兩邊的檔,或在 `filecmp` 之前先檢查 `os.access(eff, os.R_OK)`,不可讀就列 inactive 並點名 `eff`。

## F2 測試的跳過條件在還原權限之後才判斷
severity: minor
blocking: 否
引句:「if _os.access(wpc, _os.R_OK) and _os.geteuid() != 0:」
file: `scripts/test_lumos.py`(`t_hooks_path_sibling_worktree` 尾段)

失敗場景:
- 前面的 `finally` 已經把 `wpc` 改回 0o644,`_os.access(wpc, R_OK)` 因此恆為真。它沒有在檢查 chmod 000 當下檔案是否真的變成不可讀。
- 在不支援權限位的檔案系統,例如 FAT 或某些掛載,`ln` 讀得到檔案,卻不會跳過,於是 `degraded` 和 `讀不到` 兩個斷言必定失敗。
- 以 root 跑的情況由 `geteuid() != 0` 擋住,正確。
- 還原本身有 `finally`,這點沒問題。
- 這個測試的 chmod 000 也沒有涵蓋 F1 的「生效那份不可讀」,所以抓不到 F1。

歸因:未判定。這個跳過條件是本輪新增的測試,沒有修前版本可比。

## 三問
1. 原問題的修復效果:
   - claim:工作樹那份讀不到時,列 degraded 並說讀不到,而不是 unknown。
   - input:附加工作樹裡 `pre-commit` 設 chmod 000。
   - expected:degraded,訊息含「讀不到」。
   - case_source:binding 的 R3 repair。
   - 修前:`unknown`,`[Errno 13] Permission denied`。
   - 修後:`degraded ...;讀不到本工作目錄的 pre-commit`。
   - comparison:效果成立。
2. 修補處的正常、錯誤與相鄰路徑:
   - 兩份內容相同、本工作目錄沒有同名 hook、工作樹 hooks 目錄 000、工作樹那份是懸空捷徑,修前修後都是 active,說明有註明「沒有」。
   - 生效那份不可讀(F1)是新的相鄰路徑,修後歸因錯誤。
   - `ok` 為假時,`differs` 短路,不會呼叫 `filecmp`,inactive 路徑不受影響。
   - `python3.14 scripts/test_lumos.py -k hooks_path_sibling` 14 條全過。
3. 新發現的同一案例:
   - F1 在修前是 unknown(路徑正確),修後是 degraded(歸因錯誤)。
   - F2 沒有修前對照,未判定。

## 其餘已驗與未驗
- 已驗:
  - `sib` 的計算在 try 之外。`_lens_git` 會接 OSError 和逾時,`resolve()` 在 3.14 對非嚴格模式不丟例外,所以沒有找到可行的整層崩潰路徑。
  - `_enforcement_prepush_gated` 讀的 `_hooks_path_dir(root, hp)/pre-push` 與 `eff` 是同一份,新舊互讀一致。
  - 唯讀性成立:新增的 git 呼叫只有 `rev-parse`。
  - `enforcement_summary` 把 degraded 計入分母但不算 active。進場提醒會點名 degraded(`scripts/hooks/claude/lumos-entry-hook.py:172`),這是預期行為。
  - `cmd_enforcement` 在 `active < total` 時叫人跑 `lumos install --force`,對 sibling degraded 並無幫助。這是既有行為,不算本案缺陷。
  - 臨時目錄已清除。
- 未驗:
  - git 低於 2.31 的 `--path-format=absolute`。若不支援,`_rev` 回 None,退回 inactive,屬安全方向。
  - 裸 repo 與子模組的實機場景。只從程式推導,common dir 不同或 `--show-toplevel` 失敗都會回 None。
  - macOS 大小寫不敏感檔案系統的路徑比較。

總結:最高等級 minor
