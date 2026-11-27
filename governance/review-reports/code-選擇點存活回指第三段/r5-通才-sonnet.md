severity: major

severity: major
blocking: 是
`scripts/lumos:81094-81102`(`_choice_layer_not_body`)。這次修補要讓「讀取器讀不到的節留在正文、內容不會兩邊都看不到」,但標題是先經 `_CHOICE_HEAD_RE` 拿掉結尾的 `#` 收尾符,才交給讀取器的兩條正規式判。讀取器自己拿的是原始行 `ln.strip()`(`_h2_section_lines`,`scripts/lumos:13973`),所以兩邊對「`## 驗收條款 ##`」的判斷不同。這是合法的 ATX 標題寫法。結果是這一節被排出正文,讀取器又讀不到,內容兩邊都看不到,正是 r4 架構對齊 #1 要消滅的情形。同類還有:沒有任何二級標題在前、直接出現的 `### 驗收條款`。這時 `stack[0]` 是三級標題,它也被排除,讀取器的 `^##\s+` 同樣不認。兩個寫法在這份計劃裡都沒有對應測試。
引句:「return bool(_KT_SIT_ACCEPT_H2_RE.match("## " + t) or _EXPECTED_H2_RE.match("## " + t))」
最小重現(已在 `/Users/enzo/harness/lumos-reach3` 跑過):對 `"## 驗收條款 ##\n- [S1] x\n"` 呼叫 `m._choice_plan_sections(...)`,回傳 `[]`;對同一份文字呼叫 `m._h2_section_lines(text, m._KT_SIT_ACCEPT_H2_RE)`,回傳 `None`。`"### 驗收條款\n- [S1] x\n"` 的結果也一樣。對照組 `"##\t驗收條款"` 兩邊一致(正文為空、讀取器有讀到),所以問題只出在收尾符與層級判法上。

severity: minor
blocking: 否
`scripts/lumos:81080-81086` 的註解 ② 仍寫「整行比對:前面可帶一個不含空白的記號加空白,節名後只容空白、一個括號說明…」,以及「語料是 `_CKL_REAL_HEADS`(…)」。這些描述的是剛被刪掉的 `_CHOICE_LAYER_NOT_BODY_RE`,現在的判法改成直接呼叫讀取器正規式,節名後的說明已不再排除。讀註解的人會被誤導。
引句:「驗收條款」「預期值表」整行比對:前面可帶一個不含空白的記號加空白,節名後只容空白、一個括號說明」

其他驗收項目:
- 交叉引用正規式改成 `〈[^〈〉]*〉` 是對的。我用「整個標題就是〈審計修正紀錄〉」「`〈審計修正紀錄 〈x〉`」「`〈審計修正紀錄 〈x〉 附錄`」三種寫法驗過,沒有問題。
- `_choice_layer_not_body` 只有 `scripts/lumos:81115` 一處呼叫,`_CHOICE_LAYER_NOT_BODY_RE` 已無其他引用。
- `python3.14 scripts/test_lumos.py -k choice_plan_sections` 跑出 10 passed、0 failed。

總結:最高等級是 major
