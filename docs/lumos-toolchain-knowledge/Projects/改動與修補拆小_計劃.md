---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/pitfalls-code-loop
related:
  - "[[Verification/2026-10-14_修補大小與下一輪major回放]]"
  - "[[Projects/代碼審修復穩定性試行_計劃]]"
---
# 改動與修補拆小_計劃

代碼審常跑滿三輪仍有 major。帳本回放([[Verification/2026-10-14_修補大小與下一輪major回放]])顯示:第一輪改動越大越容易跑滿,每輪修補寫得越多下一輪越容易有 major;控制上一輪折入條數、第幾輪與分級,並排除舊報告裡植入的測試用假發現之後,修補行數仍有獨立的關係。這份計劃只做一件事:在編排者一定會看到的地方——`lumos loop next`——印出這次改動與上一輪修補的大小,太大時附一句建議。不擋、不改閘。

WHY:改動大小只在 `loop next` 印提示,不做回放子指令、不設前後比的撤除數字 [出處:2026-10-14 使用者裁;設計審 `改動與修補拆小` r1 四席、`修補大小上限試行` r1 四席] [因:手冊一行建議編排者碰不到;真實卷證有植入假發現、缺凍結材料、報告路徑指錯等,做成正式回放子指令要處理的資料清理很多;最近兩段四週跑滿比例 27% 與 69%,自然漂移遠大於要量的效果,前後比判不出] [不選:回放子指令加四週前後比;修復穩定性試行三案試硬上限;改處置閘或擋推送]
PRIOR-ART: Google Small CLs(https://google.github.io/eng-practices/review/developer/small-cls.html)主張小而自足的變更較易審、較易看出引入的 bug;本 repo `loop next` 首輪本來就印「主題既有節點」這類開審提醒,提示接在同一處;檔案切分沿用 `_patch_file_changes` 的檔頭狀態機、測試檔判斷沿用 `_nodehome_is_test`、簿記判斷沿用 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS`,不另寫第二套。
RETIRE-IF: 提示上線三個月(2027-01-14)內,編排者沒有任何一次在收貨紀錄或計劃裡記下「因提示拆案或改小修法」,或使用者覺得它是雜訊,就拿掉兩行提示(改動大小那行數字可以留)。

## 範圍

- 做:①`_patch_file_changes` 加一個可選參數,順便把每支檔的新增內容行收集出來;②`lumos loop next` 對代碼審迴圈印改動大小與上一輪修補大小,超過門檻附建議;③`reference.md` 說明這兩行提示與依據;④驗證筆記改寫成更新後的數字並作廢舊行。
- 不做:不擋推送、不改處置閘、必派席與三輪上限;不做回放子指令、不做前後比;設計審迴圈不印(凍結材料是整份文字,沒有新增行可數);修復穩定性試行的 S6 已撤案(`governance/review-reports/修補大小上限試行/r1-intake.md`)。

## 做法

- **收集新增行**:`_patch_file_changes` 加 `added_out=None`;給了一個 dict 時,在既有的檔頭狀態機裡,把 hunk 內以 `+` 開頭的行(去掉開頭的 `+`)依檔名附加進 `added_out[檔名]`。檔名照它既有的取法(`+++ b/`、改名、刪檔、引號路徑都已處理),hunk 內長得像檔頭的內容行照舊不當檔頭。不給參數時行為與輸出完全不變(資安席與回頭重讀都在用它)。
- **分類**:每支檔先看是不是簿記(`_BOOKKEEPING_FILES` 或以 `_BOOKKEEPING_DIRS` 開頭)——是就不算;再看是不是筆記(在本 repo 圖譜資料夾底下,沿用 `find_vault` 算出的相對路徑);再看是不是測試(`_nodehome_is_test`);其餘算程式。
- **首輪**(帳上還沒有這個迴圈的輪次,`--spec` 是 `.patch`):印一行「改動大小:這份凍結 patch 新增 N 行(程式 a、測試 b、筆記 c;簿記不算)」。程式加測試超過 300 行時,再印一行:「改動越大越容易跑滿三輪(帳本回放:第一輪新增 300 行以下的代碼審約四成跑滿,以上約三分之二);還沒派審前可以考慮拆案」。
- **第 N 輪**(N≥2,`--spec` 是 `.patch`,帳上第 N-1 輪有任一筆帶 `snapshot_path` 且讀得到):逐檔比較——這份 patch 每支檔的新增行,扣掉上一輪凍結 patch 同一支檔已有的同內容行(同檔內的多重集合相減),加總成「上一輪修補新增約 N 行(程式 a、測試 b、筆記 c)」。程式加測試超過 100 行時,再印一行:「修補越大下一輪越容易有 major(帳本回放:修補 47 行以下約三成,226 行以上約八成);派下一輪前可以再看能不能用更小的修法」。
- **讀不到就不印**:不是 `code-` 開頭的迴圈、`--spec` 不是 `.patch`、檔案讀不到、上一輪沒有凍結 patch——都不印大小提示,`loop next` 其他輸出與 rc 照舊。`--json` 多一個 `change_size` 欄位:`{"scope": "first"|"repair", "code": a, "test": b, "notes": c}`,讀不到為 `null`。
- **手冊**:`reference.md` 一段說明兩行提示的意思、門檻依據與「只是建議」;SKILL.md 第 2 步(`loop next`)那句加半句「首輪與續輪會印改動大小」。入口頁不寫日期與數字。
- **驗證筆記**:數字換成排除植入假發現之後的版本、補第一輪大小的分段表(300 行附近開始升高),舊的「併進修復穩定性試行」那行 WHY 與它的回頭條件標作廢、指向本計劃;內嵌的兩支分析腳本保留(一次性分析,不是產品工具),開頭註明。

## 驗收條款

- [S1] 當對代碼審迴圈首輪跑 `loop next --spec <凍結 patch>` 時,應 印改動大小那一行,程式、測試、筆記分開,簿記檔的新增行 應 不算 [test:t_loop_next_change_size_hint]
- [S2] 當首輪程式加測試超過 300 行時,應 多印拆案建議那一行;不超過時 應 不印 [test:t_loop_next_change_size_hint]
- [S3] 當第 N 輪(N≥2)且上一輪凍結 patch 讀得到時,應 印上一輪修補新增行數(同檔內扣掉上一輪已有的同內容行);超過 100 行 應 多印最小修法那一行 [test:t_loop_next_change_size_hint]
- [S4] 當凍結 patch 的 hunk 裡有以 `+++` 開頭的內容行(例如測試裡嵌的 patch 文字)時,那行 應 算成新增內容、不當檔頭 [test:t_loop_next_change_size_hint]
- [S5] 當不是代碼審迴圈、`--spec` 不是 patch、或上一輪凍結 patch 讀不到時,應 不印大小提示、rc 與其他輸出 應 不變,`--json` 的 `change_size` 應 是 null [test:t_loop_next_change_size_hint]
- [S6] 當 `_patch_file_changes` 不帶新參數呼叫時,回傳 應 與改動前逐位元相同 [test:t_patch_file_changes_added_out_noop]
- [S7] 當讀 `reference.md` 與驗證筆記時,提示說明與數字 應 跟程式門檻一致,舊 WHY 與其回頭條件 應 標作廢 [manual:對照 reference 的 300/100 與程式常數;看驗證筆記舊行帶 status:superseded 與被取代]

## 回退

- 提示:刪掉 `loop next` 裡印大小的那段與 `change_size` 欄位;`_patch_file_changes` 的新參數沒人用就一起拿掉。
- 文件:還原 reference、SKILL 那半句與驗證筆記的改動。
- 兩者互不依賴,可以單獨還原。

## 實務隱患

已排除:金流:只讀本機凍結 patch 與帳本,沒有付款
已排除:對外送出:只印到終端機,不連網
已排除:不可逆:唯讀,不寫任何檔、不改帳本
已排除:守衛面:不改任何閘與擋推送,`_patch_file_changes` 不帶新參數時輸出不變(S6 守)
- 帳本回放是事後觀察:「題目本身難」量不到;提示裡的數字是歷史比例,不是保證。
- 門檻 300 與 100 取自回放(第一輪大小約在 300 行開始升高;修補新增行數中位數約 100),是起點不是最佳值。

REVISIT:2027-01-14 照 RETIRE-IF 看提示有沒有人照做,交使用者裁留或撤
