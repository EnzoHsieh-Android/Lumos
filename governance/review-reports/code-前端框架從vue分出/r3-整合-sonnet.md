severity: minor

我對照了 `scripts/lumos`(修後 9591e609;程式檔和 HEAD 9508e5af 相同)逐處核對修補後的文件。文件說的剝註解掃描器、判定記憶上限、`now=`、Spring 認哪幾種寫法、`eslintConfig` 只認物件、跑過證據樣式、超限停住、`min_lines` 數增行,程式實測都對得上。有 5 處活文件還留著舊說法或自相矛盾,都是 minor,沒有 blocker 或 major。

**1. 5 處文件舊說法與矛盾**

1. `bound-tests-gate.md` 的 vitest 段自相矛盾。
   - 同一段先寫「樣式不錨行首(兩個讀者共用…)」,幾句後又寫「開頭錨在 `Tests:` 或行首(可帶色碼與空白)」。
   - 程式是後者:`(?:Tests:|(?:^|(?<=\n))[^\S\n]*(?:\x1b\[[0-9;]*m[^\S\n]*)*Tests\b)…`。
   - 實測:「  ✓ Tests 2 passed」為 False,「  Tests  34 skipped (34)」為 False。
   - 舊句沒刪,新句只是接在後面。
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸。r2 把樣式加了錨,同一段的舊句沒同步刪。
   - 引句:「樣式不錨行首(兩個讀者共用、逐行那個不去色),中段限長 200 字」
   - 附帶:「my Tests: 2 passed in title」仍會匹配,因為 `Tests:` 那一支沒有錨定。文件寫的是「錨在 `Tests:` 或行首」,寫法本身準確,但沒講明這個缺口。

2. `pitfalls-code-loop.md` 把已修掉的缺陷還寫成已知限制。
   - 「角色鏡頭認得 Kotlin 伺服端」一段末尾仍寫:「已知限制:建置檔大到超過讀取上限時,批次讀取分不出「太大」與「不存在」,會往上一層找」。
   - 同檔後面 r2 新增的段落卻寫「回空字串(在但讀不了,停在那一層判不出)」,和它直接矛盾。
   - 程式是後者:`_review_roles` 對有物件但沒讀的 blob 回 `""`,不往上找。
   - 三個月後的人讀到前面那句,會以為這個洞還開著。
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸。r2 修了行為和下方段落,沒改前面那句。
   - 引句:「已知限制:建置檔大到超過讀取上限時,批次讀取分不出「太大」與「不存在」,會往上一層找」

3. 計劃〈實作紀錄〉「跟計劃不一樣的地方 ①」同樣是過期的舊說法。
   - 原文:「批次讀取分不出「超過大小上限」與「不存在」,太大的建置檔會往上一層找(計劃寫的是判不出)…寫進 [[Systems/pitfalls-code-loop]] 的已知限制」。
   - 現在程式就是照計劃的「判不出」做,這個偏離已不存在,它指向的已知限制也是第 2 點那句過期的話。
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸。
   - 引句:「批次讀取分不出「超過大小上限」與「不存在」,太大的建置檔會往上一層找(計劃寫的是判不出)」

4. 計劃〈做法〉B10 的範圍規則,前後兩條互相矛盾。
   - 「一條統一規則」(未被修補動到)寫:「只要有一支判成 Android 或判不出(含已刪除讀不到、超過讀取上限、超過判定支數上限的檔),就照現況」。
   - 修補新增的〈接線〉寫:「這次刪掉的 `.kt` 不算進「全部判伺服端」」。
   - `_stack_platform_excluded` 實際把已刪檔濾掉:`kts` 的條件含 `(Path(repo_root)/f).exists()`。所以「刪一支伺服端 .kt、改另一支伺服端 .kt」會拿掉 Android 三題,與第一句相反。
   - 同一段還說 `androidTest/` 底下的檔「照既有測試檔判定排除」,但這點不成立:
     - 實測 `_PITFALL_DIFF_TEST_PAT.search("app/src/androidTest/java/A.kt")` 為 False。
     - `(?:^|/)tests?/` 只命中獨立的 `test/`、`tests/` 目錄。
     - 影響很小,因為 Android 模組的建置檔幾乎一定帶 Android 外掛,所以只是文件寫錯。
severity: minor
   - blocking: 否
   - 歸因:前半(已刪檔)是有證據的修復回歸;`androidTest` 那半是有證據的原有漏查。
   - 引句:「含已刪除讀不到、超過讀取上限、超過判定支數上限的檔」

