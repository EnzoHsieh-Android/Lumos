severity: clean

## 問 1 分層與依賴方向:對齊
- **主程式的位置。** 新碼都放在 `scripts/lumos` 的 macrobench 區塊後面,位置跟 stability 那套相同。`_macrobench_config` 呼叫 `_e2e_cfg_err`,跟它呼叫 `_macrobench_stab_cfg_err` 是同一個形狀(`scripts/lumos:39402` 附近的 diff 區塊)。
- **`_macrobench_mode`。** 它多接 `results_dir`,檢查寫在 `_macrobench_e2e_args_err`,不另開入口。
- **子命令。** `android-e2e judge` 在 `main()` 的分派跟 `cochange` 同型,先比 `args.cmd`、再比子命令鍵。
- **跟既有工具的呼叫關係。**
  - 讀 JSON 走 `_events_depth_ok` 加 `_macrobench_stab_scrub`,對照 `_macrobench_stab_load`(`scripts/lumos:39894`)。
  - JUnit 走 `_secev_tq` 加 `_secev_junit_facts`(`scripts/lumos:8790`、`8802`),不再自己接 `tq.junit` 的例外。
  - 讀某個版本的 `macrobench.json` 走 `_lumos_config_at_ref`,這是原本就有的共用函式。
  - 髒樹判斷走 `_dirty_non_bookkeeping`(`scripts/lumos:20940`)。
  - 讀改寫紀錄用 `_vault_write_lock` 加 `_write_lf`,跟 `_lint_waivers_add`(`scripts/lumos:38618`)同一個形狀。
  - git 呼叫走 `_nodehome_git`。
- **簿記目錄。** `.lumos/e2e-records/` 加進 `_BOOKKEEPING_DIRS`,所有消費者共用這一份清單,沒有另開第二份判準。
- **範本腳本。** 它只透過命令列呼叫 lumos(`macrobench --check-config`、`android-e2e judge --precheck`、`judge`),沒有抄 lumos 的函式,也沒有跨層直呼。這跟 `android-stability-collect.sh` 一致(它一樣用 `LUMOS` 路徑加 `sys.executable` 呼叫)。
- **範本登記。** `_VENDORED_TREE_FILES` 補了新範本,跟相鄰的範本登記方式相同。

## 問 2 命名與錯誤處理:對齊
- **命名。** `_e2e_*` 前綴、`E2E_*` 常數、`(結果, 錯誤訊息)` 回傳形狀,跟 `_macrobench_*` 和 `_lumos_config_at_ref` 的 `(內容, 狀態)` 一致。
- **錯誤輸出。** 錯誤統一用「擋下:…」印到 stderr 並回 2,跟 `_macrobench_mode` 和範本腳本裡原有的 `die()`(`android-stability-collect.sh:30-32`)一致。
- **治理帳。** 這次沒有新寫治理帳,紀錄走 `.lumos/e2e-records/`,所以沒有跟 gate 的帳寫法衝突。
- **範本裡有意不同的兩處,都已寫成圖譜 WHY。**
  - `say()` 取代直接 `print`,而且 stderr 斷了就換成 `/dev/null`,原因記在修補差異的 PITFALL。鄰居 `android-stability-collect.sh:537` 附近的收尾路徑還是直接 `print`,但那不是這份 diff 的範圍。
  - `kill_group` 是先送 TERM、等寬限、再補 KILL(`android-e2e-run.sh` 的 `kill_group`),鄰居是直接 KILL(`android-stability-collect.sh:59`)。有 WHY 說明,語意不同,不算重複規則。
  - 這兩處都屬於「錯誤處理跟鄰居不同、但有出處」。程式裡沒有互指註解,但圖譜 WHY 已記,我不列為不對齊。

## 問 3 第二種做法:沒有
我對照的都是 diff 以外原本就有的函式,不是這份 diff 新寫的。

- **flow 名規則。** 在 lumos 的 `_e2e_flow_name` 和範本的 `accept()` 各有一份。兩邊都有互指註解,測試也有一支對照巢狀路徑和 `./` 開頭,所以不算第二種做法。
- **裝置鎖。** 範本的 `take_lock` 會接手殘鎖,跟 lumos 的 `_excl_lock_try` 不自動接手相反。這是範本獨立 Python 拿不到 lumos 函式的情況,而且有 WHY 與代價說明,不算第二種做法。
- **JUnit、JSON 讀法、git 讀取、讀改寫鎖。** 這幾項上一輪重複自寫的,現在都收回到既有函式。
- **BOM 容忍度。** `_macrobench_config` 用 UTF-8 不收 BOM,`_json_at_ref` 與兩支範本收 BOM。BOM 檔會先被 `--check-config` 擋下,不會走到 judge,所以不影響行為,我沒列為不對齊。

另外一個小地方我沒列入:`_lumos_config_at_ref` 加了 `rel` 參數,但它的 docstring 還寫「讀某個版本的 .lumos/config.json」,是舊敘述,算文件不夠新,不是做法不一致。

不對齊共 0 條,其中 major 0 條

**表態記錄。** `py-external satisfied` 指向 `scripts/scenario_probe.py:1077`,我沒查它。其餘題目是 `na`,沒有 `status=tension`,所以沒有四欄要核對。
