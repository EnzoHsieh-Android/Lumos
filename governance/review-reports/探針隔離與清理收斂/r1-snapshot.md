---
type: project
status: doing
created: 2026-10-04
updated: 2026-10-04
tags:
  - type/project
  - status/doing
  - risk/守衛面
  - scope/evals
lands_in:
  - Systems/codex-harness
  - Systems/測試假綠形態
related:
  - "[[Projects/代碼審修復穩定性試行_計劃]]"
  - "[[Issues/探針Git隔離的設定與絕對路徑缺口]]"
  - "[[Issues/探針共用沙盒清理失敗仍繼續評分]]"
  - "[[Issues/探針讀碼證據不足]]"
---
# 探針隔離與清理收斂_計劃

本案接 [[Projects/代碼審修復穩定性試行_計劃]] 第1案第4輪的失敗證據；原迴圈 `code-repair-pilot-01` 累計四輪且未放行，不清帳、不改寫舊判定。本計劃先修量測儀器的共同邊界，之後才用其餘試行案例判斷三輪能否收斂。這不是自動取得第5輪代碼審名額。

PRIOR-ART: 借用現有 `make_sandbox` 複製完整 Git 歷史與 `source_probe` 每次獨立副本；Git 官方文件確認 local include、worktree config 可以改變有效設定，故寫入 local config 後仍須以 Git 的有效值驗收（https://git-scm.com/docs/git-config）。比較全新 `git init`、既有副本加檢查、每次獨立副本：全新 init 會丟失題目可見的歷史，單一共用副本的清理還須復原索引、提交、設定與未追蹤檔；選擇保留完整歷史、每次複製並在模型啟動前驗收。零新增相依。

RETIRE-IF: 若外層已有可驗證的獨立檔案系統與 Git 設定隔離，或連續四週量到逐次複製成本超過模型執行總耗時的兩成且污染案例為零，就重評本層逐次複製；入口為每週探針執行紀錄與下次 `make_sandbox` 實作變更。撤除前須保留同等的隔離反例測試。

## 根因與取捨

第4輪四組 blocker 的共同點是儀器把「已做一個動作」當成「邊界成立」：移除 remote／設定 hooksPath 不等於有效 Git 設定安全，複製頂層 `.git` 不等於巢狀 Git 安全，呼叫清理命令不等於清理成功，收到相同空字串不等於有可關聯的工具識別碼。先測結果和失敗語意，再動模型判分。

Git 副本保留來源已有歷史及現行 `rsync` 複製範圍內的檔案內容，仍排除 `node_modules`、`.venv`，並在副本提交量測快照；不聲稱保留來源未提交／索引狀態。凡來源工作樹含巢狀 `.git` 目錄或 gitfile（含 submodule 與獨立巢狀 repo），在任何副本 Git 寫入與模型啟動前拒絕，回儀器錯誤；頂層 `.git` 為相對 gitfile、指向同一副本內 `.hidden-git` 時仍允許，但要通過現有 gitdir、common-dir、toplevel 與 Git 資料符號連結檢查。這是保守的「不支援」判定，不暗稱已隔離巢狀 Git。來源與副本外的 byte 快照在反例後要相同。

移除 remote 必須檢查每條命令退出碼；設定 hook 後讀有效 `git remote` 與 `core.hooksPath`，只有 remote 空且 hook 等於本次副本專用目錄才准啟動模型。local include、worktree config 或錯誤返回若導致結果不符，刪除本次副本並報儀器錯誤；不得當作模型失敗。此邊界只涵蓋繼承的 Git 設定及意外 `git push`，不宣稱封住模型主動指定 URL、停用 hook 或以其他網路工具外送；若題目要求對外送出，沿 [[Issues/探針沙盒能推到真遠端]] 的重驗入口，先取得外層隔離再跑。

所有題目及重試改用各自副本，跑完在 `finally` 刪除；不再靠共用副本的 `checkout`/`clean` 回復。刪除失敗為 fatal 儀器錯誤：當次不算有效分數、整批 inconclusive、退出碼 3、後續 runner 零呼叫。`--keep` 明確保留每次副本並印其路徑，僅供本機診斷，該模式不聲稱完成清理。一般單題模型例外仍可記錄後續跑，沿用現有語意。

Claude 的 `tool_use.id` 和 `tool_result.tool_use_id` 均要求非空字串；不完整事件記 unknown 而非 present／absent。已有其他有效正證據時仍優先 present；Codex 缺／壞 ID 的現行路徑不變。

## 驗收條款

- [S1] 當來源含巢狀 `.git` 或 gitfile，而頂層是合法 repo 時，建立副本應在任何副本 Git 寫入前拒絕、清理副本，來源與副本外 Git 資料 byte 相同；普通 clone 及通過現有路徑檢查的頂層相對 gitfile 應成功。[test: t_probe_boundary_nested_git]
- [S2] 當 local include、worktree config 或 remote 移除失敗使有效 remote 非空，或有效 hooksPath 不等於本次專用 hook 時，模型不得啟動、建立副本應失敗並清理；好例能用本機 bare repo 的 dry-run push 證明 pre-push 生效且 bare 未變。[test: t_probe_boundary_effective_git]
- [S3] 當普通題或重試逐次執行時，探針應讓各次得到不同乾淨副本；前一次修改提交、索引、Git 設定與未追蹤檔後，下一次看不到污染，且原來源 byte 相同。一般模式各次刪除；`--keep` 各次保留並列出路徑。[test: t_probe_boundary_attempt_isolation]
- [S4] 當任一次副本刪除失敗時，main 應把當次排除於有效分數、把整批標為 inconclusive、回 3 且不呼叫後續 runner；一般模型例外仍照現行分流。[test: t_probe_boundary_cleanup_failure]
- [S5] 當 Claude 工具呼叫或結果識別碼為空字串時，無其他正證據應判 unknown 並排除有效分母；有效正證據與正常非空 ID 路徑保持原判。[test: t_probe_boundary_claude_ids]

## 先紅後綠與邊界

以 `governance/review-reports/code-repair-pilot-01/r4-parent-reproduction.json` 與 r4 報告作前提，先在現碼新增五組反例，逐條記現場前置斷言（確實有有效 remote／hooks override、巢狀 Git 指出外部資料、清理確實失敗、空 ID 確實進解析器），確認會紅再改實作。跑相關 `probe_` 子集和本案測試；真模型、網路推送及五案收斂率不由單元測試代替。若正常來源有合法巢狀 Git，明確報不支援與替代路徑，不靜默給假安全結果。

## 實務隱患

已排除:金流:僅改本機量測儀器。
對外送出:只用本機 bare Git 與 dry-run 驗證，不能把 Git hook 當完整網路隔離。
已排除:正式環境不可逆:本案不執行正式探針、不推送。
守衛面:探針的隔離與失敗判分會改，須先過設計閘，實作後依 pitfalls 風險過代碼審。

## 回退

回退本案實作時保留 r4 原始卷證與新反例，恢復原案未放行狀態；不能把舊共用副本測得的分數當新判準證據。若逐次副本成本過高，先量測、再提出能保留相同隔離證據的替代設計，不直接關掉 fail-closed 條件。

## 審計修正紀錄

待設計閘與審查。
