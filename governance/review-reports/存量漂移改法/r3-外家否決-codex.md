severity: major

## F1 指紋檢查攔不住無鎖寫入者先寫後被覆蓋
severity: major
blocking: 是 — 不改，並行的 `decision-add`、`guard bind` 或手動寫入仍會被 fix 用舊內容整篇覆蓋。
引句:「指紋不同表示有不拿鎖的寫入者在中間改過,不還原、回 2 並印兩個版本的指紋讓人處理」
file: `scripts/lumos:14695`
file: `scripts/lumos:15435`

1. fix 在鎖內讀到版本 A、算出新內容 A′；無鎖的 `decision-add` 隨後把同檔寫成 B；fix 再呼叫 `atomic_write_verify(path, A′, …)`。
2. `atomic_write_verify` 雖重新讀 B，卻只取它的 lint 指紋，沒有比較 B 是否仍等於 A，最後直接以 A′ 執行 `os.replace`。
3. 寫後磁碟內容正是 A′，所以 spec 的「改後指紋」檢查完全看不見被覆蓋的 B。這不是只發生在還原階段；資料在第一次取代時已經遺失。
4. 寫入前必須以原文指紋做 compare-and-swap，或讓所有同檔寫入入口共用同一把鎖。

## F2 以發現消失作成功判準會接受只改狀態的殘缺修復
severity: major
blocking: 是 — 不改，c2、c3、c5 都能在必要正文或預告句未改時被記成修復成功。
引句:「寫完之後再從磁碟重讀、重建圖譜物件、跑同一支判定,確認這一筆已處理」
file: `scripts/lumos:26078`
file: `scripts/lumos:26109`
file: `scripts/lumos:26122`

1. c2 只對 `status` 為 open/doing 的 Issue 產生；只改成 done、漏加結案說明，c2 就消失。
2. c3 只對 pending 驗證產生；只改 status、漏加正文狀態說明，c3 就消失。
3. c5 只對 pending 守衛產生；只改成 pass、漏同步標籤與四種預告句，c5 就消失，並會轉成新的 c1。
4. 第 1 節的成功 oracle 必須逐種類驗完整 postcondition；c5 還要拒絕產生 c1，不能只驗原種類不見。

## F3 c4 允許把欄位鍵與 YAML 結構一起替換
severity: major
blocking: 是 — 不改，人給的合法參數能刪掉 `valid_under` 或改成另一個欄位，工具仍宣告成功。
引句:「直接在原始文字上換掉那一段,欄位的寫法(單行、清單、多行區塊)、其他項目與排版一字不動」
file: `scripts/lumos:14695`

1. spec 只禁止空 `--old` 與含換行的 `--new`，沒有禁止 `--old` 涵蓋欄位鍵、縮排、清單標記或換行。
2. 對 `valid_under: 未提交` 執行 `--old "valid_under: 未提交" --new "custom: 已提交"`，命中恰一次、new 不含禁詞也不含換行，但結果直接刪除了 `valid_under`。
3. `atomic_write_verify` 只保證 frontmatter 可解析、沒有新增解析 lint；合法的另一個鍵不會被它擋下。
4. c4 必須把命中限制在解析後的值區段，並在寫後斷言 `valid_under` 的鍵、容器形狀、項目數及命中項以外的原始位元完全不變。

## F4 c4 的成功判準能在同一項仍含禁詞時放行
severity: major
blocking: 是 — 不改，fix 能回 0、寫修復帳，但同一筆 c4 仍會被 scan 列出。
引句:「c4 被換的那一段不再含那三個詞(同一欄別項還含是別筆)」
file: `scripts/lumos:26099`

1. 令同一項為 `valid_under: 未提交且 uncommitted`，以 `--old "未提交" --new "已提交"` 修復。
2. 被替換的新片段確實不含三個詞，卻仍在同一項留下 `uncommitted`；現有偵測會繼續產生 c4。
3. spec 又要求其他項仍含禁詞時不得算這筆失敗，因此不能只檢查整欄，也不能只檢查新片段。
4. 必須先定義「項目」在單行、清單、多行區塊的定位方式，再驗被命中的那一項已完全不含三詞。

