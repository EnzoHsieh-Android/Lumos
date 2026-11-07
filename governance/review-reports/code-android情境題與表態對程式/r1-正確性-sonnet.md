severity: major

審查對象是 diff 檔 `r1-snapshot-甲乙.patch`。實驗在 `/tmp/lumos-seat-work/code-android情境題與表態對程式/正確性-sonnet/r`,我沒動 repo。臨時目錄請編排者收貨後刪。

## 實驗紀錄(鏡頭 2)

- **測試檔**:`app/Repo.kt`,有 `load()`(`coroutineScope` 包兩支互不依賴的 `async`)和 `other()`(`supervisorScope`)。
- **用的型錄**:真型錄,56 列。
- **`lumos pitfalls --diff HEAD~1..HEAD`**:印出兩個情境段。`[kt 情境段] ff9e35d000b38701 app/Repo.kt:3-9 候選列 D-1、D-8`;`[kt 情境段] 97263259124b0eaf app/Repo.kt:11-16 候選列 D-9`。
- **`--dispositions-template`**:`kt-situation` 預填 `status: satisfied`,每段每列 `applies: null`。
- **表態對了放行**:D-1 答 main、證據指第 7 行(`val a = async {`),D-8 與 D-9 答不適用。`code-loop dispositions` 寫入成功,`code-loop check` 輸出「OK——可以推……3 題表態核對過」。
- **證據樣式不合擋**:D-1 的證據改指第 6 行(`coroutineScope` 那行)。`code-loop check` 輸出「段 ff9e… 的 D-1(main)證據樣式對不上:第一條 `\basync\s*\{` 不在 evidence 那一行」。
- **缺段擋**:只答第一段。輸出「缺段 97263259124b0eaf(app/Repo.kt:11-16,候選列 D-9)」。
- **偽造自動 na**:把 `kt-situation` 寫成 `{"status":"na","auto":true}`。輸出「工具判它適用,但表態是自動填的 na——要人答」,擋住了。

## 發現

**F1 · 宣告頭視窗把函式內的區域 val 誤當成頂層宣告,段材料縮成一小截,誤擋並把一個函式切成多段**

severity: major
blocking: 是
位置:`scripts/lumos:38830`(`_kt_sit_levels`)。
引句:
「hdr = stripped[max(last, pos + k - 300):pos + k]」

成因:判斷大括號是不是類別本體時,往前看的視窗從上一個 `{`、`}`、`;` 之後算起。檔案裡若有一行沒有大括號的 `data class Ui(val a: Int)`、`typealias` 或 `interface Foo`,它會落進下一個頂層 `fun ... {` 的視窗。那個函式的本體就被當成「類別層」,函式裡行首的 `val`、`var` 因此被當成宣告起點。

最小重現(已實跑):

```
package app

data class Item(val id: Int)

suspend fun loadAll2(api: Api, ids: List<Int>): List<Int> {
    val deferred = ids.map { id -> async { api.load(id) } }
    val results = deferred.awaitAll()
    return results
}
```

- 對照組:拿掉 `data class` 那行。段材料是 `[3,7]`(整個函式),D-3 答 main、證據指 `awaitAll` 那行(第 7 行)時通過。
- 有 `data class` 時:材料變成 `[7,8]`,只剩 `val results = ...` 那一句。同樣答案被擋:「段 11777c4681f1d700 的 D-3(main)證據樣式對不上:`\basync\b` 不在段材料(第 7 到 8 行)」。程式寫得對卻被擋,作者只能把那列改答「不適用」。
- 同一個機制的另一個後果:表達式本體的函式(`fun f() = coroutineScope { ... }`)裡,連續幾個區域 val 各自命中不同觸發字(`Semaphore`、`withPermit`、`awaitAll`),會各自成一段。每段材料不同,所以沒有被併段。實測 `Par.kt` 的第 6、7、8 行變成三個獨立的段,作者要逐段答。

測試缺口:`t_kt_situation_segments` 和 `t_dispositions_situation_evidence_pattern` 的樣本檔都沒有「函式前面有一行沒大括號的 class/object/interface/typealias」。把 `_KT_SIT_CLASS_HDR_RE` 的判斷整個改成永遠 True,現有測試仍會綠(推測;我沒有實際翻紅)。

**F2 · 預設型錄路徑在消費專案找不到,情境題在實際目標專案裡永遠不出**

severity: major
blocking: 是
位置:`scripts/lumos:38125`。
引句:
「_KT_CATALOG_DEFAULT = Path(__file__).resolve().parent.parent / "skills" / "kotlin-idioms" / "checks-catalog.md"」

成因:`scripts/lumos` 是以複本放進消費專案的(`_VENDORED_TOOLKIT` 列了它)。`skills/kotlin-idioms/checks-catalog.md` 不在白名單裡,不會跟著複製。複本裡 `Path(__file__).parent.parent` 是消費專案根,那裡沒有 `skills/`。

實跑(已 `env -u LUMOS_KT_CATALOG`,把 `scripts/lumos` 複製進臨時 repo 的 `scripts/lumos`):
- `lumos pitfalls --diff` 印「提醒:Kotlin 型錄的情境決策表讀不到 …/r/skills/kotlin-idioms/checks-catalog.md(FileNotFoundError),這次不出情境題(工具鏈安裝不完整?)」。
- `--dispositions-template` 也印同一行,樣板裡沒有 `kt-situation`。
- 結果:Android 應用專案的推送完全不會被問情境題。每次 kt 改動還會多出一行誤導的「安裝不完整」提醒。

