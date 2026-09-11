severity: blocker

# 推播miss量測_計劃 r1 邊界審查(極端輸入席)

立場:逐節讀完凍結快照,對照 `governance/eval/lens-utilization/recount.py`、`scripts/hooks/claude/impact-hook.py`、`scripts/lumos` 的 `cmd_search`/`_impact_reverse_lookup`、`governance/daily-governance.sh`、`governance/autonomous-loop.sh`、`governance/eval/refresh_labels.py` 與 `retrieval-goldset.json` 實際結構,聚焦空逐字稿、零推播、多讀多推、跨週/週邊界、逐字稿寫壞、搜尋輸出截斷、檔名含空白或改名這幾類極端輸入會不會把這份設計打穿。

## frontmatter / 摘要(KEY 行)

已讀,無 finding——三條 KEY 只是概述條款,實際查證放在對應 [S1]-[S4]。

## 緣起

已讀。其中「只解析『必看』那一段,『可能相關』『直接提到這個檔』兩段沒解析」這句對現狀的描述查證屬實(`recount.py` 的 `parse_pins` 只認 `HDR_OLD`/`HDR_NEW` 兩種「必看」標頭,`break` 在找到第一個必看段之後就不再往下掃);但由此延伸出的 [S1] 有實作陷阱,見 B1。

## PRIOR-ART

已讀,無 finding——「擴充既有唯讀腳本」的定位跟實際程式碼結構一致,`recount.py` 目前確實零外部依賴。

## [S1] 推播清單解析三段都認

B1
severity: major
blocking: 是
引句:「推播清單解析三段都認」
file: `governance/eval/lens-utilization/recount.py:114`
file: `scripts/hooks/claude/impact-hook.py:650`
「必看」段每行格式是「縮排+kind標籤(可選★TAG★)+路徑」,`PIN_LINE` 正則靠那個可選 ★TAG★ 群組隔開 kind 標籤與路徑;但「可能相關的 N 篇」「另外 N 篇分數不高但直接提到這個檔」兩段的行首是**分數數字**(`0.42 直接 Systems/a.md`),沒有 ★TAG★ 群組可隔開,實測把這行餵給現有 `PIN_LINE` 會把 `"直接 Systems/a.md"` 整段(含 kind 標籤)當成路徑吃進去——不是真實節點路徑,永遠比對不到任何節點。若照最省事的做法擴充既有的「掃到下個標頭前所有縮排行」迴圈去認這兩段,S1 驗收句「三段節點都進『推了』」會直接落空,且被污染的路徑會讓這兩段裡**真的被推播**的節點在 S2 miss 判斷時被誤判成沒推,反過來製造假的 miss。`t_lens_recount_classify` 全綠不能當作這條路徑被驗過的證據,因為那支測試從沒餵過帶分數前綴的行。

## [S2] miss 偵測

B2
severity: major
blocking: 是
引句:「同一份逐字稿、那次編輯之後的高信心讀取」
file: `governance/eval/lens-utilization/recount.py:414`
現有 `scan_file`/`scan_codex_file` 的 touched 掃描對「那次編輯之後」沒有上界,是從錨點一路掃到逐字稿結尾(`for j, o2 in enumerate(objs)` 沒有在下一次 push 出現時停手)。這個設計用在既有的「pinned 有沒有被用上」二元統計上還好(binary,晚讀也算讀過),但套進 S2 逐篇分類 miss 時,一個 session 若有連續多次編輯,同一次「很晚才讀」的動作會被同時算成**每一次**前面編輯的 miss 證據——長 session(含跨週的長 session)會系統性膨脹 miss 計數,而這正是本案打算拿去餵 goldset 的核心資料,驗收清單裡只寫了單次編輯、單次讀取的情境,沒有測到多編輯疊加的窗口污染。

