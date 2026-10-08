severity: major

固定席筆記:這次派工詞尾端沒有附任何固定席筆記,所以「逐條判不影響」那一項無從判,我不編。

先講結論。這份設計的方向通順,但有四個零件在程式裡不是它說的樣子。這四個零件是轉變方向、`::` 切法、`RETIRE-IF` 的擋、doctor 的重算。另有兩處規則自己打架:判不了該不該擋、名稱消失要不要看起點。以下都是我開檔讀過語意才寫的。

上一輪(r1)的席報告我讀過。r1 報的「改檔前提示 hook 不觸發」「`term` 必填」「`enum` 沒地方放」等,這版確實改掉了。下面只列新版的新洞。

## 逐節

- 前言、依據、PRIOR-ART:已讀,見 R2C1 與 R2C9。
- 現況:已讀。盤點結論裡 `RETIRE-IF` 不在前綴表、RULE 註解與範本不一致、`term` 必填,我都核對屬實(`scripts/lumos:3225`、`scripts/lumos:3268`、`scripts/lumos:40168`)。無 finding。
- 設計原則:已讀,見 R2C2。
- 前綴表:見 R2C6、R2C8。
- 欄位 v1:見 R2C1 到 R2C5、R2C7、R2C9、R2C10。
- 寫法提醒:見 R2C11、R2C12。
- 一個事實只寫一處:見 R2C13。
- 讓 AI 知道該寫什麼:已讀,無 finding。hook 不動符合 `scripts/hooks/claude/impact-hook.py` 的現況。
- 按需載入:見 R2C14。
- 不溯及既往:已讀,無 finding。
- 分期:見 R2C12。
- 已裁、天花板、不做、實務隱患:已讀,無 finding。
- 驗收條款:S5 與 R2C3 衝突,S15 與 R2C6 相關,其餘見各條。
- 回退、合約候選、審計修正紀錄:已讀,無 finding。r1 數字加總我核過:12+12+10+8+6+5=53,對得上。

## findings

**R2C1 「沿用既有轉變判定」方向是反的**
severity: major
blocking: 是——照 PRIOR-ART 說的「沿用」去接,會做出方向相反的判定。
1. 輸入是 PRIOR-ART 說存量漂移檢查「已經有『起點成立、終點不成立才擋』的轉變判定」,欄位判定要接在上面。
2. 實際上 `_drift_probe_judge` 是「終點成立,而起點沒有同一條或同一條還不成立 → 要處理」。它擋的是不成立變成立(回頭條件被觸發),跟欄位要的成立變不成立剛好相反。
3. 「同一條」的比對只比條件標記的元組,不認欄位的值。判定函式得整支新寫。
4. 壞法:實作者把欄位當成另一種條件餵進 `_drift_probe_line`,出來的是「吻合就擋」,所有健康欄位一推就被擋。
引句:「的轉變判定、時間預算、判不了的處理、子開關與單次跳過、推送前掛鉤與 CI 接線」
佐證:`scripts/lumos:28630`、`scripts/lumos:28603`

**R2C2 「名稱不見了 → 擋」沒有起點條件,跟原則 3 與 S3 打架**
severity: major
blocking: 是——照字面寫,一條舊帳會讓之後每個動到那支檔的無關推送都被擋。
1. 輸入:`[count:app/config.py::MODEL_VARS=4]` 早就因為重構而失效,名稱在起點就不存在,終點也不存在。
2. 欄位表第二個分句只寫「終點那個名稱不見了 → 擋」,沒有「起點有」。第一個分句和 `lives` 才有起點條件。
3. 原則 3 與 S3 說起點就對不上的舊帳不擋。兩邊矛盾,實作者只能猜。
4. 照字面實作,只要有人改了 `app/config.py`,這條舊帳就擋住推送。
5. 起點有名稱但數不吻合、終點名稱消失,該算哪一種,也沒寫。
引句:「起點 N(或字面值)吻合、終點不吻合 → 擋;終點那個名稱不見了 → 擋;這次新寫的欄位在終點就不吻合 → 擋(寫錯了)」

**R2C3 「判不了」的處理三處互相矛盾,而既有行為是判不了就擋**
severity: major
blocking: 是——S5 的合約和〈判不了〉那一行不能同時成立。
1. 〈判不了〉一行說「照存量漂移檢查既有的處理,不另訂」。
2. 既有行為是 `cmd_drift_check` 的 docstring 寫「判不了的…算要處理——放行等於一條繞過的路」,而且 `if not must and not unknown: return 0`。block 模式下 unknown 非空就 rc1。
3. 欄位表與 S5 卻要求求值器讀不出來(程式組出來的集合)時「不擋」。spec 沒分「語意上判不了」和「基礎設施判不了」兩種。實作者要是把求值器的判不了丟進 `unknown` 清單,S5 會紅;要是不丟,又違反「不另訂」。
4. 混合情形也沒定:起點讀不出(例如以前是動態組出來的,這次改成字面值),終點讀得出而不吻合,該不該擋?
5. 正規式數量也踩到。doctor N 的重算超過 4000 檔或 40MB 時是丟 `RuntimeError`,只記成「標記本身有問題」的提醒。搬進 drift 就成了判不了,一個 `in=**/*.py` 的標記就能擋住所有推送。
引句:「照存量漂移檢查既有的處理(git 逾時、淺複製、預算用完時的嚴格判定沿用它的設定),不另訂」
佐證:`scripts/lumos:29779`、`scripts/lumos:29831`、`scripts/lumos:3018`

