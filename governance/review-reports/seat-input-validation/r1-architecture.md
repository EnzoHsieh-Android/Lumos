severity: minor

凍結 spec 67 行已完整讀取。未發現會改變只觀測語意、跨層直呼或引入第二套驗證機制的 major/blocker。

架構四問：

① 分層與依賴方向：一致。驗證留在既有 `cmd_seat_check` 輸入邊界，之後才讀材料；未新增依賴或治理層。對照 `scripts/lumos:23281`、`scripts/lumos:23311`。

② 命名、例外及返回碼：一致。具體欄位 `ValueError` 進既有輸入失敗 rc2；合法觀測仍 rc0，符合鄰近 `quote-check`／`refcheck` 的 rc2 慣例。對照 `scripts/lumos:23063`、`scripts/lumos:40058`。

③ 是否引入第二種做法：否。沿用 `isinstance`、既有例外分支及原命令，未建立 schema 引擎；三支紅測也直接守真入口。對照 `scripts/test_lumos.py:33999`、`scripts/test_lumos.py:34071`。

④ lands_in 落點：既有節點較合適，但需補準責任描述，見下列 finding。

## architecture-F4

severity: minor  
blocking: 否  
引句:「最小修正在 cmd_seat_check 的既有讀取邊界，只補資料形態檢查」  
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:112`  
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:119`  
file: `governance/review-reports/seat-input-validation/r1-graph-context.txt:4`

`lands_in` 指向既有節點符合「一支檔一個家」，但該節點目前自稱只管 14 個圖譜 read/traverse 原語，原語清單也沒有 vault-free、可選寫越界帳的 `seat-check`。若照字面只補實作與摘要，下一次查責任邊界會看不出此命令的 rc0/rc2 與帳本例外。實作寫回時應擴充該節點責任範圍並列入 `seat-check`；不宜另開第二個同樣認領 `scripts/lumos` 的家。

已讀材料：

- `governance/review-reports/seat-input-validation/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Projects/驗證層自證三件_計劃.md`
- `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md`
- `governance/review-reports/seat-input-validation/preflight-intake.md`
- `governance/review-reports/seat-input-validation/r1-graph-context.txt`