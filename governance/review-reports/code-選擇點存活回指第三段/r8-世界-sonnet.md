severity: major

## w1 條款的續行與子清單只扣定義行,條款自己的一部分被當成「正文寫了」
severity: major
blocking: 是

世界做法:條款與敘述的界線是「結構區塊」,不是「一行」。
- StrictDoc 的條款是整個 `[REQUIREMENT]` 區塊,多行 STATEMENT 用 `>>> … <<<` 圈起來。
- StrictDoc 的 Markdown 格式把沒有 `**Key**:` 標頭的散文累積成隱含的 STATEMENT 欄位。
- Gherkin 的 Scenario 把 Given、When、Then 的續行都歸給該 Scenario。
- doctest 把提示符號後的續行歸給該範例。

我們的做法只扣定義行(`[SN]` 之後到行尾),同一條款的續行與縮排子清單都留在「計劃正文」。

重現一(合成輸入):

```
## 條款
- [S1] 選擇點存活時回指到條款
  續行說明:例外是 iOS 不適用
  - 子項 A:只在 Android
```

跑 `_choice_plan_view` 的結果:
- clauses 為 `{'S1': '- [S1] 選擇點存活時回指到條款'}`。
- sections 為 `[('〈條款〉', '續行說明:例外是 iOS 不適用\n  - 子項 A:只在 Android'), …]`。
- 條款的續行與子項進了 sections。第 2 層的規則是「quote 在那一段裡找得到,而且不在任何條款原文或預期值表列裡」。這兩行同時滿足,會被判成「只寫在正文、條款沒收」。

重現二(repo 真實計劃 `新增告警閘_計劃.md`):
- 第 67 行 `- [S1] …[test:t_lint_new_declaration]` 是定義行。
- 第 68 行是它底下的縮排子項 `  - **沒有副檔名的檔要看第一行**…[test:t_lint_shebang_ext]`。
- 輸出:`S1 bound: True`,`refs = ['t_lint_new_declaration']`。
- 第 68 行整行進了 sections 的〈條款〉段(`'t_lint_shebang_ext' in sections` 為 True)。
- 同一個測試名不在 `block` 裡(`'t_lint_shebang_ext' in block` 為 False)。
- 後果:這條子項有自己的 `[test:]`、也是 S1 的細節,卻被當成「正文寫了、條款沒收」。依第 2 層的「規格已決定,只在正文」判法,這條子項會被歸成第 2 層(該照正文補條款),但它其實是 S1 的一部分、已有測試。第 3 層對它的處理也看不到這個測試。

重現三:用 `scan.py`(`/tmp/lumos-seat-work/code-選擇點存活回指第三段/r8-世界-sonnet/scan.py`)掃 `docs/lumos-toolchain-knowledge/Projects/`。248 篇有條款的計劃裡,12 篇在定義行下一行就有縮排續行,且那行落進 sections。例如:
- `代碼審資安席_計劃.md`(6 條裡有 4 條)
- `推播miss量測_計劃.md`(6 條裡有 4 條)
- `檢索核心重建_計劃.md`(8 條裡有 6 條)
- `節點範圍與索引守衛_計劃.md`(13 條裡有 6 條)
- `新增告警閘_計劃.md`(16 條裡有 4 條)

規格〈用詞〉寫了「條款旁的說明句照樣留在正文」,所以這是明文取捨。它在「說明句」上站得住,在「條款自己的續行與子項」上站不住:世界工具會把這些歸給條款,而且 repo 裡已有 12 篇這樣寫。

建議:
- 把條款區塊定成「定義行加上其後縮排更深的連續行,到空行或下一個同層以下的項目為止」,同時扣掉並併入 `clauses`。
- 或在視圖裡給第 2 層標「這段是某條款的續行」,不讓它當「條款沒收」的證據。

引句:「taken = _choice_reader_lines(text) | set(clause_lines)」
來源:https://strictdoc.readthedocs.io/en/latest/strictdoc_01_user_guide.html
file: `/Users/enzo/harness/lumos-reach3/scripts/lumos:81120`

## 附:查了什麼

查詢:
- WebSearch「StrictDoc requirement multiline STATEMENT field vs free text sections; Doorstop item text; Sphinx-needs need directive content」。結果只涵蓋 StrictDoc。
- WebFetch 讀 StrictDoc 使用者指南,回 404,沒有取得內容。

讀過的來源:StrictDoc 文件站的搜尋結果摘要,包括文法與 Markdown 規格頁。
- StrictDoc 用 `>>> <<<` 圈多行欄位。
- 它的 Markdown 規格頁說沒有 `**Key**:` 標頭的散文累積成隱含 STATEMENT。
- Doorstop、Sphinx-needs、OpenFastTrack、Gherkin、doctest 沒有查到可引的頁面。這幾項只靠一般知識(Gherkin 與 doctest 的續行歸屬),沒有逐字引文,不當硬證據。

讀過的程式與規格:
- `/Users/enzo/harness/lumos-reach3/scripts/lumos` 的 `_choice_plan_sections`、`_choice_plan_view`、`clause_bindings`、`_h2_section_lines`。
- 規格〈用詞〉計劃正文那段。

實測:
- 合成輸入:續行、非標準標題、表格列、標題式條款、Gherkin 式縮排。
- repo 掃描:`Projects/` 下 248 篇有條款的計劃。
- 合成輸入裡,表格條款與標題式條款也是類似行為:只扣定義行,表格的後續列與標題底下的說明段留在正文。這兩種寫法 repo 裡沒掃過,屬同族,未逐一計數。

方向判斷:世界做法是「條款是區塊」,我們是「條款是一行」。這是同一族邊界裡尚未被封掉的一條,關鍵在續行與子項,不是標題或圍欄。

總結:最高等級是 major
