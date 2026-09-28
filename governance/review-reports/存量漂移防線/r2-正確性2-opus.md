severity: major

# 設計審 r2 — 正確性/邏輯席(正確性2-opus)

審的對象:凍結快照 `governance/review-reports/存量漂移防線/r2-snapshot.md`;對照 clone-ns 的 `scripts/lumos`、考卷 `rtb-2026-09-28.json`、改寫檔 `rtb-2026-09-28-probes.json`、README;rtb 複本只用 `git -C` 唯讀指令查。

## 在 rtb 複本上走過的考題(先交代,後面的 finding 會用到)

- A4、A5、A6:e606947、1eace79、16136d6 這三個提交各自把守衛紀錄從 `status: pending` 改成 `pass`。第 19 行在上一版、那一版、067f005 都是 `  TEST:還沒有測試在守這條;…`(A4/A5 用 `note_at_event` 的長檔名讀),正文也還有 `為什麼還不做:`。照甲的字面:c1 成立,而且範圍裡有 pending→pass 的事件,所以判**擋到**。每個提交「要處理」2 筆(TEST 行加「為什麼還不做」行)。
- E1:ef10bc7 把 Phase 12 計劃從 doing 改成 done。計劃正文有 `[[Issues/Phase12需要可看任務階段與處置的HTML報告]]`,Issue 是 open,所以 c2 成立,判**點到**。E2:7413936 把 Phase 11B 計劃改成 done,計劃第 19 行連到 `[[Issues/Phase11後接入大模型API的三個階段]]`(open),判**點到**。E3:b2fc512 新增 `Verification/Phase14增量2b驗證紀錄.md`,`valid_under` 裡有「未提交」,c4 列進「只列出」,判**點到**。同一個提交也新增了增量3那篇,它同樣含「未提交」,會一起列出,但那篇不在考卷裡。
- 乙的改寫,拿 event_commit 的上一版跟那一版比:A7、B4 的 `MAX_INCREASE_NUMERATOR` 在 0ffba7d^ 整棵樹搜不到,到 0ffba7d 出現在 `src/rtb/executor/execution.py:282`,是模組層的賦值。B1、B2、B5 的 `src/rtb/analyzer/runner.py` 在 8ff8c95^ 不存在、8ff8c95 存在。B3 的 Phase 12 計劃在 f183cd8^ 不存在,到 f183cd8 是 `status: doing`。六題的改寫行在兩版都位在同一個行號,文字也一樣。結論:**照 event_commit 算,六題都是起點不成立、終點成立**。B3 用考卷寫的失效提交會出問題,見 F2、F3。
- 非漂移題:E4(`Issues/執行迴圈收到SIGTERM等於硬殺.md`)在 ef10bc7 是 open,而且連到 Phase 12 計劃,所以在 E1 那一次考試會被 c2 列進「只列出」。這跟 spec 自己的預期一致(SIGTERM 那篇本來就是刻意開著的)。其餘非漂移題見 F1。

## F1 預設 block 的門檻在這份考法下判不出任何東西:非漂移題只有 B5 會進「要處理」,而 B5 算不算誤列,兩處寫法互相打架
severity: major
blocking: 是 — 預設模式照這個門檻寫死在程式裡;門檻不是自動過就是自動不過,實作者會拿一個沒有資訊量的數字去決定消費專案一更新就被擋
引句:「沒有誤列任何非漂移題」
file: `governance/eval/drift-exam/README.md:11`
1. 〈做法〉第 3 節的考法只有三種:①甲的題對失效提交跑 check;②E1、E2 重算 `lumos set`;③乙的題套上改寫後對失效提交跑 check。README 寫的 `current_state=對 067f005 跑 scan`,在 spec 的考法裡**沒有這一種**。所以 A8、A9、D4–D6、I1–I3、R1–R3 這 11 題從頭到尾沒有任何一次會被評估,只可能在別題的提交裡碰巧被列到。
2. 走 rtb 複本查過:那 11 個考題提交的「要處理」,只來自 c1(只看範圍裡 pending→pass 的守衛紀錄,也就是 A4–A6 那三篇)和注入的改寫行(A7、B1、B2、B3、B4、B5)。非漂移題裡能進「要處理」的只有 B5(8ff8c95 那次)。另外,每個提交的「要處理」最多 3 筆(8ff8c95 的 B1、B2、B5),「不超過 5」這個條件是注入題數決定的,一定成立。
3. 所以「零誤列」只看 B5 一題。可是〈做法〉第 3 節寫「B5 另記……分開報」,第 4 節第 4 點卻寫「沒有誤列任何非漂移題」,沒有把 B5 排除。B5 如果算進去,門檻永遠不會過,預設永遠是 warn;如果不算,門檻一定會過,預設就變 block。兩種結果都跟真實世界的誤報率無關。
4. 附帶:考卷的 `exam_event` 欄對不上 spec 的考法。A4–A6、E3 標的是 `status_command`,但 spec 對它們跑的是 check;E1、E2 也標 `status_command`,跑的卻是 set 重算。只照這個欄位分派考法的實作會跑錯。

