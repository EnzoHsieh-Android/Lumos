severity: major

審查範圍:凍結快照 r2-snapshot.md,對照 `check.py` 與 `checks-catalog.md` 真跑。我用 python3.14 載入 `main_rows()` 和 `batch4_expected_tags` 逐列算過。

**1.**
severity: major
blocking: 是
「候選」和「一列就夠」兩條規則互相矛盾,照哪條實作都會錯。
- 〈用詞〉把候選定義成(標籤,規則碼)。但範圍 1 說同一(列,標籤)判成擋得到的寫一列就夠,範圍 3 又寫「每個候選(列,標籤)要有判定」。
- 真跑 168 個宣稱接電的列,有 32 列在同一標籤下有多個候選,例如 UI-2 有 3 個(CoroutineCreationDuringComposition、FlowOperatorInvokedInComposition、LaunchDuringComposition),API-23 有 2 個。
- 若按(標籤,規則碼)為單位:UI-2 只寫那筆擋得到的,其餘兩個候選沒有判定,自檢報「要補判定」,和「一列就夠」打架。
- 若按(列,標籤)為單位:全部擋不到的情形,UI-2 只寫一筆「擋不到」就過關。另外兩個候選從未被判,其中可能有擋得到的。這個標籤就被悄悄丟掉。「全部擋不到才要每個候選各一列」在範圍 3 的檢查清單裡沒有對應的機械檢查。
- 你問的「擋得到那條被移出現成規則欄」:自檢會先報「判定的檢查不是候選」。作者刪掉那筆後,剩下的候選在(列,標籤)粒度下只要補一筆「擋不到」就綠。第三個候選仍未被判。
- 此外「要補判定」訊息只指名列與標籤,不指名檢查,作者也不知道要補哪一個。

引句:「同一(列,標籤)有多個候選檢查時,判成擋得到的寫一列就夠,全部擋不到才要每個候選各一列」

佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:124`(`batch4_expected_tags` 候選是 lint/cr 各自的規則碼集合)

**2.**
severity: major
blocking: 是
範圍 4 與 S3 要把「判定後沒有擋得到的列」改成「只標批一」,但這些列大多根本沒有批一。
- 批一的意思是「型錄自己的 ast-grep 規則包已上線會擋」。S3 點名的 18 列,我逐列讀了通電批次欄,只有 API-9 現在有批一。
- 其餘 17 列(API-23、UI-11、UI-49、UI-95、ARCH-28、DATA-32、PERF-1、PERF-36、UI-64、UI-80、TEST-25、UI-96、UI-92、UI-43 到 UI-46)現在都只寫「批四(…)」,沒有規則包。照字面把它們改成「批一」,就是對這 17 列宣稱「會擋的規則已上線」,而它們什麼規則都沒有。
- 型錄現有的正確寫法是「批四(現成規則)」(55 列)、「未接(還沒有規則)」(19 列)。計劃沒有說擋不到的列要不要走這兩個值。
- 這正好製造出本計劃要消滅的那種「宣稱會擋、其實擋不到」。`_guarded_rows` 靠規則 id 比對,所以統計不一定跟著錯,但型錄欄位本身就錯了。

引句:「判定後沒有任何標籤擋得到的列,通電批次改成只標批一」

佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:499`(批一的判定要求提到 `rules/` 底下的規則 id);`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/skills/kotlin-idioms/checks-catalog.md:11`(批一定義為「會擋的規則已上線」)

**3.**
severity: major
blocking: 否
計劃承諾「判定表記讀取的版本」,但表的欄位裡沒有版本欄,版本漂移沒有任何東西會偵測。
- 實務隱患寫「判定表記讀取的版本,回頭條件綁版本」。範圍 1 的欄位只有「列 | 標籤 | 檢查 | 判定 | 等級 | 預設 | 出處」。r1 的 G3 原本加了「套件版本欄」,這一版被拿掉了。
- 失敗場景:linter 範本把 Slack compose-lints 從 1.4.2 升到 1.6.0。過去判「範本版本沒有這條」而擋不到的 Slack 列,實際已經擋得到。表裡沒記版本,自檢維持綠,判定仍是舊的。
- 兩條 REVISIT 都綁日期(2027-05-08、2027-02-08),不是綁版本事件,也沒有自檢能比對版本。
- 同樣的問題也出現在〔真跑〕出處:樣本檔與 lint 版本、範本版本都沒綁。

引句:「判定表記讀取的版本,回頭條件綁版本(見文末)」

佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/skills/kotlin-idioms/checks-catalog.md:849`(〈統計〉節之前沒有版本記錄的位置)

**4.**
severity: minor
blocking: 否
自檢拿「判定」比對通電批次欄的方式沒有定義,新舊寫法容易讀錯。
- 通電批次欄裡「批四(…)」夾在「告警帶寫法=…;行為測試或正向約束=…」的子段中,標籤順序也有兩種:「批四(CI 範本:Android Lint)」和「批四(CI 範本:Android Lint;推送前:detekt 外掛 compose-rules)」。
- 同欄還有「批四(現成規則)」(55 列)、「批一(只有提示級規則,預設不接)」(32 列)、「批一、批四(…)」。
- 計劃只說「一字不差」,沒說:拿哪一段比、標籤順序固定成誰先、遇到上述舊值怎麼處理。
- 現行 `_batch4_problems` 用子字串「批四(A;B)」加 `have` 判定。新規則要換掉它,卻沒寫新語意。實作者可能選「整格相等」,那所有帶「;行為測試…」的列都報錯。
- 為什麼標 minor:現有測試和現有碼提供了線索,實作者多半能推出,不屬於合約遺漏。

引句:「通電批次欄寫的要一字不差(取代原本只看候選的比對)」

佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:344`

**5.**
severity: minor
blocking: 否
〔真跑 日期:樣本檔〕的樣本檔路徑相對誰、驗什麼,計劃沒有寫清楚。
- 範圍 3 只要求「樣本檔存在」。目錄是 `samples/lint-wiring/`,檔名「帶列編號」,但出處欄寫 `UI-24.kt` 還是整條路徑沒有規定。
- 實作者可能解析成相對 repo 根目錄,或相對型錄檔。不論哪一種,自檢不驗這支樣本檔是不是這一列的(列編號沒對上也過)。
- 一列多個檢查或多個標籤時,「一列一支」的樣本檔證不了每筆判定。
- 路徑含 `../` 的樣本檔也會因「存在」而通過。
- 等級 `detekt` 與標籤的搭配(等級 `detekt` 只該配「推送前」標籤)在範圍 3 的「只收固定值」裡也沒檢查。
- 為什麼標 minor:這些都是可以用慣例補的格式空缺,並非漏掉主要合約。

引句:「出處用型錄既有的〔查證 日期:網址〕或〔真跑 日期:樣本檔〕寫法」

佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:679`(`_VERIFIED_RE` 只管〔查證〕)

**資料狀態五問摘要**
- ①新舊互讀:同一規則碼在兩段出現,目前只有 UI-37 的 ComposeUnstableCollections,而且它是預設關,不成為候選。所以(列,標籤,檢查)粒度目前還沒踩雷,但「一段註記、另一段不註記」的情形沒有規則。同一段兩個規則碼出現在多列,屬於發現 1。
- ②寫一半:只改主表或只改判定表,都會被「要補判定」或「檢查不是候選」報出。這點成立。
- ③衍生資料:主表是候選的唯一來源,判定對不到候選時報判定錯。方向合理,缺的只是發現 1 的粒度。
- ④時間:發現 3。
- ⑤不可逆:無。

最高等級 major;blocking 2 條
