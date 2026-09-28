severity: major

# r3 正確性/邏輯席(opus)

範圍:整份凍結快照逐節讀完;程式碼對照 clone-ns `scripts/lumos`、`scripts/test_lumos.py`;考卷、改寫檔、README 在 rtb 唯讀複本上用 `git -C` 重驗(只跑 show/grep/diff/log/ls-tree)。

考卷與改寫檔重驗結果(全部成立,不另立 finding):
- 11 題正例(A4–A7、B1–B4、E1–E3)在「事件提交的上一版」與「事件提交」兩棵樹上,筆記(有 note_at_event 就用它)的第 `line` 行跟 `text` 一字不差;E3 那篇在 b2fc512 的上一版不存在、b2fc512 新增(A 狀態)。
- A4/A5/A6 的事件提交各自只把一篇守衛紀錄的 status 從 pending 改成 pass,三篇都有 `guards` 欄,四種預告句在第 18、19、25、27 行。
- 改寫檔:`src/rtb/analyzer/runner.py` 在 8ff8c95 的上一版不存在、8ff8c95 存在(B1/B2/B5);`MAX_INCREASE_NUMERATOR` 在 0ffba7d 的上一版全樹 0 處,0ffba7d 在 `src/rtb/executor/execution.py:282` 以模組層 `MAX_INCREASE_NUMERATOR = 1` 出現(A7/B4);Phase 12 計劃在 f183cd8 的上一版不存在、f183cd8 建立時 status 是 doing(B3)。
- E1:ef10bc7 把 Phase 12 計劃從 doing 改成 done,計劃第 29 行有 `[[Issues/Phase12需要可看任務階段與處置的HTML報告]]`。E2:7413936 把 Phase11B 計劃改成 done,它第 19 行有 `[[Issues/Phase11後接入大模型API的三個階段]]`。
- 〈審計修正紀錄〉r2 列的折入項逐條對正文:文法、可見行、共用 REVISIT 判定、同一行、只評估相關條件、判不了算要處理、doctor Z 不跑 git、ack 的 --kind 與綁定、c1 的 WHY 與第四句、c3 排除、c5、when-status 不存在、when-test 版面、Python 定義樣式、第二層只排除條件式、E5 印條數、set 只給檢視指令、回退節四點、考卷 B3/B1/current_state/B5、落點節、併發段、多分支時間——全部都在正文找得到。B3 改 f183cd8、B1 只留 8ff8c95 在考卷 JSON 裡也對上了。沒發現「紀錄說折了、正文沒有」的。

## F1 決定預設 block 的門檻在這份考卷上不可能不過

severity: major
blocking: 是 — 預設模式會被一個結構上必過的考試定成 block,推給所有消費專案,實作者卻以為「非漂移零誤列」真的被測過
引句:「這個門檻只有 rtb 一個專案、11 題正例與 13 題非漂移的樣本,是已知的薄弱依據」
file: `governance/eval/drift-exam/rtb-2026-09-28.json`(13 題非漂移:12 題 exam_event=current_state,B5=probe)

1. 門檻條件一是「要處理」層不能誤列任何非漂移題(B5 另計)。13 題非漂移裡,B5 被排除,剩下 12 題全走 `current_state`,也就是「在 067f005 跑 scan,那一題的行被列(任一種)算」。但 scan 按〈做法〉第 0 節和第 2 節第 3 點只「列出全部發現」,沒有把發現分成「要處理」和「只列出」兩層;分層是 check 才有的概念。所以這 12 題根本不會產生「要處理」層的誤列,能產生這一層誤列的非漂移題是 0 題。
2. 就算實作者把 scan 裡 c1 和已成立的條件對映成「要處理」:`git -C rtb-exam grep -c -F -e "[when-" 067f005 -- docs` 找到 0 處,因為 rtb 沒有任何條件式的行,current_state 又不套改寫。所以 scan 在 067f005 能列出的只有 c1–c5。這 12 題裡只有 R2、R3 落在守衛紀錄裡(F1、F2 兩篇),題目行是第 21 行(decision_refs_ai),而 c1 報的是第 18/19/25/27 行,行號對不上,不會算成誤列。
3. 門檻條件二是噪音 ≤5。rtb 歷史上沒有自然存在的條件行,所以每個考題提交的「要處理」只可能來自:c1(每個考題提交只轉正一篇守衛紀錄,最多 4 行)、改寫進去的那 1 行,和判不了的。照構造就是 ≤5。
4. 結論:兩個條件都不可能失敗,「預設 block」在實作前其實就已經定了。正文說樣本是「13 題非漂移」,但對這個門檻真正有鑑別力的非漂移樣本是 0 題。只有「只列出」層有東西可量:例如 E4(`Issues/執行迴圈收到SIGTERM等於硬殺.md` 第 3 行 `status: open`,稽核判它是對的)在 067f005 連到 `[[Projects/RTB_Phase12一鍵展示與HTML報告_計劃]]`,而那份計劃已是 done,所以 c2 一定會把 E4 的第 3 行列出來,算「只列出」層誤列 1 筆。
5. 另外,S13 要求 current_state 報「兩層誤報」,但 scan 沒有分層,那條測試寫不出確定的期望值。

