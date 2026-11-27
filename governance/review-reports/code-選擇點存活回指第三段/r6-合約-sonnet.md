severity: major

severity: major
blocking: 是
scripts/lumos:81114(`_choice_plan_sections` 的 `taken` 判斷)。`_choice_reader_lines` 取的是 `_h2_section_lines` 的行,而那支只回圍欄外的可見行。驗收條款或預期值表節裡的圍欄(程式碼區塊)內容和圍欄標記行不在 `taken`。逐行迴圈只靠 `no not in taken` 決定要不要收進正文,所以這些行會漏進計劃正文,而且正文會多出一段 `〈驗收條款〉`。r5 之前整節被排除時不會這樣,所以這是這輪修補新引入的退步。它也違反計劃和 Systems/規格閘寫的「正文不含〈驗收條款〉〈預期值表〉」和「每一行恰好在一邊」。新測試 `t_choice_plan_sections_reader_complement` 沒有含圍欄的案例,所以抓不到。
- 最小重現:對 `"---\ntype: project\n---\n## 驗收條款\n- [S1] 甲\n```\nsecret_fenced\n```\n## 範圍\n丙\n"` 呼叫 `_choice_plan_sections`。回傳 `[('〈驗收條款〉', '```\nsecret_fenced\n```'), ('〈範圍〉', '丙')]`,`_choice_reader_lines` 只回 `[5]`。
- 現行 repo 的計劃檔掃過,沒有實際撞到這個形狀,但判法本身有洞,而且 r5 剛宣稱這類位置已處理。
引句:「            if no not in taken:」

severity: minor
blocking: 否
scripts/lumos:81114。標題用 tab 的 `##<tab>範圍` 跟在驗收條款節後面時,`_CHOICE_HEAD_RE` 認它是標題,但 `_h2_section_lines` 用 `startswith("## ")` 判節尾,不認 tab。所以讀取器沒結束、把下一節的內容讀走,正文因此少了那一節。重現:`"## 驗收條款\n- [S1] 甲\n##\t範圍\n丙\n"` 回傳 `[]`,讀取器行號是 `[5, 7]`。這符合「以讀取器為準、恰好一邊」的字面,只是範圍節在正文裡消失。新測試的 tab 案例只測了驗收條款標題本身,沒測 tab 的後續標題。
引句:「前面沒有二級標題的 `### 驗收條款`、tab 與全形空白。」

三問結果:
- **修到沒**:結尾井號、前面沒有二級標題的 `### 驗收條款`、全形空白這幾案都過,`t_choice_plan_sections` 系列 12 支全綠。
- **有沒有引入新問題**:有,就是上面的圍欄漏進正文。
- **同類位置**:還有 tab 後續標題這一處。
- **圖譜一致**:計劃第 92 行與 Systems/規格閘的 WHY 和 PITFALL 已換成新判法,`[test:t_choice_plan_sections_reader_complement]` 也在。`t_docs_command_count` 綠。`drift scan` 沒點到這次的筆記,只點到「回合結束寫法檢查」與「筆記內容閘」這兩篇無關的筆記。

總結:最高等級是 major
