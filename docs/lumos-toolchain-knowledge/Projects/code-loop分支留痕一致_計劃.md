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

修 [[Issues/code-loop-pass不能指定分支]] 的前半：在 `feature` checkout 完成代碼審，準備推 `HEAD:main` 時，`code-loop pass` 只記在 `feature`；推送前按目的地 `main` 查，會要求重記審查。2026-10-04 用全新臨時 Git 倉庫重現：`pass` 回 0，但只產生 `feature.json`，治理帳的 `branch` 也只有 `feature`。這個重現與探針改動無關。`skip` 共用寫入路徑，也要能指定目的分支；`dispositions` 不改表態的判定與紀錄格式，但其 marker 讀側必須核對完整分支身分，免得另一種留痕仍可被借用。

本案作為 [[Projects/代碼審修復穩定性試行_計劃]] 第 2 案的候選。實作和測試以乾淨的 `main@2db51cc4` 副本為基準；本工作樹的未提交探針草稿不得進審材、測試或功能提交。首輪派工之前才按原計劃占位及寫 intake；若隔離、基準或唯一編排者核對失敗，停止試行登記。

## 做法與驗收

- [S1] 當 repo 使用 `code-loop pass --branch main` 或 `skip --branch main` 時，工具應先成功追加治理帳，再把留痕寫到 `main` 的 marker，仍綁目前 checkout 的完整 HEAD 提交；不帶參數時維持原本 checkout 分支。`code-loop check --branch main --at-sha <同一提交>` 能讀到，而查其他分支不得借用。原本沒有 `docs/` 的 Git repo 應先建立可提交治理帳；若追加失敗應回 rc2 且不得留下新通行 marker。 [manual:獨立 Git 倉庫測 pass skip 無 docs 與帳本寫入失敗]
- [S2] 當 checkout 是 detached HEAD 或顯式分支參數無效時，工具應容許顯式指定合法的推送目的短分支名，並讓 `pass`／`skip`／`dispositions`／`check` 在 `--branch` 空白、`refs/heads/` 全名、`@{-N}` 展開式或 Git 判非法時回 rc2；寫側不得增加 marker 或治理帳，也不得把有效的明確指定靜默退回 `HEAD`。[manual:獨立 Git 倉庫測 detached 四指令非法名稱與帳本行數]
- [S3] 當分支名映到同一 marker 檔名（例如 `a/b`／`a__b` 或大小寫不敏感檔案系統的 `Main`／`main`）時，`pass`／`skip` 與 `dispositions` 讀側應以完整分支名取最後一筆治理帳，只在 marker 的原始 `branch`、提交與內容都和該筆帳相同時信任 marker；舊或壞 marker、兩種 marker 檔名互撞、較舊但格式正確的 marker 都不得蓋過治理帳或借用別枝留痕。[manual:碰撞分支 舊檔 壞檔與舊 marker 蓋新帳的正反例]
- [S4] 當 checkout 是 `feature` 而 pre-push 收到目的 `refs/heads/main` 時，指定 `pass --branch main` 或 `skip --branch main` 應放行相同版本的高風險改動，未留痕或查別的目的分支仍應擋；阻擋訊息應給帶目標分支的可用指令。若推送的 local SHA 不是 checkout HEAD，應先叫人切到被推提交再留痕；分支名含 shell 特殊字時提示必須可安全照貼。本案不新增「審查已完成」的機械證明，編排者仍只在審查完成後呼叫 `pass`。[manual:獨立高風險 Git 倉庫以 pre-push stdin 驗同 HEAD 非 HEAD 特殊分支正反例]
- [S5] 當開始本案修復時，編排者應先加最小回歸測試並觀察 S1／S2／S3／S4 翻紅，修後跑該子集及原有 code-loop 分支留痕子集；正式代碼審以獨立 patch、報告和 intake 留證，不把 probe 的審查輪次算成本案。[manual:保存紅綠命令 輸出及審查卷證]

改動在 `cmd_code_loop` 的 `pass`／`skip` 分支選擇、CLI 參數、兩種 marker 的身分核對及 pre-push 提示。新 marker 存原始分支名；讀側先按完整分支名找最新治理帳，再決定 marker 是否與帳相符。治理帳先寫且報錯，marker 再原子替換；原本沒有 `docs/` 就建立治理帳目錄，不要求知識圖譜 vault，也不讓舊 marker 掩蓋較新的成功寫帳。分支名先用 Git `check-ref-format --branch` 檢驗，再要求輸出等於輸入且不是 `refs/heads/` 全名，避免 `@{-N}` 展開或全名與 pre-push 的短名錯位；四個指令共用驗法。推送提示依 Git pre-push stdin 的 local SHA 與 remote ref 決定能否直接留痕，引用參數時 shell quote。審材只含此案 patch，讓新席能看清一次修補造成的差異。

