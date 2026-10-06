severity: minor

## resources-F1
severity: minor  
blocking: 否  
引句:「提示沒有引句、取消零發現輪的處置選項或改用可核對的載體」

S1 要求錯誤訊息同時給出兩條復原路徑，但測試只檢查含「沒有引句」。具體反例：實作僅印「沒有引句」後 rc2，所有負向測試仍通過，卻未告知應移除誤帶的處置選項或改選全錨載體。

源碼佐證 file: `scripts/test_lumos.py:25632`

## 其餘逐節結果

- 寫入與副作用：拒收點位於 `_jsonl_append_verified` 前；正向仍經落盤讀回驗證。帳不變、無成功訊息均有覆蓋。
- 可達性：新測試具 `--loop`、`--snapshot`，並驗 `reported`；普通與 `-O`、合法正向、空輪反向控制均可達目標語意。
- PF2 不列 finding：非 UTF-8 快照確會在寫側逸出 `UnicodeDecodeError`，但凍結 spec 明限「有效 UTF-8」且明說不吞本案外例外；這是既有行為，非本裁定造成。file: `scripts/lumos:9568`
- 合約：成功落盤可讀回、second 純 telemetry、處置閘第五步、假綠前置斷言均未被破壞。
- 併發：隔離測試帳；新判斷不新增共享狀態競態。效能／資源：沿用既有單次報告與快照讀取，無新增持有資源。回退：單一寫側分支可回退。外部送出：無。守衛：僅上述提示文字未被測試鎖住。
- 唯讀沙箱未建立 CLI 現場、未重跑收據；不把此限制算產品紅燈。

總結：最嚴重為 minor，blocking 0。

已讀材料：

- `governance/review-reports/carrier-quote-preflight/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/carrier-quote-preflight/preflight-intake.md`
- `governance/review-reports/carrier-quote-preflight/r1-graph-context.txt`