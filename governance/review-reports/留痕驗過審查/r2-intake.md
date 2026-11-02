# r2 收貨紀錄

r1 全折但折入幾乎重寫做法段,新增人裁放行判定,這些內容沒有席看過,所以開修訂驗收輪:四席全新脈絡,看全文加 `r2-delta.patch`。編制少於 `loop next` 印的五席是編排者決定,帳上照實記四席。

quote-check 四席全錨定;架構對齊席檔級首交低於最高值,退回改第一行一次。邊界席 refcheck 有一筆 missing 是它用來舉證的不存在檔案,不是壞引用。

編排者機械重現:

| 項目 | 指令與結果 | 判定 |
|---|---|---|
| 輕量曾抓到 major 仍放行(c1) | `lumos loop next code-loop-fix-list` 印 escalate;該迴圈 tier=light、無輪次、唯一一列 kind=none severity=major | HIT |
| 擋下訊息沒出口(b1、r4、b5) | `cmd_loop_cap_decision` 未達上限回 rc2;凍結 rc=1 照寫檔;邊界席掃 52 個無判定檔迴圈 29 個凍出 rc=1 | HIT |
| 整支換回抹掉他人提交(r1、c6) | 回滾席臨時 repo 重現 `git checkout <功能提交>^ -- code` 丟掉後續提交的行 | HIT |
| 讀帳第二種做法(a1) | `_canary_ledger_rows` 已接 RecursionError、回壞行、吃路徑,只缺原文 | HIT |

逐條處置(c=正確性、b=邊界、r=回滾、a=架構對齊;編號接本輪報告順序):

| 發現 | 嚴重度 | 處置 |
|---|---|---|
| c1 輕量曾抓到 major 仍放行 | major | 折:加 escalate 判法,S7 改寫 |
| b1、r4、b5 判定失敗沒出口、順序誤導 | major | 折:指紋比對排到看結果之前,訊息講出口,S5、S6 改寫 |
| b2 壞帳沒下一步 | major | 折:排在 `--loop` 之後,訊息含 `skip`,明寫範圍 |
| r1、c6 回退抹掉別人的提交 | major | 折:改反向套用差異 |
| r2 回退沒帶圖譜 | major | 折:回退第 2 步 |
| r3 放寬不是改一處 | major | 折:改寫成要動哪些 |
| a1 讀帳第二種做法 | major | 折:改走 `_canary_ledger_rows`,補可選參數 |
| r5、b4、c5 nodes 語意與 skip | minor | 折:`skip` 完全不動,不收 `--loop`;nodes 語意限 passed |
| r6 新函式複雜度 | minor | 折:守衛面列三道 |
| b3、c4 壞行定義 | minor | 折:寫明非物件算壞、非 UTF-8 不算及理由 |
| b6、a3 編號引號與落帳 | minor | 折:編號一律 `_rf_qloop`;rc 表補上;不另加去重碼,讀法寫明 |
| b7、c2 spec_path 取法 | minor | 折:只取最後一輪,檢查存在 |
| b8 判定輪定義 | minor | 折:`round` 列必要欄,engine_rev 一句 |
| b9 d1 代價 | minor | 折:〈相容〉註明以此為準 |
| c3 指令缺 --spec | minor | 折 |
| c7 人裁不分 fails 種類 | minor | 折:明寫取捨,不加機制。加種類白名單的最小解不必要:人裁接受的是收尾,這道防忘記 |
| a2 舊句沒同步 | minor | 折:第 7 步補 bound-tests-gate。那句當初的完整理由查不到,本篇只寫適用範圍是本篇判斷 |
| a4 落點 | minor | 折:lands_in 換成 reversibility-governance-ledger |

r2 折入後沒有再派席驗。三輪上限還剩一輪,編排者決定不開:這份材料下一關是實作後的高風險代碼審,條款都綁測試。
