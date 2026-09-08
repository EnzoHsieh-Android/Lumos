severity: blocker

# 審查有沒有用記帳——通才審查(r1,sonnet)

被審(凍結):`governance/review-reports/審查有沒有用記帳/r1-snapshot.md`。全份逐節挑洞,不套偏食立場。

LUMOS-SPEC: docs/lumos-toolchain-knowledge/Projects/審查有沒有用記帳_計劃.md

方法:工作樹有另一 session 未提交的改動,程式一律用 `git show HEAD:scripts/lumos`(HEAD=`ab718079a9009304058d4ef6df2b0331ae16ce23`)落地到 `/tmp/lumos_head.py` 讀,不碰髒工作樹。[S1] 的自動數演算法拿三種真實席報告格式各跑一遍(獨立 severity 行、標題內嵌、驗收輪留舊項),並直接查了今天(2026-09-08)的即時 canary 帳本 `docs/.canary-log.jsonl` 與對應席報告驗證 [S3] 的多席加總問題——不是憑空推演,底下每條都有可重跑的數字。

---

## 交叉引用核對

`[S1]`~`[S5]` 五個標籤在文件內部(`## 做什麼`小節標題)全部存在,無缺目標。已讀,無 finding。

---

## 為什麼(2026-09-08 我自己量的)

已讀,無 finding——這節是動機陳述,沒有可執行的機械宣稱。

引句:「讀側必須分開印,不可拿人工帳的數字去算機器帳的比率。」

---

## [S1] 席位列自動數「報了幾條」

### Finding 1
severity: blocker
blocking: 是——直接推翻 [S1] 用來說「不必處理標題內嵌格式」的理由,而這個格式今天真實佔比接近一半。

[S1] 主張標題內嵌寫法「早就被寫側擋」所以不用另外處理,但我在今天(2026-09-08)實際成功記帳的 `governance/review-reports/code-enforcement-obs/r1-通才.md` 裡驗證這是錯的:該報告只有第 1 行 `severity: blocker`(檔級)這一條獨立宣告行,三條真實發現全用 `## F1 — BLOCKER, blocking: 是 — …`/`## F2 — BLOCKER…`/`## F3 — MAJOR…` 標題內嵌格式,寫側 `_report_severities`(`scripts/lumos:4815`)只要求「至少一行」獨立宣告(`if not _decl: 擋下`),不要求每條 finding 各自一行,所以這份報告順利通過寫側、被記進帳(`docs/.canary-log.jsonl` 該筆 `"findings": 3`)。照 [S1] 的規則(行首 `severity:` 獨立宣告行,排除檔級)機器數這份報告會得到 `reported=0`,跟人工填的 3 差了 3 條。

引句:「嵌在標題裡的寫法早就被寫側擋(讀不到獨立 severity 行 rc2),不必另處理。」

file: `governance/review-reports/code-enforcement-obs/r1-通才.md:1,3,33,67`(全篇僅第 1 行是可被 `_report_severities` fullmatch 的獨立宣告行,F1/F2/F3 三條標題內嵌一律不匹配)
file: `docs/.canary-log.jsonl`(2026-09-08 該筆 `"auditor": "通才", "findings": 3`,無 `findings_set`,代表這是一份「單筆記帳、非載體」的席位列,`reported` 若照此算法會是 0)
file: `scripts/lumos:4847`(`_report_severities` 只要求 `if not decl:` 才擋,不逐條要求每個 finding 都有獨立行)

### Finding 2
severity: major
blocking: 是——會讓同一份報告在「寫側低報防呆」與「[S1] 自動數」兩套機制上對「這份文件到底宣告了幾個嚴重度」得出不同答案。

