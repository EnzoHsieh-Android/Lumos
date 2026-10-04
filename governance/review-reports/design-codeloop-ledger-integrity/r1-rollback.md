severity: major

## 原始帳回退

severity: major  
blocking: 是  
引句:「回退此修法不截斷治理帳；回退版若仍可把尾列當答案」  
file:line: governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:44  
可重現輸入：在一個提交中同時修改 `scripts/lumos` 並向受 Git 追蹤的 `docs/.governance-log.jsonl` 追加事件，隨後回退該提交。  
預期／現況：條款要求保留原始帳；Git 回退會一併移除該事件。凍結稿未指定只回退程式、保全帳本 bytes 的步驟或驗收檢查，因此照常見回退操作會破壞 append-only 證據。

## 舊版相容

已讀無額外 finding；舊版讀取造成的假綠列於下節。

## 回退後守衛與停推

severity: major  
blocking: 是  
引句:「停止推送與 CI 放行，直到另一道獨立守衛擋住該路徑或重驗新版。」  
file:line: governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:44  
可重現輸入：無本機 marker、有適用題；治理帳最後一列是內容合法的 `dispositions` JSON 物件，但沒有 LF，然後回退至現行舊讀者。`scripts/lumos:35373` 使用 `splitlines()`，會把該尾列交給 `json.loads()`；`scripts/lumos:35529` 隨後可將它當作表態。  
預期／現況：依凍結稿，未以 LF 結尾的列不得成為答案，推送應停止。回退版卻可據此得到 `blocked=False`。凍結稿未指定獨立守衛、停用推送與 CI 的執行入口，或回退前必跑的判準；新增版的測試也無法在回退版代替該守衛。

總結：2 條 finding，blocking **2**。本席唯讀審查，未修改檔案。