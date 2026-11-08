severity: major

審查範圍:對照 repo `/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint-2`。我沒有 ast-grep,規則沒有實跑,下面是讀初稿規則與 check.py 推出來的。

我跑不到的檢查:`python3.14 scripts/test_lumos.py -k` 沒有跑,因為改動還沒有實作。我只靠讀 `t_kotlin_rulepack_*` 與 `t_kt_catalog_*` 判斷會不會被弄紅。

## Finding 1:S1 的 Zip Slip 預期值照字面跑,初稿規則不會報,不報那列也是空測
severity: major
blocking: 是

引句:「`File(destDir, entry.name)` 同函式沒有 canonicalPath 檢查」

- 初稿 `kt-zip-slip` 要求建構子「在名稱符合 Zip(InputStream|File|Entry)、nextEntry 等字樣的函式裡」才會報:`governance/review-reports/android資安靜態檢查補齊第二批/experiment/draft-rules.yml.txt:16`、`:22`。
- 既有逐例測試是把片段塞進一支通用的 `fun case(webView, settings, ...)`:`scripts/test_lumos.py:126903` 附近。那支函式裡沒有任何 Zip 字樣。
- 後果有兩個:
  - 照預期值表的字面輸入,「報」那列拿到 0 次命中,條款 S1 紅。
  - 「之後比對 canonicalPath.startsWith」那列的「不報」,因為完全沒進 zip-fn 而恆真,沒有檢驗到 canonicalPath 排除那一支。
- 接手的人要自己發明外層 ZipInputStream 包裝,規格沒寫。預期值表應該把輸入寫成含 `ZipInputStream` 和 `nextEntry` 的完整函式。

## Finding 2:DATA-95 登記的內建檢查,在範本寫的 AGP 8.5.1 下根本沒有
severity: major
blocking: 是

引句:「都是 Android Open Source Project 提供、Warning、預設開,範本 `warningsAsErrors` 下接 CI 就擋」

