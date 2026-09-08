severity: blocker

# r1 簡化守護者(sonnet)——審查有沒有用記帳_計劃

立場:每個新欄位/新段落預設不需要,要今天的證據,不接受「以後可能用到」。

## 為什麼(2026-09-08 我自己量的)

已讀,無 finding。機械覆核:`docs/.canary-log.jsonl` 總筆數 1216、`refute_verdicts` 欄位非空 0 筆,與宣稱一致。

引句:「兩個現成欄位一次都沒人填**:`--refute-verdict`(辯方表態)1216 筆裡 0 筆」

## [S1] 席位列自動數「報了幾條」

### finding 1
severity: blocker
blocking: 是
判準:自動數演算法用現行、正在使用的 code-loop 報告格式實測會數到 0,直接推翻「不靠人填」這個★標記的核心賣點。

spec 段落:[S1]

引句:「機器數報告裡行首 `severity: minor|major|blocker` 的行數(去列表符號與粗體;排除 clean;排除第一行的檔級 severity;★排除值為 `resolved` 的行★)」

問題:code-loop 報告的官方單一來源(`templates.md` 第 38 行只要求「每條標 severity」,未規定語法)在實務上多用 `- [major]` 這種列表前綴標嚴重度,不是獨立行 `severity: <值>`。今天(2026-09-08)進行中、尚未提交的 `code-batch13` 六席報告裡,四席各只有 1 行檔級 `severity:` 宣告 + 8~9 行 `- [major|minor|clean]` 格式的逐條標記——若照 [S1] 描述的演算法逐行掃「獨立行 severity: <值>」,扣掉那 1 行檔級宣告後,這四席全部會算出 `reported = 0`,即使每份都明確報了 4~9 條發現。這比計劃自己前掃抓到的「今天早上 8 份算 0」還更普遍、更當下(不是舊格式,是本週仍在用的格式),而且 `--reported` 覆蓋要求逐次附理由,等於 code-loop 每一輪都得手動覆蓋,回到 `--findings` 沒人填/填不對的老路。

佐證:
- file: `governance/review-reports/審查有沒有用記帳/r1-snapshot.md:32`(演算法描述)
- file: `skills/lumos-design-loop/templates.md:38`(格式唯一來源只要求「每條標 severity」,不規定語法)
- file: `governance/review-reports/code-batch13/r1-通才.md:3,5,11,17,23,29,35,41,47,53,59`(1 行檔級 `severity: major` + 9 行 `- [major|minor|clean]`)
- file: `governance/review-reports/code-batch13/r1-併發與資源.md:3,5,11,17,23,29,35,41,47,53`(1 行檔級 + 9 行同款 bullet)、`governance/review-reports/code-batch13/r1-邊界與輸入.md:3,5,11,17,23,29,35,41,47`(1+8)、`governance/review-reports/code-batch13/r1-架構對齊.md:3,5,11,17`(1+3)——四席一致同款格式,非單一異常樣本
- file: `scripts/lumos:4822`(`_report_severities` 的 `re.fullmatch` 只認 `severity:` 開頭獨立行,不認 `- [major]` 前綴)

### finding 2
severity: minor
blocking: 否
判準:「去列表符號與粗體」這條前處理規則在計劃自己前掃的三種格式(16/18 精確符合、2/18 驗收輪殘留、8/18 標題嵌入)裡都沒有實例支撐,屬未經驗證就先寫進演算法的範圍。

spec 段落:[S1]

引句:「自動數會數錯的地方**:席報告格式不照 SOP(嚴重度寫在表格裡、寫成 `**severity**`、一條 finding 兩行 severity)」

問題:前掃報的三種失配都不是「行首有列表符號或粗體包住 severity:」這種形態(是完全嵌在標題或整行沿用舊值),finding 1 找到的第四種格式(`- [major]` bullet)也不是「加了列表符號的 `severity:` 行」而是完全不同的標記語法,去列表符號/粗體救不了它。這條規則目前像是防禦性寫碼而非證據驅動,建議寫 spec 時拿掉或換成 finding 1 揭露的真正落差。

佐證:file: `governance/review-reports/審查有沒有用記帳/r1-snapshot.md:25`(前掃三種格式的原始樣本描述)

### finding 3(確認,非問題)
severity: minor
blocking: 否
判準:審稿人原本要問「既有 `--findings` 語意改成報幾條是否更省一個欄位」——機械核對後這條路會弄壞既有 `--gate` 的 G2 收斂判準,spec 不動 `--findings` 語意是必要決定,不是保守多慮。

spec 段落:[S1]

