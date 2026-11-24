severity: minor

我逐句對照了計劃、兩篇系統筆記、兩份手冊和 scripts/lumos(HEAD 22751fcc)。旗標名、環境變數和 choice-points 標示文字都對得上。`--only` 提示字面、斷路器計數、結果資料夾圍欄和合併基準上限公式也一致。`cmd_guard_kill` 的其他呼叫端(人裁 situation-rule、guard kill)不傳 `merge`,`on_first` 預設 None,行為不變。我沒有找到會讓照文件操作出錯的 major。也沒有跑任何測試或實驗(沒動 repo),結論來自讀 patch 和讀 repo 原始碼。

**讀帳者對新舊欄位**
- `_choice_ledger_status` 用 `.get("judged")`,舊帳缺欄位不會出錯。
- `ck` 缺 `judged` 時讀成 single。
- `_GOV_FIELD_TYPES` 新加的 `judged`、`merged`、`single`、`base_secs`、`merge_tripped`:我在 `docs/.governance-log.jsonl` 和 scripts/lumos 裡找過,沒有別的事件用這些鍵名,不會撞型別。
- `ck` 目前只被 `_gov_choice_count_one` 消費,新增鍵不影響它。
- 推送閘走 `_choice_disposition`,不讀判法欄位,也不比對狀態字串。
- 手冊寫的 `--no-merge --only` 重判流程走得通:merged 存活的行在 `_choice_kill_pick` 屬 survived,`--only` 會重跑。

**pitfalls manifest 兩條**
- 第 28996 行是 `with open(target, encoding="utf-8") as fh:`,判誤報。
- 第 29007 行是 `with open(target, "w", encoding="utf-8") as fh:`,判誤報。
- 兩處都有 with。寫入那處沒接 OSError,但逐支流程原本的寫入(`scripts/lumos:28518`)也一樣沒接,不是這次新增的洞。

**圖譜鏡頭**
- 這次沒有附固定席節點。
- 我看過的筆記(兩篇 Systems、計劃)沒有被這份 diff 破壞的硬合約。
- guard-kill 的「不傳新參數行為不變」是由 `merge=None`、`on_first=None` 兩個預設值守住。

## 1. 計劃說「沒啟用合併的原因」會印到標準錯誤,程式不印也沒人讀
severity: minor
blocking: 否
引句:「新增的提示(沒啟用合併的原因、斷路器跳開)一律印到標準錯誤」
file: `scripts/lumos:29081`、`scripts/lumos:29086`
- 計劃〈做法〉1 說條件不合時「不印字」,〈做法〉5 又說「帶出來:每個平台組有沒有啟用合併與沒啟用的原因」並印到標準錯誤,兩處矛盾。
- 程式只在基準階段不乾淨時印原因。時限不夠量齊、run_cmd 形狀不合、名稱檢查沒過、平台 flaky、筆記未提交這幾種,`_KillMerge.plats` 填了 `(False, "條件不合")`,卻沒有任何程式讀它去印或記帳。
- 接手的人跑完看到 `merged=0`,沒有任何訊號說是哪個條件擋了合併。
- 重現:對一個 run_cmd 是 `{python} tests/run.py {method}` 的平台跑 choice-kill。stderr 沒有合併相關字樣,`run` 事件的 `merged` 是 0。

## 2. `base_secs` 計劃寫「沒量齊是 0」,程式在量一半時也會累加
severity: minor
blocking: 否
引句:「`base_secs`(整數,開跑量基準花的秒數;沒量齊時是 0)」
file: `scripts/lumos:28974`
- `_kill_merge_base` 的 `finally: mg.base_secs += ...` 無論基準階段怎麼結束都累加。
- 情境:64 支單支基準量了約 6 分鐘,合併基準 rc 非 0,這個平台組改走逐支。run 事件的 `base_secs` 約 360,不是 0。
- RETIRE-IF ② 用 `(secs − base_secs) ÷ ran` 比合併呼叫和 `--no-merge` 呼叫。這種呼叫的壞法其實全走逐支,卻被扣掉量基準的時間,合併看起來比實際快。
- 規格閘那條 WHY 的「量了就無條件進位,沒量是 0」是程式的實際語意,和計劃〈做法〉5 的「沒量齊時是 0」互相矛盾。

## 3. RETIRE-IF / REVISIT 要讀的欄位沒有任何指令讀得到,② 的對照也無法驗
severity: minor
blocking: 否
引句:「REVISIT:2026-12-31 讀治理帳 choice-kill 事件的 `judged` 與 run 事件的 `ran`、`base_secs`、`merged`、`single`、`secs`、`merge_tripped`,照 RETIRE-IF 三條判」
file: `scripts/lumos:17943`、`scripts/lumos:17960`
- `_gov_choice_count_one` 和 `_gov_choice_count_verdict` 不讀 `judged`、`merged`、`single`、`base_secs`、`merge_tripped`,`gov --stats` 也不顯示。
- 三個月後要判 RETIRE-IF 只能手剖 jsonl。
- RETIRE-IF ① 的偵測路徑也有洞。合併判存活的行用 `--no-merge --only` 重判成殺掉,事件是 `via=run`,而且該鍵之前有 survived。這會被數成 `after["補測試後殺掉"]`,和「補測試後殺掉」無法區分。
- 重現:建一筆 survived(`judged=merged`),再追加一筆同鍵 killed(`via=run`)。`gov --stats` 把它列成補測試後殺掉。

## 4. `on_row` 列上的 `judged` 是死欄位,真正的判法來自另一處
severity: minor
blocking: 否
引句:「                    row["judged"] = "merged" if res.get("group") in self.merge.survived.get(res.get("platform"), ()) else "single"」
file: `scripts/lumos:28701`、`scripts/lumos:78914`
- 計劃〈做法〉5 寫 `_ChoiceKillRun` 收列時決定 `judged`。實作是 `finish` 自己用 `merge.survived` 和 `p["plats"]` 重算,`on_row` 完全不讀 `row["judged"]`。
- 同一個語意有兩份算法。改其中一份,帳不會變,也沒有東西會紅。
- 這是維護風險,沒有找到會讓帳記錯的輸入。

總結 max severity: minor
