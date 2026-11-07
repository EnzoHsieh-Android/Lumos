severity: major

F1
severity: major
blocking: 是
引句:「我們開發的過程中，所有機制的依據來源，最後也要補回plan，方便後續迭代」
問題:使用者要的是開發過程中新增的機制,最後都補回計劃。但這份計劃只在規格閘(進實作前)查〈依據來源〉。審查輪、實作時才冒出的機制,沒有任何一道閘會回頭查。
- 對照組預期值表有推送前覆查:`scripts/lumos:16556` 的 `_expected_push_one`。本案在〈範圍〉、〈驗收條款〉、〈回退〉裡都沒有對應的推送前或收尾覆查。
- 計劃檔在閘過了之後被刪掉整節,不會被擋。
- 「小改動可跳過」設計審的計劃,也不會跑規格閘。
- 計劃的名字叫「必填」,但實際只擋「進實作那一刻」。這個落差沒有交代,也沒列進〈天花板〉。

F2
severity: major
blocking: 是
引句:「每個機制的依據寫進計劃〈依據來源〉一節(一個機制一行:官方文件、同類工具做法、實測、使用者原話)」
問題:跟既有的「修前先查世界、PRIOR-ART 寫進 intake」那套重疊,計劃沒交代誰取代誰、誰維護。
- 紀律範本〈設計與排查〉已要求計劃寫一行 `PRIOR-ART:`(`scripts/templates/graph-discipline.md:69`)。
- `/Users/enzo/.claude/skills/lumos-design-loop/SKILL.md:41` 與 `/Users/enzo/.claude/skills/lumos-code-loop/SKILL.md:50` 要求每輪修補在 rN-intake 寫〈先查世界〉,每組一行 `PRIOR-ART:` 並附網址。
- 本案新增「一個機制一行」的第三處,卻沒說這三處的關係:是取代、補充,還是要把 intake 的 PRIOR-ART 搬進計劃。
- 範本新句也沒說 `PRIOR-ART:` 一行還要不要寫。
- 審查輪折入的新機制,收貨時要不要同步補〈依據來源〉,兩份 skill 都沒改。〈lands_in〉沒有這兩份 skill,也沒說不動它們。
- 後果:接手的人同一個依據寫三份,或只寫其中一份卻以為已合規。

F3
severity: major
blocking: 是
引句:「白話:計劃筆記裡每個機制(判法、門檻、範本、設定值)都要寫明」
問題:「機制」只在白話段舉了四個例子,〈用詞〉沒有定義,也沒有粒度規則(一個計劃要列幾列、什麼算一列)。
- 這份計劃自己的〈依據來源〉就只有 8 列,漏掉正文裡的好幾個機制:
  - 出處「五種」的清單,依據是什麼沒寫。
  - doctor「最多列 20 篇」的上限。
  - 「不共用 `_HIGH_RISK_EVIDENCE_SINCE`、另立常數取合併隔天」。
  - 「網址只驗格式不連網」。
  - 型錄「提醒不擋」。
  - RETIRE-IF 的門檻。
- 〈天花板〉第 2 點承認「一份計劃寫一行也算過」,等於自認粒度沒定。
- 後果:接手的人各寫各的,代碼審席位也沒有判準可以點名「少了一列」。這份計劃用自己要求別人的標準,自己就先不合格。

F4
severity: major
blocking: 是
引句:「RETIRE-IF: 連續三個月規格閘因〈依據來源〉擋下零次而且代碼審席位也沒再報」
問題:撤除條件和 REVISIT 要看的數字,計劃裡沒有任何機制去量。
- 規格閘擋下時沒有寫治理帳事件,〈範圍〉也沒要求新增。「擋下次數」與「誤判比例」因此算不出來。
- 「依據對不上程式」不是現有的審查席位類別,用 grep 在 `scripts` 與 `docs` 查不到。
- 後果:RETIRE-IF 與兩條 REVISIT 到期時沒有數據可看,等於寫了撤除條件卻無法執行(違反紀律範本鐵則 4 與〈設計與排查〉)。

