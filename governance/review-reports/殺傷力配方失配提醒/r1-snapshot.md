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

白話:殺傷力配方是「故意把程式哪一段改壞,看綁定的合約測試會不會翻紅」的說明書,寫在筆記開頭的 `kill_recipes` 欄位,每條指名一支檔、要找的原文 `old`、要換成的壞法 `new`。程式後來重構,原文找不到(或出現好幾次),這條配方就失效了——等於合約測試的自我檢查斷線,而且沒人知道,因為只有手動跑 `lumos guard kill` 才會發現。這份計劃做最小的兩件事:寫入配方時就驗原文是不是恰好出現一次,不是就提醒(照舊寫入,保留既有「宣告不擋、跑時擋」的設計);健康檢查每次逐條數原文出現幾次,失配的列出來提醒。先不擋推送,guard kill 本身不改。

依據:
- rtb 會談 2026-10-01 全圖譜漂移巡檢(rtb 提交 df6ff87,逐筆清單在 rtb 的 `governance/audits/2026-10-01-drift-sweep/findings.md`,形狀表在 rtb 的 `Issues/存量筆記漂移等工具修復`〈形狀與修法〉):形狀 K1「殺傷力配方失配」10 條——執行迴圈 5 條、提案收件口 4 條原文出現 0 次(程式重構過)、Mock-DSP 1 條出現 4 次;10 條全掛在 ★INVARIANT★ 上。巡檢者逐條驗過。
- 工具鏈現況(2026-10-01 編排者讀碼,另派不知情的查證席照原始問題重查,結論相同):唯一數原文出現次數的地方在 `cmd_guard_kill` 裡,而且是建好隔離工作樹、跑完基準測試之後才數;`cmd_guard_kill_add` 寫入配方時不開那支檔;doctor、推送前掛鉤、CI、pitfalls、contracts、guard list/audit/trace 都不讀配方內容。圖譜裡沒有討論過「配方靜態失配檢查」(沒有提案、也沒有被否決)。
- Enzo 2026-10-01 說「好」,先從 K1 開始。

PRIOR-ART: ①最小解在既有層——`cmd_guard_kill` 已經有「原文恰好一次,否則判 drifted」的判準,本案的新判斷用同一種讀法(文字模式 UTF-8)、同一種圍欄(realpath 要在平台根內)與同一個次數條件,但不改 guard kill 本身(它的圍欄、錯誤說明與回傳碼有既有合約與測試,抽共用會改到它的行為,前置掃描逐項證實);健康檢查新段落照 doctor P 段(筆記提到的程式檔路徑還在不在)的形狀:讀工作目錄、只提醒、預設每段最多列 3 條 ②世界解過——突變測試工具(mutmut、Stryker)的變異點是工具從程式自動產生、每次重算,不會有「配方失配」這種存量;本專案的配方是人寫的宣告式壞法(guard-kill 的設計取捨),所以要自己補「宣告跟程式還對不對得上」的檢查,形狀等同 doctor 的 Check N「存查詢不存答案、每次重算比對」 ③裁定=borrow-design:借 guard kill 自己的 drifted 判準,原生實作。
RETIRE-IF: 健康檢查這一段連續 8 週在工具鏈與 rtb 都沒有列出任何失配(配方都健康、或配方被全部移除),而且寫入時那道提醒這段期間一次都沒印過;或推送時改成擋的另案上線、把這一段取代掉。成立就把 doctor 這一段撤掉(寫入時的提醒保留,它沒有維護成本)。
REVISIT:2026-10-15 看 rtb 那 10 條失配配方修了沒(請 rtb 會談回報 `lumos doctor --verbose` 的 P2 段輸出);全修完就開「推送時改到配方目標檔就擋」的另案,還有剩就照剩下的數字決定再等兩週或攤給人裁。

## 範圍

- 做:一支新判斷函式(只給 kill-add 與健康檢查用);`lumos guard kill-add` 寫入時對失配的配方印提醒(照舊寫入、回傳碼不變);`lumos doctor` 新一段 P2 逐條列失配配方(只提醒)。
- 不做:改 `cmd_guard_kill`(它的圍欄、讀檔、drifted 說明與回傳碼一律不動);推送時擋(另案,等 rtb 存量清完);kill-add 擋下失配配方(保留既有設計「宣告不擋、跑時擋」——既有測試 `t_guard_kill`、`t_guard_kill_rc_precedence` 刻意用 kill-add 宣告失配或逃逸的配方來測 guard kill 的判定);自動改寫配方;驗壞法還能不能讓測試翻紅(那要真跑 guard kill)。

## 做法

### 1. 判斷函式(新)

- 收(平台根、配方),回(狀態、細節);只讀工作目錄裡的檔,不碰 git:
  - 配方不是物件、或 `file`/`old` 不是字串 → `malformed`。
  - `os.path.realpath(平台根/file)` 不在平台根的 realpath 底下 → `outside`(不讀檔)。這跟 `cmd_guard_kill` 的圍欄同一種判法:平台根底下的符號連結,只要解析後還在根內就照讀。
  - 用文字模式、UTF-8 開檔讀全文(跟 guard kill 同樣的讀法,換行一樣會被正規化,所以兩邊數出的次數一致);開不了或讀不成 UTF-8(`OSError`、`ValueError`)→ `missing`,細節帶原因。
  - `全文.count(old)` 不是 1 → `hits`,細節帶實際次數(含 `old` 是空字串的情況,次數照 Python 的算法)。
  - 恰好 1 次 → `ok`。
