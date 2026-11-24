severity: minor

整合與知識同步這一席讀完修補差異。計劃筆記與 guard-kill 筆記有三處跟程式對不上,都是措辭、過期或綁定覆蓋面,沒有讓照文件操作會出錯的矛盾。另外把筆記說法逐句對了程式。

鎖檔 `…5319e1.json.warming` 不存在,沒有要處理的鎖。我用 `git worktree add` 建了 after 版,對兩篇筆記跑了 `lumos lint`,結果都是 0 問題,之後已移除 worktree 與臨時目錄。

## Findings

### 1. 計劃〈做法〉4 末段的超時說法已過期,跟同篇〈做法〉3 打架
severity: minor
blocking: 否
引句:「+- **合併快篩**:刪結果資料夾、跑合併指令,逾時上限 = min(max(合併基準耗時 × 5, 下限), max(剩下的總時限, 1))」
file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:112`
失敗場景:本輪修補把快篩逾時上限加上 `min(…, max(remaining, 1))`,程式在 `_choice_merge_screen_cap` 也是這樣算。但同篇第 112 行(修補沒碰)仍寫「合併快篩一次最長是它的逾時上限(估 2.5–5 分鐘),所以一次呼叫最多超出 `--max-seconds` 一個合併快篩加一支逐支的時間」。修補後快篩最多只多出約 1 秒,所以第 112 行描述的超出量是修補前的行為。第 228 行「掛住的壞法多等一次快篩逾時(2.5–5 分鐘)」仍然成立,不用改。
重現:在計劃筆記裡對照第 95 行與第 112 行。
歸因:有證據的修復回歸。修補只改第 95 行,漏改同一篇的第 112 行。

### 2. 修補新增的四個機制只有一個綁到測試,其餘四支新測試沒有任何綁定
severity: minor
blocking: 否
引句:「+  PITFALL:合併快篩開跑量齊單支基準時,單支實際比「支數 × 10 秒 × 1.5」那道門的單價貴」
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:58`
file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:174`
失敗場景:這條 PITFALL 一行寫了三個症狀和五個修法(實測重估、登記後再看一次 interrupted、快篩上限、`_kill_merge_in_lane`、判法只算一份),卻只有一個 `[test:t_choice_kill_merge_budget_reestimate]`。`t_choice_kill_merge_signal_race`、`t_choice_kill_merge_screen_cap`、`t_choice_kill_merge_edges`、`t_choice_kill_merge_no_lane_chunk` 在兩篇筆記都沒被引用(grep 為證)。計劃條款 S6、S7、S9、S19 的 `[test:]` 也沒補,所以推送前的條款綁定閘不會跑這四支。
另外三處小的對不上:
- S6 與 S19 的條款句式沒寫重估收手這條退路。
- 〈出處:〉只列了 r1 的「正確性 #1 #2、資源 #1 #2 #3」,漏了 `_kill_merge_in_lane` 對應的通才 #2。
- 「一行一類」規則建議把三個症狀拆成三行。
重現:`grep -n "signal_race\|screen_cap\|merge_edges\|no_lane_chunk"` 在 plan 與 gk 都是 0 筆。
歸因:有證據的修復回歸。新測試是這輪修補加的,綁定沒跟上。

### 3. 計劃〈做法〉1 說「不改既有的 `_gradle_test_module`」,修補後它已被改成呼叫共用函式
severity: minor
blocking: 否
引句:「+    return _gradle_module_parts(task[:-len(":test")])」
file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:66`
失敗場景:計劃寫「不改既有的 `_gradle_test_module`:它的呼叫端 `_gradle_blocked_tasks` 靠『變體任務回 None』判『不擋』」。修補把它的後半抽成 `_gradle_module_parts`,函式本體確實被改了。我逐一核對 `:a:b:test`、`:test`、`test` 與 `testDebugUnitTest`,新舊回傳一致,行為沒變,只是這句敘述字面上不成立。
重現:對照該計劃行與修補差異。
歸因:有證據的修復回歸,屬措辭過期。

## 已驗主張(筆記說法對程式都成立)

- 重估公式:計劃寫「還沒量的支數 × 已量的平均耗時 × 1.5 超過剩下的總時限」。
引句:「+        if measured and mg.remaining() < sum(measured) / len(measured) * left * _CHOICE_MERGE_BUDGET_K:」
file: `scripts/lumos:28984`;`_CHOICE_MERGE_BUDGET_K` 在 `scripts/lumos:28726`,值是 1.5。
- 截斷處理:被剩下時限截斷而逾時的那支不寫進基準,回 False 讓這個平台組不合併,而且不印字,跟計劃〈做法〉5 的印字規則一致。
引句:「+        if b_to and cap < full:   # 被剩下時限截斷:不算這支的基準」
- `base_secs`:計劃寫「無條件進位、量了就記、量到一半就收手也照記、沒量是 0」。
引句:「+        mg.base_secs += time.monotonic() - t0」
這行在 `finally` 裡,收手與 `_KillHalt` 都照記;進位在 `scripts/lumos:79022`(`math.ceil`)。RETIRE-IF ② 的公式「(`secs` − `base_secs`) ÷ `ran`」也對得上。
- 判法只算一份:計劃寫「`judged` 不放進結果列,也不放進 `on_row` 交出的列」。
引句:「+        plats = p.get("plats") or ()」
`add()` 在 `scripts/lumos:78919` 與 `:78929` 建 `plats`,只收有配方的平台;`hk.merge` 在全檔已無殘留引用。guard-kill 的 INVARIANT「`guard kill --json` 純度」與「rc 優先序」不受影響,因為結果列不帶 `judged`。
- `_kill_run` 的 `merge` 參數:已從布林改成物件,全檔不再有 `merge=True` 的呼叫,只剩 `_ChoiceKillRun.__init__` 的無關預設值。guard-kill 的 `on_first` WHY 已同步改成「merge 給 `_KillMerge` 時…登記後再看一次 interrupted」。
- 筆記寫法:新 PITFALL 帶 `[出處:] [根因:] [修法:] [test:]`,符合 repo 前綴規則;被替換的 WHY 去掉了過期的複雜度數字。lint 兩篇都 0 問題。

## 三問的回答

- **原問題修復有何行為證據?** 這一席只讀筆記與程式,沒重跑兩版行為,**未判定**。修補列的測試已由 fix-check 證明綠,這只證測試綠。
- **修補處的相鄰呼叫路徑?** 本席只驗了共用 `_gradle_module_parts` 的兩個呼叫端:`_gradle_test_module` 與 `_gradle_unit_test_task`,空與 `:test` 輸入新舊一致。
- **新發現的同一案例修前、修後?** 三條都是文件與程式的字面對照。修前沒有這些字句,不適用雙版命令。

未驗範圍:假 Gradle 端到端行為、`_kill_merge_singles` 在各種時限組合下的實際執行。

總結:最高嚴重度 minor
