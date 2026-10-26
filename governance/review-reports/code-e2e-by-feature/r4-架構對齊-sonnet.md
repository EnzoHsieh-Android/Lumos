severity: major

這是架構對齊席第 4 輪的報告。鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/08273ea6…json.warming` 不存在,沒有東西要處理。

## A1 查證紀錄的捷徑檢查在原地另寫一套,沒用專案共用的路徑守衛
severity: major
blocking: 是

對照:
- file: `scripts/lumos:46653`(`_repo_path_unsafe`)。它的 docstring 寫著「逐層擋符號連結+解析後要在 repo 內」只有這一份,筆記內容審的 `_note_audit_safe_dir` 和 `_drift_ledger_path_err`(`scripts/lumos:51605`)都呼叫它。
- file: `scripts/lumos:46674`(`_repo_path_unsafe_why`)。它寫著符號連結這一類擋下訊息只有這一份文字。
- 新碼在 `_e2e_record_update` 裡自己列三個路徑逐一 `is_symlink()`,也沒有「解析後要在 repo 內」這一步,訊息也是自己寫的一句。

引句:「    if any(x.is_symlink() for x in (Path(root) / ".lumos", Path(root) / E2E_RECORDS_DIR, p)):   # 陌生專案提交一個捷徑就能把紀錄寫到專案外(代碼審 code-e2e-by-feature r3 資安席)」

失敗場景:專案之後補洞,例如 Windows junction,會只補共用那份,這支不會跟著補。這正是共用守衛的 docstring 說要避免的狀況。

歸因:有證據的修復回歸。

兩版查證:
- 我把 `4b056532`(修前)和 `7988107c`(修後)的 `scripts/lumos` 各取出來,載入檔案,對同一個專案目錄呼叫 `_e2e_record_update`。專案目錄的 `.lumos/e2e-records` 是指向專案外的捷徑。
- 修前:回傳專案內的路徑,檔案實際寫到專案外。
- 修後:回傳 `(None, '.lumos/e2e-records 或紀錄檔是捷徑,不跟過去寫…')`,專案外沒有新檔。
- 同一個路徑丟給共用的 `_repo_path_unsafe`,兩版都回 `('symlink', …/.lumos/e2e-records)`。
- 所以行為上這個修復有效,與共用守衛的判定也一致。問題只在做法不同,修法是改呼叫 `_repo_path_unsafe` 加 `_repo_path_unsafe_why`。

## A2 本機總表的寫入沒過共用的路徑守衛
severity: minor
blocking: 否

對照:
- file: `scripts/lumos:51648`(`_drift_ledger_append`)寫帳前先過 `_drift_ledger_path_err`。
- 新碼的 `_e2e_history_append` 直接 `p.parent.mkdir(parents=True)` 再交給 `_local_ledger_append`。
- 同一批修補在 A1 補了紀錄的捷徑檢查,總表這條沒補,同一個功能裡兩個寫入器的防護不一致。
- 鄰居 `_usage_log`(`scripts/lumos:26881`)也是不檢查直接用 `_local_ledger_append`,所以這條不算結構錯,只是新碼同一批裡不齊。

引句:「        ok = _local_ledger_append(p, ("\n" if _ledger_tail_needs_newline(p) else "") + text)」

歸因:有證據的原有漏查。

兩版查證:
- 專案目錄的 `.lumos` 是指向專案外的捷徑,呼叫 `_e2e_history_append`。
- 修前 `4b056532` 和修後 `7988107c` 都在專案外建出 `artifacts/android/history.jsonl`。
- 這個函式在修補範圍內沒有改動,兩版結果相同,所以不是這次修補造成的。

## A3 子指令分派另起一支函式,沒有留在 main 裡內聯
severity: minor
blocking: 否

對照:
- file: `scripts/lumos:68164`。`note-audit` 有 7 個子指令,全部在 main() 裡內聯。
- file: `scripts/lumos:68665`(`_guard_dispatch`)。`_guard_dispatch` 獨立一支的理由是十幾個子指令共用一組例外接法,只在呼叫處包一個 try。
- 新碼 `_android_e2e_dispatch` 沒有任何共用接法,只是三個 if。作者把它列進 `_guard_dispatch` 的 docstring 當例外,理由寫的是審查席要求,不是技術理由。

引句:「    if args.cmd == "android-e2e":」

歸因:有證據的原有漏查(修前就有)。`git show 4b056532:scripts/lumos` 的 `_android_e2e_dispatch` 已經存在,這次修補只改了 docstring。
⚠ 這條已經以文件例外的形式明講過,我判成 minor,要不要升成 major 由編排者裁。

## A4 `stability_scenarios` 進設定的路徑跟 `stability`、`e2e` 不同,而且驗兩處
severity: minor
blocking: 否

對照:
- file: `scripts/lumos:39435`。`stability` 和 `e2e` 在 `_macrobench_config` 驗過後,直接放進 `dict(MACROBENCH_DEFAULTS, …, stability=…, e2e=…)`。
- `stability_scenarios` 被放進「選填欄位驗型別」的 `_macrobench_config_fields`,但那一支並不驗它。驗證另外在 `_macrobench_stab_top_err` 做一次,`_e2e_cfg_err(scen=…)` 又做一次。
- 結構上是對的,只是每個欄位怎麼進 cfg 的做法不一樣。

引句:「        cfg["stability_scenarios"] = raw["stability_scenarios"]」

歸因:未判定。這只是靜態讀碼,沒有跑出行為差異。

## 三問

1. 分層與依賴方向:跟鄰居一致。
   - macrobench 設定層呼叫 e2e 驗證,方向和既有的 `_macrobench_config` 呼叫 `_e2e_cfg_err` 相同。
   - 挑主線走 `_secev_mainline`。
   - 讀工作目錄設定走 `_macrobench_config`,讀提交版走 `_e2e_config_at`,都是重用。
   - 範本腳本 `select()` 呼叫 `lumos("android-e2e", "select", "--repo", root, …)`,形狀和既有的 `lumos("android-e2e", "judge", "--repo", root, "--precheck")` 相同(`scripts/templates/android-e2e-run.sh`),失敗都用 `die((err or out).strip().removeprefix("擋下:"))`。
   - 唯一的偏差是 A1、A2 的路徑守衛,以及 A3 的分派。

2. 命名與錯誤處理:一致。
   - 函式名 `_e2e_*_cmd` 對上 `_e2e_judge_cmd`。
   - 欄位 `features`、`stability_scenarios` 是 snake_case,和 `results_dirs`、`stability_checks` 一致。
   - 環境變數 `LUMOS_STABILITY_SCENARIO`、`LUMOS_E2E_COLLECT` 對上既有的 `LUMOS_STABILITY_*`、`LUMOS_E2E_*`。
   - 擋下一律印「擋下:」到 stderr 回 2;best-effort 的寫入失敗印「提醒:」,這個寫法在 `scripts/lumos` 出現 72 處。
   - 日誌追加用 `_local_ledger_append`、`_ledger_tail_needs_newline`,讀用 `_canary_ledger_rows`,都是既有 helper。

3. 第二種做法:有一個主要的(A1),另外有 A2、A3、A4 三個次要的。
   - 本機總表沒有另起一種 JSONL 寫法,是重用既有追加 helper。
   - 挑主線和讀 JSON 也沒有另寫一套。
   - 成立的第二種做法只有 A1 的捷徑檢查。

## 已驗與未驗

- 已驗,有修前修後對照:
  - A1 的修復效果,也就是紀錄不再寫到專案外。
  - A2 的修前修後行為相同。
  - A3 在修前就存在。
- 沒驗:
  - `tests` 不在被審材料內,沒有核對 binding 的 repair 與 preserve 案例。
  - 範本腳本的實機執行路徑沒跑,只讀了碼。
  - 修補差異裡其他 hunk(`_e2e_keep_old`、效能逾時中止等)只讀過,沒有各自做修前修後對照,所以不主張它們沒有回歸。

不對齊共 4 條,其中 major 1 條

我的臨時目錄已用字面絕對路徑刪除。過程中有一次在自己的臨時目錄裡用了 `目錄/*` 萬用字元清理,沒有碰到別人的檔。
