severity: blocker

我只讀了 spec 與 `scripts/lumos`,沒有實跑。tree 中途殘留的結論來自讀 `cmd_guard_kill` 的程式。

**會寫帳、寫檔、改判定、改挑壞法或改提示的入口,以及回退後各自怎麼辦(同族掃完)**

| 入口 | 回退後的痕跡 | 對應 finding |
|---|---|---|
| `invalid` 事件 + `_choice_pick` 的 `skip` + 行狀態 `exhausted` | 沒有任何東西會讓 skip 失效,`exhausted` 的行永遠不被重驗 | 1、2、3 |
| 壞法事件 `via:"cov"` 與 `_choice_kill_pick` 帶過去 | 舊程式會把沒跑過的存活永久帶過去 | 4 |
| `choice-cov/`、`choice-layer/` 的工作目錄檔 | 沒有任何東西清它們 | 5 |
| 合批編譯檢查的套壞法與還原 | 失敗路徑沒有保證還原 | 8 |
| `prep` 的呼叫位置 | 現有的合併快篩關閉開關會連帶讓新功能整個不跑 | 6 |
| `compile_cmd` | 只靠設定檔關不掉 | 7 |
| `cov-audit` | 不更正舊紀錄 | 9 |
| 續跑快取 | 鍵不含壞法行集合與工具版本 | 10 |
| `reach`、`layer`、`reach-run` 事件、判讀檔 | 舊程式讀到只會略過,無害,見最後的已讀無 finding | 無 |

1. 〈用詞〉合批編譯檢查:編不過與「環境壞了」沒有區分,會把所有壞法全判成無效,推送閘整個放行。
severity: blocker
blocking: 是
引句:「對不回的錯誤(在沒有壞法的檔或行)整批改成逐個編譯找出元凶」
   - spec 沒有要求先確認未套壞法的原樹能編過。
   - Gradle 掛了、離線、逾時,或樹上本來就有編譯錯,都是「對不回壞法的錯誤」。
   - 之後逐個編譯每個壞法也都失敗,每行候選用完,全部記 `invalid`、行狀態變 `exhausted`。
   - `exhausted` 比照乾節點不擋,所以整批改動悄悄零檢查就放行,而且 `invalid` 事件已寫進版控帳。
   - 下次 run 靠 skip 讀回,這些行不再被重驗(見 finding 2)。
   - 「只有元凶記 invalid」的預期值(S17)在原樹本身就編不過時不成立。
   - 修法方向:先編原樹、原樹紅就中止整個編譯檢查,不記任何 `invalid`。

2. 範圍 6 與〈回退〉2:`exhausted` 一旦記下就沒有出口,而〈回退〉寫的逃生門做不到。
severity: major
blocking: 是
引句:「就在那一行記一筆 `lint-waive choice:` 或改碼讓行指紋變」
   - `_choice_waive_target` 只收 status 為 `mutant` 或 `not_unique` 的行。
   - 其他狀態(`exhausted` 也是)會回 rc2「沒有壞法——不用放行」,見 `scripts/lumos:79819`。
   - `exhausted` 的行不產壞法,不會交給 prep,所以不會再編。
   - 同一行就算後來環境好了、型別變了,候選其實編得過,也永遠不被驗。
   - 改碼讓行指紋變不算回退,是繞道。

3. 範圍 6:skip 的定義與〈回退〉2「這一段保留」互相矛盾,`at_sha` 記了卻沒人用。
severity: major
blocking: 是
引句:「`_choice_pick` 多一個 `skip`(這一行最近一次 run 的 invalid `new_sha` 集合)」
   - 關掉合批編譯檢查後再跑的那次 run 不會產生 `invalid`。
   - 照字面,「最近一次 run」的集合是空的,那行立刻被打回候選 1。這正是〈回退〉2 說保留 skip 要避免的事。
   - 反過來,若解讀成取該行歷來最近一筆 `invalid`,它不分 `at_sha` 永久有效。
   - 程式碼改到讓候選本來編得過時,這一行仍被 skip。
   - 〈範圍〉、〈用詞〉都沒寫 `invalid.at_sha` 拿來做什麼。