## F2 乙的考法寫「對失效提交跑 check」,但 B3 考卷上的失效提交在起點時條件就已經成立,照字面會判成漏;spec 說 r1 查出的失效提交錯誤題數也對不上
severity: major
blocking: 是 — 照 spec 字面實作考試,B3 會算成「漏」,B1 也會多一次「漏」,考試結果跟改寫檔的預期不一致
引句:「乙的題:套上改寫,對失效提交跑 check」
file: `governance/eval/drift-exam/rtb-2026-09-28.json`(B3 `invalidating_commits: ["b9c7496","8ff8c95"]`、B1 `["8ff8c95","0b2499a"]`)
1. `git -C rtb-exam show <rev>:…/Projects/RTB_Phase12一鍵展示與HTML報告_計劃.md` 查到的狀態:f183cd8^ 還沒有這篇;f183cd8、b9c7496^、b9c7496、8ff8c95^、8ff8c95 都是 `status: doing`。
2. B3 的改寫是 `[when-status:…Phase12…_計劃=doing|done]`。對考卷的失效提交 b9c7496 或 8ff8c95 跑 check,起點就已經成立,照「起點不成立、終點成立才擋」會判不擋,也就是**漏**。只有改寫檔裡的 `event_commit: f183cd8` 會翻,而這個欄位 spec 沒提(第 80 行只說改寫檔給「原文→改寫」),考法寫的是「失效提交」。
3. B1 考卷上列兩個失效提交。0b2499a 的上一版已經有 runner.py,所以在 0b2499a 必定判不擋。spec 沒說一題有多個失效提交時怎麼計分。
4. B3 的 `invalidating_commits` 其實跟 r1 更正前 E1 的錯法一樣(E1 已經改成 ef10bc7,B3 沒改),README 的更正紀錄也沒提到 B3。另外,spec 第 79 行寫「設計審 r1 查出 4 題失效提交寫錯」,README 更正紀錄只列 A5、A6、E1 三題。A4 的 notes 寫的是「原寫 ['e606947'] … 改成 ['e606947']」,等於沒改。

## F3 when-status 指到的筆記在被檢查的樹裡不存在時,該判「不成立」「判不了」還是「寫錯的條件」,沒有定義;B3 正好就是這個情形
severity: major
blocking: 是 — 三種判法會讓 B3 分別變成擋到、不擋(判不了)、判定不明(起點「寫錯」算不算不成立);S9 的「寫錯的條件」也因此沒辦法寫出確定的測試
引句:「那篇筆記在被檢查的樹裡 status 等於那個值」
1. B3 在 f183cd8^ 那一版,Phase 12 計劃還不存在。when-file 可以自然地把「不存在」當成不成立,但 when-status 的值是一篇筆記的狀態,筆記不存在時沒有值可比。
2. 〈做法〉第 2 節第 3 點與 S9 都要求 scan 列出「寫錯的條件」,可是哪些算寫錯,沒有任何定義。實作者如果照連結檢查的慣例把「節點找不到」歸成寫錯,B3 在起點就是寫錯。這時「起點寫錯、終點成立」算不算翻轉?第 0 節只說判不了時不擋,沒說寫錯的情形。
3. 同樣的缺口也出現在 `[when-symbol:<路徑>::<名稱>]`:路徑在起點不存在時,是不成立還是寫錯?

