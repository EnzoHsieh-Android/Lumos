severity: major

### F1 文件承諾「測試區塊新增 excludeTags 也列」且三種寫法都認,Groovy 的 `excludeTags 'x'` 抓不到
severity: major
blocking: 是 — 條款、計劃與標準都承諾會列,最常見的 Groovy 寫法卻放過,等於留了一條繞過路徑。
引句:「測試區塊新增 `excludeTags` 也列」
file: `scripts/lumos:48861`(`_TG_IN_TEST_BLOCK` 的第三條 `re.compile(r"\bexclude(?:Tags|Categories|Engines)\s*\(")` 一定要接左括號)
後果:
- 計劃〈規則表〉開頭寫「三種寫法都認(Kotlin 的 `x = v`、Groovy 的 `x v`、Provider 的 `x.set(v)`)」。
- S7 對 excludeTags 沒有限定寫法。
- 照 Groovy 慣用寫法 `excludeTags 'slow'` 或 `excludeCategories 'x.Slow'` 把測試排除掉,比對不會列候選。
- 同一區塊的 `exclude '**/*FooTest*'` 倒是會列,所以寫法間不一致。
- 新測試只用 Kotlin 的 `excludeTags("slow")`,沒有 Groovy 案例。

重現(在暫存 repo 提交兩版建置檔,用 `lumos test-guard --diff A..B --json`):

| 檔案 | 改動 | 結果 |
|---|---|---|
| `app/build.gradle` | 新增 `test { useJUnitPlatform { excludeTags 'slow' } }` | `[]` |
| `app/build.gradle` | 新增 `test { useJUnit { excludeCategories 'x.Slow' } }` | `[]` |
| `app/build.gradle` | 新增 `test { exclude '**/*FooTest*' }` | 列 `tq/build-config` |
| `app/build.gradle.kts` | 新增 `tasks.withType<Test> { useJUnitPlatform { excludeTags("slow") } }` | 列 `tq/build-config` |

歸因:有證據的原有漏查。修前(22cc6675)Groovy 與 Kotlin 兩種寫法都是 `[]`,修後只補了 Kotlin。修補把偵測範圍講成通用,但只補到一半。

### F2 計劃〈做法一〉的比對起點段落還寫 `include_local=True`,跟程式、S11、test-guard 筆記的「優先取遠端主線」相反
severity: major
blocking: 是 — 照這段重做會把「本機 main 上還沒推出去的提交」扣出比對範圍,正是修補要避免的漏洞。
引句:「用 `_lens_default_base(root, tip=終點, include_local=True)`(Room 守衛手動跑用的同一支)找得到」
file: `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:79`;程式 `scripts/lumos:49267-49271`(先 `include_local=False`,沒有才退回 `True`)
後果:
- 同一份計劃的 S11 寫「本機 main 上還沒推出去的提交照樣算進來(分岔點優先取遠端主線)」。
- test-guard 筆記的 WHY 也寫「先只看遠端主線」,只有這一段沒改。
- 三個月後的人讀到這段,會以為本機主線也算分岔點候選。

重現:
- `grep -n include_local docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md` 只有第 79 行,值是 True。
- `sed -n 49262,49272p scripts/lumos` 顯示 `_tg_start` 先取 `include_local=False`。

歸因:有證據的原有漏查。`git show 22cc6675:<計劃>` 與 `fcd27439:<計劃>` 都含同一句(各 1 筆),程式修前就是遠端優先。這一輪文件補了 S11 與 WHY,卻漏了這一段。

### F3 `tq/catch-no-fail` 的規則表與標準「抓什麼」沒跟上新分支(try 結尾有 fail、catch 接得住 AssertionError 又吞掉)
severity: minor
blocking: 否 — 擋下訊息有「該確認」可救,只是標準的描述不完整。
引句:「try 沒有 `fail(` 而 catch 裡斷言或是空的」
file: `skills/lumos-project-notes/commands/test-quality-standard.md:38`;計劃規則表 `tq/catch-no-fail` 列(`Android測試防竄改檢查_計劃.md:118`);程式 `scripts/lumos:48801-48826`
後果:
- 只有 S6 條款補了「try 結尾補 `fail()` 而 catch 接得住 AssertionError 又只印出或是空的,照樣要列」。
- 規則表的成立條件和標準的「抓什麼」仍寫成必須「try 沒有 fail」。
- 照標準寫 `try { …; fail("x") } catch (e: Throwable) { println(e) }` 的人會以為安全,推送時才被擋。

重現:
- 新增 `@Test fun s4() { try { assertEquals(5, f(1)); fail("x") } catch (e: Throwable) { println(e) } }`。
- 修前 `[]`,修後列 `tq/catch-no-fail`。

