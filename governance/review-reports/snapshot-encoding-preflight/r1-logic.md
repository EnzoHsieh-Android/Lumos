severity: major

## logic-F1

severity: major

blocking: 是

引句:「缺檔OSError分流不得改成編碼診斷，不新增集合數量等式。」

S3 只控制「持續缺檔」，漏掉一次性 I/O 失敗。現行流程第一次 `read_bytes()` 遇 `OSError` 時只把 `_qrows` 設為 `None`，不立即拒收；稍後若 `_sha256_file()` 恢復成功，因沒有 `_validated_sha["--snapshot"]`，便跳過同份內容比對並繼續 append。

具體輸入：載體快照實際為非法 UTF-8，第一次讀取因網路檔案系統或注入故障拋一次 `OSError`，第二次雜湊讀取成功。錯誤結果：非法快照未解碼、引句未驗證，卻可能 rc0 並追加成功帳，直接違反 S1。現有缺檔控制會因兩次讀取都失敗而通過，抓不到這條路。

修正規格與紅測：任何載體驗句階段的 `OSError` 都應立即以 I/O 診斷 rc2；增加「第一次 `read_bytes` 拋 OSError、第二次可讀」控制，並驗證帳逐位元不變。不得以後續 raw-byte 雜湊成功代替引句驗證。

源碼佐證 file: `scripts/lumos:9576`、`scripts/lumos:9583`、`scripts/lumos:9604`、`scripts/lumos:9612`、`scripts/lumos:9679`

測試缺口 file: `scripts/test_lumos.py:25886`

## 已讀、無其他 finding

- S2：LF／CRLF 都走相同嚴格解碼，引句正規化不改原 bytes；帳內指紋取 raw bytes。非載體不進快照解碼，政策保持。
- S4：RuntimeError 普通及 `-O` 控制能殺掉廣捕捉；應只捕捉 `UnicodeDecodeError`。
- 最小重現、回退、三版紅燈與 mutant 收據敘述彼此未混稱；生產 CLI 確實未修改，SHA256 實核為 `52c9c4d7…0276`。
- 合約：`Systems/design-loop` 唯一 INVARIANT 不受破壞；審材是 `.md`，S1–S4 均有存在的測試方法綁定，未冒稱 S4 已隨舊三條規格閘跑過。
- 併發除 F1 外，hash 後至 append 的跨程序換檔已明確排除，且處置閘會重驗 SHA；效能、資源、對外送出、金流、回退及不可逆性未見新增洞。
- `refcheck` 實跑：0 個壞引用。
- 42 條紅測因唯讀環境沒有可用臨時目錄而無法重跑；這是審查環境限制，不列產品問題。

總結：最高 severity 為 major；blocking finding 共 1。

已讀材料：

`governance/review-reports/snapshot-encoding-preflight/r1-snapshot.md`  
`scripts/lumos`  
`scripts/test_lumos.py`  
`governance/review-reports/snapshot-encoding-preflight/preflight-intake.md`  
`governance/review-reports/snapshot-encoding-preflight/r1-graph-context.txt`