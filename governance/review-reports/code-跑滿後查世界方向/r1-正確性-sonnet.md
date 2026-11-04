severity: major

我逐 hunk 讀完 diff,在 `87211d82e` 的 clone 裡實跑,並走過 `_cap_world_case`、`_retro_world_empty`、`_retro_world_check` 的各種近似輸入。其中兩處站得住的洞都在測試與守衛,不在主流程。

**實跑結果**
- `-k world` 全綠(108 項)。
- 我把生效常數暫時改到 `2026-11-01`,模擬「生效後」,再跑 `-k retro`(426 項)、`-k cap_hint`(51 項)、`-k cap_decision`(16 項),全綠。
- `--suite docs` 985 過 1 紅。那一紅是 doctor 列出的過期 REVISIT(逾期日期全是 10 月到 11 月初、與本 diff 無關)。

### F1 cap-decision 的「要求」分支在生效日前沒有任何測試跑到
severity: major
blocking: 是 — S7 驗收條款「cap-decision 記成 extra-round 後應提醒寫 world_check」的正向那半,在今天(生效日前)抓不到錯
引句:「now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")   # 跟剛寫進帳的那筆人裁同一刻判情況」
file: `scripts/lumos:22962`(測試 `scripts/test_lumos.py` 的 `t_cap_hint_world_check_first` 最後段)

失敗場景:
- `cmd_loop_cap_decision` 用「現在」重算情況,不讀剛寫進帳的那筆 ts。測試用真實時鐘,所以今天(11-04,早於 `_CAP_WORLD_CHECK_SINCE`)`now_req` 恆為 False。
- 斷言因此退化成「不印提醒」。把 `_cap_world_case({'decision': decision, 'ts': now})` 整個換成 `_cap_world_case(None)`,也就是永遠不印,測試仍全綠。要到 11-05 之後這條斷言才會翻面。
- 同一處還有次要問題:帳上 ts 是 23:59:59、`now` 已過 00:00:00 時,畫面會提醒寫 world_check,但那筆人裁在帳上其實是「不管」。方向只會多提醒、不會少提醒,窗口約一秒。
- 我確認過正向分支本身是對的。把常數改到過去後,同一支測試的正向斷言通過。問題只在今天驗不到。

重現:在 clone 把 `scripts/lumos` 的 `_cap_world_case({'decision': decision, 'ts': now})` 改成 `_cap_world_case(None)`,跑 `python3.14 scripts/test_lumos.py -k cap_hint_world`,結果 9 passed 0 failed(突變存活)。

### F2 生效常數的「新鮮度」守衛看不到再次改值,也放過同日提交
severity: minor
blocking: 否 — 只擋不到「重新調整常數」與「合併當天」兩種情形,主路徑(實作提交被 rebase 改日期)仍會紅
引句:「check("最後一次改到生效常數的提交日不晚於常數日期", day <= since[:10], f"提交日 {day}、常數 {since}")」
file: `scripts/test_lumos.py:103753`、`scripts/test_lumos.py:103758`

失敗場景:
- `git log -1 -S"_CAP_WORLD_CHECK_SINCE = "` 找的是「該字串出現次數有變動」的提交。後來有人只改常數的值(次數不變),`-S` 看不到那次提交,只會回傳最初加常數的提交。
- 測試註解與函式說明都宣稱「最後一次改到常數那一行」,實際只看第一次。計劃〈相容三〉要靠它逼人把常數改成新的合併日隔天,改值這條路沒有守住。
- 另有邊界:判斷用 `<=`,常數是當天零點,提交日等於常數日就放行。設計說的是「合併日隔天零點」,同日提交不該過。

重現:
- 改值沒被看到:clone 上新增一個提交日 2026-11-10 的提交,把常數改成 `2026-11-06T00:00:00+08:00`。`-S` 仍回傳最初那筆(11-04),測試 2 passed。該提交晚於常數,本應紅。
- 同日放行:把原提交的 committer date 改成 `2026-11-05T10:00:00+08:00`,測試 2 passed。

## 圖譜鏡頭

