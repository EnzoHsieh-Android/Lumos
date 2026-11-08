severity: major

審查對象為 r2-snapshot.md,對照 r1-intake.md 與 android-unwired-sem 的真碼。r1 要折的項目(證據改放型錄內、粒度改成(列,標籤)、取消自帶證據豁免、加等級與預設欄)都有折進快照。下面是折法帶出的新洞。

我用 python3.14 載入 check.py,對真型錄實跑,數字如下:
- 168 個宣稱接電的列,與 `batch4_expected_tags` 算出的候選完全重合(差集 0)。
- 只靠 `_B4_SKIP` 被排除的 Android Lint 段有 11 個。

**1.**
severity: major
blocking: 是
「判定後沒有任何標籤擋得到的列改成只標批一」是錯的:這類列大多本來沒有批一,改過去會變成另一種過度宣稱,而且沒有機械守衛抓得到。
- 場景:UI-49 現況通電批次是 `告警帶寫法=批四(CI 範本:Android Lint)`。判定擋不到之後,依範圍 4 與 S3 改成「只標批一」。
- 預期:這列沒有 ast-grep 規則,應該改成 `未接` 之類,不能寫批一。
- 實際:S3 預期值表列的 18 列裡,只有 API-9 原本就有批一,其餘 17 列(含 UI-49、UI-96、UI-92)會憑空多一個批一。
  - `stats_problems` 的「守到的列數」只數同時提到 `rules/` 規則 id 的列,所以統計數不變,也沒有別的檢查要求批一必須有規則,錯誤會悄悄過關。
  - 這正是計劃想防的「宣稱會擋卻擋不到」,只是從批四換成批一。
- 字面也有第二個問題:「沒有任何標籤擋得到的列」沒限定在「宣稱接電的列」。
  - 型錄裡有 52 列 `批四(現成規則)`,也有批三、未接、`批一(只有提示級規則,預設不接)` 的列。
  - 這些列判定表裡沒有擋得到的標籤,字面上會被一併改成「只標批一」。
引句:「判定後沒有任何標籤擋得到的列,通電批次改成只標批一」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:500`(統計口徑只數提到規則 id 的批一列);實跑 UI-49、UI-95、ARCH-28、DATA-32、PERF-1 等列的通電批次,都只有批四沒有批一。

**2.**
severity: major
blocking: 是
新判定表與既有 `_batch4_problems` 的關係,字面只寫「取代」,沒寫要刪什麼、舊測試怎麼改。照字面做出來會是兩套檢查打架,或舊測試全紅。
- 場景 A(只加新檢查、留舊的):`catalog_problems` 第 376 行仍呼叫 `_batch4_problems`。它只看候選,UI-96 這種「有候選但判擋不到」的列,舊檢查要求「必須寫批四」,新檢查要求「不准寫批四」,同一列無解。
- 場景 B(照「取代」刪掉舊檢查):`t_kt_catalog_batch4_wiring` 會紅。
  - 它直接呼叫 `ck._batch4_problems("內建:WrongThread(相關)", …)`,並要求錯誤訊息列出每個 `_B4_SKIP` 字樣。
  - 它還要求〈輸入與口徑〉「恰好一行」含「而且那一段不含」,且列齊每個排除字。範圍 6 要把〈輸入與口徑〉改寫成「以〈接電證據〉節為準」,範圍 7 又說不改排除字表,兩者會同時讓這支測試紅。
  - 計劃的測試清單只有新增的 `t_kt_catalog_batch4_evidence`,沒有列出這支舊測試。
- 「一字不差」也沒說比對對象。通電批次格子是 `告警帶寫法=批一、批四(…);行為測試或正向約束=範本 T12` 這種複合字串。整格比會讓 168 列全紅,只比批四括號段才對,字面沒講。
- 另一支測試 `_kt_batch2_b4_problems`(`scripts/test_lumos.py:129273` 起)寫死 7 列必須有 `批四(Android Lint)`。DATA-79、DATA-83 的 `SecretInSource` 與 `VulnerableCryptoAlgorithm` 現成規則欄帶「只看…」限定,哪天判成擋不到就會和它衝突。
引句:「通電批次欄寫的要一字不差(取代原本只看候選的比對)」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:344`、`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:376`、`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/scripts/test_lumos.py:129154`。

