# r3 收貨紀錄(code-android資安靜態檢查補齊第二批)

## 收貨

- 四席(審查甲三、審查乙三、架構對齊甲三、架構對齊乙三)全部交回後一次從逐字稿存檔;架構對齊甲三四行 severity 前有縮排,report-normalize --write 只搬到行首。
- quote-check 四份對整份 r3-snapshot.patch 全數錨定;refcheck missing 0。
- 臨時目錄 /tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/ 收貨後刪。
- 修正關卡(r2 修補):fix-check 全部通過(168.6s,修正前 29e48c26 → 修正後 5d1e7941)。
- 這是 standard 的第三輪(上限)。

## 編號與處置

編號:審查甲三 ua1–ua2;審查乙三 ub1–ub2;架構對齊甲三 ya1–ya4;架構對齊乙三 yb1–yb5(照報告順序)。原報 major:ub1、ya1。全部折入。

| id | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|
| ua1 | minor | 〈待查證〉只寫編號一格的列讓 pending_problems 崩(IndexError) | HIT:席在複本插 `| API-3 |` 重現 | 折:_pending_table 每列補到三欄;改壞例子「只寫編號一格」,拿掉補欄會丟例外、測試記成紅 |
| ua2 | minor | 計劃範圍 6 點名的情境、守到列數、級的組合、出處不全、人裁沒核對 | HIT:席改這些數自檢回 [] | 折:_stats_expected 補這五類;每個數各有改壞例子 |
| ub1 | major | 規則包條數那項沒有改壞例子,拿掉核對測試照綠 | HIT:席在複本刪那項 29 passed | 折:改壞清單改成〈統計〉每個數各加 1(含規則包條數 227);拿掉那項核對 → 測試紅 |
| ub2 | minor | 各主題、規則包各等級只改壞一個代表 | HIT:席縮迴圈照綠 | 折:九個主題、四個等級、四級兩種算法、13 種級的組合各一例 |
| ya1 | major | 主題前綴另抄一份 _STAT_TOPICS,_MAIN_ROW_RE 已有 | HIT:check.py 兩處清單 | 折:_MAIN_TOPICS 一處,_MAIN_ROW_RE 從它組 |
| ya2 | minor | 〈待查證〉切節寫死〈統計〉當節尾、少防呆、重複編號不報、死碼 | HIT:讀碼 | 折:節尾改下一個 `## `(同 _abbr_table),補欄、報重複編號,拿掉走不到的分支 |
| ya3 | minor | _PENDING_SRC 字面重抄 _WEAK_SRC 兩個字樣 | HIT:讀碼 | 折:_PENDING_SRC = _WEAK_SRC[:2] |
| ya4 | minor | 問題代號用 `<統計>`,鄰居用 `<catalog>` | HIT:讀碼 | 折:改 `<catalog>`,訊息帶「〈統計〉」 |
| yb1 | minor | 測試又拼一次批四標籤字串 | HIT:讀碼 | 折:改用 check.py 的 B4_TAG_LINT |
| yb2 | minor | _kt_batch2_catalog_problems 說明仍寫判準全部寫死在本檔,翻紅釘沒提批四 | HIT:讀碼 | 折:說明改寫,翻紅釘補批四那道 |
| yb3 | minor | 改壞實驗沒走鄰居的 _ktpack(copy=True) | HIT:讀碼 | 折:改 _ktpack(copy=True),跑完刪複本 |
| yb4 | minor | 同 ya1 | 同 ya1 | 折(同 ya1) |
| yb5 | minor | stats_problems 問題代號混用 `<catalog>` 與 `<統計>` | HIT:讀碼 | 折(同 ya4) |

--regression-set:13 條全部(都出在 r2 修補新加的 check.py 檢查與改寫的測試)。--refuted-set none。

## 修補後的驗證(上限輪,沒有下一輪全新席可派,編排者機械驗)

- 對 check.py 這輪改到的每一道逐一改壞(14 種:沒接進 catalog_problems、拿掉漏列方向、拿掉已解決還列著、拿掉格子比對、不報重複編號、不補空格、主題只核對第一個、不核對級的組合、不核對形狀類、不核對人裁、不核對規則包條數、規則包等級只核對 error、不核對守到列數、各級首字只核對 A),跑 t_kt_catalog_stats_consistent 每種都紅、各自對上它那一項改壞例子;check.py 跑完逐字還原。
- 子集:-k kt_catalog 157 passed、-k kotlin_rulepack 209 passed、-k kotlin_catalog 59 passed、-k linter_catalog 6 passed;規則包自檢 227 條 0 個問題;新增告警 0(pitfalls 判 standard)。

## 先查世界

- PRIOR-ART:ub1、ub2、ua2(同類第三輪:改壞清單只挑代表)——同 r2 的變異測試做法(https://pitest.org/quickstart/mutators/),這輪換形狀:改壞清單由〈統計〉每個手寫的數機械產生(每個數各加 1),不再手挑代表;編排者另對 check.py 每道逐一改壞驗殺得掉。
- PRIOR-ART:ya1–ya4、yb1–yb5——規則包與 check.py 既有慣例(主表唯一讀法 main_rows、節尾切法同 _abbr_table、問題代號 `<catalog>`、改壞走 _ktpack(copy=True)),沒有要另查的業界做法。
- PRIOR-ART:ua1——輸入防呆照 _abbr_table 的欄數保護。