5. 計劃〈做法〉的 `react-parallel` 和 W7 兩處沒跟上修補。
   - `react-parallel` 那段仍寫「觸發詞要命中至少兩行改動行」。效能檢核目錄、棧別提問表態閘已寫明「推送前數增行、改檔前推播分不出增刪故數全部」,計劃本身沒同步。
   - W7 的偵測清單沒提根 `package.json` 的 `eslintConfig`(物件才算)。程式與 `lint-declaration-health` 有寫,計劃的〈做法〉沒有。
   - 計劃〈審計修正紀錄〉只有 r1,沒有 r2 一筆,r2 的折入只散在各家節點。
severity: minor
   - blocking: 否
   - 歸因:未判定。是文件沒同步,不是行為問題。
   - 引句:「觸發詞要命中至少兩行改動行才算適用」

**2. 摘要行分類、每支檔有家、放行理由**

- 這 8 個檔(計劃、`bound-tests-gate`、`lint-declaration-health`、`lumos-cli-lifecycle`、`pitfalls-code-loop`、`效能檢核目錄`、`棧別提問表態閘`、`.lumos/lint-waivers.json`)都是既有節點或既有檔。我只看修補差異,沒有新增前綴行,也沒有新增程式檔,所以沒有新的摘要行分類或「每支檔有家」問題。
- 決策 d2 是 `decision-amend` 改欄位文字,四欄都在,沒有被破壞。
- 文件引用的 `t_` 測試名都在 `scripts/test_lumos.py`,查無缺漏。`t_infra_before_react_stack_key` 是計劃裡引用另一份計劃的既有說法,不在這次修補內。
- `.lumos/lint-waivers.json` 第一條理由的更正屬實:
  - `ruff --select C901`,`max-complexity=10`,`_stack_applicability` 在 600d7b02、b9ff5494、9591e609 都是 13。
  - 所以修補沒有讓它變複雜。
  - 更正後的理由只說明「不是新增的函式」和 13 的來源,沒寫為什麼不拆。這和更正前相同,不算新缺口。

**3. 三問**

- **原問題的修復效果**:我只獨立核對了文件宣稱與程式行為是否一致,沒重跑測試,也沒做殺傷力驗證。已核對的事項:
  - 先剝註解:`'**/*.yml'` 字串後面的 `android {` 仍判 Android,區塊註解裡的 `android {` 不算。
  - Spring 認 `id("…")`、`id '…'`、`apply plugin: '…'`、Maven 的 `spring-boot-maven-plugin`、版本目錄 `libs.plugins.spring.boot`。
  - 依賴座標 `org.springframework.boot:…` 判不出。
  - `apply(plugin = "…")` 這種 KTS 寫法判不出。文件只寫「id/apply plugin 形式」,沒有明說這點;偏向判不出,方向安全。
  - 判定記憶最多 64 份;`now=` 在 `_review_roles` 的預設是 None,也就是真實時鐘。
  - `_uses_vitest` 的依賴優先與 S1 一致。
  - `eslintConfig` 只認物件。
- **相鄰路徑**:我沒跑角色路的批次讀取實驗,只讀了程式。
- **同一案例修前修後**:舊說法(`_ROLE_CLOCK`、`_NODE_FLAVOR_CACHE`、`lru_cache`、「依賴座標算伺服端」、兩趟剝註解)在活文件裡都沒有殘留。唯一殘留的「兩趟」是 `test_lumos.py` 的測試 docstring,內容是「改回先 find("/*") 再剝 // 的兩趟寫法」,屬翻紅說明,正確。
- **未驗範圍**:沒有核對 `skills/`、範本和 README 類文件(它們不在這次文件修補差異裡)。沒有核對 `r3-lumos.patch` 以外的程式行為正確性。`lumos doctor` 和 `lint` 沒跑。

最嚴重 severity: minor;blocking 共 0 條。

相關檔案:
- /Users/enzo/orca/workspaces/lumos-toolchain/web-react/docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md
- /Users/enzo/orca/workspaces/lumos-toolchain/web-react/docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md
- /Users/enzo/orca/workspaces/lumos-toolchain/web-react/docs/lumos-toolchain-knowledge/Projects/前端框架從vue分出_計劃.md
- /Users/enzo/orca/workspaces/lumos-toolchain/web-react/docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md
- /Users/enzo/orca/workspaces/lumos-toolchain/web-react/docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md
- /Users/enzo/orca/workspaces/lumos-toolchain/web-react/scripts/lumos
- /Users/enzo/orca/workspaces/lumos-toolchain/web-react/.lumos/lint-waivers.json

我的臨時目錄 `/private/tmp/lumos-seat-work/code-前端框架從vue分出/整合-sonnet` 已用字面絕對路徑刪除。