## F4 「起點不成立」要先認出是「同一行」,但同一行怎麼認沒有定義;照既有做法(內容編號,或同一路徑的行文字)認,改名或改小標題的推送會把該擋的行降成「只列出」
severity: major
blocking: 是 — 這是推送閘判擋的核心規則,不寫清楚,實作者照既有兩層的做法認行,就會留下可重現的漏擋
引句:「一行在起點不存在(這次新寫的)就只看終點」
file: `scripts/lumos:23822`(`_notelines_content_id` 的輸入包含路徑與小標題)
1. 判「這行是新寫的」要在起點那一版找到「同一行」。spec 沒說怎麼找。既有兩個可以借的做法:第一層與第二層用的「同一路徑裡有沒有同樣的行文字」,以及表態用的內容編號(路徑、區塊、小標題、行文字)。
2. 重現:一次推送同時做兩件事,①新增 `src/rtb/analyzer/runner.py`,②把 `Projects/RTB_Phase3外部寫入安全_計劃.md` 改名,或改掉 B1 那行上面的小標題。rtb 在 e8ea7d0 就整批改過 Verification 的檔名,這種推送實際發生過。這時 B1 的條件行在起點找不到同一行,被當成新寫,只看終點:終點成立,結果只列出不擋,而作者並沒有碰過那一行。
3. 反方向也要寫清楚:作者只改了行尾的錯字(條件沒動)就被降級,這算不算刻意的設計?spec 只說「新寫」,沒說「改過」。

## F5 回退節的 settle 退回步驟自相矛盾:用新程式會把改寫重新套一次;用舊程式沒有補救路徑,守衛紀錄會卡成轉不了正也棄置不掉。「不給開關」的理由就建立在這個步驟上
severity: major
blocking: 是 — 照這個步驟退回,會造成逾期後一直擋推送的卡死狀態;「不打算給開關」的決定是根據一個走不通的前提做的
引句:「要退回,git 還原守衛紀錄後再跑一次 settle」
file: `scripts/lumos:11802`、`scripts/lumos:11815`、`scripts/lumos:11882`
1. 讀法一,新程式還在:用 git 還原守衛紀錄後,它回到 pending 加原本的三句預告。再跑 settle 走補救路徑,「只做第二步」,而第二步本身就包含三種句型的改寫(〈做法〉第 1 節第 2 點)。結果句子又被改寫一次,等於沒有退回。
2. 讀法二,lumos 已經退回舊版:既有的 `cmd_guard_settle` 在 `:11815` 找預告行,家筆記早已是正式行,所以找不到,印「擋下」。`cmd_guard_abandon` 在 `:11882` 用的是同一支函式,也一樣擋下。守衛紀錄就卡在 pending,到期後 `guard required` 回 1,推送被擋,而轉正與棄置都做不了。這正是 guard-kill 的 PITFALL 行描述過的「轉不了正也棄置不掉、逾期還一直擋推送」。
3. 「改寫是冪等」這句也不成立:WHY 行的判定是「固定句型開頭,行尾加(日期 已轉正)」。已改寫過的紀錄如果被手動改回 pending 再跑補救,WHY 行開頭仍然符合句型,會被加上第二個後綴。
4. 補救路徑的判準「同一句合約、同一個 `[test:]`」,碰上 settle 之後照指示跑過的 `guard audit`(`scripts/lumos:12464`,它會在正式行尾加上 `[audit:…]`)會怎樣,沒有寫。如果用整行比對,補救路徑在最常見的情形下就認不出正式行。

