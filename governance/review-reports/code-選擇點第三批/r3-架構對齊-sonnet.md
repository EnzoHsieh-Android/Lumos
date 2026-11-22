severity: minor

這輪修補的結構是對齊的,只有一處小不一致:新形狀測試重寫了「rule 頂層有沒有雙重否定」的偵測,沒有沿用鄰居 `_cb3_positive` 的做法。

## 1. 分層與依賴方向:對齊
- `t_choice_rule_shape_batch3` 放在 `t_choice_scope_rule_output` 之後、`t_gov_stats_choice_by_row` 之前,跟同批 S9 測試同區。
- 它用 `_ktpack()`、`kp.CHOICE`、`_SrcOnly`、`check`、`_re_mod`,都是鄰居用的那組,沒有跨層直呼。對照 `scripts/test_lumos.py:147066`(`t_choice_scope_rule_output`)。
- 它讀真 `api.yml` 並用同一個 `^---` 切分、`^id:` 取列號,跟 `scripts/test_lumos.py:147084` 附近 S9 的取法一致。
- 規則檔的改動只動 `api.yml`,`utils:` 與頂層 `rule:` 的位置不變。對照 `configs/ast-grep/kotlin-choice/rules-choice/api.yml:2`(C-19)。
- 型錄的 C-38、C-39 列文字有同步更新。

## 2. 命名與錯誤處理:對齊
- 測試名 `t_choice_rule_shape_batch3` 符合 `t_choice_*_batch3` 的慣例,輔助函式 `_cb3_rule_shape` 也符合 `_cb3_positive`、`_cb3_scope_unlisted` 的前綴。
- 文件字串的「[第三批 S11]」、判準來源、翻紅釘三段,跟 S5、S9 的寫法一樣。S11 也確實是計劃預期值表裡的列號。
- 規則文件整批撤掉時用 `raise _SrcOnly(...)` 跳過,跟 `t_choice_samples_batch3` 一致。
- 樣本標記 `// HIT C-38`、`// MISS C-xx` 的格式不變,多行寫法標在節點起始行,跟鄰居一樣。
- C-38、C-39 的 `child-co` 兩份 utils 仍然一字不差,仍由 `_CB3_SCOPE_UTILS` 守。

## 3. 第二種做法
- **雙重否定現在只剩一種寫法。** 照既有寫法,再由一條判準(往下找有 `has`/`precedes`,或往上超過兩層 `inside`)決定哪些列外包,這條判準有 `t_choice_rule_shape_batch3` 守。
- **C-40~C-47 與 C-19~C-31 一字不差。** 我把 C-19~C-31 與 C-40~C-47 的 `rule:` 本體、只把 regex 方法名換成佔位後比對,21 條雜湊全相同。對照 `api.yml:2`(C-19)與 `api.yml:432`(C-40)。
- **C-51、C-52 的外包不另成例外,但理由有一處不確定,見 ⚠。** 它們含 `has: {…nthChild: 1…}`,依判準本來就要外包,所以沒有另開例外。
- **形狀測試與專案「重複寫法靠比對測試守」的差異見 a1。** 專案既有做法是逐字比對,這支測試是判準分類,方向相同、機制不同。
- ⚠ **請編排者裁:C-51、C-52 該不該外包。** 外包的實際理由是「`has` 就包」這條形式判準。它們只是一層 `inside` 加一個直接子節點的 `has`,深度跟 C-19 同級,S9 也沒有它們的輸出爆量對照(C-49、C-50 同樣沒有,所以不是新的不一致)。鄰居本身也有 C-36、C-37 這種自承的例外,我判不準,不硬判。

## a1 形狀測試重寫了雙重否定偵測,沒有沿用既有輔助
severity: minor
blocking: 否
引句:「    top = any(code[i] == "  not:" and code[i + 1] == "    not:" and "rule:" in code[:i] for i in range(len(code) - 1))」
file: `scripts/test_lumos.py:147053`
同檔的 `_cb3_positive` 已經用 `ln == "  not:"`、下一行 `"    not:"`、`"rule:" in out` 來判 `rule:` 頂層有沒有雙重否定。S9 也用 `_cb3_positive(...) is not None` 當「有包」的判斷。新測試另寫一份同條件的偵測,另外還有 `nested`、`other` 的縮排掃描,同一個概念現在有兩份實作。結構(單層測試檔內、不跨層)沒問題,只是日後 YAML 寫法改了要改兩處。歸因:有證據的原有漏查,是這輪新增造成的重複,不是回歸。

不對齊共 1 條,其中 major 0 條