在 `~/harness/lumos-toolchain/skills/kotlin-idioms` 找得到型錄,但 lumos 的 `_lumos_src()`(`scripts/lumos:33059`,讀 `$LUMOS_HOME` 或 `~/harness/lumos-toolchain`)沒被用上。

測試缺口(鏡頭 1 特別查的項目):`_isolate_environment` 讓整輪測試都設了 `LUMOS_KT_CATALOG`。`_sit_run` 也總是顯式帶 env。`t_kt_catalog_evidence_patterns` 是用 `Path(GRAPHCTL).resolve().parents[1] / _KTCAT_REL` 直接讀檔,不走預設路徑。所以預設路徑沒有任何測試走到。把它改成任何錯路徑,測試都照綠。對 S1「型錄在就出題」這條驗收,這是假綠。

**F3 · 情境段計算在 git 失敗時靜默放行,和核對「無法驗證就擋下」的合約矛盾**

severity: minor
blocking: 否
位置:`scripts/lumos:38990`(`_kt_situation_segments`)。
引句:
「hunks = _kt_sit_hunks(repo_root, diff_range) or {}」

`_kt_sit_hunks` 在 git 回非零時回 `None`,這行把它吞成 `{}`,於是切不出任何段,`_kt_sit_verdict_one` 把這題視同不適用。實跑 `_kt_situation_segments(".", "deadbeefdeadbeef..HEAD", sha)` 回 `[]`,`_kt_sit_verdict_one` 回 `None`(過)。`_kt_situation_apply` 的註解寫「算不出來就判無法驗證、擋下」,但它只接 `OSError` 和 `TimeoutExpired`,git 錯誤碼不在其中。`棧別提問表態閘.md` 第 40 行的 KEY 也說「核對每題包例外→無法驗證擋下不 fail-open」,這裡和它不一致。實務上 pitfalls 先用同一範圍算過,錯誤不容易只在核對時出現,所以只標 minor。

**F4 · 大量命中的檔案(產生碼)拖慢 pitfalls,且段數沒有上限**

severity: minor
blocking: 否
位置:`scripts/lumos:38988`(`_kt_situation_segments` 一帶)。
引句:
「if not rows_rx or not diff_range:」

新增 2 個各 20000 行、每行都含 `coroutineScope` 的 .kt,`pitfalls --diff` 實測 24 秒,印出 20500 個情境段。換成不會命中的型錄是 7.5 秒,所以新增約 16 秒。推送前核對還會在 at_sha 上再算一次,而時間預算只在題與題之間檢查。作者要逐段答 20500 段,實際上做不到。

**F5 · 真型錄測試寫死 56 列**

severity: minor
blocking: 否
位置:`scripts/test_lumos.py:126909`。
引句:
「check("真型錄讀得出、56 列、沒有問題", err is None and len(rows) == 56, str(err))」

型錄規定「列編號只准往後加」,每加一列這支測試就紅。它測的重點是「真型錄讀得出、沒有問題」,56 這個數字不是行為。

## 沒找到問題的部分

- **切段邊界**:行號差 4 併、差 5 分、40 行上限、跨函式不併、CRLF、純刪行、只改縮排、import 行,測試和我的手跑都對得上。
- **剝註解**:巢狀註解、`${…}`、`'"'`、raw string 尾端多的引號,測試都有覆蓋,我也走過一遍。
- **證據樣式本身**:證據樣式的正規式裡沒有任何一條帶引號、斜線或 `$`,所以不會被「字串已清空」影響。
- **舊測試的型錄隔離**:`_isolate_environment` 的做法沒有讓舊測試變假綠,除了 F2 那條預設路徑。
- **推送閘判定**:沒有 kt 改動時,`"kt" in meta` 為假,判定完全不變。`gate` 為 high-only 或 off 時,在核對前就回傳,照既有規則不跑。
- **表態檔相容**:新舊表態檔互讀可行。舊記錄沒有 `kt-situation` 會得到「缺表態」,這是預期的重表態。

## 圖譜鏡頭

- **`棧別提問表態閘.md`**:會牴觸第 40 行的 KEY(F3)。第 35 行「適用範圍算在 merge-base..at_sha」不受影響,因為核對用的是同一個 `disp_range`。另有兩處不影響:第 43 行的「觸發字一律不分大小寫」,情境題用 `(?-i:…)` 局部關掉,該筆記的 WHY 已註明;`auto` 偽造被擋(實驗已驗)。
- **`pitfalls-code-loop.md`**:不影響。
- **`kotlin規則包.md`**:F2 影響它宣稱的「型錄隨工具鏈安裝」。消費專案的複本讀不到型錄。

## 角色卡

- **be-api-compat(對外相容)**:
  - `pitfalls --json` 只在有段時才多 `situation_segments`,是加欄位,不破壞。
  - 表態記錄的 `kt-situation` 形狀是新的(`segments`)。舊版工具對它回「不是題目表裡的 id」,新版工具讀舊記錄回「缺表態」。屬於預期的重表態,沒有找到相容破口。
- **be-authz(授權)**:這是本機 CLI,沒有端點。「誰能動這筆資料」對應到「作者能不能自己宣告不適用」。偽造 `auto:true` 被擋;全答 `applies:false` 能過,但這是計劃明文的設計(盲判在下一次)。

總結:最嚴重是 F1、F2 兩個 major(宣告頭視窗誤判造成誤擋與切碎,預設型錄路徑在消費專案找不到導致整題不出),會擋 2 條。