## F6 settle 的改寫漏了 guard plan 樣板裡的第四句預告
severity: minor
blocking: 否 — 漏掉的只是一句操作提示,status 已經是 pass,讀者不至於誤判合約還沒做
引句:「只動工具自己寫出的固定句型」
file: `scripts/lumos:11573`
1. `_guard_plan_write_node` 產生的正文最後一行是「做完之後跑 `lumos guard settle` 轉正,不要手改狀態。」。轉正之後,這句變成過期的指示,跟 spec 要處理的機制③同類,但第 1 節第 1 點只列了 TEST、WHY、「為什麼還不做」三種,c1 也偵測不到這一句。

## F7 c3 在 plan_refs 是空的時候會空真成立;待完成的守衛紀錄本來就該是 pending,卻會被當成該結案的列出來
severity: minor
blocking: 否 — c3 只列出不擋,影響的是清單雜訊和建議指令
引句:「列的計劃全都已收尾。只列出」
file: `scripts/lumos:11565`(guard plan 會寫 plan_refs)
1. 「全都已收尾」如果照 `all([])` 實作,沒有 plan_refs 的 pending 驗證紀錄一律成立。
2. `guard plan` 建出的守衛紀錄在到期前本來就是 pending,它的 plan_refs 指向 `--plan`(rtb 指的是 Phase0 架構計劃)。那份計劃一收尾,c3 和 `lumos set` 的連帶待辦②就會把這些守衛紀錄列成待處理,還附上一行要敲的指令。守衛紀錄的樣板明寫「不要手改狀態」。

## F8 check 從哪裡讀表態檔,以及表態對 scan 與 doctor 有沒有作用,都沒寫
severity: minor
blocking: 否 — 照第二層「check 只認提交樹」的先例大多會做對,但使用者不知道表態之後還得提交
引句:「(加進簿記豁免);綁①那一行的內容編號」
file: `scripts/lumos:24345`(`_note_audit_load_verdicts`:check 只認提交樹)
1. 第 0 節規定 check「讀被推送頂端提交的樹,不讀工作目錄」。`drift ack` 寫進工作目錄的 jsonl,不提交的話推送會照樣被擋。如果實作改成讀工作目錄,又會變成推送前放行、CI 擋。
2. 表態之後,scan 和 doctor 的 Z 段還列不列那一行,沒寫。B5 這類「條件已經成立、但決定延後做」的行,改成條件式以後就沒有日期可延,只能表態。如果表態只管擋、不管列,doctor 會永遠列著它。

## F9 圍欄與行內程式碼裡的條件寫法要不要評估,沒有寫;本計劃自己就有好幾個範例條件
severity: minor
blocking: 否 — 只多出 scan 與 doctor 的「寫錯的條件」雜訊,不會擋推送
引句:「可放在任何筆記行上(建議只放 REVISIT 行,見第 5 點)」
1. 第一層與 E5 都限定只看可見行,評估這一側沒有同樣的限定。快照第 56、66–71 行,反引號裡有 `[when-status:<這份計劃>=…]`、`[when-file:<repo 內相對路徑>]`、`[when-file:src/x/runner.py]` 這些範例。〈做法〉第 4 節掃工具鏈自己的圖譜時,它們會被評估,或被列成寫錯的條件,而且 Systems/存量漂移守衛寫說明時還會再多出一批。

## F10 第一層只驗鍵名與值是不是空的,形狀壞掉、永遠不會成立的條件照樣放行
severity: minor
blocking: 否 — scan 還會列「寫錯的條件」,看得到
引句:「條件鍵不認得或值是空的也擋」
1. `[when-status:Projects/X_計劃]`(少了 `=值`)、`[when-symbol:src/a.py::]`(名稱是空的)、`[when-file:/abs/path]` 都過得了第一層,但評估時永遠不會成立。推送閘等於永遠不會替這一行擋,而 E5 又把它當成「條件式」計數,不算壞損。

