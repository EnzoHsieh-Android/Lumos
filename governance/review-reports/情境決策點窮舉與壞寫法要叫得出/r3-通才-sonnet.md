severity: major

## 審讀範圍與結論

我逐節讀了 spec。我也把官方 1.10.2 的 klib 與 JVM 清單抓下來,照 spec 的抽法試抽,並對照 `check.py`、`scripts/lumos`、型錄和 `test_lumos.py`。

- 照 spec 試抽 klib,只有 `asCoroutineDispatcher`、`asPromise`、`awaitAnimationFrame`、`promise` 四個被丟,跟 spec 說的一致。
- 五個錨點名稱都在,總數遠超 300。
- 指令引用都核過,存在:`lumos gov --stats`、`loop escape --list`、`rejections`、`lint-waive kt-situation:`。
- 單位數也核過:型錄真資料的反查單位是 184 個,跟 spec 的數字一致。
- 有 11 對(情境列, 對應檢查)沒有片段,沒有任何一對有會擋的規則。
- 本輪沒有 blocker。有 2 條 major(blocking),其餘 minor。

**r1/r2 修復驗收:**
- 「klib 為主、只有標平台又找不到才丟」這條有修好。
- `isActive` 不會多出 `active`,也成立,但原因是 klib 本來就有 `isActive`,不是 JVM 補來源擋住了(見 finding 3)。
- 「改由要逐段證明」的方向是對的,但對單字片段仍然是空的(見 finding 2)。

---

## Finding 1:停用字 `Dispatchers.IO` 對不到名稱 `IO`,範圍 2 與 S1 的這一道照字面做不出來

- **spec 位置:**〈用詞〉公開名稱「可見寫法」那條、〈範圍〉2 停用字那條、S1 與預期值表的 `IO` 列。
- **問題:**
  - spec 把可見寫法限定在 object 與伴生物件的成員。
  - 但 klib 裡的 `IO` 是頂層擴充屬性:`final val kotlinx.coroutines/IO`,接收者是 `Dispatchers`,不是 `Dispatchers` 這個 object 的成員。
  - 所以 `IO` 沒有可見寫法,它的比對形狀只有 `IO` 與 `IO(`。
  - 停用字 `Dispatchers.IO` 在 `check.py:150` 的 `STOP_TRIGGERS` 裡,永遠不等於這兩個形狀。
  - `Dispatchers.Default` 反而對得上,因為 `Default` 真的是 `Dispatchers` 的成員。
- **佐證(輸入→結果):**
  - 真母體裡 `IO` 標 `無決策`、理由不帶「停用字,不帶決策:」開頭,自檢不會報。
  - 這正好是 spec 要攔的「停用字被默默帶過」。
  - S1 的「`Dispatchers.IO` 對到名稱 `IO` 應報」只能靠測試手造一個有可見寫法的假母體才綠,真資料上不成立。
  - 實作者要嘛加特例,要嘛這道守衛在 IO 上是空的。
- 引句:「例 `Dispatchers.IO` 等於 `IO` 的可見寫法」

file: `/tmp/lumos-seat-work/情境決策點窮舉與壞寫法要叫得出/通才-sonnet/k.klib.api:1057`:`final val kotlinx.coroutines/IO` 是頂層擴充屬性,下一行是 `(kotlinx.coroutines/Dispatchers).<get-IO>`。

severity: major
blocking: 是,照字面實作會漏掉「停用字不准默默標無決策」這條合約,在 `IO` 上守不住,而且 S1 對應的案例在真資料上做不出來。

---

## Finding 2:單字片段與「…」片段讓「改由只在片段層級驗」要嘛空轉、要嘛過不了

- **spec 位置:**〈用詞〉改由的 `規則 <id>` 與 `範本 T<n>` 兩款核對、〈實務隱患〉「改由宣稱擋得住其實擋不住」、〈範圍〉3。
- **問題:**
  - 我用 `check.py` 的 `dt_table` 與 `main_rows` 重數,184 個單位裡有 35 個片段是單一識別字。
  - 單一識別字的例子:`launch`、`onClick`、`collect`、`collectLatest`、`coroutineScope`、`MutableList`、`ArrayList`、`HashMap`、`bigList`、`postDelayed`。
  - 這種片段「整字出現在壞例檔 / 範本小節裡」幾乎必然成立,跟 r2 已否決的「名稱層級背書」沒有差別。
  - 例一:D-12×API-10 片段 `launch`、改由 `範本 T1`。只要 T1 任一 `### 壞寫法:API-10` 小節裡有 `launch` 就過,不管那段到底有沒有「進行中判斷」。
  - 例二:D-5×FLOW-1 片段 `collect`、改由 `規則 kt-nested-collect`。壞例檔裡每個 `collect` 行幾乎都落在被報節點內。
  - 另外 spec 沒說片段在檔裡出現多處時,是「任一處被涵蓋」還是「每一處」。「任一處」會讓短片段更容易空過。
