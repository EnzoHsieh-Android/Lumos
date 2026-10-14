severity: minor

# 第六輪「合約與圖譜一致」席報告(修補範圍:文件、測試,lumos 程式只對照文件說法)

## 先講結論(白話)
這輪文件把「改到存著殘留決策的筆記就升 high」與「鏡頭內容例外從頂端讀」寫進了大部分地方。程式、測試與文件的字句大致對得上。我沒有找到會讓合約失效或讓測試假綠的問題。留下的都是「說法不齊、綁定漏列」的小漏洞。

我逐項核對的結果:
- 計劃與各文件列出的測試名,我在測試檔裡都找得到(`def` 都在)。
- 固定席節點的 ★INVARIANT★ 沒被破壞:guard-kill 的 rc 優先序與 `--json` 純度合約行這輪沒動。design-loop 處置閘第五步要求的「計劃有 [SN] 時條款要綁測試」,各條款也都有綁。
- 鏡頭「新增殘留段從頂端讀」這個例外:`templates.md` §3、06 固定席那列、`code-loop/SKILL.md`、計劃、`pitfalls-code-loop` 五處寫法互相一致。
- 沒有機械核對的地方:`scripts/lumos` 裡沒有任何「漏答固定席」的機制,所以 SKILL.md 拿掉「沒答的席照漏答固定席處理」是對的。

---

severity: minor
blocking: 否 — 只是條款與綁定測試少列,測試本身都存在、行為沒壞。
引句:「[test: t_pitfalls_residual_ask_unreadable_reason] [test: t_pitfalls_residual_ignores_git_grafts]」
問題:有四處條款與綁定測試沒有一一對上。
- [S6] 條款文字寫了「環境帶 `GIT_DIFF_OPTS` 時結果照舊」,但綁定清單只有 `grafts` 那支,沒有 `t_pitfalls_ignores_git_diff_opts_env`。這支只出現在計劃的 WHY 行。
- [S6] 條款寫的「頂端索引記的那篇跟起點不同應判 high」,實際由 `t_guard_residual_index_records_decision_note` 驗(檢查「決策所在筆記換了」)。這支也沒綁在 S6。S6 綁的 `t_pitfalls_residual_decision_note_touched` 驗的是①到⑤五種情形,不含這一項。
- [S1] 條款只寫了「捷徑」帳。新增的 `t_guard_audit_residual_hardlink_ledger` 驗的是硬連結,沒有任何條款涵蓋,只列在 guard-kill 的 TEST 行。
- `t_reference_residual_lens_docs` 在圖譜任何地方都沒被引用,等於守衛沒有條款認領。S8 綁的 `t_reference_audit_q3_rules` 只管「只准問一次」那一族說法。
具體失敗情境:有人刪掉 `t_pitfalls_ignores_git_diff_opts_env` 或 `t_reference_residual_lens_docs`,沒有任何條款或綁定檢查會提醒「這條說法失去測試了」。
佐證:``scripts/test_lumos.py:`t_pitfalls_ignores_git_diff_opts_env`、`t_reference_residual_lens_docs` 的 def`` ;``docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:19``

severity: minor
blocking: 否 — 唯一照實的說法已在派工端的 SKILL.md,其他是過強的措辭,沒有隱瞞機制。
引句:「改成外層看門,挑答案成了被審查的事件」
問題:把關強度只在 `code-loop/SKILL.md` 寫成「審查席有沒有答這題沒有機械核對,收貨時編排者自己看」。其他處仍把效果說成事實:
- 計劃與 `pitfalls-code-loop` 的升 high WHY 寫「挑答案成了被審查的事件」。
- `reference.md` 與 `圖譜即合約.md` 寫「審查席看那筆殘留決策與問答」。
- `templates.md` §3 寫「逐條必答」。
這些都沒有帶「只保證跑一輪高風險代碼審,有沒有答沒人機械核對」。守衛測試 `t_reference_residual_lens_docs` 也只檢查 SKILL.md 那一行有這句。
具體失敗情境:讀 `reference.md` 或手冊的人會以為「必答」有機械驗收。實際上審查席漏答這題,`loop status --disposal` 照樣放行。
佐證:``skills/lumos-code-loop/SKILL.md:183``;``skills/lumos-project-notes/reference.md:299``;``scripts/lumos:`grep 漏答` 無命中``

