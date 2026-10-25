severity: major

我只讀了 r2-snapshot.patch、r2-repair.patch 和 repo 裡的鄰居函式,沒讀 r1 開頭的任何檔。表態記錄的 py-external 答 satisfied,另有一題未觸發;兩者都沒有 status=tension,沒有四欄要查。我也沒跑測試,只比對程式。

## 問 1 分層與依賴方向:對齊

- **位置**:`_e2e_*` 放在 `_macrobench_mode` 後面、`_lint_watch_mode` 前面,同一個 macrobench 區段。入口走 `main()` 的 subparser,`dest="e2ecmd"`,參數名用 `e2e_` 前綴,跟 `cochange` 的 `cccmd` 和 `coch_*` 同形(`scripts/lumos:67558` 一帶)。
- **呼叫方向**:`_macrobench_config` 呼叫 `_e2e_cfg_err`,對照 `_macrobench_stab_cfg_err`。`_macrobench_mode` 呼叫 `_macrobench_e2e_args_err`,再呼叫 `_e2e_thresholds_err`。`_e2e_judge_cmd` 呼叫 `_e2e_precheck`、`_e2e_config_at`、`_e2e_fingerprint`、`_e2e_evaluate`、`_e2e_record_update`。沒有 `_macrobench_*` 反過來呼叫 judge 內部,也沒有跨層直呼。
- **範本腳本**:只經命令列呼叫 `lumos macrobench` 和 `lumos android-e2e judge`(`android-e2e-run.sh` 的 `load_config`、`preflight`、`judge`)。這跟鄰居 `android-stability-collect.sh` 的 `load_config` 一樣,不 import lumos。
- **共用基礎件都用既有的**:
  - 讀 JSON 限深加清洗:`_events_depth_ok` 加 `_macrobench_stab_scrub`,同 `_macrobench_stab_load`(`scripts/lumos:39894`)。
  - 工作目錄髒不髒:`_dirty_non_bookkeeping`(`scripts/lumos:20940`)。
  - 讀改寫鎖:`_vault_write_lock(p)` 加 `_write_lf`,同 `_lint_waivers_add`(`scripts/lumos:38618`)。
  - git 呼叫:`_nodehome_git`。
  - `_BOOKKEEPING_DIRS` 補了 `.lumos/e2e-records/`。
  - 範本登記進 `_VENDORED_TREE_FILES`。

## 問 2 命名與錯誤處理:大致對齊,有 2 條 minor

- **對齊的部分**:
  - 驗證函式回「錯誤訊息或 None」,載入函式回 `(值, 錯誤訊息)`,對照 `_macrobench_stab_cfg_err` 和 `_macrobench_stab_load`。
  - 擋下一律印 `擋下:…` 並回 rc 2;judge 的 rc 0/1/2 在 docstring 寫明。
  - 範本的 `die()` 印 `擋下:` 並 exit 2,跟收集腳本一樣。
  - 中斷收尾用同一套(`Terminated`、`stop_listening`、`on_term`、`on_int`、`GROUPS`)。
  - 檢查 run-id、檢查 `check-ignore`、用 `-P` 並拿掉 `PYTHONPATH`、`Steps.save` 的暫存檔加 `os.replace`,都跟鄰居同形。
  - 時間格式 `now().astimezone().isoformat(timespec="seconds")`,是專案裡最常見的寫法,例如 `scripts/lumos:1601`。
  - 測試的 `_e2e_tgit` 和 `_e2e_isolated_env`:專案本來就每個功能各有一支 git 小幫手(`_mp_git`、`_nh_git`、`_kr_git`、`_fc_git`),所以這不算新做法。
- **不對齊**:見 A2 和 A3。

## 問 3 第二種做法:A1 是第二種(major),另有 2 條 minor

