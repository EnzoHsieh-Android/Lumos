severity: minor

## resources-F1
severity: minor  
blocking: 否  
引句:「涉及 `scripts/lumos` 的 cmd_seat_check 與 `scripts/test_lumos.py` 的席位對帳測試。」  
file: `governance/review-reports/seat-input-validation/r1-snapshot.md:11`  
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:112`

計劃把結果落進 `Systems/lumos-cli-read`，但該節點正文的責任是圖譜 read/traverse 14 原語；`seat-check` 是審查報告、派工單與越界帳的對帳功能，還可能寫 ledger，不屬於這 14 個原語。照目前設計寫回會讓系統責任混雜。應另開席位對帳 System，或先明確擴寫既有節點責任。

完整凍結 spec 已讀。形態預檢、材料讀取順序、帳本不寫、普通／`-O` 一致性，以及真 CLI／真函式 AST 的測試可達性均有對應斷言；未發現會導致錯誤產品行為的 major/blocker。依限制未執行真 CLI，59 pass／80 fail 未獨立重驗。

已讀材料：

- `governance/review-reports/seat-input-validation/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Projects/驗證層自證三件_計劃.md`
- `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md`
- `governance/review-reports/seat-input-validation/preflight-intake.md`
- `governance/review-reports/seat-input-validation/r1-graph-context.txt`