你是這個 repo 的協作者,任務是獨立診斷並提出「代碼審(code-loop)老是收斂不了」的全面優化方案。只讀,不改任何檔、不跑 git 寫入指令;可以跑唯讀的分析指令(python 讀檔算數字),要寫暫存檔只寫到 /tmp/codex-converge/。結論全部寫在回答裡,用繁體中文。

## 問題(使用者原話)
「最卡的還是收斂方向,常常三輪還收斂不了。」使用者想全面優化這個議題。

## 這個 repo 的審查流程(先讀)
- 代碼審手冊:skills/lumos-code-loop/SKILL.md、skills/lumos-code-loop/reference.md
- 設計審手冊與派工範本:skills/lumos-design-loop/SKILL.md、skills/lumos-design-loop/templates.md(§3、§3.1 修補鏡頭)
- 收斂判準是「處置閘」:一輪裡每個發現都折掉或附理由放行即過;代碼審輪內有 major 就不准放行任何條;high/standard 上限三輪,跑滿要人裁(可破例加開)。

## 資料(自己查,不要只信別人的結論)
- 審查帳:docs/.canary-log.jsonl(每席一列;loop、round、tier、severity、findings、folded_set/accepted_set 掛在載體席、report_path、snapshot_path、ts)
- 卷證:governance/review-reports/<迴圈>/(rN-snapshot.patch 凍結材料、rN-<席>.md 席報告、rN-intake.md 收貨紀錄、cap-retro.json 跑滿回顧)
- 跑滿回顧統計:`python3.14 scripts/lumos loop retro-stats`
- 注意資料品質:早期報告有植入的測試用假發現(含 canary 字樣)、有些報告沒有頂格 severity 行、report_path 偶爾指錯、部分輪次缺凍結 patch。

## 另一方(Claude)已做的分析與兩次設計嘗試(可讀,但請當待驗主張,不要當結論)
- 驗證筆記:docs/lumos-toolchain-knowledge/Verification/2026-10-14_修補大小與下一輪major回放.md
- 撤案的設計:governance/review-reports/修補大小上限試行/(r1-snapshot.md 是設計,r1-*.md 是四席審查,r1-intake.md 有撤案理由)
- 改寫中的設計:docs/lumos-toolchain-knowledge/Projects/改動與修補拆小_計劃.md,與 governance/review-reports/改動與修補拆小/ 兩輪審查報告
- 既有相關試行:docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md、docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審收斂根因盤點.md
- 既有離線評估工具:governance/eval/review_convergence.py 與 .md

## 要你回答的
1. 診斷:用資料說明為什麼收斂不了。至少檢驗這些候選原因,各給證據強度(強/中/弱/反證):
   - 每輪派全新多席審完整改動,新席總會找到東西(判準是「一輪零 major」)
   - 修補本身帶出新問題、修補越大越糟(Claude 的回放說修補行數每翻倍,下一輪有 major 的勝算約 1.8 倍,控制上一輪折入數後仍成立——請獨立核對,特別是因果方向與混雜)
   - 第一輪改動太大
   - 只修被點名處、同族沒一次掃完(跑滿回顧 20/20 都有這一類)
   - major 判準太低(例如測試偵測力缺口、文件不一致被判 major)
   - 有 major 的輪不准放行任何條,連 minor 都要折,導致修補膨脹
   - 審查員之間撞題、席數過多
   - 其他你在資料裡看到的
2. 方案:提出你認為最有效的一組優化(流程、判準、工具、手冊,哪一層都可以),每項寫:改什麼、為什麼(對應哪個診斷)、預期效果與怎麼量、代價與風險、跟現有規則或已否決做法的衝突。按「效果/成本」排序。可以推翻 Claude 的方向。
3. 驗證:這些方案要怎麼證明有效——哪些能用現有帳本離線回放先驗、哪些只能前瞻試行;前瞻試行的樣本與判準怎麼設才判得出來(Claude 兩次都被審查員指出「三案或四週判不出」)。
4. 明確列出你不同意 Claude 分析的地方與理由。

篇幅不限,但每個數字附算法(哪個檔、怎麼篩、分母是什麼)。
