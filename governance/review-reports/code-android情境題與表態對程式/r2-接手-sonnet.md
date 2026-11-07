severity: minor

我照文件在 `/tmp/lumos-seat-work/code-android情境題與表態對程式/接手-sonnet/` 的最小 repo 實跑了推送前情境題流程。結果如下,下面的 F1 到 F5 都是文件、訊息和程式不一致,不是功能壞掉。

- **擋下與段放行:** 擋下訊息印的 `lumos lint-waive kt-situation:<段身分> --rule kt-situation --file app/Screen.kt --note "..."` 照抄能跑。放行後 `code-loop check` 通過並印「⚠ kt-situation 有 1 段段放行」。
- **環境不可用:** 把 lumos 複本放進沒有型錄的環境,只提醒、不擋,治理帳多一筆 `fail-open`。
- **型錄與依據來源:**
  - `check.py --catalog-only` 回「型錄問題 0 個」。
  - 56 列裡 5 列標了 `(換列)`,D-1、D-2、D-8、D-9、D-50。這 5 列的例外全是 `(無)`,其他列的「不適用時」都沒有該標而漏標的。
  - 新增的兩個網址(ast-grep test、Semgrep testing-rules)都回 200,內容分別有 validated/noisy/missing/reported 與 `ruleid:`/`ok:`,支持那句。

**F1**
severity: minor
blocking: 否
引句:「代碼審 r1 D2 提前上線,形狀改成直接沿用」
計劃的範圍 5 已寫成提前上線,但同一篇還有三處照舊,跟新句子打架:
- `Projects/Android寫法語意情境表態與盲判_計劃.md:101` 的 REVISIT 仍寫「實作範圍 4–6(盲判記錄、段放行、提示)」,把段放行當成還沒做。
- `:67` 與 `:85` 的 S6 仍把 `situation-waive` 事件當成要有的東西。
- `:82` 的 S3 仍寫「從治理帳的所有 `blind-judge` 與 `situation-waive` 事件重建」。

這些事件程式裡不存在,實際用的是 `lint-waive`。S3 到 S7 綁的 `t_blind_judge_*`、`t_pitfalls_situation_blind_judge_hint`、`t_gov_stats_situation_agreement` 在 `scripts/test_lumos.py` 也都沒有,這是範圍 4 到 7 沒做所以綁不到,不是這輪新增的缺口。

**F2**
severity: minor
blocking: 否
引句:「〈用詞〉的 _kotlin_strip,情境題切段用」
`_kotlin_strip` 在程式裡不存在,`scripts/lumos:6827` 的 docstring 與計劃 `:33` 都只是在引用這個名字。實際入口是 `_strip_c_comments(kotlin=True)`,掃描本體是 `_kt_strip_spans`。計劃一次都沒提到真名,拿計劃去 grep 會找不到。`Systems/棧別提問表態閘.md:55` 寫的才是對的。

**F3**
severity: minor
blocking: 否
引句:「6. 段材料是從命中行往上最近的頂層或類別層宣告(函式、屬性或類別,最多 120 行)」
這輪改了「段材料」的定義(頂層或類別層宣告),但計劃還有兩處沿用舊說法:
- `:32` 寫「同一個段材料(同一個函式)」「跨函式邊界一律切開」。
- `:64` 寫「其餘在整個段材料(包住它的函式)」。

另外天花板這邊新加的第 6 點排在第 5 點前面(diff 裡是「+6.」先於「+5.」),編號順序亂了。

**F4**
severity: minor
blocking: 否
引句:「型錄在但讀不懂,修好型錄後再跑」
型錄在但讀表失敗時,擋下訊息只說「修好型錄後再跑」,沒印型錄路徑。我設了壞型錄跑 `code-loop check`,訊息最後的「接下來」仍是重填表態,但重填救不了這種擋下。消費專案的型錄在工具鏈裡,使用者改不到,而且這種擋下沒有段可放行。「環境不可用」那句則有雙重括號和「找不到Kotlin」缺空格的小瑕疵。

**F5**
severity: minor
blocking: 否
引句:「在「不適用時」格子開頭標 `(換列)`、例外寫 `(無)`」
型錄說明寫「格子開頭」,但 `configs/ast-grep/kotlin-android/check.py:185` 的判法是「格子裡任何位置有 `(換列)`」。我把 D-4 的 `(換列)` 放在句子中間,工具照樣判成換列並要求例外是 `(無)`。這只是措辭精度,結果對使用者無害。

總結:最嚴重是 minor(五條文件與程式的措辭或同步落差),會擋 0 條。