**3.**
severity: minor
blocking: 否
〈接電證據〉節放在檔裡哪個位置沒指定,放錯位置會讓主表讀法報出一堆假問題。
- 場景:判定表的列首是 `| API-9 |`,符合 `_MAIN_ROW_RE`。`main_rows` 只在「\n## 情境決策表」之前讀主表,而且欄數必須是 12。
  - 若實作者把新節放在〈輸入與口徑〉之後、〈情境決策表〉之前,所有判定列都會被當成主表列,報「欄位數 7,應為 12」與「編號重複」。
  - 放在〈待查證〉之後才安全。計劃只說「照〈待查證〉的做法加一節」,沒釘位置。
- 為什麼標 minor:仿〈待查證〉的做法自然會放後面,而且 S1 一跑就會紅,屬於開發時立刻發現的問題。
引句:「照型錄既有〈待查證〉節的做法,在同一份檔裡加一節、雙向比對」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:656`(`main_rows` 的切點)。

**4.**
severity: minor
blocking: 否
欄位的「固定值」沒列舉,「擋不到」列的等級、預設、出處也沒有合法值。實作者與之後新增列的人得自己發明。
- 場景:Slack 四條檢查在範本裝的 1.4.2 裡不存在,要判擋不到,見〈用詞〉「範本版本沒有這條」。
  - 這種列沒有等級與預設可讀,固定值集合沒有對應的值。
  - 判定表只有 7 欄,沒有「理由」欄。理由只能塞進出處,出處又限定〔查證〕或〔真跑〕格式,逼著硬湊網址。
  - 也沒說 Android Lint 的 Informational、Ignore 算不算 Hint。
- 等級「detekt」沒有綁標籤:規則只寫「等級 Warning/Error/Fatal 或 detekt」才算擋得到。
  - 一筆標籤是 `CI 範本:Android Lint` 的判定,等級寫 detekt 也算擋得到,等於繞過 Hint 與 Warning 的把關。
- 為什麼標 minor:這些欄位本來就是人手填、自檢只驗格式,攻擊面不大。但新增列的人會因此不知道怎麼寫,做出各式各樣的值。
引句:「判定、等級、預設欄只收固定值」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:679`(`_VERIFIED_RE` 只收含網址的查證)。

**5.**
severity: minor
blocking: 否
〔真跑〕只驗樣本檔存在,不驗它對應到這列或這條檢查,證據可以張冠李戴。
- 場景:UI-24 判定擋得到,出處寫〔真跑 2026-11-08:UI-96.kt〕(別列的樣本)。
  - 檔案存在,S4 過關,UI-24 的批四宣稱成立。
- 「一列一支」與「(列,標籤,檢查)為單位」也對不上:UI-2、UI-23 等有 2 到 3 個候選檢查的列,一支樣本無法分別證明各檢查。
- 另外,快照引用的卷證 `sweep/pilot.md` 目前不在 sweep 目錄(只有 p1 到 p7-src);雖標「新增」,但「能離線真跑」這個載重宣稱現在沒有可查的原始紀錄。
- 為什麼標 minor:作者手填的欄位本來就能被假造,這裡是補強;但至少該要求檔名含列編號。
引句:「〔真跑 日期:樣本檔〕且樣本檔存在」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/governance/review-reports/型錄接電要附證據/sweep/`(無 pilot.md)。

**r1 處置檢查**:r1 折入的 G1 到 G6 在快照裡都找得到對應文字。折法帶出的新洞就是上面的第 1 條(「退回」改成只標批一)與第 2 條(「取代」沒落實)。

最高等級 major;blocking 2 條
