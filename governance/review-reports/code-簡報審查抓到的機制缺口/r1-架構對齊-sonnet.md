severity: major

整體判斷:規則本身的寫法(`not: inside: class_declaration` 加 `has: delegation_specifier` 加 `stopBy: end`)跟 `architecture.yml` 對得上。不一致集中在新測試的做法,另有一處計劃與測試的綁定。

## 1. 新測試自己做了一套逐行核對,沒用專案既有的逐例表與規則讀法
severity: major
blocking: 是
引句:「want = {i + 1 for i, ln in enumerate(bad.read_text(encoding="utf-8").splitlines()) if "// BAD" in ln}」
file: `scripts/test_lumos.py:127338` 逐例表 `_KTSEC_CASES` 的宣告是「預期值寫死在 _KTSEC_CASES,不拿規則自己算」。
file: `scripts/test_lumos.py:127176` 逐例表有選填第五欄「預期報在哪幾行」,那一欄的設計就是為了逐行核對。
file: `scripts/test_lumos.py:127370` 讀規則只有 `check.py` 的 `load_rules` 一套(代碼審 r1 架構對齊 F1 定的)。
file: `docs/lumos-toolchain-knowledge/Projects/Android形狀列補規則_計劃.md:118` 逐行條款 S2 綁在逐例表那支測試上。
file: `configs/ast-grep/kotlin-android/samples/bad/kt-long-lived-scope-plain-job/src/main/kotlin/kt-long-lived-scope-plain-job.kt:22` 這條註解寫「照樣報」,但下面那行沒有 `// BAD`。既有壞例樣本裡,`// BAD` 只是人看的記號,沒有被機器當預期值。

新測試同時帶進三個專案原本沒有的手法:
- **預期行號來源**:它從壞例檔的 `// BAD` 記號算預期行,沒有放進逐例表。
- **直讀規則檔**:它直接讀 `rules/state.yml` 的原文做子字串比對(`test_lumos.py:126890`),沒走 `load_rules`。
- **測試內改壞規則本體**:它用 `_ktpack_edit` 對規則檔逐字替換(`:126905`、`:126910`)。既有測試改壞的是型錄(`:127477`、`:128237`)、樣本目錄或假規則檔。規則本體的改壞列舉(翻紅釘)原本是寫在 docstring、證據放卷證,不寫成測試程式。

重現(基準版是 `45f294c4b`,以下是我跑的輸出):
```
git show 45f294c4b:scripts/test_lumos.py | grep -c '// BAD'          → 0
git show 45f294c4b:scripts/test_lumos.py | grep -n '_ktpack_edit('   → 126661(定義)、127477 與 128237(都是 CATALOG)
grep -n '"state.yml"' scripts/test_lumos.py                           → 126890、126905、126910(全在新測試)
```
再補一點:同一天、同一包的規則修補(`26e557413`)只改了規則與樣本,沒加測試函式。所以「修舊規則要不要加專屬測試」專案沒有統一做法。⚠ 這一點交編排者判。但「要逐行核對時用什麼」專案有明確做法,就是逐例表,新測試沒有用。

## 2. 計劃的驗收條款 S1 綁到沒有逐行核對的那支測試
severity: minor
blocking: 否
引句:「外圍 Activity 本身的收集 應 照報 [test:t_kotlin_rulepack_samples]」
file: `docs/lumos-toolchain-knowledge/Projects/簡報審查抓到的機制缺口_計劃.md:52` S1 只綁 `t_kotlin_rulepack_samples`。
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:71` 同一件事的 WHY 綁的是 `t_kotlin_rulepack_lifecycle_service_scope`。
file: `docs/lumos-toolchain-knowledge/Projects/Android形狀列補規則_計劃.md:117` 鄰居計劃把「樣本自測」條款(S1)綁通用樣本測試、把逐行條款(S2)綁逐行那支。

S1 後半「Fragment、巢狀介面、ProcessLifecycleOwner、外圍 Activity 照報」只有新測試核對得到。通用樣本測試只驗壞例至少 2 處、好例 0 處。新測試只出現在 `Systems/kotlin規則包.md:71`,計劃裡沒有任何一條綁它。

重現:`grep -rln "t_kotlin_rulepack_lifecycle_service_scope" docs/lumos-toolchain-knowledge/` 只列出 `Systems/kotlin規則包.md`。

## 三問

**1. 分層與依賴方向:**
- 規則在規則設定層(`rules/state.yml`),樣本在 `samples/bad|good/<id>/src/main/kotlin/<id>.kt`,測試放在 `t_kotlin_rulepack_*` 那一區,型錄改在原列,脈絡寫進 `Systems/kotlin規則包`(`lands_in` 也指它)。這些位置都跟鄰居一樣。
- 測試用 `_ktpack`、`_ktpack_sg`、`_ktpack_edit`、`m.scan`,沒有自寫已有的輔助函式。
- 唯一的跨層直讀是測試直接讀規則檔原文,繞過 `load_rules`,見 finding 1。

**2. 命名與錯誤處理:**
- 規則 id 沿用,樣本檔名是 id.kt,測試名 `t_kotlin_rulepack_lifecycle_service_scope` 照 `t_kotlin_rulepack_*` 命名,`check(...)` 標籤用「S1 …」與「★改壞★」,docstring 有「翻紅釘」。
- 掃描失敗回 `None`,沒有 ast-grep 時先跑靜態那半再印提示,都跟 `_ktpack_sg` 與鄰居一致。
- 圖譜筆記方面:Issue 與計劃的開頭欄位、`PITFALL:`、`WHY:` 摘要行前綴、計劃的 `PRIOR-ART` / `RETIRE-IF` / 實務隱患 / 依據來源 / 預期值表,都跟鄰居相同。
- 型錄 STATE-5 名稱欄加括號說明,這個做法已有先例(CO-31、DATA-95)。
- 規則 regex 用「明列兩個套件前綴」的寫法,`perf.yml:28` 也是這樣寫,不算第二種。

**3. 第二種做法:** 有一處,見 finding 1。README 中英兩版同步,repo 內沒有第三處舊句。

不對齊共 2 條,其中 major 1 條
