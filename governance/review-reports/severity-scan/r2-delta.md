# 審查報告:嚴重度綁定機械掃 r2(delta 席,折入回歸鏡頭)

sha256 已核對 = e23fade6...8a5。已讀 r2 快照全文+r1 五席報告+r1 原 spec,並對照 scripts/lumos 寫側/閘/quote-check 機構與 repo 真實報告帳。

### d-f1
severity: blocker
引句:「收貨轉錄時要把表頭型正規化成獨立行(與引句正規化同一步驟)。」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:23`
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:28`
佐證:file: `governance/review-reports/severity-scan/r1-s2.md:8`
佐證:file: `governance/review-reports/severity-scan/r1-s3.md:5`
說明:全庫 grep「收貨轉錄/正規化表頭」零命中——這個把「### id / 等級 / 標題」表頭轉成獨立「severity: X」行的正規化步驟,不存在於程式碼裡任何地方,不是「既有步驟」。而 [S1] 條款本身講的是「讀報告檔...parse 全部嚴格整行」——直接讀原始檔案,完全沒提到任何前置轉換。用實測驗證後果:同一輪(r1)五席裡,`r1-s2.md`(s2-f1/s2-f2 兩條標題行)、`r1-s3.md`(s3-f1~f4 四條標題行)全篇對嚴格整行 pattern 是零匹配(grep 已跑過,兩份都是零命中)——這不是只有 ext/codex 才有的問題,是這個審查制度本身今天就在用、佔五席中兩席的格式。生效日後如果原樣照字面實作,任何人想把 `r1-s2.md` 這種格式的報告用 --report 記進帳,第一次就會被 rc2 擋下,而且沒有任何機制能讓它通過——因為聲稱能救它的正規化步驟根本不存在。這推翻了修正紀錄裡「s1-f1+s2-f1 已折入」的宣稱:現況事實段落改寫了,但條款本文(真正決定行為的地方)沒有對應機制,折入是假的。

### d-f2
severity: blocker
引句:「報告無 severity 行→拒帳 rc2」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:36`
佐證:file: `governance/review-reports/code-delguard/r3-s2.md:4`
佐證:file: `docs/.canary-log.jsonl:397`
佐證:file: `governance/review-reports/about-code-field/r1-veto-codex.md:1`
說明:這個 repo 現有的報告慣例是「逐條 finding 標 severity」,零 finding 的「乾淨輪」報告天生沒有任何一行需要寫等級宣告——`docs/.canary-log.jsonl:397` 記著 `code-delguard/r3-s2.md` 帳面 `"severity": "clean"`,但該報告全文唯一沾到 severity 字樣的是「max severity: blocker(剔除後 clean)」這種散文夾註(講的是剔除 canary 干擾前的原始最高值,不是最終判定,而且格式本來就不符行首錨定),`about-code-field/r1-veto-codex.md` 更是全篇純散文、連一個「severity」字樣都沒有。[S1] 的「且至少 parse 到一行」是無條件的:不管帳面填的是不是誠實的 clean,只要報告裡一行都比對不到就直接 rc2。這代表往後任何一份誠實的「什麼都沒抓到」報告,只要沿用這個 repo 今天就在用的散文/夾註慣例,寫的人就會被擋在門外——逼著大家為了通過機械檢查,去報告裡硬塞一行本來沒有意義的「severity: clean」樣板文字。這不是逃逸口,是把「沒東西可宣告」和「刻意隱瞞」用同一把尺量,擋掉本來就合法、且是歷史上真實發生過的記帳。

### d-f3
severity: major
引句:「凡帶 --report 的新帳列」
佐證:file: `scripts/lumos:15463`
佐證:file: `scripts/lumos:15493`
佐證:file: `scripts/lumos:3679-3704`
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:40`
說明:`--severity`(15463)和 `--report`(15493)是兩個獨立的選填 argparse 參數,沒有任何 required 或互相綁定的檢查——`canary record ... --severity major`(不帶 --report)完全合法。[S1] 自己講的觸發條件就是「凡帶 --report 的新帳列」,所以只要呼叫時不附 --report,[S1] 整段驗證邏輯根本不會被叫到。現有唯一會強制附 --report/--snapshot 的機制是 T6 定錨(3679-3704),但它只在「該 loop 帳面已有任一筆帶 findings_set 的記錄」之後才生效——也就是說每個 loop 的第一輪(carrier 尚未寫入 findings_set 之前),所有個別席位的 severity 記錄都還沒被定錨,可以完全不附 --report、完全繞過 [S1]。這正是這個方案最想守住的時刻(第一輪原始 finding 進帳),卻是保護最弱的時刻。r2-snapshot.md:40 明文宣稱「r1 外家 ext-f4 指的循環盲點因此不成立於新案」,但實際上 ext-f4 講的「advisory 抓到才升級,升級條件本身觸發不了」那個循環空窗,只是換了一個新的入口重現:低報者(或單純疏忽的人)只要不帶 --report,S1 就形同不存在,只剩下和 r1 舊案一模一樣的「掃描器抓到才轉述、轉述不動 rc」那條路。修正紀錄裡「ext-f4 → 循環空窗不存在」的結論站不住。

