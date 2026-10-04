---
type: project
status: doing
created: 2026-10-05
updated: 2026-10-05
tags:
  - type/project
  - status/doing
  - scope/guards-gates
related:
  - "[[Issues/背景啟動失敗誤報逾時]]"
  - "[[Projects/過期鎖安全接手_計劃]]"
  - "[[Projects/背景快取命中清鎖_計劃]]"
lands_in:
  - Systems/lumos-cli-write
  - Systems/codex-harness
  - Systems/測試假綠形態
---
# 背景啟動失敗即時回報_計劃

## 問題與範圍

[[Issues/背景啟動失敗誤報逾時]] 是原案第三輪仍未收斂的第二個獨立缺陷：`_lens_spawn_warmer` 在 `subprocess.Popen` 拋 `OSError` 後刪鎖卻不告訴 `_lens_wait_or_warm`，等待端繼續等一個從未啟動的工作，最後回 rc 5、`timed_out=true`，甚至指向已不存在的鎖。F1 的 [[Projects/背景快取命中清鎖_計劃]] 已在另一分支處理並留痕，本分支從該版本開出，只處理「建立子程序當下失敗」的回報，不改已啟動背景工作的等待期限與快取協議。

[[Systems/codex-harness]] 所列 Claude 派工 hook 目前只把 `lock_error` 視為 error；遇 rc 5 記 timeout，其他 rc 2 多半靜默。因此光讓 CLI 回 rc 2 仍不夠，hook 必須用固定說明告知「背景未啟動」並記 error 事件；傳到派工詞的字串只用固定模板與既有清理過換行的鎖路徑，不放原始例外字串。若角色卡已算出，仍沿現行錯誤分支附上。

前掃發現既有測試在 `Popen` 失敗後以快取讀取回呼模擬「另一程序接手並寫好快取」，要求等待端回 rc 0 且不刪新鎖。若失敗當下無條件回 rc 2，這條已受測的行為會倒退。因此失敗清鎖後**只讀一次**可信且未過期的快取：命中就用現有輸出格式回 rc 0，仍不碰替代持有者的鎖；沒有可用快取就立即回 rc 2，不進等待／超時迴圈。這個單次讀取是結果優先，不代表本次背景已成功啟動。

## 驗收條款

- [S1] 當本次取得鎖後 `_lens_spawn_warmer` 的 `Popen` 拋 `OSError`，且失敗清鎖後單次讀取仍沒有可用快取時，`_lens_wait_or_warm` 應立即回 rc 2 與 JSON `spawn_error=true`、本次 `lock_path`、原 `range`；不能等到期限後報 `timed_out` 或 `lock_uncertain`。清不掉鎖時訊息也不能宣稱鎖已不存在。 [test:t_lens_spawn_failure_reports_error]
- [S2] 當 hook 收到上述 rc 2 JSON 時，應附固定「背景未啟動、檢查鎖位置」說明，記 error 而非 timeout 事件；鎖路徑仍走原 300 字與換行消毒，原始 `reason` 不進派工詞。 [test:t_dispatch_lens_hook_spawn_error_notice]
- [S3] 當 `Popen` 成功但背景尚未產出快取，`_lens_wait_or_warm` 應在等待期限到時仍回 rc 5，讓已啟動工作繼續寫快取並清鎖；不得把真正等待逾時改報啟動失敗。 [test:t_lens_timeout_keeps_warming_cache]
- [S4] 當啟動失敗清掉原鎖後另一程序取得同名鎖，`_lens_wait_or_warm` 應保留新鎖：單次讀到可用快取就沿既有測試回 rc 0，讀不到則回 rc 2，兩者都不按「曾取得」刪新鎖。 [test:t_lens_stale_lock_reports_uncertainty] [test:t_lens_spawn_failure_preserves_replacement_lock]
- [S5] 當 hook 同時收到角色卡與 `spawn_error`，仍應附角色卡並記 error；一般 `lock_error` 提示與事件類型保持原行為。 [test:t_dispatch_lens_hook_spawn_error_notice] [test:t_lens_stale_lock_reports_uncertainty]

PRIOR-ART: [Python 3.14 `subprocess` 例外文件](https://docs.python.org/3/library/subprocess.html#exceptions)明列建子程序前的失敗會在父程序重拋，常見為 `OSError`；因此在 `_lens_spawn_warmer` 捕捉點把結果傳回等待端即可立刻分流，不必用零秒輪詢猜「有沒有啟動」。同一文件也說 WSL／QEMU 某些 `posix_spawn` 路徑下，程式不存在可能表現為子程序非零退出而非建構子拋例外；本案只對可觀測到的建構子 `OSError` 作保證，不把「啟動成功後立即退出」也說成可辨識，因背景 stdout/stderr 本來丟到 `DEVNULL` 且父程序不監督它。

RETIRE-IF: 若 `Popen` 成功返回但背景立刻異常退出成為可量測的常見誤報，撤除「只靠建構子例外即可分類啟動失敗」的範圍，另設能區分啟動確認與工作完成的握手；若新增分流的維護成本高於減少的誤報與等待時間，回到同步計算或原有停用暖機開關。

## 實務隱患

已排除:金流:此路徑只產生審查派工鏡頭，不碰付款。
已排除:對外送出:本分支不推送、不部署、不寄送資料。
已排除:不可逆:只修改隔離 clone 並在暫存目錄注入啟動失敗，不碰真實鎖。
守衛面:把未啟動誤記逾時會遮掉故障；反過來把已啟動誤記失敗會誤導人工清鎖。S1/S3 必須雙向釘住。hook 只提示，仍照原機制放行派工。

## 回退

先在受影響的 hook 執行環境設既有 `LUMOS_DISPATCH_LENS_NO_CACHE=1`，讓鏡頭改同步計算並停止新背景暖機；確認舊背景工作停止與鎖狀態後，才把本分支回退到 F1 帳本提交 `e5695c11`。該提交仍含原案其他未部署限制，不能當整體已放行版本。

## 驗證順序

以 Python 3.14 在隔離來源 repo 先跑 S1/S2/S4 故障注入，要求舊碼翻紅且前置條件真成立；修後跑五條款對應的測試，確認零 skip。既有背景真執行整合測試須有本地 `main` 或 `master` 及足夠歷史；不具備時先補測試前提，不能把 skip 當綠。完成後另記獨立 Verification 與代碼審卷證；前案 [[Verification/2026-10-05_過期鎖安全接手實作驗證]] 仍待實際安裝的 S6 條件，不因兩個小修自動改成 pass。
