severity: major

## 逐問作答

### 1. 分層與依賴方向

新邏輯掛的位置(同一張 `_STACK_QUESTION_SPECS` 字典、同一支 `_pitfall_diff_collect` 收集流程)跟鄰居一樣,呼叫層級沒有跨層直呼的問題——它會像既有 9 棧一樣被 `_stack_applicability` / `code-loop check` / `gov --stats` 消費。

但「怎麼決定一支檔屬於哪個/哪些鍵」跟鄰居不一樣:既有 9 棧一律靠 `_stack_key_for_file`(`scripts/lumos:20221-20230`)決定唯一一把鍵(連 `.ts`/`.js` 的前後端分流也是回一把鍵,見 `scripts/lumos:20226-20229`),`_by_stack` 因此是「一支改動檔的行只進一個桶」的一對一結構(`scripts/lumos:26117-26122`)。這份設計的第 2 條要求同一批增刪行「不管副檔名是哪一棧」都要再進 `data` 這個桶,等於一支 `.py` 檔的行要同時進 `py` 桶跟 `data` 桶——從一對一變多對多。這是分層沒問題、但「判定歸屬」的模型變了,詳見第 3 問 F1。

### 2. 命名與錯誤處理

錯誤處理沒有新增路徑(表態驗證、`code-loop check` 擋法、治理帳寫法整套照舊),這點跟既有一致。

命名上有一處跟既有 9 棧的規則不一致:既有題目 id 前綴一律等於它在 `_STACK_QUESTION_SPECS` 的鍵本身(`kt` 鍵 → `kt-compose`、`java` 鍵 → `java-concurrency`、`dart` 鍵 → `dart-build`,見 `scripts/lumos:20018-20168` 逐條核對)。這份設計卻是「鍵 `data`、id 前綴 `ds-`」(計劃第 46 行),鍵與 id 前綴對不上,是既有 9 棧都沒有的形狀。詳見 F3。

### 3. 第二種做法

有,而且不只一處,計劃自己也承認是刻意換掉既有判定方式(WHY 行,計劃第 27、28 行)。三個具體落點:

- **多重歸屬**(F1,major):一支檔同時進自己的棧桶又進 `data` 桶,跟 `_stack_key_for_file` 「一支檔一把鍵」的既有模型不同。
- **用另一套分類器決定要不要出題**(F2,major):沒副檔名的腳本目前 `_stack_key_for_file` 回 `None`(`scripts/lumos:20230`,`ext` 是空字串,不在 `_STACK_PERF_QUESTIONS` 裡),不會進任何棧;計劃第 2 條要它改用「每支檔有家那套判定」(`_is_code_file` 的 shebang 偵測,`scripts/lumos:6199-6228`)才算數。既有 9 棧的判定邏輯都封裝在 `_stack_key_for_file` 一支函式裡;`data` 卻要接另一個子系統(每支檔有家/`_is_code_file`,連豁免規則都是 `_NODEHOME_EXCLUDE_GLOBS`/`_cochange_excluded` 那一套,跟 `_stack_changed_ok` 既有的豁免規則——測試檔、簿記檔、`governance/review-reports/`——是兩份不同的排除清單)餵同一張題表,是第二種判定適用性的路。
- **行數門檻的棧例外**(F4,major):`_stack_applicability(lines_by_stack, threshold)` 對所有棧套同一個 `threshold`(`scripts/lumos:20281-20311`,`over = len(raw_lines) > threshold` 在 20292 行對每個 `stk` 都跑),沒有「某棧不吃門檻」這種分支。計劃第 4 條明講 `data` 要單獨跳過這條全表適用規則(計劃第 49 行),是既有共用函式裡沒有的第二套規則。

更貼既有做法的替代:如果真要讓「跨副檔名」的題組成立,比較貼近現有形狀的做法是像 `node`/`vue` 那樣——用一個判定函式把它也「收編」進 `_stack_key_for_file` 的一對一模型(例如讓某些觸發詞在任何棧命中時都順便標記 `data`,但輸出上仍是同一支檔對應一把主鍵,`data` 當成該棧規格裡「附加題」而非另一個平行桶),而不是在 `_by_stack` 之外另開一條多對多、另一套門檻、另一套分類器的通道。計劃目前的做法是三處都各開一個例外,不是抽出一套跟既有一致的規則。

### 4. 落點合不合理

`lands_in` 同時列了 `Systems/效能檢核目錄` 與 `Systems/棧別提問表態閘`(計劃第 11-13 行)。後者(表態閘/機制層,`docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md`)本來就是跟題目內容無關的通用機制,落這裡沒問題。

但 `Systems/效能檢核目錄` 開篇就自報家門:「各平台 code review 階段該查的效能問題參考目錄」(`docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:19`),PRIOR-ART 行也寫明借的是 Compose perf 文件、ASP.NET Core Best Practices、Core Web Vitals 這類效能來源(該檔 43 行),定位是「`_STACK_QUESTION_SPECS` 的效能題內容源」。`ds-` 七題是 DDIA 式的資料正確性題(新舊互讀、寫一半、快取失效、併發競態、時鐘、不可逆、對外副作用),不是效能題,寫進這篇會讓這個節點的「權威菜單=效能」定位失真,之後看這篇筆記的人(下一個 session 的 AI)會誤以為 `ds-` 題也是效能檢核的一種。比較合理的落點是只落 `Systems/棧別提問表態閘`(機制層本來就中立),`data` 題組的內容本身另開一篇(例如仿 `Systems/棧別提問表態閘` 對 py/java/dart 補棧的寫法,各補棧計劃都寫回同一份「內容源」筆記——但那份內容源限定效能;`ds-` 題該有自己的內容源筆記而不是塞進效能那篇)。

## 發現

## F1 跨棧「data」鍵要求一支檔同時進多個棧桶,跟既有一對一模型不同
severity: major
blocking: 是
引句:「增刪行,不管副檔名是哪一棧」
file: `scripts/lumos:20221`
file: `scripts/lumos:26117`

## F2 沒副檔名腳本改用「每支檔有家」判定而非 `_stack_key_for_file`,是第二套分類器
severity: major
blocking: 是
引句:「跨棧題組改用每支檔有家那套程式檔判定」
file: `scripts/lumos:20230`
file: `scripts/lumos:6199`

## F3 題目 id 前綴 `ds-` 跟題表鍵 `data` 對不上,破壞既有 9 棧「鍵=id 前綴」的命名慣例
severity: minor
blocking: 否
引句:「放進同一張題表(鍵 `data`,題目 id 一律 `ds-` 開頭)」
file: `scripts/lumos:20112`
file: `scripts/lumos:20136`

## F4 「不吃行數門檻」是對共用函式 `_stack_applicability` 的單棧例外,既有函式對所有棧套同一門檻
severity: major
blocking: 是
引句:「資料狀態題組只看觸發字」
file: `scripts/lumos:20281`
file: `scripts/lumos:20292`

## F5 `lands_in` 把非效能題組寫進定位為「效能問題參考目錄」的節點,落點跟節點自報的範圍不符
severity: minor
blocking: 否
引句:「Systems/效能檢核目錄」
file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:19`

不對齊共 5 條,其中 major 3 條。