**R2C4 `lives` 說「沿用同一支符號判定」,但既有的路徑切法會把 `Client::connect` 切錯**
severity: major
blocking: 是——S6 第二句照字面做不出來。
1. 輸入:`[lives:src/net.rs::Client::connect]`。
2. `_DriftProbeTree.one`、`prefetch`、`_drift_probe_cond_candidate` 全都靠 `_drift_cond_split`,它用 `v.rsplit("::", 1)`。切出來路徑是 `src/net.rs::Client`、名稱是 `connect`。
3. 那個「路徑」不在檔案樹上,`one()` 直接回 False,候選篩選也永遠不把它當候選(`path in touched` 不成立)。
4. spec 要求「帶副檔名的路徑之後」才切。這是另一種切法,所以不能說沿用,要新寫切法並替換三處呼叫。
5. 同樣長相的 `[when-symbol:路徑::名稱]` 仍然從最後一個 `::` 切。同一個語法在兩處有兩種切法,spec 沒交代。
引句:「沿用回頭條件探針的符號判定(同一支 `_DriftProbeTree`;Python 用語法樹、其他語言用文字)」
佐證:`scripts/lumos:28241`、`scripts/lumos:28392`、`scripts/lumos:28476`

**R2C5 「路徑要帶副檔名」把工具鏈自己的主程式排除在外**
severity: major
blocking: 是——spec 裁了「工具鏈也擋」,但工具鏈最大的一支檔沒法被欄位指到。
1. 輸入:`[count:scripts/lumos::_PROBE_KEYS=4]`。`scripts/lumos` 沒有副檔名。
2. 切法規則以「帶副檔名的路徑」為錨,「欄位寫壞」又把路徑不帶副檔名列為提醒。這條欄位會被當成寫壞,評估不到。
3. 既有程式專門處理過這種檔:`_drift_probe_code_path` 的註解寫「工具鏈主程式 scripts/lumos 沒有副檔名」。`Makefile` 與 `#!` 腳本也一樣。
引句:「鍵名不認得、少了 `=值`、值被 `]` 截斷、路徑不帶副檔名、寫在不評估的地方 → 提醒」
佐證:`scripts/lumos:28085`

**R2C6 `RETIRE-IF` 沒有「條件成立 → 擋(既有)」這個機制**
severity: major
blocking: 是——表格宣稱既有行為,實作者會以為不用做。
1. 前綴表的 REVISIT、RETIRE-IF 這一列,寫「日期或 `[when-*]` 條件(既有)」「條件成立 → 擋(既有)」。
2. 實際上 `_revisit_split` 只認 `REVISIT:`。全 repo 對 `RETIRE-IF` 的唯一處理是 `scripts/lumos:25462`,它只是把這種行從否定現況句檢查豁免。
3. `RETIRE-IF` 現在連 `SYMBOL_NAMES` 都不在,更沒有日期或條件解析、也沒有擋。S15 只測「前綴表認得」,不測擋。
4. 本 spec 自己的 `RETIRE-IF` 行是散文(「不到 5%」),機器本來就讀不了。
5. 這一列要嘛改成「不擋,只當前綴」,要嘛補一個實作步驟。
引句:「日期或 `[when-*]` 條件(既有) | — | 條件成立 → 擋(既有)」
佐證:`scripts/lumos:3225`、`scripts/lumos:25462`

**R2C7 已作廢的行,它自己帶的依賴欄位還會繼續被評估**
severity: major
blocking: 是——作廢沒有出口,舊決定會一直擋推送。
1. 輸入:一條 WHY 帶 `[count:app/config.py::MODEL_VARS=4]`,後來被新決定取代,加上 `[status:superseded]` 與連結。
2. 欄位表只說已作廢「不擋」,沒說這一行的 `[count:]` `[lives:]` 要不要跳過。欄位的評估範圍是「所有可見的正文與摘要行」,沒有排除作廢行。
3. 程式把 `MODEL_VARS` 改成 5,這條已經被取代的決定反而擋推送。加 `[status:superseded]` 這個動作不改變欄位元組,也救不了。
4. 唯一的出口是刪欄位或 `drift ack`。這跟「作廢=檢索排除、歷史保留」的設計(Zep 那條前例)相反。
引句:「不擋;同一行沒有連結 → 提醒」

