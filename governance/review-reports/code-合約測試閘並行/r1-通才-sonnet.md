severity: minor

## 1. 帳上新舊兩種 secs 並存,沒有欄位能分辨
severity: minor
blocking: 否
引句:「secs = _wall」
file: `scripts/lumos:47908`(`_bound_tests_log` 只寫 `secs`、`calc_secs` 兩欄)
- 這份 diff 之後,同一個 gate=bound-tests 的帳裡,舊紀錄的 secs 是逐項相加,新紀錄是牆上時間。紀錄本身沒有任何標記區分兩者,例如沒有 `wall:true`,也沒有 schema 版本。
- 受影響的是原案「近 30 天合約測試耗時最大值超過 90 秒就加收窄旗標」那條回頭條件。它在 `合約測試閘什麼時候跑_計劃` 的 [S6] 下讀 `secs`。改後 30 天內「最大值」仍由舊的相加值主導,新值只會被遮住。
- 「中位數」則是新舊混算,數字無意義。
- 新計劃只在 REVISIT 文字裡寫「舊帳 secs 是逐項相加,不拿來比」。這是散文約定,不是讀帳的機械界線。
- 讀帳的程式碼在 `scripts/lumos` 裡沒找到,所以目前沒有程式被誤導。誤導會出在人或日後的度量程式依 2026-10-13 這個日期手動切段時。
- 建議在新紀錄加一個欄位,例如 `secs_kind:"wall"`,或把 `secs` 改名。

## 2. 以時間量測判「同時跑」的新測試,在負載下有假紅風險,而且這些測試自己就會被並行閘跑
severity: minor
blocking: 否
引句:「ok = (ov >= 2) if want_par else (ov == 1)」
- `t_bound_tests_parallel_config_values` 的 val=3 那一例,要求三個工作者各自 `sleep 0.8` 的區間至少有兩段重疊。
- 區間的起點 `t0` 是在每個子程序 python 啟動之後才量的。機器很忙時,各子程序的啟動時間差如果超過約 0.8 秒,區間就不重疊,測試誤紅。
- 這幾支測試被 `bound-tests-gate` 綁定,所以在本 repo 會被 `parallel=4` 的閘同時跑。也就是測試自己加重負載,再用時間量測判斷「是否重疊」,有自我放大的風險。
- 沿用 pytest-xdist 慣例的做法是用同步原語取代睡眠。例如每支開工時建檔,再等「另一支的檔也存在」,有等待上限而不是靠重疊的牆鐘。
引句:「LUMOS_TEST_TIMEOUT"] = "2"」
- `t_bound_tests_parallel_matches_sequential` 把逾時設成 2 秒,綠的 `t_g*` 要睡 0.8 秒,餘裕只有約 1.2 秒。
- 負載高、python 啟動拖慢時,綠的那幾支可能被判逾時。這是假紅,不是假綠。
引句:「1.0 <= v["secs"] < 2.2」
- `t_bound_tests_secs_is_wall_time` 的上限 2.2 秒,對舊實作的相加值(約 2.4 到 2.5 秒)只差約 0.3 秒。慢機器上新實作也可能超過 2.2 秒。
- 舊實作下 S4 會紅,這點成立。但判別邊際很薄,而 `sleep` 已拉到 1.2 秒,只要把上限抬高,或改用「等同單項」的比例判斷就更穩。

## 3. 並行路徑上例外與中斷的行為和循序不同
severity: minor
blocking: 否
引句:「with ThreadPoolExecutor(max_workers=min(workers, len(jobs))) as ex:」
file: `scripts/lumos:17175`(`_kill_run` 的 `Popen(...cwd=...)` 在平台 root 不存在時丟 `FileNotFoundError`)
- 輸入:平台 `root` 指向不存在的目錄,或對並行中的閘按 Ctrl-C。
- 循序時,第一個丟出例外的項目立刻讓整個函式往上丟,其餘項目根本沒啟動。
- 並行時,例外要等 `ex.map` 迭代到那一項才浮出。`with` 離開時 `shutdown(wait=True)` 會把已在跑的測試全部等完,最長 180 秒(整套跑的指令是 600 秒)。
- 結果同樣是丟例外,不會假綠。但按 Ctrl-C 時介面會卡住很久。子程序又在獨立 session 裡,收不到 SIGINT。
- 這份 diff 的計劃「實務隱患」沒提這一點。

