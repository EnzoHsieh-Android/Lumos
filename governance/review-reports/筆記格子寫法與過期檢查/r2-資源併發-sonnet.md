severity: major

已讀整份 spec。這次沒有固定席筆記附在派工詞尾端,所以「破壞既有節點宣稱的行為或合約」無從逐條判。凡是「`路徑:行號`」都是我在對照 repo 開檔讀過語意的結果。

上一輪(r1 資源併發席)的 R1 到 R7 大多補上了:上限 20、清控制字元、自己的上線點、改到舊行不算新寫、`when-*` 語法、`[取代:]` 改名、子開關優先序。下面是補丁跟原文銜接處的新洞。

**R2R1 「判不了只列出、不擋」跟既有存量漂移檢查的判不了語意相反,而且 RULE 行會搶光預算**
severity: major
blocking: 是——照字面實作,不是被預算耗盡的 REVISIT 條件連帶擋推送,就是得另改 `_drift_report_must`,spec 沒寫這件事。
- 輸入:上千篇筆記、數百條 RULE 帶 `[retire:when-*]`,一次推送有程式檔新增、刪除或改名。
- 走到哪:〈格子欄位的過期檢查〉第一列、S12。
- 壞在哪:
  - `_drift_probe_check` 把全部筆記的條件行收進同一個 `lines`,候選與判定共用一個 60 秒的 `deadline`。預算用完後,剩下的行一律進同一個 `unknown` 清單(`scripts/lumos:29156` 起的迴圈)。
  - `unknown` 只是一串字串,沒有標記來自 REVISIT 還是 RULE。`_drift_report_must` 對它的處理是:只要非空就算要處理,`block` 模式 rc=1(`scripts/lumos:30423`、`scripts/lumos:30445` 以下)。提示文字寫明「判不了就放行等於一條繞過的路,所以算要處理」(`scripts/lumos:31169`)。
  - 所以 spec 要的「RULE 判不了只列出」要拆清單,現有程式是整串擋。照現有程式實作,「判不了只列出、不擋」做不出來。
  - 反過來,RULE 行與 REVISIT 行排在同一個迴圈裡。RULE 撤除條件(長命,可以上千條)吃掉預算,原本能判完的 REVISIT 條件被擠成「超過預算」,於是擋推送。這是 r1 R1 換了形狀的同族問題:spec 只修了不帶路徑的符號,沒修預算共用。
  - 「輸出最多 20 條加總數」只在 `_drift_print_findings` 做了。`for u in unknown: print(...)`(`scripts/lumos:30433`)沒有上限,S12 的「最多 20 條」守不住。
- spec 缺的:RULE 與 REVISIT 的預算分開(或 RULE 排在後面),`unknown` 加種類標記,以及 `_drift_report_must` 要怎麼改。
引句:「判不了只列出、不擋(跟這次改動無關);輸出最多 20 條加總數」
佐證:`scripts/lumos:29156`、`scripts/lumos:30433`、`scripts/lumos:30445`、`scripts/lumos:31169`

**R2R2 判不了只列出,加上「只在轉變那次擋」,撤除條件的觸發會永遠漏掉**
severity: major
blocking: 是——最壞時序下「靠標籤防止過期」在這條上失效,而 spec 把這個結果當成已被接住。
- 輸入:推送 A 讓某條 RULE 的 `[retire:when-file:X]` 剛好成立(X 被加進來)。同一次推送預算用完、CI 淺複製跳過(天花板 5),或作者用 `LUMOS_SKIP_DRIFT_CHECK=1` 跳過。
- 走到哪:〈格子欄位的過期檢查〉第一列(判不了不擋)、第 3 步 doctor 清單。
- 壞在哪:
  - 判定只看「終點成立、起點不成立」。注釋寫「起點早就成立 → 不列」(`scripts/lumos:29088` 以下的 docstring)。
  - 推送 B 以後,起點已經成立,不會再列。
  - 第 3 步 doctor 的提醒清單是取代鏈、度量、人裁、確認週期、SEE 連結,沒有「撤除條件目前已成立」這一項。
  - REVISIT 之所以不會漏,是因為判不了會擋(見 R2R1)。spec 把 RULE 這側改成不擋,卻沒補上 doctor 的兜底。
  - 結果:該撤的 RULE 在判不了或被跳過的那一次之後,再也不會被任何機制唸到。
