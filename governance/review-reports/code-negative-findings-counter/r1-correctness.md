severity: minor

## F1 計劃仍把已落地的入口寫成待實作

severity: minor  
blocking: 否  
引句:「生產入口還未動，先依規格閘判門與必要設計審通過後實作。」  
佐證 file: `docs/lumos-toolchain-knowledge/Projects/負數發現計數在追加前拒收_計劃.md:38`  
佐證 file: `scripts/lumos:9201`

輸入：下一個 session 以仍為 `doing` 的計劃恢復工作。  
錯誤：計劃第 38、46 行仍說入口未動、六席審查後才實作，但 HEAD 已在 `cmd_canary` 落地負數守衛，驗證頁也記載固定新碼結果。這會讓接手者誤判階段、重做設計或再次加入同一守衛。  
可執行證據：實跑 normal 與 `-O` 的 `canary record none --findings -1/-2` 均回 rc2；搭配不存在的 `--report` 仍先診斷負數。應把兩句改成明確的「實作前紀錄」，或更新為「已實作、完整分片與本案 CI 待驗」。

固定圖譜鏡頭逐條：

- `Systems/design-loop`：`.md` 計劃、S1–S3 測試綁定及處置閘證據均保留；只有 F1 的階段敘述過期。
- `Systems/lumos-cli-read`：未改 search、superseded 或 stale 行為。
- `Systems/bound-tests-gate`：未改固定席合約測試的執行或阻擋判準；沒有拿尚未完成的完整分片冒稱全綠。
- `Systems/guard-kill`：未改 rc 優先序或 JSON 純度。
- `Systems/授權與歸屬`：未碰 vendored 集合、授權檔或檔頭。
- `Systems/測試假綠形態`：測試具舊碼翻紅、合法種子及帳本逐位元前置控制，未見走不到分支的假綠。
- `Systems/lumos-cli-lifecycle`：未碰 reinject 或 CLAUDE.md sentinel。
- `Systems/canary-audit`：負數在追加前退出；成功落盤與 second telemetry 合約未變。
- 僅列名的其餘固定席未據此延伸新規則。

驗證摘要：

- 完整讀過 source patch 132 行、graph patch 300 行。
- source SHA-256：`ff5fe160ba86e89708946b83add08f2dced2fb3a984dfb7cda8f6cb69b867ab1`
- graph SHA-256：`a57d7ffde641578eac2697932dae8203376a2c53e9eef9e600b4b86236398c18`
- normal／`-O` 負數實跑皆 rc2；canary 與 governance 帳本雜湊前後不變。
- 單測 runner 因唯讀環境沒有可寫暫存目錄而未啟動；未冒稱重跑成功，也未重跑完整套件。
- actual pitfalls：standard；適用棧別題 0；未把 `filtered=false` 全檔告警算成新增 finding。
- 最高級：minor；blocking：0。