**R2C8 〈判過時〉欄寫的到期提醒,絕大多數情況送不到;`FACT` 的 `[confirmed:]` 沒有任何實作步驟**
severity: major
blocking: 是——宣稱的判過時行為,照字面實作永遠不會在該響的時候響。
1. 表格寫 RULE 的「`[until:]` 過期、`[confirmed:]` 超過半年 → 提醒」,FACT/FLOW/DEP 的「帶 `[confirmed:]` 超過半年 → 提醒」。
2. 實際送出管道只有 W4:「只對新寫的 RULE 行(走新增行那條路,不是整篇 lint)」。S13 也要求舊 RULE 行不提醒。
3. 到期是時間函數,一條沒人碰的舊 RULE 到期了,它那一行不是新增行,提醒永遠不出現。只有人剛好又改這一行,才會被提醒「你已經過期」。
4. FACT/FLOW/DEP 的 `[confirmed:]` 提醒在分期 0 到 4、W1 到 W6、S1 到 S19 裡都沒有對應的步驟。
5. 這一格的「判過時」其實沒有機械檢查,卻佔了收欄位門檻的名額。
引句:「依賴欄位變了 → 擋;緊鄰的回頭條件從不成立變成立 → 擋(既有);`[until:]` 過期、`[confirmed:]` 超過半年 → 提醒」

**R2C9 「doctor N 與存量漂移檢查呼叫同一個重算函式」,但兩邊的資料來源語意不同**
severity: major
blocking: 是——S7 第二句與「第二種做法」的合約守不住。
1. doctor N 現在用 `os.walk(repo_root)` 掃工作目錄。它排除 `CODE_SKIP_DIRS`,包含沒追蹤的檔,讀檔用 `errors="ignore"`,有 4000 檔與 40MB 上限。
2. 存量漂移檢查要比的是起點與終點兩個提交的樹,走 `_DriftProbeTree`/git 物件,沒有磁碟、沒有未追蹤檔。
3. 「抽成共用函式」沒說函式吃什麼:樹?檔案清單加讀取器?兩條路徑的過濾與編碼處理不一致,doctor 說對、drift 說錯(或反過來)就會出現。
4. 起點與終點都要讀一遍所有符合 `in=` 的檔,預算怎麼分也沒寫。
引句:「本案把 doctor N 段裡內嵌的重算抽成共用函式,存量漂移檢查也呼叫它」
佐證:`scripts/lumos:3017`、`scripts/lumos:3018`、`scripts/lumos:3034`(整段 os.walk 迴圈)

**R2C10 求值器的邊界沒定:重新指派、就地修改、值怎麼比**
severity: minor
blocking: 否——不改,實作者會多出幾種判錯;S1 到 S8 仍能綠。
1. 輸入:`X = [a, b]` 之後又有 `X += [c]`、`X.append(c)`、`if/else` 兩處指派,或 `X` 是 Enum 且有別名成員。
2. 規則只說「讀模組層的指派」「讀不出來的 → 判不了」,沒定這些情形算讀得出來還是判不了。取第一個或最後一個字面值,會悄悄給出錯的數,錯在「誤報 0」的前提上。
3. `[value:…=字面值]` 的比較也沒定:字串要不要帶引號、`1.0` 對 `1`、`True` 對 `true`。S4 沒有任何反例壓這幾種。
4. `{1, 1}` 這類重複成員,字面值成員數和執行時不同。
引句:「Python 用語法樹讀模組層的指派——清單、元組、集合、字典字面值的成員數,Enum 類別的成員數,常數字面值(整數、浮點、字串、布林)」

**R2C11 W1、W2 的判準有洞**
severity: minor
blocking: 否——只提醒不擋,但會出雜訊。
1. W1 沒定義「程式符號」是什麼形狀。PITFALL 必帶的「重現指令」、WHY 的提交編號都寫在反引號裡,又沒有依賴欄位,幾乎每條必備內容都會被提醒。
2. W1 的範本要填 `路徑::名稱=N`,但判準只知道名稱;路徑和 N 從哪來沒寫。S10 只驗「填好名稱」。
3. W2 排除 FACT,但 FLOW、DEP 同樣被定義成「只寫程式答不了的現況」。一條 `FLOW:[來源:部署] 只有 2 個 worker` 會被提醒成「程式推得出的事實」。
引句:「Systems 筆記新寫的摘要行含「只有/唯一/恰好 N/N 個/N 支」這類寫死數量,而且前綴不是 WHY、RULE、PITFALL、FACT → 提醒」
(此引句含「」。單行替代引句:「只看摘要行;FACT 排除(它寫的是程式答不了的現況)。」)

