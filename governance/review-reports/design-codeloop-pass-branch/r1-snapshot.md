---
type: project
status: doing
created: 2026-10-04
updated: 2026-10-04
tags:
  - type/project
  - status/doing
  - scope/guards-gates
related:
  - "[[Issues/code-loop-pass不能指定分支]]"
lands_in:
  - Systems/pitfalls-code-loop
---
# code-loop 分支留痕一致計劃

## 問題與邊界

修 [[Issues/code-loop-pass不能指定分支]] 的前半：在 `feature` checkout 完成代碼審，準備推 `HEAD:main` 時，`code-loop pass` 只記在 `feature`；推送前按目的地 `main` 查，會要求重記審查。2026-10-04 用全新臨時 Git 倉庫重現：`pass` 回 0，但只產生 `feature.json`，治理帳的 `branch` 也只有 `feature`。這個重現與探針改動無關。`dispositions` 的雙分支表態是另一個問題，本案不改它的判定或紀錄格式。

本案作為 [[Projects/代碼審修復穩定性試行_計劃]] 第 2 案的候選。實作和測試以乾淨的 `main@2db51cc4` 副本為基準；本工作樹的未提交探針草稿不得進審材、測試或功能提交。首輪派工之前才按原計劃占位及寫 intake；若隔離、基準或唯一編排者核對失敗，停止試行登記。

## 做法與驗收

- [S1] 當有可寫治理帳的 repo 使用 `code-loop pass --branch main` 時，工具應把留痕寫到 `main` 的 marker 和治理帳，仍綁目前 checkout 的完整 HEAD 提交；不帶參數時維持原本 checkout 分支。`code-loop check --branch main --at-sha <同一提交>` 能讀到，而查其他分支不得借用這筆新留痕；含 `/` 與 `__` 的兩個不同分支也要分清。[manual:在獨立 Git 倉庫比對 marker 治理帳 完整提交與碰撞分支讀側]
- [S2] 當 checkout 是 detached HEAD 或分支參數無效時，工具應容許顯式指定合法的推送目的短分支名，並在 `--branch` 空白、`refs/heads/` 全名、`@{-N}` 展開式或 Git 判非法時回 rc2、讓 marker 和治理帳都不增加；不得把有效的明確指定靜默退回 `HEAD`。[manual:在獨立 Git 倉庫測 detached 空白 全名 展開式 非法名稱與帳本行數]
- [S3] 當新增 `pass` 的目的分支參數時，工具應維持 `skip`、`dispositions`、`check` 的既有語意和守衛要求；本案不新增「審查已完成」的機械證明，編排者仍只在審查完成後呼叫 `pass`。[manual:比對三個既有指令的 CLI 幫助和相關測試結果]
- [S4] 當開始本案修復時，編排者應先加最小回歸測試並觀察 S1／S2 翻紅，修後跑該子集及原有 code-loop 分支留痕子集；正式代碼審以獨立 patch、報告和 intake 留證，不把 probe 的審查輪次算成本案。[manual:保存紅綠命令 輸出及審查卷證]

最小改動在 `cmd_code_loop` 的 `pass` 分支選擇、CLI 參數及 marker 的身分核對：新 marker 存原始分支名；`_codeloop_read` 遇到 marker 名碰撞而內存分支不符時，退讀依完整分支名篩出的治理帳。舊 marker 沒有分支欄且請求名含 `/` 或 `__` 時也退讀治理帳，不能把檔名當身分。保留 `_codeloop_gov_log` 與 pre-push 現有讀寫語意；既有 `pass` 在沒有 `docs/` 或治理帳寫入失敗時仍可能只寫 marker，本案的 S1 驗收限可寫治理帳的 repo，不把這個既有缺口冒充已修。分支名先用 Git `check-ref-format --branch` 檢驗，再要求輸出等於輸入且不是 `refs/heads/` 全名，避免 `@{-N}` 展開或全名與 pre-push 的短名錯位。審材只含此案 patch，讓新席能看清一次修補造成的差異。

PRIOR-ART: [Git push 的 refspec 文件](https://git-scm.com/docs/git-push)明確把 `src:dst` 的右邊定義為遠端目的 ref；[Git check-ref-format](https://git-scm.com/docs/git-check-ref-format)提供分支名檢查。沿用 Git 的座標和既有 pass/check 紀錄機制，沒有新依賴。外部文件只支持座標與輸入檢驗，不證明本試行會改善收斂。

RETIRE-IF: 第 2 案驗證若發現指定目的分支會讓不同提交或不同分支的留痕被借用，撤回此參數並保留現行私有 clone 繞法；重驗入口為本案 S1／S2 的隔離回歸及正式 code-loop 問閘。第 5 案或 2026-11-03 再按試行總計劃比較修復引入缺陷與額外時間，資料不足不宣稱改善。

## 回退

回退時移除 `pass --branch`，保留舊 marker／治理帳供歷史追溯；新參數寫入的紀錄本身仍可由既有 `check --branch` 依完整提交核對。不得刪改 append-only 治理帳。修補只在獨立副本紅綠與正式審查過關後移回本工作樹，移回時再次核對 patch 不含探針草稿。

## 實務隱患

已排除:金流:不處理金額或付款。
已排除:對外送出:本案不推送、部署或寄信。
已排除:不可逆:功能碼可回退，治理帳只追加，不重寫歷史。
守衛面:留痕名稱會影響推送閘；保留完整提交綁定、不同分支不得共用，錯誤輸入必須在寫入前拒絕。

## 前掃修正紀錄

2026-10-04 設計首輪前掃查出四個語意缺口：Git 的 `--branch` 驗法會接受全名或展開式，marker 檔名會讓 `a/b` 與 `a__b` 撞名，治理帳寫入失敗時既有 `pass` 仍回 0，以及程式本身不驗審查是否已完成。前三者已縮準輸入、補 marker 身分核對並把成功寫帳的驗收前提說明；第四者改為人工呼叫前提，不宣稱程式會驗證。前掃卷證見 `governance/review-reports/design-codeloop-pass-branch/r1-intake.md`，正式審查仍以後續凍結快照為準。
