severity: minor

照手冊順序從頭走一遍(問答、蓋 `[audit:]`、記殘留決策、`guard residual --add`),合法流程走得通。審計日期用本機日期、治理帳 `ts` 也是本機時區,兩邊口徑一致,同一天先問再審計會過。我沒有實際執行,是讀 patch 和 `review-converge/` 的程式後判斷的。REVISIT 四行格式合法,日期是 2027-01-15,開頭的列表符號和縮排 `_revisit_split` 都吃。條款與綁定測試都對得上:S1、S6、S9 列的新測試名在測試修補裡都有,S6 另列的 `t_pitfalls_residual_git_failures` 等在文字層面也對上。下面是兩條 minor。

severity: minor
blocking: 否 — 有手冊內的繞法,卡住的是少數流程,不是壞資料或漏擋。
引句:「判過 testable 的反例在整個節點都記著,合約宣稱改了字也不准改判 untestable(同一節點的別條合約用別的編號)」
問題:判過 testable 的編號改成整個節點共用,手冊只在括號裡提「別條合約用別的編號」。但反例編號來自每份審計報告,審計員每輪都可能從 c1 重新編。
失敗情境:
- 同一節點有兩條 `★INVARIANT★`,甲條的 c1 判過 testable,補完測試後,乙條審計報告裡全新的 c1 要判 untestable,`residual-ask` 回 2。
- 同一條合約「補測試、重審」的第二輪,新報告又從 c1 起編,也會撞到。
- 手冊〈第 3 問〉只叫人照審計報告的編號問,沒要求編號跨輪、跨合約不重複。編排者只能自己發現要改編號,而「改編號」正是殘餘風險段列為要事後量的行為。
- 擋下訊息有說「用別的編號」,所以不會死路,但會誘導編排者隨手換號。
- 建議:手冊在記殘留段明寫「反例編號在同一節點內不重複,例如加合約或輪次前綴」。
佐證:``file: `/tmp/code-審查收斂規則-r3-repair-lumos.patch:187-189` ``,``file: `/tmp/code-審查收斂規則-r3-repair-docs.patch:266` ``

severity: minor
blocking: 否 — 屬單人威脅模型下已接受的偽造面,加上一條沒有測試的分支。
引句:「早於反例 {_esc_clean(c, 40)} 那筆問答的日期 {max(days)}——照順序重審」
問題:日期檢查有三個縫。
1. 日期只比到「天」。同一天內先 `guard audit` 再 `residual-ask` 照樣放行,上一輪同日的舊戳記還是能頂替。
2. `guard audit --date` 可以填任意日期,測試夾具自己就用 2099。這是偽造一筆審計的捷徑,但本來就屬「偽造留痕靠事後量」。
3. `[audit:]` 抓不到日期時(`audit_day` 為 None)整段檢查靜默跳過。另外「問答 ts 讀不出日期」的那條報錯,測試修補裡沒有任何一支測試走到,拿掉它所有測試仍全綠。
這些都不會讓合法流程走不通。
佐證:``file: `/tmp/code-審查收斂規則-r3-repair-lumos.patch:242-264` ``,``file: `/tmp/code-審查收斂規則-r3-repair-tests.patch:602-625` ``

最高等級 minor,blocking 0 條。
