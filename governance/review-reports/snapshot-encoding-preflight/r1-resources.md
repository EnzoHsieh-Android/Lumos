severity: major

## resources-F1

severity: major  
blocking: 是  
引句:「當快照讀入階段出現非編碼且非I/O程式例外，記帳器應保留原例外，不改報成UTF8輸入rc2，成功帳不追加。」

現有測試只把 `Path.read_bytes` 注入 `RuntimeError`；它確實殺掉「把目前整段 `except OSError` 直接改成 `except Exception`」的 mutant，但沒有覆蓋 `_quote_rows` 本身拋出程式例外。

具體漏網實作：

1. 把 `read_bytes()` 移到 `try` 外。
2. 在 `decode()` 與 `_quote_rows()` 外包 `except Exception`，統一回 UTF-8 rc2。
3. 現有 Runtime 注入仍從 `read_bytes()` 原樣逸出，42 條測試可通過。
4. `_quote_rows` 若因程式缺陷拋 `RuntimeError`，卻會被誤診成快照編碼問題，直接違反 S4。

源碼佐證：目前 `_quote_rows` 位於同一捕捉範圍內；測試注入點只在 `Path.read_bytes`。  
file: `scripts/lumos:9578`  
file: `scripts/lumos:9583`  
file: `scripts/test_lumos.py:25812`  
file: `scripts/test_lumos.py:25823`

建議在同一測試再注入一次 `_quote_rows -> RuntimeError`，要求原例外逸出且帳不追加；如此才能限制捕捉範圍，而不只限制目前程式碼的單一排列。

其餘逐節結果：

- 目標、範圍、PRIOR-ART：無 finding；正式 CLI SHA256 已核對為 `52c9c4d7…f3760276`，未冒稱已修復。
- S1–S3：無 finding；非法編碼、零引句、報告編碼、換檔、負數及 OSError 分流都有具體結果。
- 同份 bytes：引句驗證直接使用 `_sbytes`，其 SHA 再與後續重讀結果比較後才追加。
- 追加前副作用：S1 限定其他參數與報告合法時，快照拒收發生在 `_jsonl_append_verified` 前；失敗案例檢查未建帳或帳逐位元不變。
- 合約：唯一處置閘合約未受破壞；四條 `[S1]`–`[S4]` 均綁測試，`spec-gate --no-run` 驗得四條全標、句式與回退有效。
- 風險：併發不新增保證；效能與資源不增額外快照讀取或背景工作；回退只撤本分支；無外部送出；守衛面保留正式設計審。無新第三方依賴。
- `refcheck` 實跑：0 壞引用。
- 初版三條 spec-gate 僅視為歷史紀錄；本席未宣稱四條已跑綠，也未重審前案 G。

總結：最高 severity 為 major；blocking 1 條。

已讀材料：

- `governance/review-reports/snapshot-encoding-preflight/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/snapshot-encoding-preflight/preflight-intake.md`
- `governance/review-reports/snapshot-encoding-preflight/r1-graph-context.txt`