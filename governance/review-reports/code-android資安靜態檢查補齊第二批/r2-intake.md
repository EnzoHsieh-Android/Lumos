# r2 收貨紀錄(code-android資安靜態檢查補齊第二批)

## 收貨

- 四席(審查甲二、審查乙二、架構對齊甲二、架構對齊乙二)全部交回後一次從逐字稿存檔;四份不用正規化。
- quote-check:引句有的在分包、有的在修補差異,對整份 r2-snapshot.patch 四份都全數錨定;refcheck missing 0。
- 臨時目錄 /tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/ 收貨後刪。
- 記帳照 r1-記帳更正.md:--spec 與 --reviewed 一律填整份 r2-snapshot.patch,--snapshot 與 --scope-lines 填各席那一包。
- 修正關卡(r1 修補):r1-fix.json 補說明欄後 fix-check 全部通過(150.8s,修正前 9e277bf2 → 修正後 29e48c26)。

## 編號與處置

編號:審查甲二 ta1–ta2;審查乙二 tb1–tb3;架構對齊甲二 xa1–xa2;架構對齊乙二 xb1–xb3(照報告順序)。原報 major:ta1、xb1、xb2。

| id | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|
| ta1 | major | 會擋那條「賦值 0」支拿掉 .mixedContentMode$ 測試照綠,拿掉後 textZoom = 0 也會被擋 | HIT:逐條件改壞 m11,補案例前 150 passed 0 failed | 折:補 C90(textZoom = 0 不報),m11 改壞後紅 |
| ta2 | minor | setter 的 ?. 與不帶接收者兩種形狀沒有案例 | HIT:改壞 m2、m3 照綠 | 折:補 C87、C88,兩個改壞都紅 |
| tb1 | minor | 〈待查證〉17 列的「待核對的來源」格已過期 | HIT:pending_problems 抓到 17 處,與席列的 17 列相同 | 折:17 格改成 —;自檢比對兩格寫不寫內容 |
| tb2 | minor | 只判多列、不判漏列 | HIT:舊測試只走〈待查證〉表 | 折:pending_problems 雙向;改壞「拿掉漏列方向」翻紅 |
| tb3 | minor | 兩支檢查的未核對字樣一份三個、一份兩個 | HIT:測試檔兩處 weak 不同 | 折:check.py 一個常數 _PENDING_SRC(兩個字),寫明跟 _WEAK_SRC 差在無網址 |
| xa1 | minor | 弱套件那條用套件宣告排除函式庫複本 | HIT:同 r1 aa1 | 放行:函式庫複本路徑不固定,ignores 的 glob 排不到;只此一條用,沒侵入共用判斷(同 r1 aa1) |
| xa2 | minor | 條款標記改成「第二批 S3」跟同批既有測試寫法不一 | HIT:t_kotlin_rulepack_security_rules 仍是 [S3][S4] | 折:改照鄰居 t_kt_catalog_unverified_rows 的「[[計劃]] S3」寫法 |
| xb1 | major | 批四字面寫死在測試,另立一套口徑 | HIT:測試裡 "批四(CI 範本:Android Lint)" 字面 | 折:改呼叫 check.py 的 batch4_expected_tags 算該寫的標籤;口徑只住 check.py |
| xb2 | major | 統計與待查證的重數整套住在測試檔、抄 _WEAK_SRC | HIT:測試檔兩支重數函式 | 折:搬成 check.py 的 stats_problems、pending_problems,接在 catalog_problems;測試只驗它 |
| xb3 | minor | 同 xa2 | 同 xa2 | 折(同 xa2) |

--regression-set:xa2、xb1、xb2、xb3、tb3(都是 r1 修補時寫進測試檔的寫法);其餘原本就有,不是 r1 修補造成。
--refuted-set none。

## 逐條件改壞(換形狀:同類「會擋規則的測試抓不到錯」r1 sa1、r2 ta1 連兩輪,改成對會擋那條每個條件逐一拿掉或放寬,一次掃完)

補案例前(150 案例)19 種改壞裡照綠 8 種:m2 拿掉 $X?.setter、m3 拿掉不帶接收者 setter、m8 常數支拿掉左邊名稱、m11 0 支拿掉 .mixedContentMode$、m13b 接收者只容 !!、m16 拿掉除錯排除、m17 常數 regex 不錨定開頭、m18 0 regex 不錨定。補 C87–C94 後(158 案例)19 種全部翻紅(每種 1–25 個案例紅)。改壞腳本在會談暫存區,跑完規則檔逐字還原。

## 型錄自檢的新檢查各改壞一次

c1 沒接進 catalog_problems → 14 個改壞全紅;c2 拿掉漏列方向 → 「漏列 API-2」紅;c3 拿掉已解決還列著 → 「DATA-27」紅;c4 拿掉格子比對 → 兩個格子改壞紅;c5 不核對各級首字、c6 不核對規則包等級、c7 不核對逐列查證 → 各自那一項紅。過程中發現兩個改壞會被別道代抓(DATA-27 那列格子有字、漏列連帶改變統計數),改成兩格寫 —、統計數一起改,讓每個改壞只剩一道抓得到。

## 先查世界

- PRIOR-ART:ta1、ta2(同類第二輪)——變異測試的做法:對受測程式的每個條件做一次小改動(拿掉條件、放寬邊界),測試要殺死每個變種;PIT 的變異算子清單 https://pitest.org/quickstart/mutators/ (例:CONDITIONALS_BOUNDARY、REMOVE_CONDITIONALS)。採用:對規則每個條件手寫一個變種、全部要被殺;不採用整套變異工具(ast-grep 規則不是 Java,沒有現成工具)。
- PRIOR-ART:xb1、xb2、tb1–tb3——規則包既有慣例(檢查住 check.py 的 catalog_problems、測試只驗它;t_kt_catalog_batch4_wiring 檔頭寫明不在測試另立一套口徑),沒有要另查的業界做法。
- PRIOR-ART:xa1——同 r1 aa1。
