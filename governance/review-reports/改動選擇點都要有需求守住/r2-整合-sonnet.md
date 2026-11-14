severity: major

## i1 choice-kill 宣稱中斷時「已有結果的壞法照記」,但 `cmd_guard_kill` 只在整圈跑完才交出結果列;缺列還會被判成 survived
severity: major
blocking: 是——照字面實作,一次被 SIGTERM 或逾時打斷的長跑會丟光所有進度,而且缺列的壞法可能被記成假的 survived,擋人又誘人亂判。
- 範圍 2「共用」與「記」。
- 引句:「第一個訊號 → 等這次殺傷力收尾、已有結果的壞法照記、rc 2」
- 引句:「中斷時已有結果的照記、`run` 那筆照記(帶 `interrupted: true`)」
- 引句:「其餘全部 `survived` → **survived**」
- 查證一,部分結果交不出來。
  - `cmd_guard_kill` 的 `result_out["rows"]` 在所有平台組的迴圈跑完之後才填。
  - 第一個訊號走 `_on` 裡的 `raise KeyboardInterrupt`。`_kill_run` 收掉程序群組後再往上丟,例外穿出 `cmd_guard_kill`,`result_out` 從頭到尾沒被指派。
  - 所以人裁那套兩段式「沿用」過來,只能做到收乾淨、不記任何結果。它不是「等收尾」,是立刻中斷。
  - 具體例:M×T=200 次 Gradle,跑到第 150 次被對話工具逾時的 SIGTERM 打斷 → 150 次結果全丟,ledger 只剩 `run`(interrupted)。
  - spec 的「共用」只列 `source` 一個參數,沒列要讓 `cmd_guard_kill` 邊跑邊交出結果。
- 查證二,缺列沒有判法。
  - 迴圈裡 revert 失敗會 `break`,同組後面的配方一列都不產生。
  - 〈用詞〉殺掉判定只講「任一支 killed」「任一支是 killed_unattributed…→ no_result」「其餘全部 survived」。
  - 該壞法零列時,「全部 survived」空真為真;只有部分測試列時,漏掉的那支可能才是會殺掉它的測試。兩種都會記成假的 survived。
- file: `scripts/lumos:28149`(`result_out` 在迴圈後才指派)
- file: `scripts/lumos:28102`(revert 失敗後 `break`,後面的配方沒有列)
- file: `scripts/lumos:27769`(`_kill_run` 的 `KeyboardInterrupt` 收程序群組後 `raise`)
- file: `scripts/lumos:76015`(`_situation_rule_signals`:第一個訊號 `raise KeyboardInterrupt`)
- 建議:殺掉判定明定「該壞法每支守的測試都要有列才算數,缺列 = no_result(原因 缺結果)」。同時在「共用」裡寫明 `cmd_guard_kill` 要增量交出結果,或承認中斷就整批重跑並改寫 S9。

## i2 回報上限以 B 當種子:每次提交帳就換 B、換一批抽,上限擋不住人要處置的總量
severity: major
blocking: 是——S13 這條 spec 照字面做得出來,但它要守的目的(限制人的認知負擔)被自己的流程架空,還會把已通過的代碼審打回。
- 範圍 4「回報上限」、〈用詞〉回報上限、S13、天花板 7。
- 引句:「下一次推送(B 變了)會重抽」
- 引句:「推送閘只讀被推送版本的帳」
- 推演:改 2 支 .kt、存活 20 個,上限 14。
  - 作者處置抽中的 14 個,必須提交帳,這會產生新提交,B 就變了。
  - 下一次推送在剩下 6 個裡重抽,6 < 14 → 全抽中,全擋。
  - 結果是上限只是把「全部要處置」拆成多輪;推送輪數與總工作量不減。
- 跟代碼審的先後衝突:第 1 輪若用 `situation-rule --point` 處置,就改了計劃,已過的代碼審留痕失效(`_situation_rule_next` 自己就印這條提醒)。
  - 實務隱患「choice-kill 與處置在 `code-loop pass` 之前做」假設只有一輪;但存活有沒有被抽中,要到推送才看得到。
- 論文對照:
  - 2.3 的「最多 7 × 檔數」是限制人要看的量,而且論文的發現不是強制(2.4:除非審查者標為必處理)。
  - 3.2.4 的重點是跨快照的穩定回報。這裡是同一個 B 穩定,但一提交就洗牌,跟 3.2.4 的目的相反。
