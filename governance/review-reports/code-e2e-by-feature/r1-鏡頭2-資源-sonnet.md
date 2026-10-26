severity: minor

## F1 效能測試方法名的格式檢查太晚才做,整趟建置、安裝、flow、記憶體都已經白跑
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh` 的 `accept()` 效能那段(diff 檔 960–968 行)。對照 `scripts/lumos:40773` 附近新增的 `_e2e_case_err`,它只驗 macrobench 是字串清單,不驗字元。
失敗場景:`features.login.cases.ok.macrobench` 填 `["Bench#one two"]`,或寫成 `Bench one`。
- `macrobench --check-config`、`android-e2e select` 都放行。
- 腳本先建 APK、裝上、跑完所有 flow 和每個記憶體情境(每項上限 3600 秒),才在 `for t in tests` 這個迴圈驗名字。
- `die()` 丟出 SystemExit,`except (Terminated, KeyboardInterrupt)` 接不到。
- steps.json 只寫到一半、`ended` 還是 null,沒有叫 judge,也沒有進總表。
- 這個 run-id 因為 steps.json 已存在,下次開跑檢查會被拒,要換 run-id 重跑。
- 整套跑也一樣,因為 `tests_to_run` 會從 features 取全部方法。
修法:把同一條正則放進 `_e2e_case_err`,設定檢查時就擋下;或在 `preflight` 裡先驗。
引句:「                die(f"效能測試方法名只收英數字、點、#、底線:{t!r}")」

## F2 history 讀全檔,而且 `--last 0` 或負數的行為不對
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_e2e_history_cmd`(diff 檔 488–517 行)。
- `p.read_text(...).splitlines()` 一次讀全檔,`rows` 再留下所有符合的行,總表只增不減。每行含 items 與 perf,約 1 到數 KB,10 萬行約幾百 MB 記憶體,只為了印最後 20 筆。
- `--last 0` 時 `rows[-0:]` 等於 `rows[0:]`,整份印出。`--last -3` 會變成跳過前 3 筆。argparse 的 `type=int` 不擋這兩種。
- 這是單人工具,長到那麼大要很久,所以只算 minor。
修法:逐行讀,用 `collections.deque(maxlen=last)` 留尾端,並擋 `last < 1`。
引句:「    for r in rows[-last:]:」

## 逐項查證後確定沒問題的部分
- 子程序的逾時與收尾
  - 新加的 lumos 子程序(select、`--precheck`、每個方法的效能步驟、每個情境的記憶體步驟)都走同一支 `run()`:`start_new_session`、有逾時、逾時或被中斷時整組 `kill_group`。沒有孤兒。
  - `select` 內的 git 呼叫都有 20 秒上限或截止時間。`--changed` 的 `_secev_mainline` 只走本機 ref,沒有網路呼叫。
- 重複的昂貴操作
  - 同一個效能方法或記憶體情境被多個 case 列到時,`_e2e_select` 用 `x not in sel[k]` 去重,`tests_to_run` 用 `dict.fromkeys` 去重,不會跑兩次。
  - 全套跑時 `Steps.__init__` 多叫一次 `--precheck`(開跑前檢查已保證乾淨,所以這次的結果必為乾淨),只多一次 python 啟動和 git status,可忽略。
- 鎖與 handle
  - `_e2e_record_update` 在 `with _vault_write_lock(p)` 裡,例外和提早 return 都會放掉。
  - 總表追加用 `with open(p, "a")`,每次只寫一行。
  - 裝置鎖仍由 `main()` 的 `finally: drop_lock` 放掉,新路徑沒繞過它。
- 磁碟:每個記憶體情境另開 `<run-id>.<情境>` 目錄。`prune_old_snapshots` 掃 `base` 底下全部子目錄,新目錄的 7 天以上快照照樣會清。stability.json 和日誌累積,跟舊的 run 目錄一樣沒有清理。

## pitfalls manifest
內建題:「scripts/lumos 寫總表那段的 open( —— 檔案 handle 有沒有 with/確定 close?」判為誤報。`_e2e_history_append` 的 `open(p, "a", encoding="utf-8")` 在 `with` 裡,例外時也會關。`write` 前的 `json.dumps` 失敗時不會留下寫一半的內容。`except OSError` 沒接 UnicodeEncodeError,但 steps 資料已經過 `_macrobench_stab_scrub`,我想不出實際輸入,不列 finding。表態記錄裡 py-* 各題我都沒查到與這次 diff 矛盾的地方。

## 圖譜鏡頭
- 固定席都不會被這份 diff 破壞。
  - lumos-cli-read(search 排除 superseded)、guard-kill(rc 優先序、`--json` 純度)、lumos-cli-lifecycle(re-inject 保留 sentinel 外內容)、bound-tests-gate 的各條 INVARIANT:diff 沒碰 search、guard kill、reinject、code-loop check。
  - pitfalls-code-loop、loop-convergence-recording、reversibility-governance-ledger 這幾個 RISK 節點牽連到的是 `scripts/lumos` 同一支檔,但這次只動 android-e2e 區段。
- 測試假綠形態:「還原翻紅釘要配前置斷言」只約束修 bug 的釘子。這次新增的 `t_android_e2e_by_feature` 等測試都在檢查前先確認 flow 真的被執行,沒有違反。
- 我沒有實際把這些測試跑起來,只讀了 diff,所以測試能不能抓到對應錯誤沒有驗。

這份 diff 的子程序、handle、鎖都收得乾淨,只有效能方法名驗得太晚和 `history` 讀全檔且 `--last` 沒擋 0 與負數兩個 minor。
