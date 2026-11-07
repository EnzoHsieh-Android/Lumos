severity: major

F1 T12 的凍結設定守衛被散文蓋住,把設定檔那行改成 `=true` 測試照綠
引句:「freeze.store.default.allowStoreCreation=false」
引句:「for w in (_KT_T11_API9_SUB, "allowStoreCreation=false", "freeze.store.default.path"):」
severity: major
blocking: 是
- `_kt_instr_template_problems` 只檢查字串有沒有出現在整個 T12 節。
- 這兩個字串在 T12 節的散文裡也各出現一次:`skills/kotlin-idioms/test-templates.md:5876` 含 `allowStoreCreation=false`,`:5889` 含 `freeze.store.default.path`。
- 作者的改壞用 `replace` 全文替換,散文跟程式一起被換,才會紅。
- 翻紅實驗(在 `--shared` 複本、清 `__pycache__` 後跑):
  - 把 `:5929` 的程式行 `freeze.store.default.allowStoreCreation=false` 改成 `=true`,跑 `python3.14 scripts/test_lumos.py -k kotlin_test_templates`,結果 198 passed、0 failed。
  - 整行刪掉:同為 198 passed。
  - 刪掉 `:5928` 的 `freeze.store.default.path=…` 行:同為 198 passed。
- 失敗場景:`archunit.properties` 常駐 `allowStoreCreation=true` 時,清單不見也不會紅,新違規被一起凍結成全綠。驗證紀錄 E5 也記了這個後果:「常駐 true、刪清單、含新違規 → 全綠」。
- 改法:守衛要只在 `properties` 圍欄內比對,而且要比對完整的 `key=value`。

F2 UI-39 的「標準寫法」欄改回舊說法,測試不紅
引句:「`val` 加唯讀集合(`List`/`Map`),變更用 `copy(…)` 產新實例;外部模組型別值相同的新實例常配時才考慮 `@Immutable`/`@Stable` 或穩定設定檔」
severity: minor
blocking: 否
- 計劃說 UI-39 的四欄一起改,`t_kotlin_catalog_instrumented_batch_notes` 只檢查後果、名稱、壞寫法、來源四欄。
- 翻紅實驗:把這句改回舊的「`val` 欄位 + `@Immutable`/`@Stable`,或穩定設定檔」,跑 `-k kotlin_catalog`,結果 60 passed、0 failed。
- 舊說法會叫人對含 var 的類別直接標 `@Immutable`,跟新壞寫法欄的建議相反。

F3 UI-39 的「改壞」對照是空轉
引句:「check("★改壞★ 後果欄改回舊說法時三個字都不在", "強跳過" not in c2 and "===" not in c2, c2)」
severity: minor
blocking: 否
- 這段把後果欄換成舊字串後,只檢查舊字串裡沒有「強跳過」和 `===`。
- 它沒有拿改壞後的資料去跑上面那組 S6 判準,所以什麼改動都不會讓它紅。
- 上面那組判準本身,我改壞後都會紅:UI-39 後果欄、名稱欄、來源網址、〈輸入與口徑〉回寫舊值、STATE-17 改回未接,都有翻紅。

F4 UI-39 後果欄「官方頁沒逐字寫」跟官方頁不符
引句:「就地改的實例沒變,畫面被跳過、不更新(從 `===` 推論,官方頁沒逐字寫)」
severity: minor
blocking: 否
- 我用 WebFetch 打開強跳過頁,頁上逐字寫了「Unstable parameters are compared using instance equality (`===`)」。
- 官方頁有寫 `===`;沒逐字寫的只有「就地改的實例畫面不更新」這個結論。
- 這句標註會誤導讀者以為 `===` 本身是推論,應改成只標結論那一半。

審查結論,沒有立 finding 的部分:
- **改期望的既有測試**:把 T9 換成 T20 的改壞案例,語意等價(指到範本檔沒有的組),沒有拿掉原本該守的行為。T9 現在存在,所以不能再用它當「不存在的組」。
- **允許值那一道**:作者說「改允許的值那一道不會翻紅」,理由站得住。各組列號相等、各未接值的列數相等、範本列數加未接列數等於 68,這三道已涵蓋它。把一列改成 T14 或舊值,別的檢查先紅。
- **型錄與範本對照**:型錄 59 列接上範本的組,每個編號都出現在範本檔對應的組裡。矩陣格數 61 跟驗證紀錄逐組吻合。
- **版本**:BOM 2026.06.01、lifecycle 2.10.0、nav 2.9.8、Hilt 2.58 跟驗證紀錄一致。
- **出處網址**:兩個都打得開。`dagger.dev/hilt/android-entry-point` 的引句逐字吻合,強跳過頁也存在。
- **實跑**:`-k kotlin` 342 passed,跟驗證紀錄 E11 一致。
- **守衛改壞**:T10 拿掉 `runCatching`、在 T10 測試裡加 `InstantTaskExecutorRule`,測試都會紅。
- **覆蓋不全但屬設計取捨**:T10 少 `debugImplementation leakcanary-android`、T9 無障礙拿掉 `setThrowExceptionFor`、T12 的 `hasProperty` 條件改成 `if (true)`,測試都不紅。這幾處靠實驗與驗證紀錄,計劃與作者已明說,沒有另外立條。

總結:最嚴重是 F1(T12 凍結設定守衛被散文蓋住,設定檔改成 `=true` 測試照綠),會擋 1 條。

臨時複本與 `gctl-run-*` 暫存已用字面路徑刪除,repo 未修改。