## F11 「程式檔」與比對邊界沒有定義,會影響條件提早成立或永遠不成立
severity: minor
blocking: 否 — 誠實界線已經承認非 Python 會提早成立;這裡補的是 Python 側與檔案範圍
引句:「在被檢查的樹裡,程式檔有這個名稱的定義行」
file: `scripts/lumos:23830`(既有 `_ns_is_code` 把測試檔也算成程式檔)
1. rtb 在 0ffba7d 的 `governance/review-reports/code-phase6-inc2/r1-snapshot.patch:110` 有 `+MAX_INCREASE_NUMERATOR = 1`,筆記本身也含這個名字。範圍到底是 `_nodehome_code_kind` 的副檔名清單、`_ns_is_code`(含測試),還是全部檔案,spec 沒指定;要是 .md 或 .patch 也算,條件在筆記寫下的那一刻就成立,永遠只列出。
2. Python 的 `def`/`class` 限不限模組頂層沒寫:只找頂層,方法名稱永遠不成立;不限,同名方法會提早成立。`when-test` 的「`def <名>`」有沒有字邊界也沒寫:`[when-test:test_runner]` 會被 `def test_runner_starts…` 提早滿足。

## F12 E1、E2 的 set 重算寫「在那個提交的樹上」,但那棵樹上計劃已經是 done
severity: minor
blocking: 否 — 實作者多半會改成用上一版,但照字面加上「改成」解成狀態轉換,就會算成漏
引句:「在那個提交的樹上重算」
1. 在 ef10bc7 那棵樹上,Phase 12 計劃已經是 done。如果照第 1 節第 3 點「不是改成 done/superseded 就不印」,把「改成」理解為 doing→done 的轉換,從 done 設成 done 什麼都不印,E1、E2 就記成漏。應該寫明用上一版的樹。

