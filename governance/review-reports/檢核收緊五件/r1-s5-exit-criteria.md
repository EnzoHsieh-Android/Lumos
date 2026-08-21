# r1-s5-exit-criteria — 退場條件可重算性 對抗審計

審查對象:`/tmp/檢核收緊五件-r1.md`(135 行)。鏡頭:表格「退場條件(寫入 `gov --stats` 可量)」逐列驗算,以及支撐五件一起立案的 Growth-test(準入三問)。逐條對照 `scripts/lumos` 現有程式碼(`_render_gov_stats`/`_KNOWN_GATES`/`cmd_gov`/`_append_governance_log`)。不重報 pre-flight(審計修正紀錄)已修的項目。

---

## Finding 1 — S1「詞表漏抓實例 ≥3 筆」無任何資料來源會產生這個數字

**severity: blocker**

引句：「詞表漏抓實例 ≥3 筆且無人補詞表 → 改為只列不擋」

「漏抓」定義上是「詞表沒抓到、但人事後發現是承認句」的事件——這件事發生時,Check A 本身**不會觸發**(命中詞表才觸發),所以它不可能被 Check A 自己記下來。通讀 S1 全段(第 39–49 行)找不到任何「回報漏抓」的介面:沒有 `lumos check-a report-miss` 之類的子命令,沒有治理帳欄位,沒有 frontmatter 鍵。第 49 行只講「`--ci` 時寫 `gate: check-a`」——這是**命中**事件的落帳,不是**未命中**事件的落帳。`_KNOWN_GATES`(scripts/lumos:2890)與 `_render_gov_stats`(scripts/lumos:2909-2936)也都只能統計「出現過的 gate 行」,沒有欄位可以承載「這裡本該出現但沒出現」的計數——這種負面事件天生就不在任何既有帳的 schema 裡。

第 134 行(未決)自己也承認「漏抓不是失敗,是退場條件裡的量測項」,但從沒說清楚**誰**、**用什麼指令**、**寫進哪個檔**去記一筆漏抓。這正是文件開頭 Growth-test 第一問所反對的那種病灶的翻版:宣稱一個可退場的量測條件,實際上工具端沒有任何管道能產生這個數字——與本案立案動機(check-s「宣稱有守衛、實際沒有」)同構,只是換了個位置重演。

**可量測的版本應該寫**:要嘛承認「漏抓」永遠是人工盤點(定期人工重讀詞表對照全庫一次,寫進某節點的 Verification,retirement 判準改成「距上次人工盤點 ≥90 天且盤點紀錄裡漏抓數 <3」),要嘛先加一個「回報漏抓」的最小記錄點(哪怕只是 `lumos set <node> checka_miss_reported true` 之類的手動旗標),否則這行退場條件目前無法被任何指令印出來。

---

## Finding 2 — S2「升級後仍被 ack 掉 ≥50%」的分子(升級事件)沒有可與 ack 事件對齊的落帳欄位

**severity: major**

引句：「反之若升級後仍被 ack 掉 ≥50% → 門檻 20 調整或承認某道軟提醒該整個退場」

S2 全文(第 51–58 行)只明確講了 ack 事件的落帳(第 57 行:「ack 寫治理帳 `gate: ratchet-ack`」),但**沒有講升級事件本身要不要落帳、用什麼 gate 名**。測試 15(第 115 行)列出要加進 `_KNOWN_GATES` 的三個新 gate 是「`check-a`/`ratchet-ack`/`external-absent`」——沒有第四個「ratchet」或「ratchet-promoted」。這代表升級事件如果真的走既有硬檢查框架(`run_doctor` 收集 `gov_events` → `--ci` 時 `_append_governance_log`,見 scripts/lumos:421-440、1327),它多半會沿用**原 gate 名**(例如 check-s)、只是 `kind` 換成類似 `check-j` 的 `"blocked"/hard=True` 寫法(參照 scripts/lumos:1298-1303 check-j 的落帳方式)。

