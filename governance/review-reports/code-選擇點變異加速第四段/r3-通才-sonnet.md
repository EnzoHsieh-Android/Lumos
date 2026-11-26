severity: minor

**finding 1**
severity: minor
blocking: 否
引句:「if kind != "pass" and sh.get("init") and why == "找不到 JUnit 結果檔":」
file: `scripts/lumos:29116`、classify 回這串的地方在 `scripts/lumos:28937` 附近
問題:重試的條件靠字串相等判定。classify 一改字樣,重試就悄悄不再觸發,而測試只釘住了現在這個字樣。條件也太寬:合併基準「帶腳本」、rc 非 0、沒有結果檔,不管原因都會重跑一次。具體場景是合併道的篩選串一個測試都沒選中,Gradle 回報 `No tests found`。這時腳本沒問題,卻多跑一次完整合併基準,上限是剩下的總時限。成本只是時間,而且每個平台組最多一次,所以只算 minor。
歸因:未判定(原有設計,不是這輪修復造成的)

**finding 2**
severity: minor
blocking: 否
引句:「第二段計劃加:unclean({平台: {沒跑乾淨的原因: 次數}})與」
file: `scripts/lumos:28972` 起的 `_KillMerge` 類別說明,後面接「(做法 4,只數計斷路器的那幾種)」
問題:這輪起,「逾時(跑到測試後掛住)」不計原本的斷路器,卻照樣累計進 `mg.unclean`,見 `_kill_merge_breaker` 的新分支 `elif why == _CHOICE_MERGE_HANG_WHY:`。類別說明和 `_kill_merge_breaker` 的說明都沒更新,仍寫「只數計斷路器的那幾種」。第四段計劃〈做法〉3 末條已經寫對了,所以是文件跟程式差一處。
歸因:未判定

**三問**

1. **有沒有證據顯示修復造成回歸?** 沒有。
   - 兩版 `scripts/` 相同,修前修後的程式行為沒差。
   - 修復只動文件。我逐條核對了修復補進計劃與測試敘述的主張,對得上現有程式:
     - 重試上限照剩下時限重算,見 `scripts/lumos:29119-29121`。
     - 「六萬個 ` > ` 的長行」不回溯:實跑 0.0016 秒。
     - 行尾 `\r` 認得:`"x.V > b FAILED\r"` 得到 failed=[b]。
     - `rstrip()` 會吃 `\xa0` 這類空白:`line.rstrip()` 的行為,與計劃新補的註記一致。
     - 恢復後兩個連續計數都歸零:見 `_kill_merge_breaker` 與 `_kill_merge_trip`。
   - 新增的 PITFALL 的 repro 在修後版本成立:`_choice_merge_events("x.V > foo (bar) FAILED", ["foo (bar)"])` 回 failed 空。
   - 修前版本我沒另行還原重跑。

2. **這一輪的新發現在修前修後各是什麼結果?** 兩條都是修前修後都存在,因為程式相同,文件也沒有觸及。
   - finding 1:兩版都有。
   - finding 2:兩版都有。

3. **整份快照有沒有上一輪沒人看的角落?** 我覆蓋的有:
   - `_cmd_arg_quote` 重用:POSIX 走 `shlex.quote`,Windows 走 `list2cmdline`,`{python}` 與 `{method}` 的行為不變。
   - `_isolated_worktree` 新增 `scratch` 欄位:呼叫者只有 `cmd_guard_kill` 一處讀它,另一處用它的是修正關卡,不讀 `scratch`。
   - `--init-script` 插入位置:接在 `--tests` 段之後、原字串其餘部分之前,不會落進引號內。
   - 重試路徑:`_KillHalt`、時限重算、`mg.base_secs` 在 finally 累計都有顧到。
   - 斷路器:
     - 兩個計數互不干擾,有失敗只歸零掛住計數。
     - 試探分支會累計掛住原因,但不恢復、也不再跳開。
     - 跳開與恢復時兩個連續計數都歸零。
   - 排序:
     - `_kill_merge_failed_first` 的紅、未知、掛住、通過四層正確。
     - 截斷時不判掛住,且 `STARTED` 在截斷後仍被當成「跑到測試」。
     - 兩份名單在 `_kill_merge_screen` 開頭都先清空。
   - gov:`_GOV_FIELD_TYPES` 與 `cmd_gov` 的 `ck` 都帶了 `merge_init_off`。
   - 效能:實跑 1300 支名字、2600 條事件行,`_choice_merge_events` 約 0.52 秒,是名字數乘事件數的二次成長,但落在合併指令上限內。
   - 表態記錄:這次改到的 Python 都是同步流程,沒有 async,表態的「不適用」我沒找到反例。

   未驗的有:
   - 真實 Gradle 或 Robolectric 下的事件行格式,我只信計劃裡的實測 FACT,沒重跑。
   - Windows 路徑的實際行為,只讀了程式,沒跑。
   - 帶 `-q` 或專案自己設了 `testLogging` 時的事件缺失,計劃已承認,我沒驗。
   - 測試檔本身我只讀了 diff,沒有逐支還原翻紅。
   - Kotlin 反引號含 `(` 的測試名排序退化,計劃的 PITFALL 已登記,我只驗了 repro。
   - 本席固定席節點(`bound-tests-gate`、`guard-kill` 等)的合約測試沒有重跑。
   - 這次改動沒動到各節點的 `KEY:★INVARIANT★` 合約行,我讀 diff 沒看到被削弱的跡象。

最高 minor,blocking 0 條