## F13 lands_in 沒有列 guard settle 的家
severity: minor
blocking: 否 — 只影響說明寫進哪篇
引句:「新增一道推送閘、改 `guard settle` 的寫入」
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:14`
1. 全圖譜只有 Systems/guard-kill 寫到 `guard settle`,guard plan 與 settle 的 RULE、PITFALL 都在那一篇。lands_in 只列了存量漂移守衛與兩層筆記閘,settle 改寫行為的說明會落到錯的地方。

## F14 「任一成立寫兩行」:處理完其中一行以後,另一行之後還會為已經做完的事再擋一次
severity: minor
blocking: 否 — 可以用表態解掉,但會拉高 RETIRE-IF ① 的「照留」比例
引句:「原本一句話講兩個觸發(考卷 B2:」
1. B2 拆成 `[when-file:runner.py]` 與另一個觸發各一行。runner.py 進來時第一行擋下,作者做完事刪了這一行;之後另一個觸發成立,第二行又擋一次,要求做同一件已經完成的事。spec 沒有提醒作者同時處理兄弟行。

## F15 drift exam 跑 check 時,會把 blocked 與 warned 事件寫進被考 repo 的治理帳
severity: minor
blocking: 否 — 考的是複本時影響不大,但 spec 自己說「不改被考 repo」
引句:「考試時在記憶體裡把那篇筆記的那一行換掉再評估」
file: `scripts/lumos`(`_gate_event_or_warn` 寫進 repo_root 的治理帳)
1. 每次考試會在 `--repo` 指到的 repo 留下 A4–B5 各提交的 blocked 或 warned 事件。如果指到真的 repo(〈做法〉第 4 節掃的就是 `/Users/enzo/rtb-mainwt`),會污染 RETIRE-IF ① 要量的擋下與表態分布。spec 沒要求考試模式不寫帳。

## F16 第二層排除的是所有 REVISIT 行,比折入理由要的範圍寬,判準也跟 E5 不一致
severity: minor
blocking: 否 — 用日期式 REVISIT 夾帶現況句的情形,到期時 doctor 還會唸
引句:「第二層的待審行排除以 `REVISIT:` 開頭的行」
file: `scripts/lumos:1962`(E5 會先剝掉 `- `/`* ` 列表前綴)
1. r1 的折入理由是「避免條件式被判成推得出」,但排除範圍連日期式也包含了。像「REVISIT:2026-12-31 分析端沒有正式啟動程式,有了就補測試」這種夾帶現況句的行(rtb A9 那種句子),從此第二層不審。
2. S12 只說「以 REVISIT: 開頭」。E5 與第一層會先剝掉列表前綴 `- `,實作要是沒剝,`- REVISIT:[when-…]` 仍然會被第二層送審,跟第一層判定互相卡住的老問題會回來。第二層收尾計劃的「完成審」整篇送審路徑要不要也排除,同樣沒寫。

## F17 回退節說用 `lumos search "[when-"` 能列出全部,實際上列不全
severity: minor
blocking: 否 — 只影響回退時的清點
引句:「列出全部),否則 E5 退回舊版後會把它們算成格式壞損」
file: `scripts/lumos:3429`、`scripts/lumos:3677`
1. search 預設是 ranked 模式,`top=20`,只給前 20 篇;預設也會藏起 superseded 的筆記。E5 退回舊版後,會把全部筆記(含作廢的)裡的條件式行都算成壞損。修復之後 rtb 預計有約 45 條條件式,搜尋列不完。

## 各節與相關節點
- 〈範圍〉、PRIOR-ART、RETIRE-IF:已讀,除了 F1(預設門檻)以外沒有 finding。`_nodehome_clamp_base` 在找不到上線點時回傳原本的起點(`scripts/lumos:22967`),所以在 rtb 歷史上考試不會被截空。
- 〈做法〉第 0 節的判不了與預算:「單次 20 秒、總共 60 秒、判不了不擋、記 degraded」跟 S2 一致,互相不打架。沒寫的是 c1 那一段逐提交走訪如果 git 失敗怎麼辦(判不了只講了條件評估);這點歸在 F4 的定義缺口,不另外開一條。
- 表態綁「內容編號加發現種類」跟「只擋翻轉」彼此不衝突:只有翻轉的那次推送需要表態,之後起點已經成立就不會再擋。不足的地方見 F8。
- 條款 S1–S17:S3、S4、S5、S7、S8、S10–S14、S16、S17 跟做法一致,可以測。S9 因為 F3「寫錯的條件」沒有定義而測不準;S5 受 F5 的比對方式影響;S6 少寫了「每項給一行指令」,但不影響測試。
- 相關節點判定:
  - Projects/舊句偵測實驗_計劃:本 spec 已經沒有依賴丙或符號存在性的文字(第 34 行、第 145 行都只寫指向),不受影響。
  - Projects/筆記形狀擋_計劃、Systems/筆記內容閘:第一層加 REVISIT 規則,只作用在新寫的行,不改 FACT/FLOW/DEP 的既有規則,不破壞它宣稱的行為,但有 F10 的缺口。
  - Projects/筆記內容審_計劃、Systems/筆記內容審:排除 REVISIT 行改變了「新寫行都送審」的範圍,見 F16。
  - Systems/guard-kill:「就地轉正」的 RULE 不被破壞,但回退步驟會踩到它 PITFALL 講的卡死情形,見 F5 與 F13。
  - Projects/code側刪除傳播守衛_計劃:處理的是符號刪除的傳播,本計劃不碰符號存在性,不受影響。
  - Issues/存量筆記漂移三種機制_rtb根因回饋:本計劃處理機制②③,考卷對應正確(甲 6 題、乙 5 題,共 11 題)。
  - Issues/治理帳多個寫入者都沒上鎖:新增的表態檔與 drift-check 事件是同一類只追加帳本,第 131 行已經寫要併進去,不受影響。

## 實務隱患
- 守衛面:碰到了。這份設計新增一道推送閘,並改動 settle 的寫入與兩層筆記閘的判定;F4、F5 是守衛本身的正確性問題。
- 併發:settle 包在可重入的寫入鎖裡(`scripts/lumos:14251` 是可重入的,巢狀呼叫 `cmd_set` 不會自己卡住)。不過 settle 開頭的 pending 檢查讀的是鎖外預先載入的筆記快照,兩個 settle 同時跑時,第二個會拿舊快照走進補救路徑;實際重寫前會重讀檔案,結果無害,所以不另開 finding。
- 資料汙染:考試會寫進被考 repo 的治理帳(F15)。
- 金流、對外送出、不可逆:無。只讀 git、只寫本機檔與 jsonl,理由同 spec 第 132–134 行。

總結:最嚴重的等級是 major;blocking 共 5 條(F1–F5),另有 12 條不擋。
