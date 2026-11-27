severity: minor

我跑了修補差異裡的判法。「驗收條款」「預期值表」改用讀取器的兩條判法,這個方向對,但「讀取器讀不到的留在正文」這個前提在有閉合井號的標題上不成立。`〈…〉` 交叉引用的新正規式、`〈審計修正紀錄〉` 整個標題的特例,走過幾個輸入都沒問題。

severity: minor
blocking: 否
`scripts/lumos:81102`(`_choice_layer_not_body`),搭配 `_CHOICE_HEAD_RE`(`scripts/lumos:81093` 附近)。

失敗場景:計劃裡有 `## 驗收條款 ##` 或 `## 預期值表 #`,也就是帶閉合井號的 ATX 標題。

- `_CHOICE_HEAD_RE` 會先把結尾的 `#` 去掉,傳進 `_choice_layer_not_body` 的 title 是乾淨的「驗收條款」。這一節就被當成非正文,排除了。
- 讀取器 `_h2_section_lines` 拿的是整行 `ln.strip()`,對 `^##\s+驗收條款\s*$` 比對,多出來的 ` ##` 讓它比不上,所以讀取器讀不到這一節。

我實跑的結果:

- `_h2_section_lines(txt, _KT_SIT_ACCEPT_H2_RE)` 與 `_h2_section_lines(txt, _EXPECTED_H2_RE)` 都回 `None`。
- `_choice_plan_sections(txt)` 只回 `[('〈範圍〉','甲')]`。
- 結果:那節的 `- [S1] 條` 在判讀材料、第 1 層和第 4 層依據、deps_sha 的任何一個讀者裡都看不到。這正是 r4 想堵的「內容兩邊都看不到」。

原因:`_choice_layer_not_body` 收到的是已去掉閉合井號的標題,卻拿它去「重建」讀取器看到的原行。重建的行跟讀取器實際看到的行不一樣。

引句:「return bool(_KT_SIT_ACCEPT_H2_RE.match("## " + t) or _EXPECTED_H2_RE.match("## " + t))」

最小重現:`_choice_plan_sections("---\ntype: project\n---\n## 範圍\n甲\n## 驗收條款 ##\n- [S1] 條\n")`。結果沒有〈驗收條款〉段,而 `_h2_section_lines` 同樣讀不到它。

這個標題寫法在 repo 的真標題語料裡沒有出現過,影響面窄,所以只給 minor。測試語料(`_CKL_REAL_HEADS` 與 `fake`)也沒有帶閉合井號的案例,抓不到。

修補三問:

- **修到沒**:修到了,驗收條款與預期值表的帶說明、變體標題改成跟讀取器同判,新的測試期望一致。`_CHOICE_LAYER_XREF_RE` 只拿掉閉合的一組,`〈審計修正紀錄 〈x〉` 與 `〈審計修正紀錄〉` 走過都對。
- **有沒有引入新問題**:有上面這一個。
- **同類位置**:全形空白(`\u3000`)與 `\xa0` 兩邊判得一致,沒問題。縮排標題兩邊都不認,也一致。

總結:最高等級是 minor。
