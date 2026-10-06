severity: major

## integration-F1

severity: major  
blocking: 是  
引句:「當有效兩行來源第一行字串含 Unicode 或控制分隔符時」  
file: `scripts/test_lumos.py:69723`

測試把八種分隔符直接放入 Python 單引號字串，再於 `scripts/test_lumos.py:69725` 呼叫 `compile`。具體輸入 `\v`、`\f`、U+2028 等都會先得到 `SyntaxError`，尚未執行 `_validate_repo_ref`，因此紅燈不能證明實際換行判法有錯，也無法在修正後轉綠。改用三引號字串可同時保留實體分隔符與「有效 Python」前置條件。

其餘界線內未見新增語意政策、共用入口分叉或 tuple／CLI 返回值設計錯誤；BOM、CR 解碼及目錄釘版／工作樹不對稱均有保留。

已讀材料：

- `docs/lumos-toolchain-knowledge/Projects/引用座標依實際換行_計劃.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Systems/lumos-refcheck.md`
- `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- `docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md`
- `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`