## 鏡頭逐條判定

**1. 正確性邊界**
- 沒有項目:`plan` 與 `jobs` 都空,直接 `return results=[]`。`results and all(...)` 為假,回 `[]`,與改前一致。
- 全部懸空或沒指令:`jobs` 空,不啟動執行緒池。no-cmd 的 early return 與改前相同。
- 只有一支:`len(jobs) > 1` 不成立,走循序。
- 同一指令被多項共用:`jobs` 以 `(root, cmd)` 去重,兩筆結果各自從 `seen[key]` 取同一份,tails 以 `(node,plat,method)` 為鍵,不會錯配。
- 整套跑與可過濾的混合:`timeout` 現在按 key 各存一份在 `jobs[key][0]`,沒有問題。
- 順帶一個差異:舊碼中,重複 key 命中 `seen` 時沿用的是迴圈外「上一個被實際執行的 key」的 `timeout`。當整套跑(600 秒)與逐支(180 秒)混合,且重複那筆逾時時,舊訊息的秒數是錯的。新碼每個 key 取自己的 timeout。這與「改前逐位元組相同」有差異,但差在修對的方向,而且只有逾時訊息會變。

**2. 暫存與共用資源**
- `_kill_run` 每次呼叫自建 `TemporaryFile` 並開新程序群組,沒有共享狀態。
- 治理帳只有主執行緒在全部跑完後寫,工作者不寫帳。
- 本 repo 的測試總檔有假 HOME 隔離(`scripts/test_lumos.py:532` 附近),`-k` 單支跑的重複載入也不會互踩。
- 消費專案預設是 1,不受影響。

**3. 寫一半、衍生資料、不可逆**
- 閘只讀不寫,沒有寫一半的問題。
- `secs` 是衍生欄位,見 finding 1。
- 不涉及不可逆操作。

**4. 本案特定**
- (a) `_ran_evidence_check` 只吃已存好的 `tail`,與並行無關。逾時是每支各自計時,不會因為排隊而多算。風險只是負載升高後單支變慢,逼近 180 秒上限(最慢那支約 41 秒)。偏嚴,不會假綠。
- (b) 沒寫設定時,`workers == 1`,走 `seen.update(_one(k) for k in jobs)`,執行順序與改前相同。除了上面提到的重複 key 逾時秒數,結果與順序一致。記帳欄位的差異就是 `secs` 改成牆上時間,與 finding 1 同一件事,而且這個語意改變對沒開並行的消費專案也生效。
- (c) 見 finding 1。

**5. 其他讀 secs 的位置**
- CLI 輸出是 `scripts/lumos:48527` 的「跑 {secs}s」。
- 規格閘與修正關卡走另一個呼叫端 `_spec_gate_judge_items`(`scripts/lumos:7661`),它丟掉 `_secs`,不受語意改變影響。
- 呼叫端的結果元組形狀(六欄)不變。

**6. 測試品質**
- S1(結果與循序逐項相同)與 S3(設定值)是回歸守衛。舊實作沒有 `_bound_tests_parallel`,S3 與 S2 的 val=3 那一例會紅;S1 本身不證明有真的並行,並行事實由 S2 釘。
- S4 在舊實作下會紅,見 finding 2 的邊際問題。

## 圖譜鏡頭(固定席)
- `bound-tests-gate`(★INVARIANT★「任一紅/懸空/方法名不合法/證不出跑過 → blocked=True rc1」):判紅綠、unproven、懸空、`no-cmd` 的分支原樣保留,只是挪到組結果迴圈。沒有破壞這條合約。新寫的 WHY 與 PITFALL 兩行帶了 `[test:]`,格式合規。
- `guard-kill`、`lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`、`授權與歸屬`、`design-loop`:diff 沒動 `guard kill`、`search`、`reinject`、`_VENDORED_TOOLKIT`、處置閘的程式路徑。唯一接觸點是共用的 `_kill_run`,而這份 diff 沒改它,只是從多執行緒呼叫。這些合約不受影響。
- `測試假綠形態`:S1 與 S4 沒有「前置斷言證明現場成立」的缺口。S4 有「兩篇都綁到、去重後綠」的前置檢查,S1 有「四種判定都出現」的前置檢查。
- `loop-convergence-recording`(★RISK★)以及其餘只列名的節點:diff 沒碰迴圈記帳,沒有牽連。

總結:最高等級 minor
