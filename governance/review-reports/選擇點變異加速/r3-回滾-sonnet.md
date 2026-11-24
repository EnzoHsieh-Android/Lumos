severity: major

## 入口清單與「判錯了怎麼辦」

好比整份帳是一本記帳簿,快篩只會多寫「存活」這一種字。下面逐一看,寫錯時能不能擦掉。

| 入口 | 判錯時的現況 | 結論 |
|---|---|---|
| choice-kill 事件(`verdict: survived`、`judged: merged`) | 同一鍵取最新一筆。只有 `--only` 能重判,一次一行,見 F1、F2 | 能擦,但有洞 |
| run 事件(`merged`、`single`、`merge_tripped`、`ran`、`secs`) | 只餵統計與 RETIRE-IF,推送閘不讀 | 判錯不影響閘,但統計會失真,見 F4、F5 |
| 快篩記存活的 `weak` 欄 | 已讀 `cmd_guard_kill`:弱證據來源有整套一起跑、平台標 flaky、筆記未提交、修改時間沒錯開,共四個。spec 全部排除 | 無 finding |
| 中斷時不記帳 | `run()` 收尾對已中斷的壞法跳過 `finish`,不會記到半截的帳 | 無 finding |
| 殺傷力帳 `.kill-log.jsonl` | `source=choice-kill` 時整個不寫,快篩列不會漏進去 | 無 finding |
| 關閉開關 | 只管新紀錄,帳上既有的合併存活照舊,見 F2 | 不夠 |
| 還原功能提交後舊版讀新帳 | 舊版的 `_gov_event_types_ok` 與 `_choice_ledger_index` 只看已登記欄位與 `verdict`,不認得的 `judged`、`merged`、`single`、`merge_tripped` 都略過 | 成立 |

「`--no-merge --only` 會不會真的重跑守的測試沒變而帶過去的存活行」,我用 probe 腳本呼叫 `_choice_kill_pick` 實測,結果如下。

- 最新一筆是 survived 且沒放行:給 `--only` 就會重跑。
- 這一行在放行檔裡:`todo` 空、`done` 加一,靜默不跑。
- 最新一筆是 killed 且殺它的測試仍被條款綁著:同樣靜默不跑。

---

## F1 回退段宣稱的 `--only` 重判,對已放行的行靜默無效
severity: major
blocking: 是

- 位置:〈回退〉第一點與 S18。
- 問題:spec 說帳上懷疑有錯的合併存活用 `--no-merge --only <檔>:<行>` 重跑。實際上 `_choice_kill_pick` 在 `--only` 之前,先把處置為 waived 或 killed 的行算成「已有效處置」並跳過。
- 實際終局:快篩誤記的存活被推送閘擋下後,人最可能的處置是 `lint-waive choice:… --note "等價:…"`。這正是 `--only` 重判不到的狀態。
- 例子:放行檔有 `choice:a.kt:fpX`,帳上最新一筆是 `survived`、`judged: merged`。跑 `lumos choice-kill --no-merge --only a.kt:X` 會印「已有有效處置 1 行」、不跑任何 Gradle、rc 0。
- 對 S18 的影響:抽到被放行的行時,「10 筆都判存活」讀不到任何判定。RETIRE-IF ① 偵測合併漏殺,對人已碰過的行是盲的。
- spec 沒有說要先撤放行,也沒有提示輸出。
- 引句:「`--only` 本來就不受「守的測試沒變不重跑」限制」
- file: `scripts/lumos:78348`
- file: `scripts/lumos:82117`

## F2 關閉開關與 `--no-merge` 只管新紀錄,舊的合併存活沒有批次失效或清單手段
severity: minor
blocking: 否

- 位置:〈回退〉第一點、RETIRE-IF ①、〈不做〉。
- 問題:關掉合併後,帳上既有的合併存活仍被當作「守的測試沒變而帶過去」,不重跑,輸出照印「上次存活」、rc 1。
- 找出哪些行是合併判的:spec 只說「從帳上 `judged` 為 merged 的存活找」,沒有指令。`choice-points` 與 `finish` 的輸出都沒有合併標記。`--only` 一次只收一行(argparse 單值)。
- 成本:合併判存活的壞法,大多是真存活,逐支重判一個要約 6 分鐘。〈預期效益〉估存活 92–137 個,全部重判要約 9–14 小時,等於把省下的時間全還回去。
- 設計取捨:第二輪為了簡化拿掉 `merge_ver` 與 `--recheck`,這是代價。
- 補充:功能提交一旦還原,`--no-merge` 旗標就不存在,〈回退〉步驟一與步驟二的先後沒交代。
- 引句:「帳上已有的合併存活若懷疑有錯,用 `--no-merge --only <檔>:<行>` 重跑那幾行」
- file: `scripts/lumos:78354`

## F3 「存活會被推送閘擋下」忽略回報上限,誤判存活佔名額且重判釋放不了
severity: minor
blocking: 否

- 位置:WHY 的 [因:]、〈實務隱患〉第一點。
- 問題:推送閘只擋回報上限抽中的存活,上限是有增行的檔數乘 7。「曾經存活過的行」集合只增不減,重判成 killed 也留在裡面。
- probe 實測:40 行都存活、上限 7,抽中 7 行,另 33 行沒抽中、不要求。把抽中的 7 行重判成 killed 後,擋下 0 行,其餘 33 行仍沒抽中。
- 後果:快篩多記的假存活跟真存活搶同樣的名額。重判一次,名額就被白白燒掉一個。
- 方向仍保守:被擋的人多看一行,沒抽中的等於正確的 killed,不會放壞程式過閘。但 spec 寫的「存活會被推送閘擋下要人看」不精確。
- 引句:「存活會被推送閘擋下要人看,不會讓壞程式過閘」
- file: `scripts/lumos:78793`
- file: `scripts/lumos:78767`