F5
severity: major
blocking: 是
引句:「型錄逐列出處先提醒後擋」
問題:範圍 4 沒處理既有規則和既有檢查。
- 既有規則:`Systems/kotlin規則包` 的 WHY 行寫「標準寫法的單一來源是型錄 checks-catalog.md,每列要有真的打開讀過的官方出處;查不到的列標(出處不全)」(使用者 2026-11-05 原話)。照這條,324 列沒查證本來就是違規存量。
- 既有檢查:`catalog_problems`(`configs/ast-grep/kotlin-android/check.py:159` 起)已經把「縮寫」算合格來源,而本案新規則把縮寫算「未逐列查證」。新舊口徑並存,計劃沒交代。
- 用詞自己前後不一:範圍 4 把「網址」當逐列查證紀錄,但標題叫「逐列查證」。我實跑:有網址但沒有〔查證〕的列目前是 0,所以現在看不出差別,但一旦出現就會判定不一致。
- 計劃只給 REVISIT 2026-12-15,沒說這段期間靠什麼守住既有的 WHY。

F6
severity: minor
blocking: 否
引句:「內容是一張表(欄:機制|依據|出處)」
問題:「依據」和「出處」兩欄沒分工,連這份計劃自己的表都填混了。
- 第 1 列:「依據」欄放了「必填」那句使用者原話,「出處」欄卻放另一句「補回plan」。出處並不支持依據欄的那句。
- 第 8 列的兩欄也是同一個問題。
- 閘只查「出處」欄格式,不會發現這種錯位。

F7
severity: minor
blocking: 否
引句:「實測 2026-11-06:`governance/review-reports/計劃依據來源必填/r1-intake.md` 〈型錄計數〉節的指令」
問題:出處指向審查卷證裡的檔,不是穩定來源。
- 我重跑了該節的指令,473/140/29/324 對得上。
- 但這份卷證歸審查迴圈管,可能被改寫或清理。型錄一動,數字也會漂。
- 比較穩的做法是把指令寫進〈依據來源〉那一列或系統節點。

F8
severity: minor
blocking: 否
引句:「Rust RFC 範本每份提案必填」
問題:出處的支持範圍比計劃寫的窄。
- 我抓了範本原文。範本確實有「Rationale and alternatives」與「Prior art」兩節。
- 但「Prior art」節自己寫「If there is no prior art, that is fine」。「別人有做不構成理由」對應的是「precedent ... does not on its own motivate an RFC」。
- 「必填」是計劃自己的詮釋,不是範本的規則。
- ADR 那段的引文我查到原文(`One of the hardest things to track...`),是支持的。
- 兩個出處只支持「有必填節的形式」,不支持「一個機制一行」與「規格閘擋」。計劃的 PRIOR-ART 已部分承認這點,但依據表第 2、3 列沒有標明只借形式。

F9
severity: minor
blocking: 否
引句:「`lumos doctor` 數出狀態是 todo 或 doing、沒有〈依據來源〉節或節裡有缺出處列的計劃,列名字(最多 20 篇)」
問題:doctor 的判斷不看新舊,和規格閘的判法不一致。
- 所有舊的 todo 或 doing 計劃都會被列。
- 20 篇上限加上「補完才消」,doctor 這則提醒會長期掛著清不掉,噪音會蓋過真正的缺漏。
- 計劃沒說只列新計劃,也沒說舊的怎麼收斂。

F10
severity: minor
blocking: 否
引句:「`scripts/templates/graph-discipline.md`〈設計與排查〉那段」
問題:每支檔有家這一項沒對齊。
- 範圍 3 要改 `scripts/templates/graph-discipline.md`,它的家在 `Systems/診斷迴圈先行` 一帶,不在〈lands_in〉。
- 範圍 5 要新增「從決策表列找出處」的讀表函式,沒說放在哪支檔。
- 範圍 2 的 doctor 提醒落在 `scripts/lumos`,家是 `Systems/規格閘`,而計劃的 lands_in 還列了 `Systems/lumos-cli-lifecycle`(它管的是安裝與注入,不是 doctor)。
- 照寫的人會改到沒有家或家不在 lands_in 的檔,commit 時被擋。

總結:最嚴重是 major,會擋 5 條(F1 到 F5),另有 5 條 minor 不擋。
