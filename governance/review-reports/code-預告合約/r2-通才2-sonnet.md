severity: blocker

## F1 合約文字裡含字面 `[watch:` 或 `[due:` 會讓 settle/abandon 永久卡死

severity: blocker
blocking: yes

觀察到什麼:
`_guard_planned_line`(`scripts/lumos:10720-10747`)這次改成「比對剝掉 `[watch:]`/`[due:]` 之後的完整文字」,用意是修掉第一版「前 12 字相同就互相覆蓋」的問題(這點確實修對了,見下方「已驗證正確」)。但剝除用的是全域 `.sub()`:

引句:「body = DUE_REF_RE.sub("", WATCH_REF_RE.sub("", m.group(1))).strip()」

`m.group(1)` 是功能節點裡那一整行 KEY 行去掉 `★INVARIANT-PLANNED★` 前綴後的內容,包含「合約文字本身」加上指令自己附加的尾巴 `[watch:<gref>] [due:<日期>]`。`WATCH_REF_RE`/`DUE_REF_RE` 這兩個正則本身沒有出現在這次 patch 的變動裡(定義沒改),所以不引它——但下面這行 patch 新增的比對邏輯本身已經足以說明問題:全庫共用的這兩個正則套用 `.sub()` 沒有限定只能吃掉一次:

`.sub()` 不限次數,會把**整行裡所有**符合 `[watch:...]`/`[due:...]` 形狀的片段都拿掉——不只是指令自己附加在行尾的那兩個真正標記,連「合約文字內容剛好長得像這個形狀」的片段也一併被吃掉。

而拿來比對的另一邊 `want`(從守衛節點的「預告的合約:」那一行讀回來的原始 claim,`cmd_guard_settle`/`cmd_guard_abandon` 兩處都是直接讀,沒有做任何剝除)完全沒被動過。於是只要合約文字本身包含字面的 `[watch:...]` 或 `[due:...]`,兩邊在做字串比對前經歷的處理不對稱,永遠比不上。

怎麼重現(實際跑出來的,不是推論):

```
$ python3 scripts/lumos --vault /tmp/v1 guard plan Systems/Pay "系統應該處理 [watch:whatever] 的情況" \
    --plan Projects/退款_計劃 --phase P4 --due 2099-12-31 --why 測試用 --owner enzo
✓ 預告合約已登記:...

$ python3 scripts/lumos --vault /tmp/v1 guard settle Verification/2026-09-22_系統應該處理-watch-whatever-的情況 --test t_x
擋下:Systems/Pay.md 裡找不到預告行『系統應該處理 [watch:whatever] 的情況』(被手改過或已經轉正?)
rc=2
```

Pay.md 裡那一行**逐字沒有被動過**:

```
KEY:★INVARIANT-PLANNED★ 系統應該處理 [watch:whatever] 的情況 [watch:Verification/2026-09-22_系統應該處理-watch-whatever-的情況] [due:2099-12-31]
```

signoff 之後改跑 abandon,同一個節點同樣的訊息擋下,墓碑也立不了(status 仍是 `pending`)。也就是說:這條守衛節點在 CLI 底下**既轉不了正、也棄置不掉**——`guard settle` 說找不到就擋,`guard abandon` 也說找不到就擋,兩條路都被同一個誤判堵死,只剩手改檔案這條路,而手改正是這套機制自己反覆強調「不該做」的事(`cmd_guard_settle`/`cmd_guard_abandon` 的錯誤訊息都寫「被手改過或已經轉正?」,暗示手改是唯一出路)。到期之後,doctor S15 會把它算進「逾期」持續擋推送(逾期判斷只看 `status: pending` 與 `due`,不受這個 bug 影響,所以逾期照樣算,但受害者永遠沒辦法透過正常指令解掉它)。

為什麼是 bug 而不是風格:
這不是邊緣情境的挑剔——這個 repo 自己的合約語彙就大量使用 `[since:]` `[retire:]` `[test:]` `[audit:]` `[watch:]` `[due:]` 這種方括號-冒號-內容的寫法(CLAUDE.md 通篇都是範例),一條在講「這個標記規則本身」的合約(例如「RULE 行要帶 `[since:]` 與 `[watch:]` 才算數」這類自我指涉的敘述)非常容易踩到這個形狀。而且這正是本輪修正想解決的同一類問題(「同一篇預告兩條、前綴相同」)的姐妹坑——r2 為了修掉子字串匹配的舊 bug,換成了「先剝除標記再比對」,但剝除本身沒有限定範圍(只該剝掉**指令自己附加在行尾的那兩個**,不該對合約文字內容也做全域替換),於是把舊 bug 換成了一個新的、更隱蔽的 bug:兩邊(`want` 讀回的原文 vs `body` 被過度剝除的版本)不對稱地被處理,而且發作條件不需要惡意輸入,單純合法的業務文字就能觸發,結果是永久卡死而非單純誤判一次。

已驗證正確(供對照,不是這條發現的一部分):
- 同一篇節點預告「前綴相同、後段不同」的兩條合約(如「退費流程必須先做這件事情:甲案要人工核可」vs「…乙案要雙人覆核」),`guard settle` 正確地只轉正對應那一條,另一條仍留在預告——跑出來的 Pay.md 內容確認過(`gn = ... check("④ 只有乙案被轉正" ...)` 這條測試邏輯與實測結果一致)。
- 兩篇不同守衛節點在剝除 `[watch:]`/`[due:]` 之後文字**完全相同**(手改模擬),`guard settle` 會正確擋下並印「同時有好幾行預告寫著同一句話」,不會誤選。這部分修得對。
- `guard abandon` 在家節點被改指到別篇時正確擋下,且不留半套(墓碑不立、原節點預告行不動)——實跑確認過。

路徑:`scripts/lumos:10720`(`_guard_planned_line` 定義)、`scripts/lumos:10634`(guard 節點寫「預告的合約:」時存的是未剝除的原文)、`scripts/lumos:10659`(功能節點 KEY 行組裝,尾巴附加 `[watch:]`/`[due:]`)、`scripts/lumos:10776`/`10839`(`cmd_guard_settle`/`cmd_guard_abandon` 讀回 claim,未剝除即傳入比對)。
`scripts/test_lumos.py` 裡新增的 `t_guard_plan_hostile_claims`(第 4608 行起)只測了換行、純空白、前綴碰撞三種輸入,沒有測「合約文字本身含 `[watch:`/`[due:` 字樣」這個情境;跑過 `python3 scripts/test_lumos.py -k guard`(383 個案例全綠,含這批新測試)確認現有測試套件目前抓不到這個 bug。

建議修法方向(不是本次要做的事,僅供折入時參考):`_guard_planned_line` 不該對整行做全域剝除再比對整段字串,而是應該先用更嚴格的方式只切掉「行尾那兩個由指令自己附加、格式固定的 `[watch:...] [due:...]`」(例如用 `rstrip` 式的「行尾必須依序是這兩個 tag」規則,或乾脆比對時改成「`want` 是不是 `body` 去掉行尾兩個 tag 之後的字首」而不是整段剝除再相等),而不是對合約文字內容本身也套用同一個正則替換。