## F4 〈登記〉稱 `ran` 已在 `ck` 子字典,實際上沒有
severity: minor
blocking: 否

- 位置:〈做法〉5 登記、RETIRE-IF 末句。
- 問題:`_gov_row` 的 `ck` 只取 `file`、`fp`、`killing_test`、`changed`、`mutant_lines`、`secs`、`reasons`、`site`。`ran` 不在其中。`_gov_choice_count_one` 的 run 分支也只讀 `changed`、`mutant_lines`、`secs`。
- 後果:S11 要求 `ck` 帶出 `ran`,是對的,但「既有的 `ran`」與「讀的欄位都在 `ck`」兩句與程式不符。RETIRE-IF ② 要用的 `secs / ran`,現在 `gov` 讀不到。
- 同族:`situation-rule --point` 寫的兩處 `_choice_event_extra` 事件沒有 `judged`,〈用詞〉只有 `merged` 與 `single` 兩種字串,沒交代缺值怎麼讀。
- 引句:「與既有的 `ran` 照 `_gov_row` 現有的 choice-kill `ck` 子字典慣例加進去」
- file: `scripts/lumos:18553`
- file: `scripts/lumos:17943`
- file: `scripts/lumos:79107`

## F5 回退重判與一次性基準會污染既有 RETIRE-IF 統計
severity: minor
blocking: 否

- 位置:RETIRE-IF ②、〈回退〉。
- 問題一:`--only` 把合併存活重判成殺掉,會被 `_gov_choice_count_verdict` 算進「存活後補測試殺掉」。父計劃 RETIRE-IF ① 的分母「被回報的存活」也包含假存活。
- 問題二:RETIRE-IF ② 拿上線前後每次呼叫的 `secs / ran` 中位數比較。上線後每次呼叫固定多約 6 分鐘單支基準加合併基準,且被殺的壞法多付一次快篩。小批次呼叫(`--max-mutants` 小)的比值會比上線前更差,可能誤觸「拿掉合併」。
- 引句:「同一專案上線後 run 事件 `merged` 大於 0 的呼叫,`secs` 除以 `ran` 的中位數,沒有比上線前(run 事件沒有 `merged` 欄)的呼叫低三成以上」
- file: `scripts/lumos:17968`

## F6 斷路器裡「乾淨」一詞與〈用詞〉定義衝突
severity: minor
blocking: 否

- 位置:〈做法〉3 斷路器、S8。
- 問題:〈用詞〉把乾淨定義成沒有任何失敗案例。斷路器卻寫「乾淨的一次(不論有沒有失敗)把計數歸零」,同一個詞的兩種語意。
- 照字面實作:有失敗的快篩不是乾淨,是否歸零沒有定義。
- 引句:「乾淨的一次(不論有沒有失敗)把計數歸零」
- file: `scripts/lumos:78208`

---

## 實務隱患逐類

- 守衛面:判錯方向是多記存活,不會記成殺掉。但判錯後的處置路徑有三個缺口:放行行重判無效(F1)、批次失效缺失(F2)、回報上限名額(F3)。
- 資源:基準階段一開始就量齊 64 支,預設 `--max-seconds 1800`。若使用者把總時限設得小於單支基準加合併基準(約 7 分鐘),那一次呼叫會一個壞法都不跑,而現在的用到才量不會。`--no-merge` 可退。無 finding。
- 效能:見 F5。
- 回滾:見 F1、F2。還原功能提交不碰帳,舊版讀新帳不出錯,這兩項成立。
- 相容:`_GOV_FIELD_TYPES` 新登記的 `merged`、`single`、`judged`、`merge_tripped`,與現有帳裡的欄位無衝突。已用 grep 確認帳與程式裡沒有同名欄位,而且 bool 屬於 int,不會被拒收。

## 圖譜節點逐條判

- `Systems/guard-kill` 的兩條合約(rc 優先序、`--json` 純度):不影響。`merge` 是選用參數,不傳時行為不變。`judged` 只放在 `on_row` 字典,不進結果列(S12 守)。
- `Systems/規格閘`、`bound-tests-gate`、`lumos-cli-lifecycle`、`lumos-cli-read`、`pitfalls-code-loop`、`test-quality-cli`:不影響。這份設計不改推送閘判定欄、不改 `test_quality.junit()` 的行為,只是逐檔多呼叫它。
- `Verification/測試品質第四輪修補驗證`:不影響。

## 逐節走查

- 白話、WHY、PRIOR-ART:已讀,無 finding。
- 舊否決比對:已讀,無 finding。
- 實測、用詞:已讀,見 F6。
- 做法 1:已讀,無 finding。
- 做法 2:已讀,見 F5。
- 做法 3:已讀,見 F6。
- 做法 4:已讀,無 finding。
- 做法 5:已讀,見 F4。
- 做法 6、落點、預期效益、不做:已讀,無 finding。
- 驗收條款與預期值表:已讀,見 F1。
- 回退:已讀,見 F1、F2。
- 實務隱患:已讀,見 F3。
- 依據來源、人裁紀錄、審計修正紀錄:已讀,無 finding。

發現共 6 條
