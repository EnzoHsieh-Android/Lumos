severity: minor

## 1. 分層與依賴方向

大致對齊,有兩處小差異(a1、a2)。

- **新錨點與編輯。** 新錨點「整個呼叫」加在 `_choice_anchor`,跟「方法名」「安全呼叫符」「引數」並列,位置與寫法同批二。對照:`scripts/lumos:77402`、`scripts/lumos:77410`。
- **產壞法擴充。** `(拿掉呼叫)` 的新編法放 `_choice_anchor_edits`,`_choice_api_edits` 不動。批二的安全呼叫符與引數也放在 `_choice_anchor_edits`,所以對齊。對照:`scripts/lumos:77582`、`scripts/lumos:77608`。
- **規則與樣本。** 規則進 `api.yml`,規則 id 等於列號,樣本放新檔。批二也是這樣處理(`nul.yml`、`api.yml`、`choice-batch2.kt`)。對照:`configs/ast-grep/kotlin-choice/rules-choice/`、`configs/ast-grep/kotlin-choice/samples/choice-batch2.kt`。
- **`CHOICE_ANCHORS`。** 錨點名單只在 `check.py` 那一份,加在尾端,同批二。對照:`configs/ast-grep/kotlin-choice/../kotlin-android/check.py:1394`。
- **`_choice_file_points` 的覆蓋判斷(a1)。** 目前 ERROR 與乾節點的判斷不分錨點,一律用命中的行範圍和位元組範圍。對照:`scripts/lumos:77781`。計劃改成依錨點分流,是首例。
- **`_choice_also`(a2)。** 目前以 `anchor == "方法名"` 加 `op` 分流。對照:`scripts/lumos:77680`。計劃改成依「錨點加候選是不是單一識別字」分流。

## 2. 命名與錯誤處理

對齊。

- **名稱。** 錨點名是中文詞,類別一律 API。樣本檔 `choice-batch3.kt` 對應 `choice-batch2.kt`。測試名 `t_choice_*_batch3` 對應 `t_choice_*_batch2`。批二的 `t_choice_points_nul_elvis` 與 `t_choice_points_compose` 是依功能命名,批三的 `_scope` 與 `_retry` 同樣依功能命名,兩種形式批二都有。對照:`scripts/test_lumos.py:146355`、`scripts/test_lumos.py:146434`。
- **產不出壞法。** 比對不到或沒有 `$A` 時回 `(None, None)`,編輯回 None,跟既有一致。對照:`scripts/lumos:77422`、`scripts/lumos:77590`。
- **撤列時的測試跳過。** 做法是「表裡沒有的列號就 `continue`」,對照 `scripts/test_lumos.py:146516` 附近的 `if rid not in have: continue`,同批二。

## 3. 第二種做法

沒有引入第二種做法,只有 a3 一處偏離批二已寫明的慣例。

- **等價排除。** 排除寫進命中規則本身(`not:`、`inside`),不走〈乾節點規則〉。批二的 C-34 到 C-37 就是這樣做,一致。對照:`configs/ast-grep/kotlin-choice/rules-choice/api.yml:244`。
- **補 import。** 沿用「檔頭逐一 import 原寫法才補」。`NonCancellable` 改寫完整套件名來避開補 import,是新的候選寫法,但不是新機制。
- **測試跳過。** 計劃要求本機沒裝 ast-grep 時用 `_SrcOnly` 跳過。批二 `t_choice_points_batch2_api` 已是這樣做。對照:`scripts/test_lumos.py:146361`。
- **批二鄰居的做法(⚠)。** `t_choice_samples_batch2` 在沒有 ast-grep 時是印一行再 `return`,不是 `_SrcOnly`。對照:`scripts/test_lumos.py:146550` 附近。批二計劃〈實務隱患〉自己寫了「一律 `_SrcOnly`」,所以不判計劃不對齊,留給編排者決定要不要順手統一。

## 4. 落點

合理。

- **`lands_in`。** `Systems/kotlin規則包` 與 `Systems/規格閘` 都是既有節點,批二也落這兩篇,不用另開。
- **Verification。** 另開一篇,對應批二的 `Verification/2026-11-17_選擇點第二批上線前實測`,一致。
- **母計劃。** 〈天花板〉第 1 條補指向這份,同批二範圍 6。
- **範圍 6 清單。** 有列出 `kotlin規則包` 的 `about_code`、WHY 與正文,以及 `規格閘` 的 WHY,齊全。

## a1 ERROR 與乾節點覆蓋判斷改成依錨點分流
severity: minor
blocking: 否
引句:「這種錨點改用錨點行到 `end_line` 判」
`_choice_file_points` 原本對所有錨點都用同一條覆蓋規則,每個命中只看自己的行範圍或位元組範圍。對照:`scripts/lumos:77781`。計劃讓「整個呼叫」另用錨點行到 `end_line`,同一支函式裡就有兩套覆蓋口徑。結構上跟 `_choice_anchor` 依錨點分流相同,但覆蓋判斷是首例,需要作者在寫法上給一個對照說明。

## a2 `_choice_also` 改成依候選形狀分流
severity: minor
blocking: 否
引句:「原寫法取 `b[s:e]`,不再要求 `op` 不是 None」
計劃〈用詞〉自己立的原則是「錨點名稱決定編法,不靠命中形狀分流」。`_choice_also` 現在以 `anchor == "方法名"` 分流。對照:`scripts/lumos:77680`。計劃卻讓它依「運算元起始且候選是單一識別字」進新分支,條件含候選的形狀,跟自己的原則不一致。

## a3 作用域規則用正向 `inside` 加 `stopBy`,沒提批二已定的雙重否定寫法
severity: minor
blocking: 否
引句:「不用 `stopBy: end`(會越過內層作用域,外層被內層的 `async` 誤命中」
批二〈實務隱患〉(代碼審 r1 實測)定了「新規則一律把父節點是 X 寫成雙重否定」,為的是壓低 ast-grep 輸出量。第一版 `sbr.yml` 的 C-18 與 `api.yml:244` 附近的規則都照這樣寫。批三的作用域規則改用正向 `inside` 加規則物件 `stopBy`,計劃〈實務隱患〉也承認深層巢狀輸出到數百 MB。計劃有講用正向寫法的理由(要找最近一層 lambda),但沒有講為什麼不能沿用雙重否定,也沒引用那條慣例。

不對齊共 3 條,其中 major 0 條