我逐一確認過,下列函式都不是這份 diff 新寫的:`_json_at_ref`(`scripts/lumos:60175`)、`_lumos_config_at_ref`(`scripts/lumos:54711`)、`_secev_junit_facts`(`scripts/lumos:8802`)、`_nodehome_list`(`scripts/lumos:41076`)。

## A1 讀「某個提交裡的 JSON,並分辨『檔不在』與『檔在但讀不懂』」另寫了一套
severity: major
blocking: 是
引句:「raw = _nodehome_git(root, "cat-file", "-p", f"{rev}:.lumos/macrobench.json", timeout=60)」
file: `scripts/lumos:60175`(`_json_at_ref`)、`scripts/lumos:54711`(`_lumos_config_at_ref`)

專案已有 `_json_at_ref(root, ref, rel, strict=)` 讀某版 JSON。它的狀態版 `_lumos_config_at_ref` 回 ok / missing / unreadable / git-failed,先讀、再用 `cat-file -e` 分辨「檔在但壞」和「沒有」。`_lumos_config_at_ref` 的 docstring 還寫了它是代碼審 r2 架構對齊席要求「兩處各自內嵌『先讀、再 cat-file 分辨』」收成共用的。

`_e2e_config_at` 是同一套邏輯的第三份:`cat-file -p`、失敗後 `cat-file -e` 分辨、嚴格 UTF-8、不是物件就算壞。它跟既有版本的差別只有兩點:不容許 BOM,錯誤回中文訊息而不是狀態碼。

不容許 BOM 是故意對齊 `_macrobench_config`,所以這是有理由的偏離。但可以用 `_json_at_ref(..., strict=True)` 的結果,加 `cat-file -e` 分辨,而不是整段重寫。判不準的是「不收 BOM」是否值得獨立一份。我判 major,交編排者裁。

## A2 JUnit 例外處理鏈在 `_e2e_junit_ok` 又寫一次,沒用 `_secev_junit_facts`
severity: minor
blocking: 否
引句:「except getattr(tq, "JUnitRejected", ()) as e:」
file: `scripts/lumos:8802`(`_secev_junit_facts`:同一條 `JUnitRejected`、`ParseError`、`RecursionError`、`ValueError` 的鏈,回代碼)

讀取器本身是同一個 `tq.junit`,結構上沒分岔。所以只是包裝不同:`_secev_junit_facts` 回 `({id: 狀態}, 代碼)`,另外還有案例數上限 `_SECEV_FACTS_MAX`。

`_e2e_junit_ok` 把四種例外自己再接一次,並把代碼翻成中文。可以呼叫 `_secev_junit_facts` 後自己轉成中文訊息,避免例外清單兩邊各維護。但 `_secev_junit_facts` 以案例 id 當鍵,同名案例會互蓋,Maestro 報告可能有同名案例,所以直接換不一定安全。我給 minor。

## A3 範本腳本內重複了 flow 名稱的轉換規則,沒有標註要跟 lumos 同步
severity: minor
blocking: 否
引句:「name = re.sub(r"\.[^./]*$", "", f.strip().rstrip("/").removeprefix("./")).replace("/", "__")」
file: `scripts/lumos:40322` 一帶的 `_e2e_flow_name`(用 `rpartition` 加 `"/" not in ext` 實作同一規則)

範本和 judge 必須對同一支 flow 算出同一個名字,否則 judge 找不到 `steps.json` 裡的 ui 條目,會一律判「沒跑到」。範本因為是獨立的 sh+python,不能 import lumos,重複是必要的。

但鄰居範本重複 `kill_group` 時,在註解裡寫明「跟 lumos 的 `_kill_proc_group` 同一套」。這裡兩邊都沒有互相指向的註解,漂移時只能靠測試抓。

我沒找到一支測試專門把兩邊的名稱規則對起來:`t_android_e2e_run_script` 只測 `.maestro/login.yaml` 一種寫法。這是命名與錯誤處理層的不一致,不是結構問題,所以給 minor。

不對齊共 3 條,其中 major 1 條。
