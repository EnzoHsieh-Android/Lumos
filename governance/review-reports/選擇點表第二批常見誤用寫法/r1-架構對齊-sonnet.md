severity: minor

審查依據是 `r1-snapshot.md` 對照 `/Users/enzo/harness/lumos-near-miss` 的第一版實作。

## 問 1 分層與依賴方向:對齊

- **白名單只有一份。** 第一版的類別與錨點白名單只在 `configs/ast-grep/kotlin-android/check.py:1392-1394`。lumos 讀表是經 `scripts/lumos:76891` 的 `_choice_tables` 呼叫 check.py 的 `choice_tables`,自己沒另存一份。計畫範圍 4 寫「白名單只在這裡一份」,跟現況一致,沒有跨層。
- **產壞法留在 lumos。** 新錨點與新編輯分支是加在 `_choice_anchor`(`scripts/lumos:77118`)和 `_choice_edits`(`scripts/lumos:77252`)。第一版的 `方法名` 錨點也是在這兩處用 `row["anchor"] == "方法名"` 分派,同一個形狀。
- **規則檔只負責命中。** 規則檔裡沒有寫產壞法的邏輯。`_choice_edits` 的新分支有必要:`(Unit)` 走通用分支時,`_choice_atomic` 會判成不原子,節點前面又接著 `LaunchedEffect`,所以會被包成 `((Unit))`(`scripts/lumos:77193-77196`、`77142`)。
- **統計層對齊。** 每個壞法事件已帶 `row`(`scripts/lumos:18422`),放行事件也帶 `row`(`scripts/lumos:18425`)。「依列號」可以直接用既有事件,不用新增事件欄位。

## 問 2 命名與錯誤處理:2 條不對齊

- **類別名對齊。** `NUL` 加在尾端,前例是 `API` 也不是論文縮寫(`check.py:1392`)。錨點名「安全呼叫符」「引數」,和「方法名」「陳述起始」是同一種中文名詞風格。
- **錯誤處理對齊。** 類別或錨點寫錯由 check.py 指列號的做法照舊(`check.py:1432-1435`)。

不對齊 1:規則檔名。第一版規則檔名等於類別小寫(`aor/lcr/ror/uoi/sbr/api.yml`),同一類別的列都在同一檔。計畫把 `LaunchedEffect`、`remember` 兩列類別記成 API,規則卻放進 `compose.yml`,API 類的列因此分在兩個檔。
severity: minor
blocking: 否
引句:「新增 `nul.yml`(`elvis_expression`;`?.` 的 navigation_suffix)、`compose.yml`(」
佐證 file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:1`

不對齊 2:類別歸屬。第一版 API 類只有「換方法名」與「(拿掉呼叫)」兩種(`scripts/lumos:77281-77288`)。`LaunchedEffect`、`remember` 是改或刪整個引數清單,性質不同,卻歸 API。同一份計畫為了 `?:`、`?.` 另開了 NUL 類別,這兩列沒有比照。
severity: minor
blocking: 否
引句:「四列 API(API 兄弟寫法,錨點分別是方法名、方法名、引數、引數)」
佐證 file: `scripts/lumos:77281`

## 問 3 第二種做法:2 條不對齊

- **新錨點做替換:對齊。** 理由見問 1,這是沿用 `方法名` 的分派形狀,沒有重複既有機制。
- **`?:` 的 null 字面值前提:對齊。** 計畫沿用型別前提欄「運算元有 null 字面值」,語意同 `_choice_excluded`(`scripts/lumos:77199-77208`)。

不對齊 3:等價排除的做法。第一版處理等價與編不過,是靠型別前提欄(`check.py:1394`、`scripts/lumos:77199`)和乾節點規則(`rules-arid/arid.yml`)。計畫把「`LaunchedEffect(Unit)` 等價」和「`remember` 沒尾隨 lambda 編不過」寫進 `compose.yml` 的規則本身。後者引的正是論文 3.2.1,第一版對這類事前擋是放在型別前提欄。同一份計畫的 `?:` 列卻用了型別前提,所以一份計畫裡有兩種做法。

這不判 major。`rules-choice/sbr.yml:9-27` 已有用 `not:` 在規則裡排除的先例(C-18 的 A.1.12),型錄 C-18 列也把它寫進「ast-grep 規則」欄。⚠ 給編排者:要不要視為「第二種做法」由你裁。
severity: minor
blocking: 否
引句:「引數只有一個而且是 `Unit`、`true`、`false` 字面值時不命中」
佐證 file: `configs/ast-grep/kotlin-choice/rules-choice/sbr.yml:9`

不對齊 4:`gov --stats` 的數法沒寫死。現行選擇點段有兩套口徑:第一次殺掉率只算 attempt 1 且 `via == run`,被回報的存活用 `ever` 集合(`scripts/lumos:17896`、`17934`)。放行理由則全部列出(等價、不是需求、不適用,見 `scripts/lumos:17908` 與型錄放行格式)。計畫的「依列號」沒說壞法數、殺掉數、存活數用哪一套。放行理由寫成「等價、不是需求、其他」,跟現行標籤「不適用」不是同一組。實作時容易做出第二套口徑。
severity: minor
blocking: 否
引句:「第二批與第一版每一列各自的壞法數、殺掉數、存活數、跑不出結果數,以及被回報存活後的放行理由分布(等價、不是需求、其他)」
佐證 file: `scripts/lumos:17896`

## 問 4 落點:1 條不對齊

- **主體落點合理,不用另開一篇。** `Systems/規格閘` 的 responsibility 已含「改動選擇點的語法樹掃描與每行挑壞法(choice-points)」,第一版的 `gov --stats` 選擇點段說明也在這篇(summary 第 79 行)。「依列號」和 lumos 產壞法屬於這裡。`Systems/kotlin規則包` 管型錄、規則檔、check.py,第一版〈選擇點表〉的 WHY 在第 95 行,第二批來源與不收理由屬於這裡。
- **兩篇的大小。** 規格閘 218 行約 97KB,規則包 148 行約 51KB,都不小。但第一版也是寫這兩篇,沒有選擇點專屬的 Systems 節點(`Systems/` 底下查無),所以不算不一致。

不對齊 5:規則檔要登記到家。`Systems/kotlin規則包` 的 about_code 是逐檔列出規則檔(第 22-27 行列了 `ror/lcr/aor/uoi/sbr/api.yml`),新增 `nul.yml`、`compose.yml` 與新樣本都要加進去(鐵則 5,提交前會擋)。計畫範圍 6 只寫補 WHY 行,沒提這件事。
severity: minor
blocking: 否
引句:「Systems/kotlin規則包 補 WHY 行(第二批來源與不收理由)」
佐證 file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:22`

不對齊共 5 條,其中 major 0 條
