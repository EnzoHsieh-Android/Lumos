severity: minor

整份 diff 沒有引入第二種做法,也沒有跨層直呼。只有 2 條不一致,都是命名或條款字面的小處,結構都對。

我沒有在 repo 根跑任何會改動的指令,也沒有改任何檔。

## 發現

1. 同一個審查迴圈的輪次,在同一份計劃裡有兩種寫法
severity: minor
blocking: 否
引句:「代碼審 light r1(2026-11-09,1 席):2 條/blocking 1/新測試另起逐行核對」
- 計劃〈審計修正紀錄〉把沒有 `-std` 尾碼的那個迴圈叫「代碼審 light r1」、「代碼審 light r2」。
- 同一份計劃的預期值表「來源」欄叫它「代碼審 r1」。
  - 位置在 `docs/lumos-toolchain-knowledge/Projects/簡報審查抓到的機制缺口_計劃.md:66` 與 `:67`。
- `scripts/test_lumos.py:127247` 的表頭註解也叫「代碼審 r1」。
- 重現:`grep -n "代碼審 r1" <計劃>` 只命中表格的第 66、67 行;`grep -n "代碼審 light r1" <計劃>` 只命中第 85 行的日誌。〈審計修正紀錄〉裡以「代碼審 r1(」開頭的條目是 0 條。
- 鄰居對照:
  - `Projects/測試總檔預設切片_計劃.md:84` 用「代碼審 r1」指沒有尾碼的迴圈。
  - 同檔 `:83` 用「代碼審 std r1」指 `-std` 迴圈。
  - 全 Projects 目錄只有這份新計劃寫「代碼審 light r1」。

2. 收窄既有規則並改了樣本,驗收條款卻沒有綁樣本自測
severity: minor
blocking: 否
引句:「當規則包逐例表掃到 kt-lifecycle-collect-without-repeat 時」
- 這份 diff 動了壞例與好例兩個樣本檔(增 41 行),計劃〈回退〉也列了「兩個樣本檔」。
- 計劃唯一的 `[test:]` 是 `t_kotlin_rulepack_security_rules`(新計劃 `:53`)。
  - 它只驗逐例表。
  - 驗每條規則樣本的是 `t_kotlin_rulepack_samples`(`scripts/test_lumos.py:126728`),計劃一次都沒提到(`grep -c t_kotlin_rulepack_samples <計劃>` 為 0)。
- 鄰居對照:
  - `Projects/Android不接閘資安規則重量_計劃.md:169`:同樣是收窄既有規則,有一條 `[S4] 當跑規則包樣本自測時,收窄形狀的兩條規則 應 報壞例、不報好例 … [test:t_kotlin_rulepack_samples]`。
  - `Projects/Android形狀列補規則_計劃.md:117` 的 `[S1]` 也綁了同一支。
  - 第三批計劃的條款沒有綁這支,所以這是部分鄰居的做法,不是全部。

## 三問

**1. 分層與依賴方向:對齊,已讀,無 finding。**
- 規則例外寫在 `rules/state.yml:176` 起的原規則上。排除結構是 `not: inside: class_declaration` 加 `has: delegation_specifier` 與 regex,`stopBy: end` 掛在 `inside` 底下。
  - 與 `rules/architecture.yml:292-300`(`kt-register-without-unregister` 排除 Application)逐層相同。
  - delegation_specifier 加 regex 的 inline 寫法在規則檔內處處可見(例如 `architecture.yml:18`、`state.yml:50`、`:117`),`utils/` 只放多條規則共用的判斷。
- 規則內的註解夾在 `message`/`ignores` 與 `rule:` 之間,與 `architecture.yml:291` 同位置。
- 前綴清單用明列的 `(androidx\.lifecycle\.|androidx\.media3\.session\.)?`,鄰居有 `perf.yml:244`、`compose.yml:266`;只有 architecture.yml 用寬鬆的 `(\w+\.)*`,兩種都有先例。
- 測試只擴充既有逐例表 `_KTSEC_CASES`,沒有新函式。條款綁既有的 `t_kotlin_rulepack_security_rules`。
- 型錄 STATE-5 名稱欄補括號說明(`skills/kotlin-idioms/checks-catalog.md:253`),跟 `:218` FLOW-7、`:312` CO-31 的括號說明同形。
- 圖譜把新 WHY 附在 `Systems/kotlin規則包.md:71`,接在 `:70` REVISIT 後,與 `:58-70` 的追加方式相同。
- 新計劃的章節順序是 範圍、不做、實務隱患、依據來源、驗收條款、預期值表、回退、天花板、審計修正紀錄,與 `Android形狀列補規則_計劃.md:106-189` 的順序一致。

**2. 命名與錯誤處理:大致對齊,有 2 條不一致(見發現 1、2)。**
- 對齊的部分:
  - 樣本 `// case: <slug>(說明)` 與 `kt-livedata-setvalue-background.kt:9` 同形。
  - 好例樣本用「容易誤報:…」加 `// GOOD`,與 `good/kt-register-without-unregister/…kt:29` 同形。
  - 逐例表編號 C227~C241 連號、依編號排序,第五欄行號與 `:127136` 起的規則同。
  - 表頭註解分開標預期值表逐列和代碼審補的,與 `:127136-127139` 同形。
  - 測試說明的改壞列舉沿用 `:127324` 起的「第 N 批(計劃 S1…)」格式。
  - Issue 的摘要行 `FLAG:TECHNICAL` 加 `PITFALL:… [出處] [根因] [repro]`,與 `Issues/推送前收集第五輪放行的小缺口.md` 同形。
  - 〈症狀〉〈根因〉〈現在怎麼繞〉〈什麼條件算修好〉四節與 `Issues/工作樹防護狀態生效那份不可讀時歸因錯.md` 同。
  - `[manual:]` 條款在 Projects 裡有 118 處,是既有寫法。
- 本題沒有程式的錯誤處理或日誌可比。

**3. 第二種做法:已讀,無 finding。**
- 沒有新機制、新檔案型別、新測試函式、新判定程式。
- 兩份新的 todo 計劃與兩篇 Issue 都用既有節點型別,欄位寫法照鄰居。
- 引用 lumos-gvc 工作樹未提交證據的寫法,`Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md:23` 已有先例。

不對齊共 2 條,其中 major 0 條