PRIOR-ART: [Git push 的 refspec 文件](https://git-scm.com/docs/git-push)明確把 `src:dst` 的右邊定義為遠端目的 ref；[Git check-ref-format](https://git-scm.com/docs/git-check-ref-format)提供分支名檢查。沿用 Git 的座標與既有 `dispositions` 先寫治理帳再原子寫 marker 的做法，沒有新依賴。外部文件只支持座標與輸入檢驗，不證明本試行會改善收斂。

RETIRE-IF: 第 2 案驗證若發現指定目的分支會讓不同提交或不同分支的留痕被借用，撤回此參數並保留現行私有 clone 繞法；重驗入口為本案 S1／S2 的隔離回歸及正式 code-loop 問閘。第 5 案或 2026-11-03 再按試行總計劃比較修復引入缺陷與額外時間，資料不足不宣稱改善。

## 回退

回退時停用 `pass`／`skip --branch` 並恢復舊讀側，但先檢查 `docs/.governance-log.jsonl` 中本案期間指定目的分支的紀錄；若回退版本無法識別來源，維持推送閘阻擋或重新審查，不能把歷史紀錄當成 checkout 分支的通行證。保留舊 marker／治理帳供歷史追溯，不得刪改 append-only 治理帳。修補只在獨立副本紅綠與正式審查過關後移回本工作樹，移回時再次核對 patch 不含探針草稿。

## 實務隱患

已排除:金流:不處理金額或付款。
已排除:對外送出:本案不推送、部署或寄信。
已排除:不可逆:功能碼可回退，治理帳只追加，不重寫歷史。
守衛面:留痕名稱會影響推送閘；保留完整提交綁定、不同分支不得共用，錯誤輸入必須在寫入前拒絕。

## 前掃修正紀錄

2026-10-04 設計首輪前掃查出四個語意缺口：Git 的 `--branch` 驗法會接受全名或展開式，marker 檔名會讓 `a/b` 與 `a__b` 撞名，治理帳寫入失敗時既有 `pass` 仍回 0，以及程式本身不驗審查是否已完成。前三者已縮準輸入、補 marker 身分核對並把成功寫帳的驗收前提說明；第四者改為人工呼叫前提，不宣稱程式會驗證。前掃卷證見 `governance/review-reports/design-codeloop-pass-branch/r1-intake.md`，正式審查仍以後續凍結快照為準。

2026-10-04 首輪正式審查再指出：`skip` 同樣要能指向目的分支；治理帳失敗不能留下可用 marker；legacy marker、大小寫檔名別名和 `dispositions` 讀側仍能借錯分支；壞 marker 需退帳；驗收要走高風險 pre-push 真入口並核對指令提示。各項已折入 S1／S3／S4 與回退節，處置對照見本輪 intake。一般席與架構席的 seat-check 各有 3 份未明列的派工材料，作為觀測限制保留，不代替其他席的完整審閱。

r1(2026-10-04,4 席):10 條／blocking 9／全部折入，當時的設計快照已通過處置閘。具體例：在 `feature` 上以 `pass --branch main` 留痕，再用 pre-push stdin 指向 `refs/heads/main` 應通過；指向另一個分支應擋住。
席報告目錄：`governance/review-reports/design-codeloop-pass-branch/`；逐條重現與處置見同目錄 `r1-intake.md`。

2026-10-04 代碼審首輪以新實作的 515 行 patch 凍結，兩席共報 9 條、去重為 6 類：最新治理帳會被舊 marker 遮住、非 checkout HEAD 提示錯位、無 docs repo 相容性、check 空分支退回 checkout、shell 特殊字提示及錨點未更新。這些不是原設計審快照已覆蓋的行為，故在本段修正 S1–S4；原設計審 PASS 只作歷史快照證據，後續以新代碼審快照、紅綠測試與最終驗證確認修補。代碼審逐條重現與缺陷來源見 `governance/review-reports/code-codeloop-pass-branch/r1-intake.md`。