- **反方向的問題:**
  - 另外 29 個片段含「…」,例如 `val a = x.f(…)`、`OkHttpClient.Builder()…build()`、`savedStateHandle[…]`。
  - 這些逐字不可能出現在任何壞例或範本,只能一律掉進 `代碼審`。
  - 例如 `OkHttpClient.Builder()…build()` 明明有會擋的規則 `kt-okhttp-no-calltimeout`,也用不上。
  - 「代碼審變垃圾桶」的風險因此比 spec 預估的大,RETIRE-IF 第二條容易提早觸發。
- 引句:「片段要出現在 `samples/bad/<id>/` 的某支壞例檔裡」

file: `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py:766`:`main_rows` 的第 3 欄(壞寫法形狀)就是片段來源。

severity: major
blocking: 是,約五分之一的單位(35/184)的「驗證」是空的,spec 要保證的合約(改由只在片段層級證明)照字面守不住。

---

## Finding 3:JVM 補來源的「…Kt 門面類別 public static final fun」仍會補進讀取函式與改名假名

- **spec 位置:**〈用詞〉補來源 JVM 清單 ①、S1「isActive 讀取函式不會多出 active」。
- **問題:**
  - spec 同時說「成員與讀取函式不從 JVM 清單補」,又說「…Kt 門面類別裡的 `public static final fun` 名稱」都補。
  - 頂層屬性的 getter 在 JVM 裡正是門面類別裡的 `public static final fun getX`。
- **佐證:**
  - 我照 spec 的跳過條件(synthetic、`$`、`-impl`、底線、內部套件)掃 `…Kt` 門面,klib 沒有的名稱有 22 個。
  - 其中至少這些不是「寫程式時會打出來的名字」:`getJob`、`getCoroutineContext`(LintKt)、`getDEFAULT_CONCURRENCY`、`getRECOVER_STACK_TRACES`、`getDefaultDelay`、`from`(`asCoroutineDispatcher` 的 `@JvmName`)、`flowCombine`、`flowCombineTransform`、`debounceDuration`、`isIoDispatcherThread`、`processNextEventInCurrentThread`。
  - 真名稱是 `combine` 與 `debounce`。
  - S1 的 `isActive` 案例能綠,只因為 klib 已有 `isActive`,並不是補來源擋住了讀取函式。
  - r2 修好的是類別成員,頂層屬性的讀取函式又從門面漏回來。
- **後果:**
  - 這些假名稱要各佔表上一列、標 `無決策`,自檢仍可到 0 問題,所以不擋。
  - 但「公開名稱 = 寫程式時會打出來的名字」的定義被破壞,〈統計〉的公開名稱數也被灌水。

引句:「成員與讀取函式不從 JVM 清單補」

file: `/tmp/lumos-seat-work/情境決策點窮舉與壞寫法要叫得出/通才-sonnet/j.api`:`kotlinx/coroutines/JobKt` 內的 `getJob`、`kotlinx/coroutines/flow/FlowKt` 內的 `flowCombine` 與 `debounceDuration`。

severity: minor
blocking: 否,假名稱可用 `無決策` 帶過,自檢仍可歸零,只是母體被汙染。

---

## Finding 4:`scan()` 改回傳形狀,spec 沒提既有呼叫端與測試

- **spec 位置:**〈範圍〉4「`scan()` 改成多回每筆的起訖行」。
- **問題:**
  - 現有呼叫端與測試都把回傳當三元組拆開:
    - `check.py:1052` 的 `for rule_id, f, _line in got`。
    - `check.py:1093` 的 `for (i, f, _line) in got`。
    - `test_lumos.py:127382` 附近 `t_kotlin_rulepack_security_rules` 的 `for rid, f, line in got`。
  - 直接改成四元組會讓三處 unpack 炸掉。
  - spec 沒列這幾處,也沒列該測試要同批改。
  - 實作者會被測試紅燈打回,所以不危險,只是 spec 漏了。

引句:「`scan()` 改成多回每筆的起訖行」

severity: minor
blocking: 否,既有測試會立刻紅,漏列的是改動清單,不是會漏過去的行為。

---

## Finding 5:`_kt_sit_path_ok(rel)` 簽名放不下 `skip`

- **spec 位置:**〈用詞〉路徑篩選。
- **問題:**
  - 實際的篩選串是 `not _PITFALL_DIFF_TEST_PAT.search(rel) and _stack_changed_ok(rel, skip) and _kt_sit_may_hit(...)`。
  - 其中 `skip`(消費專案裡原封不動的工具檔)在 `_stack_changed_ok` 內生效。
  - `_kt_sit_may_hit` 看的是 hunk 內容,不是路徑。
  - 簽名只有 `rel` 的話,抽出來就少了 `skip` 這一環,或要偷偷在外面保留一份,又變兩份條件。
  - 這與「行為不變」及 S6 的「反查呼叫同一支函式而不是自己組條件」互相拉扯。
  - 解法是 `skip=frozenset()` 預設參數,但 spec 沒寫。

