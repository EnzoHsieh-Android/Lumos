severity: clean

無架構 finding。凍結 spec 沿用現有收貨邊界與共用引句解析，沒有跨層直呼或建立第二套解析器。

## 四問

① 分層依賴：已讀，無 finding。`cmd_canary` 在 CLI 收貨邊界讀取快照，再交給共用 `_quote_rows`；`quote-check` 亦使用同一核心。  
file: `scripts/lumos:9576`  
file: `scripts/lumos:22352`  
file: `scripts/lumos:23085`

② 命名／例外／返回碼：已讀，無 finding。報告入口與 `quote-check` 都把 `UnicodeDecodeError` 視為材料錯誤並回 rc2；本案只把快照入口目前僅捕捉 `OSError` 的缺口補成同一形狀，且以 `--snapshot` 定位。非編碼 `RuntimeError` 仍向外傳遞。  
file: `scripts/lumos:9528`  
file: `scripts/lumos:9583`  
file: `scripts/lumos:23092`  
file: `scripts/test_lumos.py:25867`

③ 第二種做法：已讀，無 finding。spec 明定不新增解析器；設計仍以 `_quote_rows` 為唯一解析核心，快照原始 bytes 同時供解碼及 SHA256，後續再驗 hash、變動即在 append 前拒收。  
file: `scripts/lumos:9580`  
file: `scripts/lumos:9581`  
file: `scripts/lumos:9608`  
file: `scripts/lumos:9679`

④ lands_in：已讀，無 finding。唯一落點 `Systems/design-loop` 正是 `scripts/lumos` 的既有 home，且該節點已記錄此入口的局部輸入契約；不需要另開編碼解析系統。  
file: `docs/lumos-toolchain-knowledge/Projects/載體快照非法編碼受控拒收_計劃.md:10`  
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:154`  
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:229`

## 合約與風險

處置閘第五步合約不受影響：S1–S4 均有測試綁定、回退節完整，且本案不改條款判定。第六步 lands_in 亦符合。  
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:49`  
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:51`

併發：保留驗證後重算 hash 的換檔拒收。效能／資源：仍單次讀入 bytes，無背景工作或額外解析層。回退：只撤快照解碼拒收分支。對外送出、金流及不可逆均排除，因流程只讀本機材料並 append 既有本機帳。守衛面由普通／`-O`、Runtime、缺檔、合法 LF/CRLF、帳本逐位元不變控制覆蓋。  
file: `scripts/test_lumos.py:25829`  
file: `scripts/test_lumos.py:25886`

CLI SHA256 已核對為 `52c9c4d7…f3760276`；現碼快照分支仍只捕捉 `OSError`，與「正式生產 CLI 尚未修改」一致。refcheck 實跑：ok 0／missing 0／out_of_range 0。各 spec 節、preflight-intake、graph-context 均已讀，無 finding。

最高 severity：clean；blocking：0。

已讀材料：

- `governance/review-reports/snapshot-encoding-preflight/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/snapshot-encoding-preflight/preflight-intake.md`
- `governance/review-reports/snapshot-encoding-preflight/r1-graph-context.txt`