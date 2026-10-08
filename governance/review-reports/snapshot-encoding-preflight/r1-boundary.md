severity: clean

未發現可阻擋實作的設計漏洞。

## 逐節結論

- 目標與範圍：已讀，無 finding。修正限於載體快照入口；不關閉原 Unicode Issue，也不擴張非載體政策。
- 驗收條款：已讀，無 finding。UnicodeDecodeError、缺檔 OSError、非編碼 RuntimeError 分類明確；普通與 `-O` 均有控制。首次／已有帳的副作用由「驗證在 append 前完成」的既有結構及測試共同覆蓋。
- 最小重現：已讀，無 finding。歷史 CLI、候選 CLI、紅測來源及不可覆寫收據的界線清楚，未把紅測或 mutant 殺傷力說成生產已修復。
- 回退：已讀，無 finding。可只撤回 UnicodeDecodeError 的受控拒收，不須遷移、刪除或重寫既有帳。
- 實務隱患：已讀，無 finding。
- 初版控制與前掃折入：已讀，無 finding。34／38／42 三版收據未混稱；S4 與 I/O 控制的新增理由可追溯。

## 源碼與測試核對

目前載體快照以原始 bytes 讀入後嚴格 UTF-8 解碼，卻只捕捉 OSError，因此非法編碼仍會外拋；hash 驗證完成後才 append：`scripts/lumos:9576`、`scripts/lumos:9604`、`scripts/lumos:9679`。

`quote-check` 與處置閘都已將 OSError、UnicodeDecodeError 受控分類，能作本案對照：`scripts/lumos:23085`、`scripts/lumos:22947`。

指定測試確實涵蓋：

- 非法 UTF-8 首筆不建帳、已有帳逐位元不變。
- 普通與 `-O`。
- RuntimeError 保留原 traceback 與 rc1。
- 缺檔維持 I/O 診斷。
- 合法 LF／CRLF、非載體 raw bytes 指紋及驗後換檔控制。

佐證：`scripts/test_lumos.py:25800`、`scripts/test_lumos.py:25706`、`scripts/test_lumos.py:25768`、`scripts/test_lumos.py:25897`、`scripts/test_lumos.py:25930`、`scripts/test_lumos.py:278`。

CLI SHA256 實驗為 `52c9c4d7…0276`；`main` 為 `53d1c458…5ed3`。相對 main 的生產 `scripts/lumos` 無差異，只有測試與 intake 變更。refcheck 實跑結果：壞引用 0。

## 合約與風險

圖譜唯一 INVARIANT 不受破壞：審材仍為 `.md`、S1–S4 均有測試綁定、`lands_in` 已填。併發、效能、資源、回退、外部送出及守衛均有具體邊界；本地特定例外捕捉不新增鎖、網路、背景工作或不可逆操作。

最高 severity：clean  
blocking：0

已讀材料：

`governance/review-reports/snapshot-encoding-preflight/r1-snapshot.md`  
`scripts/lumos`  
`scripts/test_lumos.py`  
`governance/review-reports/snapshot-encoding-preflight/preflight-intake.md`  
`governance/review-reports/snapshot-encoding-preflight/r1-graph-context.txt`