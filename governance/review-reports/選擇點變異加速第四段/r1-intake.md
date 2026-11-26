# 選擇點變異加速第四段 r1 收貨紀錄

preflight-4: ran

## 前掃(凍結前,sonnet 一席,固定四項清單;22 條命中)

存在類與用詞類直接修真檔,不算 findings:〈用詞〉補「事件行」的切法與三個例子(含 `$`、巢狀,標明探針沒測到)、引用「合併道」「快篩結果四類」「斷路器停用」的定義處;「冷卻期」改成「斷路器停用期間」;預期效益改寫主詞。

語意類(修真檔並逐條留痕,修改前 → 後):

1. 初始化腳本寫檔時機與指令過長判斷互相矛盾:前「其他條件都過、時限門之前寫檔」又「過長判斷帶同一個參數」→ 後:先算路徑做過長判斷,其餘條件過了、時限門之前才寫,寫失敗 `sh["init"]` 為 None。
2. `merge_back` 內部順序沒定:前「通過層加掛住層(依序)」又「各段照原排序」→ 後:通過層全部在前、掛住層在後,各層內照原排序;S2 補一案(原排序掛住在前、通過在後)。
3. `c.merge_back` 沒說要清:→ 後:`_kill_merge_screen` 一開頭跟 `merge_failed` 一起清空;S2 補「前一壞法排過、下一個套不上」那案。
4. 證據口徑:前「快篩逾時的 15 個裡 13 個判殺掉」(15 含零案例)→ 後:重新從治理帳拆:逾時 11 個裡 10 個判殺掉、1 個跑不出結果;零案例 4 個裡 3 殺 1 存活。
5. 總數加不起來(130+10≠142):重新拆帳:通過 45、有失敗 66、編不過 6、沒跑乾淨 15、斷路器停用期間 10,合計 142(原數字漏算第一筆)。
6. 事件排序對哪些沒跑乾淨原因生效沒寫清、S2 只測逾時 → 後:寫明不分原因;S2 補零案例帶 FAILED 那案。
7. `_choice_merge_cmd` 兩個呼叫點沒列 → 後:寫明 `_kill_merge_ready` 過長判斷與 `_kill_merge_base` 都傳,取 `sh.get("init")`。
8. 斷路器啟用中不計時要不要歸零 streak 沒寫 → 後:不計也不歸零。
9. `--keep-worktree` 時腳本會留下 → 後:〈用詞〉與〈實務隱患〉寫明跟現場一起留。
10. 既有單元測試用 `SimpleNamespace(wt=<暫存>)` 呼叫 `_kill_merge_ready`,腳本會寫到系統暫存根 → 後:〈落點〉列「同一提交改的既有測試」,`wt` 改成 `<暫存>/wt`。
11. 假 Gradle 不會印事件行、計劃沒提 → 後:〈落點〉寫明加 `__events__` 鍵,只在合併且帶 `--init-script` 時印,既有逾時、斷路器測試語意不變。

④ 其餘驗證屬實(不用改):逐支遇單支逾時判測試掛住並停(`_CHOICE_STOP_ON`);`_kill_run` 逾時保留輸出;上層資料夾是 mkdtemp、收尾刪掉;`_kill_merge_ready` 時 `c.wt` 可用;插入位置在 `cmd[shape["e"]:]` 之前不切破引號;`merge_unclean` 只記計數類;合併基準與快篩共用 `_kill_merge_base` 組的指令;`merge_why` 讀端只當字典讀。

沒有動到核心裁定(兩條 WHY 的決定沒變,只補口徑、清空時機與測試落點)。

## 收貨(四席齊了才落地;報告從逐字稿原樣存)

- 四份 quote-check 全錨、refcheck 全 ok。通才、邊界兩份第一次交回沒有「引句:」行,退回原席只補引句、內容與等級不動後重交;正確性那份只跑 `report-normalize --write` 搬等級行。
- 編號:通才 g1–g6、正確性 c1–c5、邊界 b1–b11、架構對齊 a1–a7(照各報告 severity 行的順序)。

## 先查世界

