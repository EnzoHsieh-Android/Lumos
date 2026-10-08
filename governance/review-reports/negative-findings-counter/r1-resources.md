severity: minor

## resources-F1

severity: minor  
blocking: 否  
引句:「已有帳逐位元不變、未有帳不建立帳本，普通及最佳化皆成立。」

規格沒有固定負數檢查必須早於報告正規化；測試也只檢查 `.canary-log.jsonl`。因此可把檢查放在報告驗證後：輸入 `--findings -1 --report malformed.md` 時，先向治理帳寫入 `report-not-normalized` 事件，再回 rc2；指定測試仍全過，卻違反入口拒收不產生帳務副作用的直覺。

源碼佐證 file: `scripts/lumos:9552`、`scripts/lumos:9555`、`scripts/lumos:9676`、`scripts/test_lumos.py:293`

建議明訂負數檢查須位於任何 `_gate_event_or_warn` 與 canary 追加之前，並測試兩種帳本都不存在或逐位元不變。

其餘逐節已讀無 finding。負數由 `argparse type=int` 可由真實 CLI 到達；普通與 `-O`、首次不建 canary 帳、既有帳不變、兩席零發現 gate PASS 均有測試。唯一相關合約是設計審條款綁定閘；本改動不改其判定，合法數量仍走原路，負數提前拒收不破壞合約。

風險：併發、效能、資源、回退、外部送出均無新增風險；守衛面僅有上述副作用順序缺口。唯讀沙箱未實跑會建立臨時目錄的測試，不計產品紅燈。

總結：最嚴重 minor；blocking 0。

已讀材料：

- `governance/review-reports/negative-findings-counter/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/negative-findings-counter/preflight-intake.md`
- `governance/review-reports/negative-findings-counter/r1-graph-context.txt`