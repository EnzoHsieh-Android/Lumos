severity: minor

整體判斷:這份修補沒有引入第二種做法,也沒有跨層直呼。有一條 minor,不擋推送。

**逐項對照結果**
- **讀帳一次照編號查表**:整合方向對。`_spec_gate_latest_records` 和 `_nogo_light_window` 原本各自重讀整本帳,現在共用 `_spec_gate_ledger_index`。切行走 `_ledger_lines`,壞行與超深巢狀行只跳過那一行,跟 `_door_for_loop` 的讀法一致。
- **`nogo_rows_sha` 進留痕**:欄位名(`clause_sha`、`inputs_sha`、`nogo_rows_sha`)與規格閘留痕的命名一致。它是新增欄位,不是規則輸入,沒有動 `inputs_sha` 的組成,所以不必 bump 門規則版本。
- **門規則版本與指紋升級**:跟版本 2、3 的升級方式相同。`_DOOR_RULE_VERSION` 改成 4、說明寫進常數註解,`_DOOR_SCAN_FENCED` 以 `scan_fenced=` 併入 `_door_rule_fingerprint`,釘住測試 `t_door_rule_version_pin` 同步改成 `door_rule=4`。
- **`_prov_check`**:只把例外從 OSError 放寬到含 ValueError,既有的處置閘與資安席呼叫端行為不變,新呼叫端共用同一支,沒有另寫一套。
- **`_sh_quote`**:用的是檔內既有的 helper。我 grep 過,沒有殘留未加引號的 `lumos spec-gate {stem}` 提示。
- **入口清 git 環境**:四行放在 `main()` 開頭,全檔沒有逐呼叫的 `GIT_NO_REPLACE_OBJECTS`、`GIT_GRAFT_FILE`、`GIT_DIFF_OPTS`、`GIT_EXTERNAL_DIFF` 殘留。
- **severity 判斷**:`("major", "blocker")` 與檔內其他處(約 12044、16048 行)寫法相同。

severity: minor
blocking: 否 — 這是整併前就存在的分歧,且新舊讀法的篩選條件不同,不是新增的第二套
引句:「審查帳讀一次,照迴圈編號(NFC)分組 {編號: [紀錄…]}(帳的 append 序,含 kind=spec-gate 留痕)。」
對照:file: `scripts/lumos:13688`(`_canary_ledger_scan`:同樣是審查帳依迴圈編號分組,但濾掉 spec-gate 留痕、要求編號是字串、整本先嚴格解碼);另有 file: `scripts/lumos:12804`(`_door_for_loop`)仍自帶一份逐行讀帳迴圈。
判定理由:專案裡已有 `_canary_ledger_scan` 做「讀帳並照編號分組」,新的 `_spec_gate_ledger_index` 是並行的另一份,差別只在要保留 spec-gate 留痕、用 NFC 編號、容忍非 UTF-8。這次其實把原本兩份私有讀法(`_spec_gate_latest_records`、`_nogo_light_window`)併成一份,淨效果是減少分歧。docstring 沒交代為什麼不擴充 `_canary_ledger_scan` 加一個「含留痕」旗標。建議之後讓這幾支讀者共用同一個核心。

severity: minor
blocking: 否 — 後備路徑仍用專案原有的比法,新 helper 範圍小且有明確理由
引句:「兩條路徑是不是同一個檔:先問檔案系統(os.path.samefile;macOS 預設不分大小寫」
對照:file: `scripts/lumos:26803`(處置閘 `_prov_path` 閉包,相對路徑接 repo 根),file: `scripts/lumos:48629`(`Path(d).resolve() != expected`,檔內慣用的路徑比對)。
判定理由:全檔先前沒有 `os.path.samefile`,`_same_file_path` 是第一個。它的理由站得住腳,因為 macOS 大小寫與 NFC/NFD 的差異用字串比會漏。失敗時退回 `nfc(resolve())` 字串比,是專案原有寫法。另外「相對路徑接 repo 根」的邏輯在 `_nogo_snapshot_rows` 的 `_at` 閉包和 `_nogo_review_unbound` 裡的 `q if q.is_absolute() else root / q` 各寫了一份,跟處置閘的 `_prov_path` 是第三份同形寫法。合起來算 minor,不到 major。

最高等級 minor,blocking 0 條。
