severity: major

**1. 計劃寫的停用方式(把設定拿掉或改成 1)會讓全套測試轉紅,推送閘擋住這個修正**
severity: major
blocking: 是
引句:「只想關掉不還原程式時,把本 repo 設定的 `bound_tests.parallel` 拿掉或改成 1,行為就回到循序」
file: `scripts/test_lumos.py:50026`
1. 照〈回退〉只把設定改成 1,再跑 `t_bound_tests_parallel_repo_config_on`(驗收條款 S3 綁的測試)。
2. 它讀本 repo 的 `.lumos/config.json`,要求 `parallel` 是 2 到 16 的整數,所以斷言失敗。
3. 我在臨時 clone 實際改成 1 重現:`python3.14 scripts/test_lumos.py -k t_bound_tests_parallel_repo_config_on` 輸出 `✗ FAILED ... (1 條斷言)`,結果 1 passed, 1 failed。
4. 推送前的閘和 CI 會跑全套測試,這支必然在裡面。所以「只改設定」這條逃生路走不通。
5. 同時跑造成假紅、要緊急停用時,修正提交必須一併改測試和計劃的 S3 條款。計劃〈回退〉完全沒提這點,收拾的人會先撞牆再摸索。
6. 前一步已查:純設定檔的修正提交會判為 light(`lumos pitfalls --diff` 回 `tier: light`),不必重過代碼審,留痕也不會失效。真正的阻力是這支測試。要補的是:S3 改成「值在合法範圍或明確寫 1」,或〈回退〉明講要連動改測試。

**2. 主流程等待迴圈在第一個工作執行緒結束後變成空轉,拉高負載,正好增加假紅**
severity: major
blocking: 是
引句:「while any(th.is_alive() for th in threads) and not errs:」
file: `scripts/lumos:48299`
1. 迴圈靠 `threads[0].join(0.1)` 來等待。
2. `threads[0]` 結束後(佇列領完、它先收工),`join` 對已死的執行緒立刻返回,不再等 0.1 秒。
3. 其餘執行緒還在跑慢測試時,主流程就一直空轉,最長可到單支逾時 180 秒。
4. 最小重現:兩個 daemon 執行緒分別睡 0.2 秒和 3 秒,用同樣的迴圈等。結果是 4,649,077 次迴圈、CPU 2.8 秒(耗時約 2.8 秒),吃滿一顆核心。
5. 計劃〈實務隱患〉自己承認「負載高會讓逼近逾時的測試轉紅」,RETIRE-IF 也以「一次同時跑造成的假紅」為撤除條件。這個空轉在每次推送的尾段、最慢那幾支還在跑時必然發生,等於替假紅加壓。
6. 退路也受影響:如果出現假紅,收拾的人得先分辨是不是這個自製負載。標「未能在真實閘上重現假紅」,但空轉本身已實證。

**3. 回退後帳上同一欄 secs 會混入不同意義的值,計劃的回退段沒涵蓋**
severity: minor
blocking: 否
引句:「_rec["secs_kind"] = "wall"」
file: `scripts/lumos:47910`
1. 只把設定改回 1、程式不還原:新程式仍記牆上時間(循序下約為去重後的總和),且帶 `secs_kind: wall`。
2. 還原整個提交:舊程式記逐項相加值,不帶 `secs_kind`。
3. 兩種情況下,同一欄 secs 都會同時混著牆上時間和逐項相加值。
4. 讀端安全:`_GOV_FIELD_TYPES` 沒有 `secs_kind` 這個鍵,未知鍵不會被跳過;`secs` 型別沒變。所以新舊混用不會讓帳讀不出來。
5. 受影響的是統計:REVISIT 2026-12-15 要看 8 週中位數,回退後該中位數混了兩種語意,而計劃〈回退〉只提「舊版忽略新鍵」,沒說要用 `secs_kind` 篩選。

**回滾與相容逐條判定**
- 舊版程式讀到 `bound_tests` 鍵:基準版 `scripts/lumos` 沒有 `bound_tests` 字串,所以確實忽略,新舊混用不影響判定。消費專案用舊工具、config 有該區塊同理。
- 帳的新舊混用:`secs_kind` 不在欄位型別表內,不會被跳過整行。無問題。
- 推送閘自壞(雞生蛋):逃生路存在。`LUMOS_SKIP_BOUND_TESTS=1` 或 `--skip` 可略過合約測試閘。`_bound_tests_parallel` 讀的是工作樹設定,本機改成 1 立刻生效。但設定改回 1 會踩 finding 1 的測試。
- 停用要改的檔:只改 `.lumos/config.json` 是 light、不必重過代碼審,留痕不失效。若連同測試和計劃一起改,測試檔與計劃進入 `scripts/` 就會是程式改動,重新分級。我沒另外驗,標 ⚠ 未驗證。
- 孤兒子程序:出錯時 daemon 執行緒隨程式結束,已開跑的測試子程序在自己的程序群組跑到逾時為止,最長 180 秒。計劃已寫明,屬已承認的殘留。我沒另外找出會卡住修正推送的證據,不標 finding。

**圖譜鏡頭**
- `bound-tests-gate`:這份 diff 不破壞「紅/懸空/fake/unfilterable 擋、沒 run_cmd 不擋」的合約。判紅綠、逾時、跑過證據、去重鍵都沒動。例外是 finding 2:空轉可能把逼近逾時的測試推成紅,方向偏嚴,不會假綠。
- `guard-kill`、`lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`、`design-loop`:diff 沒碰各自合約宣稱的行為(rc 優先序、`--json` 純度、search 過濾、re-inject、處置閘)。無牴觸。
- `loop-convergence-recording`、`pitfalls-code-loop`(★RISK★):只列檔名牽連,diff 沒改它們的邏輯,無法指出具體破壞點。
- 其餘超出上限只列名的節點:我沒有逐篇讀,不判定。

我建在 /tmp 與 `/var/folders` 的臨時 clone 和測試現場都已刪除。

總結:最高等級 major
