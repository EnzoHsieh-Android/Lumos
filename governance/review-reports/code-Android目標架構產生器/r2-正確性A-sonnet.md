severity: minor

## F1 舊檔清單不再收「路徑像測試的正式 Kotlin 檔」,產出的 Konsist 測試卻仍會掃到它們(三方判法分岔)
severity: minor
blocking: 否
歸因：有證據的修復回歸(舊檔清單內容在修前修後不同);Konsist 端的紅燈未判定。
引句:「files = sorted({f for fs in under.values() for f in fs if _arch_code_file(f)})」
佐證: `scripts/lumos:57489`(`_arch_code_file` 用 `_PITFALL_DIFF_TEST_PAT` 排除 `(^|/)tests?/`、`_test\.`、`\.test\.`、`(^|/)test_`,且不分大小寫)
失敗場景:
1. 專案有一支舊檔 `feature/cart/src/main/java/x/test/Helper.kt`,或檔名是 `Fake_test.kt`、路徑含 `Tests/`。它在 `src/main`,屬正式程式。
2. 修後 `--legacy new-only` 不把它列進清單,因為 lumos 判它是測試檔。
3. 產出的 Konsist 測試只靠 `rel !in legacyFiles` 排除舊檔,範圍用 `Konsist.scopeFromProduction()` 加 `scopeDirs`。這支檔若被 Konsist 當正式程式,就既不在清單上、又在範圍內,會被當新檔檢查。
4. 這支舊檔一旦有違規,採用當天架構測試就紅。這正是舊檔清單要避免的事。lumos 那頭卻把它當非程式檔跳過。
5. Konsist 如何判「正式程式」我沒能執行驗證(環境沒有 kotlinc),所以 Kotlin 端的紅燈只是推論,嚴重度因此停在 minor。

兩版證據(同一份 3 檔 repo,指令 `lumos arch-template android … --legacy new-only --print legacy`):
- case_source:我自建的暫存 repo,含 `x/test/Helper.kt`、`x/Fake_test.kt`、`x/Tests/T.kt`、`x/A.kt`、`src/androidTest/.../B.kt`。
- before(8a601700):清單含 A.kt、Fake_test.kt、Tests/T.kt、test/Helper.kt 四支,不含 androidTest 那支。
- after(2f1b1840):清單只有 `androidTest/.../B.kt` 與 `A.kt`。
- `_arch_target_rule_index("…/test/Helper.kt", [("feature/cart/**", …)])` 與 `Fake_test.kt` 都回 None,`androidTest/B.kt` 回 0。

這是修補刻意造成的取捨:原問題是 androidTest 與 testFixtures 沒進清單。修補後那兩種進來了,但同時把「lumos 判成測試、Konsist 仍掃」的正式檔排除了。

## F2 Kotlin 手寫清單解析只驗 `files` 陣列,比 lumos 的嚴格 JSON 寬
severity: minor
blocking: 否
歸因：有證據的原有漏查(修前後這幾處解析行為相同,修補只收緊了逗號)。
引句:「if (text[i] == ']') return out」
佐證: `scripts/lumos:57424`(`_arch_legacy_at` 走 `_lumos_config_at_ref(strict=True)`,內容是完整 JSON 物件才算讀得懂)
失敗場景:
1. 清單檔被手改或衝突解決後少了結尾的 `}`,內容是 `{"files": ["a.kt"]`。
2. Kotlin 讀到 `]` 就 return,正常跳過 a.kt。
3. lumos 的 `json.loads` 回 `Expecting ',' delimiter`,清單判「讀不懂」,清單整份不起作用,a.kt 照目標審。
4. 結果兩邊相反:架構測試跳過舊檔,代碼審卻照目標審,而且 Kotlin 沒有紅燈提醒。
5. 同族的寬鬆處(推論,沒有實跑):`\x` 這類非法跳脫被 `else -> sb.append(e)` 吞掉;字串裡的裸控制字元、U+00A0 當空白(`isWhitespace`)被接受;頂層是陣列、`files` 在巢狀物件裡也會被那條 `"files"\s*:\s*\[` 找到。

兩版證據:
- case_source:`json.loads('{"files": ["a.kt"]')`,我在 after 版目錄實跑。
- before 與 after 的解析迴圈在 `]` 之後都沒有檢查尾巴(見修補差異的 `return out`)。
- 結果:lumos 一側報錯,Kotlin 一側無法執行(沒有 kotlinc),所以 Kotlin 端是依程式碼推論。
- 發生機率低,屬於「補收緊」類。