- spec 缺的:doctor 對「`[retire:when-*]` 現在成立」的靜態重驗(沿用 `drift scan` 的工作目錄判定,`scripts/lumos:31387`),或判不了時留一筆可追的紀錄。
引句:「判不了只列出、不擋(跟這次改動無關)」
佐證:`scripts/lumos:29088`、`scripts/lumos:31387`

**R2R3 `when-test` 沒有被要求帶路徑,「不掃全庫」只對 `when-symbol` 成立**
severity: major
blocking: 是——spec 的效能宣稱跟自己列的語法不符,大 repo 的任何加檔推送都會讓所有 `when-test` 撤除條件變候選。
- 輸入:上萬支程式檔的 repo。RULE 行照 spec 範例寫 `[retire:when-test:測試名]`(沒有 `路徑::`)。一次推送新增或改名任何一支程式或測試檔。
- 走到哪:第一列的候選篩選、〈實務隱患〉效能。
- 壞在哪:
  - `_drift_probe_cond_candidate` 對不帶路徑的 symbol 或 test,只要 `ch["code_shape"]` 就回 True,沒有再看名稱(`scripts/lumos:29078`)。
  - 判定時 `_DriftProbeTree.corpus(test)` 要把終點與起點兩棵樹的全部測試檔讀進來、用 ast 判定(`scripts/lumos:28959`)。
  - spec 只規定「`when-symbol` 必須帶路徑」,`when-test` 的格式是「測試名」,沒有路徑,也沒有任何限制。
  - 〈實務隱患〉寫「撤除條件只看這次推送改到的路徑、`when-symbol` 必帶路徑,不掃全庫」。對 `when-test` 這句不成立。
  - 一旦語料讀不完,就走 R2R1 的判不了路徑。
- spec 缺的:`when-test` 也必須帶路徑,或明講它是全語料掃描並算進預算。
引句:「`when-symbol` 必須帶路徑(不做全庫掃符號)」
佐證:`scripts/lumos:29078`、`scripts/lumos:28959`、`scripts/lumos:28568`

**R2R4 格子上線點記號不在 pre-commit 時,現有語意是「不過濾」,不是「不查」**
severity: major
blocking: 是——spec 靠這個機制保證「推出去前的歷史不被倒溯」,現有程式在這個狀態下做相反的事。
- 輸入:消費專案的程式已更新(程式即時全機生效),但 pre-commit 範本還沒更新,或照〈實務隱患〉的 14 天規定「記號先不寫進 pre-commit」。專案 CI 或 pre-push 呼叫 `note-shape --diff`。
- 走到哪:〈擋〉的「自己的上線點」、S7、〈實務隱患〉相容一條。
- 壞在哪:
  - `_nodehome_golive` 找不到記號回 None。
  - `_nodehome_clamp_base` 在 gl 是 None 時原樣回 base(`scripts/lumos:24933` 以下)。
  - `_notelines_new` 的 `live_mark` 在 golive 是 None 時為 None(`scripts/lumos:25674`)。docstring 寫「找不到上線點時照既有語意不過濾」。
  - 也就是記號不存在時,範圍內每一個提交的每一行都被當成新寫。spec 想要的是「記號不存在 = 格子檢查不跑」。
  - 這兩者是相反的。spec 只寫「格子檢查不跑」,沒說程式要在 gl 為 None 時明確跳過格子規則。照「沿用現有路徑」實作,更新程式的當天,所有範圍內舊行都會被當成新違規擋下。
  - S7 的測試只覆蓋「記號之前的提交」,沒覆蓋「記號根本不存在」。
- spec 缺的:gl 為 None 時格子規則整段略過,並補一條 S7 的測試。
引句:「格子規則從「掛鉤第一次出現這個記號」那個提交起算;升級前寫好、升級後才推的提交不查」
佐證:`scripts/lumos:24933`、`scripts/lumos:25674`

