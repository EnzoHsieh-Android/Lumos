severity: minor

我只用了唯讀查證,沒有改檔。確認過這幾件:
- `python3.14 scripts/test_lumos.py -k kt_catalog` 與 `-k kotlin_rulepack` 都全綠。
- 型錄自檢輸出「型錄問題 0 個、還沒逐列查證 0 列」。
- `rules-unwired/` 的規則數是 14,和〈統計〉一致。
- `skills/kotlin-idioms/SKILL.md` 沒有任何一處說這三條規則會擋,這一項對得上。

以下 6 條是撞牆點,各有佐證。

**F1**
severity: minor
blocking: 否
Systems/kotlin規則包 的檔案節還在講舊的搬家範圍。
- 引句:「推送前不再擋這兩種寫法(見〈待人裁〉);其餘規則包等級沒動」
- `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:70` 寫「2026-11-08 從 `rules-hints/` 拆來 8 條」。實際 `rules-unwired/` 有 14 條:
  - 9 條來自 `rules-hints/`,多的那條是 `kt-compose-test-node-by-literal-text`。
  - 2 條來自 `rules/`,也就是範本預設會擋的那份(`kt-async-await-immediately`、`kt-compose-test-node-by-index`)。
  - 3 條是資安規則。
- 規則包覆核兩級接新增告警閘_計劃 還保留舊說法:
  - 第 67 行寫「唯一的行為差異是放寬……少擋 8 條」。
  - 第 139 行寫「沒有改任何擋停」。
  - RETIRE-IF 寫「只剩出處不全那 8 條」。
- 三個月後的人會以為範本預設的擋停沒變。實際上 `rules/` 少了 2 條。

**F2**
severity: minor
blocking: 否
`checks-catalog.md` 第 11 行說覆核級「範本還沒接,接不接見 [[Projects/規則包覆核兩級接新增告警閘_計劃]] 待人裁」。
- 該計劃已經裁了,標題是「待人裁(2026-11-08 已裁)」,結論是 (b) 這一版不接。
- 接手的人照型錄去找那個待辦,會找不到。
- 檔案:`skills/kotlin-idioms/checks-catalog.md:11`。

**F3**
severity: minor
blocking: 否
〈統計〉把「出處不全」的意思講窄了,和型錄實況對不上。
- 引句:「套回後型錄 459 列有查證紀錄,出處不全 34 列」
- 〈統計〉寫「沒有的 13 列都是查不到權威原文、已標出處不全」,讀起來像出處不全只有 13 列。
- 我用腳本數了:標「出處不全」的有 35 列,其中 22 列(API-6、API-34、CO-37、DATA-63 等)的來源欄同時有〔查證 2026-11-05:網址〕。
  - 例:`skills/kotlin-idioms/checks-catalog.md:185` 的 API-34 是「出處不全」,卻附了兩條 kotlinlang 網址。
- 〈輸入與口徑〉沒有定義「出處不全」。
- `SKILL.md:8` 說這類列「還沒找到官方出處,只當參考、不當標準」。
- 結果是「有查證網址」和「出處不全」並存。接手的人分不出是「沒找到」還是「找到但不支持」。計劃〈依據來源〉的口徑只寫了「查不到標出處不全」。

**F4**
severity: minor
blocking: 否
情境決策表的列把出處不全的 API-14 當依據,沒有任何標記。
- D-1 的對應檢查是「API-1、API-3、API-14」,D-2 是「API-1、API-14」,檔案在 `skills/kotlin-idioms/checks-catalog.md:715` 與 `:716`。
- D-2 的標準寫法是「不要包 `async { }.await()`」,而這個寫法的依據列 API-14 被降成「只當參考、不當標準」(`SKILL.md:8`)。
- 這兩列仍走表態對程式與盲判席,計劃裡沒提到。
- 自檢只擋規則引用出處不全列的位置,不看情境決策表。
- 引句:「API-14、TEST-31 仍找不到,這一批不標出處不全」

**F5**
severity: minor
blocking: 否
DATA-12 的「取捨提醒」沒有落地定義,列內容也自相矛盾。
- 引句:「取捨提醒=不掛規則、不擋,型錄那一列寫清楚做法的代價,接電方式照舊是表態對程式與盲判席」
- 我在整個圖譜 grep「取捨提醒」,只出現在這份計劃,型錄〈輸入與口徑〉的接電方式五種與級別定義都沒收這個類別。
- 型錄 DATA-12 這一列(`skills/kotlin-idioms/checks-catalog.md:543`):
  - 壞寫法欄寫 `dataStore.updateData { api.call(); it.copy(...) }`。
  - 標準寫法欄的最後一個選項是「真的要在 transform 裡做,接受其他寫入要等」,等於承認壞寫法可接受。
  - 通電批次還掛著盲判席。盲判席要判照做或沒照做,而這列的壞寫法本身就是被允許的選項,判不出對錯。
- 盲判實際讀的是 D-42(`:756`),不是 DATA-12。D-42 的後果欄只提了一句「型錄 DATA-12,2026-11-08 人裁改成取捨提醒」。
- 取捨提醒要真的不擋,應該寫明這類列要不要掛盲判席。

**F6**
severity: minor
blocking: 否
放棄擋停的代價沒有附回頭看的條件。
- 引句:「代價:消費專案推送前不再擋這兩種寫法。」
- 專案 CLAUDE.md 鐵則 4 要求承認風險時附回頭條件。計劃裡唯一的 REVISIT 是「REVISIT:2026-12-07 看型錄自檢的」未查證列數有沒有變多,不是在管這三條規則何時能搬回 `rules/`。
- 沒有「找到官方原文就升回 rules/」之類的條件,也沒有 RETIRE-IF。這三條規則在 `rules-unwired/` 裡範本不宣告、永遠不跑,會一直擺在那裡。
- 線索:我用 WebSearch 查到 JetBrains 有「Redundant 'async' call」這個 IDE 檢查,會建議把 `async(...).await()` 改成 `withContext`。這是搜尋結果,我沒有打開官方檢查頁逐字核對。同一串討論提到這個檢查有爭議,因為取消行為不同。
  - 來源:https://lightrun.com/answers/kotlin-kotlinx-coroutines-redundant-async-call-may-be-reduced-to-kotlinxcoroutineswithcontext
  - 所以「官方查不到」這個前提值得留一個重查條件。

整體來看,2026-11-08 人裁落地的程式與測試沒有出錯。需要補的都是文件一致性:舊數字、舊說法,以及「出處不全」的定義。
