severity: minor

## 1. verdict: evidence

觀察已重現：Python `json.loads` 將  
`{"materials":["must-read.md"],"materials":[]}`  
解析為 `{"materials": []}`。

最強支持：前一個 `materials` 值確實消失，可能直覺上符合「錯形態不能當有效空清單豁免」的疑慮（`governance/review-reports/seat-input-validation/r1-snapshot.md:48`）。

決定性反證：

- 本案明定驗的是「解析後」形態：頂層須為 dict，`materials` 接受缺省、null 或清單（`governance/review-reports/seat-input-validation/r1-snapshot.md:34-35`）。
- S3 明定空清單維持 rc0、vacuous（同檔 `:43`）。
- 舊 S1 同樣明定空 materials 豁免，且整體只是觀測、不阻擋（`docs/lumos-toolchain-knowledge/Projects/驗證層自證三件_計劃.md:33-36`）。
- 現行程式也是 `json.loads` 後取值，空清單直接 vacuous（`scripts/lumos:23296-23310`）。

因此，這個輸入沒有違反本案任何具體驗收條款；若要拒絕重複名稱，必須新增「原始 JSON member 名稱唯一」合約並改解析邊界，不能算成本案資料形態修正的必修錯行為。RFC 的 SHOULD 與 Python 保留最後值只證明觀察合理，真正排除必修的是上述 spec／S1 範圍。

## 2. finding

- severity: minor
- blocking: true
- 問題：現有 `lands_in` 指向 `Systems/lumos-cli-read`（`governance/review-reports/seat-input-validation/r1-snapshot.md:11-12`），但該節點責任限於 14 個圖譜 read/traverse 核心原語（`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:107-117`）；`seat-check` 不讀圖譜 Env，也不屬這 14 個原語。
- 正確落點：`Systems/design-loop` 已明載收貨三道及 `seat-check` 的 materials、vacuous、觀測語意（`docs/lumos-toolchain-knowledge/Systems/design-loop.md:56`），且同樣認領 `scripts/lumos`（同檔 `:149-166`）。

結論：本案脈絡應寫回既有 `Systems/design-loop`。兩篇都認領同一支檔不構成衝突；判準是各自責任，而非唯一檔案歸屬。