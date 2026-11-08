severity: major

審查範圍是正確性與邊界。我讀了快照,並用 python3.14 載入 `check.py` 對真型錄實跑。證據表和新自檢都還沒實作,所以下面的資料狀態推演靠現有的 `batch4_expected_tags` 與 `_batch4_problems` 實跑。

**1. 退回只標批一的列,「那段補註記」不足以讓那列變成沒接電**

severity: major
blocking: 是

具體失敗場景:範圍 2 對 12 列說「那段補『(相關:…)』註記、退回只標批一」,只寫一段。但 `batch4_expected_tags` 是逐段判,任何一段沒帶排除字就算接電。我拿真型錄的列實跑:

- API-23 現成規則欄是 `內建:UsingHttp、InsecureBaseConfiguration;資安包:DefaultCleartextTraffic`。只在最後一段補「(相關:…)」,結果仍是 `['CI 範本:Android Lint']`。
- TEST-25 是 `Android Lint:AssertionSideEffect、ExpensiveAssertion`。「、」會把兩個 id 切成兩段,「預設關」註記只落在第二段。第二段沒有 `Android Lint:` 前綴,本來就不產生標籤。第一段 AssertionSideEffect 仍判成接電,註記白寫。
- UI-11 有三段,同時掛 Android Lint 和 compose-rules 兩個標籤。一個「相關」只蓋掉一段。

實作者照字面做,有兩種結果:
- 通電批次改成只標批一,現有的 `_batch4_problems` 會報「第四批通電批次要寫批四(…)」,測試紅。
- 或者實作者為了讓測試綠,把批四標籤留著,S3「只標批一」就破功。

為什麼標 major:S3 條款在這 12 列中至少 3 列照字面做不出來。

引句:「判定擋不到的 9 列(API-9、API-23、UI-11、UI-49、UI-95、ARCH-28、DATA-32、PERF-1、PERF-36)與預設關或等級是 Hint 的 3 列(UI-64、UI-80、TEST-25),共 12 列,那段補「(相關:…)」註記」

佐證:file: `configs/ast-grep/kotlin-android/check.py:124`

**2. 混合標籤列(21 列)證據表一列對不出兩個標籤各自的證據**

severity: major
blocking: 是

具體失敗場景:真型錄有 21 列的通電批次是「批四(CI 範本:Android Lint;推送前:detekt 外掛 compose-rules)」,例如 UI-10、UI-11、UI-13。證據表格式是「每列一筆:型錄列編號、檢查、擋得到的壞例…」,一個列編號只有一個「檢查」欄。這 21 列有兩個標籤,卻只有一筆證據,說不出證據對的是哪個標籤。

- 如果 Android Lint 那段有證據、compose-rules 那段其實擋不到,自檢照樣放行,compose-rules 標籤成了無證據的悄悄多宣稱。這正是這份計劃要根除的失敗形狀。
- 反過來,UI-11 要降級時,Android Lint 一半被判擋不到,compose-rules 一半(`cr:compose:vm-forwarding-check`)可能擋得到。計劃把整列「退回只標批一」,把可能有效的 compose-rules 標籤也一併拿掉。
- 計劃對這種列只寫「要在證據表有一筆」,沒定義一筆夠不夠,也沒說依 (列, 標籤) 還是依列。

為什麼標 major:這是宣稱接電的主要資料形狀之一(21 列),規格沒涵蓋,照字面實作會漏掉合約。

引句:「每列一筆,型錄列編號、檢查、擋得到的壞例、官方頁或原始碼逐字一句、網址、查證日期。」

佐證:file: `skills/kotlin-idioms/checks-catalog.md`(UI-10、UI-11、UI-13 的通電批次欄),以及 `configs/ast-grep/kotlin-android/check.py:344`。

**3. 證據表只比對「有沒有這一列」,不比對證據的「檢查」欄是不是現成規則欄登記的那條**

severity: major
blocking: 是

具體失敗場景:範圍 3 的驗證只有:
- 列存在
- 網址是 https 開頭
- 日期格式對
- 壞例欄與原文欄不空

只有自帶證據的列才驗「檢查 id 出現在現成規則欄」。

- 場景:UI-24 的現成規則欄原本是檢查 A,證據表寫的是 A。之後有人把規則欄改成檢查 B(換規則碼),或證據表那筆的「檢查」欄寫錯成別的 id。自檢全綠,證據仍當 A 的證據。
- 因為證據表是型錄現成規則欄的衍生資料,誰是真相沒在規格裡寫明:列編號對上就算數,內容漂移沒人抓。這就是「寫一半」(型錄改了、證據表沒跟)的形狀。
- 另外「壞例」欄也沒跟壞寫法欄(第 3 欄)對。

為什麼標 major:雙向比對只比對 key,證據表防不住它想防的漂移。

引句:「證據表的每一筆要對得到一列宣稱接電的列(不能留過期的證據);每筆的網址要是 https 開頭、日期是 YYYY-MM-DD、壞例與原文欄不空;自帶證據的列,情境欄寫的檢查 id 要出現在現成規則欄。」

佐證:file: `configs/ast-grep/kotlin-android/check.py:344`(`_batch4_problems` 只看規則欄與批次欄,不看證據)。

**4. 「自帶證據」的 39 列整批免證據,跳過預設關和 Hint 的核對**

