---
type: project
status: doing
created: 2026-10-01
updated: 2026-10-01
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/guard-kill
related:
  - "[[Systems/guard-kill]]"
  - "[[Issues/存量筆記漂移三種機制_rtb根因回饋]]"
  - "[[Projects/漂移防治路線圖_計劃]]"
---
# 殺傷力配方失配提醒_計劃

白話:殺傷力配方是「故意把程式哪一段改壞,看綁定的合約測試會不會翻紅」的說明書,寫在筆記開頭的 `kill_recipes` 欄位,每條指名一支檔、要找的原文 `old`、要換成的壞法 `new`。程式後來重構,原文找不到(或出現好幾次),這條配方就失效了——等於合約測試的自我檢查斷線,而且沒人知道,因為只有手動跑 `lumos guard kill` 才會發現。這份計劃做三件事:寫入配方時就驗原文是不是恰好出現一次,不是就提醒(照舊寫入,保留既有「宣告不擋、跑時擋」的設計);健康檢查每次逐條數原文出現幾次,失配的列出來提醒;補一個移除配方的指令,讓失配的配方有路可修。先不擋推送,guard kill 本身不改。

依據:
- rtb 會談 2026-10-01 全圖譜漂移巡檢(rtb 提交 df6ff87,逐筆清單在 rtb 的 `governance/audits/2026-10-01-drift-sweep/findings.md`,形狀表在 rtb 的 `Issues/存量筆記漂移等工具修復`〈形狀與修法〉):形狀 K1「殺傷力配方失配」10 條——執行迴圈 5 條、提案收件口 4 條原文出現 0 次(程式重構過)、Mock-DSP 1 條出現 4 次;10 條全掛在 ★INVARIANT★ 上。巡檢者逐條驗過。
- 工具鏈現況(2026-10-01 編排者讀碼,另派不知情的查證席照原始問題重查,結論相同):唯一數原文出現次數的地方在 `cmd_guard_kill` 裡,而且是建好隔離工作樹、跑完基準測試之後才數;`cmd_guard_kill_add` 寫入配方時不開那支檔;doctor、推送前掛鉤、CI、pitfalls、contracts、guard list/audit/trace 都不讀配方內容。圖譜裡沒有討論過「配方靜態失配檢查」(沒有提案、也沒有被否決)。
- Enzo 2026-10-01 說「好」,先從 K1 開始。

PRIOR-ART: ①最小解在既有層——`cmd_guard_kill` 已經有「原文恰好一次,否則判 drifted」的判準,本案的新判斷用同一種讀法(文字模式 UTF-8)、同一種基準與圍欄(平台根所在 repo 的最上層、realpath 前綴判法)與同一個次數條件,但不改 guard kill 本身(它的圍欄、錯誤說明與回傳碼有既有合約與測試,抽共用會改到它的行為,前置掃描逐項證實);健康檢查新段落照 doctor P 段(筆記提到的程式檔路徑還在不在)的形狀:讀工作目錄、只提醒、預設每段最多列 3 條 ②世界解過——突變測試工具(mutmut、Stryker)的變異點是工具從程式自動產生、每次重算,不會有「配方失配」這種存量;本專案的配方是人寫的宣告式壞法(guard-kill 的設計取捨),所以要自己補「宣告跟程式還對不對得上」的檢查,形狀等同 doctor 的 Check N「存查詢不存答案、每次重算比對」 ③裁定=borrow-design:借 guard kill 自己的 drifted 判準,原生實作。
RETIRE-IF: 連續兩次、間隔至少 4 週的 `lumos doctor --verbose` P2 段在 rtb(跨會談回報)與至少一個配方數 10 條以上的其他消費專案都是 0 條(配方都健康、或配方被全部移除)——只看工具鏈不算數(工具鏈只有 1 條配方,條件恆成立;CI 上的 `check-p2` 事件也不會留存);或推送時改成擋的另案上線、把這一段取代掉。成立就把 doctor 這一段撤掉(寫入時的提醒與 kill-rm 保留,它們沒有維護成本)。
REVISIT:2026-10-15 用跨會談訊息請 rtb 會談跑 `lumos doctor --verbose` 並回報 P2 段全文,回報貼進本計劃〈實作紀錄〉;P2 列出 0 條 → 開「推送時改到配方目標檔就擋」的另案;1 到 3 條 → 再等兩週(這行改日期,★只准延一次★,延過之後還有剩就攤給人裁);4 條以上 → 攤給人裁(是不是改寫配方的成本太高、要不要改做自動提議改寫)。

