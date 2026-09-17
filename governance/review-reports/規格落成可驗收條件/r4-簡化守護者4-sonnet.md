severity: blocker

# 規格落成可驗收條件_計劃 r4 審查報告(外部審稿人／panel:簡單的守護者、複雜的敵人)

## 逐節閱讀記錄

**frontmatter / decisions(d1–d12)、PRIOR-ART / RETIRE-IF**:已讀,無 finding。d1–d12 的 supersede 鏈可回溯、每個 valid:false 都有對應 superseded_by,內部一致。

**為什麼(數字表)**:已讀,無新 finding(既有數字已被 r1–r3 三輪重數訂正,見下方 F5/F8 對這批數字用途的延伸質疑)。

**兩層要分開**:已讀,無 finding。規格書/條款分層邊界清楚,翻譯範例具體。

---

## Findings

### F1(panel①:三層條款數清點)

逐條分類 S1–S34(S14 併入 S2,共 33 條):**直接守原題**(門判定+句式+雙向門跑條款+推門閘,S1/S2/S3/S4/S5/S6/S16/S21/S30)= **9 條**;**守機制**(防作弊/基建支撐,如 keeps 防繞過、run_cmd 鎖單支、紅的判準嚴謹化、留痕可歸責,S7/S8/S15/S17/S23/S24/S25/S26/S27/S32)= **10 條**;**守機制的機制**(逃逸帳量測本身及其精度/去重/健檢/規則版本/讀側相容/節邊界定義,S9/S10/S11/S12/S13/S18/S19/S20/S22/S28/S29/S31/S33/S34)= **14 條**。三層合計 33 條吻合。結論:守原題本身只占 27%,守機制的機制占 42%,panel 疑慮(從一條文法長到多層防線)有機械依據。

引句:「驗收條款一律寫成能直接變成測試的句式並綁上測試;做錯能退回的計劃(雙向門)不派人審、只讓機器跑條款」

severity: major
blocking: 否(判準:這是結構透明度問題,不是機制缺陷,不阻擋落地,但應該把這個比例寫進誠實界線讓後人一眼看到)

### F2(panel②:先不開放雙向門能砍掉什麼)

若第一階段只做「條款文法+綁定+跑紅」半套、全部計劃當單向門(即不啟用雙向門放行路徑),可整套砍掉:keeps 三層防線(S6 的「至少一條未標 keeps」語意、S7、S25)、節邊界定義(S29)、已排除行掃描與其反例(S16/S23)、door_rule 版本(S33)、留痕條款指紋與過期判斷(S15 的排除理由/測試名部分、S24)、讀側白名單相容(S28)、推送閘讀留痕全綠(S21/S30/S31)。粗估可砍 S6(部分)/S7/S16/S23/S24/S25/S28/S29/S31/S33 共約 10 條,原題只剩「文法+綁定+跑紅」(S3/S4/S5/S8/S17/S27/S32 等)。逃逸自動記(S9–S13/S18–S20/S22)本來就與雙向門開關無關,不受影響。

引句:「三層(每條紅/至少一條未標 keeps/既存性)各防不同攻擊面,不合併」

severity: major
blocking: 否(這是可執行的落地順序建議,不是必須先做才能安全的東西——spec 自己「上線順序寫死」段落已經隱含類似分期,但沒有把「先不開放雙向門能省掉哪些條款」講清楚,建議補一句)

### F3(panel③:逃逸自動記與規格閘本體應否拆開)

回退節自己承認「逃逸自動記保留(它本來就該有,與退場無關)」——這句話直接證明兩者是可獨立成立的東西。但整份 RETIRE-IF 與第六節退場條件全部繫在「雙向門逃逸率」上,逃逸自動記本身沒有獨立的 RETIRE-IF(它不會因為自己失準而被撤除,只會因為「歸因啟發式對回率低於五成」而被重做,這條掛在 RETIRE-IF ③,仍然是規格閘框架下的條件而不是逃逸自動記自己的)。拆開後,逃逸自動記可以有自己更簡單的驗收標準(對回率、fail-open 可見性),規格閘本體則保留「30 份雙向門」的統計驗收——目前綁一起讓兩者的 RETIRE-IF 互相稀釋。

引句:「逃逸自動記保留(它本來就該有,與退場無關)」

severity: major
blocking: 否(不影響正確性,是治理清晰度建議;現況已用同一份 lands_in/RETIRE-IF 運作,拆開是重構級別的整理,不必卡在這版落地)

### F4(panel④:承重牆多久才能第一次承重)

spec 已在誠實界線自陳「在 30 份雙向門計劃跑完之前不得宣稱有效」,對 panel 這個疑慮是誠實揭露而非隱瞞,不構成隱藏缺陷。唯一缺的是:沒有給任何「30 份大概要多久」的估算(每週實際會有幾份計劃落在雙向門)——第六節「這三個數字是拍的」也承認同一件事,但沒有把「距離第一次真正承重要多久」這個問題本身寫成待答。撤除條件①(單一 blocker 逃逸立刻退回)其實提供即時的下限保護,不是完全空窗,但這點 spec 沒有明講,讀者容易誤以為整段空窗期毫無防護。

