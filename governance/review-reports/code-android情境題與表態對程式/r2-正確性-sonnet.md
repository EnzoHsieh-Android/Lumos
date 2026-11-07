severity: major

**審查範圍:** 讀完整份 r2-repair-甲乙.patch 與 r1-intake.md。我在 `/tmp/lumos-seat-work/code-android情境題與表態對程式/正確性-sonnet/` 造了小 repo 實跑 `pitfalls --diff` 與 `code-loop dispositions` / `code-loop check`。另用 `git archive` 的複本跑 `-k kt_situation`(97 個斷言全過)並各改壞一次。沒有改 repo 本體,暫存已用字面絕對路徑刪除。

**修補三問摘要**
- 原問題修好(重現再跑):
  - 段放行後同段改一行:段身分 `4d6c273316354666` 變 `471c80eeabf5cabc`,放行失效,又被擋。
  - 型錄改版後快取:改 D-1 觸發字,快取換新鍵、切段結果跟著變。
  - 型錄檔不在:只提醒、記一筆 fail-open 帳、rc 0。
  - 型錄在但證據樣式編譯不過:擋下、rc 1。
  - 檔名含空白、中文、單引號:正常切段。檔名含 TAB:判無法驗證。
  - 300 檔乘 290 行(本案改過的路徑,實測):切段約 0.5 秒。
- 修補帶進新錯:F1。
- 同形狀別處:F1 的詞表只有 `_kt_sit_levels` 一處用,沒有別處。

**F1 宣告頭改用「最後一個關鍵字」後,Hilt 常見寫法 `class X @Inject constructor(...)` 被誤判成非類別,證據樣式的「段材料」範圍從函式放大成整個類別,壞寫法被放行**

severity: major
blocking: 是

引句:「kws = re.findall(_KT_SIT_HDR_KW_RE, "".join(flat))」
引句:「return bool(kws) and kws[-1] in ("class", "object", "interface")」

- 根因:`_KT_SIT_HDR_KW_RE` 的詞表含 `constructor`。宣告頭 `class A @Inject constructor(` 拿掉括號後,最後一個關鍵字是 `constructor`,不在 class/object/interface 裡,於是 `_kt_sit_hdr_is_class` 回 False。
- 這是 D8 修補自己引入的:舊的 `_KT_SIT_CLASS_HDR_RE` 只要視窗裡出現 `class` 就算類別,這個寫法原本判得對。
- 直接呼叫 `_kt_sit_hdr_is_class` 的結果:
  - `class A @Inject constructor(private val a: A) : VM() ` → False
  - `class A private constructor() ` → False
  - `class A(val a: Int) ` → True
- 類別本體被當成非類別層後,類別裡的 `fun` 不被認成宣告起點。`_kt_sit_material` 往回找,找到類別頭那一行(第 3 行,在 `class UserViewModel @Inject constructor(...)` 上),把整個類別當段材料。
- 最小重現(repo 在 `/tmp/lumos-seat-work/code-android情境題與表態對程式/正確性-sonnet/ctorA` 與 `ctorB`,已刪,檔案內容見下):
  - 同一個 VM.kt:`good()` 有 `coroutineScope`、兩個 `async`、`a.await()`;`bad()` 有 `coroutineScope`、`async`,沒有 `.await()`。
  - 只有類別頭不同:
    - ctorA:`class UserViewModel @Inject constructor(private val api: Api) : ViewModel() {`
    - ctorB:`class UserViewModel(private val api: Api) : ViewModel() {`
  - 用真型錄 D-1 證據樣式,D-1 答 main、evidence 指 `bad()` 裡 `val a = async` 那行(第 14 行):

| | 段材料 | `code-loop check` 結果 |
|---|---|---|
| ctorB | `[12,17]`(只有 `bad()`) | rc 1,「`\.await\(\)` 不在段材料(第 12 到 17 行)」 |
| ctorA | `[3,18]`(整個類別,`good()` 的 `.await()` 也算進來) | rc 0,「表態閘:3 題適用、3 題表態核對過」 |

