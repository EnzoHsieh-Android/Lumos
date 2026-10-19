severity: major

範圍:修補差異 r3-repair-lumos.patch 逐段讀完,修前 b9ff5494 與修後 9591e609 的 `scripts/lumos` 取出放臨時目錄,載入後兩版對跑。實驗放在 `/tmp/lumos-seat-work/code-前端框架從vue分出/正確性-sonnet/`,兩個臨時 git repo 已刪。

## Findings

### 1. 超過 512KB 的來源檔(.java / .kt)被判成 backend,修前是判不出
severity: major
blocking: 是
歸因:有證據的修復回歸

- **diff 段落:** `_review_roles` 裡新加的 `("" if n is not None else None)`。
- **問題:** 這個 `""` 映射原本是為超限的建置檔寫的,但對所有 `want` 裡的檔一律生效,來源檔也被一起轉成 `""`。
- **為什麼會判錯:** `_review_role_for` 的手機分支只有 `content is None` 才判不出。`""` 會繼續往下走:
  - 在 `.java` 走到 `not _ROLE_ANDROID_IMPORT.search("")`,直接回 backend。
  - 在 `.kt` 走到 `_kt_role`,再依建置檔判成 backend。
  - 超大檔其實沒讀,所以不知道它有沒有 UI 匯入。
- **和 pitfalls 路徑不一致:** 工作樹路徑的 `_kt_flavor` 寫 `content or None`,把空字串當判不出,這邊沒對齊。
- **具體例 1:**
  - 輸入:`Big.java`,600KB,第一行 `import androidx.appcompat.app.AppCompatActivity;`。
  - 預期:判不出(None)。
  - 修前:None。
  - 修後:`'backend'`。
  - 同一個 repo 裡讀得到的 `Small.java` 判成 frontend。
- **具體例 2:**
  - 輸入:根目錄 `build.gradle.kts` 是 Spring,`app/Big.kt` 超過 512KB 且以 `import androidx.compose.runtime.Composable` 開頭。
  - 修前:None。
  - 修後:`'backend'`。
- **重現(兩版對跑):** 兩個實驗用 `_review_roles(R, base, head, budget=30)`。
  - 例 1 輸出:`before {'Big.java': None, 'Small.java': 'frontend'}`,`after {'Big.java': 'backend', 'Small.java': 'frontend'}`。
  - 例 2 輸出:`before {'app/Big.kt': None, ...}`,`after {'app/Big.kt': 'backend', ...}`。
- **整批 16MB 總量上限:** 超過上限的來源檔也走同一條路,被判成 backend。
- **測試抓不到:**
  - `t_review_role_skips_huge_blobs` 的現場沒有任何建置檔,`.kt` 因此落到 None 而綠。
  - 新加的 `t_review_roles_oversize_build_stops_not_climbs` 和 `t_review_roles_total_cap_stops_not_climbs` 都只驗建置檔。
  - 把 `""` 映射限縮到建置檔名,上述測試照綠;現有測試沒有任何一條會對這個壞法翻紅。
- **修法方向:** 只對建置檔和 package.json 回 `""`,來源檔維持 None;或讓 `_kt_flavor_at` 和 `.java` 分支把 `""` 當判不出。

