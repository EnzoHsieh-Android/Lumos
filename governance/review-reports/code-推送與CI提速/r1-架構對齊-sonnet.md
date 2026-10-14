severity: minor

整體結構對得上既有做法:沒有發現第二套快取、第二套原子寫入或第二個資料檔位置。下面 3 條不對齊都是 minor。固定席節點在最後逐條判。

## 問 1:分層與依賴方向

對齊的部分:
- 執行器 `test_lumos.py` 不 import `scripts/lumos`,自己用 `Path(GRAPHCTL).resolve().parent.parent` 定位檔案。既有快取也是這樣定位:file: `scripts/test_lumos.py:39483`。
- 耗時表放 `governance/`,進版控並列入 `_BOOKKEEPING_FILES`。這跟 `governance/anchor-baseline.json` 的位置和簿記待遇一致:file: `scripts/lumos:29377`。
- 子指令只由 `lumos` 改寫資料檔,執行器只讀,方向沒有反過來。
- `.lumos/test-durations-run*.json` 這份暫存只在來源 repo 寫(`_is_src` 判斷),跟 `test-cache*.json` 的條件相同:file: `scripts/test_lumos.py:39482`。檔名也沿用同一套 `shard.replace('/', 'of')`:file: `scripts/test_lumos.py:39484`。

severity: minor
blocking: 否
問題 1(⚠ 判不準是不是缺陷):耗時表路徑有兩份來源。`lumos` 這邊有常數 `_TEST_DURATIONS_REL`,執行器那邊的 `_durations_table_path()` 自己手寫 `"governance" / "test-durations.json"`。既有的 `_ANCHOR_BASELINE_REL` 只有 `lumos` 一個消費者:file: `scripts/lumos:26412`,所以沒有這個問題。新測試只驗了「在簿記檔清單裡」,沒驗兩邊路徑相等。其中一邊改名時,`refresh` 會寫到執行器不讀的地方,執行器就靜默退回輪流分。
引句:「return Path(GRAPHCTL).resolve().parent.parent / "governance" / "test-durations.json"」

## 問 2:命名與錯誤處理

對齊的部分:
- 新子指令掛法同 `note-audit prepare` 這類巢狀指令:`HELP_WHEN` 同時列了 `test-durations` 和 `test-durations refresh`,用 `add_subparsers(required=True)`,跟 `testmap` 一樣:file: `scripts/lumos:54855`。
- 錯誤訊息前綴 `擋下:`、rc2 對應參數或環境錯,跟 `push-range`、`push-summary` 一致:file: `scripts/lumos:48590`。
- 暫存檔名 `.lumos-tmp` 加 `os.replace`,跟 `cmd_testmap_build` 和 test-cache 的寫法同款:file: `scripts/lumos:45950`。

severity: minor
blocking: 否
問題 2:`cmd_test_durations_refresh` 寫入失敗時印 `寫不進耗時表:…`(無 `擋下:` 前綴),沒有清掉 `.lumos-tmp`。`cmd_testmap_build` 失敗時用 `die("寫檔失敗: …")` 並且會 `tmp.unlink()`:file: `scripts/lumos:45960`。這裡 `os.replace` 失敗後,殘留的暫存檔會留在 `governance/`。
引句:「print(f"寫不進耗時表:{e}", file=sys.stderr)」

severity: minor
blocking: 否
問題 3:同一份耗時表,兩邊對壞資料的處理不同。執行器遇到壞表就 rc2 讓每一份都擋下,`refresh` 遇到壞舊表卻靜默從空表重來,會把表裡已有的條目全部覆蓋掉。這是作者刻意的設計(docstring 有寫)。既有 `testmap` 沒有可比的前例,所以只標不一致。

## 問 3:第二種做法

沒有第二種做法:
- 快取:實測秒數沿用 `.lumos/` 加 `.lumos-tmp` 加 `os.replace` 加 `_is_src` 條件。沒有開新目錄,也沒有改用 `~/.cache/lumos`(`_home_cache_write`)或 `atomic_write_verify`。
- 資料檔位置:`governance/*.json`,跟 `anchor-baseline.json` 同層。
- 子指令派發:`if args.cmd == "test-durations"` 與 `push-summary`、`push-range` 同形。

severity: minor
blocking: 否
問題 4(⚠ 判不準是不是缺陷):耗時值的驗證寫了兩套,規則同義但寫法不同。
- 執行器端:`isinstance … not _md.isfinite(v) or v < 0`,壞值就丟 `ValueError`。
- `lumos` 端:`v >= 0 and v == v and v != float("inf")`,另一處是 `0 <= v < float("inf")`,壞值就丟掉那一筆。
`lumos` 端自己也有兩種寫法。若一邊日後收緊(例如加上限),另一邊不會跟著變。
引句:「if isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v < float("inf"):」

## 固定席節點逐條判

- `測試假綠形態`:新測試 `t_runner_shard_by_duration` 和 `t_test_durations_refresh` 都有 `★前置★` 斷言,沿用該 INVARIANT 的寫法,不影響。
- `lumos-cli-lifecycle`、`lumos-cli-read`:這份改動沒碰 re-inject 和 search,不影響。
- `guard-kill`、`design-loop`:這份改動沒碰 guard kill 和處置閘,不影響。
- `pitfalls-code-loop`、`reversibility-governance-ledger`、`loop-convergence-recording`:耗時表加進 `_BOOKKEEPING_FILES` 是沿用既有的單一來源機制,不是新的第二套。

不對齊共 4 條,其中 major 0 條