[S1] 的新算法要求「去列表符號與粗體」才能比對行首,這跟現有 `_report_severities`(寫側低報防呆用的唯一 parser)不做任何 marker 剝除是兩套不同實作。用 `code-clause-bindings-b/r3-架構對齊-sonnet.md` 實測:三個小節的逐條判定都寫成 `- severity: clean`/`- severity: minor`(帶 `- ` 前綴),現有 `_report_severities` 對這些行 fullmatch 全部失敗、只吃到第 1 行的檔級宣告(`severity: minor`),所以今天的低報防呆閘其實「看不見」這三行小節判定,只是剛好檔級值與小節裡的最高值一致才沒出事;[S1] 的新算法(有剝 marker)則會正確吃到第 85 行的 `- severity: minor`,跟小結「不對齊共 1 條」對上。兩套 parser 對同一份文件的「宣告了什麼」認知不一致,[S1] 沒有討論要不要統一或至少互相校驗。

引句:「去列表符號與粗體;排除 clean;排除第一行的檔級 severity」

file: `scripts/lumos:4815-4823`(`_report_severities` 的 `re.fullmatch` 不剝任何 marker)
file: `governance/review-reports/code-clause-bindings-b/r3-架構對齊-sonnet.md:27,50,85`(三行 `- severity: …` 全帶清單前綴,現有低報閘讀不到)

### Finding 3
severity: major
blocking: 是——同一句規則字面上可以有兩種讀法,其中一種讀法會對一整個真實席位家族系統性多算一條。

「排除第一行的檔級 severity」沒說清楚是「檔案的物理第 1 行」還是「文件裡第一個出現的 severity 宣告行」。用 `code-clause-bindings-b/r1-外家否決-codex.md` 實測:這份報告(Codex「外家」席固定格式)第 1 行是 HTML 註解,檔級宣告 `severity: major` 落在第 2 行——若按字面「排除第 1 行」不會排到任何東西,結果是檔級行 + 6 條 finding 行 = 7,跟人工填的 `findings: 6` 對不上(多算 1);只有讀成「排除第一個出現的宣告」才會正確排掉第 2 行、數出 6。這個格式(HTML 註解開頭)是「外家否決」這整個席位家族固定用的正規化寫法,不是單一報告的偶發格式。

引句:「排除第一行的檔級 severity」

file: `governance/review-reports/code-clause-bindings-b/r1-外家否決-codex.md:1,2,20,26,32,38,44,50`(第 1 行是註解,第 2 行才是檔級宣告)
file: `docs/.canary-log.jsonl`(該筆 `"auditor": "外家否決-codex", "findings": 6`)

---

## [S2] 載體列「駁回清單」

### Finding 4
severity: major
blocking: 是——[S3] 讀側印出的兩個數字,可信度天差地遠卻並排顯示,跟本計劃自己訂的「兩本帳分開印」精神矛盾,只是矛盾發生在同一段「機器數的帳」內部而非人工帳與機器帳之間。

`reported`(N)是從 sha256 綁定、不可事後竄改的報告檔算出來的;`refuted-set` 的 id 只是 CLI 打進去的字串,寫側完全不驗證它是否出現在 intake 或任何真實文件裡(spec 自己承認「讀側不驗,人抽查」)。[S3] 把兩者印在同一行funnel(「報 N → 存活 M / 駁回 R」)裡,卻沒有像段首固定句那樣提醒讀者:R 的可信度跟 N 不同級,一個編排者可以毫無成本地把任何理由字串塞進 `--refuted-set` 讓「駁回」數字好看,而 `gov --stats` 的讀者看不出這條數字跟旁邊的 `reported` 站在不同的可信基礎上。

引句:「★閘不驗駁回的對錯★(那是人工判斷,intake 留重現指令);這裡只讓它有 id、有理由、數得出來。」

file: `scripts/lumos:5045-5070`(`--refuted-set` 目前尚未實作,但依 `--findings-set` 現有驗證邏輯的同款寫法可推知:集合/理由格式會驗,內容真實性不會驗)

---

## [S3] 讀側:每輪一行、全庫一段

### Finding 5
severity: blocker
blocking: 是——用今天兩筆真實資料驗證,同一輪的「報」可以小於「存活」,funnel 讀起來會顯示不可能的負數駁回或倒退的存活率。

