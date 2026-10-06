severity: clean

已完整逐節讀完凍結 spec；零 finding。回退方式可保留已獨立提交的紅燈測試，既有 BOM、CR/CRLF、空行、尾端換行、無行號，以及目錄在釘版／工作樹間的不對稱語義均有明確兼容條款與測試。界線僅涵蓋本次設計造成的回退或既有引用退化；不評既有缺陷、Windows 相容性或尚未修改的生產碼。

已讀材料：

- `governance/review-reports/source-coordinates/r1-snapshot.md`
- `docs/lumos-toolchain-knowledge/Projects/引用座標依實際換行_計劃.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Systems/lumos-refcheck.md`
- `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- `docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md`
- `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`