## 三問
1. **原問題修復效果**
   - 修了三處,對應三個症狀,都已實跑:
     - androidTest 與 testFixtures 檔進清單:after 的 `--print legacy` 含 `src/testFixtures/java/F.kt` 與 `src/androidTest/.../B.kt`,before 沒有。
     - 範圍路徑的 `$` 在 Kotlin 字串裡跳脫:before 產出 `listOf("feature/$gen")`,after 產出 `listOf("feature/\$gen")`。
     - 空白範圍 `'  '`:before 回「少於兩段」,after 回共用樣式檢查的訊息。兩版都是 rc 2。
   - Kotlin 逗號嚴格:靠程式碼閱讀與作者在 macrobench-lab 的重編譯紀錄。我這邊無 kotlinc,Kotlin 端未判定。
2. **修補處的正常、錯誤與相鄰路徑**
   - 正常路徑仍成立:`python3.14 scripts/test_lumos.py -k arch_template` 為 84 passed、0 failed。`-k vendored` 113 passed、`-k help_when` 2 passed、`-k arch_target` 181 passed。
   - 我獨立把 64 組開關各產一次,逐組核對:規則數等於 9+3(ddd=full)+1(modules=multi);測試函式沒有同名;每個 `[test:]` 都有對應函式;沒被規則認領的只剩命名慣例那支;ddd=lite 的 RULE 行不含「聚合」。結果 0 組不合。
   - 相鄰路徑:F1(清單與 Konsist 判法分岔)。
   - 殘留引用:`_ARCH_TPL_LEGACY_SKIP`、`_ARCH_TPL_TEST_TAG_RE` 全 repo 已無引用。
3. **新發現的同一案例修前修後**
   - F1:修前清單含 `test/Helper.kt`,修後不含,見上。
   - F2:修前後解析迴圈尾巴行為相同,屬原有。

## 已驗主張證據
- claim:舊檔清單與分目標節點判定一致(androidTest、testFixtures 納入)。input:上述 5 檔 repo。expected:清單 ⇔ `_arch_target_rule_index` 非 None。case_source:自建暫存 repo。before:缺 androidTest 與 testFixtures。after:有。comparison:成立。
- claim:`$` 範圍在 Kotlin 常數安全。input:`--scope 'feature/$gen'`。expected:`\$gen`。before:`$gen`(會被當字串樣板)。after:`\$gen`。comparison:已修。
- claim:空白範圍被共用檢查擋下。input:`--scope '  '`。before:訊息「少於兩段」,rc 2。after:訊息「空的、以 ./ 或 / 開頭,或有反斜線」,rc 2。comparison:已修,訊息原因更準。
- 未驗範圍:Konsist 的 scopeFromProduction 語意與 Kotlin 編譯(無 kotlinc)、多模組實跑、Windows 路徑與 CRLF(`read_text` 已做通用換行,理論上無事)、`--node none` 與 `--node` 含特殊字元。

## 圖譜鏡頭固定席判定
- `lumos-cli-read` ★INVARIANT★(search 預設排除 superseded):不影響。diff 只新增 `arch-template` 子命令與資料檔,沒碰 search 或其濾網。
- `測試假綠形態` ★INVARIANT★(還原翻紅釘需前置斷言):不影響。diff 沒動那條綁定的 slim/uninstall 測試。新增的 S8 原文釘選測試屬另一席範圍。
- `design-loop` ★INVARIANT★(處置閘第五步):不影響。沒改處置閘判定。
- `lumos-cli-lifecycle` ★INVARIANT★(re-inject 只動 sentinel 之間):不影響。diff 只在 `_VENDORED_TREE_FILES` 加一項。vendored 相關測試 113 passed。
- `guard-kill` ★INVARIANT★(rc 優先序、`--json` 純度):不影響。`arch-template` 與 guard kill 無共用路徑。
- `bound-tests-gate` ★INVARIANT★:不影響。沒動閘邏輯。它綁的測試名未被 diff 改名。
- `pitfalls-code-loop`、`arch-alignment-lens`:`_arch_code_file` 與 `_arch_target_rule_index` 只被呼叫,沒被改動,審查判法不變。F1 的分岔來自產生器新增的呼叫,而不是審查端的改動。

總結:共 2 條,都是 minor。