引句:「既有 `--findings` 語意不動(歷史帳不回溯),新讀側只用 `reported`。」

問題:`--gate` 的 G2 讀 `r.get("findings")` 逐輪比對,要求 tail-K 視窗內單調不增、末輪 ≤1 且嚴格下降到 0,並且 `severity=="clean"` 時強制 `findings==0`——這套邏輯把 `findings` 當「尚存活的問題數」使用,不是「這輪報了幾條」;若把 `--findings` 改成報告總數,clean 輪只要曾報過已駁回的假陽性就會直接打穿這條互證,K-streak/G2 兩個現行收斂閘全部失真。維持 `--findings` 語意不動、另開 `reported` 是這個限制下唯一安全的做法。

佐證:file: `scripts/lumos:6849-6874`(G2 讀 `findings` 做單調遞減與 severity 互證)、`scripts/lumos:5170-5219`(`--severity`/`--report` 寫側綁定同一批欄位)

## [S2] 載體列多一組「駁回清單」

### finding 4
severity: minor
blocking: 否
判準:「id 要對得上 intake 才算數,人抽查」預設 intake 裡已有一致的 id 命名法可對,但目前實際的 intake 檔案彼此格式不一,人抽查時要先自己重建對應表,增加而非降低抽查成本。

spec 段落:[S2]

引句:「★閘不驗駁回的對錯★(那是人工判斷,intake 留重現指令);這裡只讓它有 id、有理由、數得出來。」

問題:抽驗現有 `rN-intake.md` 發現同一種「重現結果」寫法在不同輪次分別用 `F1「…」→ MISS`、`邊界 #3`、`通才 F5`、純數字編號「1./2./…」四種標法,彼此不統一、也不必然對應到 `--findings-set` 的 `f1/g1/i1` 這種 id 慣例。這個落差本身不足以阻擋開工(駁回本來就是人工判斷、不進閘),但建議在收貨 SOP 裡順手規定 intake 的重現條目 id 要沿用 `--findings-set` 同一套 id,不然「人抽查」這句承諾會比預期難兌現。

佐證:
- file: `governance/review-reports/Codex完全支援/r1-intake.md:16`(用 `F1「…」→ MISS`)
- file: `governance/review-reports/probe-retire-v2/r1-intake.md:7-8`(用 `s1`/`ext` 加編號)
- file: `governance/review-reports/code-batch13/r1-intake.md:35-41`(用純數字 1-7)
- 對照:`docs/.canary-log.jsonl`(`code-clause-bindings` 系列輪次的 `findings_set` 用 `f1..f13`/`g1..g10`/`h1..h6`)

## [S3] 讀側:每輪一行、全庫一段

已讀,兩段各自的讀者不同、資料範圍在程式碼裡本來就不共用,不是同一件事印兩遍:`--disposal` 只讀單一 `loop_id` 傳進來的 `rounds`(`scripts/lumos:13528` 的函式簽名只收一個 loop 的記錄),讀者是正在跑這條 loop、要知道這輪報/存活/折/放行有沒有兜起來的人;`gov --stats` 讀的是整個去重後的六帳(`scripts/lumos:4345` 的 `rows`/`ded` 是全庫聚合),讀者是做定期治理巡檢、要看全庫趨勢的人,兩者資料來源在架構上就不重疊,合併成一段任一邊都會少東西。

引句:「`lumos loop status <編號> --disposal` 尾端(觀測,不進合取)每輪印一行:」

### finding 5
severity: minor
blocking: 否
判準:「逃逸 E」放進「每輪一行」的格式裡暗示可以逐輪歸因,但逃逸帳的資料結構完全沒有輪次欄位,只能給出整條 loop 的累計數,spec 沒有講清楚這點會讓實作者誤以為要做輪級歸因。

spec 段落:[S3]

引句:「有 `reported` 的輪數、Σ報/Σ存活/Σ駁回/Σ折/Σ放行、逃逸帳筆數與最重等級;辯方表態那段照舊。」

問題:`cmd_loop_escape` 寫進帳的欄位只有 `{ts, token, loop, stage, severity, desc, defect_ref?}`,完全不記是哪一輪放行後才逃逸的;`--disposal` 目前的架構也只處理最新一輪(`rid, latest = next(reversed(groups.items()))`),不是逐輪印歷史表。所以「逃逸 E」實際能給的只會是「這條 loop 累計到現在的逃逸數」,跟同一行裡「報 N/存活 M」這種真正屬於該輪的數字混在一起容易誤讀成該輪專屬,建議 spec 明講是 loop 累計值。