B3
severity: blocker
blocking: 是
引句:「沒推卻被讀的那一半直接丟掉」
file: `governance/eval/lens-utilization/recount.py:376`
file: `scripts/hooks/claude/impact-hook.py:718`
`scan_file` 只在逐字稿裡出現 `attachment.type == hook_additional_context` 時才會建立一筆 row(第 376 行的 `if not att or ...: continue`);而 `impact-hook.py` 的 `inject_additional_context`/`inject_ranked_context` 在 direct/indirect/incidents 與 results/lane/stack_questions 全空時是直接 `return`,完全不印 JSON、也不會在逐字稿裡留下任何 hook_additional_context 標記。結果是「一次編輯推了零篇」這個最極端的情境在現有資料模型裡**沒有任何 anchor 可以掛**,S2 沿用既有 touched 判法等於天生量不到這一類——而這恰好是「後者就是推播漏掉的東西」這句話裡邏輯上最純粹的那個案例,不是實作細節可以補,是整個 anchor 機制的結構性盲區。

B4
severity: minor
blocking: 否
引句:「用現在的圖譜判當時的推播」
file: `scripts/lumos:19852`
file: `scripts/lumos:19882`
承認的限制只講「筆記後補路徑」這個方向的漂移,沒講反方向:`row["file"]` 存的是編輯當下 Edit/Write 工具給的路徑字串,若那支**程式碼檔**後來被改名,`_impact_reverse_lookup` 用舊路徑做完整路徑比對(19882 行 `claim["token"] == rp`)必定落空,裸檔名容錯(19852 行起)只在檔名本身沒變、只是目錄搬動時才救得回來。真的改了檔名的情境會讓本該進「規則內」的 miss 掉進「判不出」,不是誤判成錯的桶,只是少了自動歸類的那一批,傷害小於 B1-B3。

## [S3] 搜尋零命中

B7
severity: major
blocking: 是
引句:「配對它的輸出,判零命中」
file: `governance/eval/lens-utilization/recount.py:221`
file: `scripts/lumos:3187`
現有 `classify_bash` 只解析 Bash **指令字串**本身(`search_terms.update(terms)`),整支 `recount.py` 找不到任何讀取 `tool_result`/`toolUseResult` 的程式碼——S3 要「配對它的輸出」是要新蓋一條「Bash tool_use → 對應 tool_result」的配對機制,不是重用既有東西,spec 寫得像是既有能力的延伸,實際是全新管線。另外,零命中判法鎖定的兩個模式(「共 0 篇候選」文字尾行、`--json` 的 `candidates` 欄)都只在 `ranked`(預設)分支印出;實測 `--regex` 會強制關掉 ranked(`if ranked and regex: ranked=False`),`--legacy` 與非 ranked 路徑也完全沒有 `--json` 輸出(第 3187 行印的是 `"N 處 / M 篇"`,不受 `--json` 影響),所以任何用 `--regex`/`--legacy` 查詢的零命中都會落進「判不出」而非「零命中」——spec 本身有把「兩種都對不上」的情況收進判不出,所以不會誤判,但這代表零命中計數對這兩種模式是系統性低估,而这兩種模式恰好是精確比對場景下 agent 更常用的旗標。

## [S4] 每週留存

B5
severity: major
blocking: 是
引句:「同一週重跑覆寫同一個檔」
file: `governance/eval/lens-utilization/README.md:13`
`recount.py` 全檔沒有任何一處讀取或輸出 `timestamp` 欄位(逐檔搜尋零命中),`main()` 每次執行都是把 `~/.claude/projects/*/` 底下**現存的全部**逐字稿重新掃一遍、不分是本週還是三週前的活動。S4 沒有講清楚「本週跑一次、寫進 `<年>-W<週>.json`」到底是「這週發生的事」還是「這週拍的一張全量快照」;README 第 13 行已經寫明逐字稿約 30 天滾動清除,這暗示設計意圖其實是後者(用週快照對抗 30 天視窗流失),但如果讀這批檔案的人(含 REVISIT:2026-09-17 那天讀分佈的人)把連續兩週的檔案當成互斥的週間增量來比較趨勢,會被嚴重誤導——因為兩份快照有將近 30 天的重疊視窗,不是不重疊的週切片,驗收句「同週再跑→覆寫同一份」只測了冪等,沒有測資料語意。

