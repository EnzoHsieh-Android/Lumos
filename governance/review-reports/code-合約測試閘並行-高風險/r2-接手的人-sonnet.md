severity: minor

整份 diff 我讀完了。範圍包括計劃、Systems 筆記、06 與 07 手冊、`scripts/lumos` 的 `_run_bound_tests` 等待迴圈、`_bound_tests_log` 與提醒去重,以及九支新測試。我也實際執行了下列項目:

- `-k bound_tests_p` 與 `-k bound_tests_secs` 兩批測試,共 41 支和 5 支,全綠。
- 對兩篇筆記跑 `lumos lint`,0 問題。
- 計劃 REVISIT 那條 python 取數指令,在 repo 根目錄可以執行,輸出 `0 None`。因為還沒有帶 `secs_kind` 的列,這是預期結果。

沒找到會讓人撞牆的 major 問題。發現三條 minor,大意是:手冊與程式在邊角值上說法不一致;撤除條件與取數口徑對不上;一支測試太慢。

1. `parallel: 1.0` 靜默當 1,手冊與計劃都說小數會出聲
severity: minor
blocking: 否
引句:「    if v != 1 or isinstance(v, bool):」
- 07 手冊寫「寫錯(字串 `"4"`、小數、布林、超出範圍…)會印一句提醒並當成 1」。計劃〈做法〉寫「沒寫、1、布林、小數、字串、超出範圍一律當 1;有寫但不合法…印一句提醒」。
- 程式用 `v != 1` 判斷是否出聲,而 `1.0 == 1`。我實跑 `_bound_tests_parallel`,config 寫 `{"bound_tests":{"parallel":1.0}}`,回 1 且 stderr 沒有任何提醒。`2.5` 與 `2.0` 則會出聲。
- 接手的人照手冊把「小數」當成一定會被提醒的案例去試 `1.0`,會看不到提醒。S2 測試只測了 `2.5`,沒有蓋到 `1.0`。
- 歸因:未判定。我沒能在兩個版本上對照,因為 zsh 的 `git show <sha>:path` 指令被 `bad substitution` 擋掉。

2. S4 測試的 docstring 與實際程式、計劃數字不一致
severity: minor
blocking: 否
引句:「[合約測試閘並行執行 S4]閘回報與記帳的 secs 是跑測試那段的牆上時間:兩篇筆記綁同一支約 1 秒的測試,」
- 同一支測試的 docstring 後半寫「secs 要約 1 秒…會報 2 秒以上」。
- 但測試本體把 `run.py` 注入 `time.sleep(2.0)`,斷言是 `1.8 <= secs < 3.5`。計劃 S4 條款寫的是「約 2 秒 vs 約 4 秒」。
- 接手的人讀 docstring 會以為門檻是 1 秒,改測試時容易把斷言範圍改錯。測試本身有效:退回逐項相加會得到約 4 秒而翻紅。
- 歸因:未判定。

3. RETIRE-IF 與 REVISIT 的基準口徑對不上
severity: minor
blocking: 否
引句:「打開後連續 8 週合約測試閘耗時中位數沒有比打開前低三成以上」
- RETIRE-IF 說要比「打開前」。但同一份計劃的〈回退〉與筆記都說舊帳 secs 是逐項相加、沒有 `secs_kind`,不能比。所以帳上沒有可比的「打開前」數字,只有那一次手量的 176.5 秒。
- REVISIT 的取數指令把所有 `gate=bound-tests` 且帶 `secs_kind=wall` 的列取中位數,沒有分 kind。低風險 advisory 推送、範圍很小的跑法都會拉低中位數,而 176.5 是一次涵蓋 51 支的完整範圍。
- 結果是 2026-12-15 比較出來的數字會系統性偏好,可能誤判「達標」。
- 接手的人當天照指令跑會得到一個數字,但沒有寫明該跟誰比、要不要分 kind。
- 歸因:未判定。

