severity: major

我讀完整份 diff,並把 `kt_situation` 相關測試跑了一遍(97 passed)。測試全綠,但下面第 F1 條的壞行為沒有任何測試守著。

F1. `_kt_sit_hdr_is_class` 把 `class X @Inject constructor(...) {` 與 `class X private constructor(...) {` 的本體判成非類別層
引句:「    return bool(kws) and kws[-1] in ("class", "object", "interface")」
- 白話:r1 為了修 `data class` 後面接 `fun` 的誤判,改成只看宣告頭裡「最後一個」關鍵字。可是 `_KT_SIT_HDR_KW_RE` 把 `constructor` 也列為關鍵字。Hilt 常見的 `class Repo @Inject constructor(...) {` 與 `private constructor` 寫法,最後一個關鍵字就變成 `constructor`,整個類別本體被當成函式內部。
- 後果:類別裡的 `fun` 找不到所屬宣告,`_kt_sit_material` 改回傳整個 class(最多 120 行,超過就退成前後各 20 行)。
  - 證據樣式的第 2 條起改在整個 class 裡找,A 函式的壞寫法可以借 B 函式的 `.await()` 過關,表態對程式變鬆。
  - 同一類別裡相隔 4 行內、不同函式的命中,會併成一段,段身分也跟著變。
- 重現:我用 `python3.14` 載入 `scripts/lumos` 實跑。
  - `_kt_sit_hdr_is_class("class Foo private constructor(val a: Int) ")` 回 False。
  - 對照 `"class A(val x: Int) : B() "` 回 True。
  - 對同一份程式(含 `suspend fun load() = coroutineScope {…}`),`class Repo(private val api: Api)` 的第 9 行材料是 (7,10)。`class Repo @Inject constructor(private val api: Api)` 的第 9 行材料變成 (5,13),也就是整個類別。
- `t_kt_situation_decl_header` 只測了 `data class`、`interface`、`typealias` 三種前綴,沒有 constructor。
- 修法:`constructor`、`init`、`get`、`set` 不該把前面的 `class` 蓋掉。例如只在最後一個是 `fun`、`val`、`var` 時才判成非類別。
severity: major
blocking: 是

F2. 切段快取只寫不清,每個鍵一個大 JSON
引句:「        _home_cache_write("kt-situation", _kt_sit_cache_path(key), {"segs": segs})」
- 快取鍵含範圍兩端、被推版本、型錄列和 `scripts/lumos` 的大小與時間。每次推送或每次改 lumos 都換新鍵,寫進 `~/.cache/lumos/kt-situation/<鍵>.json`。
- 內容含每段的 `_mat`(最多 120 行剝過的程式)和 `_code`。
- `_home_cache_read` 只在讀取時看 TTL,過期檔從不刪,所以目錄會一直長。
- 全域規則「修完要對大型輸入跑一次效能與記憶體檢查」和「暫存清理」都針對這種情況,diff 沒有上限或清掃。
- 我實跑時目錄裡只有 7 個檔,但沒有任何機制保證它不長。
- 修法:寫入時順手刪超過 TTL 的檔,或限制檔數。
severity: minor
blocking: 否

F3. 情境段放行混進新增告警閘的統計與提示
引句:「    what = "這個情境段(整段不核表態對程式)" if str(key).startswith(_KT_SIT_WAIVE_PREFIX) else "這條新增告警"」
- 情境段放行寫進同一個 `.lumos/lint-waivers.json`。`doctor` 的「新增告警閘的放行狀況」(`file: scripts/lumos:4189` 附近)直接印 `放行清單有 {len(_wv)} 條`。
- 這個數字會把 `kt-situation:` 的段放行也算進去,標題仍寫「新增告警閘」。
- `_lint_waivers_ai_pending` 在推送前小結(`file: scripts/lumos:72211`)的計數也一樣,而且是整包計入。
- 這不會擋住推送,但新增告警閘的放行率會被情境題灌水或稀釋,兩邊互相誤判。
- 放行檔壞掉時,新增告警閘的 `waiver_err` 擋下與情境題的「無法驗證」擋下會同時觸發,兩套訊息都叫人先修同一個檔。
- 修法:`doctor` 與小結按 `kt-situation:` 前綴分開計數,或分兩個檔。
severity: minor
blocking: 否

F4. 放行出口提示只帶第一個問題的那一段,也沒提醒 AI 可以自己放行
引句:「    sg0 = next((sg for sg in segs if sg["seg"] not in waived and sg["seg"] in ";".join(probs[:1])), None)」
- 擋下訊息只印第一個問題那一段的放行指令。最多 6 個問題各屬不同段時,要擋、放、再擋、再放,一次一段。
- 缺段或缺列(AI 只要補答就能過)的擋下訊息也附上「整段略過」的出口。這等於教 AI 用放行代替作答。
- 放行會記成 AI 放的並留帳,所以不算破口,只是引導偏了。
- 修法:出口只掛在證據樣式對不上這類誤擋上,缺段缺列不給。
severity: minor
blocking: 否

F5. `LUMOS_KT_CATALOG` 的「只在測試執行器生效」判斷靠 TMPDIR 目錄名,任何人都能偽造
引句:「    return Path(os.environ.get("TMPDIR") or "").name.startswith("gctl-run-")」
- 設 `TMPDIR=/x/gctl-run-a` 加 `LUMOS_KT_CATALOG=<永不觸發的小型錄>`,正式推送也會換成那份型錄,整個情境題消失。
- 這個 repo 的威脅模型是單人加 AI 依序操作,不防刻意偽造,所以降為 minor。
- 但 r1 D4 的目的就是「正式路徑不能被這個變數繞過」,現在只防意外,不防偽造。修法:把「是測試執行器」的標記改成執行器自己設的專用環境變數。
severity: minor
blocking: 否

F6. `_KT_SIT_ROW_RX` 變成死碼,與 `_kt_sit_rows_rx` 重複
引句:「_KT_SIT_ROW_RX = [(r["id"], re.compile("|".join(_kt_trigger_re(t) for t in r["triggers"])))」
- 這是 diff 裡未改動的上下文行。
- r1 D9 新增了 `_kt_sit_rows_rx`(三元組,含預篩集合)。
- 載入時的 `_KT_SIT_ROW_RX` 只剩 `if not _KT_DT_ERR and _KT_SIT_ROW_RX:` 一處用來判斷真假,等於為了判斷「有沒有觸發字」多編一次所有列的正規式。
- 兩份各自建構觸發字,日後改 `_kt_trigger_re` 或預篩規則容易只改到一邊。
- 修法:改成 `bool(_kt_sit_rows_rx(_KT_DT_ROWS))`,刪掉這個常數。
severity: minor
blocking: 否

總結:最嚴重是 F1(Hilt 與 `private constructor` 類別的段材料誤擴成整個類別,表態對程式變鬆,且沒有測試),會擋 1 條。

**審查範圍說明**
- `_load_hook_file` 搬前:全庫三個呼叫點都在它之後才執行,載入順序沒問題。
- `_gate_failopen` 新呼叫者:簽名與先例相符,沒找到問題。
- check.py 新 `dt_table` / `dt_row`:未發現與既有呼叫者衝突。
- `_kt_sit_may_hit` 預篩:我構造的幾種觸發字開頭都沒找到漏判的輸入。
- 我在 `/tmp/lumos-seat-work/` 建的臨時檔已用字面路徑刪除。
