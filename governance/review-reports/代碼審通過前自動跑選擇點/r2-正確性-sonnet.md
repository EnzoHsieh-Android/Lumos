severity: major

我讀完整份 spec,並對照 `/Users/enzo/harness/lumos-finding-seat/scripts/lumos` 查證。範圍與同頂端的宣稱、事件去重與撤除條件、統計欄位三處有出入。

## 〈白話〉〈WHY〉〈PRIOR-ART〉〈舊否決比對〉
已讀,無 finding。方向(只預判、不跑測試)與 bound-tests-gate 固定席的 KEY:★INVARIANT★ 相容。那條合約只管 `code-loop check` 對綁定測試逐支真跑,而本案不動 check,也不在 pass 跑測試。pitfalls-code-loop 固定席目前只有「pass 前先跑新增告警與表態兩道」那條 WHY(`_codeloop_pass_mech`)。本案照同形狀接在後面,不破壞它。

## 〈範圍〉〈做法〉 範圍與「推送前同一頂端本來就會擋同一批」
severity: major
blocking: 是(照字面實作會在已推過的分支上擋下推送前不會擋的行)
引句:「判定跟推送前那道同一支函式、同一套範圍(推送前同一頂端本來就會擋同一批)」
- spec 的〈做法〉範圍一節規定 pass 用 `_choice_range(rr, None, None)`。該函式呼叫 `_push_range_start(rr, "0" * len(tip), tip, remote, ref)`,舊值固定傳全零,範圍等於分岔點到頂端的整條分支。file: `scripts/lumos:77837`。
- 推送前那道傳的是遠端舊值。`_push_range_start` 的說明寫「舊值找得到而且每一個分岔點都是舊值的祖先 → 用舊值(一般增量)」,所以第二次以後推的範圍只含新提交。file: `scripts/lumos:69640`。
- 反例:分支早在生效日(2026-11-16)前或更早就推過一部分。pass 會把那些舊提交的改動行也納入,要求它們有選擇點紀錄。
- 同一個反例的另一條路:後來的提交改動了舊行的鄰近行。行指紋(`fp`,每行的內容指紋,帳上以 (檔, fp) 為鍵)會變,舊行在 pass 就變成「缺紀錄」,增量的推送前卻不判它。
- 結果:pass 擋下、推送前不會擋,「提早抓到」的前提不成立。使用者要為已推過的行補 `choice-kill` 或 `lint-waive`。
- 這是現況對照錯誤,不是措辭問題。要嘛 pass 也傳遠端舊值(`_choice_range` 加參數),要嘛在 spec 明寫 pass 判整條分支、與推送前會不同。

## 〈做法〉事件、〈統計〉、〈實務隱患〉、RETIRE-IF、REVISIT:同頂端去重與撤除條件量不到
severity: major
blocking: 是(撤除條件在帳上算不出來,S9 的計數也會被去重吃掉)
引句:「同一個頂端、同一組原因照舊只記一次」
- `_choice_push_event` 的去重鍵是 kind、`head_sha`、原因清單,不含 `site`。file: `scripts/lumos:78756`。
- 同一頂端若先有推送前那筆,之後 pass 擋下就不會記,`site=pass` 的筆數會被低估成 0。反過來先 pass 後推送前,推送前那筆被吃掉。
- RETIRE-IF 與 REVISIT 要的是「pass 擋下的紀錄裡,過半在同一個 HEAD 推送前也會被擋」。去重正好讓這個比較在帳上不可能成立:同頂端兩邊只會留一筆。
- 〈範圍〉③ 規定的處置流程是「處置後提交,再重跑」,擋下之後 HEAD 一定前進。事件記的 `head_sha` 是擋下當下的頂端,而推送發生在新頂端。實際上幾乎沒有「同一個 HEAD」可比,條件只會永遠判成「沒有提早抓到東西」或永遠量不到。
- 需要明寫怎麼量,例如帳上多記 `site` 且去重鍵納入 `site`,或比較看原因與行指紋(`fp`),不看頂端。

## 〈統計〉 `gov --stats` 讀 `site`
severity: minor
blocking: 否(S9 會翻紅,實作者會發現,但 spec 漏列要改的地方)
引句:「數 `site == "pass"` 的 blocked」
- `_gov_row`(統計列的 mapper,把帳上事件轉成統計列)對 choice-kill 只帶 `("file","fp","killing_test","changed","mutant_lines","secs","reasons")` 進 `ck`。頂層欄位也只有 `verdict/row/attempt/reason/via/run_id`,`site` 都不在其中。file: `scripts/lumos:18550`、`scripts/lumos:18552`。
- `_gov_choice_count_one` 收到的 `r` 讀不到 `site`,spec 沒提要改這個 mapper。
- 再加上 `_GOV_FIELD_TYPES`(治理事件欄位型別登記)沒有 `site`(未列的鍵不檢查,所以不會讀壞)。其他既有讀者查過沒問題:`_choice_ledger_index` 只收 kind 為 choice-kill 的事件,blocked 事件的 `site` 它看不到;去重用 `token`,也不受影響。
- 另外,現有那行印的是「推送被擋 N 筆」,納入 pass 後字面不符,spec 沒處理。

