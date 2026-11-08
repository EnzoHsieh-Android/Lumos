severity: major

整體看,這份計劃在規則 id、訊息句式、型錄欄位、節段、驗收條款上都沿用第一到三批的寫法。有兩處跟既有做法不一樣:測試走了另一條路(major),四條新規則沒寫放哪支 yml、沒套路徑排除與訊息檢查(minor)。

## 1. 分層與依賴方向

新規則放 `rules-unwired/`、等級 hint,這跟鄰居一致:`rules-unwired/` 現有 hint、warning、error 三種等級都有。型錄、規則包、測試、圖譜的分層也跟前三批相同。沒有跨層直呼。

severity: minor
blocking: 否
引句:「四條新規則(先放 `rules-unwired/`,等級 hint;訊息照規則包既有句式「[型錄編號]錯在哪;改用 …」)」
計劃沒寫四條規則各放 `rules-unwired/` 的哪支 yml。鄰居一律在 `_KTSEC_PLACE` 寫明「目錄、檔名、型錄編號」三項。
- file: `scripts/test_lumos.py:127060-127086`
- 這一點在 `rules-unwired/` 更要寫明。現有檔只有 api、architecture、coroutines、data、flow、state、testing 七支,沒有 compose.yml;`Systems/kotlin規則包.md:77` 寫著 compose.yml 因移出五條規則而刪掉。
- `kt-disposable-effect-empty-dispose` 屬 Compose 領域,按鄰居分法會落在 compose.yml,計劃沒交代是要重開這支檔,還是放別處。

## 2. 命名與錯誤處理

規則 id 都有 `kt-` 前綴,訊息句式、樣本目錄結構、型錄「自寫 ast-grep <id>」、通電批次「告警帶寫法=未接(規則在 rules-unwired/:…)」都跟鄰居一致。
- file: `skills/kotlin-idioms/checks-catalog.md:534`(ARCH-90 那列)

不對齊的有三條。

severity: minor
blocking: 否
引句:「`kt-disposable-effect-empty-dispose`」
這條規則的命名跟鄰居不同。UI-32 的規則 `kt-compose-dispose-empty-cleanup` 在 `rules/compose.yml:171`,Compose 規則一律帶 `kt-compose-` 前綴。
- file: `configs/ast-grep/kotlin-android/rules/compose.yml:171`
- 計劃的 PRIOR-ART 和範圍都沒提 UI-32 這條既有規則。UI-33 抓的是「空 onDispose 且沒有註冊呼叫」,剛好是 UI-32「有註冊呼叫卻空 onDispose」的補集。
- 計劃應寫明兩條規則的分界,以及同一段 `DisposableEffect` 不會被兩條重複報。

severity: minor
blocking: 否
引句:「同時驗四列型錄現成規則欄的規則 id 在規則包裡存在、在計劃寫的目錄。」
新測試沒有做 S4 那三道檢查,而鄰居測試對每條規則都做。三道是:訊息以 `[編號]` 開頭且不超過 `MSG_MAX`、路徑排除恰為預期項數、目錄與檔名正確。
- file: `scripts/test_lumos.py:127113-127121`
- 鄰居連第三批的 12 項路徑排除都寫進 `_KTSEC_PLACE` 守住。
- 計劃對四條新規則是否套既有八項測試碼排除隻字未提,ARCH-59 和 ARCH-62 在 `src/test` 裡也會報。

severity: minor
blocking: 否
引句:「- [S5] 當讀真型錄與規則包時,API-2、UI-33、ARCH-59、ARCH-62 四列的現成規則欄」
驗收條款的 S 編號排成 S1、S2、S3、S5、S4,鄰居是順序排的。
- file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第三批_計劃.md:100-103`

## 3. 第二種做法

severity: major
blocking: 是
引句:「新增 `t_kotlin_shape_rows_rules`(新增):自己的逐例表,每例寫成一支**完整的 kt 檔**」
⚠ 這條我判得不準,請編排者複核。我判 major 的理由有三:

- **專案的家規指向這是第二種做法。** `Systems/kotlin規則包.md:56` 有一條 WHY 寫「[不選:測試裡另寫一套重數(第二種做法)]」,即判準只許有一份。
  - 新測試另起一份逐例表,再加一份自己的「建 kt 檔、跑 ast-grep、數命中」迴圈。
  - 現有 `t_kotlin_rulepack_security_rules` 的迴圈用的是 `_ktpack_sg()`、`m.CONFIGS`、`m.scan` 這套共用器具。
  - 計劃沒寫新測試會不會重用這套,看起來是平行再建一份。
  - file: `scripts/test_lumos.py:127131-127149`

- **計劃寫的理由只有一半站得住。**
  - 站得住的部分:`_KTSEC_CASES` 的包法寫死在迴圈裡(`package sec` 加 `fun case(...) {` 把片段包起來)。Kotlin 不准在函式內宣告 interface,所以 ARCH-62 的例子放不進去。
  - 站不住的部分:說「改它的包法會牽動既有一百多例」。
    - `_KTSEC_CASES` 有 126 筆,但擴充不必動它們。
    - 鄰居自己有先例:`_KTSEC_PLACE` 的值本來就用 `(d, fname, cat, *extra)` 加選填第四項(`scripts/test_lumos.py:127113`、`127075`),`_KTSEC_IGNORES_DESKTOP` 就是這樣加進去的。
    - 逐例表也可以給四元組加選填第五項,例如 `toplevel=True` 或 `lines=(…)`,既有一百多例原樣不動。
  - 所以理由只撐得住「需要不包函式的路徑」,撐不住「需要整支新測試」。

- **頂層宣告的寫法專案裡已經有。**
  - `samples/bad|good/<id>/src/main/kotlin/*.kt` 全是頂格的完整檔,例如 `samples/bad/kt-room-dao-blocking/src/main/kotlin/kt-room-dao-blocking.kt:2` 的 `interface UserDao`。
  - `t_kotlin_rulepack_samples` 已經能驗 interface 例子,只是它只驗命中數,不驗行號。
  - 計劃要新增的「報在哪幾行」這一項,可以做成在 `_KTSEC_CASES` 迴圈上加選填的行號欄,不必另起一個測試。

## 4. 落點合不合理

`lands_in` 寫 `Systems/kotlin規則包` 合理。第一到三批都寫同一篇,該節點管 `configs/ast-grep/kotlin-android/` 等檔,也有 WHY 行記各批的放置與升級條件。不需要另開一篇。

severity: minor
blocking: 否
引句:「[[Systems/kotlin規則包]] 不接閘目錄那行(現在寫共 25 條)的條數與規則清單」
圖譜的寫回只改了條數那一行,少了鄰居有的那一步。鄰居每批都在該節點的 WHY 行補一筆「哪幾條放哪個目錄、升級條件、樣本外數字」。
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:53`
- 計劃沒說要在這條 WHY 補第四批的放置,也沒說新增一條 WHY 記測試為何獨立。
- 第二個缺口跟第 3 問連在一起:新增獨立測試是個決策,應有一條 `[test:t_kotlin_shape_rows_rules]` 的 WHY 行。

不對齊共 6 條,其中 major 1 條

我沒有在 `/tmp/lumos-seat-work/android形狀列補規則/架構對齊-sonnet/` 建過任何路徑。
