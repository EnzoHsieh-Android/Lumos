現況判定：載體 `canary record` 的 `--snapshot` 含非 UTF-8 bytes 時，會在寫帳前拋出未捕捉的 `UnicodeDecodeError`，CLI 以 rc1＋traceback 結束；不會追加 canary 帳。這是已知、已重現但尚未修到寫入入口的相容性缺口，不需要另造新機制。

### 可核對證據

- `cmd_canary` 只有載體席（`findings_set is not None`）才嚴格解碼 snapshot：
  [scripts/lumos:9576](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:9576)
- 先 `read_bytes()`，再嚴格 `.decode("utf-8")`；但 `except` 只接 `OSError`，接不到繼承自 `ValueError` 的 `UnicodeDecodeError`：
  [scripts/lumos:9578](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:9578)
- 實際探針以合法載體報告＋`ff fe` snapshot 跑出 rc1、完整 traceback，且 `canary_ledger_exists: false`：
  [preflight-encoding-probe.json](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/carrier-quote-preflight/preflight-encoding-probe.json)
- 因追加 `_jsonl_append_verified` 在後面才執行，所以此例外不會留下半筆或錯帳：
  [scripts/lumos:9630](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:9630)

### 已有脈絡與處理

- 已有開放 Issue：`Issues/主程式讀取路徑漏接UnicodeDecodeError`。它明記 CLI 外部輸入路徑是實際風險，並決定逐入口判斷，不能全檔機械擴大捕捉。
- `Projects/載體零引句在記帳前拒收_計劃` 已明確記錄本案例：
  [計劃第 42–47 行](/tmp/lumos-review-snapshot-encoding-preflight/docs/lumos-toolchain-knowledge/Projects/載體零引句在記帳前拒收_計劃.md:42)
  - 當時刻意排除於零引句修復之外。
  - 已確認會中斷且不追加帳。
  - 若改為 rc2，要求另立輸入契約及正反控制，不能順手默改。
- 2026-08-04 的 `Verification/2026-08-04_design-loop處置閘終審硬化` 所稱 `UnicodeDecodeError→接住`，修的是讀側處置閘，不是這個寫側入口。
- 現成前置處理是 `lumos quote-check <report> --spec <snapshot>`：它已捕捉 `UnicodeDecodeError` 並回 rc2：
  [cmd_quote_check](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:23085)
- 處置閘讀側也已將相同情況轉成可理解的 quote-check FAIL，而非 traceback：
  [scripts/lumos:22947](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:22947)
- 載體報告的對稱入口已修：非法 UTF-8 report 會受控 rc2，並有 `t_canary_carrier_invalid_report_encoding`：
  [scripts/lumos:9526](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:9526)

### 應保留的相容邊界

- 最小解是沿用 `cmd_quote_check`／讀側既有模式，在載體 snapshot 解碼處捕捉 `UnicodeDecodeError`，回 rc2、指出 `--snapshot` 編碼錯誤，且帳逐位元不變。
- 維持嚴格 UTF-8；不可使用 `errors="replace"`，否則引句可能對著被改寫的文字驗證。
- 只收緊載體席；非載體目前只留路徑與原始 bytes 雜湊，既有政策不要連帶改變。
- 保留現有分流：缺檔仍走 snapshot I/O 訊息、空檔仍走空檔訊息、有效 UTF-8 零引句仍走「沒有引句」、全錨載體仍成功。
- 指紋必須沿用同一份已解碼原始 bytes；不可解碼一次、之後另讀新版檔案卻把新版 hash 當成已驗證。
- 現有硬合約沒有直接規定這個入口必須 rc2；相關硬合約是「宣稱成功必已落盤可讀回」。因此若修，應依既有計劃指示補一條專屬輸入契約及普通／`-O` 正反測試，而不是擴成全 repo 編碼整治。

結論：先跑 `quote-check` 已能避免直接撞 traceback；真正減少入口證據錯誤與重記的局部修法，是把同一個受控 rc2 判定搬進載體 `cmd_canary`，不改其他入口。全程未改檔、未跑全套、未動 Git。