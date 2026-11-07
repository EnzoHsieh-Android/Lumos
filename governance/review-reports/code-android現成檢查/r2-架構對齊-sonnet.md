severity: major

**① 分層與依賴方向**

依賴方向都對。A1 從 `_lint_android_ci_advisories` 呼叫既有的 `_ci_workflow_texts`(`scripts/lumos:60278`),和 `_detekt_ci_has_typed_task` 呼叫下層讀檔函式同一方向(`scripts/lumos:38952`)。口徑 `batch4_expected_tags` 放進 `catalog_problems`(`configs/ast-grep/kotlin-android/check.py:155`),測試只呼叫它。lumos 沒有反過來 import check.py,沒有跨層直呼。

`_android_build_texts` 這輪確實改成沿用 `_stack_scan_skip`(`scripts/lumos:33926`)和 `_kt_strip_comments`(`scripts/lumos:38147`),這兩項屬實。

F1、F2 是測試裡的重寫,不是層次問題,放在第③問。

**② 命名與錯誤處理**

- 提醒標法對齊。A3 的 `[kt 第 N 條] A3:` 對應 detekt 逐條提醒的 `[{label} 第 {idx} 條] {c}:`(`scripts/lumos:39203-39205`)。序號都用 `enumerate(…, 1)`,也都不回顯命令內容。`[CI] A1:`、`[CI] A2:` 對應既有的 `[CI] T4:`(`scripts/lumos:39207`)。
- 健檢那則的 20 條上限(`_ashow`)和 detekt 的 `_dshow` 同形(`scripts/lumos:4172-4175`)。
- 輸出順序用 `_ANDROID_ADVICE_ORDER` 排序,和 `_DETEKT_ADVICE_ORDER` 一致。
- 錯誤處理對齊:讀檔失敗就跳過,和 `_ci_workflow_texts` 一樣。具名管道只開一般檔,這是 `_android_build_texts` 自己的守衛,沒有既有對照。
- 測試載入 check.py 的寫法不一致,見 F2、F4。

**③ 第二種做法**

F1
severity: major
blocking: 是
引句:「        return m._android_ci_has_lint_task([[m._ci_strip_comment(ln) for ln in tx.split("\n") if not ln.lstrip().startswith("#")]」
- 測試的 `has()` 把「整行註解拿掉、再切行尾註解」重寫了一遍。既有的 `_ci_workflow_texts` 正是這個邏輯,docstring 寫明「哪些算註解只有一份」(`scripts/lumos:60278-60291`)。
- 產品碼這輪已改成沿用,測試卻另寫了一份,而且測的正是 A1。
- `_ci_workflow_texts` 吃的是路徑清單,測試只要寫暫存檔再呼叫它就行。
- 現狀的風險:`_ci_workflow_texts` 以後改了「哪些算註解」,測試不會跟著紅。
- 對照:`scripts/lumos:60264`(`_ci_strip_comment`)、`scripts/lumos:60278`(`_ci_workflow_texts`)。

F2
severity: major
blocking: 是
引句:「def _kt_pack_check_module():」
- 新增了第二個載入 check.py 的 helper。既有的 `_ktpack()` 已經做了同一件事(`scripts/test_lumos.py:125451`),同檔更早定義,新 helper 在 `scripts/test_lumos.py:126503`。
- 兩者的路徑算法不同:既有的是 `Path(GRAPHCTL).resolve().parents[1]`,新的是 `Path(__file__).resolve().parent.parent`。
- 模組名也不同:`ktpack_check` 對 `kt_pack_check`。
- 既有的 `_ktpack(copy=True)` 另外提供「複製後改壞」用的複本,新 helper 沒有。
- 這正是 r1 架構席點名的「不在測試裡另立一套」,這輪只是換了個地方另立。

F3
severity: minor
blocking: 否
引句:「def _ci_config_texts(repo_root, github_only=False):」
- 這輪新拆出 `_ci_config_paths`,但 `_ci_config_texts` 仍留著,內容是自己的 `read_text(errors="replace")` 加 `try/except OSError`。
- 它只給 T4 的 `_detekt_ci_has_typed_task` 用(`scripts/lumos:38952`),讀的是原文,沒去註解。
- 同一個功能裡有兩條讀 CI 檔的路:A1 走 `_ci_workflow_texts`(去註解),T4 走 `_ci_config_texts`(不去)。
- A1 的 docstring 卻寫「跟 T4 找 detekt<變體> 同一個形狀」。註解行裡寫的 detektDebug 會讓 T4 判已接,A1 則不會,兩邊口徑不同。
- 結構上不致命,因為 T4 是更早的程式。但這個 diff 動到了它,又沒收斂。
- `_ci_config_paths` 另列 `.yml/.yaml` 並加 `is_file()`,和既有四處 `sorted(list(wf.glob("*.yml")) + list(wf.glob("*.yaml")))` 並存(`scripts/lumos:48456`、`59583`、`59688`、`60173`)。
- 它多出 `_CI_OTHER_CONFIG_FILES`,所以不算純重複,只算又多一個列檔入口。⚠ 判不準,交編排者。

F4
severity: minor
blocking: 否
引句:「    for line in cmd.replace("\\\n", " ").split("\n"):」
- `_detekt_plugin_values` 重用了 `_detekt_split_segments`、`_detekt_strip_prefix`、`_detekt_cli_args` 這些基本件,這點屬實。
- 但「續行換空白、逐行拆段、剝前綴、`sh -c` 遞迴 depth 限 0」這個走訪骨架,是 `_detekt_command_codes` 加 `_detekt_segment_codes` 的第三份複本(`scripts/lumos:39166`、`39113`)。
- 日後 detekt 判定新增包裝詞或 shell 遞迴規則時,要改兩處;「兩邊看到同樣的詞」只在今天成立。
- 比 r1 的 `shlex.split` 自寫版好很多,所以只列 minor。⚠ 判不準,交編排者:可抽共用走訪器,也可接受為已沿用基本件。

F5
severity: minor
blocking: 否
引句:「        ck.CATALOG = tmp」
- 測試用手動換掉 `ck.CATALOG` 再還原的方式做變異。
- 既有做法是 `_ktpack(copy=True)` 建複本,再改 `m.CATALOG`、`m.HERE`(`scripts/test_lumos.py:125462-125468`)。
- 另一處既有測試直接用 `mc.CATALOG.write_text` 寫複本(`scripts/test_lumos.py:125674`)。
- 這是第三種寫法,和 F2 同根。

check.py 新口徑與既有欄位檢查同形:同樣用 `problems.append((rid, 訊息))`,同樣先判欄位數再判內容(`configs/ast-grep/kotlin-android/check.py:181-206`)。新增的 `B4_*` 常數沒有底線,但同檔 `STOP_TRIGGERS` 也是公開名,不算不對齊。

**結論**

不對齊共 5 條,其中會擋的 2 條。
