severity: minor

# 架構對齊審查(code-簡報審查抓到的機制缺口-std r1)

範圍是 `r1-pack.patch`(525 行)。鄰居對照讀的是 `/Users/enzo/orca/workspaces/lumos-toolchain/interview-gaps`(HEAD 3beebb947,等於 pack 範圍終點)。這份 diff 改的是規則例外、兩個樣本、逐例表、型錄一列、README 一句和幾篇筆記,結構上沒有跨層直呼,也沒有第二種做法。我找到 5 條不一致,都是細節層級。

## 1. 計劃〈依據來源〉第 4 列的出處格不符本 repo 的出處規則

severity: minor
blocking: 否
引句:「| lumos-gvc 工作樹 Verification/2026-09-21_戊組知識只在Issue的四題八十場(未提交) |」
file: `skills/lumos-project-notes/SKILL.md:40`(出處格至少要有網址、repo 內存在的反引號檔、存在的節點連結、使用者原話、實測 YYYY-MM-DD:說明,其中一種)
file: `scripts/lumos:14884`(`_plan_source_cell_ok` 就照這五種判)
file: `docs/lumos-toolchain-knowledge/Projects/Android形狀列補規則_計劃.md:91`(鄰居〈依據來源〉每列都有可查出處)

同一張表的第 3 列有補 `[[Projects/Lumos定位_程式碼為主脈絡為輔_計劃]]` 連結,所以合格。第 4 列只有「工作樹 + 未提交」的自由文字,五種都不是。

重現:我在 `/tmp/lumos-seat-work/code-簡報審查抓到的機制缺口-std/架構對齊-sonnet/repo`(HEAD 的 clone)跑下面這行,輸出如下。

```
PYTHONDONTWRITEBYTECODE=1 python3.14 scripts/lumos spec-gate "Projects/簡報審查抓到的機制缺口_計劃"
[spec-gate] 依據來源: ✗ — 1 處不合:
    • 第 48 行:README 實驗句(正確筆記):出處欄沒有讀者查得到的出處(網址、repo 內存在的檔、存在的節點連結、…至少一種)
```

在 clone 的計劃裡替第 4 列補上同一個節點連結後,規格閘印 `依據來源: ✓ 4 列`。這條嚴重度按錨定只能判 minor,但這份計劃是新計劃,這一道會讓規格閘回 1。

## 2. 計劃缺〈審計修正紀錄〉節,鄰居跑過審查的計劃都有

severity: minor
blocking: 否
引句:「從 [[Projects/簡報審查抓到的機制缺口_計劃]] 移出:那份計劃的設計審連兩輪在這一件上被打穿,這裡重新設計。」
file: `skills/lumos-project-notes/reference.md:1018`(審計修正紀錄每輪固定兩行:rN(日期,席數):N 條/blocking N/一句結論,加指向席報告的指標)
file: `docs/lumos-toolchain-knowledge/Projects/Android形狀列補規則_計劃.md:189`
file: `skills/lumos-design-loop/SKILL.md:40`(設計審折入的結果寫進「審計修正紀錄」)

主計劃目前只有〈範圍〉到〈天花板〉,最後一節是 `## 天花板`。計劃正文與 `kotlin規則包.md` 的 WHY 都寫了「設計審 r1、r2」,卻沒有任何一輪的固定兩行。

我數了 2026-11-05 之後建立的計劃,跑過設計審或代碼審的都有這一節,只有這份例外。另外兩份 todo 計劃與 `依實測覆蓋挑測試_計劃.md`(todo)也沒有,但它們沒走完審查。

## 3. 預期值表 S1 的第 4、6 列,在逐例表和樣本裡找不到字面對應

severity: minor
blocking: 否
引句:「| S1 | 壞例檔同時有 Service 類別與 `class SettingsFragment : Fragment()` 的 collect | Fragment 那處照報 | repeatOnLifecycle 官方範例就是 Fragment |」
file: `scripts/test_lumos.py:127100`(鄰居:第三批「預期值表 S1 逐列」)
file: `scripts/test_lumos.py:127320`(鄰居:「C95~C116 是預期值表 S1 逐列、C117~C120 是代碼審 r1 補的」,逐列與補的分開標)

新增的註解寫「預期值表 S1(C227~C233)」,等於聲明這 7 個例子就是 S1 的 7 列。實際對照有兩處對不上。

- **第 4 列**:`SettingsFragment` 在 `configs/ast-grep/kotlin-android/samples/*/kt-lifecycle-collect-without-repeat` 和 `scripts/test_lumos.py` 都 grep 不到。壞例樣本檔裡根本沒有 Service 類別,好例樣本裡有 Service 但沒有 Fragment 的收集。
- **第 6 列**:表上寫「Fragment 裡 `ProcessLifecycleOwner…`」,對應的 C232 輸入是 `class App : Application()`,收集那段是 `ProcessLifecycleOwner.get().lifecycleScope.launch { session.state.collect { show(it) } }`。這一列只有樣本的 `BannerFragment` 對得上。

此外 C228、C229、C230 在 S1 表裡沒有對應列,它們來自代碼審 r1 折入。鄰居會把這種例子標成「代碼審補的」,這裡沒標。