## F5 跨型別收案集合會把非法 Issue 狀態誤認成結案
severity: major
blocking: 是 — 不改，`lumos set` 能讓仍非合法結案態的 Issue 收到刪除回頭條件的錯誤指示。
引句:「那篇是 Issue、值在 `QUERY_CLOSED_STATUSES`(set 不驗類型值域,所以同時看類型)」
file: `scripts/lumos:5244`
file: `scripts/lumos:13702`

1. Issue 的合法結案值只有 done、resolved、wontfix。
2. `QUERY_CLOSED_STATUSES` 是跨型別集合，另含 pass、superseded、abandoned；這些分屬 Verification、Project 或守衛語意。
3. `set` 不驗型別值域，所以 `lumos set <Issue> status pass` 會成功；照 spec，E5 與 `_issue_close_revisits` 隨即把它標成「這篇 Issue 已結案」。
4. 判定必須使用 Issue 專屬結案集合，不能以「type 是 Issue」加跨型別集合代替。

## F6 c2 結案入口漏掉既有的 Issue 結案橫幅合約
severity: major
blocking: 是 — 不改，body-only 讀者仍會把已修好的症狀與根因當成現況。
引句:「status 用 `edit_fm_scalar` + `edit_fm_sync_status_tag` 改;正文最後加一行」
file: `docs/lumos-toolchain-knowledge/Projects/宣稱級時間戳_計劃.md:18`
file: `docs/lumos-toolchain-knowledge/Issues/寫下風險當成處理風險.md:25`

1. 圖譜既有鐵則要求已結案 Issue 在正文第一段放結案橫幅，並明示下方排查紀錄不是現況。
2. spec 只在正文末尾追加結案行；`show --body-only` 或直接從標題往下讀時，舊症狀仍先出現。
3. 這正是既有事故所記的錯讀形態。c2 `--close` 必須建立或更新頂部橫幅，末尾稽核行不能取代它。

## F7 [S2] 與第 2 節對既有轉正日期的優先序互相衝突
severity: major
blocking: 是 — 不改，同一篇守衛可依實作者採信哪一段而寫出不同歷史日期。
引句:「日期依序取 `--date`、正文手補的已轉正日期、守衛紀錄第一次變成 pass 的提交日期」
file: `scripts/lumos:12022`

1. 第 2 節明定第二順位同時包含正文手補日期與摘要 WHY 行尾的日期，兩處不同還要擋下。
2. [S2] 的完整優先序漏掉摘要 WHY 日期，直接從正文跳到 git 提交日期。
3. 只有 WHY 帶日期時，第 2 節要求沿用該日期，[S2] 卻要求使用 git 日期；shallow repo 下甚至一邊成功、一邊回 2。
4. [S2] 與其測試必須補上 WHY 日期及兩處衝突案例，否則驗收條款會釘住錯誤行為。

## F8 秒級 `ts` 不是可安全決定最新表態的全序
severity: major
blocking: 是 — 不改，表態合併後能選中舊關係清單，畸形紀錄也能讓 scan、check、doctor 共用路徑失敗。
引句:「取 `ts` 最新的那一筆,它的 `related` 涵蓋現在的清單(現在的是它的子集)才算已表態」
file: `scripts/lumos:27051`

1. spec 將 `ts` 精度限定到秒；同一秒內的兩筆表態沒有先後，而第 7 節又明定不能依檔內順序。
2. 多工作樹合併後，兩筆同秒、不同 `related` 時沒有規則可決定哪筆代表最後決定；任取一筆會錯誤豁免或重列。
3. 現有 loader 只驗 path 與 kind，會接受 `ts: null`、物件、壞日期等手改紀錄；spec 只規定壞 `related`，沒有規定壞 `ts` 的 fail-safe 行為。
4. 必須定義格式與時區、畸形值處置及平手規則；安全的平手處置是視為未表態並重新列出。