- `UnsanitizedFilenameFromContentProvider` 的檢查頁(https://googlesamples.github.io/android-custom-lint-rules/checks/UnsanitizedFilenameFromContentProvider.md.html)寫 `Since: 8.8.0 (January 2025)`。
- 同頁對照:`SdCardPath` 是 Initial、`SetWorldWritable` 是 1.5.0、`UnsafeDynamicallyLoadedCode` 是 2.0.0,都沒問題。
- 但範本與資安補齊計劃寫的最低版本是 AGP 8.5.1:`docs/lumos-toolchain-knowledge/Projects/Android資安與崩潰靜態檢查補齊_計劃.md:42`,另有測試 `scripts/test_lumos.py:129103`。
- 結果:型錄新列 DATA-95 若照慣例寫「批四(CI 範本:Android Lint)」,在 AGP 8.5.1 到 8.7 的消費專案上會是假接電。
- 規格的「預設開」只驗了預設,沒驗版本。需要在 DATA-95 寫明「AGP 8.8.0 以上才有」,或不寫批四標籤。

## Finding 3:「〈待查證〉由程式從主表撈」是錯的,〈統計〉也沒列入範圍
severity: major
blocking: 是

引句:「〈待查證〉節那一行由程式從主表撈,主表改了自然跟著變」

- repo 裡沒有任何程式產生〈待查證〉。`check.py:344` 只是找那一節的位置,測試 `scripts/test_lumos.py:126957` 還明寫「待查證節不在檢查範圍」。
- 目前就已經對不上:DATA-27 主表來源欄(`skills/kotlin-idioms/checks-catalog.md:559`)已改成〔查證 2026-11-05〕,但〈待查證〉那列(`:865`)還寫「待查(Lint SdCardPath 代號待查)」和「STORAGE(未開頁核對)」。
- 照規格併入 `SdCardPath` 後,這列會繼續留著,跟 DATA-27 打架。型錄自檢和 S3 的「0 個問題」都抓不到。
- 〈統計〉(`:915` 起,例如 `:919` 總列數 514、`:925` 待查證 135、`:926` 規則包條數 211、不接閘 14)和〈輸入與口徑〉`:11` 對「未接」的定義也是人工數字。
- 這批會變動的數字:
  - 新增 12 列。
  - 規則包 +13 條。
  - 不接閘 14 變 26。
  - 會擋的規則守到的列數 +1。
  - 逐列查證 +12。
  - 待查證 -1。
  - 「未接」的定義要補「量過但誤報超過一成或命中不到 20 處」。
- 沒有任何測試或程式核對這些數字,規格範圍沒列,三個月後必然是舊數字。

## Finding 4:DATA-79、82、83 的通電批次被口徑機械鎖在「批四」,跟「讓型錄說實話」打架
severity: minor
blocking: 否

引句:「現成規則欄把 `資安包:VulnerableCryptoAlgorithm` 寫明」

- `check.py:361` 的規則:現成規則欄只要還有 `資安包:` 或 `內建:` 加規則碼,通電批次就必須是「批四(CI 範本:Android Lint)」。
- 規格只改現成規則欄、名稱和實測狀態。DATA-83 的「情境怎麼認」格(`checks-catalog.md:615`)還寫著「形狀:由 Android Lint VulnerableCryptoAlgorithm 判」。
- DATA-79(`:611`)和 DATA-82 同樣:通電批次仍宣稱 Lint 擋,而 MD5、一般寫死秘密、RSA 無填充那半是不接閘的自寫規則。
- 規格該說這三列的「情境怎麼認」「接電方式」「通電批次」怎麼寫成「只接一半」。

## Finding 5:初稿 13 條訊息有 8 條超過 120 字,規格沒講怎麼縮
severity: minor
blocking: 否

引句:「每條訊息 應 以這次新增或併入的型錄列編號開頭、不超過 120 字」

- 引句裡的 120 字上限對應 `check.py:30` 的 `MSG_MAX`,超過就報(`check.py:679`)。
- 範圍 4 說「定案形狀照卷證 experiment/draft-rules.yml.txt,改名改訊息照既有格式」,但初稿訊息字數實測如下,八條超標:

| 規則 | 字數 |
|---|---|
| zip-slip | 134 |
| provider | 180 |
| static-iv | 139 |
| weak-key-size | 130 |
| weak-cipher-suite | 137 |
| object-input-stream | 159 |
| loadurl-external | 144 |
| xxe | 235 |

- 其中 xxe 要砍掉一半,修法說明會被擠掉。規格只說「換編號」,漏了這件工作。

## Finding 6:「22 條沒涵蓋、1 條部分涵蓋」在卷證裡查不到,而且與下游條數對不上
severity: minor
blocking: 否

引句:「兩次都判 22 條沒涵蓋、1 條部分涵蓋(卷證 experiment/ 與本計劃〈實驗〉)」

- 我列 `experiment/` 目錄:只有 `cases/`、兩份語料清單、`draft-rules.yml.txt` 和兩份判讀表(`judge-insample.tsv`、`judge-oos.tsv`)與 `judge-criteria.md`。沒有 MobSF 50 條逐條對照表,也沒有複核結果。
- 條數也對不上:22 加 1 等於 23 條,但下游是 13 條規則加〈不做〉的 7、2、1、1、1 共 12 條,合計 25。
- 除非其中至少兩條規則不是由 MobSF 對照來的,否則數字有誤。三個月後的人無法重驗。
- 對照表應存進卷證,或規格註明哪些規則不是 MobSF 來的。

## 已逐條判不影響(附理由)

- **`t_kt_catalog_security_lint_ids`**:不受影響。24 個資安包 id 各只登記一列,規格保留 `資安包:VulnerableCryptoAlgorithm` 在 DATA-83;新增文字不含別的資安包 id,而且那支測試的 regex 對「後面接括號」放行。
- **`t_kotlin_rulepack_security_rules`**:不受影響。它只掃自己造的 `_KTSEC_CASES`,放置表只列第一批四條。
- **`t_kotlin_rulepack_samples`**:不受影響。只要求「至少 100 條」,不寫死總數。
- **`t_kotlin_rulepack_unwired_dir`**:不受影響。新列帶〔查證〕,不標出處不全。
- **`t_kt_catalog_unverified_rows`**:前提是每個新列都帶〔查證 日期:網址〕,規格已要求。
- **`t_kt_catalog_batch4_wiring`**:DATA-27 維持「批一」,不被批四口徑檢查,不紅。
- **規格引用的網址**:十個官方與 MASTG 網址、四個 Lint 檢查頁我 curl 過,全部 200。MASTG-TEST-0309、0208 的標題與規格用途相符。
- **Lint 檢查頁標的等級**:那四頁都是 Warning、Android Open Source Project 提供。

另外,新規則要過 `check.py` 的樣本檢查:每條規則至少兩處壞例命中、兩段好例,規格〈回退〉有提到「樣本」,但驗收條款沒寫,實作時會被 `check.py` 擋住。