歸因:有證據的修復回歸。行為在這一輪新增,文件只更新了條款一處。

### F4 CI 規則的 `-x` 對整行判斷,同一行串了 `pytest -x tests/` 就誤報;條款寫「不列」
severity: minor
blocking: 否 — 是候選不是定罪,可放行,屬精度問題。
引句:「`pytest -x tests/`、`mkdir -p a || true`、不含 Gradle 呼叫的區塊加 `continue-on-error: true`」
file: `scripts/lumos:49008`(`_TG_CI_X` 對整條邏輯行 search)與 `scripts/lumos:49032-49047`
後果:
- 計劃對「拿掉測試任務」那條寫了「照 `&&`、`||`、`;`、`|` 切段,只看有 Gradle 呼叫的段」。
- 對「新增 `-x`」那條沒切段。
- `./gradlew assemble && pytest -x tests/` 會被當成 Gradle 被排除了 test。
- 讀文件的人會以為兩條都切段。

重現:
- 把 CI 檔的一行從 `./gradlew assemble` 改成 `./gradlew assemble && pytest -x tests/`。
- 修前與修後都列 `tq/ci-config`(`tests` 含 `test`)。

歸因:有證據的原有漏查。修前修後輸出相同。

### F5 單行過長的測試檔,擋下訊息自相矛盾:「沒有比對」又「其餘照比」
severity: minor
blocking: 否 — 只是訊息措辭,但這個訊息就是給人和 AI 照著處理的。
引句:「測試檔裡超過 2 萬字的行不比對,那支檔另列一條可放行的 `tq/too-large`」
file: `scripts/lumos:49156-49172`(`_TG_WHY["tq/too-large"]` 的基本句沒改)與 `scripts/lumos:49283-49287`
後果:
- 實際輸出:「檔案超過比對工具的上限,沒有比對(有一行超過 20000 字,那幾行沒比對,其餘照比)」。
- 「該確認」仍是「人工看這支檔的改動,或拆小」。
- 文件與行為說的是「只抹掉長行、其餘照比」,但開頭那句說整支沒比。

重現:
- 在測試檔加一行 `// ` 加 20001 個 x,用 `lumos test-guard --diff A..B` 看輸出。
- 修前:「…沒有比對(有一行超過 20000 字,不解析)」,前後一致。
- 修後:前後矛盾。

歸因:有證據的修復回歸。修補只改了括號內的 extra 文字,沒改基本句。

### F6 「引號整個是含 test 的任務名」實際上任何帶 test 子字串的引號字串都算,例如 `"latest"`
severity: minor
blocking: 否 — 誤報而不是漏報。
引句:「或區塊開頭、同一行裡有引號整個是含 test 的任務名」
file: `scripts/lumos:48859`(`_TG_TASK_NAME_Q`:`["']:?(?:[\w-]+:)*[\w-]*[Tt][Ee][Ss][Tt][\w-]*["']`)
後果:
- 計劃、筆記與標準都稱為「任務名形狀」,但程式只檢查引號內有沒有 test 這四個字母。
- `"latest"`、`"contest"` 一樣讓同一行的 `enabled = false` 被當成測試任務關閉。
- 讀文件的人無法預期這類誤報。

重現:
- 新增 `if (project.hasProperty("latest")) { tasks.configureEach { enabled = false } }`。
- 列 `tq/build-config`,修前修後皆同。

歸因:有證據的原有漏查。

### F7 計劃〈規則表〉`tq/skip-added` 列的偵測清單比 S1 與程式少
severity: minor
blocking: 否 — 純精度。
引句:「`Assumptions.assume…(` 的命中次數差大於 0」
file: `Android測試防竄改檢查_計劃.md:116`;程式 `scripts/lumos:48837-48840`
後果:
- 同一份計劃的 S1 寫了 `TruthJUnit.assume()`,規則表的那一列沒有。
- 程式另外認 `@Disabled*`、`@Enabled(On|If|For)*`,規則表也沒寫。
- 依規則表判斷「會不會被抓」的人會少算。

重現:
- 對照 `_TG_SKIP_ANN_RE` 與 `_TG_ASSUME_RE` 的樣式和規則表那一列。

歸因:有證據的原有漏查。