- 建議:種子改用不含帳本提交的東西(例如範圍內非簿記檔的最後一個提交、或存活身分集合本身的雜湊),或承認抽籤只在第一次推送有效。
- file: `scripts/lumos:72609`(代碼審通過後的簿記提交訊息;帳本是簿記檔,但計劃不是)
- file: `scripts/lumos:76522`(`_situation_rule_next` 第 3 點:提交後已過的代碼審留痕失效)

## i3 壞法的挑選只在「同一份型錄」下穩定;型錄一改,已處置的行全部變成「缺紀錄」
severity: major
blocking: 是——型錄改動是這個設計預期會天天發生的事(乾節點與表由人照回饋增補),字面實作會讓每次改表都造成全分支重跑 Gradle。
- 〈用詞〉一行一個壞法、壞法身分,以及〈回退〉。
- 引句:「推送閘在 B 版重算壞法再用雜湊對」
- 引句:「型錄照 `_kt_catalog_path()` 取(工具鏈來源那份」
- 引句:「單一列誤報多:從〈選擇點表〉拿掉那一列,或在〈乾節點規則〉加一列(下一次推送就不再算)」
- 機制:候選清單、洗牌結果與「已知編不過的形狀」都依賴型錄。型錄來自工具鏈來源,不隨被推送版本(B)走。
  - 例一:ROR 列補一個候選,或拿掉 AOR 列 → 同一行重算挑中的壞法換了 → `new_sha`/`member` 對不上 → 該行原本的 killed 失效,變成缺紀錄。
  - 例二:兩台機器的工具鏈版本不同,作者那台記的帳在推送那台對不上。
  - 〈回退〉只講那一列「不再算」,沒講同一行上其他列的選擇會跟著洗牌。
- 建議:帳列帶 `catalog` 版本指紋,而且閘以「那一行(line_sha)有任何有效處置」為準;或型錄變動後,舊紀錄在該行沒變時視為有效。
- file: `scripts/lumos:39302`(`_kt_catalog_path`:工具鏈來源,不隨被推送版本)

## i4 候選壞法 `a`、`b`、`true`、`false` 需要運算元範圍,spec 只定義了運算子 token 的位置
severity: major
blocking: 是——實作者無法照 spec 生成 `new`,只能自行發明運算元切法,每種切法的編不過率與等價率都不同。
- 〈用詞〉選擇點表(ROR、LCR、AOR),〈用詞〉選擇點,〈用詞〉壞法身分。
- 引句:「LCR:`a && b` → `a || b`、`a`、`b`、`true`、`false`」
- 引句:「運算子成員要兩側是空白或換行(`a > b`、行尾的 `a &&`)」
- 引句:「`new` 是 `old` 套上壞法」
- 問題:
  - 只有 `&&`→`||`、`>`→`>=` 這類換運算子的候選,靠定位運算子 token 就做得出來。
  - 換成 `a`、`b`、`true`、`false` 要知道 `a`、`b` 從哪裡到哪裡,論文靠 AST,spec 的天花板 2 只承認「不照格式寫的運算子會漏」。
  - 例:`if (x != null && list.any { it.id > limit } || forced)`。把 `&&` 換成 `a`,要刪掉的右半邊在哪裡結束,文字比對沒有答案。
  - 行尾 `&&` 的運算元在下一行,`old` 只有「那一行(+最多前後各 2 行)」,而 `old` 要唯一。換成 `b` 要不要改到下一行,spec 沒說。
- 建議:第一版候選只收不需要運算元範圍的(換運算子、`!` 增刪、API 改名、整行刪),`a`、`b`、`true`、`false` 等有 AST 才做。

## i5 `situation-rule --point` 只講入口驗證,依賴情境段 `sg` 的內部函式都沒處理
severity: major
blocking: 是——「其餘照原本流程」照字面做,會在 `meta["seg"]` 之類的地方當掉,或印出對選擇點無意義的指示。
- 範圍 3「規格沒寫」。
- 引句:「`--seg`/`--row`/`--file`/`--old`/`--new` 改成選用,跟 `--point` 互斥(入口驗證)」
- 引句:「條款寫回、綁測試、跑殺傷力(要 killed)、記人裁事件照原本流程」
- 查證,都依賴 `sg`/`seg`/`row`:
  - `_situation_rule_platform(env, rr, sg)` 用 `sg["file"]`,而且只看預設平台。
    - S5 要求守的測試可在非預設平台,`--point` 的 `--test` 在非預設平台時殺傷力會跑錯平台。
    - 它的拒絕訊息指向「段放行」,選擇點沒有這個出口。
  - `_situation_rule_also(rr, sg, …)` 的 `--import` 同樣吃 `sg["file"]`。
  - `_situation_rule_event_parts` 取 `meta["seg"]`、`meta["row"]`,沒有就 `KeyError`。
  - `_situation_rule_show` 與 `_situation_rule_next` 印的是段、列、「重答這一列的出處」,對 `--point` 都不成立。
  - `_situation_rule_already` 的 `seg=None,row=None` 比對:任何 point 事件都會對上任何 point 事件。spec 已補「改用壞法身分」,這一點到位。
- file: `scripts/lumos:75924`
- file: `scripts/lumos:76329`
- file: `scripts/lumos:76117`
- file: `scripts/lumos:76507`
- file: `scripts/lumos:76522`
- 建議:寫明 point 路徑要抽出「平台與檔路徑解析」「事件欄位」「結尾提示」三塊;平台改照每支測試的平台取(同 choice-kill)。

## i6 `spec-gate --push-check` 加旗標:「同 `pitfalls` 那條」不成立,版本錯開時會讓整道規格閘靜默失效
severity: major
blocking: 是——掛鉤與 `scripts/lumos` 是分開複製的,新掛鉤打舊 lumos 會讓參數被 argparse 拒絕;這道閘只認 rc 1 才擋。
- 範圍 4「接線」。
- 引句:「`spec-gate --push-check` 新增選用參數 `--push-remote <遠端>` 與 `--pushed-ref <被推的 ref>`(同 `pitfalls` 那條)」
- 引句:「pre-push 掛鉤照 pitfalls 那行的寫法傳入」
- 查證:
  - `pitfalls` 只收 `--pushed-ref`,不收 `--push-remote`。`--push-remote` 加 `--pushed-ref` 成對出現的先例是 drift、room-guard、reread-check。
  - 掛鉤對 pitfalls 的做法是先 `grep` 找專屬字樣 `dest="pf_pushed_ref"` 探版本、有才帶旗標。掛鉤註解寫明理由:舊版 argparse 拒絕會讓整份輸出消失。
  - `spec-gate --push-check` 要有自己的探針字樣,spec 沒提。
  - 掛鉤現在只在 `sg_rc -eq 1` 時擋,其他非零(argparse 的 rc 2)被當放行。新掛鉤配舊 lumos → 推送前規格閘的全部既有圈(風險低留痕、預期值表、依據來源)都悄悄不跑。
- file: `scripts/hooks/pre-push:504`
- file: `scripts/hooks/pre-push:566`
- file: `scripts/hooks/pre-push:592`
- file: `scripts/hooks/pre-push:621`
- file: `scripts/lumos:79668`
- file: `scripts/lumos:79332`
- 建議:寫明加探針字樣、沒有旗標就走「只用推送範圍本身」。

## i7 「碰到的計劃」照 `_spec_gate_push_candidates` 取,但它讀工作目錄圖譜,跟「只看 B 版本」互相矛盾
severity: major
blocking: 是——spec 自己有兩句互斥的話,照字面做必然違反其中一句,S16 的後半在計劃狀態不同的情況下會做錯。
- 範圍 4「讀哪一版」、〈用詞〉碰到的計劃、〈用詞〉生效日。
- 引句:「碰到的計劃**:照 `_spec_gate_push_candidates`:範圍改到的計劃檔」
- 引句:「不讀工作目錄的 `env.notes`」
- 查證:
  - `_spec_gate_push_candidates(env, rr, vrel, touched)` 吃 `env.notes`(`status`、`lands_in`、正文連結)與家對照表(`_impact_home_map(env)`),都來自工作目錄。
  - 例:B 版的計劃 status 是 doing,工作目錄已手改成 done 但沒提交 → 候選漏了,被擋「無規格」,但 B 其實有進行中計劃。反過來,工作目錄多一份未提交的 doing 計劃 → 候選有它,`git show B:<計劃>` 讀不到,spec 沒說這時怎麼辦。
  - 既有先例:情境題的 `_kt_sit_spec_names_calc` 用 `_drift_tree_env` 從被推版本的樹建記憶體圖譜,再交同一支 `_spec_gate_push_candidates`。spec 沒指名它。
  - 〈用詞〉生效日用 `_plan_effective_day(rr, prel, created, head=None, scope="note")`,`created` 來自 `env.notes`,`head=None` 時看 HEAD 的 git 歷史,不是 B。
- file: `scripts/lumos:16535`
- file: `scripts/lumos:74823`
- file: `scripts/lumos:58201`
- file: `scripts/lumos:14511`
- 建議:指名用 `_kt_sit_spec_names_calc` 或 `_drift_tree_env(B)` 的記憶體圖譜取候選與狀態,`created`/日期同樣取 B。

## i8 「一行一個壞法」的篩選條件跟「往外帶行求唯一/標不唯一」互相矛盾;不唯一的行沒有處置出口
severity: minor
blocking: 否——照哪一邊實作都做得出來,S3 的預期值表會抓出分歧;出口是改程式,不是死路。
- 〈用詞〉一行一個壞法、壞法身分、S3、範圍 4「判定」、範圍 2 判。
- 引句:「而且不是已知編不過的形狀」
- 引句:「那一行不唯一時 應 往外帶行求唯一,仍不唯一標不唯一」
- 引句:「對回報上限挑中的存活與全部 no_result、不唯一、過期、缺紀錄的行 → 擋」
- 引句:「存活或 no_result 都能判」
- 問題:
  - 一行一個壞法那句要「新那一行在整支檔裡恰好一次」才算候選,壞法身分那節又讓不唯一的行往外帶行,仍不唯一標「不唯一」。
    - 若前者指原行恰好一次,重複行永遠是「沒有壞法」,到不了不唯一狀態,S3 第二列過不了。
    - 若指壞法後的新行,它對 `old` 的唯一性沒有幫助(`cmd_guard_kill` 要的是 `src.count(old) == 1`)。
  - 判定對「不唯一」要擋,`--judge` 只列存活與 no_result。不唯一的行沒有可用的 `old_sha`,記不了 judged。出口只剩改程式讓上下文不同,spec 沒寫。
- file: `scripts/lumos:28060`(`cmd_guard_kill` 要 `old` 在檔裡恰好一次)

## i9 對照論文原文:運算子表被縮小卻標「論文表 1」,而且沒列入「跟論文不同」
severity: minor
blocking: 否——spec 內部自洽,只是引用不實,會讓人以為忠實於論文。
- 〈用詞〉選擇點表、PRIOR-ART、依據來源表。
- 引句:「ROR(論文表 1):`a > b` → `a >= b`、`a < b`、`true`、`false`」
- 引句:「AOR:`a + b` → `a - b`、`a`、`b`」
- 引句:「UOI:布林運算元 `b` → `!b`;拿掉前置 `!`」
- 引句:「`==` 只換 `!=`、`!=` 只換 `==`(論文附錄 A.1.23)」
- 引句:「每行一個(隨機排序運算子、第一個產得出的就用)」
- 論文表 1 原文:
  - ROR:`a > b → {a < b, a <= b, a >= b, true, false}`。spec 少 `a <= b`。
  - AOR:`a + b → {a, b, a - b, a * b, a / b, a % b}`。spec 少 `*`、`/`、`%`(Just 等的縮減版才是這樣,但 spec 沒這樣引)。
  - UOI:`a → {a++, a--}; b → !b`。「拿掉前置 `!`」不在表 1。
  - A.1.23 只說 `==` 只換 `!=`、`===` 只換 `!==`,沒有「`!=` 只換 `==`」。
- Listing 2 是洗牌「運算子」,每個運算子產一個壞法,第一個產得出的就停。spec 的 PRIOR-ART 這樣轉述,〈用詞〉卻是把整行所有(選擇點 × 候選)排成一個清單洗牌,對應 Listing 1 的均勻隨機加備援,偏向候選多的運算子。
- 這些都該進「跟論文不同的地方」清單。

## i10 乾節點規則第一版漏掉論文自己點名的高產類,PRIOR-ART 清單與〈乾節點規則〉第一版不一致
severity: minor
blocking: 否——規則由人增補,但擋推送的閘會在第一版噪音偏多時先累積誤擋。
- PRIOR-ART、〈用詞〉乾節點規則。
- 引句:「提早 return、旗標、資料流 flush/close、依賴注入」
- 引句:「第一版照論文附錄 A 譯成 Kotlin:log(」
- 論文 3.2.5:一開始生產力提升最大的三項是 log、時間(deadline、timeout、backoff)與設定旗標。附錄 A.1.13、A.1.16 是旗標/閘設定。
- spec 的 PRIOR-ART 列了「提早 return、旗標」,〈乾節點規則〉第一版沒有這兩類。
- 附錄 A 在 Kotlin 常見但沒譯的:
  - A.1.10:與 null 比較。
  - A.1.11:浮點數 `>`↔`>=`。
  - A.1.20:集合 `size` 與 0 比較。
  - A.1.22:`isEmpty()` 提早 return。
  - A.1.24:`coerceIn`/`minOf`/`maxOf`。
- 「照附錄 A 譯成」的說法過頭,應列出譯了哪幾條、哪幾條不譯與理由。

## i11 論文 3.2.1 要求「事前不產生編不過的壞法」,spec 改成事後 `no_result` 加人判;「已知編不過的形狀」沒有實體
severity: minor
blocking: 否——有出口(`not-applicable`),但每個編不過的壞法要付一次完整 Gradle 加一次人判。
- 依據來源表、〈用詞〉編不過的形狀、一行一個壞法。
- 引句:「| 編不過的壞法要有規則擋 | 論文 3.2.1 節 |」
- 引句:「而且不是已知編不過的形狀」
- 論文 3.2.1:編不過的壞法要在產生端用規則防,不是跑完才發現。
- spec 的「已知編不過的形狀」:
  - 唯一的來源是 `--stats` 累計 3 次以上,列為「表要改」候選,要人改表。
  - 沒有哪個資料結構記「已知」,一行一個壞法的篩選無從排除。
- 例:AOR 的 `a + b` → `a - b` 對字串串接必然編不過,而 Kotlin 字串 `+` 很常見。每次先挑到它就一次 `no_result`,再加一次人判,要累計到 3 次才進候選。
- 建議:候選表加「型別限制」欄(例如字串 `+` 不給 `-`),或把「已知編不過」落成表裡可讀的列。

## i12 推送前輸出整合:標題計數與尾段建議都是為計劃寫的,選擇點被擋時會誤導;列出的行數沒有上限
severity: minor
blocking: 否——判定正確,只是訊息會誤導。
- 範圍 4「擋下訊息跟預期值表缺簽合在同一次輸出」。
- 引句:「擋下訊息跟預期值表缺簽合在同一次輸出(`_spec_gate_push_bad_head` 補新標籤)」
- 引句:「訊息按排版列出(定位、成員、壞法、缺什麼、指令)」
- 查證:
  - `_spec_gate_push_bad_head` 的標題是「N 份計劃沒過」,N 是 `len(bad)`。每個選擇點一條就會算成幾百份計劃。
  - `_spec_gate_push_check` 擋下時還會印「規格閘要紅、推送閘要綠,兩頭夾住:把條款的測試做綠再推;留痕過期就重跑 lumos spec-gate <計劃>」。這對只因選擇點被擋的推送是錯的指示。
  - 全部 no_result、不唯一、過期、缺紀錄的行都要列,沒有上限。新檔一次推 300 行會印 300 條。
- file: `scripts/lumos:17373`
- file: `scripts/lumos:17425`
- 建議:選擇點那圈合成一條摘要加最多 N 行示例;`bad_head` 與尾段建議各補一個標籤分支。

## i13 帳量分析漏了版控的 kill-log;`_gate_event_fit` 也縮不了「物件」欄位
severity: minor
blocking: 否——長期成本。
- 範圍 5「帳量」。
- 引句:「實作量一筆的位元組數並保持在 `_gate_event_fit` 的上限內」
- 引句:「`test_blobs` 是物件」
- 查證:
  - `cmd_guard_kill` 每個(配方 × 測試)寫一筆 `docs/.kill-log.jsonl`,帶 `tail`(最多 200 字)與編不過、紅燈時的 `fail_excerpt`。這本帳也進版控(`git ls-files` 查得到)。
  - M×T=200 就是 200 筆。「只存雜湊」只對治理帳成立。
  - `_gate_event_fit_drop` 只會從尾端丟「清單」(`rows[:] = …`)。`test_blobs` 是 dict,超過 4096 時丟不了,對 dict 還會當掉。spec 沒指定 `list_key`。
- file: `scripts/lumos:28157`
- file: `scripts/lumos:1908`
- 建議:帳量節補 kill-log 的估算與提交方式,`test_blobs` 改成清單或限制大小。

## i14 作者側與推送閘用兩套主線判法,閘要的行集合可能比 choice-kill 跑的多
severity: minor
blocking: 否——只造成「缺紀錄」要補跑,方向不放寬。
- 範圍 1、範圍 4「範圍」。
- 引句:「範圍沒給時照人裁 `--diff` 的規則(`_codeloop_disp_range`)」
- 引句:「主線照 `_push_mainlines`(跳過被推的那條)」
- `_codeloop_disp_range` 走 `_mainline_ref`(只認 main/master 的 upstream)。`_push_mainlines` 是另一套(遠端 HEAD、遠端 main/master、多候選取最近的分岔點),註解明寫兩套並存。
- 例:本機 main 領先 origin/main 又沒設 upstream。`choice-kill` 用本機 main 算出較小範圍,閘用 origin/main 算出較大範圍 → 閘要的行 choice-kill 沒跑。
- file: `scripts/lumos:75325`
- file: `scripts/lumos:69071`

## i15 `--point` 寫回的條款會被當「人裁條款」,免預期值表
severity: minor
blocking: 否——仍要同意與 killed,是範圍外溢的副作用。
- 範圍 3「規格沒寫」。
- 引句:「事件另帶 `point` 欄(定位)與壞法身分」
- 引句:「情境題人裁的統計(`_gov_situation_spec_counts`)不算帶 `point` 欄的事件」
- `_spec_gate_ruled_events` 認 gate 與 kind 都是 `situation-rule` 的事件,比對計劃、條款編號、條款雜湊、測試名,不看 `seg`、`row`、`point`。對上的條款在 `_expected_requirement` 裡「不算新行為條款、不要求預期值表列」。
- 結果:高風險計劃的新行為條款可以走 `--point` 繞過預期值表簽核。spec 只處理統計,沒處理這條讀者。
- file: `scripts/lumos:14539`
- file: `scripts/lumos:14595`
- 建議:`_spec_gate_ruled_events` 認 `point` 事件時另判,或明寫「選擇點條款也免表」並記為決策。

## i16 論文 2.1 的「依覆蓋率挑要跑的測試」被拿掉,成本變成 壞法數 × 守的測試數,而且沒有上限
severity: minor
blocking: 否——RETIRE-IF ② 會量到,但沒有事前上限。
- 〈用詞〉殺掉判定、跟論文不同的地方 ②。
- 引句:「每個壞法對每支守的測試各一個臨時配方」
- 引句:「論文只變異有覆蓋的行」
- 論文 2.1 用行覆蓋決定每個壞法要跑的最小測試集。spec 的差異 ② 只講「不接覆蓋率」,沒講後果:每個壞法跑計劃全部守的測試,而且 r1 折入時放棄了提早停。
- 例:計劃有 15 支測試,新檔 40 個壞法 = 600 次 Gradle,論文是批次並行,`cmd_guard_kill` 是單一工作樹逐一跑。
- 回報上限只限制人要處置的存活,不限制要跑的壞法數。
- 多份進行中計劃時:殺掉判定只講單一計劃。跨計劃合併(P1 存活、P2 殺掉)沒定,S5 的「只呼叫一次」也只對單一計劃成立。
- 建議:加每次呼叫的壞法數或總時間上限,超過就分批並如實報「沒跑完」。

## i17 「無規格」擋下後,全部 `--judge` 能不能放行沒寫;可行的出口訊息也沒寫
severity: minor
blocking: 否——使用者 2026-11-13 已裁「照擋」,這裡只補出口。
- 範圍 4「判定」、S10、S14。
- 引句:「當推送範圍有選擇點但沒碰到任何進行中計劃,推送前那一道 應 擋下 reason 無規格」
- 引句:「推送前那一道 應 視那一行已處置」
- S10 說 judged 視為已處置,S14 說沒碰到計劃一律擋,兩者疊起來:一個沒有連結計劃的 hotfix 把每行都 `--judge` 了,推送還是被擋。
- 碰到的條件靠「被改程式檔的家節點被進行中計劃的 `lands_in` 或連結指到」。消費專案若沒連,會被擋「無規格」而計劃其實存在。訊息應講出這一點,出口是補連結。

## r1 折入驗收
- 到位:
  - 推送閘接線:有新旗標,主線照 `_push_mainlines`,B 取右端(但見 i6、i7)。
  - `no_result` 的出口:`--as not-applicable` 加 run_cmd 要含 `{method}`。
  - `blocked` 帶 `token`、同 B 同組 reason 不重記。
  - 帳只存雜湊(但見 i13)。
  - `_gov_situation_spec_counts` 排除帶 `point` 的事件。
  - `_situation_rule_already` 改用壞法身分判冪等。
  - 型錄讀表與 `catalog_problems` 的位置:`_MAIN_ROW_RE` 的前綴不含 `C-`、`A-`,新節放在決策表之後不會被主表讀到。
  - S19 的 attempt 算式已自洽(第一次跑 5 筆,3 killed,3/5)。
- 沒到位或折出新洞:
  - 帳提交與代碼審的先後:規則本身對,但被 i2 的重抽架空。
  - `node` 填哪份計劃:單一計劃處理了,多計劃沒有(i16)。
  - 帳量:漏 kill-log(i13)。
  - 一行一個壞法新引進 i3、i4、i8。

## 逐節核對
- 〈白話〉〈不做〉〈回退〉〈天花板〉〈依據來源〉:已讀,無 finding(論文引用的偏差見 i9、i10、i11)。
- 範圍 N、S1 到 S21 與預期值表各列的交叉引用:目標都存在、前後一致。
- 已驗證屬實的程式碼假設:
  - `_live` 是 `_spec_gate_push_scan` 的巢狀函式,要抽成頂層得多帶 `touched_plans` 參數。
  - `_KNOWN_GATES` 要加 `choice-kill`,否則 `_gate_event` 拒寫。
  - `_backing_kill_rows` 目前只跳過 `situation-rule`。
  - `LOOP_NOT_CLOSE_EVENTS` 的守衛只看 design-loop 與 code-loop。
  - `_GOV_FIELD_TYPES` 新欄位(`attempt`、清單、物件)與現有七本帳資料沒有型別衝突(實查過 `attempt`、`run_id`、`secs`、`file`、`row` 等欄位)。
  - `_nodehome_is_test` 要帶 layout 參數。

## 實務隱患鏡頭(逐類)
- 資源/耗時:i1、i16。
- 帳量:i13。
- 範圍計算與接線:i6、i7、i14。
- 與既有讀者的相容(讀帳的 gov、ruled、統計):i15;`_gov_row` 與 `_GOV_FIELD_TYPES` 無衝突,已查。
- 噪音與誤擋:i4、i10、i11、i12。
- 併發與交易:無。單人單機依序操作的聲明成立,寫帳逐筆追加,沿用既有鎖。
- 資安:無。新增的是讀 git 與寫自家帳,輸入限制在既有的測試名合法性檢查(`_test_name_ok`)內。

## 固定席節點判定
- `Systems/guard-kill` 的 INVARIANT「rc 優先序」:不影響。choice-kill 讀 `result_out` 的列,不讀 rc;`source` 參數不傳維持原行為。副作用只有批次呼叫時 stderr 會印「✗ 有配方 SURVIVED」,是雜訊。
- `Systems/guard-kill` 的 INVARIANT「`--json` 成功時 stdout 恰一行 JSON」:不影響。choice-kill 不走 `as_json`。
- `Systems/規格閘` 的 KEY:既有行為不影響。新那一圈與預期值表那圈讀的版本不同,spec 已明寫為既有天花板。見 i7 與 i15 提到的兩處需要補說明。

最嚴重:major;blocking 共 7 條