severity: major
blocking: 是

具體失敗場景:計劃自己承認全表核對找到兩種漏法(預設關、等級是 Hint),並在 129 列做了核對。但 39 列自帶證據的列全部免核,理由只是「壞寫法本身是用那條檢查定義的」。這條理由只回答「擋不擋得到壞例」,不回答「預設開不開、等級是不是 warning 以上」。這 39 列都是 Android Lint 內建或資安包的檢查,例如 ARCH-81 的 NewApi、InlinedApi。

- 我實跑了真型錄:39 列情境欄都寫「形狀:由 Android Lint … 判」。
- 部分列有範圍限定。DATA-79 寫「SecretInSource(只看 GenerativeModel 建構子)」,DATA-83 寫「只看 Cipher.getInstance」。這種列用「自帶證據」豁免,就是計劃自己在 r3 被打穿的那種「只管」註記。
- 檢查 id 的驗證是「出現在現成規則欄」。規格沒說是整詞比對還是子字串比對。子字串比對時,打錯的 id(例如 `Range` 對 `OutOfRange`、少打一個字)也會過。

為什麼標 major:豁免範圍沒做預設關和 Hint 的核對,正是計劃自己找到的兩種漏法。

引句:「自帶證據的列:情境欄寫「形狀:由 Android Lint <檢查 id> 判」的列(2026-11-08 共 39 列,全部是 Android Lint 那種;compose-rules 的列沒有這種寫法,全部要附證據)」

佐證:file: `skills/kotlin-idioms/checks-catalog.md`(ARCH-81、DATA-79、DATA-83 的情境欄)。

**5. 自帶證據的情境欄寫兩個以上 id、或 id 後帶括號時,規格沒定義怎麼解析**

severity: major
blocking: 是

具體失敗場景:真型錄情境欄的寫法有:
- 單個 id:`SetJavaScriptEnabled`
- 用「、」分隔的多個 id:`JavascriptInterface、AddJavascriptInterface`
- 帶括號限定:`SecretInSource(只看 GenerativeModel 建構子)、AuthLeak`

規格只說「情境欄寫的檢查 id 要出現在現成規則欄」,沒說:

- 怎麼從「Android Lint X、Y 判」切出 id 清單。
- 括號內文字算不算 id,切法是否照現成規則欄的 `[;；、]`。
- 多個 id 是全部都要出現,還是一個就夠。
- 「Android Lint」後面是空白而不是「:」,和現成規則欄的 `_B4_LINT` 格式不同,不能直接重用。

不同實作者會做出不同的行為。例如括號裡的「GenerativeModel」被當 id 去比對現成規則欄,會誤報。「全部要出現」和「任一個出現」對 typo 的容忍度也不同。

為什麼標 major:不寫死就會有實作者各自解讀,無法驗證 S1/S2。

引句:「自帶證據的列,情境欄寫的檢查 id 要出現在現成規則欄」

佐證:file: `configs/ast-grep/kotlin-android/check.py:121`(`_B4_LINT` 只認「前綴:」格式)。

**6. 證據表 TSV 的結構邊界沒寫:重複列編號、欄位含 tab 或換行**

severity: minor
blocking: 否

具體失敗場景:證據表是 TSV,證據原文是「逐字一句」官方頁文字,可能含 tab、引號或被硬換行。規格沒說遇到時是報錯還是轉義。

- 列編號重複:規格寫「型錄有證據沒有、證據有型錄沒有都報」,沒寫「同一列兩筆」。實作用 dict 載入時,後筆悄悄蓋掉前筆,留下過期證據而自檢全綠。
- 欄位數不是 6 欄的列:S2 沒列出,列數不對可能整列被當成空欄。
- 同一個 (列, 檢查) 一個標籤一筆還是一筆就夠,也沒說明。

為什麼標 minor:可用一句「重複的列編號與欄位數不是 6 都報」補上,但不補會造成靜默漂移。

引句:「型錄改動:判定擋不到的 9 列」

佐證:file: `configs/ast-grep/kotlin-android/check.py:89`(`catalog_ids` 與 `main_rows` 用同樣方式處理重複列編號,可參考)。

**7. 時間軸:證據日期只驗格式,不管過期**

severity: minor
blocking: 否

具體失敗場景:判定「預設關」「Hint」是 2026-11-08 的快照。Android Lint 新版把預設等級改掉、官方頁改版,或網址 404,證據表仍全綠。計劃已用 `REVISIT:2027-02-08` 覆蓋人工回頭,但自檢不會因時間經過報警。

為什麼標 minor:計劃的〈天花板〉已經承認「驗不了證據本身對不對」,REVISIT 有日期可追,不構成漏掉的合約。

引句:「自檢只驗證據存在、跟型錄一致、格式對,驗不了證據本身對不對」

佐證:file: `configs/ast-grep/kotlin-android/check.py:683`(`catalog_unverified` 有類似的逾期檢查模式可參考)。

**資料狀態五問結論:**
- ① 新舊互讀:第 1、2、5 條。
- ② 寫一半:第 3 條。
- ③ 衍生資料:第 3 條,規格沒寫誰是真相。
- ④ 時間:第 7 條。
- ⑤ 不可逆:無。

最高等級 major;blocking 5 條
