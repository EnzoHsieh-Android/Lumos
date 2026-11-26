severity: clean

我讀完 r2-repair-review.patch 的 scripts/lumos 與 scripts/test_lumos.py 兩段,沒有可標的 finding。只有 `_choice_merge_event_line` 在 `str.rstrip()` 上有一處和舊正規式不同的寬鬆,另一處是時限用盡時的重試上限,兩者都不構成 finding。檢查範圍是 /Users/enzo/harness/lumos-choice-speed4 在 HEAD ac80263d 的狀態,我只讀、沒改任何檔。

**邊界輸入實測**(python3.14 載入 scripts/lumos,直接呼叫 `_choice_merge_event_line`)

| 輸入 | 結果 |
|---|---|
| `A > t PASSED\r`、`A > t PASSED \t` | 認得,回 `('A','t','PASSED')` |
| 小寫事件字樣 `A > t passed` | None |
| tab 分隔 `A > t\tPASSED` | None,舊正規式同樣不認 |
| 只有事件字樣 `PASSED`、`A > PASSED`、`> t PASSED` | None |
| 名字空 `A >  PASSED` | None |
| 行首空白 `  A > t PASSED` | None |
| 名字含 ` > `:`A > x > y FAILED` | 在第一個 ` > ` 切開,名字是 `x > y` |
| 名字以空白結尾:`A > t  PASSED` | 名字是 `t `,與舊正規式的貪婪匹配一致 |
| 行尾多餘字:`A > t PASSED extra` | None |
| 含 10 萬、100 萬個 ` > ` 的長行 | 都在 1 毫秒內完成,沒有二次方回溯 |

**修補處的正常、錯誤與相鄰路徑**
- **`_cmd_arg_quote`**:只是把原本兩處內嵌的引號寫法抽成一支共用函式,Windows 走 `list2cmdline`,其餘走 `shlex.quote`。空字串、含空白或引號的路徑,兩邊產出和修補前逐字相同。
- **斷路器**:新函式 `_kill_merge_trip` 把兩條跳開路徑合併,並在跳開時把 cool、streak、hang_streak 一起歸零。試探快篩通過恢復時,streak 與 hang_streak 也一起歸零。我順著 `_kill_merge_breaker` 的各分支核對過,pass、fail、unclean、逾時、停用中試探都對得上。
- **重試上限**:改成 `min(cap, max(mg.remaining(), 1.0))`。重試前有 `c.hk.between()`,時限用完會先丟 `_KillHalt`。時限剩 0 或負數時,最多多給 1 秒,和第一次基準與 `_choice_merge_screen_cap` 的 `max(…,1.0)` 寫法一致。

**一處寬鬆差異,歸因:有證據的修復回歸,但只影響逐支順序、不改判定,不標 finding**
- 事件行在去掉行尾空白後才取最後一個空白之後的字樣。`rstrip()` 會吃掉 `\x0b`、`\u3000`、`\xa0` 這類字元。
- 這類行尾的事件行現在會被認得,舊正規式 `[ \t\r]*` 不認。實測 `'A > t PASSED\u3000'` 回 `('A','t','PASSED')`。
- 事件解析只用來排逐支順序、不判任何結果,所以後果有限。

**兩版對照(修前 54715c64,修後 ac80263d)**
- 修前我只看了 patch 的舊碼(`-` 側)並做推演,沒有實際載入跑;修後版本才實跑。
- 修前的長行回溯:舊 `_CHOICE_MERGE_EVENT_RE` 的懶惰 `[^\n]*?` 加後面的 `[^\n]+`,在無事件字樣的長行上會回溯,這是修補要解的問題。測試 `S2 解析:含六萬個 ` > ` 的長行一秒內解完` 是對這個行為的回歸釘。
- 修後:上面的 10 萬、100 萬個 ` > ` 長行都在 1 毫秒內完成。

**配對案例**
- 我沒有開 r2-behavior-cases.json,repair 與 preserve 選例沒有獨立核對。
- repair 案例的證據只有 patch 裡新增測試的程式與註解(S2 長行、S3 恢復後從頭數、S6 重試上限)。
- 這些測試我沒有實跑,所以「修復有效」只是推論,測試通過與否沒驗。
- preserve 面僅限上面的手動輸入:舊正規式有匹配的主要形狀(CRLF、尾端空白、名字含 ` > `、名字尾空白)新函式都得出相同結果。

**三問**
1. 原問題的行為證據:無回溯的實測見上;斷路器恢復後 hang_streak 歸零,靠 S3 新增兩條案例,是程式碼推論,未實跑。
2. 修補處的路徑:`_cmd_arg_quote` 與 `_choice_merge_events` 的呼叫端、`_kill_merge_breaker` 各分支在程式碼閱讀上都成立。
3. 新案例的修前與修後差異:只有上面的 `rstrip` 寬鬆一處。

**未驗**
- Windows 實機的 `list2cmdline` 行為。
- 上千支測試被 `_kill_cap` 截斷的完整路徑。
- 上千個名字時 `_choice_merge_events` 內 names 乘事件數的迴圈成本;這段修補前就在,不在這次差異裡。
- 全套測試沒跑。

最高 clean,blocking 0 條