[S3] 描述的公式「報 N → 存活 M / 駁回 R」隱含 N 是 M+R 的上界(先報、去重、才知道存活跟駁回),但實測 `code-clause-bindings-b` r1 輪:三席報告的 `severity:` 獨立宣告行(排除檔級、排除 clean)分別是 架構對齊=0、單reviewer=2、外家否決=6,Σ`reported`=8;而載體(單reviewer 那筆)記的 `findings_set` 卻有 9 個 id(`i1`–`i9`)。查 `r1-intake.md` 第 29 行,`i9` 的成因寫著「我(折 i4 時測試翻紅)」——是編排者自己在修 i4 時另外踩到的,從沒被任何一席的報告書面提報過,所以它天生不在任何一份 `reported` 的分母裡;`code-enforcement-obs` r1 輪同日再現同一模式(`外家否決` 席 `findings=5`,但同一筆的 `findings_set` 有 11 個 id)。[S3] 沒有討論「載體的存活集合可以包含任何一席都沒報過的項目」這件事,會讓「報 8 → 存活 9」這種算術上不可能的行直接印出來。

引句:「報(席位總和)→ 去重後 存活(findings-set)+ 駁回(refuted-set)→ 存活裡 折(folded)/ 放行(accepted)」

file: `docs/.canary-log.jsonl`(code-clause-bindings-b loop、round=r1:三筆各自的 `findings`/`severity`,單reviewer 那筆額外帶 `findings_set: [i1..i9]`)
file: `governance/review-reports/code-clause-bindings-b/r1-intake.md:29`(`i9 自踩:像清單的判定拿整行判,「…詳見 [S2]」被判像清單 | 我(折 i4 時測試翻紅) | cg-p 紅 | HIT`)
file: `docs/.canary-log.jsonl`(code-enforcement-obs loop、round=r1:外家否決筆 `"findings": 5, "findings_set": [11 個 id]`)

### Finding 6
severity: minor
blocking: 否——只是排版位置的可讀性顧慮,不影響任何機械判定或數字正確性。

`_render_gov_stats` 現有結構是「逐主題各印一段」(`finding_kinds`/`refute_verdicts` 各自一段),新的「審查有沒有用」段落照這個既有 pattern 加一段結構上做得到,不是 [S3] 需要擔心的機械可行性問題;唯一要注意的是要放在既有段落之後、且照既有慣例維持「只算有標欄位的輪數」的措辭,避免讀者誤以為涵蓋全庫。

引句:「有 `reported` 的輪數、Σ報/Σ存活/Σ駁回/Σ折/Σ放行、逃逸帳筆數與最重等級」

file: `scripts/lumos:4345-4420`(`_render_gov_stats` 現有 `finding_kinds`/`refute_verdicts` 兩段各自獨立 print block,新段落可比照插入)

---

## [S4] 逃逸的當下就記

design-loop skill 步驟 10 目前只是「過了之後列合約候選」的自問清單,不是逃逸提醒的自然落點,但這是可讀性瑕疵不是功能缺陷——加一句提醒不會跟現有內容衝突,只是稍微混雜了兩件不同的事。

### Finding 7
severity: minor
blocking: 否——純粹是 SOP 段落的主題純度問題,不影響任何機械行為。

design-loop SKILL.md 步驟 10 現在的主題是「自問哪些行為算合約候選」,跟「下游抓到可歸因的設計期漏洞去記逃逸帳」是兩件時間點不同、動作不同的事(前者是主動盤點,後者是被動記錄),硬塞進同一步會讓步驟 10 讀起來像兩份清單黏在一起,不如仿照 code-loop 現行做法——獨立成步驟 10 之後的一段散文(如 code-loop skill 第 8 步後的獨立段落)。

引句:「design-loop skill 步驟 10 補同一句(設計審放行後、實作階段抓到的設計期漏洞也是逃逸)」

