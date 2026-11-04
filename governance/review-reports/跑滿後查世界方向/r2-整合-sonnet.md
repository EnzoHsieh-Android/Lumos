severity: major

# r2 外部審稿:跑滿後查世界方向_計劃(第 2 版)

白話:這份投稿的主線(把主觸發併進既有〈先查世界〉、跑滿提示改順序、手冊同步點補齊)方向正確,r1 多數折入有落實。三個月後接手的人會撞牆的有四處:決策 d1 與正文的觸發條件不同、「新增一種狀態」會打到 retro-stats 的固定計數表、手冊同步點清單仍漏了指令速查表兩列、〈先查世界〉那條 WHY 與 REVISIT 沒接上。

## 摘要與名詞、問題與最小解、不做、回退
已讀,無 finding(回退與相容性的疑慮併在 f9)。

## 做法第 0 點(主觸發,擴充〈先查世界〉)

1. d1 與正文的觸發條件不一致。r1 的 G1 去向說「d1 改成連兩輪出現而這一輪有 major」,但 d1 與白話段仍帶「準備換形狀時」,第 0 點正文沒有這個條件。實作與 S8 守衛只能擇一,而 CLAUDE.md 規定 `decisions:` 欄位才有挑戰程式碼的效力。這個條件是主觀判斷:帶它,漏查就沒有對照標準;不帶它,每個連兩輪的根因組都要多查一次。
   引句:「同一類根因連兩輪出現而這一輪那組有 major、準備換形狀時」
   file: `docs/lumos-toolchain-knowledge/Projects/跑滿後查世界方向_計劃.md:16`
severity: major
   blocking: 是,決策紀錄與正文對觸發條件各說一套,實作者無法判斷以哪個為準。

2. 第 0 點沒有說明既有句尾的處理。原段是「同一個判讀第二次被打穿時這一步必做,而且先找不靠字面判斷的現成做法(例:判讀靠名字字表…)」。
   - 第 0 點只改寫前半句,後半句「先找不靠字面判斷的現成做法」留著還是刪掉,沒有寫。
   - 留著:它會套到每個新觸發的根因組,而這些組不一定是字面判讀。
   - 刪掉:2026-11-02 那條 WHY 的決定內容就丟了。
   - 另外,原段有「查不到就寫查了哪些詞、為什麼沒有」的退路,新增的「至少兩個來源」沒說明它與這條退路的關係。
   引句:「在〈先查世界〉那組多寫一行 `方向:對|要換|判不準 — <一句>`,要換方向時攤給人裁」
   file: `skills/lumos-design-loop/SKILL.md:41`
severity: minor
   blocking: 否,不會讓工具出錯,只會讓手冊新舊兩句並存。

3. 「要換方向時攤給人裁」與代碼審 SKILL.md 步驟 4 的守衛面規則沒有對上。步驟 4 寫「同類第二次被打穿就換形狀:整類拿掉,或在外面加一道不靠字面的看門」,是編排者自己動手。第 0 點是先查方向、要換就攤人。兩者的觸發點相同(第二輪),規定的動作不同,spec 沒有寫誰先誰後,也沒有說攤給人裁之後,步驟 4 的自行換形狀還適不適用。
   引句:「在〈先查世界〉那組多寫一行 `方向:對|要換|判不準 — <一句>`,要換方向時攤給人裁」
   file: `skills/lumos-code-loop/SKILL.md:45`
severity: minor
   blocking: 否,兩條規則並存會讓編排者各取所需,但不影響工具行為。

## 做法第 1 點(跑滿提示改順序)
已讀,無 finding。我 grep 了 `scripts/test_lumos.py`,沒有任何測試釘「先記人裁」「要破例再開一輪」「繼續之前先寫跑滿回顧」的字面。會碰到提示的兩支測試只比對 `cap-decision` 子字串:`t_cap_retro_next_hint_scope_only`(`scripts/test_lumos.py:104275`)與 S6(`scripts/test_lumos.py:103682`)。新增的那句不能含 `cap-decision`,而且只能印在「範圍內、還沒有人裁」的分支,否則範圍外迴圈的反向斷言會紅。

