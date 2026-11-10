severity: minor

不對齊的地方都只是命名或位置不一致,沒有結構問題。本機沒有 ast-grep,所以樣本自測和逐例表我沒有實跑,只讀了檔案。

## 三問

**1. 分層與依賴方向:已讀,規則、樣本、測試各放在鄰居的位置,沒有跨層直呼**
- 規則例外的排除寫法照 `kt-register-without-unregister`:`not` 加 `inside` 加 `class_declaration`,再加 `has` 與 `delegation_specifier` 加 regex,`stopBy: end` 掛在 `inside`,`not` 放在 `any` 前面。這是共用寫法,不是第二種。
  - 新規則:`configs/ast-grep/kotlin-android/rules/state.yml:176`(`id: kt-lifecycle-collect-without-repeat`)。
  - 鄰居:`configs/ast-grep/kotlin-android/rules/architecture.yml:293-300`。
- 排除寫法只有這一條規則用,沒有進 `utils/`,跟 Application 那段一樣內嵌。`utils/` 目前只放兩條以上規則共用的判斷(`debug-only.yml`、`has-registration-call.yml`)。
- 逐例表 C227~C233 接在 C226 後面,沿用第五欄行號,`0, ()` 的寫法照 C222;開頭註解與 docstring 的格式也照鄰居。
  - 新增:`scripts/test_lumos.py:127246`(逐例表註解)、`scripts/test_lumos.py:127328`(docstring)。
  - 鄰居:`scripts/test_lumos.py:127240`、`scripts/test_lumos.py:127324`。
- 兩個樣本檔在原檔上追加,好例的「容易誤報:」註解照慣例。
- 圖譜筆記方面:
  - `Systems/kotlin規則包.md` 新增的 WHY 接在摘要最後,跟其他 REVISIT 穿插的追加方式一致。
  - 兩張新 Issue 的標籤、`PITFALL` 格式與章節結構都照鄰居。
  - 另兩張待辦計劃的欄位和 `PRIOR-ART` / `RETIRE-IF` 位置也照鄰居。
- 唯一的偏差是下面的 finding 1 和 finding 2。

**2. 命名與錯誤處理:大致對齊,有兩條不一致(finding 1、2)**
- 規則 id、樣本檔名、`C` 編號、筆記檔名與摘要行前綴都符合鄰居。
- 驗收條款編號從 S1 跳到 S4,有前例(`Projects/後端工程提問與證據擴充_計劃.md` 的 S1 跳到 S3),不列。

**3. 第二種做法:一處待編排者判定(finding 3)**
- 沒有新輔助函式,測試重用既有逐例表和 `check.py` 的讀法,README 中英兩版同步。
- regex 用固定的兩個套件前綴加 `\s*\(`,不像 Application 那段用 `(\w+\.)*`。`rules/perf.yml:28` 已有固定前綴寫法(`^(okhttp3\.)?(Interceptor|Authenticator)$`),所以不是第二種做法,不列。
- 表態記錄寫「改到主程式的設定讀法與訊息顯示」,這份 diff 只動了測試資料和 docstring,沒有動主程式。五題 `na` 的結論對這份 diff 仍成立。

## Findings

### 1. 驗收條款 S1 只綁逐例表測試,字面卻含樣本檔的行為
severity: minor
blocking: 否
引句:「同一支壞例檔裡另有 Service 類別時,Fragment、實作 MediaSessionService.Listener 的 Fragment、ProcessLifecycleOwner 的收集、外圍 Activity 本身的收集 應 照報 [test:t_kotlin_rulepack_security_rules]」

file: `docs/lumos-toolchain-knowledge/Projects/Android形狀列補規則_計劃.md:117-118` 鄰居把樣本自測(S1,綁 `t_kotlin_rulepack_samples`)和逐例表(S2,綁 `t_kotlin_rulepack_security_rules`)拆成兩條。預期值表也有獨立的樣本層一列(`:129`)。

- 新計劃把兩層併成一條,只綁逐例表測試,預期值表也沒有樣本層那一列。
- 「同一支壞例檔裡另有 Service 類別」是 `samples/bad` 檔的內容。`t_kotlin_rulepack_security_rules` 的函式本體對 `samples` 的引用數是 0(`awk 'NR>=127304 && NR<=127420' scripts/test_lumos.py | grep -c samples` 得 0)。
- 逐例表 C227~C233 裡沒有「同檔 Service 加 Fragment」的組合,所以這句話沒有任何綁定測試守著。

### 2. 計劃說「在情境說明補一句」,型錄沒有這個欄,實際改在名稱欄
severity: minor
blocking: 否
引句:「型錄 STATE-5 那列在情境說明補一句」

file: `skills/kotlin-idioms/checks-catalog.md:154` 表頭欄位是「編號 | 名稱 | 壞寫法形狀 | … | 情境怎麼認 | …」,沒有「情境說明」。`grep -c "情境說明" skills/kotlin-idioms/checks-catalog.md` 得 0。

file: `skills/kotlin-idioms/checks-catalog.md:218` 名稱欄放自由文字括號有前例(`一次性事件 vs 狀態(既有表寫…)`)。所以位置本身沒問題,錯的是計劃用了型錄裡不存在的欄名。

- 實際改動在名稱欄,新增「(只管畫面;Service 本來就在背景收,不在範圍內)」,措辭也跟計劃寫的那句不同。
- 接手的人照計劃找欄位會找不到。

### 3. 壞例樣本檔裡放了不會報的 Service 類別
⚠ 交編排者。severity 自降為 minor,因為未能重現「此前沒有任何壞例檔這樣放」。
severity: minor
blocking: 否
引句:「// 同一支檔裡有 Service 類別:例外只看外圍類別,檔裡其他類別照報」

file: `configs/ast-grep/kotlin-android/samples/good/kt-register-without-unregister/src/main/kotlin/kt-register-without-unregister.kt:29-30` 被排除的 `class App : Application()` 放在好例檔,壞例檔沒有。

- 鄰居壞例檔裡的「反向對照」例子(`kt-long-lived-scope-plain-job`、`kt-data-class-mutable-field`、`kt-sql-string-concat`)都是照報的寫法。
- 新壞例檔開頭的 `SyncService : LifecycleService()` 和 `MainActivity` 裡的 `inner class LocalService : LifecycleService()` 都不會報,也沒有 `// BAD`。這是「`samples/bad` 只放會報的寫法」的例外。
- 「只看外圍類別」這件事已有逐例表 C233(Activity 加內部 Service)守著。樣本層重複放一份,而且放在壞例目錄裡。
- 本機沒有 ast-grep(`which sg ast-grep` 無輸出),無法掃全部壞例檔證明沒有別處這樣放。這是否算「第二種做法」,要編排者判定。

不對齊共 3 條,其中 major 0 條
