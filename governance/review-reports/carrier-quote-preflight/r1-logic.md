severity: major

## logic-F1

severity: major  
blocking: 是  
引句:「只在已讀取有效 UTF-8 快照時辨認零引句；不把讀不到快照誤報成零引句。」

spec 區分了有效 UTF-8 與讀取失敗，但 [S4] 只驗「檔案不存在」，未規定或測試「檔案存在但不是 UTF-8」。目前寫側以嚴格 UTF-8 讀快照，卻只捕捉 `OSError`；`UnicodeDecodeError` 會直接逸出。讀側已有正確先例，會同時捕捉兩者並判 quote 失敗。

具體輸入：有完整引句的載體報告＋內容為 `ff fe` 的現存快照 → `canary record` 不是 rc2 的輸入拒收，而是 rc1 traceback；帳雖未追加，但 CLI 契約與「不可讀快照不能混成零引句」的錯誤分流沒有完成。應在 [S4] 明定非 UTF-8 快照走既有 rc2 讀取錯誤出口，並加普通與 `-O` 測試，且斷言不是「沒有引句」。

源碼佐證 file: `scripts/lumos:9565`  
源碼佐證 file: `scripts/lumos:9568`  
源碼佐證 file: `scripts/lumos:9569`  
源碼佐證 file: `scripts/lumos:22925`  
源碼佐證 file: `scripts/lumos:22928`  
源碼佐證 file: `scripts/test_lumos.py:25638`

## 逐節結論

問題與範圍、PRIOR-ART、RETIRE-IF：已讀，無其他 finding。

核心裁定：空輪、全輪載體集合、單席 `findings` 數量及 literal `none` 的語意分離正確；未發現全域保留 `none` 或強迫集合數量相等。

驗收條款：S1–S3 的正反控制與前置斷言可達目標分支；S4 有上述缺口。

回退、落點：局部回退且保留讀側閘，無其他 finding。

## 合約與風險

- record 成功必須已落盤可讀：前置拒收位於 append 前，不破壞。
- second 純 telemetry：未觸及。
- 處置閘第五步條款綁定：未改其判定，無影響。
- 翻紅釘需前置斷言：現有測試已證明 loop 報告解析；不違反，但缺少非 UTF-8 案例。
- 併發：未新增共享並行流程。
- 效能：僅載體多做既有線性引句掃描。
- 資源：無新增長存資源。
- 回退：功能提交可局部撤回。
- 外部送出：無網路、金流或正式環境異動。
- 守衛：唯一 blocking 為非 UTF-8 輸入分流未被規格與測試封住。

總結：最嚴重 major；blocking 1。PF1 前提修正成立；PF2 經源碼獨立核對後成立，且應納入本案驗收。

已讀材料：

- `governance/review-reports/carrier-quote-preflight/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/carrier-quote-preflight/preflight-intake.md`
- `governance/review-reports/carrier-quote-preflight/r1-graph-context.txt`