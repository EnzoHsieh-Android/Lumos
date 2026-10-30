severity: major

## F11 產出的 Kotlin 清單讀法只靠比對文字，兩個合理的改壞照綠
severity: major
blocking: 是
歸因：有證據的原有漏查（F3 的修補本身沒有行為證據）
引句:「"text[i] == ','" not in new.split("fun skipSpace")[1].split("\n        }")[0]」
佐證:file: `scripts/templates/android-arch-target.md:readLegacyFiles（修後版本）`
1. 修補宣稱要擋的錯：Kotlin 讀舊檔清單比 lumos 寬鬆（尾逗號 Kotlin 照讀、lumos 判讀不懂）。工具鏈 repo 編不了 Kotlin，所以只有 `t_arch_template_android_konsist_legacy_shape` 比對產出文字。
2. 改壞 B：在 `check(text[i] == ',')` 與 `i++` 之後加 `skipSpace(); if (i < text.length && text[i] == ']') return out`。
   - 效果：尾逗號 `["a",]` 被 Kotlin 接受，F3 的錯回來。
   - 比對結果：skipSpace 本體仍沒有 `text[i] == ','`，`check(text[i] == ',')` 與「逗號也不能多」字串也都還在。
   - 實測：`python3.14 scripts/test_lumos.py -k konsist_legacy_shape` 修後版本加改壞 B，13 passed, 0 failed。
3. 改壞 C：刪掉修補新加的空陣列提早返回 `if (i < text.length && text[i] == ']') return out`。
   - 效果：`{"files": []}`（lumos 讀得懂）會讓 Kotlin 報「只能放字串」，採用日整片紅。
   - 實測：同一支測試，13 passed, 0 failed。
   - 空清單可以出現：範圍內只有 `_arch_code_file` 判成測試或文件的檔時，清單就是 `{"files": []}`。
4. 兩版證據：
   - 修前（8a601700）：沒有逗號相關的檢查。把修後的測試檔放進修前工作樹，`-k konsist_legacy_shape` 在 `split("fun skipSpace")[1]` 拋 `list index out of range`，所以紅。
   - 修後：測試綠，但改壞 B、C 都擋不住。
5. 缺口：沒有任何檢查用行為驗證 `readLegacyFiles`。「macrobench-lab 重新編譯實跑」（驗證紀錄）在本席環境不能重現，標未判定。

## F12 required 版 ViewModel 測試只檢查名字有出現，沒檢查用法
severity: minor
blocking: 否
歸因：有證據的原有漏查
引句:「all(f'"{x}"' in req.group(0) for x in ("Repository", "RepositoryImpl", "DataSource", "Dao", "Api"))」
佐證:file: `scripts/templates/android-arch-target.md:257`
1. 輸入：把 `usecase=required` 那塊的 `dataSuffixes.any { type.endsWith(it) }` 改成 `dataSuffixes.any { type == it }`。
2. 效果：`OrderRepositoryImpl`、`OrderDao` 這類型別不再被擋，F5 要擋的錯回來。五個字串仍在函式本體內。
3. 實測：`-k switch_effects` 修後版本加這個改壞，14 passed, 0 failed。
4. 修前（把修後測試放進修前工作樹）：`S2:usecase=required 的 ViewModel 測試不比 optional 鬆` 紅，所以測試對「整個拿掉」有效，對「留著清單、改壞用法」無效。
5. 為什麼只評 minor：改壞需要動用法而保留清單，合理度比 F11 低。

## F13 範圍內 `test`／`tests` 資料夾裡的正式檔不進舊檔清單，Konsist 卻會檢查它們
severity: minor
blocking: 否
歸因：有證據的修復回歸（修前會收，修後不收）
引句:「files = sorted({f for fs in under.values() for f in fs if _arch_code_file(f)})」
佐證:file: `scripts/lumos:57489`、`scripts/lumos:37565`（`_PITFALL_DIFF_TEST_PAT` 含 `(?:^|/)tests?/`）
1. 輸入：repo 內 `feature/cart/src/main/java/x/test/Helper.kt`（package 叫 `test` 的正式檔）、`x/A.kt`、`x/ui/U.kt`，用 `--legacy new-only --print legacy` 產清單。
2. 修前：清單三支全收，含 `x/test/Helper.kt`。
3. 修後：清單只有 `A.kt`、`ui/U.kt`，`Helper.kt` 被擋掉。
4. 後果：產出的 Konsist 測試用 `Konsist.scopeFromProduction()`，`src/main` 底下的 `Helper.kt` 是正式程式。它在範圍內、不在清單上，所以被當新檔檢查。若它違反規則，採用當天就紅。
   - 文件說「new-only 剛採用時範圍內全是舊檔，全綠是正常的」，對這類檔不成立。
   - 修補的測試把 `mysrc/test/Q.kt` 從期望清單拿掉，是刻意接受，但文件沒講。
5. 處置：這類檔要手動補進 `.lumos/arch-legacy.json`，文件沒提。

