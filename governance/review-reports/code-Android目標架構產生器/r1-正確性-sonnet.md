severity: major

## F1 範圍判斷的斜線邊界與 NFC 在產出的 Kotlin 裡沒有任何測試守
severity: major
blocking: 是
引句:「return scopeDirs.any { rel == it || rel.startsWith("$it/") } && rel !in legacyFiles」
佐證: file: `scripts/test_lumos.py:t_arch_template_android_konsist_legacy_shape`(diff 內 S8 那支)
具體失敗場景:
- 計劃〈做法〉8 與本案鏡頭 4 都要求「落在範圍目錄底下(以斜線為界)」。`t_arch_template_android_konsist_legacy_shape` 只用 `in` 比對六個字串片段:`generateSequence(...)`、`val rootNames = all.classes()`、`private val scopeDirs = listOf(...)`、`readLegacyFiles(File(repoRoot...`、`check(f.isFile)`、`rel !in legacyFiles`。它不看 `inScope` 的比對式,也不看 `relPath` 的 `nfc(...)`。
- 最小重現:複製 scripts 與 skills 到臨時目錄,把資料檔裡兩處 `rel == it || rel.startsWith("$it/")` 都換成 `rel.startsWith(it)`。範圍 `feature/cart` 因此會吃進鄰目錄 `feature/cartx/...`,但 `python3.14 scripts/test_lumos.py -k arch_template_android_konsist_legacy_shape` 仍然 `8 passed, 0 failed`。
- 產生器這邊的 `t_arch_template_android_legacy_modes` 有逐檔期望清單(`cartx`、`mysrc/test`、NFD 的 Café),Kotlin 這邊沒有對應防線。兩邊判法一旦分岔,整套測試照綠。
- 工具鏈 repo 編譯不了 Kotlin,測試只能比對文字。但文字檢查至少該釘住 `inScope` 的比對式和 `relPath` 裡的 `nfc(`;S10 手動驗證只做過一次,沒有釘住這幾行。

## F2 範圍目錄含 `$` 時,產出的 Kotlin 把路徑當字串樣板
severity: minor
blocking: 否
引句:「"SCOPE_LIST": ", ".join(_j.dumps(s, ensure_ascii=False) for s in norm),」
佐證: file: `scripts/lumos:57813`(diff 內 `_arch_tpl_render`)
具體失敗場景:
- `--scope 'app/src/main/java/com/ex/app/$gen'`。`_arch_tpl_scope_error` 不擋 `$`,git 追蹤的檔也存在,所以產生器通過。
- `--print test` 實跑的輸出是 `private val scopeDirs = listOf("app/src/main/java/com/ex/app/$gen").map { nfc(it) }`。Kotlin 會把 `$gen` 當成對名為 `gen` 的屬性的引用:未定義時編譯失敗;剛好有同名成員時,範圍靜默變成別的字串,測試空轉。
- 同一個 `$gen` 寫進舊檔清單 JSON 就是字面的,所以舊檔清單與範圍目錄的判法在這個輸入上不一致。`json.dumps` 沒有跳脫 `$`,範圍檢查也沒擋。

## F3 舊檔清單刪到最後一行後,Python 與 Kotlin 對同一個檔的讀法相反
severity: minor
blocking: 否
引句:「while (i < text.length && (text[i].isWhitespace() || text[i] == ',')) i++」
佐證: file: `scripts/lumos:57429`(`_arch_legacy_at` 走 `_json_at_ref` 嚴格 JSON)
具體失敗場景:
- 技能文件教「舊檔重構完,從清單刪掉它那一行」。產生器輸出每行一個路徑、依字典序排,所以刪掉最後一行,前一行會留下尾逗號:`"a.kt",` 後面直接接 `]`。
- Python 的 `json.loads` 會拒絕(實測 `Illegal trailing comma before end of array`),於是 `_arch_legacy_at` 回 unreadable,清單當空集合,整份舊檔都照目標審。
- Kotlin 手寫讀法把逗號當空白跳過,照常讀成清單,架構測試仍然綠。同一份檔,兩邊判成相反結果,而技能文件沒有提醒要檢查 JSON 合法。
- 開頭逗號 `[,"a"]` 與連續逗號也有同樣的分歧。

## F4 ⚠ 舊檔清單排除 androidTest 與 testFixtures,但 lumos 的審查把這兩個目錄的檔當程式檔
severity: minor
blocking: 否
引句:「_ARCH_TPL_LEGACY_SKIP = ("src/test/", "src/androidTest/", "src/testFixtures/")」
佐證: file: `scripts/lumos:37565`(`_PITFALL_DIFF_TEST_PAT`);同一個樣式用在 `scripts/lumos` 的 `_arch_code_file`
具體失敗場景:
- 實測 `_arch_code_file("feature/cart/src/androidTest/java/x/B.kt")` 與 `src/testFixtures/...` 都回 True,`_arch_target_rule_index(..., [("feature/cart/**", ...)])` 命中 0。只有 `src/test/` 因 `(?:^|/)tests?/` 才被排除。
- 採用 new-only 後,既有的 androidTest 或 testFixtures 檔不在清單上。日後分支只要碰到其中一支,架構對齊席就拿目標規則判它,違反即 major。
- 這與技能文件「範圍內現有的檔全部列進舊檔清單,照舊鄰居審」不符。Konsist 的 `scopeFromProduction` 一向不看這兩個目錄,所以測試與審查兩邊判法不同。
- 計劃〈做法〉4 白紙黑字排除這三個目錄,所以是否算缺陷要交編排者裁。