- 連帶影響:ctorA 兩個段的段身分都綁整個類別,類別裡任何一行改動都讓所有段身分失效,舊表態和段放行跟著作廢。
- 長建構子(12 個參數,約 500 字)的 ViewModel 還有第二個原因:視窗只回看 300 字(`pos + k - 300`),`class` 字樣會被截掉。這個截斷是舊程式就有的,但 D8 號稱修宣告頭視窗,沒補。
- 測試為什麼沒抓到:`t_kt_situation_decl_header` 只造 data class、interface、typealias 三種前導。我沒有改壞測試,理由是現況本身就帶這個錯,97 個斷言全綠。要補一支 `@Inject constructor(`、`private constructor(`、`constructor(` 的案例,加上一支長建構子案例。
- 修法方向:`constructor` 只在它是宣告頭第一個關鍵字(次建構子)時才當結論;在 class 之後出現的 `constructor` 要略過。視窗改成從上一個 `{ } ;` 起算,不要固定 300 字。

**F2 切段快取只靠讀取時看 TTL,沒有任何清除,而且單檔可到數十 MB**

severity: minor
blocking: 否

引句:「_home_cache_write("kt-situation", _kt_sit_cache_path(key), {"segs": segs})」

- 實測:這台機器 `~/.cache/lumos/kt-situation/` 已有 7 個檔,其中 13.7MB 和 20.3MB 各一(22200 段、33000 段,連 `_mat`、`_code` 全文都存),合計約 66MB。這些不是我的 repo 產生的。
- 鍵含 lumos 檔的 mtime,每次工具鏈更新就讓整批舊檔變孤兒。TTL 只在 `_home_cache_read` 裡比對,過期檔不會被刪。
- 每個推送(新 sha)多一個檔,沒有上限也沒有清理,對照使用者 2026-10-12 對暫存累積的裁示。
- 建議:寫入時順手刪該目錄超過 TTL 的檔,或限制單檔段數與總量。

**F3 `t_kt_situation_segments` 在這輪修補後變得很慢,離逾時上限很近**

severity: minor
blocking: 否

引句:「        if cat is not nowhere:
-            continue      # 樣板與 check 那半只跑讀不到那一案」

- 原本「型錄格式壞」那案跳過樣板與 check 兩段,現在兩案都跑,每案多三個 lumos 子行程。
- 實測同一支測試:125.2s(同時有別的會談在跑,機器有負載)和 80.5s,上限 180s,執行器標「餘裕 1x/2x」。
- 負載再高一點就會在 CI 逾時而紅,而且是測試本身的問題。
- 建議:把兩案的 `code-loop dispositions` + `check` 合併成一次,或把格式壞那案移到行程內呼叫 `_dispositions_verdict`。

**測試獨立判準(依 03-寫回圖譜.md〈實作測試品質〉)**
- 快取鍵的衍生資料失效有被守住,但是意外守住的。我把鍵裡的 `rows` 和 lumos mtime 拿掉(其他不動),只有 `t_kt_situation_catalog_location` 的 D4 對照紅(同一 repo 同一 sha,換成「永遠不亮」的型錄,拿到舊段)。
  - 這是附帶覆蓋,不是專為「型錄改版要換快取」寫的測試。
  - `me`(lumos mtime)那一項單獨拿掉沒驗證。
  - 沒有開 finding,因為至少有一支會紅;建議加一支專門的。
- D1 `_SIT_NAMED` 和 D8 的預期值是手算,不呼叫被測函式,判準獨立。
- 該案也說明 F1 為什麼是新洞:三種前導之外的宣告頭完全沒案例。

**資料狀態五問**
- 新舊互讀:快取鍵含 `_KT_SIT_CACHE_SCHEMA` 與 lumos mtime,舊快取不會被誤讀。舊表態帳的答案形狀沒變;但 D8 與 F1 會改段身分,舊答案要重答,屬預期。
- 寫一半:快取走 `_home_cache_write` 原子換名。放行檔壞掉會判無法驗證、擋下,有測試。
- 時間:`deadline` 只在檔與檔之間檢查,單一巨大檔切段不會被打斷。我測 6 萬次觸發字擠在一行是 9.8 秒,未超過預算,所以沒開 finding。
- 不可逆:AI 放的段放行只印 ⚠,不擋;這跟新增告警閘既有做法一致,不算本輪新增問題。

總結:最嚴重是 F1(Hilt `@Inject constructor` 讓類別被誤判,段材料放大成整個類別而放行壞寫法,可當場重現),會擋 1 條。