4. `t_bound_tests_parallel_config_values` 單支要跑約 62 秒,餘裕只有 3 倍
severity: minor
blocking: 否
引句:「def t_bound_tests_parallel_config_values():」
- 我實跑,這支測試報 `62.6s … (餘裕 3x) ⚠ 餘裕不足 3 倍`。原因是 10 個案例中有 8 個是循序案例,每個固定等 2 秒看有沒有別支同時在跑。
- 機器負載高時這支測試可能逼近上限而間歇紅。接手的人遇到間歇紅,第一反應會懷疑並行實作而不是測試太慢。
- 歸因:未判定。

## 三問
由於本席鏡頭是整合與知識同步,我只對下列條款做了行為核對。我沒有讀 binding 的 behavior_cases,也沒有逐案跑修前版本,所以修前結果一律標「未判定」。

① 修復效果的行為證據:
- S5 `error_stops_fast` 在兩種排位下都綠,實跑 0.3 秒(單獨看這個數字偏低,我沒有深究計時範圍)。
- S6 的 CPU 小於牆上時間斷言有過。
- S7 中斷後最多開跑 2 支,有過。
- S4 與 S8 的 wall time 測試有過。
- 我讀碼確認:退回逐項相加、改用 `time.time`、或只 join 第一條執行緒,這三種退法都會翻紅。我沒有逐一做還原實驗。

② 正常、錯誤與相鄰路徑:
- 規格閘(`scripts/lumos` 7661 行)、`code-loop check`(48422 行)與修正關卡(13317 行)三處都走 `_bound_tests_check` 或 `_run_bound_tests`。07 手冊「規格閘與修正關卡也會同時跑」的說法與程式一致。
- `secs_kind` 不在 `_GOV_FIELD_TYPES` 內,但該表只驗證已列欄位,未列欄位照常通過。
- `lumos gov` 只對 fix-check 讀 `secs`(8707 行),計劃說「不帶 bound-tests 的 secs」屬實。

③ 新發現案例的修前修後:
- 只有 finding 1 做了修後實測,修前未判定。

## 未驗範圍
- 計劃量測的 176.5 秒與 55.8 秒是作者手量,我沒有重量。
- 「只改設定檔時風險分級是 light」我沒有驗證。我用 `pitfalls` 跑的範圍包含程式檔,結果是 standard,不適用。
- 我沒有跑 `lumos doctor` 與 `spec-gate`,所以 REVISIT 日期格式與八條條款的 spec-gate 判定沒驗過。

## 圖譜鏡頭(固定席逐條)
- `Systems/bound-tests-gate`(★INVARIANT★ 逐支真跑,任一紅、懸空、偽證據、unfilterable 即 rc1):
  - 判紅綠、逾時、證據與去重的邏輯沒動,只是改成先收集再排程、最後按原順序組結果。
  - 我看不出合約被破壞。S1 驗證了 N=1 與 N=3 結果相同。
  - 新增段落〈同時跑幾支與 secs 的意思〉與前面第 3 步、「帳的類別」、「回頭看條件」沒有互相矛盾。
- `Systems/guard-kill`、`測試假綠形態`、`lumos-cli-lifecycle`、`lumos-cli-read`、`design-loop`:
  - 這份 diff 沒有動 `_kill_run`、guard kill 的 rc 優先序與 JSON 純度、search 濾網、re-inject,也沒有動處置閘第五步,都不受影響。
  - `design-loop` 第五步要求計劃有 `[SN]` 時條款綁 `[綁定測試:有]`。新計劃的八條條款都有 `[test:]`,我沒跑 spec-gate 驗證。
  - 測試假綠形態要求前置斷言。S2、S4、S5、S6、S7 都有「前置」檢查,與該合約同向。
- `loop-convergence-recording`、`pitfalls-code-loop`(★RISK★):這份 diff 沒有動它們的程式路徑。
- 其餘超出上限、只列名的節點:沒有牽連。

總結:最高等級 minor
