severity: major

固定席筆記逐條判斷(hook 沒有附筆記,我自己讀了這三篇):
- `Systems/存量漂移守衛`:不破壞既有行為,但有兩處要遵守。第一,該篇 WHY 寫明 m1 的判定另開一支、不放進 `_drift_check_core`,因為那支也給考試與歷史重放用。欄位判定必須照辦,spec 沒講。第二,該篇 RULE 寫 gate=off 的專案照樣跑 m1。欄位開關要是不做同樣的交代,就會重演那個意外(見 R2I7)。
- `Systems/筆記內容閘`:不破壞。否定現況句提醒由 `note_shape.negation` 管,和 `tag_hints` 是兩個開關,衝突見 R2I6。
- `Systems/lumos-cli-read` 的 ★INVARIANT★(search 預設藏作廢節點,`--json` 帶 `hidden_superseded`):現有行為不破壞,但行模式的隱藏行數沒有進 `--json`,見 R2I8。

**R2I1**
severity: major
blocking: 是——照 spec 做,擋下訊息印出的兩條指令(`drift ack`、`drift fix`)都跑不起來,使用者被擋了沒有逃生口。
1. 輸入:欄位被擋下的一筆發現。
2. 走到〈讓 AI 知道該寫什麼〉第 2 點和〈分期〉第 1 步。
3. 壞處:
   - 擋下訊息要教人用既有的 `drift ack`。但 `_DRIFT_KINDS` 只有 probe、c1 到 c5、m1 七種,`drift ack --kind` 的 argparse `choices` 和 `_drift_ack_args_err` 都以它為準,不在裡面的種類直接 rc2。
   - 新種類也沒進 `_DRIFT_KIND_NAMES`,印發現和表態確認訊息時會 KeyError。
   - `_drift_fix_hint` 對不認得的種類會落到 `return [base]`,印出 `lumos drift fix … --kind <新種類>`,但 `_DRIFT_FIX_KINDS` 只收 c1 到 c5。
   - 分期第 1 步只寫「發現種類記進治理帳」,沒列新種類要加進這四處。
引句:「與 `drift ack`(既有)的指令」
佐證:`scripts/lumos:27554`、`scripts/lumos:28861`、`scripts/lumos:40602`、`scripts/lumos:29072`、`scripts/lumos:27557`

**R2I2**
severity: major
blocking: 是——spec 自己有兩條互相矛盾的判定範圍。S4 照字面實作要看新寫欄位,候選篩選卻只看「改到目標檔」的欄位。
1. 欄位表的表頭說只看「這次改到 `路徑` 那支檔」的欄位。
2. 同一表格的數量與值那一列又說「這次新寫的欄位在終點就不吻合 → 擋」,S4 也綁了這條。
3. 一個新寫、寫錯數字、目標檔這次沒動的欄位,不在候選裡,S4 的測試過不了。
4. 另一個缺口是「起點 N」到底取哪個版本的筆記:
   - 如果取 base 的筆記,同一次推送把程式 4 改 5、又把欄位 `=4` 改成 `=6`(寫錯),終點不吻合,但算不算「新寫」沒定義。
   - 如果取終點的筆記,起點必然不吻合,就被當舊帳放行。
   - 既有的條件式回頭條件有「同一條」的比對規則(`_drift_probe_judge` 的 `old` 參數);欄位沒有對應定義。
引句:「這次新寫的欄位在終點就不吻合 → 擋(寫錯了)」
佐證:`scripts/lumos:28630`、`scripts/lumos:28556`