4. 〈回退〉1、4:`via:"cov"` 的存活在整段程式撤掉後,會被舊程式永久帶過去而不重跑。
severity: major
blocking: 是
引句:「會重跑(範圍 6),不會留下沒跑過的存活」
   - 現行 `_choice_kill_pick` 在 `disp == "survived"` 且 `tests_sha` 相同時就帶過去,不看 `via`,見 `scripts/lumos:79072`。
   - 〈回退〉1 的保證只在「新程式把 coverage 關掉」成立。
   - 〈回退〉4 只寫「照 1、3」,沒有要求保留 `via:"cov"` 的判斷。
   - 退回舊程式後,這些沒跑壞法的存活照樣擋推送,而且 `tests_sha` 不變就永遠不重跑。
   - 現行 `_choice_disposition`、`_choice_ledger_status` 也把它當真存活。
   - 〈回退〉4 要明寫:撤掉前保留帶過去規則,或先對這類事件寫補償事件。

5. 〈回退〉4:「14 天清檔規則」清不到 `choice-cov/` 與 `choice-layer/`。
severity: major
blocking: 是
引句:「工作目錄的 `choice-cov/`、`choice-layer/` 由 14 天清檔規則清掉」
   - `_note_audit_work_dir` 只清頂層的 `*.md`:`d.glob("*.md")`,見 `scripts/lumos:56735`。
   - 工作目錄是 `.lumos/note-audit`,見 `scripts/lumos:55914`。
   - 子資料夾裡的 `.exec`、JSON 與 `choice-layer/<編號>-<序號>.md` 都不會被清。
   - 每次覆蓋基準的 `.exec` 依 `at_sha` 累積,沒有人刪。
   - 回退後也留著,但〈回退〉說會清。
   - spec 沒有為這兩個新子資料夾定義清理。

6. 範圍 2:`prep` 的呼叫位置自相矛盾,現有的關閉開關會讓新功能整個靜默不跑。
severity: major
blocking: 是
引句:「guard-kill 在 `_kill_merge_iter` 先量齊基準的同一個位置呼叫它」
   - 〈用詞〉寫的是「建好隔離工作樹後、跑任何配方之前」。
   - 但 `mctx` 在 `merge is None` 時為 `None`,迴圈直接跑 `plist`,根本不進 `_kill_merge_iter`,見 `scripts/lumos:28478`。
   - `--no-merge` 與 `LUMOS_SKIP_CHOICE_MERGE=1` 都會讓合併快篩關閉,見 `scripts/lumos:79397`。
   - 結果是編譯檢查與覆蓋整個不跑,也沒有任何提示。
   - 這兩個現有的回退開關,〈回退〉完全沒提它們與新功能的關係。
   - `--reach-only` 才與 `--no-merge` 互斥,一般 run 沒有寫。
   - 合併道不足 2 支、`_kill_merge_ready` 回 `None` 的路徑也沒說 prep 是否仍執行。

7. 範圍 1 與〈回退〉2:`compile_cmd` 只能靠設定檔關,但 Android 沒寫就用預設,關不掉。
severity: major
blocking: 是
引句:「平台設定拿掉 `compile_cmd`(Android 預設改成關)或撤掉那段」
   - 範圍 1 規定沒寫時 Android 用預設(開)。
   - 拿掉鍵反而是開,沒有 `false` 或 `--no-compile-check` 之類的關法。
   - 括號裡「Android 預設改成關」是改程式,不是設定回退。

8. 範圍 2 與〈用詞〉合批編譯檢查:套壞法的失敗路徑沒有保證還原。
severity: major
blocking: 是
引句:「每次編譯的逾時照 guard-kill 量基準的上限 `max(600, floor)`」
   - 只寫「最後還原」,沒要求 try/finally。
   - 編譯逾時,或 rc 非 0 而解析不出錯誤時,語意沒定義。這種情形多半是環境故障(見 finding 1)。
   - 第一批的壞法有換候選時,第二批套的是還原後的原樹,還是疊在前一批上?沒寫。
   - 還原失敗時沒寫要照 `mstate["unsure"]` 標弱證據。
   - 若還原沒做完,同一棵樹接著量覆蓋基準,基準會在壞法樹上量。
   - 一般中斷時 `_isolated_worktree` 的 finally 會拆樹;但 `--keep-worktree` 保留現場的路徑會留著壞法樹。