## 做法第 2、3 點(骨架與檢查)

4. 「新增一種狀態」會打到五個呼叫端共用的狀態詞彙。
   - `_cap_retro_fix_cmd(root, loop_id, state)` 的 `state` 來自 `_cap_retro_status`,只有 recorded、skipped、stale、none、gov-bad 五種。
   - `_RETRO_STATE_LABEL`(`scripts/lumos:22125`)與 retro-stats 的 `totals[key] += 1`(`scripts/lumos:23016`)都用這五個鍵。後者在 try 外面,多一種狀態就是 KeyError。
   - version 要改成 2 的提示,本來就可以寫進 `--check` 逐欄列出的那一行。「還沒記」與「過期」兩種狀態的修法已經是「`--check` 過了再 `--record`」,不需要新狀態。
   - loop-retro 的 WHY d7 規定五處共用同一支判定,spec 只列出一處改動。
   引句:「修法交給 `_cap_retro_fix_cmd` 那張表(新增一種狀態)」
   file: `scripts/lumos:22125`
severity: major
   blocking: 是,照字面實作會讓 retro-stats 或 doctor 在新狀態上崩潰,或讓五處判定分岔。

5. 「不要求時 world_check 整段不驗」與「不要求時有填就照驗」互相矛盾。第 3 點第三項說人裁早於生效日的 version 1 回顧不驗 world_check。最後一項說「accept-risk 或不要求時」有填就照上面驗,填一半算錯。人裁早於生效日、version 2、world_check 填一半的回顧,兩句給出相反答案,S5 只覆蓋 version 1 的情況。
   引句:「最新一筆人裁是 accept-risk、或不要求時:`world_check` 省略、`null`、`{}`、空骨架」
severity: minor
   blocking: 否,這是邊角組合,但兩種讀法會讓實作與測試寫出不同行為。

6. 網址「互不相同」的正規化太淺,verdict 用詞對不上。
   - 正規化只轉小寫、去 `#`、去結尾斜線,所以同一頁的 `http://x/a` 與 `https://x/a`,以及 `www.x` 與 `x`,都算兩個來源。「至少兩個來源」可以用同一頁湊滿。
   - 手冊的 intake 行寫 `方向:對|要換|判不準`,JSON 的 verdict 是 `direction-ok|change-direction|undetermined`,中間的對照沒有任何地方寫。
   - 已知天花板一承認格式不等於查過,我不要求防偽造,只要求兩個詞表有一張對照。
   引句:「兩項以上的網址在正規化(scheme 與主機名轉小寫、去掉 `#` 之後、去掉結尾斜線)後要互不相同(用集合比)」
severity: minor
   blocking: 否,屬於天花板一已承認的範圍,只差把對照表寫清楚。

7. 測試覆寫生效日用環境變數,等於正式程式碼裡留了一條關掉閘的旁路。
   - 既有前例 `LUMOS_PANEL_RETIRE_CUTOFF`(`scripts/lumos:18839`)的說明就寫「供測試/緊急覆寫」。
   - 同檔的 `_SPEC_GATE_SINCE` 等常數(`scripts/lumos:13714`)並不走環境變數,測試改用 in-process 修改常數。
   - 回顧測試因為走子行程才需要環境變數。「只給測試用」是約定,不是機制;任何 shell 設了這個變數都會讓閘靜默不要求 world_check。
   - 在單人自用的威脅模型下這個風險很低,但實務隱患節沒有列。
   引句:「環境變數覆寫,只給測試用」
   file: `scripts/lumos:18839`
severity: minor
   blocking: 否,旁路存在但屬已有前例的做法,補上實務隱患一行即可。

## 做法第 4 點(記帳與 retro-stats)