**R2R5 doctor 的事後掃描路徑沒被 S7 涵蓋,而且格子的新行集合跟筆記形狀擋的新行集合不是同一個**
severity: major
blocking: 是——格子規則併進共用的 `_note_shape_eval` 時,doctor 會把沒有格子的舊行當成繞過回報。
- 輸入:專案在 note-shape 上線點之後、格子上線點之前寫了很多舊寫法的 WHY、PITFALL。跑 `lumos doctor`(非 `--ci`)。
- 走到哪:〈擋〉的「自己的上線點」。
- 壞在哪:
  - `_note_shape_doctor_lines` 用 `_NOTE_SHAPE_GOLIVE_MARK` 算起點 gl,再呼叫 `_note_shape_eval(root, False, gl, tip, ...)`(`scripts/lumos:26311` 以下)。這條路徑回報的是「已推上遠端卻違反……(多半是 --no-verify 繞過)」。
  - S7 只寫「推送與 CI 應不用格子規則查它」,沒提 doctor 事後掃描。
  - `_notelines_new` 只吃單一 `mark` 參數。逐提交是否算新行取決於那一個記號(`scripts/lumos:25656` 以下)。格子要自己的記號,就得對同一範圍多跑一輪(逐提交 diff 與改名偵測全部重算),或重構成雙記號。spec 兩樣都沒提。
  - 該函式自己的注釋量過:事後掃描 500 個提交約 9 秒(`scripts/lumos:26323` 附近),每次非 CI 的 doctor 都跑,格子再加一輪就是兩倍。
- spec 缺的:doctor 事後掃描對格子規則用格子自己的 gl;單一範圍內雙記號的做法;doctor 掃描的成本上限。
引句:「當提交發生在格子上線點之前,推送與 CI 應 不用格子規則查它」
佐證:`scripts/lumos:26311`、`scripts/lumos:25656`

**R2R6 `[retire:度量 …]` 的指標沒有可量的對象,治理帳又是 16MB 的單檔累加帳**
severity: major
blocking: 是——doctor 要實作的判定在 spec 裡沒有輸入。
- 輸入:任一 RULE 寫 `[retire:度量 觸發次數 > 5 近4週]`。
- 走到哪:〈格子規格〉度量一條、〈格子欄位的過期檢查〉`[retire:度量 …]` 一列。
- 壞在哪:
  - 治理帳每筆事件只有 `ts/commit/gate/kind/hard/nodes/note`,沒有「哪條 RULE」的識別。我在 `docs/.governance-log.jsonl` 實測:100304 行、約 15.9MB,單檔累加、無輪替。
  - 「觸發次數」「跳過次數」是哪個閘、哪種 kind 的事件,spec 沒定義。
  - 帳是按時間排序的追加檔,「近 N 週」仍要讀檔尾到足夠舊;N 沒有上限。每條帶度量的 RULE 若各讀一次就是 N 倍 I/O。
  - 現有先例是讀檔尾、上限 24MB(`scripts/lumos:2053`)。spec 說「只讀治理帳近 N 週的事件」,沒說一次 doctor 只讀一次、沒說上限。
  - 事件的篩選口徑沒定,實作者只能猜,結果是兩個實作者算出不同的「過期」。
- spec 缺的:指標對應的 gate 與 kind、是整庫計數還是每條 RULE 計數、N 的上限、doctor 一次只讀一遍。
引句:「度量 | 近 N 週的指標符合 | 提醒 | doctor(只讀治理帳近 N 週的事件)」
佐證:`scripts/lumos:2053`、`docs/.governance-log.jsonl`(100304 行)