## 範圍

- 做:一支新判斷函式(給 kill-add 與健康檢查用,判法逐項對齊 guard kill,並有一條對照測試釘住兩邊不分家);`lumos guard kill-add` 寫入時對有問題的配方印提醒(照舊寫入、回傳碼不變);新增 `lumos guard kill-rm` 移除指定的一條配方(失配配方的修法:先 rm 舊的、再 kill-add 照現在程式改寫的新配方);`lumos doctor` 新一段 P2 逐條列有問題的配方(只提醒,記治理帳事件 `check-p2`)。
- 不做:改 `cmd_guard_kill`(它的圍欄、讀檔、判定、說明與回傳碼一律不動);推送時擋(另案,等 rtb 存量清完);kill-add 擋下有問題的配方(保留既有設計「宣告不擋、跑時擋」——既有測試 `t_guard_kill`、`t_guard_kill_rc_precedence` 刻意用 kill-add 宣告失配或逃逸的配方來測 guard kill);自動改寫配方;驗壞法還能不能讓測試翻紅(那要真跑 guard kill)。

## 做法

### 1. 判斷函式(新,判法對齊 guard kill)

- guard kill 的實際做法(讀碼確認):對配方所屬平台的根目錄所在的 git repo 開一份隔離工作樹,工作樹的根是那個 repo 的最上層;配方的 `file` 從工作樹根算起;圍欄是「`os.path.realpath(工作樹根/file)` 要以 `realpath(工作樹根)` 加路徑分隔字元開頭」;讀檔用文字模式 UTF-8;原文用 `count` 數,恰好 1 次才套壞法。新函式在工作目錄裡照同一套算:
  - **基準**:配方所屬平台的根目錄 → `git -C <平台根> rev-parse --show-toplevel` 得到那個 repo 的最上層(下稱 repo 頂);`file` 從 repo 頂算起。平台根不存在、或不在 git repo 裡 → 由呼叫端各自處理(見下),不呼叫判斷函式。
  - ★先判配方是不是物件,再讀任何欄位★:不是物件,或 `file`、`old` 不是字串,或 `platform`、`invariant` 有值但不是字串 → `malformed`(這一步在取平台之前,所以型別壞的配方不會在取平台時先出錯)。顯示時 `invariant` 缺或不是字串一律當空字串。
  - **路徑解析照 guard kill 在隔離工作樹裡的結果模擬**(第 2 輪正確性席實跑:只看工作目錄的 realpath 會在四種情況跟 guard kill 判得不一樣):一支小解析器,以 repo 頂為根、逐段走 `file`——`file` 是絕對路徑 → `outside`;遇到 `..` 而已經在根 → `outside`(guard kill 的工作樹資料夾名跟 repo 不同,爬出去再爬回來會落在工作樹外);遇到符號連結就讀它的目標:目標是絕對路徑 → `outside`(工作樹裡的連結指回原 repo、落在工作樹外),相對路徑 → 把目標的各段接回去繼續走(連結套連結照樣處理);跟隨連結超過 40 次 → `outside`(迴圈)。走完還在根內才算解析成功,得到實際路徑。這樣「相對連結指向絕對連結」也會被判 `outside`。
  - 不是一般檔(目錄、具名管線、裝置檔)→ `missing`,細節寫「不是一般檔」(不開它,避免讀具名管線卡住)。
  - 文字模式 UTF-8 開檔讀全文;`OSError` → `missing`(細節帶原因);讀不成 UTF-8(`UnicodeDecodeError`)→ `undecodable`。
  - `全文.count(old)` 不是 1 → `hits`,細節帶實際次數;恰好 1 次 → `ok`。
  - ★同一次判定裡,同一支檔(以 repo 頂加 `file` 解析後的實際路徑為鍵)只讀一次★,全文快取給後面的配方共用。