## F14 技能文件〈改主意〉缺「all 改 new-only」，照做會得到一支紅測試
severity: minor
blocking: 否
歸因：有證據的原有漏查
引句:「用新的開關重跑產生器,換掉節點與架構測試兩份;**舊檔清單不要重產**」
佐證:file: `skills/lumos-project-notes/commands/target-arch-android-template.md:〈改主意怎麼做〉`
1. 輸入：原本用 `--legacy all` 採用（沒有 `.lumos/arch-legacy.json`），之後照〈換開關〉改成 `--legacy new-only`。
2. 照文件做：只換節點與測試，不產清單。
3. 結果：`readLegacyFiles` 的 `check(f.isFile)` 讓 9 支測試全紅，訊息卻建議「用 `--legacy all` 重產」，與使用者要的方向相反。
4. 文件只寫了 new-only 改 all，沒寫反向要產一次清單。

## F15 舊計劃 S1、S3 的條款句已和綁定測試不符
severity: minor
blocking: 否
歸因：有證據的原有漏查
引句:「沒換佔位照抄時 lint 應印日期格式警告。 [test: t_arch_target_android_template_valid]」
佐證:file: `docs/lumos-toolchain-knowledge/Projects/Android的MVVM與DDD目標架構範本_計劃.md:驗收條款`
1. 新增的補註（修補差異之外的完整改動）說「S1 的『沒換佔位照抄』那半不再適用」，但條款句沒改。
2. S3 條款句仍寫「對照表列出的每個測試名應在 Kotlin 圍欄裡有同名測試函式」，而文件已沒有對照表與圍欄。
3. 影響：`lumos spec-trace` 或讀條款的人會以為這兩支測試仍驗這些，實際已不驗。

## 三問
1. 原問題的修復效果有何行為證據？
   - 判定：舊檔清單判法（G1）、`$` 跳脫（G2）、required 版 ViewModel 測試（G4）、`--scope` 共用檢查（G5）在修前紅、修後綠，上述範圍的證據成立。
   - 修前紅的證據：把修後測試放進修前工作樹，`switch_effects` 紅 1 條，`legacy_modes` 紅 2 條（清單含 `README.md`、`mysrc/test/Q.kt`，缺 androidTest、testFixtures），`scope_and_print` 紅 5 條，`konsist_legacy_shape` 拋例外。
   - `$` 的證據：修前 `listOf("feature/$gen")`，修後 `listOf("feature/\$gen")`。
   - G3 的行為證據只有 macrobench-lab 實跑，不能重現，標未判定；F11 說明文字檢查擋不住它。
2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？
   - 修後 `-k arch_template` 84 passed 0 failed，`-k arch_target_android` 8 passed 0 failed。
   - 相鄰路徑：`.md`／`png`、NFD、cartx、`legacy=all` 都有斷言。
   - 破口：F13（`test` 段正式檔）、F11 的空清單、F12。
3. 新發現同一案例在修前、修後各是什麼結果？
   - F13：修前收、修後不收，見 F13 第 2、3 點。
   - F11、F12：修前沒有對應檢查，修後仍擋不住改壞，證據見各條。
   - F14、F15：兩版文件都有，非修補造成。

## 正向主張證據
- 主張 1（F5 已修）
  - input：`usecase=required` 的產出。
  - expected：擋 `Repository`／`RepositoryImpl`／`DataSource`／`Dao`／`Api`。
  - case_source：`switch_effects` 的新斷言。
  - before：紅。after：綠。
  - comparison：修前不擋後四種，修後擋。
- 主張 2（舊檔清單與架構對齊一致）
  - input：11 支檔的臨時 repo。
  - expected：清單正好 8 支，且「在清單上」等於「命中宣告」。
  - before：清單含 `README.md`、`Q.kt`，缺 `B.kt`、`F.kt`。after：綠。
  - comparison：獨立手寫期望清單，不是從實作推。「⇔」那條斷言對照的 `_arch_target_rule_index` 內部呼叫同一支 `_arch_code_file`，本身重複；期望清單才是獨立判準。
- 主張 3（`--scope` 空白、`./`、`/`、反斜線有拒絕）
  - before：`'  '` 被擋成「少於兩段」，原因不對。after：全部有統一原因。
  - 不判定：測試把五種輸入改成同一句原因後，已不能分辨哪一道檢查生效。

## 圖譜鏡頭固定席判定
- `lumos-cli-read`（search 排除 superseded）：沒碰 search，不破壞。
- `測試假綠形態`（還原翻紅釘要配前置斷言）：新測試多數有前置（`len(tracked) == 11`、預設組 12 條、9 支）。Kotlin 那幾條只比對文字，沒有現場成立證明，即 F11、F12。
- `pitfalls-code-loop`、`guard-kill`、`lumos-cli-lifecycle`：這份 diff 不碰，不破壞。
- `design-loop`（條款綁測試）：被綁的測試名都存在，S10 是 `[manual:]`，不破壞。
- `bound-tests-gate`：最慢的綁定測試 20.8 秒，低於 180 秒上限。
- `arch-alignment-lens`：新增的一條 bullet 與程式一致。
- 未驗範圍：macrobench-lab 實跑、`lumos doctor` 全跑、Kotlin 編譯。

## 時間與清理
- 測試的日期用當天加一年，沒有寫死日期。
- `_arch_tpl_call` 以 try/finally 還原 cwd。
- 本席臨時工作樹與暫存目錄已用字面路徑刪除並 `worktree prune`。

總結:共 5 條，major 1 條（F11），minor 4 條（F12、F13、F14、F15）。
