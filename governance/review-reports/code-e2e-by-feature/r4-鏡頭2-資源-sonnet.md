severity: minor

## F1 記憶體情境目錄名可能和使用者自訂的 run-id 撞名
severity: minor
blocking: 否
file: ``scripts/templates/android-e2e-run.sh:471``(`sid = run_id if scn is None else f"{run_id}.{scn}"`),預檢在 ``scripts/templates/android-e2e-run.sh:326``
失敗場景:
- 先用 run-id `r1` 按功能跑記憶體情境 `a`。收集腳本把結果寫進 `.lumos/artifacts/android/r1.a/stability.json`,這個目錄沒有 `steps.json`。
- 之後使用者把 run-id 取成 `r1.a`(run-id 規則允許點),再整套或按功能跑。預檢只看 `<run-id>/steps.json` 在不在,所以放行。
- 建置、安裝、UI、截圖都跑完,才輪到收集腳本。它在 `scripts/templates/android-stability-collect.sh:391` 發現 `stability.json` 已存在,印「已經有結果檔了」就退出。
- 那一步判成沒判完。整輪重跑浪費的是建置加整段 UI 的時間。反過來(先 `r1.a` 後 `r1` 帶情境 `a`)一樣。
- 情境名只收英數字、底線、連字號(`scripts/lumos:40400`),不含點,所以只有使用者自己用 `<id>.<情境>` 形狀取名才會撞。
歸因:未判定。這個命名方式在修前 4b056532 就有(`git show 4b056532:scripts/templates/android-e2e-run.sh` 的 `sid = ...` 那行相同),不是這輪修補造成的。我只讀碼推導,沒有真的跑撞名案例,所以是推導出來的。
引句:「        sid = run_id if scn is None else f"{run_id}.{scn}"」

## 三問

**① 原問題的修復效果有何行為證據**
- 修補後 `t_android_e2e_run_edges` 7 過 0 紅(`7988107c`,約 22 秒)。
- 修前 `4b056532`,換上修後的測試檔,同一個測試紅 2 筆:
  - 一筆是「替身收集腳本有設但這次沒收記憶體時照寫紀錄」(對應 G3)。
  - 一筆是 `[Errno 2] ... proj/.lumos/e2e-records` 例外(對應 G4,寫不進去、捷徑那組)。
- 效能逾時不往下(G5):修後 `t_android_e2e_run_edges` 通過。程式碼上看到 `break` 在 `st.step(...) is None` 時生效(`android-e2e-run.sh:481`、`:495`)。
- 兩次都用 `python3.14 scripts/test_lumos.py -k <名>`,載入版本是各自 clone 內的 `scripts/lumos`,由 `git rev-parse HEAD` 確認為上面兩個提交。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立**
- 效能每方法一次(`t_android_e2e_perf_per_method`):修前與修後都是 1 過 0 紅。
- 同一個效能方法列在多個情境:`_e2e_sel_add`(`scripts/lumos:40940` 一帶)會去重,整套跑時 `tests_to_run` 用 `dict.fromkeys` 去重,所以不會跑兩次。
- 子程序:
  - 新加的每一步都走 `run()`,有逾時,逾時或中斷時整個程序群組先 TERM 再補 KILL,不留孤兒。
  - `lumos select` 與 `judge --precheck` 也走 `run()`,預設上限 120 秒。
  - `--changed` 的每個 git 呼叫上限 20 秒,次數有限。
- 裝置鎖:放在 `try/finally`,有 `drop_lock`。中斷在 `Steps()` 建立之前時,`st is None` 路徑也會 `drop_lock`。
- 檔案 handle:
  - `_local_ledger_append` 與 `_ledger_tail_needs_newline` 用 `os.open` 加 `finally: os.close`。
  - `_canary_ledger_rows` 用 `with ...open`。
  - 讀改寫紀錄的 `_e2e_record_update` 在讀改寫鎖內,新增的 `OSError` 分支直接回錯誤訊息,不丟堆疊。
- 總表寫一半:短寫或 `OSError` 回 False,只印提醒、不改判定。下一次追加前 `_ledger_tail_needs_newline` 會補換行。
- 磁碟:`<run-id>.<情境>` 目錄也在 `prune_old_snapshots` 掃的 `android/*` 底下,超過 7 天的 `heap-*.pftrace` 會被刪。其餘檔案(`stability.json` 等)小、不清。
- 未驗:
  - 沒有實機或替身跑完整的中斷後孤兒回收,只讀碼確認。
  - 沒量快照實際大小,所以「7 天內開發中頻繁跑造成的累積量」未判定。

**③ 新發現(F1)修前修後各是什麼結果**
- 修前、修後的程式碼相同,所以兩邊行為一致。沒有實際跑撞名案例,屬未判定。

## 子程序與效能量測(補充證據)
- 總表 history 讀 5 萬行、58MB 的 `history.jsonl`:`lumos android-e2e history --last 5` 用了 1.32 秒。
  - 對照只有 1 行的總表是 0.64 秒,所以增量約 0.7 秒。
  - 最大常駐記憶體兩者都是約 338MB,沒有隨檔案變大,因為是逐行讀加 `deque(maxlen)`。
- 這個量測用 `/usr/bin/time -l`,跑在修後 `7988107c`。總表讀取不是這輪修補改的,修前沒另外量。
- 重複的昂貴操作:非按功能的整套跑,`Steps.__init__`(`android-e2e-run.sh:399`)會多叫一次 `lumos judge --precheck`,預檢本來已叫過一次。judge 內部還會再判一次,多的是幾次 git status,成本小,不構成問題。

## pitfalls manifest
內建題:「scripts/lumos 寫總表那段的 open( —— 檔案 handle 有沒有 with/確定 close?」判為誤報。
- 寫總表的 `_e2e_history_append` 走 `_local_ledger_append`,用 `os.open` 並在 `finally` 內 `os.close`。
- 帳尾檢查 `_ledger_tail_needs_newline` 也是 `finally: os.close(fd)`。
- 讀端 `_canary_ledger_rows` 用 `with Path(path).open("rb")`。
- 例外與提早 return 都不會留下開著的 handle。

## 圖譜鏡頭
- 這次派工沒附固定席節點(LUMOS-LENS 說「這次沒附固定席節點」,鎖狀態未知),屬「圖譜沒有釘到節點」備援。我沒有被要求逐條回答固定席筆記。
- 唯一讀過的合約來源是規格 `Projects/Android端到端驗收_計劃.md〈按功能與使用情境跑〉`。診斷內容見上面 F1;沒找到破壞合約的證據。
- 指定的鎖檔 `~/.cache/lumos/dispatch-lens/...json.warming` 我沒檢查,也沒刪。

臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭2-資源-sonnet` 與測試紅時留下的 `gctl-run-efuy6n1q` 現場,都已用字面絕對路徑刪除。

這一輪只找到一條與修補無關的命名撞名隱患,資源面的子程序、檔案、鎖、重複操作、磁碟與大總表都未發現會讓下一次跑不起來的問題。
