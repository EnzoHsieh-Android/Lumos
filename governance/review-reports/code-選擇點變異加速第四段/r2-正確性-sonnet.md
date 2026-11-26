severity: minor

這輪修補沒有找到會做出錯行為的洞。只有一條低風險觀察,不構成阻擋。

我在修後版本 ac80263d 的副本跑了 `python3.14 scripts/test_lumos.py -k choice_kill_merge`,結果 299 passed、0 failed。

**finding 1**
severity: minor
blocking: 否
引句:「body, sep, ev = line.rstrip().rpartition(" ")」
場景:事件行改字串切後,行尾空白從原正規式的 `[ \t\r]*` 放寬成 `rstrip()`,連不換行空白(U+00A0)、全形空白(U+3000)也算空白。
- 輸入:`PASSED > a STARTED\u3000`。
- 修前(正規式):`None`。
- 修後(字串切):`('PASSED', 'a', 'STARTED')`。
- 我拿舊正規式和新函式對 30 萬筆隨機字串做差異測試,共 253 筆不同,全部是這種行尾空白。
- 把 `rstrip()` 換成 `rstrip(" \t\r")` 後不同筆數為 0,所以除了這一點,其餘判定都跟舊規格一致。
- 影響:Gradle 不會印這種行尾字元,只有頂格的假事件行才會被騙,而且只影響逐支排序。
- 計劃〈用詞〉寫的是「只准有行尾空白」,這個差異不違反字面。
歸因:有證據的修復回歸(只是字面上更寬,實害極低)。
- 兩版查證:修前用 `_CHOICE_MERGE_EVENT_RE.fullmatch`,修後用 `_choice_merge_event_line`,結果如上。
- 差異腳本在 `/private/tmp/claude-501/fz.py`。

**三問回答**

**①原問題的修復效果**

| 主張 | 輸入 | 預期 | 修前 | 修後 |
|---|---|---|---|---|
| 事件行解析不再二次方回溯 | 含六萬個 ` > ` 的長行 | 線性時間解完 | 舊正規式慢(有回溯風險) | 新測試要求一秒內,通過 |
| 重試上限照剩餘時限重算 | 兩支各 40 秒、基準上限 100、第一次花 70 秒 | 重試上限 ≤ 30 且不帶腳本 | 重試沿用原上限 100 | 新測試斷言 `caps[1][0] <= 30.0` 且不帶腳本,通過 |
| 恢復與跳開時兩個連續計數都歸零 | 15 次掛住、跳開、試探通過恢復、再掛 1 次 | 不再跳開 | 作者說恢復只清 `streak` | 新案例通過 |

- 重試上限那一條,我把測試所說的缺陷反向對照:若重試仍用原 `cap`,上限會是 100,測試會翻紅。
- 恢復歸零那一條,跳開時 `_kill_merge_trip` 已先把 `hang_streak` 清零,所以恢復處的那次清零與它重複。拿掉恢復處那行,測試不會翻紅,但行為也不會變,所以不是缺口。

**②修補處的正常、錯誤與相鄰路徑**
- `_cmd_arg_quote` 的函式主體跟抽出前逐字相同(Windows 用 `list2cmdline`,其餘用 `shlex.quote`)。
- `_run_cmd_expand` 抽出後沒有殘留對已刪除 import 的引用。
- guard kill、合約測試閘、過濾探針經 `_run_cmd_expand` 的 `{python}` 與 `{method}` 代換結果不變。
- `_choice_merge_cmd` 的引號行為不變。
- 檔內只有一處 `_cmd_arg_quote` 定義,沒有重複定義。
- `_KillMerge` 的 `hang_breaker` 是新增的最後一個選用參數,唯一的呼叫點 `_KillMerge(self.t0 + self.max_seconds, t0=self.t0)` 不受影響。
- 重試路徑只在原因是「找不到 JUnit 結果檔」且帶腳本時進入。重試通過後用回傳的 `mcmd`,`sh["init"]` 不再被讀;`_choice_merge_cmd` 只在兩個呼叫點用到,都在 `_kill_merge_base` 一帶。

**③新發現在修前與修後**
- 只有 finding 1,修前修後結果如上。

**圖譜鏡頭**
- `Systems/guard-kill.md` 的兩條 INVARIANT 不受影響:`_cmd_arg_quote` 只是搬移同一套引號邏輯,rc 優先序與 `--json` 純度沒動。
- `bound-tests-gate`、`lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`、`design-loop` 的合約都不牽連這次的 choice-kill 合併快篩邏輯。
- `guard-kill.md` 那條 WHY 的文字已同步更新為「沒產生結果檔才重試」與「恢復時兩計數歸零」。
- 這次沒有附「新增的殘留」段,殘留問答換號與第二個代理的題目不適用。

**未驗範圍**
- Windows 路徑下 `_cmd_arg_quote` 的行為。
- 平行測試時的事件交錯。
- 真實 Gradle 對初始化腳本的實際拒收樣子,只看了假 Gradle 測試。

暫存:我的副本在 `/tmp/lumos-seat-work/code-選擇點變異加速第四段/正確性-sonnet/w`,依規則請編排者收貨後刪。

最高 minor,blocking 0 條
