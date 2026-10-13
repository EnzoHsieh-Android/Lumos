severity: minor

### 1. 並行設定值另寫一支手刻的 config 讀取,沒走既有讀法
severity: minor
blocking: 否
引句:「cfg = json.loads((Path(repo_root) / ".lumos" / "config.json").read_text(encoding="utf-8"))」
file: `scripts/lumos:5836`(`load_platforms` 同一次 `_run_bound_tests` 開頭已解析同一個 config.json,且收 `cfg` 參數可重用)
- `_run_bound_tests` 一進來就呼叫 `load_platforms(repo_root)`(`scripts/lumos:5830` 一帶),它已讀過並解析同一份 `.lumos/config.json`。`_bound_tests_parallel` 又自己讀一次。
- 專案裡 note_lint、note_shape 的做法是:`_note_shape_config`(`scripts/lumos:30562`)和 note_lint 讀取(`scripts/lumos:6801`)把警告收進 `warnings` 清單回給呼叫端,由呼叫端統一印。這裡改成在深層 helper 直接 `print(..., file=sys.stderr)`。
- 這不算新做法,因為 `load_platforms`(`scripts/lumos:5842`)和 `_config_has_top_run_cmd`(`scripts/lumos:48304` 一帶)本來就有同樣的手刻讀取加直接印提醒。
- 不一致的點:同一個 config 在同一個函式裡被讀兩次。計劃自己寫的「設定警告每次呼叫印一次,同一次操作可能印好幾次」,就是直接印、沒有收集去重造成的。
- 這屬於同一個專案裡兩種都有的做法,所以只標 minor。

### 2. 記帳欄位 `secs_kind` 只寫在 `secs` 有值時,命名與寫入條件跟既有的 `calc_secs` 風格不同
severity: minor
blocking: 否
引句:「_rec["secs_kind"] = "wall"」
file: `scripts/lumos:47887`(`_bound_tests_log` 既有的 `secs` 與 `calc_secs` 是兩個平行的數值欄位,各自獨立判斷 `is not None`)
- 既有慣例是「欄位名直接說這個秒數量的是哪段」:`secs` 是跑測試那段,`calc_secs` 是算波及那段(docstring 在 `scripts/lumos:47895`)。新增的 `secs_kind` 是一個旁掛的列舉欄位,而且是無條件寫死 `"wall"`。
- 結構上沒錯,舊帳沒這欄就是相加值。
- 但記帳消費端(`scripts/lumos:8707` 的 `_STATS_NODE_SEMANTICS` 一帶)沒有對應處理。
- 判不準這算不算命名不一致,標 ⚠。理由:新欄位的格式是首創,沒有同類欄位可對照。

不對齊共 2 條,其中 major 0 條。

---

三問逐問

**1. 分層與依賴方向**
- 沒有跨層直呼。`_run_bound_tests` 仍是規格閘(`scripts/lumos:7661` 的 `_spec_gate_judge_items`)、修正關卡與推送前閘共用的單一入口。
- 並行只加在這支函式內部,呼叫端與回傳形狀(`results, err` 與 `tails`)不變。
- 每支仍走既有的 `_kill_run`(`scripts/lumos:17175`),沒有另寫一份子程序殺掉的做法。
- 牆上時間 `_wall` 在 `_bound_tests_check` 層量,沒有塞進 `_run_bound_tests`。分層乾淨。

**2. 命名與錯誤處理**
- 提醒前綴「提醒:」與 stderr 寫法跟 `scripts/lumos:5842` 一致。
- 讀不到設定時回 1,與 `_config_has_top_run_cmd`「讀不到當沒有」同一個容錯方向。
- 執行緒例外:worker 用 `except BaseException` 收進 `errs`,再由主流程重丟。專案裡 `scripts/lumos:17134` 與 `scripts/lumos:19494` 已有 `except BaseException` 的先例。
- 主流程輪詢 0.1 秒是新寫法。專案其他等待用 `deadline` 加 `time.monotonic()`(例如 `scripts/lumos:28430`),但這裡不是等逾時,是等 worker 結束,所以不能直接對照。
- 時間量測用 `_time.time()`,與 `_kill_run` 及 `calc_secs` 同款,一致。
- python-idioms 條款以 asyncio 為主,沒有直接規範 threading daemon,所以沒有可引用的條款。

**3. 第二種做法**
- `Grep threading|Thread(|queue|concurrent|daemon=|ThreadPool` 在 `scripts/lumos` 只命中這份 diff 自己(`scripts/lumos:48193` 到 `48218`),其餘命中是字串樣式表。
- 專案內沒有既有的執行緒 helper 可重用。專案已有的並行是程序層級的 `--shard`,在 `scripts/test_lumos.py`(`t_prepush_falls_back_when_runner_lacks_shard`)。
- 所以這是專案第一份行程內執行緒並行,不是「第二種做法」。計劃的 PRIOR-ART 有交代取捨。
- 測試側:`_bt_parallel_fixture` 是為了 in-proc 呼叫 `_run_bound_tests` 而另建,沒有重用 `_mk_bound_tests_repo`。後者是完整 git repo 加筆記,比這裡需要的重得多。專案裡沒有現成的輕量 in-proc 夾具(Grep `_run_bound_tests(` 在測試檔只有這份 diff 的三處呼叫),所以不算重複。
- 一致處:其他有跑 `code-loop check` 的測試是「`_mk_bound_tests_repo` 加子程序」。`t_bound_tests_secs_is_wall_time` 也走這條,對齊。
- 一致處:`t_bound_tests_*` 以 `print("  ✓ …")` 收尾,這份新測試也照做。
- 一致處:清理用 `pgrep -f <自己的暫存目錄>`,範圍限定在自己的目錄。

總結:最高等級 minor
