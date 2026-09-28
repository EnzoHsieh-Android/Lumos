# r3 收貨紀錄(code-筆記內容審,末輪)

凍結材料:r3-delta.patch(584 行,r2 修正差異:97c6bf94..a72a0e2e,排除治理帳與卷證);整條分支參考 r3-snapshot.patch(3216 行)。三席全新(通才3 opus、架構對齊3 sonnet、外家否決3 Codex),派工詞禁讀任何席報告;三席記帳一律填 r3-delta.patch 的指紋。

## 席位收貨

- 3 席全交,等完成通知、ls 確認,全交回才搬進卷證、才讀、才動工作目錄。
- report-normalize 3 份皆已正規化。quote-check:通才3、外家3 全錨定;架構對齊3 有 1 句錨不到(F1 把跨三行的 try/except 當一句引)。不改席位引句,改由編排者機械重現:r3-delta.patch 裡確有新函式讀檔包 `except OSError:` 而同檔兩個 doctor 讀同一批檔沒包(`grep -c "except OSError:" r3-delta.patch` ≥1,讀碼對照 doctor 兩處),HIT。

## 編排者重現(寫成回歸 t_note_audit_code_review_r3_regressions;修前紅的驗法:整支 lumos 退回 r3 修正前版本跑,11 條斷言全紅)

| 發現 | 重現 | 結果 |
|---|---|---|
| r3x-F1、r3g-F2 CI 工作項目切分漏合法寫法(行尾註解、引號名字、jobs: 註解) | 回歸 ①(三種形狀+對照組) | HIT(修前紅) |
| r3x-F2、r3g-F1 git add -u / commit -a 後認不出改名 | 回歸 ③ ③b;③c 確認本機已提交的改名不誤擋全新筆記 | HIT(修前紅) |
| r3x-F4、r3g-F5 共用全零常數不認 64 個 0 | 回歸 ④(三道檢查) | HIT(修前紅) |
| r3g-F3 第一層「沒呼叫」不跳過註解、兩句中間漏唸 | 回歸 ②b | HIT(修前紅) |
| r3g-F4 回歸沒守到第一層 doctor 接線、③ 斷言太寬 | 回歸 ② 走 _note_shape_doctor_lines;r2 回歸 ③ 改斷言「ci.yml 的 audit」 | HIT(修前紅) |
| r3s-F1 讀 CI 檔容錯不一 | 讀碼(見上);兩層 doctor 改經 _ci_workflow_texts 同一支讀 | HIT |
| r3s-F2 截斷沒講共幾個 | 回歸 ②c | HIT(修前紅) |
| r3s-F3 第一層訊息沒指名工作項目 | 回歸 ② | HIT(修前紅) |
| r3x-F3 推送前掛鉤把 rc2 當放行 | 試著從掛鉤路徑重現:掛鉤的終點是 git 傳進來的本機提交(`git cat-file` 必在),全 0 在掛鉤第 209 行先跳過;造不出「掛鉤收到本機找不到的終點」。席位的重現是手動模擬掛鉤判法、餵寫錯的範圍,不是掛鉤會走的路 | MISS(重現不到;rc2 的意義在 CI 與手動呼叫,已寫進計劃實作紀錄) |

- 12 條(合併重複後 9 件):11 條折、1 條列 refuted(r3x-F3);輪內有 major,不放行。
- 末輪折入的差異另開驗收輪派全新席看(照 code-筆記形狀擋 的先例),不自己宣稱修好。