file: `skills/lumos-design-loop/SKILL.md:39`(現有步驟 10 全文只講合約候選,無逃逸相關字樣)
file: `skills/lumos-code-loop/SKILL.md:31`(對照組:code-loop 把逃逸提醒放在步驟 8 之後的獨立段落,不混進任何編號步驟)

---

## [S5] 範圍刀

已讀,無 finding——範圍刀本身自洽(不新開帳本、不回填、不做模型、不改處置閘判定、不動 `--findings` 語意),跟程式碼現況(`cmd_canary`/`_render_gov_stats` 都是在既有結構上加欄位/加段落)一致,沒有發現暗中擴大範圍的跡象。

引句:「不新開帳本(全部加在既有 canary 列與 gov --stats 上)」

---

## [S1] 與既有機制的額外交互(不屬任一 [S] 小節,但直接影響「照這份做會不會做出錯的帳」)

### Finding 8
severity: major
blocking: 是——round-less 迴圈結構性地離不開需要 `--findings` 的舊閘,[S1] 的敘事等於在鼓勵這批迴圈的操作者省略一個實際上仍是硬性門檻的欄位。

[S1] 說「既有 `--findings` 語意不動,新讀側只用 `reported`」,但 `cmd_loop_status --light` 與 `--gate`(未帶 `--panel`)兩條路的收斂判定目前仍是 fail-closed 依賴 `--findings`:`--light` 若 `findings is None` 直接判「欄位互證矛盾」FAIL(`scripts/lumos:6775-6777`);`--gate` 的 G2 步驟若 tail-K 窗內任一輪缺 `findings` 直接印「tail-K 有輪缺 findings 欄位(fail-closed)」(`scripts/lumos:6850-6854`)。而 `--disposal`(新 SOP 首選)的 carrier 驗證強制要求 `--round`+`--auditor`,round-less 的舊制 `--light`/序列式迴圈永遠無法滿足這個前提、永遠遷不到 `--disposal`,只能繼續依賴 `--light`/`--gate`——換句話說,round-less 迴圈是「永久卡在需要 `--findings` 的舊閘上」的一群,不是過渡期問題。[S1] 沒有提醒這一點,兩份 skill 的記帳範本目前雖然還留著 `--findings <存活條數>`,但 [S1] 的措辭本身容易被將來的操作者讀成「這欄可以不填了」。

引句:「既有 `--findings` 語意不動(歷史帳不回溯),新讀側只用 `reported`。」

file: `scripts/lumos:6775-6777`(`--light`:`if f is None or (sev == "clean" and f != 0) or (sev == "minor" and f < 1): fails.append(...)`)
file: `scripts/lumos:6850-6854`(`--gate` G2:`elif any(f is None for f in fs): g2_fail = "tail-K 有輪缺 findings 欄位(fail-closed…)"`)
file: `scripts/lumos:4989-4991`(disposal carrier 驗證:`if loop and findings_set is not None and not (round_id and auditor): 擋下`,round-less 迴圈天生無法帶 `findings_set`)

---

## 實務隱患(逐類風險鏡頭)

### 併發(兩個 session 同時記同一輪)
Carrier(帶 `findings_set` 那筆)的互斥檢查(`len(carriers) > 1` 擋)是讀時才驗、寫時不鎖檔,這是既有 `.canary-log.jsonl` append-only 架構就有的既有風險,[S1]/[S2] 沒有讓它變得更糟(`reported` 是每筆各自算、不搶同一把鎖;`--refuted-set` 沿用跟 `findings_set` 同一筆 carrier,繼承既有風險而非新增)。真正的問題不是風險本身,是計劃自己標的「併發/效能」小節其實沒答到併發,見下方 Finding 9。

### Finding 9
severity: minor
blocking: 否——這是既有機制早就有的風險,[S1]/[S2] 沒有加重它,只是計劃自己聲稱這節「答過」併發但其實只答了效能。

