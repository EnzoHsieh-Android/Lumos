severity: minor
Final 回報如下。

## 審查結果(整合席:合約與圖譜一致/知識同步)

整體判定:3 條 finding,都是 minor、都不擋。程式端與主要筆記對得上,問題集中在修補沒掃乾淨的舊說法。

我實際核對過這些:
- 對照 `scripts/lumos` 的 `_name_filter_escape`、`_name_filter_collisions`、`_test_name_ok`、`_WIN_CMD_SPECIAL`、`_split_test_ref_ex`、`_bind_name_problem`、`_kill_method_name`、`_C_STRIP_RE`、`_apply_test_overrides`。
- 計劃做法 4(`-g` 錨 `\s<名>(?:\s@\S+)*$`、tag 先剝、自己那支由第一個同名測試佔用、describe 加測試拼名算撞名、頭尾空白不收)與程式一致。
- 剝註解的三引號與 `@"` 字串、Windows 擋 `& | < > ^ % " !`、`_TEST_NAME_RULE_ZH` 講到 200 字與 Windows 字元,都與計劃和 Systems 節點一致。
- 決策 d1 的敘述與修後程式沒有牴觸。
- 新增的 FACT 行都有 `[來源:外部] [confirmed:] [查:]`。
- 六篇動到的筆記 `lumos lint` 全部 0 問題。
- 「綁 describe 標題選到零支、判紅」在計劃和 Systems 兩處說法一致。
- 沒有新增程式檔,「每支檔有家」不受影響。

沒驗到的範圍:計劃 FACT 說的 Playwright 1.64.1 實跑結果(tag 接在標題後、describe 同名只選到那支測試)我沒有重跑,只能信作者在 order-web 副本的紀錄。

---

**F1**
severity: minor
blocking: 否
歸因:有證據的修復回歸。修前 `5f8f8e48` 的程式與這兩處文字都是 `(?:^|\s)…$`;修後程式改了錨,這兩處沒跟著改。
- 問題:修補把 Playwright 的 `-g` 錨改成 `\s<名>(?:\s@\S+)*$`,但還有兩處寫著舊錨 `(?:^|\s)<名字>$`:
  - `docs/lumos-toolchain-knowledge/Projects/測試名收自由字串_計劃.md` 的驗收條款 S50。它與新增的 S65 互相矛盾,而且 S50 綁的測試 `t_playwright_name_filter_anchored` 現在驗的是新錨。
  - `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md` 的「名稱篩選的跳脫與撞名」第一條。
- 同一段的第二條也過期:寫「別的標題含這個名字(不分大小寫)就不跑」,但實際 Playwright 只數結尾是這個名字的標題,dart(`plain`)是分大小寫的。
- 程式內也有一處:`scripts/lumos` 裡 `_name_filter_escape` 的 docstring 還寫舊錨,函式裡面的行內註解才是新的。
- 具體例:照 bound-tests-gate 或 S50 改回 `(?:^|\s)名$`,帶 tag 的 Playwright 測試會必紅,Windows 上 `|` 與 `^` 也會被 cmd.exe 誤解。目前有 `t_playwright_tail_tags_and_own` 擋著,所以降為 minor。
- 重現:`grep -rnF '(?:^|\s)' docs scripts/lumos --include=*.md --include=lumos`
引句:「- [S50] 當 playwright 平台展開名稱時,`-g` 應錨在結尾 `(?:^|\s)<跳脫後>$`。[test: t_playwright_name_filter_anchored]」

**F2**
severity: minor
blocking: 否
歸因:有證據的原有漏查。這是前幾輪留下的漏網,不是這輪修補造成的。
- 問題:`file_name_match` 現在單平台和多平台都能覆蓋(`_apply_test_overrides` 有處理),但三處列舉覆蓋欄位時漏了它:
  - 計劃做法 5。
  - `docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md` 的「多平台每個平台設定…也收 `exts`/`scaffold_ext`/`method_regex` 覆蓋」那行。
  - `skills/lumos-project-notes/reference.md` 的「逃生口:`config.json` 的 `test` 可欄位級覆蓋 `exts`/`scaffold_ext`/`method_regex`」。
- 具體例:Playwright 自訂 testMatch 的人讀 reference.md,看不到可以寫 `file_name_match`。這個寫法只出現在 Systems 節點另一行與計劃做法 2。
引句:「逃生口:`config.json` 的 `test` 可欄位級覆蓋 `exts`/`scaffold_ext`/`method_regex`;多平台時寫在那個平台的設定裡」

**F3**
severity: minor
blocking: 否
歸因:有證據的原有漏查。
- 問題:修補替 Android 計劃和實作計畫的 4 處舊說法補了「已被取代」,但仍有未標的過期說法:
  - `Projects/Android側UI測試綁圖譜工作流_計劃.md` 的「★r2 補的第四條」:「Kotlin 反引號中文測試名綁不上……函式名必須先改成識別字」。
  - 同檔 decisions 裡 valid:true 那筆的 `why_chosen`:「放寬 IDENT_RE 會一併鬆掉…冒號解析與識別字保證」。結論「不改成吃檔案路徑」仍成立,但這個理由的前提已被取代。
  - 實作計畫 Task 6 Step 1 仍要求把 Kotlin 測試改成識別字名。現在照做不會壞,只是多做一步。
- S25 的 grep 關鍵字(「必須是識別字」「識別字名」等)抓不到「必須先改成識別字」,所以漏網。
引句:「**要綁合約的測試，函式名必須先改成識別字**（本例：`manualDiscountOver100Blocked`）」

---

**最嚴重 severity:minor;blocking 共 0 條。**

## 三問回答

1. **原問題的修復效果有何行為證據?** 我沒有重跑測試。核對靠逐行讀程式對文件:修後程式碼的錨定、撞名、Windows 字元、三引號剝註解與 `_split_test_ref_ex` 的切法,和計劃做法、S63、S64–S76、Systems 節點的文字一致。Playwright 實跑部分未驗。
2. **修補處的正常、錯誤、相鄰呼叫路徑是否仍成立?** 就文件同步這個角度,成立。`_bind_name_problem` 與 `_kill_method_name` 都走 `_split_test_ref_ex`,與計劃 S58、S63、S73 一致;`guard scaffold` 仍用 `IDENT_RE`,與各處「只有 scaffold 要識別字」一致。例外是 F1 的殘留舊錨。
3. **新發現同一案例修前、修後各是什麼結果?** F1 修前文件與程式一致(舊錨),修後程式變了、文件沒跟,是修復造成的漂移。F2、F3 修前修後都有,不是這輪造成的。

## 相關路徑
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/docs/lumos-toolchain-knowledge/Projects/測試名收自由字串_計劃.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/docs/lumos-toolchain-knowledge/Projects/Android側UI測試綁圖譜工作流_計劃.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/docs/lumos-toolchain-knowledge/Projects/Android側UI測試綁圖譜工作流_實作計畫.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/skills/lumos-project-notes/reference.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/scripts/lumos`
