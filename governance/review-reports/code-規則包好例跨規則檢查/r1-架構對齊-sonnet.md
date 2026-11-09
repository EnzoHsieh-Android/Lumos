severity: minor

整體判斷:這份 diff 沿用了專案既有的做法,沒有引入第二套機制。結構對得上,只有測試的寫法有一處不一致。

**1. 分層與依賴方向**
- 放的位置對。常數、檢查和 `good_cases()` 的略過都落在 `check.py`,和 `REVIEW_FP_PREFIX` 同一支檔、同一層。
  - 常數宣告:`configs/ast-grep/kotlin-android/check.py:31-32`
  - `good_cases()` 的略過:`check.py:999`
  - 判定迴圈:`check.py:1054-1067`
- 樣本放在 `samples/good/<規則 id>/` 底下,歸屬仍用既有的 `_sample_owner()` 判定(`check.py:985-993`),沒有另造路徑解析。
- 測試加在 `scripts/test_lumos.py` 的 `t_kotlin_rulepack_*` 家族,位置緊鄰 `t_kotlin_rulepack_samples`(`scripts/test_lumos.py:126710`)。
- Issue 筆記放修好紀錄,Systems 家筆記放 WHY。兩處都是既有的落點(`Issues/Kotlin規則包代碼審放行的小問題.md:57-66`、`Systems/kotlin規則包.md:23-33`)。
- 依賴方向沒有倒置。

**2. 命名與寫法**
- `CROSS_PREFIX` 的命名、行尾註解風格、用 `startswith((A, B))` 的寫法,都和 `REVIEW_FP_PREFIX` 一致(`check.py:31-32, 999`)。
- 問題訊息以「規則 id: 中文句」呈現,和鄰居的「好例誤報」「好例至少要兩段」同格式。
- 筆記的 WHY 和 REVISIT `[closed:…]` 格式與鄰行相同。
- `[test:]` 也有綁。
- 不一致的只有測試寫法,見 A1。

**3. 第二種做法**
- `cross-` 和 `review-fp-` 不該合成一種,兩者用途不同。
  - `review-fp-` 記的是「語意覆核級或不接閘規則已知會誤報」,只在 `rule_id in review_ids` 時豁免(`check.py:1054`)。
  - `cross-` 記的是「別條會擋規則的壞寫法」,而且一定要被別條命中,否則報錯(`check.py:1064-1067`)。
  - 兩者的豁免對象和反向檢查都不同。
  - 合成一種會讓「會擋規則的 review-fp- 樣本照報」這條既有保護(`scripts/test_lumos.py:126747-126766`)失效。
- 兩個前綴在 `good_cases()` 共用同一處略過,是合併得恰當的地方。
- 唯一不對稱的是「本條規則命中自己的 `cross-` 檔仍算誤報」,而 `review-fp-` 對自己是豁免的。這有道理,因為 `cross-` 放的是別條的壞寫法,不是本條的已知誤報。

**發現**

A1
severity: minor
blocking: 否
引句:「+        check("① 好例被別條會擋規則命中要報", f"{host}: 好例被會擋規則 {other} 命中" in ta, ta[:400])」
- 鄰居 `t_kotlin_rulepack_samples` 的改壞斷言統一用 `check("★改壞★ …")` 或 `check("★對照★ …")` 當前綴(例如 `scripts/test_lumos.py:126720-126727, 126766`)。
- 新測試改用 ①~⑤ 編號,沒有 ★ 前綴,而它正是一支「改壞測試」。
- 編號只在 docstring 的「翻紅釘」裡對應,和鄰居的「看標籤就知道在做改壞或對照」不同。
- 結構沒問題,只是標籤寫法和鄰居不一致。
- file: `scripts/test_lumos.py:126720`

⚠ 判不準、未列為發現:新測試的 `if not sg: print("(本機沒有 ast-grep…)"); return` 與鄰居 `scripts/test_lumos.py:127322-127325` 同形,對得上。不過 `t_kotlin_rulepack_samples` 在沒有 ast-grep 時還會多跑一段靜態檢查。新測試整支都需要 ast-grep,所以沒有靜態那半可以跑,我認為合理。

不對齊共 1 條,其中 major 0 條
