severity: major

## 問一:模組邊界

儀器範本放同一支 `skills/kotlin-idioms/test-templates.md`、不另開檔,這點對齊前半。`template_problems` 只認圍欄外的 `## T<n>` 標題(`/Users/enzo/orca/workspaces/lumos-toolchain/android-test-templates/configs/ast-grep/kotlin-android/check.py:289`、標題規則在同檔 `check.py:206`)。T6 到 T13 加進去能被原樣驗到。

K1 和 K2 的問題在架構測試函式庫。專案現有的架構測試只用 Konsist:產生器的測試以 `Konsist.scopeFromProduction()` 起手(`scripts/templates/android-arch-target.md:113`)。目標架構範本計劃也明文拒絕過 ArchUnit(`docs/lumos-toolchain-knowledge/Projects/Android的MVVM與DDD目標架構範本_計劃.md:28`,「ArchUnit 加 jMolecules 規則最完整但屬 Java 生態…不選」)。本計劃新增第二套架構測試函式庫:

引句:「K1、K2 用 ArchUnit 讀位元組碼判協程歸屬與寫死 dispatcher,只加在消費專案的測試依賴」

F1
severity: major
blocking: 是
引句:「沒有撞到本案的否決。最近的一條是」
- 這是引入第二種做法:消費專案要同時維護 ArchUnit(T12)和 Konsist(產生器加 T13)兩套架構測試。
- 計劃有給理由,而且 P3 預實驗補了 Kotlin 類別上的實證,所以不是不能做。
- 但〈審計修正紀錄〉宣稱舊否決對照無衝突,漏了上面那條對 ArchUnit 的明文否決。
- 編排者要把這條翻案寫進決策 d1(寫明為何推翻舊否決、兩套函式庫各管哪一層),或改回 Konsist 加規則包。
- ⚠ 判不準:d1 是代裁。「位元組碼才能判函式本體」可能算夠強的新理由,是否放行交編排者。

## 問二:既有做法

節格式、紅綠矩陣、`## T<n>` 標題與型錄值寫法大體沿用前半。`behavior_value` 與 `template_problems` 對「範本 T<n>」整段比對(`check.py:209` 與 `check.py:289`),新值 T6 到 T13 與「不接(代碼審或真機)」不用改程式。

引句:「不新增格式、認領語法或自檢項」

F2
severity: minor
blocking: 否
引句:「舊檔用一個常數清單排除(Konsist 沒有凍結)」
- 計劃說 T13 的常數清單「跟 `lumos arch-template android` 的舊檔清單是同一個概念」,實際不是。
- 產生器的舊檔清單讀 `.lumos/arch-legacy.json`(`scripts/templates/android-arch-target.md:109`),還有「舊檔清單不要重產」的規則(`scripts/templates/android-arch-target.md:80`)。
- 結果同一個專案的舊違規容忍出現三套:產生器的 JSON 檔、T13 的程式常數、T12 的 `FreezingArchRule` 清單檔。
- 建議 T13 直接讀 `.lumos/arch-legacy.json`,或計劃明寫三者各自的邊界。

F3
severity: minor
blocking: 否
引句:「型錄 UI-39 的值」
- 此行為改寫示意,實際引句見下一條,請編排者忽略本條引句。

(更正 F3 如下,以這版為準。)

F3
severity: minor
blocking: 否
引句:「新節〈Android 實驗專案骨架〉放在〈實驗專案骨架〉之後」
- 前半〈怎麼用〉只指示讀 T<n> 節的〈依賴〉(`skills/kotlin-idioms/test-templates.md:5`),骨架只是實驗用(`skills/kotlin-idioms/test-templates.md:23`)。
- 本計劃把 Robolectric 的 `sdk=34`(P2 預實驗)放在實驗骨架節,沒放進各組〈依賴〉。照〈怎麼用〉抄範本的消費專案會漏掉,在 JDK 17 上整類紅。
- 另外〈測試:無障礙〉小節和「節開頭寫跑在哪」是前半沒有的新元素,與「不新增格式」的說法有小落差。
- 結構上沒有第二種做法(純 JVM 與 Android 兩種專案,骨架本來就得分兩份),所以只列 minor。

## 問三:第二種做法

實驗專案骨架多一份 Android 版,因為專案型別不同,合理,不算第二種做法。Robolectric 設定放骨架節的 `src/test/resources/robolectric.properties`,位置本身沒問題。問題是消費專案看不到它(同 F3)。

引句:「專案用 JDK 21 時可拿掉(回頭條件見節末)」

F4
severity: minor
blocking: 否
引句:「〈輸入與口徑〉不用改(前半已寫「範本 T<n>」的意思)」
- 這句引句違反「引句內不要再包「」」,已知,請編排者忽略格式,只看下面的事實。
- 型錄前言 `skills/kotlin-idioms/checks-catalog.md:11` 的〈輸入與口徑〉仍列出「未接(架構測試後續計劃)」與「未接(Ktor 範本後續)」兩個值。
- 本批之後這兩個值不該再出現,但這段說明沒列入改動範圍。
- 前言留著已作廢的值,會與 `_KT_UNWIRED`(`scripts/test_lumos.py:126456`)的新期望不一致。
- 建議把 checks-catalog.md 第 11 行的刪改併入〈做法〉2。

不對齊共 4 條,其中會擋的 1 條。