問題是 `_render_gov_stats`(scripts/lumos:2909-2936)的聚合邏輯只 `agg.setdefault(r["gate"], …)` 依 **gate** 分組,完全不看 `kind`,輸出欄位是「去重後筆數/原始行數/不同 nodes 值數/不同 commit 數/首見日/末見日」——沒有任何一欄能把「這道 gate 底下有幾筆是被促升的硬事件、幾筆是原本的軟 warned」分開。也就是說,就算升級事件真的落了帳,只要它沿用原 gate 名,在 `gov --stats` 畫面上會被原 gate 的軟提醒行數吃掉、無法單獨數出「這輪一共升級了幾個 (gate,node)」這個分子;而如果它改用一個**沒被列進 `_KNOWN_GATES`** 的新 gate 名,則連出現在統計表裡都不保證(未收錄的 gate 名不影響「未出現清單」判定,但也沒有測試釘住它一定會被統計到)。兩條路都通不到「`gov --stats` 可量」。

**可量測的版本應該寫**:明講升級事件落帳用獨立 gate(例如 `gate: ratchet`),同步加進 `_KNOWN_GATES`,並在 `_render_gov_stats` 或另一個彙整邏輯裡對 `ratchet` 與 `ratchet-ack` 兩個 gate 的「不同 (gate,node) 數」做交集比對,才談得上「≥50%」這個比例怎麼算出來。

---

## Finding 3 — S3「連續 10 個 high loop 皆有外家」/「連續 5 個 high loop 靠 waived 過」不是 `gov --stats` 能印的東西

**severity: major**

引句：「連續 10 個 high loop 皆有外家 → 維持(它有用);若連續 5 個 high loop 靠 waived 過 → 外家管道根本不穩,問題在管道不在閘,攤人」

`cmd_gov`(scripts/lumos:2957 起)的資料源是寫死的七個檔:`.bypass-log.jsonl`/`.rot-queue.jsonl`/`.governance-log.jsonl`/`.signoff-log.jsonl`/`.kill-log.jsonl`/`.canary-log.jsonl`/CI 帳(scripts/lumos:2987-3021)。這七個 `load()` 呼叫裡**沒有一個**讀 `governance/review-reports/<loop>/rN-dispatch*.json`——而 S3 自己第 62 行寫「輸入:既有 `governance/review-reports/<loop>/rN-dispatch*.json` + 既有 `_roster_family()`」,這是 dispatch manifest,不在 `cmd_gov` 的七源清單裡,S3 的設計範圍(第 60-67 行)也完全沒有提到要替 `cmd_gov`/`_render_gov_stats` 新開一個 loader 去讀它。

換句話說:S3 只改 `cmd_loop_status`(loop 執行時當場擋)與 `loop next`(印 streak),兩者都是**執行當下**的即時判斷,不寫成可回頭統計「過去 10 個 high loop 各自有沒有外家」的帳本結構——要驗這個退場條件,得自己寫一支腳本去遍歷 `governance/review-reports/**/rN-dispatch*.json`,按 loop 分組、按時間排序、抓 kind=code∧tier=high 的最後兩輪、檢查有沒有 external family,這完全是 `gov --stats` 之外的工具。表頭寫「寫入 gov --stats 可量」,但 S3 自己交付的東西完全不落在 `gov --stats` 能讀到的七源裡。

waived 那一半更弱:第 65 行講豁免是「人明示 `canary record ... --note` 含 `external-waived:<理由>`」——這串文字進的是 `.canary-log.jsonl` 的 `note` 自由文字欄,`cmd_gov` 的 canary mapper(scripts/lumos:3009-3016)把 note 併進 `detail` 字串,`_render_gov_stats` 對 `detail` 完全不解析、不計數,只算筆數/節點數/commit 數。要數「連續 5 個 high loop 靠 waived 過」得對 `detail` 做子字串比對再手動分組,不是 `gov --stats` 現有任何一欄印得出來的數字。

**可量測的版本應該寫**:要嘛把「本輪外家出席 y/n」與「本輪是否 waived」在 loop 收尾時額外落一筆 `gate: external-seat`/`gate: external-waived` 的治理帳(仿 S1 的 check-a 落帳法),讓 `cmd_gov` 能讀到;要嘛承認這條退場條件走的是「人工遍歷 dispatch manifest」而不是 `gov --stats`,改表頭措辭。

---

## Finding 4 — S4「累積 10 案後比例 <10%」的比例是 `loop status` 印的,不是 `gov --stats` 印的;且 `gov --stats` 也不加總 findings/doc 數值

**severity: major**

引句：「累積 10 案後比例 <10% → 欄位退場(流程自產量不值得追)」

S4 自己第 71 行寫得很明白:比例是 **`loop status` 各模式輸出末尾加一行**印出來的,不是 `gov --stats`。`loop status` 是單一 loop 的視角(per-loop 輸出),要湊到「累積 10 案」的全域比例,得跨多個 loop 各自跑一次 `loop status` 再自己加總——`gov --stats` 完全沒被賦予這個角色。