- **平台根**:配方的 `platform` 欄有值就用它,否則用設定檔的預設平台;根 = `load_platforms(專案根)["platforms"][平台]["root"]`(專案根照 `_repo_root_from_env`,跟 guard kill 同一套)。設定檔讀不了、或平台不在設定裡,不呼叫判斷函式,由呼叫端各自處理(見下)。

### 2. 寫入時提醒(kill-add)

- 在配方組好之後、判重迴圈之前跑判斷函式;不是 `ok` 就在標準錯誤印一行「⚠ 提醒:這條配方的原文在 <file> <細節>;guard kill 跑到它時會判 drifted——先照現在的程式改寫原文再宣告」,然後照舊往下走(判重、寫入、回傳碼全部不變)。新增與只更新 `--covers` 兩條路都會經過這一步。
- 設定檔讀不了或平台不在設定裡:印一行「⚠ 提醒:平台 <名> 不在設定裡(或設定讀不了),沒驗原文」,照舊寫入(既有測試 `t_guard_kill_log_new_fields` 用設定裡沒有的平台宣告配方,要照舊能寫)。

### 3. 健康檢查新一段 P2

- 放在 P 段之後,標題「殺傷力配方的原文還對不對得上程式(提醒,不擋)」。
- 跳過的節點逐字照 P 段:`type` 是 verification、或 `status` 去頭尾空白後是 superseded、stale。其餘有 `kill_recipes` 欄的節點(用已讀進來的開頭欄位篩,沒有這個欄就不讀檔)才讀配方。
- `kill_recipes` 解析不了的節點列一條(說明照 `_kill_read_recipes` 回的錯);每條配方跑判斷函式,不是 `ok` 的列「節點 → 平台:file:狀態細節(合約片段:配方 invariant 前 30 字,跟 guard kill 輸出同長度)」。
- 設定檔讀不了:整段印一句「設定檔讀不了,這一段算不出來,先跳過」(比照 doctor 既有幾段的寫法);某條配方的平台不在設定裡:那條列「平台不在設定裡」。
- 用 `warn_soft`(不動 doctor 的回傳碼;預設每段最多列 3 條,`--verbose` 或 `--ci` 全列)。全部對得上印一行「殺傷力配方的原文都對得上」;沒有任何配方印「沒有殺傷力配方」。
- 整段包在例外保護裡:這一段自己出錯就印「這一段算不出來」,不讓整個 doctor 停掉。

## 條款

- [S1] 當 `lumos guard kill-add` 要寫的配方原文在目標檔出現 0 次、2 次以上、目標檔讀不了或路徑跑出平台根時,應印一行提醒並照舊寫入、回傳碼跟沒有這條提醒時相同;恰好 1 次時應不印這條提醒 [test:t_guard_kill_add_warns_drifted_recipe]
- [S2] 當 `lumos guard kill-add` 的平台不在設定裡或設定讀不了時,應印「沒驗原文」的提醒並照舊寫入 [test:t_guard_kill_add_warns_drifted_recipe]
- [S3] 當有 `kill_recipes` 的節點裡有配方失配、檔讀不了、路徑跑出平台根、格式不對或整欄解析不了時,doctor 的 P2 段應列出那條(含實際次數或原因),而且 doctor 在一般與 `--strict` 模式的回傳碼都不受影響;verification 型、superseded、stale 節點的配方應不列 [test:t_doctor_kill_recipe_drift]
- [S4] 當配方都對得上時,P2 段應印「殺傷力配方的原文都對得上」;沒有任何配方時應印「沒有殺傷力配方」;設定檔讀不了時應印「這一段算不出來」 [test:t_doctor_kill_recipe_drift]
- [S5] 當配方的 `file` 解析後跑出平台根時,判斷函式應不讀那支檔、回 outside;平台根底下、解析後仍在根內的符號連結應照讀 [test:t_kill_recipe_static_check_paths]
- [S6] 既有 `cmd_guard_kill` 與 `cmd_guard_kill_add` 的判定、輸出與回傳碼除了多一行提醒之外應不變 [test:t_guard_kill_rc_precedence]

## 回退

- revert 實作提交即可:doctor 少一段、kill-add 少一行提醒;筆記與配方都沒被改過。

## 實務隱患

- **既有測試**:kill-add 只多印一行、不擋,既有 `t_guard_kill`、`t_guard_kill_rc_precedence`、`t_guard_kill_log_new_fields` 用失配或逃逸配方宣告的 8 處照舊能寫;若有測試逐字比對 kill-add 的標準錯誤,實作時逐支看。
- **本 repo 自己跑 doctor 的測試**:`t_doctor_summary_admits_soft_reminders` 在本 repo 真跑 doctor;本 repo 現在只有一條配方而且對得上,P2 不會多出軟段;日後失配也會走 `warn_soft`、計數自洽。
- **大檔**:每條配方讀一次目標檔全文;工具鏈與 rtb 現況各十幾條配方,量級可忽略;實作時量一次 doctor 多花的時間記進〈實作紀錄〉。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀本機檔,不連網
- 已排除:不可逆:只多一行提醒與一段健康檢查,revert 就回得去
- 已排除:守衛面:不擋任何推送、提交或宣告,guard kill 本身不改

## 誠實界線

- 只驗「原文還找得到、而且只有一處」,不驗套用壞法之後測試還會不會翻紅(那要真跑 guard kill)。原文還在、但程式語意變了、壞法已經打不到合約,這段看不出來。
- 讀的是工作目錄的檔(包含沒提交的改動);guard kill 讀的是隔離工作樹裡檢出的提交版本,兩者在有未提交改動時可能不同。
- 不擋推送:失配照樣推得出去,只是每次健康檢查都會唸。

## 實作紀錄

(實作時補)

## 審計修正紀錄

(審查時補)