- PRIOR-ART:斷路器依失敗種類分門檻——redress 每類錯誤各自門檻(https://aponysus.github.io/redress/concepts/circuit-breakers)、Azure 斷路器依例外種類調整策略(https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)。採用:「跑到測試後逾時」另一個計數,門檻 15(c1、b8)。
- PRIOR-ART:Gradle 初始化腳本相容性——設定快取把初始化腳本當輸入、Isolated Projects 先要相容設定快取(https://docs.gradle.org/current/userguide/isolated_projects.html);論壇不建議 `allprojects` 跨專案設定(https://discuss.gradle.org/t/gradle-init-script-and-beforeproject-allprojects/51594)。採用:不做版本判斷,帶腳本不通過就不帶重試(g4、b2)。
- PRIOR-ART:加引號——專案既有 `_run_cmd_expand`(POSIX shlex.quote、Windows list2cmdline);照用(a4、b4)。

## 發現與處置

| id | 席 | 一句 | 處置 |
|---|---|---|---|
| g1 | 通才 1 | 既有測試改 wt 形狀會讓結果資料夾跑出工作樹 | 折:改由 `_isolated_worktree` 給 `scratch`,既有測試不給、不改 |
| g2 | 通才 2 | 假 Gradle 沒 flush,逾時案讀不到事件 | 折:落點寫明 `flush=True` |
| g3 | 通才 3 | 事件行沒要求頂格、可被測試輸出騙 | 折:`_CHOICE_MERGE_EVENT_RE` 行首不得空白;隱患寫明殘餘 |
| g4 | 通才 4 | 腳本讓合併基準不通過時整平台退回逐支 | 折:不帶腳本重試一次、`merge_init_off` |
| g5 | 通才 5 | 舊計劃句子沒標被取代 | 折:落點列三處舊句子 |
| g6 | 通才 6 | 預期效益兩個前提沒實測 | 折:改寫預期效益、標明沒實測 |
| c1 | 正確性 1 | 跑到測試的逾時完全不計,工具上限不夠時沒有煞車 | 折:另一個計數,門檻 15 |
| c2 | 正確性 2 | 通過層排在掛住層前沒理由 | 折:掛住層移到通過層前、寫排序理由 |
| c3 | 正確性 3 | 截斷時開始沒結束會被判掛住 | 折:有截斷標記時進未知層 |
| c4 | 正確性 4 | 舊條款沒標被取代 | 折:同 g5 |
| c5 | 正確性 5 | 假 Gradle 沒 flush | 折:同 g2 |
| b1 | 邊界 1 | 既有測試會把腳本寫到系統暫存根 | 折:同 g1 |
| b2 | 邊界 2 | 腳本被拒沒有降級 | 折:同 g4 |
| b3 | 邊界 3 | 專案設的 events 缺 started、-q 的部分覆蓋 | 折:隱患寫明部分覆蓋時的行為 |
| b4 | 邊界 4 | Windows 引號自創、路徑含 % | 折:沿用 list2cmdline;含 `_WIN_CMD_SPECIAL` 就不帶 |
| b5 | 邊界 5 | 測試名含 ` > ` 解錯、巢狀三段式衝突 | 折:在第一個 ` > ` 切;拿掉三段式例子 |
| b6 | 邊界 6 | Windows 主控台編碼讓中文名對不到 | 放行(見下) |
| b7 | 邊界 7 | 通過層排在掛住層前白跑 | 折:同 c2 |
| b8 | 邊界 8 | 一律不計沒有上限 | 折:同 c1 |
| b9 | 邊界 9 | S3 少混合序列與停用中試探案 | 折:S3 補兩案 |
| b10 | 邊界 10 | 假 Gradle 沒 flush | 折:同 g2 |
| b11 | 邊界 11 | 停用期間 10 個回 30 秒以內偏樂觀 | 折:預期效益改成照沒跑乾淨那類算 |
| a1 | 架構 1-1 | `_kill_merge_ready` 加了寫檔副作用 | 折:寫檔移到 `_kill_merge_base` |
| a2 | 架構 1-2 | 原因決定權分在 classify 與 screen | 折:改在 classify 一處決定 |
| a3 | 架構 2 | 寫檔失敗靜默 | 折:印一行到標準錯誤 |
| a4 | 架構 3-1 | Windows 雙引號是第二套加引號 | 折:沿用 `_run_cmd_expand` 那套 |
| a5 | 架構 3-2 | 名稱比對另立一套 | 折:沿用 `_choice_merge_fullname`、`_choice_merge_hits` |
| a6 | 架構 4-1 | 新 merge_why 字樣沒登記規格閘 | 折:落點加規格閘 |
| a7 | 架構 4-2 | 缺被取代註記 | 折:同 g5 |

- b6 放行理由:只影響逐支順序、不影響判定;本機沒有 Windows 環境可實測;寫進〈實務隱患〉。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| c1 | 讀 `_choice_merge_screen_cap`(合併基準 × 5)與第一段計劃「增量編譯多久沒量過」 | HIT:上限不含壞法重編時間,原稿完全不計就沒有煞車 |
| a4 | 讀 `_run_cmd_expand` 的 list2cmdline 分支 | HIT:既有一套,原稿寫雙引號 |
| g2 | 讀 `_CKM_GRADLE` 的 print 與 `_kill_proc_group` SIGKILL | HIT:沒 flush |
| c3 | 讀 `_kill_cap` 截斷標記 `...[truncated` | HIT |