引句:「在 30 份雙向門計劃跑完之前不得宣稱有效」

severity: minor
blocking: 否(已誠實揭露,不隱瞞;建議補一句說明①號撤除條件在空窗期就已經是即時防護,不必等 30 份)

### F5(panel⑤:審查帳本身是反例——「每條都有編排者機械重現」與卷證不符)★

誠實界線用「每條都有編排者機械重現當外部回饋,不是純散文互折」把本輪(r1–r3)的散文式折入跟「為什麼」節批評的散文收斂做出區隔。但查三輪 intake:r1「編排者重現」表只列 10 條(23 條折入中),r2 只列 7 條(30 條中),r3 只列 8 條(22 條中)——合計約 25/75(三分之一),**不是「每條」**。其餘約三分之二(如 C3 停用詞表不齊、C5/C8/C13–C22 等)是審查員純文字判斷「這段講不清楚/沒定義/漏一種情況」,沒有對應的 grep/git/code 重現紀錄。這正是本篇自己在「為什麼」節批評的「散文互折」形態,誠實界線的區隔論證因此不成立(至少對三分之二的折入無效)。

引句:「且每條都有編排者機械重現當外部回饋,不是純散文互折」

severity: major
blocking: 是(判準:這句話是誠實界線用來回應「本迴圈是不是自己的反例」這個核心張力的關鍵論證,現在有verifiable反例,若不修正會誤導讀者以為 r1–r3 的折入品質有機械保證,而多數其實沒有——這是精度優先的文件裡不該留的事實誤述)

### F6(keeps 既存性檢查依賴使用者自填的 created 欄位,可被繞過)★同族缺陷第三次出現

第三節 keeps 既存性檢查(S25)寫「取測試檔在 `created` 日期之前的最後一次提交」——這裡的 `created` 是計劃筆記開頭欄位裡使用者自填的日期,程式沒有鎖它(`grep "created.*不准改\|immutable"` 全 repo 零命中),也沒有拿計劃檔自己在 git 歷史裡第一次出現的日期做交叉驗證。作者只要把 `created` 改早(用 `lumos set` 這個「開頭欄位用指令改」的合法路徑),就能把 keeps 既存性檢查的判準窗口往前挪,讓任何早於「真正動筆日」但晚於「造假 created 日」的樁測試通過既存性檢查——這正好繞過了 r3 才剛堵上的「git log -S pickaxe 可用舊名繞過」那個洞(C2),是同一種攻擊面(偽造「這支測試比計劃早」)的第三種形狀:①軟提醒沒人做(d3 舊理由)→②pickaxe 不驗路徑/不驗至今存活(r2→r3 已堵)→③現在改看 `created`,但 `created` 本身無鎖。本專案自己的經驗(同族缺陷修兩輪沒乾淨要換形狀)在這裡適用:這是同一族的第三次出現,不該只補丁,要嘛把 `created` 鎖成第一次寫入後不可改(需要新的欄位保護機制),要嘛改用計劃檔自己在 git 歷史裡第一次出現的 commit 時間而非使用者自填欄位。

引句:「取測試檔在 created 日期之前的最後一次提交」

severity: blocker
blocking: 是(判準:這是整套雙向門「不派人審」安全模型裡,唯一防止「先埋樁測試再回頭標 keeps」的機械閘,若可被自填欄位繞過,S25 形同虛設,而 S25 正是 r3 專門為了堵前一版漏洞新開的條款——不修就是把三輪之前堵過的洞重新打開)

### F7(「紅」的支數解析只覆蓋 Python,未沿用既有多棧 `_RAN_EVIDENCE` 基礎設施)

