severity: minor

## j1 驗收條款與預期值表的編號順序不是由小到大
severity: minor
blocking: 否
引句:「- [S5] 當跑規則包樣本自測時,kt-lifecycle-collect-without-repeat 應 報壞例、不報好例」
對照:file: `docs/lumos-toolchain-knowledge/Projects/Android形狀列補規則_計劃.md:115-121`
說明:這份計劃的條款順序變成 S1、S5、S4。預期值表也一樣,S5 那列插在 S1 和 S4 中間(「S5 | 好例樣本 SyncService、PlaybackService 的收集…」)。鄰居 Android形狀列補規則_計劃 的條款和預期值表都依編號遞增排(S1 到 S5)。結構(`應` 句式、`[test:]` 綁定、預期值表欄位)都對,只是順序不同,所以判 minor。

## 三問

**1. 分層與依賴方向:對齊。**
- 規則放在 `state.yml`,沿用既有 STATE 類的檔案。例外寫成最外層 `not: inside: class_declaration` 加 `has: delegation_specifier` + `regex` + `stopBy: end`,接在原本的 `any:` 前面。這跟 `architecture.yml` 的 `kt-register-without-unregister` 排除 Application 的形狀一樣,diff 的規則註解也明說照它寫。對照:file: `configs/ast-grep/kotlin-android/rules/architecture.yml:292-300`。
- 規則檔沒有跨層直呼。
- 測試新增的列放進 `_KTSEC_CASES`,由 `t_kotlin_rulepack_security_rules` 的兩個迴圈(寫檔、掃描)消費。對照:file: `scripts/test_lumos.py:127372-127400`。
- 樣本自測由 `t_kotlin_rulepack_samples` 跑,改動沒有繞過這兩支測試。
- 規則本體的 regex 跟鄰居不同:鄰居是通用的 `^(\w+\.)*\w*Application\(`,這裡改成固定的 `androidx.lifecycle.` 和 `androidx.media3.session.` 前綴加三個類名,並允許括號前有 `\s*`。這是刻意的,為了讓非 androidx 的同名 Service(C240)照報,計劃有寫明。這是同一種寫法的調整,不是新做法。

**2. 命名與錯誤處理:大致對齊,只有 j1 一條。**
- 規則 id 沒改,仍是 `kt-lifecycle-collect-without-repeat`,型錄列仍是 STATE-5。
- 逐例列編號 C242、C243 接在 C241 後面,元組格式照舊:`(路徑, 本體, 規則 id, 次數, 行號元組)`。
- 樣本檔路徑沿用 `samples/{bad,good}/<規則 id>/src/main/kotlin/<規則 id>.kt`。
- 樣本內的 `// case: 名稱(說明)` 註解,跟 `kt-livedata-setvalue-background`、`kt-android-viewmodel` 等壞例樣本一致。好例的 `// 容易誤報:` 開頭,跟 `kt-register-without-unregister` 好例的 `// 容易誤報(代碼審 r1 m4):` 一致。
- 條款綁定:S1 綁 `t_kotlin_rulepack_security_rules`,S5 綁 `t_kotlin_rulepack_samples`,跟鄰居計劃(規則包覆核兩級接新增告警閘 S2)用法相同。
- 計劃的節名和順序是 範圍、不做、實務隱患、依據來源、驗收條款、預期值表、回退、天花板、審計修正紀錄。節名和鄰居 Android形狀列補規則_計劃 相同,順序略有不同(鄰居多了 用詞、實驗、量測結果,這份沒有),節名本身一致。
- 審計修正紀錄的輪次標籤統一成「代碼審 r1 (light)」、「代碼審 std r3」這類寫法,條目格式照鄰居的「輪次(日期,席數):條數/blocking 數/摘要」。
- ⚠ 審計紀錄的排列順序:這份計劃是舊的在前、新的在後。鄰居 Android形狀列補規則_計劃(新的在前)和 規則包覆核兩級接新增告警閘_計劃(舊的在前)本身就不一致,專案沒有單一做法可對,交編排者。
- 中文數字「兩席」和阿拉伯數字「2 席」並存,鄰居也兩種都有,不列。

**3. 第二種做法:沒有。**
- 沒有自創輔助函式。測試仍走 `_KTSEC_CASES` 單一逐例表,沒有另寫一套掃描或比對。
- 條款句式、`[test:]` 綁定、`REVISIT`/`RETIRE-IF` 欄位沿用既有。
- 新增的 Issue 兩篇,格式(`FLAG:TECHNICAL`、`PITFALL:… [出處:] [根因:] [repro:]`、症狀/根因/現在怎麼繞/什麼條件算修好)與既有 Issues 一致。tags 沒帶 `priority/*`,但 159 篇 Issues 裡 132 篇也沒帶,所以不算不一致。
- 新增的兩篇 `Projects` 計劃(人工指定高風險路徑、行內忽略註解要留紀錄)的 frontmatter 欄位和 `lands_in`,跟鄰居計劃一致。
- `kotlin規則包` 的 WHY 行用 `[出處:][因:][不選:][test:]`,四欄齊全,跟同節相鄰的 WHY 行一致。

不對齊共 1 條,其中 major 0 條