## F9 全圖譜重建可能超過 30 秒並讓活鎖被接手
severity: major
blocking: 是 — 不改，大型或慢磁碟圖譜上兩個守規矩的 fix 也能同時進入寫入區。
引句:「鎖內重新載入整個圖譜約一秒內(工具鏈 590 篇)」
file: `scripts/lumos:620`
file: `scripts/lumos:14714`
file: `scripts/lumos:26078`
file: `scripts/lumos:32781`

1. `Env(vault)` 會遞迴讀全庫；`_drift_state_findings(..., only=...)` 又在套用 `only` 前先建立全圖型別索引。
2. spec 在寫前與寫後都重建圖譜，其中至少一次位於鎖內；590 篇的一秒量測不是消費端規模上限。
3. 寫入鎖的 mtime 超過 30 秒就會被 `_excl_lock_try` 原子接手，沒有 heartbeat 或持有程序存活檢查。
4. 當鎖內重建超過 30 秒，第二個程序會移走仍在使用的鎖並進入臨界區，互斥保證失效。鎖租期必須覆蓋最壞工作量或改成存活檢查／heartbeat。

## F10 寫前符號連結檢查仍有 TOCTOU 與硬連結穿透
severity: major
blocking: 是 — 不改，陌生 repo 仍能讓帳本追加寫到 repo 外檔案。
引句:「寫之前檢查帳檔、以及它解析後的真實路徑要在 repo 根底下、本身與上層目錄都不是符號連結」
file: `scripts/lumos:8511`

1. 現有 `_jsonl_append_verified` 在檢查完成後才以一般 `open(path, "a")` 開檔；一般 open 會跟隨開啟當下的符號連結。
2. 另一個程序在檢查與 open 之間換成符號連結時，前置檢查結果已失效。
3. repo 內若放的是指向外部 inode 的硬連結，`resolve()`、`is_symlink()` 與上層檢查全部通過，append 仍會修改外部檔案。
4. 安全承諾需要在開啟動作本身使用 no-follow／dirfd 邊界並以 `fstat` 驗證取得的描述符；單獨的路徑預檢不能成立。

## 逐節覆核

### 開頭、PRIOR-ART、RETIRE-IF

已讀,無 finding  
引句:「最小解在工具鏈自己這一層。①c1 的改句邏輯現成」

### 範圍

已讀,無 finding  
引句:「rtb 那 24 筆由 rtb 會談用新指令修(本計劃只負責工具)」

### 做法第 1–8 節與條款

已讀；問題分別列於 F1–F10。

### 做法第 9 節

已讀,無 finding  
引句:「同步改的筆記與文件:Systems/存量漂移守衛」

### 回退

已讀,無 finding  
引句:「修復帳:回退後留著無害,舊版 lumos 不認得這個檔」

### 實務隱患逐類

1. 守衛面：有，F2、F4、F5 會假成功、漏報或給錯處置。
2. 不可逆：有，F1 能覆蓋尚未提交、git 無法找回的並行修改。
3. 併發：有，F1、F8、F9。
4. 效能：有，F9；現有量測只涵蓋 590 篇。
5. 安全：有，F10。
6. 向後相容：無新增 finding；舊 c2/c3 表態重列與舊版多跑測試已明示，額外欄位也符合現有寬鬆讀法。
7. 金流：無；設計只改本機筆記與帳檔。
8. 對外送出：無；只讀本機 git，沒有網路或外部服務入口。

### 誠實界線

已讀,無額外 finding  
引句:「在 [[Projects/舊句偵測實驗_計劃]] 做完之前,這一種漂移沒有工具路也沒有防線」

### 合約候選

已讀,無 finding  
引句:「(設計審過閘後填。)」

### 審計修正紀錄

已讀,無額外 finding；未讀任何 r1/r2 席報告。  
引句:「已補:c1 推日期只在沒有 `--date` 也沒有已寫日期時才查 git」

總結：最高為重大，共 10 條會擋實作。