## 4. 計劃條款說可帶兩種套件前綴,逐例表與改壞列舉只守一種

severity: minor
blocking: 否
引句:「regex: '^(androidx\.lifecycle\.|androidx\.media3\.session\.)?(LifecycleService|MediaSessionService|MediaLibraryService)\s*\('」
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:66`(本專案自己的 WHY:自寫規則的逐例測試要逐項拿掉每個正規式選項,每項都要有例子變紅)

計劃〈範圍〉1 寫「可帶 `androidx.lifecycle.` 或 `androidx.media3.session.` 前綴」。新增的 7 個例子裡只有 C228 帶前綴,而且是 media3 那個。`androidx.lifecycle.` 前綴在 C227~C233 與兩個樣本裡出現 0 次,`\s*`(括號前空白)也是 0 次。

docstring 的改壞清單只列「拿掉 androidx.media3.session 前綴 → C228 紅」。拿掉 `androidx\.lifecycle\.|` 或 `\s*` 後,沒有例子會變紅。我用 grep 確認了 0 次出現,但本機沒有 ast-grep,沒能實跑翻紅。

## 5. 壞例樣本檔指向測試表的例子編號

severity: minor
blocking: 否
引句:「// 例外只看類別自己的繼承清單(Activity 裡有內部 Service 的情況見逐例表 C233)」
file: `configs/ast-grep/kotlin-android/samples/bad/kt-register-without-unregister/src/main/kotlin/kt-register-without-unregister.kt:19`(鄰居壞例註解只寫形狀說明和來源規則 id)
file: `configs/ast-grep/kotlin-android/rules/api.yml:246`(設定層引用計劃節點 `[[Projects/…]]`,不引用測試編號)

我 grep 了 `samples` 底下所有 `.kt`,提到逐例表編號的只有這一行。樣本(設定層)指向測試表(測試層),C 編號又會隨表重排而變。鄰居引用的是計劃節點或審查輪次(例如 `samples/good/kt-register-without-unregister/...kt:29` 的「代碼審 r1 m4」)。

## 三問

**1. 分層與依賴方向:對齊,僅第 5 條例外。**
- 規則例外放在原規則的 `rules/state.yml`,結構照 `rules/architecture.yml:293-300`:最外層 `not: inside: class_declaration`,加 `has: delegation_specifier` 與 regex,再加 `stopBy: end`。
- 好例放被排除的 Service,壞例只放仍會報的三種寫法(Listener 介面、ProcessLifecycleOwner、Activity),符合 `samples/good/kt-register-without-unregister/...:29` 的做法。
- 逐例表接在 C226 之後,沿用第五欄預期行號;不在 `_KTSEC_PLACE` 的既有規則有先例(`kt-http-logging-body-unguarded`、`kt-prod-reads-system-clock`、`kt-room-destructive-migration`、`kt-compose-dispose-empty-cleanup`)。
- 型錄只改 STATE-5 名稱欄,括號補範圍有先例(`skills/kotlin-idioms/checks-catalog.md:312`,CO-31 寫「(目標含 JS 或 Wasm 時)」)。
- 圖譜筆記落在 `Systems/kotlin規則包`,與計劃的 `lands_in` 一致。
- 唯一例外是第 5 條的樣本指向測試表。

**2. 命名與錯誤處理:大致對齊,有第 1~4 條。**
- 沒有新函式,所以沒有錯誤回傳問題。
- 逐例表檔名 C227~C233 續號,註解表頭寫法同 `scripts/test_lumos.py:127136`,docstring 的翻紅釘獨立成一段。
- Issue 筆記是 `FLAG:TECHNICAL` + `PITFALL:` + `[出處][根因][repro]`,與 `Issues/detekt逗號佔位符代碼審放行的小問題.md` 相同。
- 計劃條款編號 S1、S4 跳號有先例(`Projects/改檔前推播失敗出聲_計劃.md` 的 S1、S3…)。
- Issue 沒有 REVISIT 行也是常態(93 篇 open Issue 裡只有 14 篇有)。
- 不對齊處見第 1~4 條。

**3. 第二種做法:已讀,無 finding。**
- 規則、樣本、測試、型錄、筆記各自沿用既有做法。
- regex 的可選套件前綴有先例(`rules/perf.yml:28`、`rules/compose.yml:266`)。
- 把設計審打穿的項目移出另開計劃,有先例(`Projects/依實測覆蓋挑測試_計劃.md` 的「開審前必須先解(…帶過來)」)。
- 附帶一點:表態記錄寫的是 `EnzoHsieh-Android/lumos-frontier-research-survey` 分支、版本 cbafb2f9,並說改到「規則包自我檢查、主程式的設定讀法與訊息顯示」。這份 pack 的 Python 改動只有 `scripts/test_lumos.py` 的 15 行(資料表加例子和 docstring),沒有 `scripts/lumos` 或 `check.py`。這份表態記錄與這份 pack 的內容對不上,5 題「不適用」的宣稱對這份 diff 空洞成立。

我留了暫存目錄 `/tmp/lumos-seat-work/code-簡報審查抓到的機制缺口-std/架構對齊-sonnet/`(clone 與 `newcases.txt`),收貨後請編排者刪。

不對齊共 5 條,其中 major 0 條