**R2C12 兩個開關的上線順序與管轄範圍沒定**
severity: minor
blocking: 否——只影響關得掉與關不掉的判斷。
1. W4 放在分期 0,而 `note_shape.tag_hints` 要到分期 2 才出現。實務隱患卻說「W4 要關就 `note_shape.tag_hints: off`」,S14 的關閉測試也涵蓋 W4。分期 0 到 2 之間 W4 無開關可關。
2. `cmd_note_shape` 在 `note_shape.gate=off` 時於算 hints 之前就 return(`scripts/lumos:25830`)。這時 `tag_hints` 的值沒人讀,spec 沒提這個從屬關係。
3. `drift_check.fields` 與 `drift_check.gate` 的關係沒定。既有 `old_sentence` 是獨立開關;但 PRIOR-ART 說欄位接在 probe 判定上,而 `gate=off` 時 `_drift_check_c` 在 `scripts/lumos:29812` 就回 0。一個把 `gate` 設成 warn 或 off 的專案,`fields: block` 預設到底算不算數,字面上推不出。
4. W3 與 S18 都沒有掛在 `tag_hints` 下列舉的測試;S14 的「W1 到 W6」沒涵蓋 S18 的提醒。
引句:「子開關 `note_shape.tag_hints`:`warn`(預設)/ `off`,照 `note_shape.negation` 的先例,壞值照 warn 並講一句。」

**R2C13 spec 自己的範例把欄位寫在行內程式碼裡,照抄就落入「不評估」區**
severity: minor
blocking: 否——只是範例瑕疵,但這些範例會被拿去寫速查表與 skill。
1. 〈寫法〉第 96 行規則:行內程式碼裡的欄位不評估,還會提醒「寫在不評估的地方」。
2. 〈正文怎麼寫〉的兩個範例都把欄位包在反引號裡:`[count:app/config.py::MODEL_VARS=4]` 與 `[lives:app/router.py::dispatch]`。AI 照這兩個範例抄,寫出來的欄位正好是死區。
3. 速查表是從這些範例做的,所以要明講「範例的反引號是排版,真正寫的時候不加」。
引句:「寫「WHY:[2026-10-01 討論]模型變數的數量要跟 GPU 記憶體對齊,加變數前先量記憶體 `[count:app/config.py::MODEL_VARS=4]`」——數量只在欄位裡」

**R2C14 搜尋行模式的預設上限與既有合約不一致,截斷順序也沒定**
severity: minor
blocking: 否——只影響 agent 看到哪些行。
1. `--top` 現有語意是「0=全量,預設;圖譜先行不靜默截斷」(`scripts/lumos:40186` 附近)。行模式改成預設 80,同一旗標兩種預設。
2. 超過 80 行時留哪些行沒定。入口範例 `--about <檔> --prefix RULE,PITFALL,WHY` 把三種前綴混在一起排,可能先丟掉最該看的 RULE。
3. 截斷數印在 stderr,agent 常不讀 stderr。
引句:「行模式預設 80 行,`--top 0` 全給),截掉的行數印在 stderr」
(原句是「…`--top` 限總行數(行模式預設 80 行,`--top 0` 全給),截掉的行數印在 stderr」;上面引句取其中連續一段。)

## 實務隱患(碰到的風險類)

- **併發**:無新問題。唯一新增的寫入點是治理帳,沿用既有。
- **效能**:有,見 R2C3 第 5 點與 R2C9 第 4 點。對起點與終點各讀一遍符合 `in=` 的檔,預算怎麼分沒寫。
- **相容(新舊互讀)**:舊筆記沒欄位,不受影響。唯一例外是新增的 `[status:superseded]` 適用到 WHY/PITFALL 後,既有 `rule_lifecycle_warnings` 對 superseded 的 RULE 一律唸「確定撤掉就把整行刪掉」(`scripts/lumos:3336`)。W4 若直接沿用那支函式,會跟 spec「保留並連結」的做法打架,實作時要拆開。
- **時間(到期、確認日期)**:見 R2C8。
- **不可逆**:spec 說「欄位留著無害」。我反例找不到。R2C7 是唯一例外:留著作廢行上的欄位不無害。
- **注入、資源、回滾**:無新問題,理由同 r1。搜尋唯讀,不開程序,回退各步都能獨立還原。
- ⚠ **首推空起點(判不準,交編排者)**:`_drift_probe_prepare` 在 `base` 為空樹時 `benv=None`,所有欄位都算「這次新寫」。按 S4 的字面,每條在終點不吻合的欄位都會擋。我沒能確認首次推到空遠端時 `_push_range_start` 實際回的是空樹還是 merge-base,也沒確認 `drift exam --history` 重放會不會也走這條。這要不要擋,spec 沒表態。

最高嚴重度:major,blocking 9 條
