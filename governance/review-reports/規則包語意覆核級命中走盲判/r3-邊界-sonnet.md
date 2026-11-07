severity: major

審查範圍:r3-snapshot.md 全文逐節讀完,對照 `scripts/lumos` 與 `configs/ast-grep/kotlin-android/` 查證。本環境沒裝 ast-grep,所以 SARIF 的實際輸出沒跑,只讀程式。固定席結論:這份設計不會破壞四個落點節點宣稱的既有行為。表態閘讀側是逐題迭代,不認得的題號會被略過;治理帳的 `blind-judge` 事件缺 `role` 欄時,`_kt_bj_event_ok` 照樣略過。但下面 F1、F2、F3 三條會讓本案自己的條款落不了地。

## F1 治理帳存不下規則 id 與程式片段,統計與誤報樣本匯出做不出來
severity: major
blocking: 是(統計與匯出照現行寫法無法實作)
範圍 3 的答案形狀、範圍 4 的結果檔,以及範圍 5 和 6 的資料來源。
- 答案是 `hits: [{seg, answer, reason, issue?}]`,抽查結果是 `rule_hits: [{seg, verdict, reason}]`,兩者都沒有規則 id,也沒有檔名或程式片段。
- `seg` 是規則、檔名、片段的 sha256 前 16 碼,反推不回規則。
- 範圍 6 要「每條規則列」筆數,範圍 5 要把 `<規則 id>/review-fp-<seg>.kt` 的內容寫成「抽查材料裡那幾段程式」。這兩樣都得從治理帳取資料,但帳裡沒有。
- 要做只能回到舊版本重跑 ast-grep,spec 沒寫。
- 另一個接線缺口:`gov --stats` 讀的是 `_gov_row`,它對欄位做白名單,不認得 `rule_hits`,新欄會被丟掉。spec 沒列這處要改。
- 同一個函式的去重 token 對 `blind-judge` 事件用 `written_at`。spec 沒要求新事件帶 `written_at`,沒帶就退回 HEAD 提交時間,同一個 HEAD 上的多次抽查會被折成一筆。
引句:「從治理帳的表態紀錄與抽查紀錄算;同一分支只取最後一筆表態,避免一個分支推多次被數多次。每條規則列:作者答 fp 幾筆、答 risk 幾筆」
file: `scripts/lumos:17602` `_gov_row` 只透傳白名單欄位,沒有 `rule_hits`。

## F2 逾時、工具沒裝、參數太長的處理與既有函式不符,S10 的「工具沒裝要擋」做不到
severity: major
blocking: 是
範圍 2、條款 S10、預期值表。
- spec 說 `_kt_rule_hits` 呼叫的 `_lint_new_run_cmds` 會「抽兩份快照、只回新增」。實際它只跑命令,回 `(base_claims, head_claims)`。
- 抽快照在 `_lint_new_extract`,支援檔在 `_lint_new_support`,差集在 `_lint_new_diff_claims`,大檔與逗號路徑處理在 `_lint_new_oversize` 和 `_lint_new_sep_split`。這些編排得由 `_kt_rule_hits` 自己重寫,spec 沒說。
- 這支函式也不丟例外。失敗都記進 `out["undone"]`,分三類:`env`、`too-long`、`budget`。
- `_lint_new_classify` 把「工具沒裝/逾時/拉不到規則」全歸成同一類 `env`,結果是自動放行(fail-open)。`too-long` 和 `budget` 才是擋。
- spec 的處理方式剛好反過來:
  - 把「參數太長」歸進逾時 fail-open,既有閘是擋。
  - 工具沒裝要「無法驗證、擋」,既有閘是 fail-open。
  - `run_one` 對工具沒裝與逾時都回同一個 `"env"`,分不開,S10 那兩列預期值沒法同時成立。
- 另外,超過預算先走的是 `per_cmd_floor_sec` 的 `budget` 類,不是逾時。
- spec 說「照表態閘既有規則」,可是表態閘的既有規則是 `_KtSitOverBudget` 或 `_KtSitUnverifiable` 例外,與新增告警閘的分類是兩套。
引句:「超過時間預算(含參數太長、命令沒跑完)丟 `_KtSitOverBudget` 同型的例外,算不出來(工具沒裝、git 失敗)丟無法驗證。」
file: `scripts/lumos:42405` `_lint_new_classify` 把 env 類(含工具沒裝)判自動放行。
file: `scripts/lumos:42664` `_lint_new_run_cmds` 只回兩側 claims,失敗寫進 `out`,不丟例外。

