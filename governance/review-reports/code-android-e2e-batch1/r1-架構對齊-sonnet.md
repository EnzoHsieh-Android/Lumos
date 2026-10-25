severity: major

**第一問:分層與依賴方向。對齊,沒有跨層直呼。**
- 新碼放在 `scripts/lumos` 的 macrobench 區塊後面,位置與鄰居相同:`_macrobench_config` 是 `file:39399`,`_macrobench_mode` 在 patch 的 101 行。
- 設定驗證由 `_macrobench_config` 呼叫 `_e2e_cfg_err`,與 `_macrobench_stab_cfg_err` 同形。
- 寫入走 `_vault_write_lock` 加 `_write_lf`,與 `_lint_waivers_add` 一樣(`scripts/lumos:38618`)。
- 工作目錄改動檢查走 `_dirty_non_bookkeeping`(`scripts/lumos:20940`),簿記目錄也登記進 `_BOOKKEEPING_DIRS`。
- 範本腳本不 import lumos,只透過 `lumos macrobench` 和 `lumos android-e2e judge` 的命令列互動,與 `android-stability-collect.sh` 的分工一致。
- 子命令分派的形狀與 `cochange` 略不同,見 A8。

**第二問:命名與錯誤處理。大致對齊,有幾處 minor 不一致。**
- 對齊的部分:
  - 回 `(值, 錯誤訊息)`。
  - judge 的 rc 0/1/2。
  - 「擋下:」訊息走 stderr。
  - 前綴 `_e2e_*` 與 `_macrobench_*` 並列。
  - 設定錯誤用「macrobench.json 的 e2e 段:…」,與 stability 段訊息同形。
  - 範本腳本的 `die`、`Terminated`、`kill_group`、`stop_listening`、`on_term`、`on_int` 與 `android-stability-collect.sh:31-65` 逐字同形。
- 不對齊的部分見 A4 到 A8。

**第三問:第二種做法。有,見 A1 到 A3,三條都是 major。**

## A1 新增 `_e2e_git`,第二種 git 呼叫包裝
severity: major
blocking: 是
引句:「def _e2e_git(root, *args, binary=False):」
- diff 內:`_e2e_git`(patch 288-297)自己 `subprocess.run(["git","-C",...], timeout=120)`,吞掉例外後回 `None`。
- 既有做法有三個:
  - `_lens_git`,`scripts/lumos:59613`。它已支援 `binary=True`、`timeout` 和 `quote`,並且處理 NUL 參數的 `ValueError`。
  - `_nodehome_git`,`scripts/lumos:41060`。它是「位元組輸出、失敗回 None」的包裝,與 `_e2e_git(binary=True)` 語意完全相同。
  - `_secev_git`,`scripts/lumos:9919`。它會加 `-c log.showSignature=false`。
- 同一份 diff 的 `_e2e_precheck` 已經經由 `_dirty_non_bookkeeping` 用了 `_nodehome_git`,所以同一功能內出現兩套 git 呼叫。
- 差異:`_e2e_git` 不處理 `ValueError`,也沒帶 `log.showSignature=false`。`rev-parse HEAD` 這類呼叫在使用者設了 showSignature 時就有機會受影響。
- `_e2e_git` 的 `timeout=120` 與 `_nodehome_git` 預設 20 也不同。
- `scripts/lumos:20940` 的說明就是「git 跑不起來回 None」的既有慣例。

## A2 新增 `_e2e_load_json`,第二種 JSON 讀檔輔助,且少了鄰居的防護
severity: major
blocking: 是
引句:「def _e2e_load_json(path):」
- diff 內:`_e2e_load_json` 只做 `json.loads(read_text)` 加例外兜底。judge 用它讀 `steps.json`、紀錄檔、stability 判定輸出和 macrobench 判定輸出。
- 鄰居:`_macrobench_stab_load`(`scripts/lumos:39894`)和 `_macrobench_thresholds`(`scripts/lumos:39788`)是同一個「讀 JSON 回 (值, 錯誤)」的模式。前者還加了 `_events_depth_ok(raw, 20)` 深度限制和 `_macrobench_stab_scrub`(孤立代理字元清洗)。
- 差異:這些防護是專門針對 `--json` 印出時崩潰修的(`scripts/lumos:39894` 附近註解提到代碼審 r3 邊界席)。
- 新輔助沒有深度與清洗,且讀的是範本腳本落在磁碟上的輸出檔。判定輸出有孤立代理字元時,`_e2e_print_runs` 或後續寫紀錄會走到同一個崩潰點。
- 建議收斂成共用同一支,或讓 `_e2e_load_json` 呼叫 `_macrobench_stab_load` 那一套。