## 〈做法〉場合參數:「要先提交才算」那一句放哪
severity: minor
blocking: 否(措辭層,但 S1、S7 的預期互相打架)
引句:「放行檔與計劃的改動要先提交才算(預判從頂端提交讀它們)」
- 〈做法〉把這句掛在「缺紀錄」的處置說明底下。
- S7 卻要求「survived 且放行未提交」時訊息含這句,而 survived 屬於「存活」。`_CHOICE_PUSH_FIX["存活"]` 沒有這句,「過期」「不唯一」也沒有。file: `scripts/lumos:78611`。
- 這句應該對所有原因都印,或在 spec 明說只印在哪幾類。

## 〈做法〉場合參數:殘留的推送字樣與事件備註
severity: minor
blocking: 否(顯示與帳的文字精度)
引句:「`[spec-gate 推送前]` 換成 `[code-loop pass 選擇點]`」
- `_choice_push_scan` 還印「裝 ast-grep 後再推」(`scripts/lumos:78807` 一帶)。
- 表壞那條 `_choice_bad` 也含「再推」。
- 範圍標籤 `how` 在 pass 傳入 A..B 時會是「推送範圍」。
- 擋下事件的 note 仍是「選擇點推送前擋下:…」,且 `_choice_push_round` 自己的 P 前綴與「沒有測試守」「這一圈放行」不在 spec 列的七個函式裡。
- 實作會漏換,pass 輸出和帳備註會混用「推送」字樣。

## 〈驗收條款〉S6 與預期值表
severity: minor
blocking: 否
引句:「當專案沒有圖譜資料夾、其他條件同 S1 時,`code-loop pass` 應 照 S1 擋下,不噴例外」
- S1 的前提是「碰到進行中計劃、計劃綁了測試」,而計劃就存放在圖譜資料夾。
- 資料夾真的不在 at_sha 那棵樹上時,`_choice_guard` 的 `live` 為空,走的是「無規格」那條擋下,不是 S1 的「缺紀錄」加 `choice-kill` 指令。`scripts/lumos:78838` 一帶。
- 若只是工作目錄刪掉、提交裡還在,則完全不影響判定。
- 預期值表那列只寫 rc 2,沒寫是哪一種原因,實際造得出來的是「無規格」。spec 需要講清楚是哪一種。「無規格」的處置建議(補 lands_in 或連結)對沒有圖譜的專案也無意義。

## 〈做法〉擋下與使用者照指示做
severity: minor
blocking: 否(能過,但多一個 spec 沒講的關卡)
引句:「處置後提交,再重跑 code-loop pass」
- 提交放行檔、計劃或補的測試,會讓 HEAD 前進,而這些都不是簿記檔。
- 排在前面的表態那道(`_dispositions_verdict`)綁提交,不在簿記白名單內的改動會讓舊表態失效。pitfalls-code-loop 節點明寫「pass 之後又提交程式、再 pass 一次時,舊表態綁的是舊提交,會被表態那道擋下」。
- 所以照 spec 指示處置後,第二次 pass 可能先被表態擋,要重答表態,這步擋下訊息沒提。
- 補測試、改計劃也是審查席沒看過的新代碼。〈實務隱患〉說「沒有新增沒審過的路徑」不完全對。這段改動落在代碼審之後,現在推送前被擋再處置也是一樣的風險,但 pass 擋下後又要重答表態才能過,spec 至少該說明這條路。

## 〈回退〉〈依據來源〉〈審計修正紀錄〉
已讀,無 finding。

## 已查證沒問題
- pass 讀工作目錄、推送前讀已提交帳:以 S2 流程為準,pass 記通過後提交帳是簿記檔,留痕仍有效,不會變成記錯帳。
- `_gov_rows_at(rev=None)` 的實作與 spec 描述一致,篩選與壞行丟棄成立,`_choice_ledger_index` 不會讀錯 `site`。
- 接點位置(`_codeloop_pass_mech` 之後、`_codeloop_pass_verify` 之前)成立,S8 成立。
- `_choice_range` 在主線、頂端已在主線時回原因,S10 放行成立。
- `_choice_push_round` 一族不讀 `env`,S6 的「不噴例外」那半成立。

最嚴重等級 major,blocking 共 2 條
