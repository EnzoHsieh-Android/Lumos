severity: major

## B1 S7 的量法照寫做不出來:choice-points 沒有 JSON 輸出,批 4a 範圍的右端 ff9c96a 在實驗專案找不到
severity: major
blocking: 是(S7 是上線前必交的驗證條款,照現在的寫法交不出紀錄,主要輸入不存在)
引句:「用主線版與本計劃版的 lumos 各跑一次 choice-points 輸出 JSON 比對」

1. `choice-points` 只印人看的文字行,內容是定位、列號、類別、`舊 → 新` 片段和帳上狀態。它沒有 `--json` 旗標(`scripts/lumos:85730-85734` 只有 `--diff`、`--branch`、`--repo`),輸出裡也沒有 new_sha(`scripts/lumos:79631-79646`)。
2. S7 要數「改挑行數」「變成不唯一的行數」「帳上 new_sha 跟新挑法對不對得上」。文字輸出只能比類別與列號;不唯一那一行有固定字樣,算得出來;但 new_sha 得一次性腳本自己對 `new` 片段算 sha256 前 16 碼。S7 沒寫這一步,「JSON 比對」這個說法本身是錯的。
3. 實驗專案範圍 `4f170b2..ff9c96a`:
   - `4f170b2` 存在,在 `batch4-impl` 與兩個 `backup/batch4a-pre-squash*` 分支上,不在 main。
   - `ff9c96a` 在 `/Users/enzo/harness/lumos-android-lab` 的 `git log --all` 裡不存在,在 batch3、batch4、batch4-impl、cov 四個複本也都 `cat-file` 失敗。
   - 備份分支名帶 `pre-squash`,實驗專案批 4a 很可能被壓縮過,原提交已消失。
   - ⚠ 我不能讀私有那份,不知道它在不在那裡。
   - `git clone --shared` 出來的複本拿不到這個提交,spec 沒有備案(換哪個右端、或改用 `HEAD`)。
4. 「會重跑的存活行數」要靠「帳上最新是依測試雜湊沿用」判定,也就是要用複本 HEAD 當下算出的守的測試雜湊去比。一次性腳本只讀治理帳算不出這個值。它得呼叫 `_choice_tests_sha` 這類內部函式,或把範圍內「最新一筆是 survived 且非 via cov」的行數當上界。S7 沒寫用哪一種。複本檢出在舊提交時,帳也只有到那個提交為止的紀錄,跟 HEAD 上的帳不同。
5. 實驗專案帳的格式沒問題:`docs/.governance-log.jsonl` 的 choice-kill 事件是扁平欄位,file、fp、new_sha、verdict、tests_sha 都在,我實際讀了一筆。

## B2 沿用存活改比 new_sha,等於讓「同一行沒換挑法」的存活行也會因無關編輯重跑,而 S7 只數改挑行
severity: minor
blocking: 否(安全方向,只多跑不漏;但 S7 的「會重跑存活行數」會低估)
引句:「帳上那筆的壞法(new_sha)跟這次挑到的一樣才沿用」

1. new_sha 是 `_choice_identity` 的產物:`old` 在整支檔不唯一時會往外多帶前後各最多 2 行(`scripts/lumos:79311-79332`,以 `_count_overlapping(text, old, stop=2)==1` 判)。
2. 所以同一行、同一行指紋、同一個壞法,只要檔內別處新增或刪掉一份相同文字,`old` 的長度就變,new_sha 跟著變。這些行指紋沒變,存活行的鍵 (檔, fp) 也沒變。
3. 新規則下這種行會被排進重跑。原本的沿用判定(`scripts/lumos:80075`)不受這種無關編輯影響。
4. 同理,型錄之前加列造成的候選順序漂移,也會讓帳上 new_sha 對不上現挑。S7 只在「改挑行」裡數,數不到這些行。
5. 修法:S7 的重跑計數改成「範圍內所有最新是依測試雜湊沿用存活、且帳上 new_sha 對不上現挑的行」。

## B3 存活行帳上沒有 new_sha 欄位時怎麼比,spec 沒寫
severity: minor
blocking: 否(缺欄一律走重跑,安全方向;實務上也不會發生)
引句:「帳上最新那筆的 new_sha 等於這次挑到的 new_sha 才沿用,不等就排進要重跑」

1. 帳的欄位檢查把 new_sha 列為選填字串(`scripts/lumos:18577`)。`evs[-1].get("new_sha")` 缺欄時是 None,`None == 字串` 為 False,依 spec 字面「不等就重跑」,缺欄的存活行一律重跑。
2. 我用 `git log -S` 查,`"new_sha": ident["new_sha"], "verdict"` 這段從第一個 choice-kill 功能提交 `8332cc620` 起就在 `_choice_event_extra` 裡。choice-kill 與 situation-rule 兩條寫帳路徑都有 new_sha,所以實務上沒有缺欄的舊帳。
3. spec 與 S9 都沒寫缺欄、或欄位不是字串時的走法,也沒有案例。建議在 S9 補一句「缺欄當不等」。

## B4 身分不唯一的行(identity None)在沿用存活那條不會走到新比對
severity: minor
blocking: 否(順序已經擋住,S7 有數)
引句:「`_choice_kill_pick` 沿用存活的那個分支(守的測試雜湊沒變的存活)多比一項」

