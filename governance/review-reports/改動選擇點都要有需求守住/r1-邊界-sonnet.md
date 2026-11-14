severity: major

## b1 測試檔判定沒帶 layout,androidTest 會被當正式碼
severity: major
blocking: 是——照 spec 字面呼叫 `_nodehome_is_test(path)`,S1 第 7 列的 androidTest 檔會被列成選擇點。
- 位置:〈用詞〉選擇點、預期值表 S1。
- 查證:`_nodehome_is_test(path, layout=({}, {}))` 的 androidTest 判定要靠 `_nodehome_layout(all_paths)` 算出來的 layout。我實際呼叫:不帶 layout 時 `app/src/androidTest/java/x/FooTest.kt` 與 `TestUtils.kt` 都回 False。帶 layout 才回 True。
- 另外 `app/src/testFixtures/…`、`app/src/sharedTest/…` 不論帶不帶 layout 都回 False。這兩種目錄 Android 專案很常見,裡面的 fake 與輔助碼會被當正式碼產生選擇點。
- 缺的是:spec 沒寫 layout 從哪一版的檔案清單算(要算 B 版),也沒處理 testFixtures 與 sharedTest。
- 例:改動在 `app/src/androidTest/.../FooTest.kt` 含 `filter`,預期無選擇點,實際會列出。
引句:「〈用詞〉測試檔照 _nodehome_is_test」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:48129`

## b2 識別字成員會命中非呼叫用法,產生編不過的壞法
severity: major
blocking: 是——表成員被當單純字串比對,命中參數名、屬性、宣告,噪音多到卡推送。
- 位置:〈用詞〉選擇點的比對規則。
- 查證:`_kt_trigger_re` 只擋前後是英數或底線,不要求 `.` 前綴或 `(`、`{` 後綴。
- `padding(all = 16.dp)` 會命中 `all`→`any`,壞法是 `any = 16.dp`,編不過。
- `pair.first` 會命中 `first`→`last`,Pair 沒有 `last`,編不過。
- `val filter = MutableStateFlow(..)` 的宣告會命中,成了改名,其他行引用到就編不過。
- `+`→`-` 遇到字串串接 `"a" + b` 也編不過。S20 範例拿 `toString` 裡的 `+`→`-` 當存活,實際多半是 no_result。
- 這些都落進 no_result,而 no_result 會擋推送(見 b3)。spec 的〈實務隱患〉只說「多半要改表」。
- 例:`Modifier.padding(all = 8.dp)` 在改動行 → 預期不該產生選擇點,實際產生一個。
引句:「識別字成員照整字比對(同 `_kt_trigger_re` 的邊界)」

## b3 no_result 擋推送卻沒寫人能做的出口
severity: major
blocking: 是——一個編不過的壞法,開發者在推送前沒有任何規格內的動作能放行。
- 位置:〈用詞〉有效處置、〈範圍〉3、〈範圍〉4。
- 問題:有效處置只認 killed 或 judged,no_result 不算。
- 〈範圍〉3 標題是「存活的處置」,沒說 `--judge` 能不能用在 no_result。
- 唯一明講的出路是改型錄表,那是工具鏈維護者的事,不是被擋住的開發者能做的。
- 例:`pair.first` 的壞法編不過 → no_result → 推送被擋 → 開發者只能 `--import`(只補 import,救不了這個)或去改工具鏈型錄。
- 要補:no_result 能不能 `--judge`、`as` 要不要加第三種值(例如「壞法不適用」),以及這種判決是否同樣式推廣。
引句:「最新一筆是 `survived`、`no_result` 不算,重跑會再跑。」
引句:「多半要改表(把那個成員拿掉)而不是要人處置」

## b4 `?.` 與帶點成員沒說適用哪套邊界規則
severity: minor
blocking: 否——有兩種合理實作,但多半不會做錯到擋人。
- 位置:〈用詞〉選擇點、〈範圍〉空值。
- 問題:`?.` 既不是識別字,也不在「換運算子」那組。若套運算子規則(兩側要有空白),`a?.b` 永遠命中不到。
- 預期值表 S1 沒有任何 `?.` 的列,沒有測試釘住。
- 拿掉呼叫的 `.flowOn(…)` 命中 `x?.flowOn(d)` 時,拿掉後剩 `x?`,語法錯,成 no_result。
- `.flowOn(…)` 的括號跨行時不算選擇點,是靜默漏掉。天花板沒寫這條。
引句:「運算子成員只認兩側都有空白的」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:39345`

## b5 「外層 fun」跟被沿用的函式邊界程式不是同一件事
severity: major
blocking: 是——需求脈絡組的鍵在不少常見寫法下算不出來,spec 只定了頂層的退路。
- 位置:〈用詞〉需求脈絡組。
- 查證:`_kt_sit_material` 往上找的是最近的「頂層或類別層」宣告,範圍包含 fun、val、var、class、object、interface。
  - 它回的是 (起, 迄) 行號,沒有名字。
  - 超過 120 行(`_KT_SIT_MAT_MAX`)或結尾早於命中行就回 None。
- 照 `_kt_sit_hdr_is_class` 的邏輯,`object : Foo { … }` 匿名物件的本體算類別層。外層函式裡匿名物件之後的點,往上會先撞到匿名物件裡的 fun,迴圈不命中、回 None。
- 屬性初始化(`val x = a > b`)、`init { }`、長於 120 行的 @Composable 函式,都沒有被這支找到對應的 `fun`。
- spec 只定「頂層的點按檔分組」。這些在類別裡但不在函式裡、或長函式的點,被歸到哪一組沒寫。
- 還有:函式名怎麼取(擴充函式 `fun String.foo()`、`fun interface`、泛型 `fun <T> …`、反引號名)沒定。
- 例:200 行的 `@Composable fun Screen()` 裡兩個存活點 → 材料回 None → 組鍵未定義,`--group` 與 `--split` 沒有可指的組號。
引句:「往上找最近的 `fun` 宣告,沿用情境題切段找函式邊界那支」
引句:「頂層(不在函式裡)的點按檔分組」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:40083`

## b6 樣式的 `<top>` 與常見函式名讓「不是需求」推廣範圍過大
severity: major
blocking: 是——一次判決會跨檔、跨類別壓掉未來的缺口,跟 spec 自己宣稱的「不跨函式」不符。
- 位置:〈用詞〉樣式、〈實務隱患〉樣式推定。
- 問題:樣式 = (表組號, 成員, 外層函式名),沒有檔、沒有類別。S20 第 1 列也明寫「另一支檔的 `toString`」要被推定。
- `<top>` 是所有非函式內程式的共用名,例如屬性初始化、`init`、b5 那些找不到函式的情況。
- `onCreate`、`invoke`、`map`、`build`、`copy` 這類全專案重複的函式名也會跨檔共用樣式。
- 例:有人在 `A.kt` 的屬性初始化裡把 `+`→`-` 判 not-requirement,之後 `B.kt` 的 `init` 區塊裡的 `+` 也被自動推定,不擋。
- 需要把檔路徑(至少模組)或類別名放進樣式,或明講 `<top>` 不推廣。
引句:「外層函式名照寫,頂層寫 `<top>`」
引句:「樣式含外層函式名,不跨函式推廣」

## b7 檔頭有 BOM 時 package 行排除失效
severity: minor
blocking: 否——只影響第一行的 package 宣告。
- 位置:〈用詞〉選擇點。
- 查證:`_kt_sit_read_many` 用 `decode("utf-8", "replace")`,BOM 不會拿掉。`re.match(r"\s*(?:import|package)\s", "\ufeffpackage a.filter")` 我實測回 False。
- 所以新檔第一行 `package com.app.filter`,`filter` 會被當成 `filter`↔`filterNot` 的選擇點。
- `_kt_sit_read_many` 只換 `\r\n`,單獨的 `\r` 不處理;而 guard kill 用 `open(encoding="utf-8")`,連 `\r` 都轉。兩邊換行口徑不完全一致。CRLF 本身沒問題:兩邊都能對上 `\n`。
引句:「排除 `import`/`package` 行之後,選擇點表成員的每一次出現」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:40114`

## b8 天花板 2 與剝註解程式的實際行為矛盾
severity: minor
blocking: 否——只是文字與實作不一致,方向偏保守。
- 位置:〈天花板〉2。
- 查證:`_kt_strip_code_tok` 遇到反引號只跳過、不記成要剝的區段,內容原樣留在剝過的文字裡。三引號字串裡的 `${…}` 也當程式碼保留。
- 實測輸出(節錄):`fun \`a > b test\`() = x` 與 `${a > b}`(位於三引號字串內)都原樣留著。
- 所以反引號識別字與原始字串樣板裡的運算子,會被當選擇點,跟「不算」相反。
- 例:`` fun `a > b test`() = x `` → 會產生 `>`→`>=` 的選擇點(改名)。
引句:「跨行原始字串與反引號識別字裡的不算」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:6939`

## b9 推送閘算不出來時擋還是放沒寫
severity: major
blocking: 是——失敗模式落在實作者的猜測,放行是繞過閘,擋下會卡死大分支。
- 位置:〈範圍〉4 讀哪一版、〈實務隱患〉推送閘的耗時。
- 查證:既有情境題的呼叫端對 `_KtSitUnverifiable` 與 `_KtSitOverBudget` 一律「擋下:算不出來」,例如 `scripts/lumos:75548` 與 `scripts/lumos:75582`。
- 觸發條件有四種:單支 .kt 超過 4MB(`_KT_SIT_READ_MAX`)、切段超過 30 秒預算(`_KT_SIT_BUDGET`)、檔名含引號或換行讓 git 加引號、git 出錯。
- spec 只講「B 取不到照既有放行規則」與「治理帳讀不到 → 擋」,沒講選擇點掃描本身超時或讀不到時的行為。
- 若放行,等於一個大改動或怪檔名就能整道閘不判;若擋,又沒有逃生口。5000 行改動的耗時只寫「要量」。
- 例:B 版有一支 5MB 的 .kt,有選擇點 → 預期該擋哪個 reason?spec 沒有對應的 reason(blocked 的 reason 集合沒有「算不出來」)。
引句:「大分支(改 5000 行)要量,實作時寫進報告。」

## b10 「組號」一詞指兩種東西
severity: minor
blocking: 否——形式不同,多半看得出來,但帳欄位與統計有歧義。
- 位置:〈用詞〉選擇點表、需求脈絡組、樣式;〈範圍〉2 的記帳欄位、〈範圍〉3 的 `--judge`、`--group`。
- 問題:表組號是 `C-<n>`,需求脈絡組組號是 `<檔>::<函式名>`,都叫組號。
- 帳上的 `group` 欄位沒說是哪一種。`--stats` 的「每組平均點數」要的是脈絡組,樣式要的是 `C-<n>`。
- `--judge <定位>|<組號>` 若給 `C-3`,是整個表組的所有點(跨檔),還是脈絡組?沒說。
- 組號的 `::` 與檔路徑本身的 `:`、`#`(定位語法 `<檔>:<行>#<n>`)沒有處理檔名含這些字元的規則。
引句:「(組號 `C-<n>`、成員、外層函式名)」

## b11 預期值表有一個來源指到不存在的條文
severity: minor
blocking: 否——只是追溯指錯。
- 位置:預期值表 S11 第 3 列。
- 查證:〈範圍〉4 沒有「殺掉它的測試要還在」這條,它在〈用詞〉有效處置。
- 另外:改到的行是整行層級,同一行只改了一個 token,該行所有既有選擇點都要重新處置。這是設計取捨,但 spec 沒寫進天花板。
引句:「〈範圍〉4 殺掉它的測試要還在」

## 逐節
- 白話、舊否決比對、不做、依據來源、回退:已讀,無 finding。
- 驗收條款 S1–S20:S17 排在 S20 之後,編號齊全,無缺號。
- 每點一次 `cmd_guard_kill`:一次改動 N 個選擇點就有 N 次隔離工作樹與基準。Android Gradle 基準動輒數分鐘,RETIRE-IF ② 的十分鐘上限很容易超過。這是設計取捨,不單獨計 finding。

## 實務隱患鏡頭
- 效能/資源:N 點 N 次基準(見上);推送閘讀檔上限與預算見 b9。
- 輸入消毒:`old` 前 60 字進報告與推送訊息時,spec 沒寫要走 `_kill_esc`。原始碼含終端跳脫字元會原樣印出,程式裡已有 `_kill_esc` 可用。
- 換行:CRLF 兩邊口徑一致,無隱患;BOM 見 b7。
- 併發:單人依序操作,spec 已排除,無。
- 資安:選擇點內容來自作者自己的原始碼,無外部輸入面,無。

## 固定席節點(Systems/guard-kill)
- INVARIANT rc 優先序:不影響。choice-kill 只讀 `result_out` 的列,自己決定 rc,`cmd_guard_kill` 的 rc 判定沒改。新增的 `source` 參數不傳維持原行為。
- INVARIANT `--json` 純度:不影響。choice-kill 以非 json 模式呼叫,不碰 `--json` 的輸出路徑;`source` 只加在帳本列。

最嚴重:major;blocking 共 6 條