### d-f4
severity: major
引句:「報告 minor+帳 major(高報)→拒帳 rc2(不等就擋,方向不豁免)」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:36`
佐證:file: `governance/review-reports/severity-scan/r1-s1.md:26`
佐證:file: `scripts/lumos:10217`
佐證:file: `scripts/lumos:10219-10220`
說明:r1-s1.md 自己的「掃過但乾淨的面」已經用 repo 裡三個真正消費 severity 欄位的閘(disposal 的 accepted/folded 合取、panel 存活合取、light ratchet)逐一核過:「高報無法反過來造出假綠的那種假面(它頂多是逼出不必要的折疊,不是逃避折疊)」——這個結論在 r2 沒有被推翻,也沒有被討論,卻被 [S1] 直接用「不等就擋,方向不豁免」全盤反向處理,把高報和低報用同一把 rc2 硬擋。更矛盾的是下游邏輯本身站在「高報更安全」這一邊:`scripts/lumos:10217`/`10219` 的規則是「輪內任何一席 severity 是 blocker/major,accepted 集合就必須清空」——帳面記得越高,下游判定越嚴、越保守。這代表一個審查員如果基於額外脈絡想要保守地把帳面記高一點,現在會被硬性擋下——除非回頭去竄改已經凍結、已經算過 sha 的報告檔本身,讓報告文字跟帳面「配平」。這件事本身就是 ext-f2 已經點名要避免的「報告與帳同出一人之手、可被同步調整」風險模式,矛盾的是同一份文件在 40 行講「不擋共謀,只擋疏忽」,卻在 36 行的 fixture 逼著誠實的保守記帳者去做「調整報告以配合帳面」這個和共謀同一形狀的動作。

### d-f5
severity: minor
引句:「ts 在生效日前的舊帳不溯及」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:28`
佐證:file: `scripts/lumos:3492`
說明:這句被放在 [S1](寫側、record 呼叫當下執行)的描述裡,但寫側每次執行時,新記錄的 ts 一定是 now(),不可能小於「生效日」——`canary record` 沒有任何 --ts 之類的覆寫參數(3492 行寫死,無法從 CLI 傳入過去時間)。所以這句話對 [S1] 自己的執行路徑而言是一個永遠不會為真的死條件;它真正有意義的地方其實是 [S2](讀取歷史 jsonl、需要用 ts 分辨新舊帳)。把這句話寫在 [S1] 底下,會讓實作者誤以為 [S1] 本身需要一段「檢查 ts 是否早於生效日」的分支邏輯——這段邏輯要嘛是永遠不觸發的死碼,要嘛(更危險)逼著實作者加一個 --ts/--backdate 之類的覆寫欄位「讓」這個豁免生效,一旦真的加上去,就等於替 [S1] 開了一個時間戳造假就能繞過驗證的後門。目前尚未發生,列 minor,但這是條款把兩層(寫側/讀側)的生效日邊界混寫在一起造成的概念混淆,值得在動手實作前先分清楚寫給哪一層。

## 掃過但乾淨的面
- s1-f2/s2-f2(引句/blockquote 逃逸)確實被字面規則堵住:行首錨定要求整行從行首就是標籤,「引句」開頭行(不管單行還是分離成兩行)、> 開頭的 blockquote 續行,都不可能匹配——邏輯上兩型逃逸確實被排除,不需要額外啟發式。條款文字和實作意圖一致。
- arch-f2(值序第四份複製)折入是真的:條款明文「值序抽模組常數 _SEV_ORDER(既有三處字面複製回填,不開第四份)」,對照 `scripts/lumos:3911`/`4100`/`15463` 現存三處各自內嵌的定義,這條指令具體可執行,不是空話。
- arch-f3(孤兒檔)折入是真的:grep 只命中 `scripts/lumos:10311` 這一個寫入點,條款明講「不開新檔,寫進既有 roster-alerts.log 加 kind」,與現有 kinds 逗號串接多標籤格式相容,可行。
- arch-f4(sha 重複驗)折入是真的:條款「被 disposal 尾端呼叫時信合取③已驗過(旗標跳過)」,對照 disposal ③ 留痕重驗段(`scripts/lumos:10226-10262`)確實已對同一批 report_path 逐一重算過 sha256,新增旗標跳過重算的設計方向正確。
- s3-f2(回頭條件散文化)折入是真的且機械可查:有日期、有檔案、有門檻,和 roster 前例的回頭條件同等機械化。
- s3-f4(免責字樣)折入是真的:現有 canary 觀測段(`scripts/lumos:10291-10293`)已用「(觀測,不進合取)」同款措辭打過先例,新 tail 沿用是可執行的具體指令。
- ext-f2(誠實邊界)折入誠實、沒有過度宣稱:明講「不擋有意共謀,對抗性造假歸既有 [audit:] 獨立審計層」,劃清了 [S1] 只防疏忽轉錄錯的邊界。
