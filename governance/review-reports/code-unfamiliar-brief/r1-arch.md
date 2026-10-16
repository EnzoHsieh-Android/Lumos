severity: minor

A1 新增的評測 Systems 未列入圖譜總索引，從標準入口無法發現

severity: minor

blocking: 否

引句:「responsibility: 負責陌生棧簡報五案的凍結、資格預檢與結果匯總，不負責正式代碼審閘門或模型派工」

file: `docs/lumos-toolchain-knowledge/Systems/陌生棧不變量簡報評測.md:6`

file: `docs/lumos-toolchain-knowledge/MOC/index.md:75`

本次新增的評測主節點與四個案例節點均屬 `scope/evals`，但 MOC 的「評測 Evals」未連到其中任何一篇。從計劃連結進場仍能還原內容，因此不阻擋；但只循標準 MOC 入口的新 session 會找不到這套機制。

架構三問：

- 分層／依賴：已讀，無 finding。新模組留在 `governance/eval`，只用標準庫與 manifest 相對路徑，未直呼 CLI、模型或正式 code-loop。`rule_conflict_scan.py:17`、`build_goldset.py:22`、`k1_stop_replay.py:10` 各自維持既有 eval 邊界。
- 命名／錯誤：已讀，無 finding。`ManifestError` 統一資格失敗，讀檔與解析錯誤保留 exception cause；相較探索掃描的跳過策略，正式資格預檢採 fail-closed 合理。
- 重複／競爭實作：已讀，無 finding。未找到第二套 manifest 凍結、十場 preflight 或 receipt 決策線實作；`scripts/test_lumos.py:98274` 只是沿用既有 subprocess 測試轉接層。

圖譜還原：

- 狀態：計劃仍為 doing；五個合成案例已完成資格預檢，21 個凍結檔 SHA 與 20 格 oracle 矩陣通過。
- 限制：資格預檢不證明 Brief 改善審查；合成案例、模型自報陌生度與模型效果均不能外推真人或正式專案。
- v2／Gemini：v2 僅是 assistant 編輯候選，未凍結、未經 S3 洩題審，也不是 Astra 實跑；Gemini U4 僅是探索性編輯試跑，不是正式成對評測，且 control 已先抓到缺陷。
- 下一步：獨立做候選 Brief 的洩題與來源審查，凍結共同任務、工具材料、模型與有效性規則，再執行正式十場；完成後才依預註冊線輸出 stop 或 proceed-to-historical。
- 內容矛盾：未發現。內容本身可自足還原，但標準 MOC 導航因 A1 僅屬部分自足。

殘留問答：範圍內沒有 governance/residual-index.json 差異，也未找到 `[residual:]`、`residual-ask` 或 `pending_questions` 新紀錄；因此沒有題號或文字被換號／改字重問。第二代理是否為另一代理亦無可核對紀錄，不適用，不能冒稱已完成雙代理問答。

審材：governance/review-reports/code-unfamiliar-brief/r1-snapshot.patch（1747 行）已讀。

驗證：`PYTHONDONTWRITEBYTECODE=1 python3.14 scripts/test_lumos.py -k unfamiliar_stack_brief` → 3 passed、0 failed。

總結：最嚴重 severity=minor；blocking=0。
