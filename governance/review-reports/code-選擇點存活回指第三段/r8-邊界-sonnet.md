severity: minor

修補本身修到了。`clause_lines` 的行號和 `_note_lines` 同源,我試了十種極端輸入,沒有任何一種讓條款定義行同時留在正文又留在條款。新測試在本機也通過。

| 輸入 | 結果 |
|---|---|
| 正文段落中間的條款定義行 | 條款只留在條款,前後的說明句照留正文 |
| 只在行內引用的 `[SN]` | 不算條款,正文照留 |
| 圍欄裡的 `[S1]` | 不算條款,圍欄內容留在正文 |
| 表格列、清單縮排的條款 | 兩者都被扣掉 |
| 條款定義行在 frontmatter 之前 | 條款被扣掉,不誤傷 |
| `clause_lines` 給空集合 | 照舊 |
| `clause_lines` 給不存在的行號或負數 | 照舊,不報錯 |
| 修補前版本(`clause_lines` 預設空) | 條款原文在正文裡,確認新測試的翻紅釘是對的 |

以下兩處同類位置的覆蓋面還不完整。

severity: minor
blocking: 否
`scripts/lumos:81173`:`_choice_plan_view` 只把每個條款編號第一次出現的 `r["line"]` 傳進去,同編號重複定義的第二行沒有被扣。重現:`## 驗收條款(說明)\n- [S1] 甲原文 [manual:人工看一次]\n- [S1] 重複原文 [manual:人工看一次]\n## 範圍\n丙`。結果 `sections` 是 `[('〈驗收條款(說明)〉', '- [S1] 重複原文 …'), ('〈範圍〉', '丙')]`,第二行的條款原文留在正文,第 2 層會把它當成「正文寫了」。重複編號在別處已被標成 duplicate 而擋下,所以實際影響小;`dup_lines` 目前沒被用到,補上就收斂。
引句:「secs = _choice_plan_sections(text, {r["line"] for r in rows})」

severity: minor
blocking: 否
`scripts/lumos:81128`:條款定義行本身是標題行(`### [S1] 標題條款原文 …`)時,該行走標題分支,不經 `taken` 過濾。條款原文因此成了段名,例如 `〈驗收條款(說明)〉/〈[S1] 標題條款原文 [manual:人工看一次]〉`,只要底下有內文就會出現在 `sections` 和 `all` 裡。重現:`## 驗收條款(說明)\n### [S1] 標題條款原文 [manual:人工看一次]\n段落\n## 範圍\n丙`。段名會把條款原文又帶進正文那一側,新測試沒涵蓋標題行條款。
引句:「taken = _choice_reader_lines(text) | set(clause_lines)」

總結:最高等級是 minor。