1. `_choice_kill_pick` 先判 `x["status"] not in ("mutant","not_unique")`,再判處置,接著 `status == "not_unique"` 就 `nu.append` 並 `continue`(`scripts/lumos:80067-80072`)。沿用存活那個 `elif`(`80075`)只會收到 status 為 mutant 的行。status 為 mutant 的行,identity 一定非 None(`scripts/lumos:79433-79437`)。所以不唯一的行不會碰到 `x["mutant"]["identity"]["new_sha"]`,沒有 `None["new_sha"]` 的 TypeError。
2. 邊界:原本唯一、已存活被沿用的行,改挑後變成不唯一,會直接掉進 `nu`,不經過新比對。spec 已在 S7 要求數這個數字,不另外開條。
3. 實作時 S9 測試要把 new_sha 取值寫在 `status == "mutant"` 的前提下,不要在 `elif` 外面先取。

## B5 等級值驗證擋 bool 與擋壞值之後的行為
severity: minor
blocking: 否
引句:「的值不是 int 1、2、3 之一(布林值、字串、0、4 都算錯)」

1. 預期值表的 S3 用 `True`、`"1"`、0、4 各一次當輸入。素樸寫法 `v in (1,2,3)` 會放過 `True`(`True == 1`),這條測試會紅,所以 bool 擋得住。
2. 沒測到 `1.0`(`1.0 in (1,2,3)` 為 True)。spec 文字寫「int」,要用 `type(v) is int` 才擋得住浮點,spec 沒指明寫法。
3. 這些壞值走到 `_choice_pick_iter` 時怎麼辦沒寫。「每一級各自取出」若寫成 `for lvl in (1,2,3): [c for c in cats if tiers.get(c,3)==lvl]`,值是 0 或 4 的類別會整類消失。spec 只說「查不到的當第 3 級」,沒說「查得到但值非法」。
4. 因為正式路徑上自檢先擋,這只影響直接傳壞 tiers 的單元測試。建議補一句「值不在 1..3 的當第 3 級」。

## B6 `--only` 指定一行時
severity: minor
blocking: 否
引句:「殺掉、放行、依覆蓋判的存活、過期、跑不出結果的分支不動」

1. `only is not None` 時,依測試雜湊沿用那個 `elif` 本來就不成立(`only is None` 在條件裡,`scripts/lumos:80075`),一律重跑。新增的 new_sha 比對對 `--only` 不生效,不會產生新行為,也不會誤擋。
2. 那一行的壞法已是新挑法,沒有「畫面是新壞法、帳上是舊壞法」的錯位。
3. spec 沒提 `--only`,可補一句「`--only` 不受影響」,也可以不補。

## B7 合批編譯跳過集合在新順序下用盡整條候選序列
severity: minor
blocking: 否
引句:「上一級沒有產得出的壞法(全被型別前提排除、產不出編輯、或全在跳過集合)就往下一級取,全部取完才是用盡(exhausted)」

1. `_choice_line_pick` 的 `exhausted` 判斷是「`pick(skip=sk)` 為 None 且 sk 非空且不帶 skip 的 `pick()` 非 None」(`scripts/lumos:79431-79443`)。這個判斷只看候選序列,不看順序,新順序下語意不變。
2. 跳過集合以 new_sha 比對(`scripts/lumos:79389`),跟順序無關,spec 說「換順序不會誤跳或漏跳」成立。
3. 邊界:`identity is None` 的候選永遠不在跳過集合裡(`scripts/lumos:79389`)。新順序下,第 1 級第一個候選若身分不唯一,就一定回傳它,而不是往下一級找唯一的。舊順序有同樣的性質,不是新引入,S8 預期值表也沒覆蓋這個組合,可以補一個案例。
4. S8 的「再把 ROR 的候選也全放進跳過集合,回用盡」,依上面的判斷成立。

## B8 S7 的一次性腳本與 `git clone --shared` 的其他前提
severity: minor
blocking: 否
引句:「另用一次性腳本(放會談暫存區、不進 repo)讀實驗專案治理帳」

1. `choice-points` 有 `--repo` 旗標可以指到複本,所以「用主線版與本計劃版各跑一次」可行,但要事先備好兩份 lumos 的執行路徑。
2. 複本是 `git clone --shared`,實驗專案的 `docs/.governance-log.jsonl` 在複本裡是被追蹤檔,內容就是複本檢出的版本。B1 第 3 點的提交缺失,會讓這一步也拿不到範圍當下的帳。
3. 這些已併進 B1 的修法:S7 要先寫明實際可用的範圍右端、怎麼取 new_sha、怎麼取守的測試雜湊。

## 牽連節點 `Systems/規格閘`
已讀。它是計劃要補寫的家,0 份計劃、20 行 KEY、0 條合約。三級挑法只改類別順序,沿用存活多比 new_sha 屬於「有效處置」那條 WHY 已提到要補的句子,不動殺掉與放行的鍵 (檔, 行指紋)。我判這一波改動不會破壞該節點宣稱的行為。

## 其餘節
白話、做法的等級表與自檢、驗收條款 S1 到 S6 與 S8 到 S10、回退、不做、實務隱患、落點與依據來源:已讀,無 finding。

最嚴重:major
blocking 條數:1