file: `/Users/enzo/harness/lumos-d4-triggers/scripts/lumos:39961`:`_kt_situation_segments` 內的 `todo` 串。

severity: minor
blocking: 否,補一個預設參數即可,現行 S6 的兩個路徑案例都會過。

---

## Finding 6:S7 的綁定測試對新增的反查問題可能看不見

- **spec 位置:**S7 與〈範圍〉4。
- **問題:**
  - 現有 `t_kotlin_rulepack_samples` 在有 ast-grep 時呼叫 `m.check(sg)`。
  - 但它只拿 `sample_probs = [p for p in probs if any(k in p[1] for k in ("壞例","好例","樣本","載入","祖先"))]` 來斷言。
  - 新的反查問題如果訊息不含這幾個字,「真型錄 `--sg` 模式 0 問題」就沒有任何地方斷言。
  - 本機沒有 ast-grep 時只跑靜態那半。
  - spec 只寫了 `[test: t_kotlin_rulepack_samples]`,沒說要擴充這個過濾。

引句:「掃描逾時或失敗 應 報問題而不是通過 [test:t_kotlin_rulepack_samples]」

file: `/Users/enzo/harness/lumos-d4-triggers/scripts/test_lumos.py:126757`:`sample_probs` 的關鍵字過濾。

severity: minor
blocking: 否,補一行過濾或訊息用詞即可,不影響設計方向。

---

## Finding 7:補進 D-4 的 `mapLatest`、`transformLatest` 不會對上 D-4 的證據樣式

- **spec 位置:**〈範圍〉5 第二點、S5。
- **問題:**
  - D-4 的證據樣式主是 `\bflatMapLatest\b\|\?\.cancel\(\)`,例外是 `\.collect\s*\{\|\bChannel\b`。
  - 作者表態「適用、照標準寫法」並指向 `mapLatest` 那行時,樣式對不上,會得到「證據樣式對不上」的提醒。
  - 提醒不擋,但會被記成誤報,汙染 RETIRE-IF 看的「提醒確認」統計。
  - 已先補的 `flatMapConcat`、`flatMapMerge` 也有同樣情況。
  - spec 只說補觸發字,沒說要不要動 D-4 的標準寫法或證據樣式。
  - `situation_sample_problems` 只驗既有樣本,抓不到這件事。

引句:「D-4 照 `mapLatest`、`transformLatest` 的官方文件(新值來時取消前一個轉換,跟 `flatMapLatest` 同類)補這兩個觸發字」

file: `/Users/enzo/harness/lumos-d4-triggers/skills/kotlin-idioms/checks-catalog.md:743`:D-4 的證據樣式欄。

severity: minor
blocking: 否,後果是提醒誤報而不是擋錯,但實作者該決定要不要同批放寬樣式。

---

## Finding 8:`<無片段>` 單位配 `規則` 或 `範本` 時,spec 沒定義怎麼核

- **spec 位置:**〈用詞〉改由四款、〈範圍〉3。
- **問題:**
  - `規則`、`範本` 的核對都以「片段出現在…」為前提。
  - `<無片段>` 沒有片段可比,字面上只剩 `代碼審` 可用(`不是寫法` 已明文禁止)。
  - 真資料的 11 對無片段單位目前都沒有會擋的規則,所以暫時不衝突。
  - 但日後一對無片段的單位若有規則或範本,spec 沒說能不能引用。

引句:「`<無片段>` 單位不准用」

severity: minor
blocking: 否,目前真資料沒有會踩到的單位,屬規格留白。

---

## 逐節

- 白話與使用者原話:已讀,無 finding。
- PRIOR-ART 與 RETIRE-IF:已讀,無 finding。指令引用 `gov --stats`、`loop escape --list`、`rejections` 都存在,數字依據也對得上。
- 〈API 決策點〉歸屬五種的核對邏輯:除 finding 1 外已讀,無 finding。
  - 逐行對照真觸發字:`combine` 被 D-5、D-6、D-35 三列搜到,`merge` 對 D-59,`Channel.BUFFERED` 一族被 `Channel` 觸發字搜到,都能用 `D-n` / `撞名 D-n` / `決策不問` 標完,沒有互相卡死。
- 〈叫不出的壞寫法〉叫得出判定:
  - `TEST-` 兩個路徑的口徑成立。`app/src/test/...` 會被 `_PITFALL_DIFF_TEST_PAT` 擋掉,`androidTest` 不會。
  - 型錄真資料裡 T0 有多個重複的 `### 壞寫法:TEST-6`,不構成問題,但 `TEST-` 多半只能走規則或代碼審。
- 〈回退〉〈天花板〉:已讀,無 finding。

最嚴重 severity:major;blocking 共 2 條(finding 1、2)。
