severity: minor

## 1. 分層與依賴方向
結構對齊。事件帳外掛 `seatOf` 照守衛 `parseMarker` 的同一套(切行含 U+2028/2029、`clean` 剝格式字元判空行、`SEAT_RE` 嚴格比、三段 `segOk`),跟既有「兩端各寫一份、共用案例對」同形:`rules-fixture.ts` + `t_ledger_rules_match_reader`、`SEAT_RE` 從原始碼抽出來比。兩支外掛彼此沒有匯入,依賴方向沒變;案例檔各歸自己的家(兩篇 Systems 的 about_code 都列了)。
對照:`mods/claude/lumos-ledger/hooks/register.ts:290`(seatOf)、`mods/claude/lumos-guard/hooks/register.ts:70`(parseMarker、firstLine 在 :56)、`mods/claude/lumos-ledger/hooks/rules-fixture.ts:5`、`scripts/test_lumos.py:74236`。
差異但有理由:`rules-fixture.ts` 只有一份(Python 讀它);這裡 Python 端沒有第三份實作,外掛不能匯入別的外掛資料夾,所以放兩份、Python 比 bytes。這是既有模式的必要變形,不算第二種做法。

## 2. 命名與錯誤處理
命名沿用守衛的 `clean`、`FORMAT_CHARS`、`segOk`、`SEAT_RE`;案例檔 `SEAT_CASES` 與 `RULES` 同為 `export const` 大寫。錯誤處理一致:非字串、不合格、寫壞都回 null,不丟錯。`SEAT_RE` 的抽取正規式改成跟 `t_seat_templates_carry_marker` 同一種(`/(.+)/$`),對齊。
有兩處文字沒跟上(見 F1、F2)。

## 3. 第二種做法
沒有新增第二種判法:事件帳這邊少了 `SEAT_LOOSE_RE`/`looseHead`,但那只決定「寫壞」與「不是標記」的差別,對事件帳都是 null,結果等價,案例檔涵蓋這幾類。「兩份一模一樣的檔 + 比 bytes」是專案裡新的小手法(此前沒有跨外掛複製檔),但由外掛不能跨資料夾匯入逼出來,而且有 Python 測試釘住,不會漂移。

### F1 守衛節點裡的對照說法已過時
severity: minor
blocking: 否 — 只是節點文字與新做法矛盾,結構對
引句:「③Python 端從原始碼抽 `SEAT_RE` 編譯來比——標記格式只留一份真相,不像事件帳那樣兩端各寫一份再拿同一組案例對。」

說明:同一個 diff 新增的第 92 行與事件帳節點都說現在事件帳就是「兩端各寫一份、共用案例」,這句「不像事件帳那樣」讀起來變成在說事件帳的 `seat` 判法不是這樣。建議把這句限縮成「Python 端抽 SEAT_RE 比」或註明事件帳 `seat` 欄現在也走共用案例。

### F2 Python 測試的說明字串沒涵蓋新增的案例檔比對
severity: minor
blocking: 否 — 命名與說明不一致,測試行為本身對
引句:「事件帳補記搜尋與席位 S4:事件帳外掛記 spawn 的 seat 欄用的 SEAT_RE,跟審查席隔離外掛的一字不差」

說明:`t_ledger_seat_re_matches_guard` 現在多比兩份案例檔,docstring 與函式名(`..._re_matches_guard`)仍只講 SEAT_RE。既有 `t_ledger_rules_match_reader` 的 docstring 有把案例檔寫進去,這邊建議照辦。

總結:不對齊共 2 條,其中 major 0 條