## F2 c1 的一筆發現對一行還是對一篇沒定,考卷卻拿第 19 行比對

severity: major
blocking: 是 — 照一篇一筆實作,A4–A6 三題會被算成「漏」,甲的考試結果和擋下報告都會錯
引句:「驗證紀錄 status 是 pass、有 `guards` 欄,而且還有第 1 點那四種固定句的任一種」
file: `rtb-exam` 裡 `1eace79:.../Verification/2026-09-22_事故-F2-…md` 與 `16136d6:.../Verification/事故F3_…md`,WHY 在第 18 行、TEST 在第 19 行、兩句正文在第 25、27 行

1. c1 的判準寫成整篇守衛紀錄的條件(「還有四種句子的任一種」),可是第 4 點又要求「每筆發現回報哪篇、哪一行」。實作者會有兩種做法:(a) 一篇一筆,回報第一個命中的行;(b) 一句一筆,一篇最多 4 筆。
2. 照 (a):A4/A5/A6 第一個命中的是第 18 行(WHY),考卷三題的 `line` 都是 19(TEST)。exam 用「那一題的筆記與行在要處理」比對,三題全部算漏,但閘其實擋到了。
3. 照 (b):一篇就 4 筆「要處理」,`drift ack … --kind c1` 得對每一行各表態一次。而且一次推送只要轉正 2 篇就是 8 筆,超過〈做法〉第 4 節第 4 點「每個考題提交 ≤5」那條噪音線(這次考卷剛好每個提交只有一篇,所以沒碰到)。
4. 缺的是:c1 發現的粒度,以及 exam 的比對規則(按行號、按原文,還是按「同篇任一行」)。

## F3 c1 和 settle 共用的「固定句」沒定錨點,改寫後的句子仍包含原句

severity: major
blocking: 是 — 照字面用子字串比對,新版 settle 轉正後的那次推送一定被自己的 c1 擋下
引句:「正文 `為什麼還不做:` → `預告當時為什麼還不做:`」
file: `scripts/lumos:11572`(樣板 `為什麼還不做:{why}`)、`scripts/lumos:11573`(樣板 ``做完之後跑 `lumos guard settle` 轉正,不要手改狀態。``)

1. settle 會把正文的 `為什麼還不做:` 改成 `預告當時為什麼還不做:`,改完的句子仍然包含原句當子字串。c1 的判準只寫「還有四種固定句的任一種」,沒說要從行首比對。
2. 會出錯的情境:用新版 settle 轉正,再推送。範圍裡有 pending→pass(第 5 點),check 對那篇跑 c1;如果用子字串比對,`預告當時為什麼還不做:…` 會命中,推送被擋,作者只能表態或略過。S4、S8 的測試如果沒有「settle 之後跑 check」這一段,這個問題不會被測到。
3. 第四句:程式樣板裡是 ``做完之後跑 `lumos guard settle` 轉正``,帶反引號;但 spec 第 1 點寫成 `做完之後跑 lumos guard settle 轉正…`,反引號在 markdown 裡被吃掉了。實作者照 spec 的字面寫比對,會找不到第四句:settle 每次都印「找不到固定句型」,c1 也永遠看不到第四句。
4. 另一個會出錯的情境:作者只改了 TEST 行的日期。如果 settle 比對整句(含日期與負責人)而 c1 只比前綴,settle 會跳過這句,c1 卻還是命中,推送同樣被擋。spec 沒要求 settle 和 c1 用同一支比對函式、錨定行首(去掉摘要的縮排之後)。

## F4 「只評估相關條件」跟「一行多個條件全部成立才算成立」互相矛盾,另外漏了改名