對照 `Systems/loop-retro`、`Systems/loop-convergence-recording`、`Systems/每輪修補差異派工` 現在宣稱的行為,這份 diff 沒有破壞它們。

- **loop-retro 的「叫人做什麼只由 `_cap_retro_fix_cmd` 一支決定」**:`_cap_retro_fix_cmd` 現在是外層加 `_cap_retro_fix_cmd_base`。判斷仍在 base 一處,外層只在句尾接 `_CAP_WORLD_FILL`。`t_cap_retro_r3_prompt_table`、`t_cap_retro_r2_prompt_no_deadend` 在模擬生效後的時鐘下仍綠。
- **沒帶 case 的呼叫端**:`doctor` I2、`retro-stats` 的 `ent["cmd"]`、`--template --write` 兩處(目錄不安全、檔已存在)都沒帶 case,輸出不變。代價是要求情況的迴圈在 `doctor` 與 `retro-stats` 的修法行不會提醒補 world_check。計劃做法 1 本來就沒列這兩處,所以不算違規。
- **五處共用同一支判定**:`_cap_retro_check` 回傳多帶情況,`_cap_retro_status` 存進 `world_case`,`retro-stats` 與 `--record` 只讀它。我確認 `scripts/lumos` 與 `scripts/test_lumos.py` 之外沒有其他呼叫者會被三元組改壞。
- **新舊互讀**:帳上 99 筆既有 cap-decision 的 ts 全部解得開,判為 ignored 或 optional,沒有舊迴圈被翻成過期。
- **相容二、三仍是已知天花板**:沒更新的工具讀到 version 2 會判「version 要是 1」;生效後用舊工具人裁加開、又記了 version 1 回顧的,會被重判成過期。計劃已明寫,F2 的守衛正是為相容三設的。
- **筆記標記小瑕疵**:loop-retro 新 WHY 的 `[test:t_retro_check_world_check_legacy]` 只管生效判定。同一條講的「統計只數要求而且已記回顧」實際由 `t_retro_record_world_verdict` 守。這是標記不準,行為沒錯。
- **手冊同步**:`t_manuals_world_direction_sync` 的 15 個錨點對上計劃做法 5 列的每一處(同檔兩處也都列),每處都含「先查方向」或 world_check。`argparse` 說明(`scripts/lumos:72885`、`72893`)與擋下訊息(`scripts/lumos:22791`、`22801`)沒提查方向,不在計劃清單內,我不算缺漏。

## 其餘逐項走過、判為正確(未發現缺陷)

- `_cap_world_case`:
  - ts 為空字串、帶尾空白、非字串(`None`、`True`、`5.0`)、無時區、解不開,一律判 required(偏嚴,符合 S5)。
  - ts 等於生效時間與跨時區同一刻都判 required。
  - decision 不是 extra-round 或 accept-risk,判 ignored。
- `_retro_world_empty`:
  - 骨架空殼、清單為空的空殼、全空白字串判「沒填」。
  - `[]`、`""`、`false`、`0`、多鍵、缺鍵、格子是 `null` 都判「有填」。
- 重記與多筆人裁:
  - 重記同一迴圈,`world_verdicts` 只算一次。
  - 最新人裁是 accept-risk 時,不論回顧檔有沒有填 verdict,都不進統計。
  - 舊迴圈的 world_check 填字串,`--record` 與 `retro-stats` 都不丟例外。
- 網址檢查:`re.fullmatch(r"(?i)https?://\S+", …)` 在怪埠號、tab、全形空白下都沒有例外,行為符合 S2。

v1/v2 兩處新程式碼的正確性沒有找到會做出錯行為的輸入;需要處理的是 F1(補一支今天就能跑到「要求」分支的測試,或改成讀回寫進帳的 ts)與 F2(守衛改成能看見值的變動,並把 `<=` 改成 `<`)。實驗與 clone 都留在 `/tmp/lumos-seat-work/code-跑滿後查世界方向/正確性-sonnet/`,請編排者收貨後刪;我已刪掉自己跑 `--suite docs` 留下的兩份 `gctl-run-*` 現場。
