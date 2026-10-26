severity: minor

## 三問的答案

**問 1 分層與依賴方向:對齊。**
- `_e2e_changed_files` 挑主線用 `_secev_mainline`,跟 `_secapr_cmd_verify` 同一套。file: `scripts/lumos:11662`。
- 它讀 git 用 `_nodehome_git`,跟 e2e 這一族原有的 `_e2e_judge_cmd` 的 `rev-parse HEAD` 一樣。file: `scripts/lumos:41187` 附近。
- 讀 HEAD 提交樹的設定走 `_e2e_config_at`,它再走 `_lumos_config_at_ref`。這是原有路徑。
- 讀工作目錄的設定走 `_macrobench_config`,跟 `macrobench --check-config` 同一套驗法。file: `scripts/lumos:39432`。
- 寫紀錄走 `_e2e_record_update`。這條路徑已經有讀改寫鎖,新碼沒有另寫。file: `scripts/lumos:40803`。
- 新函式都落在原有 `_e2e_*` 區塊,依賴方向是範本腳本呼叫 lumos,沒有反向。
- 範本腳本叫 `select` 的方式,跟叫 `judge --precheck` 完全一樣:
  - 都用腳本內既有的 `lumos(...)` 包裝。
  - 都在回傳碼不為 0 時 `die((err or out).strip().removeprefix("擋下:") ...)`。
  - 對照 `scripts/templates/android-e2e-run.sh` 的 `preflight()` 與新增的 `select()`。
- 範本腳本的 `E2E_BENCH_NAME_RE` 與 `E2E_SCENARIO_KEYS` 在兩邊各留一份,另用測試比相等。這跟原有的 `_e2e_flow_name` 與「test_data 那一行」是同一種做法。file: `scripts/lumos:40298`。

**問 2 命名與錯誤處理:對齊。**
- 函式名都用 `_e2e_*` 前綴。
- 設定欄位 `features`、`stability_scenarios` 是 snake_case,跟 `stability_checks`、`visual_threshold` 同風格。`stability_scenarios` 放最外層,跟 `stability` 段並列,位置合理。
- 環境變數 `LUMOS_STABILITY_SCENARIO` 跟 `LUMOS_STABILITY_SETTLE`、`LUMOS_STABILITY_STOP_TIMEOUT` 同前綴。`LUMOS_E2E_COLLECT` 跟 `LUMOS_E2E_LONG_TIMEOUT` 等同前綴。
- 子指令名 `select`、`history` 跟 `judge` 同為小寫單詞。
- `select` 與 `history` 的錯誤處理是 `print("擋下:…", file=sys.stderr)` 加 `return 2`。寫帳失敗只印「提醒:」,不改判定結果。這跟 `_gate_event`、範本腳本的「提醒:」一致。
- 日誌方式:
  - 本機總表現在改走 `_local_ledger_append`,帳尾補換行走 `_ledger_tail_needs_newline`,讀走 `_canary_ledger_rows`。這三支都是既有 helper。
  - 對照 `scripts/lumos:1698`、`:1847`、`:20348`,以及同類用法 `:1835`、`:26881`。

**問 3 有沒有第二種做法:有兩處偏差,結構都在既有模式內。**
- 本機總表追加寫法:修前是自己 `open(p, "a")` 寫(修前 `scripts/lumos:41029`),屬於第二種做法。修後換成共用 helper,已對齊。
- 挑主線、讀 JSON:沒有另寫一套,走 `_secev_mainline` 與 `_macrobench_config`。
- 子指令分派:見 A1。
- 歷史檔路徑字面量重複寫:見 A2。

## A1 android-e2e 子指令分派另搬成獨立函式
severity: minor
blocking: 否
- 對照:`_guard_dispatch` 的 docstring 寫明「其他子指令群分支少、各自已有 try,照舊留在 main() 裡內聯,沒有要全部改成這個形狀」。file: `scripts/lumos:68613`。
- 對照:cochange、home 等其他子指令群都內聯在 `main()`。file: `scripts/lumos:68100` 附近。
- 新的 `_android_e2e_dispatch` 只有 3 個分支,docstring 沒有說明為什麼要獨立。
- 結構是 guard 已有的先例,所以不是新發明,但它違反了 guard 那段文字寫下的「只有 guard 例外」。這個判斷我不確定,標 ⚠ 交編排者:要不要把 guard 的例外條件當成約束。
- 歸因:有證據的原有漏查。
- 修前:`git show 9e21d491:scripts/lumos | grep -n "def _android_e2e_dispatch"` 在 41067 行就有,main 呼叫在 68001 行。
- 修後:`git show 787dd51b:scripts/lumos | grep -n "def _android_e2e_dispatch"` 在 41150 行,main 呼叫在 68094 行。
- 修補只往這個函式加了 `select`、`history` 的分支,沒有新增這個函式。
引句:「def _android_e2e_dispatch(args):」

## A2 本機總表路徑字面量重複,沒有常數
severity: minor
blocking: 否
- 對照:紀錄目錄有常數 `E2E_RECORDS_DIR`,見 file: `scripts/lumos:40270`,並由 `_e2e_record_path` 使用。
- 總表路徑 `.lumos/artifacts/android/history.jsonl` 在寫入端、讀取端與兩處說明文字各寫一次,沒有常數。
- 歸因:有證據的原有漏查。修前 41026 與 41038 行已經是兩處字面量,修後仍是 41102 與 41120 行。
引句:「p = Path(root) / ".lumos" / "artifacts" / "android" / "history.jsonl"」

## 修補三問(對照問 3 的歷史追加)
1. 原問題的修復效果:本機總表追加從自寫 `open("a")` 改成 `_local_ledger_append` 加 `_ledger_tail_needs_newline`。
   - 修前版本:`git show 9e21d491:scripts/lumos` 的 41026 到 41032 行確認是自寫寫法。
   - 修後版本:`git show 787dd51b:scripts/lumos` 的 41106 行確認走共用 helper。
   - 這是靜態對照。我沒有實際執行追加,也沒有跑 `t_android_e2e_history_edges`,所以只能說「寫法已對齊」,不能說「行為已驗」。
2. 相鄰路徑:`_ledger_tail_needs_newline` 的 docstring 與 `_local_ledger_append` 的 docstring 還寫著舊的呼叫端清單(「三支寫入器共用」「只有這三支呼叫」)。
   - 這是文件陳舊,不是行為差異,不列為不對齊。
   - 我沒有逐條驗它們的行為,標未判定。
3. 新發現的同一案例(A1、A2)修前修後結果相同,見上。

**未驗範圍**:
- 我沒有執行任何測試。
- 我沒有核對範本腳本的手寫參數解析與 `argparse` 的行為是否一致。
- 我沒有檢查文件與筆記的文字修正。

不對齊共 2 條,其中 major 0 條
