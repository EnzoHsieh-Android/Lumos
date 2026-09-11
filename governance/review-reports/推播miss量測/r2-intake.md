# r2 收貨紀錄(推播miss量測)

- 派三席:通才-sonnet、邊界-sonnet(第 2 版修訂稿;派工詞加寫 git 實驗一律 `git -C`)、外家否決-codex(gpt-5.6-sol、medium,代碼審第三輪外家席跑完後才派)。
- 三份報告 report-normalize 都已正規化;通才、邊界 quote-check 全數錨定。外家席 10 句有 1 句錨不到:H10 引「每個子行程設 60 秒逾時,逾時那支檔的分類記判不出並計數」,原文「判不出」外面有一對「」,它漏了——照規則錨不到不採信,不列進本輪發現;它講的「沒有整次週跑的總預算」與 G6 相同,G6 錨得到、已折。
- 多席獨立一致的直接折:多檔 apply_patch(F1、H3)、about_code 與編輯目標的路徑口徑(F3、H5)、時區(G5、H8)、三支既有測試沒守門(F2、G4)、子代理讀取(F6、G3)。

## 機械重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| F1 | 讀 impact-hook `main()`:多檔 apply_patch 逐檔算、`"\n\n".join(chunks)` 合成一份,各塊不標檔名 | HIT |
| H3 | 同 F1 | HIT |
| G1 | 讀 `cmd_search`:排序模式最後一行「(共 N 篇候選,照相關性排序;想照檔名排加 --legacy)」、舊模式「N 處 / M 篇 [已排除 code block,--code 可含]」,那行後面都接固定尾字 | HIT |
| G2 | 逐字稿實例 `scripts/lumos search "…" 2>&1 \| head -6`(邊界席附的逐字稿行) | HIT |
| G5 | 逐字稿 timestamp 是 UTC `Z`,shell 端 `date +%G-W%V` 用本機時區 | HIT |
| H8 | 同 G5 | HIT |
| G6 | 讀 `autonomous-loop.sh`:整支只有 `take_lock` 一把鎖,run_exam…run_replay 依序在鎖內 | HIT |
| H6 | 讀 `cmd_impact`:「某節點既在 incidents 又在 direct/indirect → 從 direct/indirect 移除」 | HIT |
| H9 | 讀 `build_ranked_context`:有 `[{stk} 效能檢核——…]` 段標頭 | HIT |
| F3 | 讀 `_about_code_path`:about_code 擋絕對路徑;Claude Edit 的 file_path 是絕對路徑 | HIT |

其餘各條(F2、F4–F6、G3、G4、G7–G10、H1、H2、H4、H5、H7)是文件缺陷或設計取捨,照席位所附 file:line 讀碼核過。

## 處置

- 25 條全折(F1–F6、G1–G10、H1–H9;accepted 0、refuted 0),H10 錨不到不列。