- **配方身分**:節點字串一律用筆記在圖譜裡的相對路徑(跟 kill-add 判重時傳給 `_kill_recipe_key` 的 `str(rel)` 同一個值)。配方是物件、而且 invariant、file、old 都是字串 → 用既有 `_kill_recipe_key(節點、invariant、file、old)`;其他(不是物件、欄位缺或型別不對)→ 用 `sha256(json.dumps(["malformed", 節點, 原始元素], ensure_ascii=False, sort_keys=True))`,讓格式壞的配方也有身分、kill-rm 也移得掉。印出時取前 12 個字元當短身分。一支共用函式算身分,P2、kill-add 提醒、kill-rm 都呼叫它。
- **對照測試**:同一批題目(平台根是子資料夾、平台根就是 repo 頂、repo 內符號連結、絕對路徑符號連結、跑出 repo 的相對路徑、0 次、多次、非 UTF-8)讓新函式與真跑 `lumos guard kill` 各判一次,斷言兩邊的對應:`ok` ↔ guard kill 套用了壞法(沒判 drifted、沒判 error 逃逸)、`hits`/`missing` ↔ drifted、`outside` ↔ error(逃逸)、`undecodable` ↔ guard kill 讀這支檔出錯。日後誰改了判法,這條先紅。

### 2. 設定檔

- 讀設定之前先自己把 `.lumos/config.json` 當 JSON 解析一次:檔存在但解析不了、或解析出來不是物件 → 這次判定為「設定檔讀不了」(`load_platforms` 遇到壞 JSON 會印一句警告後自己退回單一預設,不會丟錯,所以不能靠它的例外判斷);解析得了才把解析結果交給 `load_platforms(專案根, cfg=解析結果)`(用它既有的 `cfg` 參數,不讓它再讀一次檔),★一次判定裡只呼叫一次★,結果給每條配方共用。呼叫時暫時接走它印到標準錯誤的警告;它丟出任何例外(內容寫錯,例如兩個平台沒寫預設、`root` 是 null)→ 同樣判定為「設定檔讀不了」,原因取例外訊息或接走的第一句警告。
- 配方的 `platform` 有值就用它,否則用設定的預設平台;平台不在設定裡 → 那條記「平台不在設定裡」。

### 3. 寫入時提醒(kill-add)

- 在判重之後、真正寫入之前,對「這次實際要寫進去的那一條」跑判斷函式:新增就是新組的配方;只更新 `--covers` 就是既有那一條(用它自己的 `platform`)。被判重擋下的情況不跑、不印。
- 不是 `ok` 就在標準錯誤印一行提醒,字面照狀態:`hits`「這條配方的原文在 <file> 出現 N 次;guard kill 跑到它會判 drifted」、`missing`/`undecodable`「<file> 讀不到(<原因>);guard kill 跑到它會判 drifted 或讀檔出錯」、`outside`「<file> 解析後跑出 repo;guard kill 會擋在圍欄外(判 error)」、`malformed`「配方欄位格式不對」;每行結尾接可以直接貼的修法「修法:lumos guard kill-rm <節點> --id <短身分>,照現在的程式改寫後再 kill-add」。然後照舊寫入:標準輸出跟沒有這條提醒時逐字相同、標準錯誤只多這一行、回傳碼不變。
- 設定檔讀不了、平台不在設定裡、平台根不存在或不在 git repo:印一行「⚠ 提醒:<原因>,沒驗原文」,照舊寫入(既有測試 `t_guard_kill_log_new_fields` 用設定裡沒有的平台宣告配方,要照舊能寫)。

### 4. 移除配方(kill-rm,新)