即便退一步問「`gov --stats` 本身能不能做這個加總」,答案也是不能:canary mapper(scripts/lumos:3009-3016)雖然把 `findings`/`severity` 帶進了列的 dict,但 `_render_gov_stats`(scripts/lumos:2916-2925)的聚合迴圈只累加 `raw`/`ded`/`nodes`/`commits`/`dates` 這五個桶,從未讀取、加總過 `r["findings"]` 或未來會加的 `doc` 值。`--findings-doc` 是全新欄位,S4 的設計範圍(第 68-72 行)只碰 `canary record` 與 `loop status` 兩個入口,沒有任何一句話提到要修 `_render_gov_stats` 去加總這個新欄位。所以「S4 比例可由 `gov --stats` 讀出」在程式碼層面是假的:今天不行,S4 交付完也不行。

**可量測的版本應該寫**:表頭若要保「寫入 gov --stats 可量」的統一敘事,S4 就該同步替 `_render_gov_stats` 加一組 findings/doc 加總欄(仿 S5 新增欄位的做法);否則就承認 S4 的比例走 `loop status`,退場判準改成「`loop status` 逐輪印出的比例累積 10 筆後由人手動加總」。

---

## Finding 5 — 表頭「寫入 gov --stats 可量」對五件不是統一事實,S5 自己的列已經先自我推翻

**severity: major**

引句：「退場條件(寫入 gov --stats 可量)」

這是整張表的欄位標題,等於對五件做了一次性宣稱:每一列的退場條件都能從 `gov --stats` 讀出來。但表格自己最後一列(S5)寫「純數字,無退場問題;隨 --stats 走」——連退場條件都沒有,不需要也不存在「可量」這件事;而如 Finding 2–4 所證,S2/S3/S4 的分子或比例來源實際上都不落在 `gov --stats` 現有(或 S1-S5 交付後會有)的資料結構裡。一個對五列統一適用的表頭,實際上只對 S1 成立(check-a 落帳完整、且 90 天窗零命中可用既有「未出現清單」機制驗出,見 scripts/lumos:2946)。這種「幫全表掛一個共同保證,實際只有 1/5 兌現」的寫法,正是本案自己在 Growth-test 裡點名要防的「宣稱有守衛、實際沒有」模式,發生在退場條件表自己身上。

**可量測的版本應該寫**:表頭拆開,逐列各自標「可由 gov --stats 讀出」或「需額外工具/人工彙整」,不要用一個統一括號覆蓋五種實際上不同的可驗證程度。

---

## Finding 6 — S1 退場起點「存量 38 處補標後算起」與同文件內已修正的數字矛盾,退場條件表未同步更新

**severity: minor**

引句：「上線 90 天內 `check-a` 在 `--ci` 零新命中(存量 38 處補標後算起)→ 退場候選」

第 47 行(S1 本體、審計修正紀錄已處理過的段落)已經把「38」標成不可靠、改口徑:「★數量以詞表實掃為準:pre-flight 實測依詞表 28~51 行不等,「38」是 08-21 手數的近似,不再引用★」——`審計修正紀錄` 第 129 行第②點也明講「存量 38 處無法重現(依詞表 28~51),改以實掃為準」。但退場條件表(第 93 行)完全沒跟進這次修正,仍然把「90 天倒數的起點」錨在同一個被自己文件宣告失效的「38」上。這不是新洞(pre-flight 已抓到 38 這個數字有問題),而是**修正沒有散布到文件內第二個引用處**——退場條件表這一列本身沒被 pre-flight 覆蓋到。

**可量測的版本應該寫**:「上線 90 天內 `check-a` 在 `--ci` 零新命中(以上線當日 `lumos lint --scan-only`/等效指令實掃到的命中數為準,不引用任何手數近似值)→ 退場候選」。

---

## Finding 7 —「不再預設軟提醒、不擋」與 S4/S5 明標「不擋」正面衝突

**severity: major**

引句：「不再預設「軟提醒、不擋」——那個預設就是寬鬆的來源。」

