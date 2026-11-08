severity: major

我只讀了快照,並用 python3.14 載入 check.py 對真型錄做統計。沒有改任何檔,也沒有跑測試。

**1**
severity: major
blocking: 是
標題:「自帶證據的列」免附證據,但只驗檢查 id 有沒有出現在現成規則欄,不驗「擋得到」定義裡的預設開啟與等級。任何新列只要在情境欄抄一句「形狀:由 Android Lint X 判」就能繞過證據表。
失敗場景:
- 輸入:新增一列,現成規則欄寫「內建:SomeDisabledByDefaultCheck」,情境欄寫「形狀:由 Android Lint SomeDisabledByDefaultCheck 判」,通電批次寫「批四(CI 範本:Android Lint)」。
- 預期:這條檢查預設關,按〈用詞〉的「擋得到」定義不該宣稱接電。
- 照計劃實際:這列算自帶證據,證據表不用有筆,id 也對得上,自檢過,宣稱接電成立。
- 原計劃只在 129 列裡找到 12 列有問題(約 9%,其中 3 列是預設關或 Hint),卻沒有掃自帶證據的 39 列。計劃的理由是「壞寫法本身就是用那條檢查定義的」,但這只保證檢查會報,不保證預設開啟或等級夠。
- 我實跑:真型錄 39 列都符合這句寫法,內含 ARCH-81 NewApi、ARCH-84 MissingClass 等。
引句:「這列的壞寫法本身就是用那條檢查定義的。自檢另驗情境欄寫的檢查 id 也出現在現成規則欄。」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:344`(`_batch4_problems` 只看規則欄與批次欄)

**2**
severity: major
blocking: 是
標題:證據表以「型錄列編號」為鍵,不分 Android Lint 與 compose-rules 兩個標籤。兩個標籤都標的列,一筆證據就同時放行兩邊。
失敗場景:
- 真型錄有 21 列同時標了 Lint 與 compose-rules 兩個標籤,例如 UI-10、UI-13、UI-26、UI-54、UI-100。
- 輸入:證據表為這列寫一筆 Android Lint 的證據,compose-rules 那段完全沒有證據。
- 預期:compose-rules 的宣稱缺證據,要被點名。
- 照計劃實際:自檢只比對「這列有沒有一筆」,有一筆就全過。
- 反向也成立:這 21 列若讓情境欄寫上「由 Android Lint X 判」,compose-rules 也免證據。
- 計劃明說 compose-rules 的列全部要附證據,規格卻沒有把證據綁到標籤。
引句:「宣稱接電的列,要不是自帶證據的列、就要在證據表有一筆」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:344`(`B4_TAG_LINT` 與 `B4_TAG_CR` 是分開判的,但計劃的證據比對只看列編號)

**3**
severity: major
blocking: 是
標題:證據格式只驗「網址是 https、日期格式對、壞例與原文欄不空」,「檢查」欄沒有任何比對。證據表的「附證據」可以用佔位字應付,也會在型錄之後被改動時過期而不被發現。
失敗場景一:
- 輸入:新增一列要宣稱接電,證據表寫 `NEW-1  x  x  x  https://a.b  2026-11-09`。
- 預期:被擋。
- 照計劃實際:格式全過。
失敗場景二:
- 輸入:之後有人把這列現成規則欄換成另一條檢查,或改了第 3 欄壞寫法。
- 預期:舊證據作廢。
- 照計劃實際:證據表的「檢查」欄與壞例沒有跟現成規則欄、壞寫法欄比對,舊證據照舊放行。
- 結果:新增列只需要塞一筆符合格式的垃圾,「不附證據就不能宣稱」的合約被拿掉。
- 計劃在〈天花板〉承認驗不了證據對錯,但至少「檢查」欄應出現在該列現成規則欄、網址主機應落在〈依據來源〉列的網域內,這些在無工具下可機驗,計劃沒列。
引句:「每筆的網址要是 https 開頭、日期是 YYYY-MM-DD、壞例與原文欄不空」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:344`(`_batch4_problems` 現況沒有對證據內容的任何比對)

**4**
severity: major
blocking: 是
標題:證據表沒有「預設開啟」與「等級」欄,「擋得到」定義裡的這兩個條件無處留證據,日後新增列也無法機驗。
失敗場景:
- 輸入:新增一列,證據寫了壞例與官方頁原文,但該檢查預設關(或預設等級是 Hint),作者沒發現。
- 預期:被擋,因為〈用詞〉說這種不算擋得到。
- 照計劃實際:證據表欄位只有「型錄列編號、檢查、擋得到的壞例、官方頁或原始碼逐字一句、網址、查證日期」,全部通過,而且還能引用一句官方原文。
- 這正是計劃自己開頭列出的第五、第六種漏法(預設關沒列進清單、Hint 不讓建置失敗),新機制對它們沒有守衛。
引句:「每列一筆:型錄列編號、檢查、擋得到的壞例、官方頁或原始碼逐字一句、網址、查證日期。」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:119`(`B4_DEFAULT_OFF` 只是硬寫的 id 清單,與證據表無關)

**5**
severity: minor
blocking: 否
標題:新的測試與 pre-push 觸發條件沒涵蓋新增的 TSV 檔。
失敗場景:
- 輸入:只改證據表(例如刪掉一筆)就提交。
- 預期:推送前的測試子集會跑 `t_kt_catalog_*`。
- 照計劃實際:計劃寫的觸發條件是「碰到型錄或 check.py 時跑」,TSV 沒被點名。
- 結果:本機閘可能不跑,等 CI 全套才發現。
為什麼標 minor:CI 全套仍會抓到,只是延後。
引句:「推送前的關鍵字子集碰到型錄或 check.py 時跑」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:357`(`catalog_problems` 只讀 `CATALOG` 一個全域)

**6**
severity: minor
blocking: 否
標題:TSV 解析與測試複本的行為沒有規定。
失敗場景:
- 重複列編號:同一編號有兩筆,後一筆蓋掉前一筆,前一筆壞證據被隱藏。
- 欄位內含 Tab 或換行,或欄位數不對。
- S2 的測試要「在型錄複本拿掉證據表的一筆」,但 `catalog_problems` 目前只讀全域 `CATALOG`。若證據表路徑不是由複本旁邊推出,測試要嘛改到真檔、要嘛測不到。
為什麼標 minor:這些是實作細節,測得出來,但計劃沒寫,照字面做的人容易漏。
引句:「證據表的每一筆要對得到一列宣稱接電的列(不能留過期的證據)」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/configs/ast-grep/kotlin-android/check.py:357`

最高等級 major;blocking 4 條