- `lumos guard kill-rm <節點> --id <短身分>`:短身分至少 8 個十六進位字元,不合就擋下、rc2(避免一兩個字元誤刪);在那篇的配方裡(含格式壞的元素)用共用身分函式找身分以它開頭的:零條 → 擋下;對到的全部是同一個完整身分(手改造成的完全重複)→ 一起移除;對到不同完整身分的多條 → 擋下並列出候選的完整身分。同檔原子寫入(同 kill-add 的寫法)。
- 移除前在標準輸出印出被移除那條的完整內容(platform、covers、note、test 等全部欄位),以及一行照它改寫後重新宣告的 kill-add 範本(原文那一欄留給人照現在的程式填),讓修法不會丟掉舊配方的設定。
- `[kill:recipes]` 標記掛在合約的 KEY 行上:移除之後,如果剩下的配方沒有任何一條的 invariant 還對得到那一行,就把那一行的標記拿掉;還有別的配方對得到就留著。
- 不刪 kill-log 的舊紀錄(那是歷史帳;背書計算本來就只認筆記現有的配方)。

### 5. 健康檢查新一段 P2

- 放在 P 段之後,標題「殺傷力配方的原文還對不對得上程式(提醒,不擋)」。專案根用 doctor 既有、P 段同一個 `repo_root` 變數;找不到(沒有 docs/)就印「這個專案沒有 docs/ 資料夾,跳過」。
- 跳過的節點逐字照 P 段:`type` 是 verification、或 `status` 去頭尾空白後是 superseded、stale。其餘節點用已讀進來的開頭欄位篩,有 `kill_recipes` 欄才讀。
- 列出的項目:
  - 某平台根不存在或不在 git repo:那個平台只列一條「平台 <名> 的根找不到(<路徑>),它底下 N 條配方沒驗」,不逐條列。
  - 配方的平台不在設定裡:那條列「平台 <名> 不在設定裡,沒驗」。
  - `kill_recipes` 解析不了:那篇列一條(說明照 `_kill_read_recipes` 回的錯)。
  - 每條配方判斷不是 `ok`:列「節點 → 平台:file:狀態細節(合約片段:invariant 前 30 字,跟 guard kill 輸出同長度;修法:lumos guard kill-rm <節點> --id <短身分>)」。
  - 設定檔讀不了:整段印一句「設定檔讀不了,這一段算不出來,先跳過」。
- 用 `warn_soft` 印(不動 doctor 的回傳碼,一般與 `--strict` 都一樣;預設每段最多列 3 條,`--verbose` 或 `--ci` 全列);有列出項目時,照 doctor 既有各段的做法在事件清單加 `{"gate": "check-p2", "kind": "warned", ...}`(帶列出的節點);事件清單照既有做法只在 doctor 以 `--ci` 跑時寫進治理帳(工具鏈 CI 每次推送都跑 `lumos doctor --ci`);閘名 `check-p2` 登記進 `_KNOWN_GATES`。全部對得上用 `ok()` 印「殺傷力配方的原文都對得上」;沒有任何配方印「沒有殺傷力配方」。
- 每一條配方、每一篇筆記的處理各自包在例外保護裡:一條出錯只列那一條「這條判不了:<原因>」,不讓整段失效;整段外層再包一層,真的出錯印「這一段算不出來」。

## 條款