計劃「實務隱患」節把「併發/效能」合寫成一條,但整條內容只講讀側多掃一次帳本的效能成本,完全沒提兩個 session 同時搶當同一輪 carrier 的寫入競態(這在既有 `_jsonl_append_verified` append-only 模式下確實可能發生,但由 `_loop_status_disposal` 讀時的 `len(carriers) > 1` 檢查 fail-closed 兜底,不是靜默出錯)。這是文件完整性瑕疵(標題涵蓋兩類、內文只答一類),不是新增的功能風險。

引句:「讀側多掃一次 canary 帳(1216 筆、約 1 MB),`gov --stats` 已經在讀它,不另開檔。」

file: `scripts/lumos:5280-5296`(disposal 讀側 `carriers = [r for r in latest if "findings_set" in r]; if len(carriers) > 1: 擋下`——併發雙寫的既有兜底)

### 效能
無新增風險——`_render_gov_stats` 已經在讀同一份 `.canary-log.jsonl` 做 `finding_kinds`/`refute_verdicts` 等段落,新段落是同一次讀取上多幾個累加器,不是新開檔案或新掃描回合。

### 歷史帳相容(2026-09-09 前的列缺欄位)
無新增風險——`reported` 缺值印「報 ?」是明寫的規則,且 `_SEV_ORDER`/`_report_severities` 現有邏輯本來就不認 `resolved` 這個值(fullmatch 只認 `clean|minor|major|blocker`),所以歷史帳裡不會有 `severity: resolved` 污染既有低報防呆的判定,新舊規則在這一點上不衝突。

### 回滾

### Finding 10
severity: minor
blocking: 否——影響範圍限於一段觀測性統計的準確度,不影響任何會擋人的閘,且跟本專案帳本 append-only、不回溯改寫的既有哲學一致。

`.canary-log.jsonl` 是只進不出的帳本,一旦 [S1] 的自動數演算法上線後被發現有系統性錯誤(例如 Finding 3 的「排除第一行」歧義、或 Finding 1 的標題內嵌盲區),已經寫進帳的 `reported` 值無法回頭訂正,唯一補救是往後手動 `--reported` 覆蓋——而 REVISIT 抽查排在 2026-10-08(整整一個月後),這段期間累積的 `reported` 若真的系統性錯誤,會在 `gov --stats` 裡安靜錯一個月才被抓到。計劃有寫「REVISIT 抽查」但沒寫「抓到之後怎麼處理已經寫壞的那批」,不過鑑於這段本來就標「觀測、不進任何閘」,壞在觀測層而非放行層,不構成 blocking 等級的風險。

引句:「REVISIT:2026-10-08 拿一個月的席報告抽 20 份人工對一次自動數」

---

## 圖譜鏡頭(hook 附加節點,逐條判)

- `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md`:此節點宣稱的核心合約是「預設 `lumos loop status` 的 tail-K 收斂只看 `kind`+`severity`,缺 `severity` 視同未收斂」(見該節點 KEY:「缺 severity 視同未收斂」)。這份設計完全不動 `severity` 欄位語意、不動預設(無 `--gate`/`--light`/`--panel`/`--disposal`)路徑,對此節點宣稱的行為**不構成破壞**。但本報告 Finding 8 指出的 `--light`/`--gate` 對 `--findings` 的 fail-closed 依賴是這個節點的**衍生**機制(M1包擴充),不在此節點原始合約文字內,故該節點本身仍算「未受影響」,風險記在 Finding 8。
- `docs/lumos-toolchain-knowledge/Issues/流程自產工作量未量測.md`:此節點關注 `--finding-kind`(code/spec/process 三分類)佔比量測。這份設計五個 [S] 小節都沒有觸碰 `finding_kinds` 欄位或其讀側迴圈(`scripts/lumos:4390-4396`),**不影響**此節點宣稱的量測機制。

---

## 總結

最嚴重 severity:blocker(Finding 1、Finding 5)。blocking 條數:6(Finding 1、2、3、4、5、8 為 blocking:是;Finding 6、7、9、10 為 blocking:否,共 10 條 finding)。