第四節「紅」的判準寫「解析測試工具輸出裡的支數(unittest 的 `Ran N test(s)`、pytest 的 `N failed / N passed` 相加)」,這是全新、只認 Python 測試輸出格式的解析器。本 repo 既有 `_RAN_EVIDENCE`(scripts/lumos:~25700 附近)已經為 java/csharp-xunit/node-jest/python 等至少 5 種技術棧各自維護實測過的輸出樣式正則,是本專案近期投入(Java/Kotlin/Swift/Dart/C#/Flutter 補棧)刻意做的多棧基礎設施。spec-gate 的支數解析完全獨立於這套機制,對非 Python 消費專案(`test_profile` 不是 python)會因為抓不到 `Ran N test(s)`/`N passed` 樣式,永遠落入「N==0 弱證據,擋下」,等於這些技術棧的消費專案完全用不了雙向門放行路徑,而殘餘段只揭露 `-k` 子字串撞名(Python 特有問題),沒有揭露這個更根本的多棧覆蓋率缺口。

引句:「解析測試工具輸出裡的支數(unittest 的 `Ran N test(s)`、pytest 的 `N failed / N passed` 相加)」

severity: major
blocking: 是(判準:本 repo 自己是 Python 專案,這版落地不會立刻出錯;但本專案的 lumos 是要 vendored 分發給多棧消費專案的工具鏈,依 CLAUDE.md 鐵則四「承認風險要附回頭看的條件」,這種未揭露的範圍限制必須至少寫一條 REVISIT 或在殘餘段明說,否則會重演本專案已記錄過的「消費專案接入靜默失效」同型坑)

### F8(d9「34/538 稀疏」統計只算計劃自身標籤,未涵蓋規則②的連結節點訊號population)

第一節硬單向門規則②(連到帶 `★IRREVERSIBLE★`/`★CHECKPOINT★` 合約行或**掛任何 `risk/` 標籤**的節點)是獨立於規則①(關鍵字表命中)的訊號來源,判定範圍是「計劃連到的節點」,不限於四類。但整份文件唯一拿出來當「稀疏、集中在守衛面,所以預設要翻成單向」證據的 34/538 統計,量法寫死為「只認開頭欄位 `---` 區塊裡的 `- risk/<值>` 行」——這只數了計劃**自己的**標籤,沒有數規則②會額外命中多少份(連到任何掛 risk/ 標籤節點的計劃)。方向上這不會造成安全風險(規則②命中越多,越多計劃會被判單向門,是更保守的方向),但用來支撐「稀疏所以要翻預設」這個論證的數字並沒有覆蓋到規則②真正的判定範圍,論證本身有缺口。

引句:「計劃連到的節點(`related`、`lands_in`、正文 `[[連結]]`)帶 `★IRREVERSIBLE★` 或 `★CHECKPOINT★` 合約行,或掛任何 `risk/` 標籤」

severity: minor
blocking: 否(判準:方向是保守/安全的,不影響機制正確性,只是統計論證不夠嚴謹;不必卡落地,寫一句「34/538 只算規則①母體,規則②另外命中的量沒算」即可)

---

## 固定席節點逐條判(是否破壞其宣稱的行為/合約)

- **Systems/design-loop ★INVARIANT★**(處置閘第五步語意):不影響。spec 明文要求新共用檢查器 `_clause_check(plan, door=one-way)` 呼叫時必須維持「懸空只提醒不擋」既有語意(r3 C11 已折入、並改寫草稿文字強制此點),且 `_disposal_clause_step` 現況本就是懸空只印提醒不擋(file: `scripts/lumos:15800`),spec 沒有要改這條。
- **Systems/bound-tests-gate ★INVARIANT★**:不影響。spec 在 r3 已自我訂正,明文放棄借用 `_ran_evidence_check`(該支只證「有跑過」不數支數),另開新的支數解析器,不動 bound-tests-gate 本體(file: `scripts/lumos:25726` 註解自述其邊界)。
- **Issues/code-loop守衛main-direct盲區**:不影響,反而主動避開——spec 明文要求推送閘範圍「沿用 pre-push 現有的 push-range 計算、不得自算 merge-base」,正是對該事故的預防性對齊。
- **Systems/anchor-integrity ★RISK★**:不影響。scripts/lumos、scripts/hooks/pre-push 是既有錨點檔,落地時 `lumos anchor verify` 會自動翻紅要求 `anchor approve`(既有機制,已在本計劃「進度」段對逃逸自動記那次改動走過一次同樣流程),spec-gate 落地時同一機制會再次機械觸發,不需要本計劃額外交代。
- **Systems/每支檔有家**:不影響。scripts/lumos、scripts/hooks/pre-push 是既有檔案,已有多篇既有 Systems 節點(design-loop、bound-tests-gate、anchor-integrity 等)在 about_code 列它們為家,本計劃只是新增行為,不是新建檔案,不觸發「每支檔有家」的新開義務;lands_in 新開 `Systems/規格閘` 管的是本計劃新增的 `cmd_spec_gate`/`_clause_check`/`_excluded_line` 等新函式,範圍界定清楚。
- **Systems/lumos-cli-read ★INVARIANT★**(search 排除 stale/superseded):不影響,本案未觸碰 `cmd_search` 邏輯。
- **Systems/lumos-cli-lifecycle ★INVARIANT★**(re-inject sentinel 外 byte-equal):不影響。要動什麼表裡「設計 spec 寫完…」那行(CLAUDE.md:62)位於 `LUMOS:GRAPH-DISCIPLINE:START/END` sentinel 區塊內(file: `CLAUDE.md:2,66`),spec 也正確要求透過 `lumos update` 重新注入而非手改,走的正是 sentinel 內允許覆寫的路徑,不違反此不變量。
- **Systems/canary-audit ★INVARIANT★**(record/second 落盤可讀回;second 純 telemetry 不影響 gate rc):不影響。`kind` 列舉新增 `spec-gate` 是加值不改路徑,寫入/讀回機制沒變,也沒有觸碰 `cmd_canary_second` 的判定邏輯(file: `scripts/lumos:6251` 起的 `cmd_canary_second` 未被本計劃列入「要動什麼」)。

---

## 總結

最嚴重 severity:**blocker**(F6)。
blocking 計數:**3 條**(F5、F6、F7)。
