severity: minor

**1. 分層與依賴方向:對齊。**
- 改動落點跟第二、三批一樣:
  - 規則、樣本放在 `configs/ast-grep/kotlin-android/rules-unwired/` 與 `samples/`。
  - 型錄放在 `skills/kotlin-idioms/checks-catalog.md`。
  - 測試放在 `scripts/test_lumos.py::t_kotlin_rulepack_unwired_dir`。
  - 圖譜放在 `Systems/kotlin規則包` 與各計劃。
- 沒有跨層直呼,也沒有新增的程式檔。
- `compose.yml` 只剩一條規則,整支刪掉,跟「每條規則一個家」的作法一致。
- 計劃的 `lands_in: Systems/kotlin規則包` 與第二批計劃同型。
- r2 的 a6(建議拆兩篇計劃)已放行。理由是第二批計劃有新規則與重量同篇的先例,這份快照也寫了。

**2. 命名與錯誤處理:大致對齊,有兩處小不一致。**
- 對齊的部分:
  - 樣本註解(a1):新加的好例用「容易誤報:」,跟既有 138 處一致,例如 `samples/good/kt-async-await-immediately/.../kt-async-await-immediately.kt`。
  - API-36、UI-103 的通電批次(a2):寫「告警帶寫法=未接(還沒有規則)」,屬型錄既有三種寫法之一,見 `skills/kotlin-idioms/checks-catalog.md:430`。
  - 規則訊息:維持 `'[編號]…;改…'` 的句式。
  - 型錄〔查證 2026-11-08:網址〕:格式跟鄰居列一樣。
  - 通電批次:七列新寫的是「規則在 rules-unwired/:還沒在真專案量過誤報」,仍是既有的「規則在 rules-unwired/:原因」句型。`Systems/kotlin規則包.md:52` 的 WHY 已有同樣說法,所以我不列為不對齊。
  - 逐列查證計劃那條 REVISIT(a3):已加 `[closed:2026-11-08 …]`,跟第二批計劃的 closed 寫法一致,見 `Projects/Android資安靜態檢查補齊第二批_計劃.md` 同日改動。
  - 新增 WHY(a5):`Systems/kotlin規則包.md:62` 有 `[出處:][因:][不選:][test:]`,跟鄰居 WHY 同形。
- 不對齊的一處是決策翻案的指向。逐列查證計劃的 d1 被改成指向本計劃 `#d1`(`Projects/Android寫法型錄逐列查證_計劃.md:21`),但本計劃 d1 已經被 d2 取代。其他計劃的 `superseded_by` 都指到仍有效的接班決策,例如 `Projects/席位人格化_計劃.md:17`。讀者要跳兩層才到現行決策。

severity: minor
blocking: 否
引句:「superseded_by: "[[Projects/Android不接閘資安規則重量_計劃]]#d2"」

**3. 第二種做法:沒有。**
- 查證流程沿用型錄既有的〔查證〕加(出處不全)機制。
- 量測沿用第一、二、三批的升級條件與判法。
- 測試仍在既有的 `t_kotlin_rulepack_unwired_dir`,第 ⑥ 道改成允許空集合,偵測能力交給第 ⑩ 道的假規則。這是改寫既有檢查,沒有新增平行機制。
- 新增的補充實驗(v2 判準、敏感度腳本)放在卷證 `experiment/`,第三批也是這樣放。
- 型錄這次也沒有發明新的欄位。

**4. 落點合不合理:大致合理,有一句過期。**
- 已寫進去的:
  - 不接閘目錄改成 26 條,見 `Systems/kotlin規則包.md:77`。
  - 逐列查證那條 WHY 補了更正,見 `Systems/kotlin規則包.md:51`。
  - 新增「查不到就移出規則包」的 WHY,見 `Systems/kotlin規則包.md:62`。
  - 型錄〈統計〉(28、525)與 `_KT_STATS_LINES` 的寫死值已同步。
  - 逐列查證計劃的 d1 與回頭條件已處理。
  - 第二、三批計劃的補註與 status 已更新。
- 還留著的過期句子在 `Systems/kotlin規則包.md:77`:仍以現在式寫「引用型錄出處不全列的規則(先從 `rules-hints/` 拆來 8 條……再從 `rules/` 搬 2 條……範本預設會擋的那份因此少 2 條)」。實際上現在沒有任何規則掛在出處不全的列上。a4 要補的是第 51、76 行(新增 WHY 後行號後移成 51、77)。第 51 行補了,這一句沒跟著改成歷史註記或刪掉。

severity: minor
blocking: 否
引句:「[[Systems/kotlin規則包]] 補一條 WHY(出處不全的規則先查、查不到就移出規則包,不再停放),不接閘目錄那行改成 26 條」

不對齊共 2 條,其中 major 0 條

審材外查證:
- file: `skills/kotlin-idioms/checks-catalog.md:11`
- file: `skills/kotlin-idioms/checks-catalog.md:13`
- file: `skills/kotlin-idioms/checks-catalog.md:430`
- file: `skills/kotlin-idioms/checks-catalog.md:676`
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:77`

我沒有在 /tmp/lumos-seat-work/android不接閘資安規則重量/架構對齊三-sonnet/ 底下建任何東西。