9. 範圍 5:抽查發現覆蓋判錯後,更正路徑只管本次 run。
severity: major
blocking: 是
引句:「這次 run 的 `none` 一律改成照跑(等於斷路)」
   - 之前的 run 已記的 `via:"cov"` 存活,在 `cov_sha` 不變、覆蓋仍開時照樣被帶過去。
   - 〈實務隱患〉「下一次 run 重算」只在 `cov_sha` 變或關覆蓋時成立,見範圍 6。
   - `cov-audit killed:true` 沒有任何讀者會據此作廢舊的 `via:"cov"` 事件。
   - 只抽 `none` 的 2 行:`clause` 行選錯子集造成的漏殺完全沒人抽。
   - 抽 2 行對 N 行的偵測力也沒量。

10. 範圍 2 續跑快取:鍵不含壞法行集合與覆蓋設定版本,會用過期結果判出假的 `none`。
severity: major
blocking: 是
引句:「鍵是平台、測試名、測試所在檔 blob;同一個 `at_sha` 再跑時直接取用,被中斷的 run 下次接著跑。」
   - 快取存的是「經過的壞法行」,它依賴那次 run 的壞法行集合。
   - 同一個 `at_sha` 下,`--only`、換候選(行範圍變)、範圍不同都會讓行集合不同。
   - 取到舊快取時,新壞法行不在已存的集合裡,被判成沒經過,判成 `none` 記 `via:"cov"` 存活。
   - 鍵也不含 init script 或 JaCoCo 設定版本。
   - 設定修好後,同一 `at_sha` 的 14 天內仍取到「覆蓋全 0」的舊結果。

11. 範圍 8 的清單檔放在工作目錄,卻沒寫清單遺失時怎麼辦。
severity: minor
blocking: 否
引句:「之後的 `--part n --list <編號>` 從清單取,不重算」
   - 清單被刪(finding 5 的清理改好之後也一樣會被 14 天規則清)或換機器時,`choice-layer <結果> --list <編號>` 沒有定義行為。
   - 待複核與 `--redo` 的更正路徑本身走得通:`--template` 對非有效的存活出材料。

12. 範圍 9:判讀檔資料夾與 `_BOOKKEEPING_DIRS` 的效力只在新程式成立。
severity: minor
blocking: 否
引句:「加進 `_BOOKKEEPING_DIRS`,同 `governance/reread-verdicts/` 的先例,提交它不會讓代碼審留痕失效」
   - 退回舊程式或安裝版落後時,已提交的 `governance/choice-layers/` 不在簿記名單。
   - 〈回退〉3「要清就 git rm 並拿掉」也沒說「留著檔但拿掉名單」的後果。

已讀,無 finding:
- 舊程式讀新 kind:`_choice_ledger_index` 要求 `kind == choice-kill`,`gov` 的 kind 分支對 `reach`、`layer`、`invalid` 都不處理,所以只是略過。
- 新欄位名(`reach`、`layer`、`killed`、`cov`、`judgment`、`at_sha`)在現有帳裡沒有型別衝突。
- `t_loop_close_kinds_classified` 只看 design-loop 與 code-loop 兩個閘,新 kind 不會讓舊程式的測試翻紅。
- `_choice_event_extra` 的 `judged:"cov"` 在舊程式只會被當成非 `merged`,顯示為「存活」。

實務隱患:
- 資源:有,覆蓋 `.exec` 檔無清理,見 finding 5。
- 不可逆:有,`invalid`、`exhausted` 與 `via:"cov"` 存活都無法退出,見 finding 2、3、4。
- 併發:無。單人單機依序操作,spec 已排除。
- 金流:無。只讀測試覆蓋。
- 對外送出:無。覆蓋在本機跑。

總結:最高等級是 blocker,blocking 共 10 條
