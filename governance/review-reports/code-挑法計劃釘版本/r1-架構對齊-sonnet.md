severity: minor

## A1 新釘的提交不是這兩支樣本檔最後被改的提交,但仍合法
severity: minor
blocking: 否
引句:「configs/ast-grep/kotlin-choice/samples/arid.kt@4ad615e0e7a1:18」

既有做法:釘版本的寫法是 `路徑@<至少 12 位提交編號>:行號`。這個形狀在 `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:66` 和 `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:42` 有定義。條件有四項:
- 提交編號至少 12 位。
- 提交在某個分支的歷史上。
- 該提交裡有這個路徑。
- 行號在檔長之內。

對照結果:
- 這份 diff 的寫法跟專案既有的一樣,只換了提交編號,仍是 12 位。
- 舊編號 `f618b62cde0b`(一則 docs 提交)和新編號 `4ad615e0e7a1` 都是 `Lumos/main` 的祖先。`merge-base --is-ancestor` 對兩者都回 0。
- 這兩支檔在新提交裡存在:`arid.kt` 95 行、`choice.kt` 71 行。行號 18、58 到 69 都在檔長內。
- 第 58、60、61、69 行在 `4ad615e0e7a1`、`8332cc620` 和 `f618b62cde0b` 三個版本裡內容逐字相同,所以換提交不會讓行號指向別的內容。

差在哪:任務說明寫「樣本檔最後被改的提交」,實際不是這樣。
- `git log -1 Lumos/main -- samples/arid.kt` 和 `samples/choice.kt` 都回 `8332cc620`(2026-11-14)。
- `4ad615e0e7a1`(2026-11-22)只在 `configs/ast-grep/kotlin-choice/samples/` 目錄下新增了 `choice-batch3.kt`,沒改這兩支檔。
- 所以 `4ad615e0e7a1` 是「樣本目錄最後被改的提交」,不是「這兩支檔最後被改的提交」。
- 這不影響 refcheck 或筆記形狀閘的驗證結果。如果 commit message 或計劃裡寫成「檔案最後被改」,措辭就對不上,建議改成「樣本目錄最後被改」,或改釘 `8332cc620`。

補充:`grep 'kt@'` 只命中這一篇,專案裡沒有別的 `.kt@<提交>:` 釘版本可以對照,其他釘版本的寫法都在規則說明文字裡。

最嚴重:minor
blocking 條數:0
