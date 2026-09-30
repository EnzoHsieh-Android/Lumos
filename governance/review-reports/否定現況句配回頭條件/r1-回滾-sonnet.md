severity: major

## F1 照提醒配了條件式回頭條件,句子本身仍會被推送前筆記內容審判成推得出而擋住,提醒字樣沒講
severity: major
blocking: 是
引句:「條件式回頭條件本來就被內容審排除(」
file: `scripts/lumos:25720`
file: `scripts/lumos:25810`
file: `scripts/lumos:26292`
file: `scripts/templates/note-audit-judge.md:11`
1. 核對程式:內容審只跳過「那一行條件式回頭條件」(25720 的 cond 判斷),否定現況句本身照送審。判定者範本把 "there is no guard for X" 這類「缺什麼」直接定義成 CODE(範本第 11 行,證據寫 `=> 0`)。
2. `_note_audit_covered` 只認 CONTEXT 與 SKIP(25810)。CODE 與 MIXED 都算沒涵蓋;`note-audit skip` 明講「判過推得出的不能略過」(26292)。
3. 走一遍:寫「getMetrics 尚未實作,是下一個增量」(spec S1 自己的「算」例句)→ 提交時提醒,照 S5 字樣「緊鄰那一行加一行條件式回頭條件」→ 推送時判定者把這句判 CODE 或 MIXED → 沒涵蓋 → pre-push 與 CI 擋,不能 skip,只能刪句或申訴。配了條件只讓那一行免審,句子沒有免審。
4. spec 〈做法〉6 有講「最乾淨的寫法是把那句改寫成回頭條件本身」,但逐字釘死的提醒字樣(S5)只教「緊鄰再加一行」,第四行「程式碼查得到的現況就刪掉這句」排在最後、且沒說「配了也可能被刪」。真實使用者(含 agent)照第一段做,提交過、推送才被擋,兩道閘的指示相反,正是「左右為難」。
5. 影響面:量測裡「真句」的 55% 是條件可綁 symbol/file 的那類,恰好也是判定者最容易判成「缺什麼=CODE」的那類;所以被提醒又照做的多半會撞牆。RETIRE-IF ①「兩週內配上條件式的不到兩成就撤」也會被這個撞牆誤導成「提醒沒人理」。
6. 建議:提醒字樣第一種配法就寫成「把整句改成 REVISIT 本身」(REVISIT 行內容 `補上 X 之後…`),並在 S5 與 S4 之外多一條條款釘「配句子+條件」與內容審的關係(至少用替身判定檔測一次:句子 CODE 時 pre-push 的實際結果)。

## F2 回退清單漏了綁定測試、被改寫的節點與計劃自身的 REVISIT,「推送前後沒有要收拾的狀態」說過頭
severity: minor
blocking: 否
引句:「不寫帳、不寫檔,推送前後沒有要收拾的狀態;專案要先停提醒不必等回退」
file: `scripts/lumos:2807`
file: `scripts/lumos:2849`
1. 〈回退〉只列程式、範本、skill。實作還會加:條款 S1–S7 的七個 `[test:t_note_shape_negation_*]`、`t_graph_discipline_negation_revisit`、Systems/筆記內容閘的新 WHY 與被改寫的量測程式那段、計劃裡的 `REVISIT:[when-symbol:scripts/lumos::_ns_negation_hints]` 與上線後第 8 週日期式 REVISIT。單純 `git revert` 功能提交會一起還原,但 revert 之後別的提交若動過這幾篇(例如 8 週內量測結果寫進計劃)就會衝突,手動還原時清單沒列的部分會殘留:測試綁到不存在的函式、節點指向不存在的 `_ns_negation_hints`。
2. 範本還原後,已經 `lumos update` 過的消費專案 CLAUDE.md 帶著新鐵則 4(指向 skill 的寫法段),跟回退後的範本不同步,doctor Check D 會對每個已更新的專案報「紀律區塊漂移」(2807 起),要每個專案再跑一次 `lumos update`。回退段只講「重注入本 repo 的 CLAUDE.md」。
3. 「上線提交」定義用 `git log -S _ns_negation_hints --reverse`:回退再重上時第一筆仍是舊提交,8 週起算點不會重設;回退時要註明,或改用「最近一次新增」。
4. 建議:回退段補上述四項與「已更新專案要重跑 lumos update」;「沒有要收拾的狀態」改成「執行期沒有,文件與測試有」。

## F3 negation 設定值的邊角(null、false、大小寫)沒定,跟 drift_check.old_sentence 先例不一致
severity: minor
blocking: 否
引句:「寫了 warn/off 以外的值(含 `block`)→ warn 並印」
file: `scripts/lumos:28497`
file: `scripts/lumos:24738`
1. 先例 `_drift_old_sentence_config` 把 JSON `null` 當「沒寫」(28497 的 `if v is None`);`_note_shape_config` 則是 `ns.get("gate","block")`,`null` 會落進「看不懂」。spec 說「沒寫」→ warn 不印,「寫了 … 以外的值」→ 印,對 `"negation": null` 沒表態,實作者可能兩種都寫。
2. 想關掉提醒的人最自然寫 `"negation": false` 或 `"Off"`、`"OFF"`:照 spec 會得到 warn 加一行「看不懂」,而且 `_note_shape_config` 的警告是每次提交都印(不管有沒有改到筆記),使用者被同一行提醒每次提交重複打擾。先例 gate 也是大小寫敏感,所以不是新問題,但這是「關不掉」的入口,值得在字樣裡列出只認小寫 `warn`/`off`。
3. 已核對相容的部分:舊 lumos 只讀 `note_shape.gate`,多出的 `negation` 鍵被忽略;`note_shape` 不是物件、設定檔壞 JSON 時 `_note_shape_config` 已印警告,spec 決定 negation 不重複印,與 S4 一致。建議 S4 補一條 `null` 的測試值。

## F4 提醒沒有預先驗證條件會不會「寫下去就成立」的入口
severity: minor
blocking: 否
引句:「先確定那件事還沒發生:條件一寫下去就成立,這次推送會被漂移檢查擋下。」
file: `scripts/lumos:27406`
1. 已核對:新寫的條件式若終點已成立,`drift check` 會判「這次新寫(或改了條件)的回頭條件,條件已經成立」(27406),預設 block,所以 spec 這段描述成立。
2. 但提醒只叫人「先確定」,沒給指令。rtb 那 33 行裡 19 行是「句子早就過期」,也就是寫的人自己都沒發現東西已經在了;叫他們憑記憶確定,正是他們出錯的地方。提醒字樣沒有 `lumos drift check`(或推送前才會跑的那條指令)當場驗的寫法,第一次在 rtb 提交會先綠、推送才紅,又是提交與推送兩道閘的時間差。建議字樣加一行「寫完可先跑 `lumos drift check` 看會不會馬上成立」(指令名要對 spec 實作時實際存在的子指令)。

## 已讀,無 finding
- 〈範圍〉〈做法〉1、2:字眼表與過濾規則從回滾與相容鏡頭看無新增問題。
- 〈做法〉3 的早退改寫與只提醒不寫帳:對照 `cmd_note_shape`(25451 起)的現行流程,`hints` 只在 `--staged` 傳入、`--diff` 與 doctor 兩個呼叫端(25366)不傳,相容;block 的 return 1 在現行碼是「印違規、寫 blocked、回 1」一段連著,實作時提醒段必須插在 return 前,spec 已寫明,沒問題。
- 消費專案第一次提交:提交前掛鉤 rc0 時 stderr 直接顯示、只有 rc1 才擋(`scripts/hooks/pre-commit` Gate NS),所以 rtb 更新後第一次提交只會看到提醒、不會被擋;上線標記 `note-shape --staged` 字樣不受影響。
最高等級:major;blocking 共 1 條