severity: major
blocking: 是 — 照字面實作,帶兩個條件的行會被誤擋,或被當成判不了而擋下
引句:「其他條件起點與終點結果一定一樣,不評估」
file: 無(spec 內部矛盾)

1. 第 0 節的篩選單位是「條件」,但成立與否的單位是「行」(一行多個條件是 AND)。輸入:`REVISIT:[when-file:src/a.py][when-symbol:Foo] …`,這次推送新增 src/a.py,而 Foo 從來沒定義過。
2. `when-file` 通過篩選,`when-symbol` 沒通過(Foo 不在改動行),照字面「不評估」。這時整行是否成立無從決定:如果把沒評估的條件當成立,這行被算成「起點不成立、終點成立」,擋下(誤擋);如果當判不了,照第 0 節「判不了算要處理」,也是擋下。正確答案是「不成立、不列」。
3. 正確的說法應該是:篩選選的是「行」(任一條件落在範圍事件裡),被選中的行要在兩端評估它所有的條件。spec 沒這樣寫。
4. 篩選也漏了改名:① `when-symbol:src/new.py::Foo`,這次把 src/old.py 原封不動改名成 src/new.py。`git diff` 預設會偵測改名,純改名沒有改動行,Foo 不會出現在改動行裡,這行不被評估,真正的事件就漏了。② `when-status:Projects/X_計劃=doing`,X 是由另一篇 doing 的筆記改名而來。git 把它標成 R,不是 A,篩選條件只寫「被新增或刪除」,同樣漏掉。`file` 鍵有明寫「改名」,但 `symbol`、`test`、`status` 沒有。

## F5 E5「0 條也印」撞上既有紅釘:全靜默

severity: major
blocking: 是 — 實作者照做會打破一條既有的紅釘測試和一個設計決定,spec 卻沒說要翻這個決定;而且 check-revisit 事件可能每天都發
引句:「(N 是 0 也印),這樣就算推送閘拔掉,這些行在 doctor 還看得到」
file: `scripts/test_lumos.py:34604`(`t_doctor_revisit_reminder` 紅釘⑤「0 到期 0 壞行=整段不印(全靜默慣例)」)、`scripts/lumos:1947`(E5 註解「全靜默」)、`scripts/lumos:1989`(`check-revisit warned` 事件在同一個 if 裡)

1. 目前 E5 只有在有到期或壞行時才印 `[E5]` 段;紅釘⑤斷言沒有到期、沒有壞行時 stdout 裡不能出現 `[E5]`。〈回訪掃描_計劃〉把「全靜默」列成設計。
2. spec 要 E5「一律」印條數,0 也印,這跟紅釘⑤直接衝突。S11 只說「一律印出條件式回頭條件的條數」,沒提要改這條紅釘,也沒提翻掉那個決定。
3. 連帶的問題:如果實作者把整段改成一律印,又沿用同一個 if 塊,`check-revisit warned` 事件就會每次 `doctor --ci` 都寫。nags 那條連喊 ≥14 天就升級的規則,會把「沒有東西到期」也升級。spec 要寫明這一行要放在哪(比如放 Z 段,或 E5 以外的地方)、事件要不要跟著發。

## F6 條件式回頭條件沒有期限可退,名字寫錯或評估器認不得就永遠不會觸發

severity: major
blocking: 是 — 改寫 rtb 那約 45 條、工具鏈自己的舊條件時,會把原句裡「到期還沒發生就重看」的語意丟掉,而且寫錯的條件沒有任何地方會唸
引句:「日期或條件二擇一放在 `REVISIT:` 後第一個位置」
file: `rtb-exam` `067f005:…/Projects/RTB_Phase3外部寫入安全_計劃.md:197`(B1 原文含「若到這天仍沒有啟動程式,重看這條必答的證據是否足夠」)、`governance/eval/drift-exam/rtb-2026-09-28-probes.json`(B1 改寫後沒有日期)

