severity: major

要先說明:這次修補沒有新增「第二種做法」。分派函式、本機總表的追加寫法、挑主線、讀設定,在修前版本 787dd51b 就已經是現在的樣子。下面兩條都是修前就有的漏查,修補只在上面加碼。

**驗證設定**
- 修前與修後的 `scripts/lumos` 都是用 `git -C <e2e-docs> show <sha>:scripts/lumos` 取出,放在我自己的暫存目錄,沒有在 e2e-docs 裡動版本。
- 載入方式是 `python3.14 -I` 用 SourceFileLoader 載入該檔,探針印出了載入路徑,確認載到的是 before 或 after 那份。
- e2e-docs 的 HEAD 在審查時是 4b056532,所以引用的行號都對修後版本。

## A1 功能對照表的 paths 另寫了一套「相對路徑」檢查,沒走同一族既有的 `_e2e_relpath_err`
severity: major
blocking: 是

對照:file: `scripts/lumos:40277`(`_e2e_relpath_err`,app_dirs、exclude、flows、apk 共用。擋反斜線、`C:\`、`/` 開頭、`..`、`.`)。
新碼在 `scripts/lumos:40448-40457`(`_e2e_feature_head_err`),自己用 `Path(x).is_absolute()` 加 `..`,修補又再加一道 `posixpath.normpath` 比對。
引句:「bad = next((x for x in f["paths"] if Path(x).is_absolute() or ".." in Path(x).parts), None)」

失敗場景是同一個規則兩套寫法,結論不一致。同一個字串在 app_dirs 被擋,在 features.paths 卻收下。
- 例如 `app\src`、`C:\x` 這類寫法,`--changed` 之後永遠對不到任何改到的檔。
- 反方向也不一致:`app//src` 在 app_dirs 照收,在 features.paths 被擋。

歸因:有證據的原有漏查。修前 787dd51b 的 40451 行就已經有這套自寫檢查。修補沒有改接 `_e2e_relpath_err`,而是在自寫那套上再加 normpath 比對,所以兩套的差異變多了。

同一批輸入、兩版的結果(`_e2e_feature_head_err` 對 `_e2e_relpath_err`):

| 輸入 | 修前 features.paths | 修前 app_dirs | 修後 features.paths | 修後 app_dirs |
|---|---|---|---|---|
| `app\src` | 收 | 擋 | 收 | 擋 |
| `C:\x` | 收 | 擋 | 收 | 擋 |
| `.` | 收 | 擋 | 擋 | 擋 |
| `app//src` | 收 | 收 | 擋 | 收 |
| `/abs`、`../x`、`app/../x` | 擋 | 擋 | 擋 | 擋 |
| `app/src`、`./app` | 收 | 收 | 收 | 收 |

- 修補讓 `.` 在兩邊一致,這是正向的改善。
- 反斜線與磁碟機寫法的差異,修前修後都在。

## A2 stability_scenarios 的 warmup、cycles 整數判斷沒用同一族既有的 `_secev_int`
severity: minor
blocking: 否

對照:file: `scripts/lumos:39476`(stability 段用 `_secev_int(st.get(k)) and 1 <= … <= MACROBENCH_MAX_CYCLES`),`_secev_int` 定義在 `scripts/lumos:8559`。
新碼在 `scripts/lumos:40399`。
引句:「if any(k in v and (not isinstance(v[k], int) or isinstance(v[k], bool) or not 1 <= v[k] <= MACROBENCH_MAX_CYCLES) for k in E2E_SCENARIO_KEYS[2:]):」

這裡的判斷結果跟 `_secev_int` 等價,因為 JSON 不會產生 int 的子類別,所以只是命名與重用不一致,結構是對的。同族的 `_e2e_record_err` 在 40589 行也用 `_secev_int`。

歸因:有證據的原有漏查。修前 40398 行就是同一寫法,修補沒碰。

## 三問

**1. 分層與依賴方向:一致。**
- 新碼都在 `_e2e_*` 這一族,和 `_e2e_judge_cmd`、`_e2e_precheck` 同層。
- 選主線走 `_secev_mainline`(`scripts/lumos:40849`,和 11690 行的 `_secev_mainline(root, "HEAD")` 同用法)。
- 讀設定走 `_macrobench_config`(`_e2e_worktree_e2e` 內),讀提交版走 `_e2e_config_at`。
- 讀 git 走 `_nodehome_git`,判髒走 `_dirty_non_bookkeeping`。
- 範本腳本呼叫 lumos 的寫法和既有的 `--precheck` 一樣:都是 `lumos("android-e2e", …)`,失敗時 `die((err or out).strip().removeprefix("擋下:") …)`。
- 驗證:兩版 `android-e2e select` 對空目錄都回 2 並印「擋下:工作目錄沒有 .lumos/macrobench.json」,結果相同。

**2. 命名與錯誤處理:一致,只有 A2 這一處小差異。**
- 函式名都是 `_e2e_*`。
- 設定欄位 `features`、`stability_scenarios` 放在 macrobench.json,和 `stability` 並列。
- 環境變數 `LUMOS_STABILITY_SCENARIO` 沿用 `LUMOS_STABILITY_*` 前綴。範本腳本用環境變數傳功能性參數給子腳本,既有的 `visual-check.sh` 也是這樣做(`env=dict(env, THRESHOLD=…)`)。
- 錯誤一律印「擋下:…」到 stderr 並回 2。
- 兩版 `history --last 0` 都回「擋下:--last 要是正整數」和 rc 2;`history` 對空目錄回 0,結果相同。
- 按功能跑寫不進正式紀錄時印「提醒:」不改回傳碼,這是有意的,不算不一致。

**3. 第二種做法:只有 A1。**
- 本機總表 history.jsonl 的追加走 `_local_ledger_append` 加 `_ledger_tail_needs_newline`(`scripts/lumos:41146` 對 1970 行,兩支都是既有的)。
- 讀總表走 `_canary_ledger_rows(errors="replace")`,沒有另寫逐行 JSON 讀法。
- 兩版結構都一樣(`_local_ledger_append(` 都是 5 處)。
- 子指令分派 `_android_e2e_dispatch` 是現有 `_guard_dispatch` 以外的另一種掛法,在修前就存在。修補只在 `_guard_dispatch` 的說明裡登記了這個例外(`scripts/lumos:68660`),我沒把它列成 finding。登記只寫了「審查要求」,沒寫為什麼要分出來,若要追理由得去問作者。
- 「改到哪些檔」的 `_e2e_changed_files` 是這支檔裡第 N 個列改動檔的 helper,但它要合併「對主線分岔點的差異、HEAD 之後未提交的改動、沒追蹤的新檔」三塊。同檔其他同類 helper 沒有現成能做這件事的,我不算它是第二種做法。

**已驗與未驗**
- 已驗,且修前修後結果相同:`select`、`history` 的錯誤路徑和回傳碼。
- 已驗修補效果:A1 表格裡 `.` 與 `app//src` 的行為變化。
- 未驗:binding 的 cases 裡那些 `t_android_e2e_*` 測試,沒有重跑。我這一席只看一致性,沒有重跑這些測試。這是未判定,不是已確認。
- 未驗:範本腳本的真機流程,沒有實機環境。
- 未驗:history 單行長度超過 4096 位元組時,它和 `_gate_event_fit` 的上限做法是否一致。我判斷這是本機單人帳,沒有往下查。

派工單裡提到的鎖檔 `…673f0.json.warming` 在檢查時已不存在,所以沒有刪任何鎖。我的暫存目錄已用字面絕對路徑刪除。

不對齊共 2 條,其中 major 1 條