**R2R7 `[取代:決策編號]` 的編號只在單篇筆記內唯一,取代鏈沒定義怎麼沿**
severity: major
blocking: 是——doctor 判「不存在」或「自己也作廢」的輸入有歧義,沿鏈可能走到錯的節點。
- 輸入:`WHY:… [status:superseded] [取代:d3]`。
- 走到哪:〈格子規格〉最後一列、〈格子欄位的過期檢查〉`[取代:]` 一列。
- 壞在哪:
  - 決策編號 `d\d+` 是每篇筆記自己從 d1 起編的(`_notelines_decision_fields` 的 `id:` 比對,`scripts/lumos:25760` 附近)。在工具鏈圖譜裡 `id: d1` 出現在 127 篇,`d2` 在 73 篇。只寫 `d3` 沒辦法全庫解析,doctor 不知道該查哪一篇。
  - 「它自己也作廢了」對節點是什麼:`status: superseded`?對決策是 `valid:false`(`decision-supersede` 寫的欄位,`scripts/lumos:16390`)?spec 沒定義。
  - 「沿鏈最多 10 層」對節點目標,鏈該沿目標節點的哪一行?一篇筆記有多條 `[取代:]` 行,spec 沒說。
  - 判不了(解析不出)時的處理沒寫:提醒、還是當作存在?
- spec 缺的:決策引用的完整格式(例如 `節點#d3`)、「作廢」的判準、沿鏈的單位、解析不出的處理。
引句:「指到的節點或決策不存在、或它自己也作廢了」
佐證:`scripts/lumos:16390`

**R2R8 〈擋〉寫「CI 照擋」,天花板 5 卻說 CI 淺複製整個跳過**
severity: minor
blocking: 否——實作者讀到後會照既有行為做,只是文件前後說法不一致,不會做出壞系統。
- 輸入:CI 淺複製。
- 壞在哪:`cmd_note_shape` 的 `--diff` 路徑在淺層 clone 直接回 0 並記 skipped-env(`scripts/lumos:26384` 以下)。〈擋〉第一條說「CI 照擋」,天花板 5 說「淺複製的 CI 不跑」。兩處對同一件事講法相反。
引句:「同一條路——新增行、違規清單、`LUMOS_SKIP_NOTE_SHAPE=1` 單次跳過留帳、CI 照擋」
佐證:`scripts/lumos:26384`

**R2R9 FACT 必有 `[confirmed:]` 加 30 天預設週期,提醒會同日成批到期,`--ci` 沒有上限**
severity: minor
blocking: 否——只是 CI 日誌變吵,不影響擋或不擋;但回頭看的條件(RETIRE-IF 沒有量這項)沒寫。
- 輸入:一次整理批次寫入數十條 `[來源:生產]` 的 FACT,`[confirmed:]` 都填同一天。
- 壞在哪:
  - 生產來源預設 30 天,同日寫的全部在同一天到期。
  - `warn_soft` 非 CI 預設每段只印 3 條,但 `_verbose = verbose or ci`(`scripts/lumos:1349`),`--ci` 全列。一次到期數十到數百條就全進 CI 日誌。
  - RULE 的 `[confirmed:]` 半年過期提醒已經存在於 lint 的 `rule_lifecycle_warnings`(`scripts/lumos:3391`),第 3 步再加一份 doctor 提醒會雙報。
- 不改的話沒有具體壞系統,故定為 minor。
引句:「RULE 超過半年;FACT 超過 `[recheck:]` 或來源預設」
佐證:`scripts/lumos:1349`、`scripts/lumos:3391`

**實務隱患逐類**
- 併發:兩個推送各自對遠端舊值算範圍,正確。但 `drift ack` 檔(提交進樹)與預算共用的狀況見 R2R1,沒有新的寫入競態。
- 效能:必有鍵比對是字串比對,沒問題。撤除條件的成本見 R2R1、R2R3。doctor 度量成本見 R2R6。事後掃描見 R2R5。
- 資源:無長駐程序,正確。
- 相容:見 R2R4。
- 注入:擋下訊息回填已有截斷與清控制字元,已補上。`unknown` 這條路徑的輸出沒有同樣處理,見 R2R1。
- 金流、對外送出、不可逆:同意 spec 的排除,理由成立(只讀筆記與程式文字)。

〈分期〉〈回退〉〈天花板〉〈不做〉〈驗收條款〉〈合約候選〉各節已讀,除上述外無 finding。

最高嚴重度:major,blocking 7 條
