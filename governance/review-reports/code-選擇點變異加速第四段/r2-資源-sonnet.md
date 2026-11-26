severity: minor

資源鏡頭下沒有 major 發現。修補本身沒有引入新的孤兒程序或時間預算洞;一條原有的二次方成本只算 minor。

**Finding 1:事件行對名字的比對是「名字數 × 事件數」的二次方成本**
severity: minor
blocking: 否
引句:「evs = [e for f, e in last.items() if _choice_merge_hits([f], m) > 0]」
file: `scripts/lumos:28926` 附近(`_choice_merge_events` 的收尾迴圈)
- 這個迴圈不在修補差異內,只是修補改寫的解析函式旁的原有迴圈。
- 實測(Python 3.14,輸出已被 `_kill_cap` 截在 256KB,約 11,800 條事件行):10 個名字 0.05 秒,100 個 0.38 秒,400 個 1.48 秒。名字數受指令上限 32KB 約束,所以頂多數秒。
- 修補把每行的解析改成字串操作,這一步確實變線性:25 萬字元的單行(含 `" > "` 重複、`"a "` 重複等病態形狀)都在 1 毫秒內。
- 只在逾時或失敗路徑跑一次,不會把預算吃光,所以只算多花時間。
- 歸因:有證據的原有漏查。修補前後這個迴圈一字未動(見 r2-repair-review.patch 的 `_choice_merge_events` hunk,只換了解析行)。

**已驗主張**

1. 主張:斷路器恢復後,「跑到測試後掛住」的連續計數會從頭數。
   - input:先連續 14 次 `_kill_merge_breaker(..., H)`,再 5 次「逾時」計數類跳開,接著一次 pass 的試探恢復,再一次掛住。
   - expected:恢復後 `hang_streak` 為 0,再掛一次不會立刻跳開。
   - case_source:我自己組的最小重現。
   - before(54715c64 的 lumos 檔):恢復後 `hang_streak={'p':14}`,再掛一次 `plats=(False,'斷路器')`,等於一次掛住就跳開。
   - after(ac80263d):恢復後 `hang_streak={'p':0}`,再掛一次 `plats=(True,'')`、`hang_streak=1`。
   - attribution:有證據的修復回歸修好,這是修補提交的效果。

2. 主張:合併基準重試的逾時上限不再超過剩下的總時限。
   - 讀碼:原本重試與第一次共用同一個 `cap`,現在是 `min(cap, max(mg.remaining(), 1.0))`。
   - 重試只在 `why == "找不到 JUnit 結果檔"` 時發生,逾時不進這條路。
   - 逾時由 `_kill_run` 的 `TimeoutExpired` 分支以 `_kill_proc_group` 收掉整個程序群組並 `wait()`。
   - `KeyboardInterrupt` 分支同樣收組後再往上丟,重試路徑沒有新增孤兒程序。
   - 重試前仍呼叫 `c.hk.between()`。
   - 剩下的時限 ≤0 時重試只會有 1 秒上限,有界。
   - 我沒有跑端到端的重試,這條只讀碼,沒有 before/after 的行為證據。

3. 主張:`_kill_merge_trip` 抽出後,兩種連續計數的跳開行為一致。
   - 兩條路徑都設停用、`trips` 加一,並把 `cool`、`streak`、`hang_streak` 歸零。
   - 實測 5 次一般逾時跳開後 `streak=0`、`hang_streak=0`。
   - `hang_breaker` 參數預設等於 `_CHOICE_MERGE_HANG_BREAKER`,相鄰呼叫端沒傳參數,行為不變。

4. 主張:`_cmd_arg_quote` 與原先兩處內聯寫法等價。
   - 讀碼:Windows 用 `list2cmdline([x])`,其餘用 `shlex.quote`,與原寫法逐字相同。

**未驗範圍**
- 只實測了函式層,沒有跑真的 Gradle。
- Gradle 背景程序與測試執行器在逾時時是否隨 `killpg` 一起消失,我沒有驗。`_kill_run` 逾時只殺開在新 session 的 shell 群組,若 Gradle 背景程序脫離該 session,會殘留。這在本次修補之外,也無法從這份差異證實。
- 「連續 15 次掛住才停用」在慢機器上最壞要花 15 倍快篩上限,但每次都受剩餘總時限約束。這是計劃的刻意設計,沒有改動。

最高 minor,blocking 0 條