8. RETIRE-IF 的量法量不出效果,而且它量的東西 `retro-stats` 本來不輸出。
   - 「判不準」是只要寫 20 個字、不用附來源的最便宜出口。
   - 條件寫成「結論是要換方向或判不準的次數為 0 且折入數沒降」才撤,所以只要有人用 undetermined 偷懶,次數就不為 0,機制永遠撤不掉,而它其實沒改變任何決定。
   - `retro-stats` 只印三種結論的次數,沒有「沒填」與「跳過」的分母,折入數(folded)也不在它的輸出裡。
   - 數字量級:`docs/.governance-log.jsonl` 裡 loop-retro 有 79 筆 extra-round 人裁和 101 筆 recorded,所以半年內樣本不少。缺的是分母和 folded,不是樣本。
   - 對照另一條:`kind: skipped` 事件我數到 0 筆,所以天花板二目前還沒被用過。
   引句:「同期加開後那一輪的折入數(帳上 folded)沒有比生效前半年的加開輪少」
   file: `docs/.governance-log.jsonl`
severity: minor
   blocking: 否,不影響工具行為,但半年後這條撤除條件會判錯。

## 做法第 5 點(手冊七處與 command-reference)

9. 同步點清單仍漏列,「共七處」是封閉清單。七處的行號我逐一核對,332、542、245、620、`05-設計審查迴圈.md:33`、`docs/command-reference.md:137` 都對。漏列的有:
   - `skills/lumos-project-notes/commands/05-設計審查迴圈.md:22`,「跑滿上限沒過,人裁決定…」那列直接教人去跑 `cap-decision`,沒有先查方向。
   - 同檔第 23 列「記了人裁,要寫跑滿回顧」只寫起草、`--check`、`--record`,沒提 world_check。依這張速查表走的人,`--check` 會擋在 world_check 缺漏上,卻沒有地方先講。
   - `docs/command-reference.md:136`(`cap-decision` 本身)。spec 只列了 137。
   - S8 的守衛如果只認這七處,這幾列會一直漏著。
   引句:「共七處,措辭各不同,逐處列」
   file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:22`
severity: major
   blocking: 是,spec 宣稱清單完整並以它綁定 S8,實際還有至少三處到頂/人裁流程說法沒被同步。

10. S8 守衛的粒度太粗,抓不到少改一處。
    - 既有的同類檢查 `_CR_MANUALS`(`scripts/test_lumos.py:104033`)是整份檔的子字串 `in` 比對。
    - `reference.md` 在 332 與 542 各有一處到頂說法,兩份 `reference.md` 共用這種檢查,改了其中一處就會讓整檔通過。
    - spec 還把「七處」寫成「七個檔」,實際是五個檔加 `command-reference`。
    - r1 的 G3 就是因為數錯處數才折的,這個守衛沒有擋住同一種錯的再犯。
    引句:「當手冊同步點那七個檔與 command-reference 被讀時,每一處到頂的說法都應含先查方向的字樣」
    file: `scripts/test_lumos.py:104279`
severity: minor
    blocking: 否,不影響執行,但守衛放過半套改動。

11. §9 起草派工詞的「不要填」清單沒有同步。spec 只在編排者須知補一句,派工詞圍欄裡的「不要填:avoid、changes、completed_by」沒加 world_check。起草者拿到的骨架含空的 world_check 殼,只靠「只改下面列的欄位」擋它;它若有網搜工具,可能自行填進編造的來源,格式會通過 `--check`。這一句圍欄原文是照抄給子代理的,放在 `templates.md` §9 的圍欄內。
    引句:「派工前不寫進回顧檔——起草者會讀到它、破壞起草獨立(d2)」
    file: `skills/lumos-design-loop/templates.md:571`
severity: minor
    blocking: 否,風險集中在起草者越權,現行派工詞已有「只改列出的欄位」作一層擋。

## 做法第 6 點(寫回)

12. 〈先查世界〉的 WHY 與 REVISIT 沒有接上。這是這一輪點名要查的項目。
    - `Systems/每輪修補差異派工` 第 20 行那條 WHY 帶 `[不選:只在跑滿回顧或卡關時才查(那時已多燒好幾輪)]`。本計劃的保底層(跑滿回顧必填 world_check)正是被否決過的那種時機。
    - 第 6 點只說要補一行 WHY,沒有說明新 WHY 怎麼和這條 `[不選:]` 並存。三個月後的人讀到兩條互相打架的 WHY,不知道哪條有效。
    - 同篇第 21 行 REVISIT 2026-12-15 量的是「rN-intake.md 有沒有〈先查世界〉一節」,有沒有那一節。擴充之後,節一定在,「方向:」那一行有沒有寫量不到。
    - 本計劃自己的 REVISIT 2027-02-04 才量方向行,比前者晚了一個半月。12-15 若據此把〈先查世界〉做成機械檢查,檢查的對象只會是舊的「節存在」。
    引句:「的回頭條件照舊數〈先查世界〉」
    file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:21`