這是全案的立案宣言,緊接在「三件硬擋、兩件只給數字」之後,語意是「本案拒絕再走「軟提醒、不擋」這條老路,因為那正是本輪七張自我批判單的病灶共因」。但 S4 標題自己寫「(**資料,不擋**)」(第 68 行),S5 標題自己寫「(**數字,不擋**)」(第 74 行)——五件裡有兩件、剛好 40%,是明文設計成不擋的資料/數字輸出,與 check-s 當初「響了一萬八千多次沒人處理」的軟提醒在**行為上同構**:都是「印出來,不影響任何 gate 結果,期待人自己看」。文件沒有解釋為什麼 S4/S5 的「不擋」跟被本案拿來當立案動機的 check-s 軟提醒不是同一種風險,只是換了名字(「資料」「數字」而非「提醒」)。如果理由是「S4/S5 不是要人採取行動的提醒,只是可退場判斷用的原始數字」,這個區分文件裡沒寫出來,讀者只能看到表面矛盾:宣稱不再預設軟提醒不擋,同一份設計裡又把五分之二的件明標不擋。

**可量測的版本應該寫**:在立案宣言後面加一句判準,說明「軟提醒、不擋」被拒絕的具體定義是「要求人採取行動但沒人會看」,而 S4/S5 屬於「不要求任何行動、僅供其他判斷讀取的原始數字」——並解釋這條界線為什麼不會重蹈 check-s 覆轍(例如:S4/S5 有沒有一個一定會被讀到的下游消費者,像是被 S1-S3 的退場判準引用,而不是像 check-s 一樣只印在 console 上等人主動看)。目前文件沒有這句話。

---

## Finding 8 — Growth-test「真事故」只點名四個事件,對應 S1-S3;S4/S5 沒有獨立事故背書,靠捆綁搭便車;且四個事件裡至少一個是已被自己專案的 A/B/C 判準歸類為「量測缺口」而非「已發生損害」的事件

**severity: major**

引句：「共同形態=**宣稱有守衛、實際沒有**,這是正確性問題。」

準入三問第 1 問(第 29 行)列的四個事故是①check-s 空轉(對應 S2 棘輪)②外家席缺席(對應 S3)③probe 三參數/pass --note(不對應 S1-S5 任何一件——這個事故已經在 `Issues/寫下風險當成處理風險.md` 被歸類為「B→降級」並靠改散文措辭解決,見該節點第 67 行「skill 散文「須」改「建議(工具不驗)」」,不需要新機制)④Check N 存量零使用(對應 S1)。frontmatter 的 `related` 清單另外掛了 `Issues/流程自產工作量未量測`(S4 的立案依據,第 72 行有引用)與 `Issues/只退場不痛的機制`(全案總帽子),但這兩張單子都**不在**準入三問列的①-④事故清單裡——S4、S5 兩件在 Growth-test 的「真事故」回答裡完全沒有各自的事故引用,是靠與 S1-S3 綁在同一個「三問」段落、共用同一句「有,且本週密集」的結論搭便車過關的。這正是使用者要對抗的「捆綁五件在同一個 design-loop 裡,會不會讓單一薄弱件搭前面強件的順風車」的具體實例:S4/S5 沒有被單獨過一次 Growth test 第 1 問。

另外,四個事故裡①②④(check-s/外家/Check N)在 `Issues/寫下風險當成處理風險.md` 自己建立的 A/B/C 判準裡,②外家與④Check N 明確歸類為「B 型:可機械但未做」而非「已造成損害」(該節點第 67-70 行的分類表);①check-s 的 Issue 節點自己承認「判準本身是合理的,問題從來不在判準,在沒有回看路徑」(`Issues/自足性審計提醒空轉四十六天.md` 第 49 行)——也就是說,已發生的是「量測動作被跳過/沒人看」,不是「因為沒守住而產生了錯誤結果」。把這些歸類為 Q1「真事故」的「有」,混淆了「已證實有害的事件」與「已知的量測缺口」,而後者正是 Growth-test 第 1 問原本要排除、對應到第 2 問「風格偏好」該擋下的東西的鄰居類別——本案沒有交代為什麼「量測缺口」在這裡算「真事故」而不是需要更謹慎處理的灰色地帶。

**可量測的版本應該寫**:Growth-test 第 1 問拆成五次獨立回答,S4 引用 `流程自產工作量未量測`、S5 明講「本件無事故支撐,是觀測性基礎設施,豁免 Q1」;並在四個既有事故的敘述裡區分「已發生的錯誤結果」與「已知但未處理的量測缺口」,只有前者才算「真事故」。

---

## 嚴重度統計

blocker: 1, major: 6, minor: 1