## F3 「把 `--config` 參數換成同目錄的 review/hints 設定」沒定義怎麼認、怎麼換
severity: major
blocking: 是
範圍 1。
- 既有宣告的實際形狀是整串 shell 字串,例如 `ast-grep scan --config $HOME/harness/.../sgconfig.yml --format sarif {LINT_FILES} > {LINT_SARIF_OUT}`。這裡面:
  - 路徑帶未展開的 `$HOME`,不展開就算不出「同目錄」。
  - spec 沒說要不要認 `~`、相對路徑、單雙引號包住的路徑、`--config=路徑`、`-c`。
  - 同一條命令出現兩次 `--config`,或帶 `--filter`、`--rule` 等別的參數時,哪個算數也沒定義。
- `.lumos/lint.json` 有多條指到 `sgconfig.yml` 的命令時,每條都換兩次,身分相同的命中會重複進清單。
- `linter精選目錄` 現行寫法是:要用提示級就另加一條命令直接指向 `sgconfig-hints.yml`。照舊寫法接過的專案,命令直接指 review 或 hints,新增告警閘會逐筆擋、不給 `fp` 出口。本題又因為「只認 `sgconfig.yml`」而不適用。
- spec 範圍 7 只改範本那句話,沒說已接過的專案怎麼遷移。
- 預期值表 S1 沒有任何一列涵蓋路徑寫法或多命令。
引句:「專案的 `.lumos/lint.json` 某條命令的 `--config` 指到規則包的 `sgconfig.yml` 時,命中題就用同一條命令、把那個參數換成同目錄的 `sgconfig-review.yml` 與 `sgconfig-hints.yml` 各跑一次。」
file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:195`、`:198` 現行範本用 `$HOME/...sgconfig.yml`,並叫人另加一條指向 hints 的宣告。

## F4 同身分多筆新增命中與「每筆都要有答案」互相打架
severity: minor
blocking: 否(答法有歧義,不是會擋錯的缺口)
範圍 2、3 與用詞「規則命中」。
- `_lint_new_diff_claims` 算的是出現次數,同一個身分新增 N 次就回 N 筆,但每筆的 `key` 相同,也就是 spec 的 `seg`。
- 命中清單因此有重複 seg,答案卻是 `{seg, answer}` 一個 seg 一筆。「每筆都要有答案」沒說重複 seg 要答一次還是 N 次。
- `--carry` 帶過同 seg 的舊答案時,新複製貼上出來的同片段,會被舊答案自動蓋過。spec 只在天花板 2 籠統提到身分只看命中行,沒提這個放大。
引句:「同檔同片段多處共用一個身分。」
file: `scripts/lumos:42244` `_lint_new_diff_claims` 對同 key 回多筆 claim。

## F5 候選門檻沒有抽查樣本數下限
severity: minor
blocking: 否
範圍 6、S8。
- 「改形狀候選」要答過至少 20 筆、fp 佔八成以上、抽查判 false 至少九成。三條都過才列,但「九成」的分母沒有下限。
- 20 筆裡 fp 16 筆、只抽查 1 筆且判 false(100%),就會被列為改形狀候選。
- 預期值表只有「抽查 10 筆 9 筆」那一列,沒有抽查筆數很少的邊界列。
- 「升擋候選」門檻是 fp 少於一成,不看抽查。20 筆全答 risk 也會升擋,不過 risk 的語意是接受風險,這點 spec 沒討論。
引句:「答過至少 20 筆、fp 佔八成以上、而且抽查判 false 至少九成 → 列「改形狀候選」」

## F6 抽查材料的 40 行上限與 S4 對不上,截斷規則也沒定義
severity: minor
blocking: 否
範圍 4、條款 S4。
- 範圍 4 寫「命中處前後各 8 行…每段最多 40 行」。S4 和預期值表只寫「前後 8 行、一筆超過 5 處只給 5 處」,漏了 40 行上限。
- 覆核規則很多是「某個 lambda 裡缺了 X」,這種規則的命中範圍本身就是整個 lambda(例如 `suspendCancellableCoroutine { $$$ }`)。命中範圍超過約 24 行時,「前後各 8 行」就超過 40。
- 超過時截哪裡沒寫,截掉的偏偏可能就是判斷缺不缺 X 所需的證據,抽查會失準。
引句:「命中處前後各 8 行(同片段多處各給一段,一筆最多 5 處、每段最多 40 行,超過的印「另有 N 處」)」

## F7 檔名與規則 id 當輸出路徑或印給代理的內容,沒說要跳脫
severity: minor
blocking: 否
範圍 4、5。
- 抽查材料「每筆給檔名」。既有情境題的材料對檔名用 `_kill_esc` 跳脫,spec 沒說這題照辦。檔名含換行、反引號、控制字元或提示注入字樣時,會直接進代理的提示。
- `--fp-samples` 把規則 id 當目錄名,寫 `<輸出目錄>/<規則 id>/`。規則 id 來自 SARIF 的 `ruleId`,spec 沒限制含 `/`、`..` 或空字串的情形。「檔頭一行註解寫來源專案與日期」的專案名含換行時也會破壞註解。
- 由 F1,規則 id 目前也沒存在帳裡,真要匯出得重算,等於把外部字串直接拼進路徑。
引句:「各寫成 `<輸出目錄>/<規則 id>/review-fp-<seg>.kt`(內容是抽查材料裡那幾段程式,檔頭一行註解寫來源專案與日期)」

## F8 回退節宣稱舊版會略過未知題號,但寫側與 CLI 會拒絕
severity: minor
blocking: 否
〈實務隱患〉不可逆項與〈回退〉。
- 讀側(核對)是迭代題目表,不認得的題號確實略過。
- 寫側 `_dispositions_validate` 對表外題號回「不是題目表裡的 id」。退回後的舊版若被要求寫入或驗證含 `kt-rule-hits` 的表態檔,會被擋。`--carry` 帶出來的舊答案也含這題,同樣會被擋。
- spec 說「舊版不認 `kt-rule-hits` 題(未知題號照表態閘既有規則略過)」,只對讀側成立。
引句:「治理帳已寫的答案與抽查留著,舊版不認 `kt-rule-hits` 題(未知題號照表態閘既有規則略過)」
file: `scripts/lumos:72998` 表外題號寫成錯誤句。

## F9 命中題的「適用」判斷要先跑 ast-grep,也沒說伺服端 Kotlin 與 `lint_new.gate` 設定怎麼辦
severity: minor
blocking: 否
範圍 2、3 與用詞「命中題」。
- 表態閘現有題目的「適用」是便宜的觸發判斷,情境題另有 `android_only` 與平台排除。本題適用條件是「這次改動有規則命中」,意味著樣板、`pitfalls` 收集、`code-loop check` 每次都要在兩份快照上、兩份設定各跑 ast-grep(快取只擋同一範圍同一版本)。
- 規則包是 Android 專用,範圍 3 沒說伺服端 Kotlin 專案要不要出這一題,也沒說題目走不走既有的 android_only 欄。⚠ 查證未到底:我沒追完 `_STACK_QUESTION_SPECS` 對這題的過濾,只確認了情境題有該欄位。
- `lint_new.gate` 設成 `off` 或 `warn` 時,新增告警閘的行為會變,本題只說 `stack_questions.mode` 與 fail-open,沒說會不會跟著變。
引句:「只在這次改動有規則命中時適用。」
file: `scripts/lumos:38393` 情境題以 `android_only` 註冊進 `_STACK_QUESTION_SPECS`。

## 實務隱患鏡頭
- 金流:無,spec 不碰付款。
- 對外送出:無,只跑本機 ast-grep 與讀本機檔。
- 不可逆:有,治理帳只追加。F8 的回退落差,加上 F1 若不補欄位,帳裡的資料之後無法支撐統計。
- 守衛面:有,見 F2、F3。守衛面的收合規則與既有新增告警閘分類不一致。
- 資源與效能:有,見 F9。命中數極多時,材料的 30 筆上限加上每筆 5 處、40 行還算有界;算命中本身沒有「命中筆數」上限,清單與快取檔大小沒定。
- 格式壞:`.lumos/lint.json` 壞掉的處理沒寫(既有讀取器會報錯,本題沿用與否沒說)。治理帳壞行用既有 `_codeloop_ledger_events` 可以略過,只在 F1 補欄位後才有意義。

總結:最高等級為 major,blocking 共 3 條。
