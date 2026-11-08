severity: minor

整份 diff 的結構跟專案現有做法一致,只有一條 minor。我查過鄰居檔、型錄同欄位的既有寫法和 git 歷史,沒找到第二種做法或跨層直呼。

**第 1 問 分層與依賴方向:對齊**
- 規則是從 `rules-unwired/` 刪掉、或原地改寫。`api.yml`、`architecture.yml`、`coroutines.yml`、`flow.yml`、`state.yml`、`testing.yml` 都沒換檔案位置或結構。
- 刪掉 `rules-unwired/compose.yml` 沒有懸空引用。該檔只剩一條規則,而 `rules/compose.yml` 仍在,`rules-unwired/` 沒有硬性要求每個主題都有檔。
- 對應的 `samples/{bad,good}/<規則id>/` 目錄整個刪除,跟規則一起走。
- 測試改動留在既有的 `t_kotlin_rulepack_unwired_dir`、`_KTSEC_CASES`、`_KT_STATS_LINES` 裡。新增的 C124 到 C126 接在 C123 之後,沿用 `_KTSEC_CASES` 的編號序。
- 型錄只改列內欄位,圖譜只動計劃、規則包節點和逐列查證計劃,沒有跨層。

**第 2 問 命名與錯誤處理:大致對齊,一條 minor**
- 規則訊息仍是 `[主題-編號]一句原因;改用 …` 的句式,跟 `rules-unwired/state.yml`、`rules-unwired/testing.yml`、`rules-unwired/coroutines.yml` 一致。
- 好例檔裡新增的「容易誤報:」註解沿用鄰居寫法,例如被刪的 `kt-async-await-immediately` 好例。
- 型錄的「告警帶寫法=未接(還沒有規則)」本來就有,新增三列沿用。「原記:」在型錄約 21 列既有,新增列沿用。
- `decisions` 的 `valid: false` 加 `superseded_by` 加 `ended` 的鏈,跟 `Projects/指令索引與情境測試_計劃.md:17-18`、`Projects/席位人格化_計劃.md:17-18` 的欄位一致。`superseded_by` 值寫成 `"[[Projects/…]]#d2"`,全圖譜只有約 5 筆這樣寫,沒有單一主流,不判不一致。

severity: minor
blocking: 否
新計劃的 tags 缺 `risk/守衛面`,第二批、第三批和第一批「資安與崩潰靜態檢查補齊」計劃都有。但 `Projects/Android*` 約 25 篇裡只有這三篇帶,不算普遍慣例,所以只列 minor。這份計劃動的就是規則包守衛,補上比較對稱。
引句:「- scope/stack-knowledge」
file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:9`

**第 3 問 第二種做法:沒有**
- 沒有新機制、新工具函式或新欄位寫法。`kt-prod-reads-system-clock` 的收窄是在同一條規則裡改樣式清單。
- 測試的 `gone` tuple 和 `by_id` 是同檔 `three` 的同形改寫。
- 「收窄形狀」是用同一套 `any:` 樣式加好例「容易誤報:」註解,沒有另立機制。
- 計劃的 PRIOR-ART 和 RETIRE-IF 兩行格式跟鄰居計劃一致。

**⚠ 交編排者的點**
- 整條規則移出規則包是第一次發生,但 `3295519b1` 是這條線上第一個刪規則檔的提交,所以沒有既有做法可對。我只確認後續守衛(⑨、型錄「還沒有規則」)都有接上,沒有另一套說法。

不對齊共 1 條,其中 major 0 條

我在 `/tmp/lumos-seat-work/code-android不接閘資安規則重量/架構對齊-sonnet/` 底下沒建過任何路徑。