佐證:file: `scripts/lumos:6626-6628`(逃逸帳 `rec` 建構,無 round 欄)、`scripts/lumos:13574`(`_loop_status_disposal` 只取最新一輪 `latest`,不遍歷 `groups` 歷史)

## [S4] 逃逸的當下就記:兩個提醒點

已讀。skill 現況覆核屬實:`lumos-code-loop/SKILL.md` 第 31 行已有逃逸帳提醒句,`lumos-design-loop/SKILL.md` 的步驟 10(第 39-40 行)確實還沒有同款提醒,S4 對這兩處現況的描述準確。

引句:「`lumos ci-wait` 紅燈的收尾訊息加一句:修完若可歸因到某次已放行的審查 →」

### finding 6
severity: minor
blocking: 否
判準:歷史資料顯示 `ci-wait` 紅燈路徑目前 0 次真正對應到審查逃逸,新提醒句在已知樣本上會 100% 落空,值得在 spec 裡註記這是低命中率的提醒、不是判準。

spec 段落:[S4]

問題:`docs/.ci-log.jsonl` 139 筆裡 `conclusion=="failure"` 共 12 筆,`failed_step` 全部是「Full test suite」「Anchor verify」「SyntaxWarning 歸零閘」「自主迴圈測試」「code-loop gate」這類測試/守衛紅燈,沒有一筆讀起來像「審查放行後 CI 才抓到的漏網」;而 `docs/.escape-log.jsonl` 迄今唯一一筆逃逸紀錄的 `stage` 是 `push-gate`(本地 pre-push hook),不是 `ci`,代表這條路徑歷史上從沒真正接住過一次逃逸。這不足以擋下這個提醒(成本只是一行文字、不影響 rc、不強迫填寫),但值得 spec 明講這句提醒目前命中率是 0/12,提醒讀者判斷時別被它訓練成「看到就關掉不讀」。

佐證:
- 機械統計:`docs/.ci-log.jsonl` 12 筆 `failure`,`failed_step` 值域=`{test/Full test suite, test/Anchor verify (baseline 缺失必紅), test/SyntaxWarning 歸零閘, test/自主迴圈測試, test/code-loop gate (push 後盾;體檢}`
- file: `docs/.escape-log.jsonl:1`(唯一一筆,`"stage": "push-gate"`)
- file: `scripts/lumos:17252-17253`(`ci-wait` 紅燈輸出路徑,目前無此提醒句)
- file: `skills/lumos-code-loop/SKILL.md:31`(code-loop 已有同款提醒,S4 的新增點是讓沒走 code-loop skill 流程、只單獨呼叫 `ci-wait` 的人也看得到,這點本身合理,不構成擋下的理由)

## [S5] 範圍刀

已讀,無 finding。範圍刀列的五條(不新帳本、不回填、不做統計模型/不自動調參、不改處置閘判定、不動 `--findings` 語意)跟前面逐條核對的結果一致,沒有發現實作會被迫破這五條界線。

引句:「不新開帳本(全部加在既有 canary 列與 gov --stats 上)、不回填舊卷證」

## 實務隱患

已讀,無新增 finding(第一條「自動數會數錯的地方」已併入 [S1] finding 1/2 處理,兩份 REVISIT 日期本身合理、不重複)。

引句:「REVISIT:2026-10-08 拿一個月的席報告抽 20 份人工對一次自動數」

## PRIOR-ART

已讀,無 finding。世界對照(review yield / DORA 逃逸率)與自家已有欄位(`finding_kinds`/`refute_verdicts`/逃逸帳)的裁定描述跟程式碼現況吻合,borrow-design 的框定跟這次改動範圍一致。

引句:「自家=`finding_kinds`、`refute_verdicts`、逃逸帳、`gov --stats` 各段都已存在」

## 圖譜鏡頭

已核對兩個計劃連結節點,沒有發現這份 spec 會破壞它們宣稱的行為或合約:`Systems/loop-convergence-recording` 記載的 K-streak/G2/settle/disposal 四種收斂判準都是靠既有欄位(`findings`/`severity`/`findings_set` 等)運作,這次新增的 `reported`/`refuted-set`/`reported_by` 全是選配欄、未被任何既有判準讀取(finding 3 的機械核對已確認 `--findings` 不動),不影響其收斂邏輯;`Issues/流程自產工作量未量測` 記載的 `finding_kinds` 是同一種「先開始記、REVISIT 才回看」的既有先例,這次 [S1]/[S2] 走的是同一套模式,方向一致、REVISIT 日期(2026-10-08、2026-11-08)不撞期(該節點自己排的是 2026-10-15)。

---

總結:最嚴重 severity=blocker,blocking 條數=1。