## A3 新增 `_e2e_now`,第二支時間格式函式
severity: major
blocking: 是
引句:「return _dt.datetime.now().astimezone().isoformat(timespec="seconds")」
- `_e2e_now`(patch 555-557)與 `scripts/lumos:40664` 的既有函式逐字相同。我在該處只看到一支同形函式,沒讀它的函式名與用途。
- 專案另有 `_utc_ts`(`scripts/lumos:29914`,UTC 版)。
- ⚠ 專案裡「`datetime.now().astimezone().isoformat(timespec="seconds")`」到處行內寫(例如 `:1443`、`:1601`、`:14130`、`:17415`),所以「沒有共用 helper」本身就是既有做法。
- 判定:若 `:40664` 的函式是通用的,這是 major(第二支同功能函式);若只是行內慣例,這條降為 minor。請編排者看 `:40664` 的函式名後決定。

## A4 `_e2e_junit_ok` 的 XML 解析沒走既有的安全包法
severity: minor
blocking: 否
引句:「tree = ET.parse(path)」
- `scripts/lumos` 裡另有三處用 ElementTree:`:8804`、`:39048`、`:40486`。
- 我只確認了 `:40486` 是同樣的區域 import,沒逐一比對它們對解析失敗和大小限制的處理。若鄰居有大小或實體防護,這裡是漏了。
- 這裡讀的是範本腳本落地的檔案(維護者自己跑的),所以我不敢升 major。

## A5 範本腳本的裝置鎖是第二種鎖做法
severity: minor
blocking: 否
引句:「holder = lock_holder(serial)」
- 腳本內 `take_lock` 用 `O_EXCL` 寫 PID,PID 已不在就清掉接手。
- 既有鎖 `_excl_lock_try`(`scripts/lumos:60949`)的說明明文寫「依鎖內 PID 接手會雙持(ABA),所以不自動接手」。
- `android-stability-collect.sh` 沒有任何鎖(grep 只命中 `check-ignore`)。
- 所以這是專案裡第一個「PID 活著才算占用」的鎖,且與 lumos 本體的明文否決方向相反。
- 範本是獨立的 python,用不到 lumos 的函式,所以我只列 minor。
- ⚠ 這是設計取捨,交編排者看是否要在筆記裡寫理由。

## A6 測試新增 `_e2e_tgit`,沒用既有的 git 初始化輔助
severity: minor
blocking: 否
引句:「def _e2e_tgit(root, *args):」
- `scripts/test_lumos.py:22415` 已有 `_git_init_commit`,`:22433` 已有 `_git_head`。
- 新輔助為了多檔提交用 `-c user.name=t ... commit.gpgsign=false` 自成一套,不算完全重複。
- 但 `t_android_e2e_*` 沒有鄰居 `_ms_collect_env` 那套 `GIT_CONFIG_GLOBAL=os.devnull`、`GIT_CONFIG_NOSYSTEM`、`XDG_CONFIG_HOME` 隔離。
- `_e2e_script_env` 的環境變數(patch 482-495)沒有這三項。
- `_ms_collect_env`(`scripts/test_lumos.py:19146`)的註解就記載過「全域 gitignore 有 `.lumos/`」會讓「產物目錄沒被忽略」誤紅。這個坑 e2e 腳本也會踩,因為它也跑 `check-ignore`。

## A7 設定讀檔的編碼處理與 `_macrobench_config` 不同
severity: minor
blocking: 否
引句:「d = json.loads(raw.decode("utf-8-sig"))」
- `_e2e_config_at` 用 `utf-8-sig` 讀提交樹裡的 macrobench.json。
- `_macrobench_config`(`scripts/lumos:39399` 起)用 `read_text(encoding="utf-8")`,有 BOM 就讀不了。
- 同一個檔,兩條讀法的容忍度不同。範本腳本的 `load_config` 也用 `utf-8-sig`。
- 結果:有 BOM 的檔 `--check-config` 先擋下,所以實際不會走到不一致,但兩邊的寫法不一樣。

## A8 子命令分派沒用 `e2ecmd`
severity: minor
blocking: 否
引句:「aesub = ae.add_subparsers(dest="e2ecmd", required=True)」
- 鄰居 `cochange` 會依 `args.cccmd` 分派(patch 720-725)。
- 這裡建了 `e2ecmd`,分派卻直接 `return _e2e_judge_cmd(...)`,沒看它。現在只有一個子命令所以行為正確。
- 之後加第二個子命令(計劃是「第一批」)就會被當成 judge 執行。

不對齊共 8 條,其中 major 3 條。

A3 已標 ⚠:`:40664` 的函式用途我沒讀,若它只是行內慣例,major 降為 minor,總數變成 major 2 條。A4 和 A5 的判斷依據也只到我實際讀到的範圍。

相關路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/code-android-e2e-batch1/r1-snapshot.patch`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/scripts/templates/android-stability-collect.sh`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/scripts/test_lumos.py`