1. 日期和條件只能二選一,條件式的行就不再受 E5 的到期檢查。scan 只列三種:已成立、寫錯(形狀不合,或 status 指到不存在的筆記)、判不了。
2. 會出錯的輸入:① `[when-symbol:MAX_INCRASE_NUMERATOR]`,名字拼錯,形狀是合法的,永遠不成立,scan 不列、doctor 不唸、閘不擋。② Python 常數寫成 `MAX: Final = 3` 或 `MAX=3`,第 2 節第 1 點只認「模組層 `名稱 =`」,定義了也判成不存在。③ `when-file` 的路徑拼錯,結果同 ①。這三種情況下,那條回頭條件都悄悄失效,再也不會被看到。
3. rtb 原文 B1、B5 都是「事件,或到某天」兩個觸發(B5:「還沒有啟動程式就把日期往後延」)。改寫檔把日期拿掉了,第 4 節修復階段照這個樣子改,就會系統性地丟掉期限那一半。〈誠實界線〉只講到「任一成立寫兩行」,可是日期行和條件行寫成兩行時,處理掉一行並不會連動另一行,這點也沒寫。
4. RETIRE-IF 三個量都測不到「條件永遠不成立」這種失效。

## F7 status_replay 要的「那份計劃」考卷沒有欄位,E2 的失效提交一次收尾兩份計劃

severity: minor
blocking: 否 — 實作者可以從失效提交的 diff 反推,但要自己定規則
引句:「在記憶體裡把那份計劃的 status 改成 done」
file: `rtb-exam` `git diff 7413936^ 7413936`(Phase11B 與 Phase8 兩份計劃都從 doing 改成 done)

1. 考卷每題的欄位裡沒有「要收尾的是哪份計劃」。E1 的 ef10bc7 只收尾一份(Phase 12),推得出來;E2 的 7413936 收尾了 Phase11B 和 Phase8 兩份,只有 Phase11B 連到那篇 Issue。實作者得自己決定是兩份都改,還是挑有連結的那份。
2. 「另跑 check,出現在只列出也算點到」沒寫 check 的範圍。在記憶體裡改過的樹不是一個提交,check 讀不到;應該寫明用「失效提交的上一版..失效提交」這段真實範圍。

## F8 第一層要擋「不評估的地方」,三處講的範圍不一樣

severity: minor
blocking: 否 — 測試寫法會不一致,但不會做出壞系統
引句:「(decisions 欄)的條件標記也擋——寫了不會被判,是死語法」
file: 無(spec 內部不一致)

1. 第 2 節第 4 點只擋 decisions 欄;S10 寫「條件寫在不評估的欄位時擋下」(泛指);第 0 節列的不評估欄位有 `valid_under`、`revalidate_when`、decisions…。
2. 輸入:新寫一行 `valid_under: … [when-file:src/x.py]`。照第 2 節第 4 點放行,照 S10 擋下。`t_note_shape_revisit_needs_date_or_probe` 的期望值得二選一。

## F9 「日期式」怎麼切沒定義,跟 E5 解析日期的方式對不上;列表記號變多也會改到 E5 的範圍

severity: minor
blocking: 否 — 第一層可能放行 E5 會判成壞行的寫法,但 E5 照樣會唸
引句:「後面第一個東西若是一個條件標記,這行是」
file: `scripts/lumos:1964-1969`(E5 取到第一個空白為止,用 `fromisoformat` 解析)、`scripts/lumos:1961-1962`(E5 只去掉 `- ` `* `)

1. E5 把 `REVISIT:` 後面到第一個空白為止的字串拿去解析日期,`REVISIT:2026-11-19(…` 會被算成壞行。工具鏈自己的圖譜已經有 `REVISIT:2026-11-19(`、`REVISIT:2026-10-05;` 這種寫法(`grep -rhoP "REVISIT:\s*\d{4}-\d{2}-\d{2}\S" docs/lumos-toolchain-knowledge`)。
2. 第 0 節的「第一個東西是 YYYY-MM-DD」如果用前綴正則判,第一層會放行這種新行,E5 卻把它記成格式壞損。應該寫明「日期式 = 通過 E5 同一種解析」。
3. 共用判定多認了 `+ `、`1. `、`1) `、`> `,E5 改用共用判定後範圍會變大:引用區塊裡的 `> REVISIT: …` 會開始被計入壞行。第 2 節第 2 點說 E5「改一處」,其實不只一處。

## F10 `<節點>` 的寫法和目錄路徑沒定義