severity: minor
blocking: 否 — 入口行為本身有測試守住,缺的是紀錄品質與其中一行的測試。
引句:「四個分支逐字同一段」
問題:入口清 git 環境那條 WHY(計劃的 `main()` 開頭那行)有三處不足。
1. 出處寫「協調者轉述另一分支資安席實測」、正文寫「四個分支逐字同一段」,都是過程紀錄,日後的讀者查不到,也違反「過程不寫進筆記」。
2. 沒有 `[代價:]`。程式裡 `os.environ` 是直接改,所有子行程都繼承。包括 `bound-tests` 與 `fix-check` 跑的使用者專案測試,它們會被強制關掉替身與 grafts,並丟掉使用者自己設的 `GIT_EXTERNAL_DIFF` 與 `GIT_DIFF_OPTS`。測試檔的 `_rc_git_env` 說明已經踩到這件事,WHY 卻沒寫。
3. `os.environ.pop("GIT_EXTERNAL_DIFF", None)` 這行沒有任何測試。`test_lumos.py` 裡的 `GIT_EXTERNAL_DIFF` 只出現在測試自己丟環境變數的清單。把入口那行刪掉,所有測試照綠,WHY 卻寫「拿掉 GIT_EXTERNAL_DIFF」。
具體失敗情境:有人把入口那行刪掉做清理,沒有測試翻紅。使用者設了外部差異工具時,各閘讀到的差異不再可預期。
佐證:``scripts/lumos:main() 開頭 os.environ.pop("GIT_EXTERNAL_DIFF", None)``;``docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:47``

severity: minor
blocking: 否 — 描述過時但結論同向,不會導致錯誤操作。
引句:「一律設 `GIT_NO_REPLACE_OBJECTS=1`(代碼審 r4 資安席」
問題:修補後逐呼叫帶環境的函式已刪,改由 `main()` 入口統一設。但兩處仍用舊機制的口氣描述:
- 計劃的實務隱患段(作為上下文行留著)。
- `pitfalls-code-loop` 風險分級那條 WHY。
同一份計劃新增的 WHY 反而寫「不選:逐呼叫帶 env(r4 的做法)」,前後不一致。
另外 guard-kill 主 WHY 與計劃「殘留索引每筆記 fp」那條,描述索引欄位時沒補 `notes`,只有 doctor 那行補了。
具體失敗情境:讀者查「replace refs 在哪裡擋」,先看到逐呼叫帶環境的說法,在 `scripts/lumos` 找不到對應函式。
佐證:``docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:98``;``docs/lumos-toolchain-knowledge/Systems/guard-kill.md:70``

severity: minor
blocking: 否 — 粗粒度代價寫在計劃與 `pitfalls-code-loop`,使用者面的手冊少寫只是資訊不足。
引句:「新增判 untestable 的問答、改到存著已登記殘留決策的那篇筆記也升 high」
問題:「改到存著殘留決策的筆記就升 high」的說法各處一致,但粗粒度代價不齊。計劃的 WHY(「碰到那篇筆記的推送,就算只改錯字也要過一輪高風險代碼審」)、`pitfalls-code-loop` 與 `reference.md`(「刻意的粗粒度」)有寫。`圖譜即合約.md` 與 06 的殘留列沒寫代價。
另外 `templates.md` §3 鏡頭 3 仍寫「對著段裡的殘留決策與問答列(編號、判定、checker、ts)」,觸發條件只講新增殘留或新增問答,沒講「只改筆記也會附這一段」。
具體失敗情境:有人只改殘留決策所在筆記的錯字,收到升 high 與一段陌生的「新增殘留」必答題,查手冊找不到理由與代價說明。
佐證:``docs/methodology/圖譜即合約.md:129``;``skills/lumos-design-loop/templates.md:231``

最高等級 minor,blocking 0 條。
