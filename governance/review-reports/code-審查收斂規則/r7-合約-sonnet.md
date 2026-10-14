severity: minor

本席讀了文件修補、測試修補,以及 review-converge 工作樹裡的圖譜、手冊和 `scripts/lumos`。整體一致:新字樣各處都對得上,條款也有綁定測試。我另外跑了 `lint`(三個節點都是 0 問題)和六組相關測試(`t_reference_residual_lens_docs`、`t_pitfalls_residual_note_*`、`t_dispatch_lens_residual_*`、`t_doctor_residual_index_legacy_format`、`t_pitfalls_residual_graph_file_any_vault`、`t_pitfalls_ignores_git_external_diff_env`),全綠。

**逐項核對**
- 「只保證跑一輪高風險代碼審,審查席有沒有答沒有機械核對」:這句逐字出現在 reference.md、圖譜即合約.md(全形逗號,測試有換成半形再比)、templates §3、計劃 WHY 與 pitfalls-code-loop 的 WHY。06 用縮寫版「只保證跑一輪審,審查席有沒有答沒有機械核對」,code-loop SKILL.md 用「審查席有沒有答這題沒有機械核對」,意思一致。
- 舊說法「審查席看殘留決策與問答」「把挑答案變成被審查的事件」:在文件裡都改掉了。計劃第 116 行只在引述 r4 的原話,是歷史紀錄,可以留。
- `unresolved` 與舊格式:文件寫的跟程式一致。找不到、格式不合或撞名、筆記在 repo 外會記 `{"unresolved": 原因}`。理由句講原因、不叫人跑 `--reindex`;舊格式(沒有 notes 欄)才叫人 `--reindex`。doctor 把舊格式另報一行、不算內容不一致。
- 新 REVISIT 行:`REVISIT:2027-01-15 新增殘留段的必答題:…` 格式跟同組的四行一致。`lumos lint` 沒有報問題。
- 新測試都綁在計劃的 [S5] [S6] [S9] 條款上:
  - 鏡頭三支:`t_dispatch_lens_residual_new_not_crowded`、`t_dispatch_lens_residual_no_index_no_section`、`t_dispatch_lens_residual_unknown_not_cached`
  - 分級四支:`t_pitfalls_residual_note_unresolved_reason`、`t_pitfalls_residual_note_path_checked`、`t_pitfalls_residual_note_nfd_path`、`t_pitfalls_residual_graph_file_any_vault`
  - 外部差異一支:`t_pitfalls_ignores_git_external_diff_env`
  - doctor 一支:`t_doctor_residual_index_legacy_format`

**finding 1**
severity: minor
blocking: 否 — 只是提示文字講得比實際保證強,沒有破壞合約行或改變行為
引句:「新增殘留的推送會被判高風險,要過代碼審(審查席看這筆殘留決策與第二個代理的問答)」
問題:這輪把手冊、圖譜、計劃都改成照實寫「審查席有沒有答沒有機械核對」,但 `scripts/lumos` 裡還有四處舊說法沒跟著改。
- `guard residual --add` 成功後印的那句,就是上面的引句。
- 第 18857 行的註解寫「審查席看得到殘留決策與那幾筆問答,『挑到想要的答案』成為被審查的事件」。
- 第 44785 行的 `_residual_tier_hits` docstring 同樣寫「派工鏡頭把殘留決策與問答附給審查席、列一題必答」,沒補上「沒有機械核對」。
- 第 44508 行的升 high 理由句寫「附給審查席逐條答」。

計劃 [S8] 明文要求「lumos 的提示文字」每一處都寫明把關在高風險代碼審,而且講新增殘留段時「把關強度照實寫」。這四處沒達到。它們不在 `t_reference_residual_lens_docs` 的檢查範圍,所以測試是綠的。

失敗情境:編排者加完殘留,看到「審查席看這筆殘留決策與第二個代理的問答」,就以為會有人逐條核對,收貨時不自己看那題有沒有答。這正是 r6 合約席指出的落差。
佐證:``scripts/lumos:19332``、``scripts/lumos:44508``、``scripts/lumos:44785``、``scripts/lumos:18857``。後兩處的 docstring 與註解是我順帶讀到的,不是 r6 以來新增的。

**finding 2**
severity: minor
blocking: 否 — 條款有字面落差,不影響程式行為
引句:「④(r6 合約席)reference.md、圖譜即合約.md、templates §3、計劃 WHY 照實寫」
問題:計劃 [S8] 要求 templates §3、06、code-loop SKILL.md、reference.md、方法論與本計劃都照實寫把關強度。`t_reference_residual_lens_docs` 只逐字檢查四處(reference.md、圖譜即合約.md、templates §3、計劃 WHY)。SKILL.md 只比對「沒有機械核對」五個字。06 那一列的「只保證跑一輪審,審查席有沒有答沒有機械核對」完全沒被檢查,06 只被檢查「只改錯字也要過一輪高風險代碼審」。pitfalls-code-loop 的同句也沒有守衛,不過 [S8] 沒點名它。

失敗情境:有人把 06 那列的「只保證跑一輪審,審查席有沒有答沒有機械核對」刪掉或改回「審查席看…」,測試仍然全綠,條款卻在 06 變成假的。
佐證:``skills/lumos-project-notes/commands/06-代碼審與推送.md:20``(該列),``docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:74``([S8])。

**finding 3**
severity: minor
blocking: 否 — 只是措辭,不影響行為
引句:「把挑答案的那次推送送進一輪高風險代碼審才擋得住」
問題:這句在同一行 WHY 裡,跟括號裡剛加的「審查席有沒有答沒有機械核對」互相拉扯。「才擋得住」仍帶著保證的口氣。依 CLAUDE.md 鐵則 4,「沒有機械核對」那句本該只留在獨立的 REVISIT 行。現在新 REVISIT 行是加了,但計劃第 56、79、116 行和 WHY 裡仍留著原句。這是風格層級的落差。
佐證:``docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:32``。

最高等級 minor,blocking 0 條。
