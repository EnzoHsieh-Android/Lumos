severity: minor

我讀了 diff 的 `scripts/lumos` 新碼、測試、文件列表和筆記,逐項對照 `_compose_metrics_mode` 一族與 `_lint_watch_mode`。結構上沒有跨層、沒有第二種做法。有兩條小的不一致。

**問 1:分層與依賴方向:對齊**
- 新碼的位置、接線和呼叫鏈跟鄰居一樣。
  - 放在 `_compose_metrics_mode` 之後、`_lint_watch_mode` 之前,同一段 vault-free 轉接器區。佐證:`scripts/lumos:39355` 附近。
  - `HELP_WHEN` 加一行,位置緊接 `compose-metrics`。佐證:`scripts/lumos:64990`。
  - `sub.add_parser("macrobench")` 的 `--repo`、`--json`、`--update-baseline` 比照 compose-metrics,`dest` 用 `macrobench_repo`,跟 `compose_metrics_repo` 同形。佐證:`scripts/lumos:66067-66072`。
  - 轉接放在 compose-metrics 後面,同樣在 `find_vault` 之前。佐證:`scripts/lumos:66420-66421`。
- 新碼只呼叫既有的 `_secev_num`(`scripts/lumos:8554`)和 `_write_lf`(`scripts/lumos:28446`)。
  - 沒有另寫一套數值判型或寫檔函式。
  - `_write_lf` 是原子寫入,鄰居用裸 `open(..., "w")`(`scripts/lumos:39286`)。這是新碼用了專案已有的 helper,不算第二種做法。
- 新碼把一個大函式拆成多個小函式(`_macrobench_config`、`_macrobench_collect`、`_macrobench_compare` 等),都用 `_macrobench_` 前綴。`_compose_metrics_mode` 是單一大函式,但 `_compose_read_module`、`_compose_diff` 也有拆 helper,拆法對齊。
- 沒有跨層直呼。
- 文件和守衛同步到位。
  - `ARCHITECTURE.md` 三處計數 93 改 94,`SARIF` 葉節點加 `macrobench`。
  - `reference.md` 新增一列,並把兩處計數改 94(`reference.md:118` 的清單含 `macrobench`)。
  - `commands/INDEX.md` 和 `commands/04-自檢與健康.md` 各補一列。
  - 計數守衛 `t_docs_command_count`(`scripts/test_lumos.py:31935`)比對的幾份文件都已改齊,不會擋推送。
- 新增了 `Systems/macrobenchmark-adapter.md` 當家,宣告 `about_code: scripts/lumos`。compose 也是一支獨立的 adapter 節點(`Systems/compose-metrics-adapter.md`),對齊。

**問 2:命名、錯誤處理、日誌:大致對齊,有兩條小差異**
- 設定檔壞掉時,錯誤走 stderr,字首是「擋下:」,rc 為 2。佐證:`scripts/lumos:39264`,新碼的 `_macrobench_mode` 用的是同一個寫法。
- 有退步、沒設定檔都回 rc 0,基準讀不了不覆蓋。rc 語意跟 compose-metrics 一致。
- 函式內 `import json` 的寫法跟鄰居一樣。
- 常數用 `MACROBENCH_*` 前綴,對應 `COMPOSE_RATIO_EPS`。
- 例外處理也一致:`except Exception` 後把原因收進 `failed[]`,不讓例外往上冒。
- 差異見下面 K1、K2。

**問 3:第二種做法與同步:無 major**
- 設定檔載入沒有走共用 helper,而是自己寫 `_macrobench_config`。
  - 這跟 `_compose_metrics_mode`、`_lint_watch_mode` 一樣是在函式內直接讀 JSON。專案裡沒有共用的 `.lumos/*.json` 載入器,所以不算第二種做法。
  - 差別只在新碼回 `(cfg, err)` 二元組,不直接 print。
- 測試用 `_load_lumos_inproc`(`scripts/test_lumos.py:238`)載入模組,是專案現行慣例。`t_compose_parse` 的舊式 `SourceFileLoader` 重載反而是舊寫法。
- `_macrobench_mod()` 只是 `_load_lumos_inproc()` 的一層薄別名,沒有帶來新做法。
- 暫存目錄用 `TemporaryDirectory`,鄰居用 `mkdtemp` 不清。新碼這樣寫比較好,符合清暫存的規矩。

**不一致清單**

K1 ⚠ 跟 compose-metrics 的 `--json` 和人讀輸出形狀不同
- 既有 X:compose-metrics 的 JSON 鍵是 `regressions`、`checked_modules`、`new_modules`、`failed`、`baseline_missing`。
  - `failed` 的每項是 `{name, reason}`。
  - 沒設定檔時,人讀輸出印空字串。
  - 人讀輸出是英文:`N regressions (modules: M)`、`notice: ...`。
- 隱患 Y:兩個同家族的轉接器輸出形狀不同,以後如果像 compose 設計稿 v2 那樣,用排程腳本統一吃這幾個命令的 JSON,得寫兩套解析。
- 這次 Z:macrobench 的鍵是 `checked`、`new`、`missing`、`device_changed`、`listed`、`failed`、`baseline_missing`、`baseline_unreadable`,另加 `configured` 和 `files`。
  - `failed` 的每項是 `{file, reason, kind}`。
  - 沒設定檔時印一句中文說明。
  - 人讀輸出是中文。
  - 這裡我判不準,新碼可能是刻意改成中文白話。
- 不一致 N:1 檔(`scripts/lumos`)。
severity: minor
- blocking: 否
- 引句:「failed.append({"file": rel, "reason": f"讀不了:{e}", "kind": "unreadable"})」
- 佐證:`scripts/lumos:39240`(compose 的 `failed.append({"name": name, "reason": ...})`)

K2 ⚠ 方法論總表沒補這一列
- 既有 X:`docs/methodology/圖譜即合約.md:160-161` 的表把 `lint-watch`、`compose-metrics` 各列一列,寫了何時跑、吃什麼、怎麼放行。compose 的設計稿也把它列進「要同步的文件」。
- 隱患 Y:這張表是各偏科轉接器的總覽,少了 macrobench 就不完整。
- 這次 Z:新增了 `macrobench`,但 diff 沒動這張表,只動了 reference、INDEX、04、ARCHITECTURE。
- 不一致 N:1 檔(`docs/methodology/圖譜即合約.md`)。
- 沒有測試或推送守衛擋這件事。我判不準這張表是否一定要補,所以標 ⚠。
severity: minor
- blocking: 否
- 引句:「SARIF --> ST["sqlfluff-sarif · stylelint-sarif · dart-sarif<br/>compose-metrics · macrobench · lint-check"]」
- 佐證:`docs/methodology/圖譜即合約.md:161`

不對齊共 2 條,其中 major 0 條