severity: major
    blocking: 是,12-15 的回頭條件會量錯,新 WHY 也與既有的 `[不選:]` 矛盾而沒有說明。

13. 三處寫回遺漏了其他會變舊的說法,`lands_in` 也只列兩篇。
    - `Projects/審查跑滿回顧_計劃.md:98` 寫「`version`:1。」,只加一句指過來,舊句還在。
    - 同篇第 134 行描述 [cap-hint] 人裁提示的內容,提示順序改了這裡會變舊。
    - 管 [cap-hint] 提示的 `Systems/loop-convergence-recording`(第 37 行的 PITFALL 描述了提示行為)沒進 `lands_in`。
    - `Systems/loop-retro` 的 WHY d7(五處共用一支判定)沒有提到新增的生效日分支。
    - 「CHANGELOG 寫明」只出現在實務隱患,做法裡沒有對應的步驟,也沒有測試守它。
    引句:「[[Projects/審查跑滿回顧_計劃]] 的回顧檔格式那段加一句指過來(第 2 版多了 world_check)」
    file: `docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:98`
severity: minor
    blocking: 否,屬於筆記同步,不影響工具行為。

## 做法第 7 點(既有測試)
已讀,無 finding。我 grep 了 `scripts/test_lumos.py`,凡呼叫 `_cap_retro_check` 的只有 `scripts/test_lumos.py:104390`(用 `{"rounds": []}`,沒有人裁種類,依 spec 的「先判是不是 extra-round」不會要求 world_check)。手寫回顧文件的只有 `_cr_retro_doc`(`scripts/test_lumos.py:103445`)與一支斷言 `version == 1` 的骨架測試(`scripts/test_lumos.py:103881`),spec 都已列。

## 實務隱患節

14. 「相容二」的處理只靠人工同步,沒有分階段。還沒更新 lumos 的機器讀到 version 2 的回顧檔,會判「version 要是 1」並擋 `canary record`。回退節的「version 收 1 或 2 那段留著」只保護回退之後,對先上線新骨架再讓舊機器升級這件事沒有幫助。分兩次發版(先讓檢查收 1 或 2,隔一段時間才讓骨架出 2)就不需要靠 CHANGELOG 提醒。我沒有證據顯示有多少台機器沒用 symlink 安裝,所以這是 ⚠:升級落差的實際大小要查消費端的安裝方式才知道。
    引句:「推出新版時要同步更新,CHANGELOG 寫明」
severity: minor
    blocking: 否,該風險已被明列,但處理方式沒有機制。

併發、效能、資源、回滾逐類結論:
- 併發:沒有 finding。`--template --write` 用 O_EXCL;`--record` 驗和算指紋用同一份位元組(既有做法);生效常數是靜態值。
- 效能:沒有 finding。回顧檔上限 256KB,網址正規化與集合比是線性;r1 的 b8(壞項問題清單不封頂)已放行,我的看法沒變。
- 資源:沒有 finding。
- 回滾:唯一的疑慮在 f14(舊機器讀不到 version 2),其餘回退步驟完整。

總結:最嚴重為 major,共 4 條 blocking(f1、f4、f9、f12),其餘 10 條為 minor、不阻擋。
