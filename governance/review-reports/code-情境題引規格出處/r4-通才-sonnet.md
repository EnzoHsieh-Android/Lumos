severity: major

## t1 第二個終止訊號一律強制結束,關終端時連送的兩個 SIGHUP 會把收尾打斷
severity: major
blocking: 是
歸因:有證據的修復回歸
引句:「r2 的「第二個以後只記下」撤回:收尾卡住時(git 掛住、大 build 目錄)沒有任何辦法中止」
file: `scripts/lumos:75818`(修後的 `_situation_rule_signals`,處理器 `_on` 在 `len(st.got) >= 2` 時直接呼叫 `_situation_rule_force_exit`)

這個修補為了讓「收尾卡住時能強制結束」,把 r2 刻意加的守衛拿掉了。那個守衛擋的是 r2 已點名的情境:關終端時核心和 shell 各送一次 SIGHUP,連續到達。修後的 `_on` 不分兩個訊號的間隔和種類,第二個就 `os._exit`。

失敗場景:
1. 殺傷力驗證跑到一半,使用者關掉終端,程序在約 50 毫秒內收到兩個 SIGHUP。
2. 第一個 SIGHUP 轉成 KeyboardInterrupt,`_isolated_worktree` 的 finally 開始收工作樹。
3. 第二個 SIGHUP 在收尾中到達,程序立刻 `os._exit(2)`,不跑 `worktree remove` 和刪暫存資料夾。
4. 結果是 `lumos-kill-*` 工作樹和暫存資料夾留在磁碟上,git 的 worktree 登記也還在,要等下次跑人裁時清一天以上的殘骸。
5. 寫回段也一樣:第一個訊號只記下,第二個在寫計劃的視窗裡就強制結束,落進「不確定寫進去沒有」的人工查帳流程。

重現(載入修後的 `scripts/lumos`,以及修前 `f04090128` 的版本)。子程序進入 `_situation_rule_signals()`,finally 裡 sleep 0.5 秒模擬收工作樹,再寫標記檔。從外面送兩個 HUP,間隔 50 毫秒:
- 修前 `f04090128`:輸出 `KI caught`,標記檔存在,rc=0。收尾做完。
- 修後 `7e2c292e3`:輸出「強制結束(第二個終止訊號)…隔離工作樹與暫存資料夾沒收」,標記檔不存在,rc=2。收尾被打斷。
- 補充:`kill -HUP` 緊接著送兩次、中間不隔時間,Python 會把同號訊號合併成一次,看不出差異。要有間隔才重現,真實的 shell 轉送正是有間隔的。

測試覆蓋:`t_situation_rule_double_signal` 的組合 SIGTERM×2、SIGTERM→SIGHUP、SIGINT×2 都把「50 毫秒內第二個就強制結束」當成期望,所以這條回歸測試抓不到。

可行的補救方向(供處置參考):第二個訊號要距第一個超過一小段寬限(例如 1 到 2 秒)才強制;或收尾沒在寬限內完成才強制。

## 附:三問、圖譜鏡頭

- **原問題的修復效果(有行為證據):** 在修後版本的解出樹上跑了相關測試子集,全綠:
  - `python3.14 scripts/test_lumos.py -k situation_rule_write_phase` 4 passed
  - `-k situation_rule_force` 5 passed
  - `-k situation_rule_double` 12 passed
  - `-k situation_rule_already` 9 passed
  - `-k situation_rule_plan` 8 passed
  - `-k isolated_worktree` 13 passed
  - `-k spec_gate_ruled` 15 passed
- **修補處的正常、錯誤、相鄰呼叫路徑:**
  - `_isolated_worktree` 的 `on_keep(None)`:全 repo 只有 guard kill 傳 `on_keep`,它的 lambda 已處理 None。
  - `_spec_gate_ruled_ids` 的其他呼叫端(`scripts/lumos:14617`、`:16304`)簽名沒變。
  - `_disk_spelling` 吃 Path,`env.vault` 是 Path。
  - 寫入鎖:`_situation_rule_drop_lock` 只刪第一行是自己程序編號的鎖檔,用的是 `_vault_write_lock` 收尾同一套判法。
  - 等鎖時被中斷的流程跑過,沒有發現殘鎖或誤刪別人的鎖。
- **新發現的同一案例修前、修後:** 只有 t1 這一條,結果如上。
- **沒夠證據成案、不計入 finding:**
  - `_KILL_RUN_LIVE` 與 `_LINT_WT_REG["procs"]` 是兩份平行的程序登記,但 lint 那份綁在 lint 專用的收尾上,沒有講得出具體風險。
  - `_spec_gate_ruled_ids` 的 `ai_out` 在同一條款有多筆 AI 事件時,由「最後一筆」變成「第一筆」。修後的「已寫過」判定已擋掉同文字不同段的重複寫回,實際走不到。
  - 強制結束發生在原子寫入中途時,可能留下暫存檔。視窗極小,沒有重現,不報。
- **圖譜鏡頭:** 派工附的 LUMOS-LENS 寫明「這次沒附固定席節點」,所以沒有固定席筆記可逐條判。鎖檔 `…a6b82636….json.warming` 不存在,沒有需要處理的鎖,照派工詞審查。範圍內的筆記改動(guard-kill、規格閘、棧別提問表態閘、計劃)我只抽看,沒有發現和程式矛盾。
- 修補差異裡逐字引句:「收掉還在跑的測試程序群組(_KILL_RUN_LIVE)、刪自己的寫入鎖檔(st.lock)、印 st.force_msg,os._exit(st.force_rc)。」
- 清理:實驗用的 `/tmp/lumos-seat-work/code-情境題引規格出處/通才-sonnet/` 已用字面絕對路徑刪除。

最嚴重:major;blocking 共 1 條