severity: minor
blocking: 否 — scan 會把指不到的 status 列成寫錯,算有兜底
引句:「`status` 是 `<節點>=<值>`(從第一個 `=` 切,兩邊都不能空」
file: `governance/eval/drift-exam/rtb-2026-09-28-probes.json`(B3 用的是圖譜相對路徑、不帶 `.md`)

1. 沒定義 `<節點>` 能不能帶 `.md`、能不能只寫檔名主幹、是不是相對於圖譜根目錄。lumos 其他指令(env.find)都收檔名主幹;但在某個提交的樹上評估,要先把整份圖譜列出來才解析得到主幹。第一層、check、第 2 節第 7 點(`lumos set` 的文字比對「條件指的節點就是這份」)三處如果各自認一套寫法,同一行在三處會得到不同結果。
2. `when-file:src/rtb/analyzer`(一個目錄)合乎文法:沒有 `/` 開頭、沒有 `..`。但篩選看的是 `git diff` 列出的檔案路徑,目錄路徑永遠不會出現在裡面,所以這行在 check 裡永遠不被評估;「那支檔存在」對目錄算不算也沒定。

## F11 `lumos set` 的待辦跟 c3 範圍不一致,第③項沒管同一行的其他條件

severity: minor
blocking: 否 — 只是多印
引句:「`plan_refs` 指到它、status 是 pending、沒有 `guards` 欄的驗證紀錄」
file: 無

1. 第②項:一篇驗證紀錄的 `plan_refs` 是 [A, B],B 還是 doing。A 收尾時 set 會列出它,但 c3 要求 plan_refs「全都已收尾」,不會列。兩處講的「計劃收尾了、驗證紀錄還待定」不是同一個集合。
2. 第③項:`[when-status:A=done][when-file:x]` 這一行,只做 status 的文字比對就會報「因此成立」,但 x 還不存在,照 AND 語意這行其實不成立。

## 各節無 finding 的交代

- 開頭、PRIOR-ART、RETIRE-IF:已讀,無 finding。借用的函式都驗過:`_nodehome_clamp_base` 找不到標記時回原起點,所以 rtb 考試不會被截斷;`_vault_write_lock` 可重入;`_nodehome_is_test` 要傳 layout;`_nodehome_reader` 讀提交時跟工作目錄一樣的檔直接讀磁碟,內容等價;`_note_audit_items` 是第二層的待審行入口。以上都符合 spec 的用法。
- 範圍:已讀,無 finding。沒有殘留依賴丙,或依賴健檢的符號、測試存在性檢查的文字。
- 回退:已讀,無 finding(settle 不准單獨還原守衛紀錄的理由,跟現行 `cmd_guard_settle` 先改家筆記、再 `cmd_set` 的兩步寫入一致)。
- 落點:已讀,無 finding(`Systems/存量漂移守衛` 還不存在,標了「新開」;其他 lands_in 和 related 節點都在)。
- 實務隱患、誠實界線:已讀,除 F4、F6 以外無 finding。
- 相關既有節點:①舊句偵測實驗:本 spec 沒有文字依賴它的產出,不影響。②code 側刪除傳播守衛:沒碰刪除傳播,不影響。③筆記形狀擋/筆記內容閘:加一條 REVISIT 規則,沿用上線點截斷,舊行不管,不破壞既有宣稱(F8、F9 是規則本身沒定清楚)。④筆記內容審/Systems/筆記內容審:只排除條件式行,日期式照審,不破壞「新寫的現況句要判」的宣稱。⑤guard-kill:settle 改成單次寫入,再加補救路徑,跟它記的「還原不出原文會卡死」那條 PITFALL 同方向;F3 是新的問題。⑥治理帳多個寫入者都沒上鎖:spec 把兩個新寫入者補進那篇 Issue,沒有宣稱已經解決,不影響。⑦存量漂移三種機制 Issue:本 spec 只處理機制②③,範圍一致。

實務隱患逐類:
- 誤報與疲勞:見 F1(門檻測不到)與 F3(settle 之後自己擋自己)。
- 漏抓:見 F4(改名、AND)與 F6(永不觸發)。
- 效能:check 每個條件要在兩端各評估一次,不是「最多一次」;但條件數量小,無新隱患。
- 併發:settle 包在可重入鎖裡,已驗;表態檔一次追加一行,已交給 Issue 處理;無新隱患。
- 輸入安全:用 `-e`/`--` 隔開,又禁止 `/` 開頭與 `..`;無新隱患。
- 相容與回退:見 F5(既有紅釘)。
- 金流、對外送出、不可逆:無,理由同 spec(只讀寫本機筆記與 git 裡的檔)。

最嚴重等級 major;blocking 共 6 條(F1–F6),另 minor 5 條。