引句:「blobs = {k: (v.decode("utf-8", "replace") if v is not None else ("" if n is not None else None))」

### 2. 跑過證據的新錨定讓 vitest 在 turbo / `pnpm -r` / 帶時間戳前綴的輸出下判成沒跑
severity: major
blocking: 是
歸因:有證據的修復回歸

- **diff 段落:** `_RAN_EVIDENCE["node-jest"]["re"]` 把 `Tests` 錨在行首(只容空白和色碼)。
- **問題:** vitest 的摘要行沒有 `Tests:`。monorepo 常見的輸出會在行首加前綴,新樣式就對不到。
  - turborepo 加 `@org/web:test: `。
  - `pnpm -r` 加 `packages/app test: `。
  - CI 加 `[12:00:01] `。
- **具體例:**
  - 輸入:`"@org/web:test:  Test Files  1 passed (1)\n@org/web:test:       Tests  1 passed (1)\n"`。
  - 預期:有證據(測試真的跑過且 passed)。
  - 修前:True。修後:False,會連同 fix_hint 叫人換 reporter,但那不是真正原因。
- **對照:**
  - `"      Tests  1 passed (1)\n"` 和 `"Tests:       1 passed, 1 total\n"` 兩版都是 True。
  - 只有帶前綴的 vitest 行從 True 變 False。
  - 被擋掉的不是 r2 資安席想擋的「標題裡剛好有 Tests 2 passed」,是真實的 passed 摘要。
- **重現:** `m._ran_evidence_check("node-vitest", s)[0]`,修前 `True`,修後 `False`。
- **測試抓不到:** 新測試 `F:vitest 縮排摘要照認` 只驗純縮排,沒有任何前綴的案例,改回前綴會失敗的情況沒人守。

引句:「(?:Tests:|(?:^|(?<=\n))[^\S\n]*(?:\x1b\[[0-9;]*m[^\S\n]*)*Tests\b)[^\n]{0,200}?(?<![0-9])[1-9]\d*[^\S\n]+passed」

### 3. 新掃描器 `_KT_SCAN_TOKEN` 對含大量 `\"` 的長行是二次方,修前是線性
severity: major
blocking: 是(給得出最小重現;構造輸入才觸發,見下)
歸因:有證據的修復回歸

- **diff 段落:** `_KT_SCAN_TOKEN` 的 `"(?:\\.|[^"\\\n])*"` 與 `'(?:\\.|[^'\\\n])*'`。
- **問題:** 字串沒閉合時,這個起點會一路掃到行尾才失敗。引擎接著從下一個 `"` 重試,每次又掃到行尾。
- **具體例:**
  - 輸入:一行 `"` 後面接 N 個 `\"`,行尾不閉合。
  - 實測 `_kt_strip_comments`:N=1 萬 1.37 秒、2 萬 5.16 秒、4 萬 20.05 秒(約 8 萬字元)。單引號版同樣:4 萬 20.02 秒。
  - 修前版本同輸入 0.0 秒。
  - 建置檔上限是 512KB,外推會到分鐘到小時級。
- **為什麼要報:**
  - 這和 r2 資源席抓的 `^\s*` 空行回溯同一類,作者為它加了全檔守衛,這條是新寫的同類。
  - pitfalls 路徑沒有預算保護,`_review_roles` 的預算也只在檔與檔之間檢查,卡不到單一次正規式。
- **前提:** 要構造「未閉合字串加大量跳脫引號」的建置檔才會觸發。威脅模型是單人、AI 依序操作,實際觸發機率低,但我能重現且規模夠大,所以不降級。
- **修法方向:** 讓未閉合的字串候選吃到行尾,例如在結尾改成 `(?:"|$)`,這樣失敗的起點也會消耗整行,不會重掃。

引句:「_KT_SCAN_TOKEN = re.compile(r'\"\"\"[\\s\\S]*?(?:\"\"\"|\\Z)|\"(?:\\\\.|[^\"\\\\\\n])*\"|\\'(?:\\\\.|[^\\'\\\\\\n])*\\'|//[^\\n]*|/\\*[\\s\\S]*?(?:\\*/|\\Z)')」

### 4. Spring 判法收窄後漏掉括號式的 apply
severity: minor
blocking: 否
歸因:有證據的修復回歸(召回率下降,方向是安全的判不出)

- **diff 段落:** `_KT_BUILD_SERVER` 的 `\bapply\s+plugin\s*:\s*` 分支。
- **問題:** 只認 Groovy 的 `apply plugin: '…'`,不認這兩種寫法:
  - Kotlin DSL 的 `apply(plugin = "org.springframework.boot")`。
  - Groovy 的括號形式。
  - 這是 `subprojects {}` 裡很常見的寫法。
- **證據:**
  - `_kt_build_verdict('apply(plugin = "org.springframework.boot")\n')`:修前 server,修後 None。
  - 同一份文字:`apply plugin: 'org.springframework.boot'` 修後仍是 server。
- **影響:** 真的伺服端 Kotlin 專案會被判不出,繼續被附上 Android 題。不會把 Android 判成伺服端,所以只是 minor。

引句:「(?:\bid\s*\(?\s*|\bapply\s+plugin\s*:\s*)["']org\.springframework\.boot["']」

### 5. pom.xml 沒有 XML 註解的剝除,而且掃描器把 `/*` 當註解起點
severity: minor
blocking: 否
歸因:未判定(pom 在修前就走同一支剝註解,但 `spring-boot-starter-parent` 是這次新加的判定字串)

- **問題 a:** `<!-- <artifactId>spring-boot-starter-parent</artifactId> -->` 這種被註解掉的 parent 會被判成 server。實測修後 server,修前 None。
- **問題 b:** pom 裡的 `<include>**/*Test.java</include>` 含 `/*`,會被當區塊註解起點,吞到下一個 `*/` 或檔尾。後面的 spring-boot-maven-plugin 會被吃掉,結果變 None。這個方向是安全的。
- **範圍:** Android 專案幾乎沒有 pom,風險小,只是行為不一致。

引句:「|io\.ktor\.plugin|spring-boot-maven-plugin|spring-boot-starter-parent」

### 6. 全檔守衛 `t_no_multiline_caret_whitespace_star` 有漏洞
severity: minor
blocking: 否
歸因:有證據的原有漏查

- **問題:** 守衛逐行找 `\bre\.M\b|re\.MULTILINE|\(\?m\)`,別名 `_re_f.M` 不在內。
- **證據:** 我用 AST 掃全檔,`^\s*` 搭多行旗標的唯一剩餘處是 `scripts/lumos:6761`,即 `_re_f.search(r"^\s*FLAG:(\S+)", summ, _re_f.M)`。
- **實測:** 4 萬行空行 2.88 秒、2 萬行 0.71 秒,是二次方,但規模小。
- **影響:** 測試檔案中的「全檔守」說明不實,一般情況下影響低。

引句:「if "^\\s*" in ln and (re.search(r"\bre\.M\b|re\.MULTILINE|\(\?m\)", ln))]」

## 已驗無問題

**判定記憶(`_KT_BUILD_VERDICT_CACHE`)**
- 灌 70 份不同文字後大小維持 64。
- 淘汰最早那份後重算判定一致,是純函式,key 是全文,沒有舊值讀到新檔的問題。

**新掃描器的字串與註解判法**(對照修前,`_kt_build_verdict`)
- 以下輸入,修後都得到預期的 server:
  - 跳脫引號 `"a\" // x"`。
  - 字元常值 `'"'`。
  - 三引號內含 `"b"`、`//`、`/*`。
  - 行註解接字串。
  - `${foo("// x")}` 模板。
  - `exclude("**/*.kt")` 的 glob。
- 修前同題 `template`、`triple_with_quote`、`kts_exclude_glob` 判成 None,是修補確實修到的錯。
- 未閉合的 `/*` 吃到檔尾,結果 None,符合設計。

**`now=` 參數**
- 全 repo 與測試已無 `_ROLE_CLOCK`、`_NODE_FLAVOR_CACHE`、`_node_pkg_text`、`_functools`、`_KT_LINE_COMMENT` 的殘留參照。
- 呼叫端 `scripts/lumos:47711`、`52961` 都沒傳 `now`,走 `now or _t.monotonic`,執行當下才取值,測試 patch `time.monotonic` 的寫法仍生效。

**`^[ \t]*` 改寫**
- 8 處都沒有被吞換行的語意依賴。
- `_quote_norm` 最後會把所有空白摺疊;`clause_bindings` 和 `decision_amend` 是單行匹配。
- 唯一差異是 `\s` 能吃的 NBSP、全形空格,這幾處不會出現。

**測試檔判法**(`_PITFALL_DIFF_TEST_PAT` 兩版對 26 個路徑逐個比對)
- 根目錄 `tests/a.py`、`test/a.py` 修後算測試(修前不算),符合修補意圖。
- `latest/`、`contest/`、`testing/` 仍不算。
- `test.py`、`test.go`、`spec.rb`、`Test.tsx`、`TEST.js`、`test.d.ts`、`Test.java` 修後變成正式檔,是設計上的收窄。
- 副檔名比較忽略大小寫,所以 `test.TS` 仍算測試。

**`eslintConfig` 值要是物件**
- ESLint 規定這個欄位是物件,收窄正確;空物件 `{}` 仍算命中。

**`_stack_platform_excluded` 加 `.exists()`**
- 刪檔不再讓「全部判伺服端」恆假,正確。
- 前提是工作樹等於被審範圍的 head;若 `--diff` 指的 head 不是目前檢出的版本,新增但工作樹沒有的檔會被靜默略過。我沒實測這條路徑,列入未驗。

## 三問
1. **原問題的修復效果:**
   - 剝註解和 Spring 外掛判法確實修到(finding 前 4 段的 `template` 等修前判錯、修後判對)。
   - 超限建置檔停在該層判不出,已用 `t_review_roles_oversize_build_stops_not_climbs` 的現場驗過。
   - 超限來源檔的修復有副作用,即 finding 1。
2. **修補處的正常、錯誤與相鄰呼叫路徑:**
   - 正常讀取路徑(建置檔小於上限)不受影響。
   - 相鄰的「來源檔超限」路徑被改壞(finding 1)。
   - `_RAN_EVIDENCE` 新錨定對相鄰的帶前綴 vitest 輸出判錯(finding 2)。
   - 新掃描器對長行輸入退化(finding 3)。
3. **新發現同一案例的修前修後:** 各 finding 內已列兩版結果。finding 5 的 pom 兩種情況修前判定字串不同,無法等價比較,標未判定。

未驗範圍:
- `_review_roles` 的時間預算實測。
- 帶換行的檔名路徑,`sizes` 對位與修前相同。
- Kotlin 巢狀註解 `/* /* */ */`,掃描器以第一個 `*/` 收尾,會露出註解裡的 `id("org.springframework.boot")`,我只在腦內推演,沒有跑。
- `.exists()` 在 head 與工作樹不一致時的行為。

最嚴重 severity:major,blocking 共 3 條(finding 1、2、3)。
