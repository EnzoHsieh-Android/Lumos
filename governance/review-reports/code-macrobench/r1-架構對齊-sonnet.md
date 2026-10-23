severity: minor

審查範圍:`scripts/lumos` 的 `_macrobench_*` 一族、argparse 與 dispatch、HELP_WHEN,以及 `scripts/test_lumos.py` 的 `t_macrobench_*`。筆記與結果檔不在本席的結構題範圍內。

**問 1 分層與依賴方向:對齊**
- 放置位置對齊。新碼緊貼在 `_compose_metrics_mode` 之後、`_lint_watch_mode` 之前(diff 的 `scripts/lumos` hunk,對照 `scripts/lumos:39173`、`scripts/lumos:39620`),同樣是 vault-free 的單檔子指令。
- 註冊與分派對齊。`sub.add_parser("macrobench")` 的 `--repo` / `--json` / `--update-baseline` 比照 `compose-metrics`(`main()` 裡該段);`main()` 的 `if args.cmd == "macrobench": return _macrobench_mode(...)` 跟 `compose-metrics` 並排。`HELP_WHEN` 也補了一行。
- 依賴方向沒有跨層。新碼只呼叫既有的低層原語 `_secev_num`(`scripts/lumos:8554`,外來 JSON 數值檢查,bool 不算)和 `_write_lf`(`scripts/lumos:28446`,原子寫入),沒有反向呼叫,也沒有繞過 vault 或 UI 層。
- 結構上比鄰居更整齊。鄰居是一支約 300 行的 `_compose_metrics_mode`,新碼拆成 `config` / `read` / `collect` / `compare` / `load_baseline` / `update` / `print` 小函式,職責同樣落在「讀檔、比基準、印」,不算第二套分層。

**問 2 命名與錯誤處理:大致對齊,有兩處小不一致**
- 對齊的部分:
  - 函式前綴 `_macrobench_*` 對應 `_compose_*`,模式入口叫 `_macrobench_mode`,對應 `_compose_metrics_mode`。
  - rc 語意相同:設定檔壞了回 2,並印 `擋下:…` 到 stderr(`scripts/lumos:39193` 一帶);有退步或基準缺失回 0。
  - 沒有設定檔時回 0。基準讀不了時不覆寫。`--update-baseline` 在零解析時不寫。
  - 讀不了的檔進 `failed` 清單而不是中斷,也和鄰居一致。
  - 日誌方式一致,都是 `print`,沒有引入 logging。
- A1:沒有設定檔的行為跟鄰居不同。鄰居在 `--json` 時印空形狀,非 json 時印空字串(`scripts/lumos:39179` 起的那段 `if not cfg_path.exists()`)。新碼非 json 時印一句說明「這個專案沒接 …」,`--json` 時印 `configured=False`,多了鄰居沒有的鍵。
- A2:JSON 輸出的鍵名不一樣。鄰居用 `checked_modules` / `new_modules`,新碼用 `checked` / `new` / `missing` / `device_changed` / `listed`。兩者的領域單位本來就不同(模組對情境),不算結構問題,但消費端要認兩套形狀。
- 補充觀察:鄰居寫基準用裸 `open` 加 `json.dump`(`scripts/lumos:39309` 一帶),新碼用 `_write_lf`。新碼才是專案規範的寫法(`_write_lf` docstring 寫明是「vault 唯一寫入原語」),所以這是新碼比鄰居更對,不列為不對齊。

**問 3 第二種做法:沒有引入,測試端有一處重複**
- 沒有新依賴、新 HTTP client 或新狀態管理。JSON 讀寫用標準庫,和全檔一致。數值檢查用既有 `_secev_num`,沒有自創。原子寫入用既有 `_write_lf`,也沒有自寫第二套。
- A3(測試):`t_macrobench_*` 新增了 `_macrobench_mod()`,自己用 `importlib` 加 `SourceFileLoader` 載入 `scripts/lumos`。但 `scripts/test_lumos.py:238` 已經有 `_load_lumos_inproc()`,是帶快取、docstring 明寫給單元釘用的標準載入器。
  - 前例:該檔還有 `_load_lumos_module`(688)、`_import_lumos`(8104)、`_load_lumos`(12912)、`_load_lumos_mod`(23890)等多份同功能載入器。新增第 5 份屬於沿用「各自複製」的慣例,沒有創新。
  - 不過鄰居 `t_compose_metrics_cli` 走的是 subprocess,新單元釘直接 import 是專案內已有的兩種做法之一,不構成新做法。
  - 後果是每次呼叫 `_macrobench_mod()` 都重新執行整個 `scripts/lumos` 模組(8 處呼叫),比用快取單例慢,但不改變行為。

**Findings**

A1 沒有設定檔時的輸出形狀跟鄰居不一致
severity: minor
blocking: 否
引句:「print("這個專案沒接 Macrobenchmark 退步提醒(沒有 .lumos/macrobench.json),沒有東西可比。")」
佐證:``file: `scripts/lumos:39179` ``(鄰居缺設定檔時非 json 印空字串)

A2 JSON 欄位命名自成一套,和 `compose-metrics` 的 `checked_modules` / `new_modules` 不同
severity: minor
blocking: 否
引句:「print(json.dumps(dict(res, configured=True, files=n_files), ensure_ascii=False))」
佐證:``file: `scripts/lumos:39173` ``(鄰居回傳的鍵集合)

A3 測試新增自己的模組載入器,專案已有快取版的 `_load_lumos_inproc`
severity: minor
blocking: 否
引句:「spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))」
佐證:``file: `scripts/test_lumos.py:238` ``

**表態記錄反駁**:本席只看結構一致性,表態記錄的 py-* 題都和結構無關,沒有可反駁的宣稱。`_macrobench_collect` 對結果目錄用 `rglob`,沒有 async 或熱迴圈,與記錄的 `na` 一致。

不對齊共 3 條,其中 major 0 條