B6
severity: minor
blocking: 否
引句:「本週沒跑過才跑,輸出寫到」
file: `governance/autonomous-loop.sh:368`
`<年>-W<週>.json` 沒有明講「年」用日曆年還是 ISO 年;若實作用 Python `date.today().year` 搭 `isocalendar()[1]`(常見寫法),跨年最後一週/第一週會出現年份與週號對不上的錯檔名。同一支排程檔家族(`autonomous-loop.sh:368/405/423`)已經有三處用 `date +%G-W%V`(ISO 年配 ISO 週)這個正確寫法,只是 spec 沒有指名要跟進,也沒有驗收句覆蓋跨年那一週,屬於容易被抄對、但沒被明文要求的邊界。

## [S5] README 同步

已讀,無 finding——「補三段、寫明天花板」這個要求本身沒有歧義;天花板要不要涵蓋 B1-B7 這幾條是實作/收尾階段的事,不在這條款本身的語意問題。

## 邊界與不做

已讀,無 finding——「不動 impact hook、不動派工鏡頭、不改 `docs/.usage-log.jsonl`」跟 F08 既有裁定一致;「只量本 repo 的逐字稿,沿用既有 cwd 篩法」跟 `scan_file`/`repo_paths` 現行實作一致,沒有引入新的篩選邏輯。

## 承認的限制

已讀。四條裡「量不到 Bash 改檔」「零命中判法靠輸出字樣」都如實承認且方向正確,但「用現在的圖譜判當時的推播」只覆蓋了筆記側的漂移(B4 已指出反方向的程式碼檔改名沒被覆蓋),而 B2/B3 兩條(窗口無上界、零推播無 anchor)完全沒被列進這節——鐵則要求「承認風險要附回頭看的條件」,這兩條目前連「承認」這一步都還沒做到,自然也就沒有 REVISIT。

## 實務隱患

已讀,逐類過:
- 併發:寫暫存+自驗+`os.replace` 原子換名是本 repo 既有慣例(`atomic-write-shared-files` 同款做法),`refresh_labels.py` 的 `_goldset_lock`(flock)也證明這個 repo 對併發寫入有成熟解法可抄;daily-governance.sh 本身有外層 lock(`take_lock`/`finalize`)防止整支排程重疊執行,兩個週跑同時跑的情境被結構性排除,無 finding。
- 效能:掃全部逐字稿數秒到十幾秒、週跑一次的量級跟現有歷史重算腳本相同,無 finding。
- 資源:純讀檔,無 finding。
- 隱私:見 B8。
- 金流、對外送出、不可逆:不適用——純讀取加一份可重跑可刪除的報表檔,無金流/外送/不可逆操作路徑,無 finding。

B8
severity: minor
blocking: 否
引句:「只存推導列(節點名、檔名、計數、零命中查詢字串),不存原文」
file: `governance/eval/lens-utilization/recount.py:221`
同一句話裡把「零命中查詢字串」歸進「推導列」,但查詢字串是從 Bash 指令裡原樣抽出來的 token(`classify_bash` 的 `search_terms`),不是統計推導出來的數字或節點名——如果 agent 曾經搜尋帶敏感字眼的查詢(例如貼了一段業務數字去搜),那段文字會被逐字存進週檔。跟「工作階段代號存雜湊」的謹慎程度不一致,是隱私承諾內部的措辭鬆動,不是機制漏洞,故列 minor。

## 驗收

已讀。列出的四組驗收情境(三段解析、單次編輯 miss 分類、單次零命中+單次命中、週跑冪等)都只覆蓋「教科書式」的單一情境,B1(分段格式不同導致污染)、B2(多編輯窗口污染)、B3(零推播無 anchor)、B5(週檔語意)、B7(`--regex`/`--legacy` 盲區)這五條全部發生在驗收清單沒有覆蓋到的路徑上,照現有驗收句子逐字實作,測試會全綠但資料仍然是壞的。

## 總結

最嚴重 severity 是 blocker(B3);blocking 共 5 條(B1、B2、B3、B5、B7)。