## F5 usecase=required 的 ViewModel 測試比 usecase=optional 的更鬆,漏掉資料來源
severity: minor
blocking: 否
引句:「type in forbiddenInViewModel || type.endsWith("Repository")」
佐證: file: `scripts/templates/android-arch-target.md`(diff 內 `test usecase=required` 與 `test usecase=optional` 兩塊)
具體失敗場景:
- required 的規則寫「也不直接收 Repository 或資料來源」,並綁了 `viewModelDependsOnUseCasesNotFrameworkOrRepository`。
- 該測試只擋型別名以 `Repository` 結尾。`ViewModel(private val dao: OrderDao)` 或 `OrderRepositoryImpl` 的型別名結尾不是 `Repository`,測試仍綠。
- optional 版明確擋 `RepositoryImpl`、`DataSource`、`Dao`、`Api`。開關語意上 required 應不比 optional 鬆,實際反過來。
- 此條是讀碼推的,Kotlin 沒有編譯重現。`t_arch_template_android_switch_effects` 只檢查 optional 版的測試本文,沒有 required 版對應檢查。

## F6 定義了 `_ARCH_TPL_TEST_TAG_RE` 卻沒有任何地方使用
severity: minor
blocking: 否
引句:「_ARCH_TPL_TEST_TAG_RE = re.compile(r"\[test:([A-Za-z_][A-Za-z0-9_]*)\]")」
佐證: file: `scripts/lumos:57779`(全檔搜尋只有這一處出現)
具體失敗場景:
- 看起來是要在產生器內檢查「RULE 綁的 `[test:]` 在同份 Kotlin 檔裡有同名函式」,實際只由測試檢查。
- 「專案自己的資料檔優先」這條讀法允許專案改資料檔。專案改了 RULE 的 `[test:X]`、卻沒有 X 這支測試,產生器會 rc 0 照出,不會拒絕。
- 這是內部不一致的未使用名稱。

## 圖譜鏡頭固定席逐條判定

- `Systems/lumos-cli-read`(INVARIANT:search 預設排除 superseded、不排除 stale):**不影響**。diff 沒碰 search、濾網或排序,只新增 `arch-template` 子命令。
- `Systems/測試假綠形態`(INVARIANT:還原翻紅釘要配前置斷言證明現場成立):**不影響**,但相關。
  - 這次是新功能測試,不是 bug 修補的還原翻紅釘。
  - 新測試多有前置檢查:`rc == 0`、`len(full) == 2`、六個開關讀到、四次子程序 rc 0。
  - S8 那支沒有前置,見 F1。
- `Systems/pitfalls-code-loop`(RISK)與 `Systems/loop-convergence-recording`(RISK):**不影響**。
  - 只新增函式,沒動 `pitfalls` 分級、派工鏡頭、收斂記帳。
  - `_arch_target_vault_rel`、`_arch_targets_config`、`_lens_git` 只被當唯讀呼叫。
- `Systems/lumos-cli-lifecycle`(INVARIANT:re-inject 只覆蓋 sentinel 之間):**不影響**。`_VENDORED_TREE_FILES` 只多登記一個資料檔,沒碰注入或 sentinel。
- `Systems/design-loop`(INVARIANT:處置閘第五步)與 `Systems/guard-kill`(INVARIANT:rc 優先序、JSON 純度):**不影響**。這些路徑的程式與測試都沒動。
- `Systems/arch-alignment-lens`:本次牽連最深,沒破壞合約,但 F3 與 F4 是產生器和它的讀法之間的分歧。
  - diff 只在筆記加一句指路。
  - 舊檔清單「整條路徑比對、兩邊先轉 NFC、不當萬用字元」:Python 這邊與產生器一致,Kotlin 那邊見 F1。
- 各條合約行都沒有「⚠帶殘留 N 筆」徽章,不需要逐型答。
- 超出上限只列名的那批(`bound-tests-gate`、`cochange-guard` 等)與固定席無關,這次 diff 沒碰它們的程式。
- 角色卡:派工詞寫 `LUMOS-ROLE-CARDS: on`,但尾端沒有附到前端卡或後端卡,略過。

總結:共 6 條,major 1 條(F1),minor 5 條(F2、F3、F4、F5、F6),blocker 0 條。
