severity: major

## 問一:分層與依賴方向

[S1]~[S4] 四塊全部掛在既有的單檔零依賴 CLI(`scripts/lumos`)上:寫側加在 `cmd_canary` 既有的處置帳驗證段落之後(同函式內加欄,不是新函式/新模組),讀側加在 `_loop_status_disposal` 尾端的觀測段與 `_render_gov_stats` 的新段,沒有新開帳本、沒有新指令、沒有跨檔案的新資料流。這跟本專案「全加在既有 record/stats 上,不新開帳本」的既定作法(spec [S5] 自己也這樣宣告)一致,也跟 `_loop_status_disposal` 既有的 canary 觀測尾段("觀測,不進合取")同一種掛法。[S4] 的兩個提醒點(ci-wait 收尾句、skill 步驟)只是指向既有的 `lumos loop escape` 指令,不新開機制。三問裡這一問對齊,無 finding。

severity: clean
blocking: 否
引句:「不新開帳本(全部加在既有 canary 列與 gov --stats 上)」
file: `scripts/lumos:13742`(既有 `_loop_status_disposal` 尾端「canary(觀測,不進合取)」段;[S3] 的「報→存活/駁回→折/放行」尾行沿用同一位置、同一句式,不是另開一段驗證邏輯)

## 問二:命名與錯誤處理

`--reported N` 覆蓋要帶 `--reported-note`、沒帶理由就 rc2,這跟既有 `--accept-reason` 系列「不給不寫鍵、給了就要非空理由,否則 rc2」的錯誤處理慣例(`scripts/lumos:5098-5101`)是同一套語彙,`reported_by: auto|manual` 這種「一個小封閉列舉記錄這個值是誰定的」也對得上既有 `orchestrator`(`scripts/lumos:5046-5062`)、`matched_by`/`picked_by`(`scripts/lumos:18193`、`scripts/lumos:20708`)的命名前例。這部份對齊。

唯一一處錯誤處理的嚴格度不一致在 [S2]:`--refuted-set` 在「有 `--findings-set` 卻沒帶」時預設視同 0、不擋,而同一個指令、同一個功能家族裡的手足旗標 `--folded-set`/`--accepted-set` 對「不完整」是硬擋——`FO | AC != F` 時直接 rc2(`scripts/lumos:5087-5090`),沒有「沒給就當空集合」這種寬容路。三個集合旗標(folded/accepted/refuted)概念上都是「掛在 findings-set 底下的子清單」,但只有 refuted 這一支換了驗證哲學:別支「不完整就擋」,它是「不給就當 0、不擋」。spec 自己也講了理由(擋會逼人亂填),是有意識的取捨,不是疏漏,所以不到「第二種做法」的量級,但同一組手足旗標裡驗證嚴格度不一致,值得記一筆。

severity: minor
blocking: 否
引句:「有 `--findings-set` 而沒帶 `--refuted-set` 視同 0 條駁回(不擋」
file: `scripts/lumos:5087`(`if not FO <= F or not AC <= F` 起、`FO | AC != F` 硬擋的既有寫法——同一指令內 folded/accepted 兩支子清單不完整就直接 rc2,沒有「未給視同 0」的先例)

## 問三:第二種做法

[S1] 的自動計數演算法(行首 `severity:` 掃描、去列表符號與粗體、排除 clean、排除第一行、排除 `resolved`)是在既有的「報告 severity 行怎麼讀」這件事上,重新寫一份規則,而不是沿用或擴充現有的單一實作。本專案這個位置本來就有兩份「唯一實作」的硬性規矩:一份是 `_report_severities`——docstring 明寫「★單一 parse 實作★(寫側+severity-check 共用)…禁第四份(同 `_quote_rows` 單一實作鐵則)」,而且 `cmd_canary` 寫入 `--report` 時本來就在呼叫它算 `rmax`(`scripts/lumos:5206`);另一份是 `_quote_norm`——docstring 明寫「唯一正規化…★抽取與比對共用這一份——嚴禁第二份實作★(2026-08-02 教訓:預檢與主迴圈兩份實作當場漂移)」,而「去粗體/去標記」正是它已經在做的事(`scripts/lumos:13418` 的 `s.replace("*", "").replace("`", "")`)。[S1] 沒有講「擴充 `_report_severities`」或「借 `_quote_norm` 的正規化」,而是描述了一組自己的規則(去列表符號、排除第一行、排除 clean、排除 resolved)——這正好是專案自己標註過教訓、明令禁止的那種「第三份平行實作」,寫側驗證用一份解析、讀側計數用另一份,兩份對同一份報告文字可能數出不同答案而沒人發現(`_report_severities` 目前是逐行 `fullmatch`,連列表符號都不容忍,[S1] 卻要求容忍;哪怕最終殺傷力不大,架構上就是同一件事被平行重做一次)。

severity: major
blocking: 是
引句:「去列表符號與粗體;排除 clean;排除第一行的檔級 severity;★排除值為 `resolved` 的行★」
file: `scripts/lumos:4816`(`_report_severities` docstring「★單一 parse 實作★…禁第四份」)、`scripts/lumos:13410`(`_quote_norm` docstring「唯一正規化…嚴禁第二份實作」)——[S1] 沒有指名沿用這兩份裡的任一份,而是另寫一套排除規則

連帶的是 `severity: resolved` 這個新值:它不在 `_SEV_ORDER = {"clean","minor","major","blocker"}` 這個唯一值域常數裡(`scripts/lumos:4772`),`_report_severities` 的正規也只認這四個值(`scripts/lumos:4822`)。[S1] 要讓 `resolved` 能被「排除」,前提是新的計數演算法得先認得這第五個值——等於值域被迫在 `_SEV_ORDER` 之外又長出一份。spec 沒交代這第五個值要不要、如何併回 `_SEV_ORDER` 這個單一定義來源,只說了新演算法要排除它,這是同一個「第二份實作」問題在值域層的延伸,不是獨立新增的架構問題,但值得單獨記一筆嚴重度(是否要擋帳、要不要讓既有 `--severity` CLI choices 也認得這個值,spec 沒講清楚)。

severity: minor
blocking: 否
引句:「嚴重度行寫 `severity: resolved`(不是留舊值)」
file: `scripts/lumos:4772`(`_SEV_ORDER` 只有 clean/minor/major/blocker 四值,唯一值域來源;`resolved` 不在其中)

不對齊共 3 條,其中 major 1 條