### F8 Verification 筆記的 `revalidate_when` 已被 r2 到 r4 的規則改寫觸發,筆記本身沒更新
severity: minor
blocking: 否 — 重跑證據只在卷證 intake 裡,圖譜裡查不到。
引句:「revalidate_when: 比對工具的任一條 tq/ 規則、測試函式切法、指紋算法或比對起點改寫時,重跑考場對照表與真實歷史」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-02_Android測試防竄改檢查實跑.md:6`
後果:
- 這篇筆記最後一次改動是「代碼審第一輪折入」。
- 之後規則、指紋身分、比對起點都改過。
- 作者在 r4-intake 自述重跑 776 個提交仍是 44 條、對照表 21 筆相同,但這個數字沒回寫到筆記。
- 三個月後的人看不出筆記的結果是改寫前還是改寫後。

重現:
- `git log --oneline -3 -- <該筆記>` 最新是 `9fcc5f53f wip: 代碼審第一輪折入`。
- 我沒有重跑考場歷史(私有專案),所以只確認筆記沒更新,不判重跑結果是否正確。

歸因:未判定。

## 圖譜鏡頭
- `lumos lint` 跑 `Systems/test-guard`、`Projects/Android測試防竄改檢查_計劃`、`Systems/pitfalls-code-loop`,均 0 問題。`lumos doctor` 為 0 issues。
- test-guard 新增與改寫的 WHY 都有 `[出處:]`、`[因:]` 與 `[test:]`,沒有寫別家的檔名,也沒抄程式碼推得出的現況。
- `lumos impact --diff 047031883..fcd27439…` 列到 `Systems/pitfalls-code-loop`(RISK 守衛面)與 `pitfalls-lint-adapter`。
  - 兩篇都沒有 INVARIANT 合約行與這輪改動衝突。
  - `pitfalls-lint-adapter` 的 KEY 已同步寫「有候選或比對出錯時留帳」。
- 全 repo 搜尋「背後跑」「有候選留帳」,沒有殘留舊說法。指令參考(中英)、06 手冊、標準、pitfalls-code-loop 都已改。
- 「同族都只認 1」我查了:`LUMOS_SKIP_ROOM_GUARD` 與 `LUMOS_SKIP_NOTE_SHAPE` 都是 `== "1"`,事實成立。
- 標準的「抓不到」與 `lumos test-guard --json` 的 `limitations` 逐字同一份:我用腳本比對(去掉反引號,以「;」連接)為 True,`t_tq_guard_cli_contract` 也釘著。
- 本機跑 `-k tq_guard` 251 passed,`-k lint_new` 79 passed,`-k lint_waive` 30 passed,0 failed。

## 去識別化與卷證指紋
- 掃描 r4-snapshot.patch 中非 `review-reports` 的公開檔的新增行,找本機路徑、7 到 12 碼十六進位、套件名樣式和分支名。
  - 唯一的十六進位命中是計劃裡的 `047031883`。它是工具鏈自己的分支起點,不是考場識別字。
  - 套件名樣式只有公開函式庫(org.junit、com.google.common.truth 等)與 README 明列的代稱 `com.example.pos…`。
- CamelCase 識別字只見代稱(`CategoryVm`、`CategorySource`、`VoidCategory` 等)與公開 API 名。
- 這一輪沒有改動 `governance/eval/results/` 底下任何檔。
- 兩個 manifest 實算 sha256,全數吻合:
  - `android-test-guard-drill-20261102`:9 個檔,無缺漏、無多出。
  - `android-unit-standard-drill-20261101`:20 個檔,無缺漏、無多出。

## 三問
1. **原問題的修復效果有何行為證據?** 有。我實跑確認 r3 要修的案例都已修好:多行 assume、`-xtest`、`--exclude-task=test`、`|| exit 0`、`|| echo`、子殼層與 `$()`、`findByName` 與 `tasks[…]`、detekt 內層 reports、2 萬字長行抹掉其餘照比、環境變數只認 1。對應測試全綠。但 excludeTags 只修了 Kotlin 寫法(F1),文件也漏了一處舊段落(F2)。
2. **修補處的正常、錯誤與相鄰路徑是否仍成立?**
   - 成立:
     - 測試檔長行不影響同檔其他規則(實測仍列 `tq/skip-added`)。
     - JUnit 5 改成 `private` 或 `static` 如工具輸出所述不列。
   - 不成立:
     - 相鄰路徑多行 CI 的 `-x` 有誤報(F4)。
     - `"latest"` 誤判(F6)。
     - 太大訊息自相矛盾(F5)。
3. **新發現的同一案例在修前、修後各是什麼結果?**

   | 案例 | 修前 | 修後 |
   |---|---|---|
   | Groovy `excludeTags` | `[]` | `[]` |
   | Kotlin `excludeTags(…)` | `[]` | 列 |
   | try 結尾有 `fail`、catch Throwable 只印 | `[]` | 列 |
   | 長行訊息 | 前後一致 | 自相矛盾 |
   | `./gradlew … && pytest -x tests/` | 列 | 列 |
   | `"latest"` | 列 | 列 |

   歸因對應各條 finding:F1、F4、F6、F7 是原有漏查,F3、F5 是修復回歸,F2 是原有漏查,F8 未判定。

共 8 條 finding(2 條 major、6 條 minor),另三問已答。