**R2I3**
severity: major
blocking: 是——S6 要求含 `::` 的名稱(例 Rust 的 `Client::connect`)照「帶副檔名的路徑之後」切,但 spec 宣稱沿用的判定切法不同。
1. 錨點求值寫「沿用回頭條件探針的符號判定」。
2. 探針用 `_drift_cond_split`,是 `v.rsplit("::", 1)`。我實跑:`src/x.rs::Client::connect` 切成 `('src/x.rs::Client', 'connect')`。
3. 路徑 `src/x.rs::Client` 不在樹上,`tree.one` 回 False,起點和終點都 False,於是永遠不擋。這條錨點會靜默失效。
4. `_drift_cond_split` 是探針判定、預讀、候選篩選、判不了點名四處共用的(註解寫明代碼審 r5 專為此合併),改它會連帶動回頭條件。spec 沒承認要改,也沒說另寫一支。
5. 「名稱還在」的語意也比 spec 暗示的弱:非 Python 檔的 `_defines` 只要名稱以單字形式出現在檔案任何位置(含註解、字串)就算在。函式刪了、註解還提到它,錨點不會擋。
6. 這點要寫進〈天花板〉第 5 條。
引句:「沿用回頭條件探針的符號判定(同一支 `_DriftProbeTree`」
佐證:`scripts/lumos:28241`、`scripts/lumos:28379`、`scripts/lumos:28392`

**R2I4**
severity: major
blocking: 是——「抽成共用函式」從現有程式碼抽不出來,起點求值方式 spec 沒交代。
1. 輸入:HTML 數量標記 `<!--lumos:count=N re=… in=…-->`。
2. doctor N 段目前是在工作目錄用 `os.walk(repo_root)` 掃磁碟,有 4000 檔、40MB 的上限,超過就當標記本身有問題的提醒。
3. 存量漂移檢查要在起點和終點兩個提交各算一次。這得從 git 樹批次讀出所有符合 `in=` 的檔,對 `**/*.cs` 這種 glob 是整個 repo 的 blob 讀兩遍。
4. 所以這不是搬動程式碼,而是要新寫一支吃「檔案來源」的函式。spec 只講抽出來、受總預算管。
5. 還有三處沒講清楚:
   - 掃描量超過上限時,doctor 現在只提醒,漂移檢查「判不了」依既有慣例卻是要處理(block 模式擋推送)。spec 寫「判不了:照既有處理,不另訂」,沒說這種情況算哪邊。
   - 預算:`_drift_check_c` 把 60 秒給 core 加 probe,m1 另有 30 秒。欄位判定掛哪一個預算沒講,吃 core 的會擠壓 probe。
   - 標記放在行內程式碼裡,doctor N 現在照常評估(註解寫「保留 inline code」)。〈欄位 v1〉的「寫在哪裡才算」寫行內程式碼不評估。同一個標記在兩個檢查裡的規則不同,而 S7 要求兩邊共用同一函式。
引句:「抽成共用函式,存量漂移檢查也呼叫它」
佐證:`scripts/lumos:3040`、`scripts/lumos:3017`、`scripts/lumos:27565`

**R2I5**
severity: major
blocking: 是——W1 的觸發條件「程式符號」和 W2 的「寫死數量」沒有判準,S10、S11 寫不出確定的測試,實作可能吵到被關掉。
1. W1 寫「用反引號提到程式符號」。現有反引號裡什麼都有:路徑、指令、設定鍵、環境變數。
2. spec 沒說用什麼判定符號,也沒說拿什麼比對(例如名稱在樹上存在)。
3. 這份 spec 自己的 WHY 摘要行就滿是 `drift_check.fields`、`note_shape.tag_hints` 這類反引號。照最寬鬆的實作,提交它自己就會觸發 W1。
4. 這個專案處理同類提醒的慣例,是先給字眼表並用量測程式釘死準度。否定現況句提醒的字眼表就釘在 `_NS_NEG_NARROW_ZH` 並有逐字測試。W1、W2 都沒有。
5. W2 的「只有/唯一/恰好 N/N 個/N支」既不是字眼表也不是正則。「3 個月」「兩個」之類會被當成寫死數量。
6. 分期第 2 步也沒有準度量測的安排。
引句:「新寫的 WHY、RULE、PITFALL 行用反引號提到程式符號,又沒帶任何依賴欄位 → 提醒」
佐證:`scripts/lumos:25374`、`scripts/lumos:25570`

**R2I6**
severity: major
blocking: 是——同一個提醒有兩個開關,又有一條提醒在它的開關存在之前就上線。
1. W3 是「沿用既有的否定現況句提醒」。那個提醒由 `note_shape.negation` 管(`_note_shape_negation_parse`)。
2. S14 卻要求 `tag_hints` 是 off 時 W1 到 W6 都不出現。W3 要嘛是同一個提醒印兩次,要嘛 S14 的測試過不了。
3. W4 在第 0 步就要上線,「讓既有提醒送得到」,但 `note_shape.tag_hints` 要到第 2 步才出現。
4. 〈實務隱患·相容〉卻寫「W4 在所有專案出現,要關就 `note_shape.tag_hints: off`」。第 0 步到第 2 步之間 W4 沒有開關。〈回退〉第 0 步只能還原提交。
5. `note_shape.gate=off` 時 `cmd_note_shape` 在算提醒之前就返回。「所有專案」的承諾對這種專案不成立,spec 沒說。
6. S13 只驗 since、retire,W4 條文還寫了 until 過期,兩邊不齊。
引句:「當 `note_shape.tag_hints` 是 off,W1 到 W6 與欄位寫壞的提醒 應 都不出現」
佐證:`scripts/lumos:25537`、`scripts/lumos:25827`、`scripts/lumos:25835`

**R2I7**
severity: minor
blocking: 否——spec 的設定寫法有幾處對不上現有程式,實作時會發現,但不會做出錯的行為。
1. 「照 `drift_check.old_sentence` 的先例」只有一半成立。
   - old_sentence 預設是 warn,壞值也照 warn(`_drift_old_sentence_config`)。
   - spec 要 block 預設、壞值照 block。這是 Enzo 已裁的,但「先例」兩字會誤導實作者去抄 warn。
2. `_drift_config` 現在回 4 元組,至少 5 處測試直接拆它(例如 `scripts/test_lumos.py:51188`、`:52645`、`:57629`)。加第三個開關會動到這些呼叫端。spec 沒指定是擴充元組還是另開一支。
3. 開關關係沒寫:`gate=off` 或 `gate=warn` 時,`fields` 照 block 跑嗎?存量漂移守衛的 RULE 明講過 m1 是各管各的,所以 `gate=off` 的專案升級後會被擋。欄位判定同理。
4. doctor 要不要為 `drift_check.fields` 和 `note_shape.tag_hints` 各加一行?m1 就是因為沒加,被代碼審 r2 抓成 PITFALL(`Systems/存量漂移守衛.md:74`)。spec 兩個開關都沒列 doctor 行。
引句:「`drift_check.fields`(block 預設,壞值照 block 並講一句,照 `drift_check.old_sentence` 的先例)」
佐證:`scripts/lumos:29724`、`scripts/lumos:29695`、`scripts/lumos:30924`

**R2I8**
severity: minor
blocking: 否——搜尋新旗標的細節 spec 沒補齊,實作者會自己選,但選的結果可能違反既有合約。
1. `--top` 現在的 argparse 預設是 0,意思是「全量,不截斷」。spec 要行模式預設 80、`--top 0` 全給。這兩者在不改預設值為 `None` 的前提下分不出來,spec 沒指出。同一個旗標在排序模式算篇數,在行模式算行數,也沒說。
2. `Systems/lumos-cli-read` 的 ★INVARIANT★ 規定隱藏數走 stderr、`--json` 另帶 `hidden_superseded`。行模式隱藏的行數只寫印 stderr,`--json` 沒有對應欄位,機器端看不到被藏了幾行。
3. 行模式要同時看被標 superseded 的行和節點層的作廢節點。作廢節點裡的行要加哪個旗標才看得到沒寫。`--include-retired` 和既有的 `--include-superseded` 名稱太近,使用者容易用錯。
4. 搜尋進入點 `p.add_argument("term")` 是必填位置參數。「term 可以不給」要改成 `nargs="?"`,cmd_search 的簽名也要動。
5. 行模式要自己的輸出路徑:`--regex` 和 legacy 在 `cmd_search` 裡是邊掃邊印,`--json` 只存在於 ranked 路徑。
引句:「行模式預設 80 行,`--top 0` 全給」
佐證:`scripts/lumos:40184`、`scripts/lumos:40168`、`scripts/lumos:3986`、`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:37`

**R2I9**
severity: minor
blocking: 否——`--about` 照字面能實作,但在這個 repo 最常改的檔上用處有限。
1. 「那支檔的家筆記(about_code 列了它)」。`scripts/lumos` 被 40 篇 Systems 筆記的 about_code 列出,那 40 篇共有 159 條 WHY/RULE/PITFALL 摘要行。我是用 grep 數的,多行寫法的行可能沒算進去。
2. 行模式預設只給 80 行,截斷順序 spec 沒定義。〈按需載入〉第 3 點沒說排序。
3. 這個 repo 已有「家」的解析機制(推筆記認家,`lumos impact --file` 用)。spec 沒說 `--about` 要不要沿用,也沒說只取家還是取全部列出它的筆記。
4. 因此 skill 查詢表那行「我要改這支檔,有哪些還有效的規則與坑」,在這個 repo 最常被改的檔上會回傳被任意截掉一半的清單。
引句:「那支檔的家筆記(about_code 列了它)的摘要行」
佐證:`docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:1`

**R2I10**
severity: minor
blocking: 否——spec 範例和規則自己對不上,AI 照抄範例會寫出不評估的欄位。
1. 範例把欄位包在反引號裡:「加變數前先量記憶體 `[count:app/config.py::MODEL_VARS=4]`」。按〈欄位 v1〉的規則,行內程式碼裡的欄位不評估。AI 照抄這個範例,會寫出永遠不生效的欄位。這些範例預計搬進 skill 單源,速查表也要避開。
2. 〈寫在哪裡才算〉說這類欄位要被提醒「寫在不評估的地方」。S9 的清單包含行內程式碼和圍欄。
   - 但現有的 `_ns_negation_hints` 路線只看可見的 body/summary 行(`i not in vis_nos`),會跳過圍欄。
   - 條件式回頭條件的 `_probe_lines` 的 dead 清單只收表格和 frontmatter 非 summary 欄位,不收行內程式碼和圍欄。這是刻意的:文件範例不該被提醒。
   - S9 的「行內程式碼、圍欄」要新寫路徑,不是「同一套」。而且這份計劃自己就在表格和行內程式碼裡寫了 `[count:路徑::名稱=N]`,提交就會自己觸發。
3. 否定現況句的欄位遮罩 `_NS_NEG_FIELD_KEYS` 沒有 count、value、lives。我實跑 `[value:cfg.py::MODE=TODO]` 會觸發否定現況句提醒(命中 `TODO`)。新欄位值裡出現這類字,W3 會誤報。
引句:「行內程式碼、表格、圍欄、frontmatter 非摘要欄位裡的欄位不評估」
佐證:`scripts/lumos:25389`、`scripts/lumos:25496`、`scripts/lumos:28690`

**R2I11**
severity: minor
blocking: 否——同一個 `[status:superseded]` 在兩處給了相反的處理建議。
1. 現有 `rule_lifecycle_warnings` 對 RULE 行的 `[status:superseded]` 唸「確定撤掉就把整行刪掉,別留著讓人誤讀」。
2. spec 把 `[status:superseded]` 擴到 WHY、PITFALL,並要求同一行附 `[[連結]]`,留著當歷史,搜尋時預設隱藏。
3. RULE 行的 `lumos lint` 警告和 spec 的做法衝突。〈欄位 v1〉說已作廢是「既有欄位,擴到 WHY、PITFALL 行」,沒提 RULE 行該怎麼處理已有的警告。
4. 分期第 3 步沒列要改這句警告。
引句:「不擋;同一行沒有連結 → 提醒」
佐證:`scripts/lumos:3337`

**R2I12**
severity: minor
blocking: 否——幾處文件和量測沒列進計劃,落實時會被 doctor 或消費專案發現。
1. S3 說「舊帳由 doctor 列出」。分期沒有任何一步做 doctor 列出欄位舊帳。
   - 現有 doctor N 只管 HTML 標記。
   - 存量漂移守衛的 `drift scan`、doctor Z、考試都不跑 m1(一棵樹判不了「消失」)。欄位的「起點不吻合」要判,同樣得兩棵樹。
2. RETIRE-IF 靠「新寫脈絡行帶欄位的比例」和「被擋 20 筆誤報」。分期第 4 步只寫「上線後照 RETIRE-IF 與 REVISIT 量」。
   - 沒有量測程式或帳欄位。否定現況句提醒當時有 `governance/eval/negation-revisit/` 的量測程式和 `hinted` 帳。
   - 〈實務隱患〉也承認「誤報要人工抽查判,帳只給次數」。
3. 要同步改、spec 沒列的文件:
   - `skills/lumos-project-notes/commands/08-自動跑的.md` 第 5、9 行描述提交前和 CI 做什麼。
   - 這份 `03-寫回圖譜.md` 第 8 行的 note-shape 說明。
   - `scripts/test_lumos.py` 裡拆 4 元組的測試(R2I7)。
   - 動紀律範本後,本 repo 自己注入的 CLAUDE.md 區塊要重新注入。
   - 紀律範本現況 11485 bytes,已超過瘦身基線 5256 bytes 的 150%。「加一行」的主張成立,但 doctor Check D 會繼續提醒。
引句:「4. **量測**:上線後照 RETIRE-IF 與 REVISIT 量。」
佐證:`skills/lumos-project-notes/commands/08-自動跑的.md:5`、`scripts/lumos:2842`

各節結論:
- 前言、依據、PRIOR-ART、現況、設計原則、前綴表:已讀。除上列各條引到的句子外,無 finding。
- 現況的四處文件矛盾我抽查 `reference.md:408` 的 RULE 範例和 `SYMBOL_NAMES` 沒有 RETIRE-IF,確實存在。
- 〈欄位 v1〉:見 R2I2、R2I3、R2I4、R2I10。路徑切法在不同位置的欄位寫法,未發現其他衝突。
- 欄位與既有的行號引用檢查不衝突:我實跑 `_ns_check_line`,`[count:…::X=4]`、`[value:…::URL=http://h:80]`、`[lives:src/x.rs::Client::connect]` 都不會被當成程式行號引用(0 筆違規),這點沒問題。
- 寫法提醒:見 R2I5、R2I6、R2I10、R2I11。
- 一個事實只寫一處、讓 AI 知道該寫什麼:提交前掛鉤 `note-shape --staged` 確實在 pre-commit(`scripts/hooks/pre-commit:230`),lint 通過時輸出被吞掉的說法也成立(第 187 行 `$(…)` 擷取輸出,只在失敗才印),所以提醒只能走 note-shape 這條。第 4 點「impact hook 不加筆記分支」未發現矛盾。
- 按需載入:見 R2I8、R2I9。
- 不溯及既往、分期、已裁、天花板、不做:見前述各條。
- 驗收條款:S1、S2、S5、S8 沒發現問題。S3、S4、S6、S7、S9、S10、S11、S13、S14、S16、S17 在前述各條中提到。S12 的比對規則已讀,無 finding。
- 回退:第 1 步「舊工具不認得新欄位,也不會當成效力條件」成立,因為 RULE 效力只看既有三欄。
- 合約候選:同上。
- 審計修正紀錄:已讀,無 finding。

實務隱患逐類:
- 併發:新增寫入只有治理帳,沿用既有寫入點,無新增風險。
- 效能:HTML 標記重算要兩個提交各讀一遍 repo,spec 承認受預算管但沒說怎麼做,見 R2I4。
- 資源:無長駐程序,無風險。
- 回滾:見 R2I6 第 3、4 點(第 0 步的 W4 沒有開關)。
- 注入:搜尋輸出是唯讀片段,同現況風險。
- 金流、對外送出、不可逆:同意 spec 的排除說明。

最高嚴重度:major,blocking 6 條