- [S1] 當 `lumos guard kill-add` 實際要寫進去的配方原文出現 0 次、2 次以上、讀不到、讀不成 UTF-8、路徑解析後跑出 repo 或欄位格式不對時,應在標準錯誤多印恰好一行照狀態的提醒(讀設定時接走的警告不另外印)(含可直接貼的 kill-rm 修法)並照舊寫入,標準輸出與回傳碼跟沒有這條提醒時相同;恰好 1 次時應不印;被判重擋下時應不印 [test:t_guard_kill_add_warns_drifted_recipe]
- [S2] 當只更新 `--covers` 時,kill-add 應用既有那一條自己的平台驗原文;當設定檔是壞 JSON、不是物件、內容讓 `load_platforms` 丟例外、平台不在設定裡或平台根找不到時,應印「沒驗原文」的提醒並照舊寫入、回傳碼跟現在相同 [test:t_guard_kill_add_warns_drifted_recipe]
- [S3] 當 P2 段遇到配方失配、讀不到、讀不成 UTF-8、跑出 repo、格式不對、平台不在設定裡、整欄解析不了時(同一篇裡好壞配方混在一起也一樣),應各自列出那條(含實際次數或原因與 kill-rm 修法),以 `--ci` 跑時記 `check-p2` 事件,而且 doctor 在一般與 `--strict` 模式的回傳碼都不受影響;verification 型、superseded、stale 節點的配方應不列 [test:t_doctor_kill_recipe_drift]
- [S4] 當配方都對得上時,P2 應印「殺傷力配方的原文都對得上」;沒有任何配方時應印「沒有殺傷力配方」;設定檔是壞 JSON 時應印「這一段算不出來」;某平台根找不到時應只列那個平台一條 [test:t_doctor_kill_recipe_drift]
- [S5] 新判斷函式對同一批題目(平台根是子資料夾、平台根是 repo 頂、repo 內相對符號連結、絕對路徑符號連結、相對連結指向絕對連結、`file` 是絕對路徑、`..` 爬出 repo 頂再爬回來、跑出 repo、0 次、多次、非 UTF-8)的判定,應跟真跑 `lumos guard kill` 的結果一一對應(非 UTF-8 那格 guard kill 現在是程式出錯、回傳碼 1) [test:t_kill_recipe_check_matches_guard_kill]
- [S6] `lumos guard kill-rm` 應只移除短身分對到的那一條(或對到的全部是同一完整身分的重複時一起移除)、原子寫入,移除前印出那條完整內容與 kill-add 範本;格式壞的配方也移得掉;移除後沒有任何配方對得到的 KEY 行應拿掉 `[kill:recipes]` 標記,還有配方對得到的應保留;短身分不到 8 個十六進位字元、對到零條、或對到不同完整身分的多條時應擋下回 2、筆記不變 [test:t_guard_kill_rm]
- [S7] `cmd_guard_kill` 的程式不應被這次改動碰到;既有 drifted 的說明字面(「old 命中 N 次(需恰 1——配方漂移,重寫)」「file 開不了:」)與逃逸說明應照舊 [test:t_kill_recipe_check_matches_guard_kill]

## 回退

- revert 實作提交:doctor 少一段、kill-add 少一行提醒、kill-rm 指令消失;筆記與配方都沒被這次改動自動改過(kill-rm 是人下指令才動)。
- revert 之後,本計劃條款綁的 `[test:]` 會懸空(spec-trace 會唸),REVISIT 照樣到期——revert 那次要把本計劃 status 改成 superseded 或在〈實作紀錄〉記一句「已撤回、REVISIT 不必做」。

## 實務隱患

- **既有測試要一起改的**:`lumos guard` 的子指令清單有一條測試逐字釘住(它的註解寫明加子指令時照實更新那一行),加 `kill-rm` 要同一個提交更新;每個二層子指令都要在 `HELP_WHEN` 表有「什麼時候用」一列,`kill-rm` 要補。
- **既有測試**:kill-add 只多印一行、不擋,既有 `t_guard_kill`、`t_guard_kill_rc_precedence`、`t_guard_kill_log_new_fields` 用失配或逃逸配方宣告的 8 處照舊能寫;沒有逐字比對 kill-add 標準錯誤的既有測試(回滾席查過)。
- **本 repo 自己跑 doctor 的測試**:`t_doctor_summary_admits_soft_reminders` 在本 repo 真跑 doctor;本 repo 現在只有一條配方而且對得上,P2 不會多出軟段;日後失配也走 `warn_soft`、計數自洽。
- **量**:rtb 現有 73 條配方、工具鏈 1 條;每條讀一次目標檔全文(同一支檔被多條指到時只讀一次)。併發席實測 200MB 檔讀一次約 0.2 秒、本 repo doctor 全跑約 17 秒;實作時量一次 rtb 規模下 doctor 多花的時間記進〈實作紀錄〉。
- **讀到寫到一半的檔**:doctor 跑的同時有人在存檔,讀到半截內容會誤報一次,下次 doctor 就恢復;只提醒,不處理。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀本機檔,不連網
- 已排除:不可逆:多一行提醒、一段健康檢查、一個人下指令才動的移除指令;revert 就回得去,移除的配方可從 git 歷史找回
- 已排除:守衛面:不擋任何推送、提交或宣告,guard kill 本身不改

