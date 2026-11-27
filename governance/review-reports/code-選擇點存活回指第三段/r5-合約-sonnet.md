severity: major

這輪修補本身修到了,但發現一處註解與實際行為相反,三個月後接手的人看了會照錯的規則去改判法。

驗收結果:
- `python3.14 scripts/test_lumos.py -k t_docs_command_count` 綠(4 passed)。
- `-k t_choice_plan_sections` 綠(10 passed)。
- `python3.14 scripts/lumos drift scan` 沒有點到這次的計劃或 `Systems/規格閘`。
- 計劃〈用詞〉計劃正文、`Systems/規格閘` 新改的行、程式的實際判法三者一致:「驗收條款」「預期值表」都是整行相等,帶說明的標題留在正文。
- `Systems/規格閘` 引用的 [test:] 名稱都存在。
- `_choice_layer_not_body` 直接呼叫 `_KT_SIT_ACCEPT_H2_RE` 與 `_EXPECTED_H2_RE`,交叉引用正規式也確實只吃閉合的一組〈〉,修補有到位。

語料對照:我用 grep 掃 `docs/lumos-toolchain-knowledge` 下含這三個詞的二級標題,`Projects/` 底下的全部真標題都在 `_CKL_REAL_HEADS` 裡。語料裡另有幾條 grep 找不到的(「預期值表」、單獨的「審計修正紀錄」、「補設計審裁定與審計修正紀錄」、「驗收條款：候選規格…」),多收不要緊,只是來源已不在。

severity: major
blocking: 是
`scripts/lumos:81083`(同一段在 `scripts/test_lumos.py:152246` 也有)。程式上方註解仍寫著舊規則:前面可帶記號、後面容括號或冒號說明,正文 `驗收條款與範例` 這類。r4 之後實際判法是整行相等(`^##\s+驗收條款\s*$`)。所以 `驗收條款(全部有真測試、綠)` 與 `驗收條款：候選規格…` 在程式裡是正文,註解卻說會被排除。測試 docstring 也同樣過時,還有「驗收條款 」在 `fake` 表被標成排除。接手的人照這段註解去「修」判法,會把判法改回 r3 與讀取器不同套的形狀,正是 r4 要消除的問題。計劃、規格閘筆記與註解互相矛盾。
重現:`python3.14 scripts/lumos` 載入後 `_choice_layer_not_body("驗收條款(全部有真測試、綠)")` 回 False,而註解字面說「節名後只容…一個括號說明」要排除。
引句:「# ②「驗收條款」「預期值表」整行比對:前面可帶一個不含空白的記號加空白,節名後只容空白、一個括號說明(半形或全形」

severity: minor
blocking: 否
`scripts/lumos:81102`。標題尾端帶關閉井號時,兩邊判法對不上:`_CHOICE_HEAD_RE` 會把 `## 驗收條款 ##` 的尾端 `##` 去掉,於是判成排除。但讀取器 `_h2_section_lines` 用 `ln.strip()` 比對整行,不認這個標題,結果內容兩邊都看不到。這正是 r4 想避免的情況。repo 裡沒有這種標題,且單人自用,影響小。
重現:`_choice_plan_sections("# T\n\n## 驗收條款 ##\nfoo\n## 範圍\nbar\n")` 只回 `['〈範圍〉']`。
引句:「return bool(_KT_SIT_ACCEPT_H2_RE.match("## " + t) or _EXPECTED_H2_RE.match("## " + t))」

總結:最高等級是 major。