## 誠實界線

- 只驗「原文還找得到、而且只有一處」,不驗套用壞法之後測試還會不會翻紅(那要真跑 guard kill)。原文還在、但程式語意變了、壞法已經打不到合約,這段看不出來。
- 讀的是工作目錄的檔(包含沒提交的改動);guard kill 讀的是隔離工作樹裡檢出的提交版本。所以照提醒改寫配方、P2 轉綠之後,要先提交程式與筆記,再跑 `lumos guard kill <節點>` 確認真的殺得掉。
- 不擋推送:失配照樣推得出去,只是每次健康檢查都會唸。
- 落點:程式說明寫進 [[Systems/guard-kill]](kill-rm 用法、P2 段、判斷函式跟 guard kill 的對照);skill 裡提到 kill-add 的三處(`skills/lumos-project-notes/reference.md` 的指令表、`commands/06-代碼審與推送.md`、`commands/INDEX.md`)各補 kill-rm;kill-add 的 `--file` 說明字串從「相對配方平台 root」改成「相對配方平台所在 repo 的最上層」(guard kill 實際就是這樣算);[[Projects/漂移防治路線圖_計劃]] 的 1a 上線後改成「已上線」。

## 實作紀錄

(實作時補)

## 審計修正紀錄

- 前掃(2026-10-01):21 條命中全改進真檔;核心改動(平台根、guard kill 不改、kill-add 只提醒、新函式自己的狀態)交 r1。卷證 `governance/review-reports/殺傷力配方失配提醒/r1-intake.md`。
- r1(2026-10-01,6 席:正確性 opus、邊界、接手、回滾、併發、架構對齊 sonnet):30 條/blocking 8/全折。
  - 基準改成平台根所在 repo 的最上層,加對照測試釘兩邊判法(三席;例:平台根是 `.maestro/`、`--file prod.py` → 原稿判對得上、guard kill 判斷線,改後一致,S5)。
  - 設定檔先自己解析(三席:`load_platforms` 遇壞 JSON 不丟錯、退回預設,原稿「讀不了」走不到,S4)。
  - 新增 kill-rm(接手席:提醒叫人改寫,但配方身分含原文、舊的刪不掉,S6)。
  - 只更新 covers 時用既有那條的平台(正確性席實跑重現假提醒,S2)。
  - RETIRE-IF 改看 `check-p2` 事件(接手席:提醒只印不記、量不到)。
  - 另折:提醒字面照狀態、只讀一般檔、平台根找不到只列一條、型別先判、設定只讀一次、量改 73 條、回退補懸空處理、REVISIT 門檻、先提交再跑 guard kill。
  - 鏡像核對(同日)補:絕對路徑符號連結照 guard kill 歸 outside;kill-rm 改收短身分、印可直接貼的修法;`[kill:recipes]` 標記逐 KEY 行處理;`check-p2` 只在 `--ci` 落帳並登記閘名;kill-add 輸出契約(標準輸出不變、標準錯誤恰多一行);延期只准一次;設定須是物件;`--file` 說明字串一起改。
- r2(2026-10-01,5 席全新:正確性 opus、邊界、接手、回滾、架構對齊 sonnet):18 條/blocking 12/全折。
  - 路徑改用模擬 guard kill 工作樹的小解析器(正確性席實跑三種漏網:`file` 絕對路徑、`..` 爬出再爬回、相對連結指向絕對連結;第 1 輪只補了絕對路徑連結,S5 補格)。
  - 設定交給 `load_platforms` 的 `cfg` 參數、接走警告、例外一律當讀不了(三席:內容寫錯會讓 kill-add 崩潰不寫入,比現在退步,S2)。
  - kill-rm 加最短長度、重複一起移除、格式壞的也有身分、移除前印完整內容與範本(兩席:修法會丟設定、壞配方走到死路,S6)。
  - RETIRE-IF 改看兩次以上的 rtb 與另一消費專案回報(接手席:CI 事件不留存、工具鏈只有 1 條配方,條件恆成立)。
  - 另折:子指令清單測試與 HELP_WHEN 一起改;skill 三處落點;身分的節點字串寫死。

