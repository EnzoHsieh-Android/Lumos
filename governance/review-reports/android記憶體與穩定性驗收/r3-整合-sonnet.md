severity: blocker

這份審查是靜態讀 spec、對照 repo 程式與固定席節點,沒有實跑收集腳本或 Maestro。

## 逐節判

**〈白話〉到 WHY 第 25~30 行(原生 / Java 洩漏判定、快照規則)**

severity: major
blocking: 是,首次接真實專案時「沒人指著的原生記憶體」會因機制假設不成立而誤報,而且預設門檻 0 位元組讓誤報直接變紅。
引句:「程式裡已經沒有任何指標指著的 malloc 區塊,第三方 SDK 的 Java 物件被丟掉卻沒呼叫 release 時,它配的原生記憶體就落在這裡」
情境:Android libmemunreachable 的 README 只列出 globals(.data/.bss)、各執行緒暫存器與堆疊當根集合,Java/ART 堆積不在其中(我讀官方 README 的結果,它沒明講 Java 長整數欄位怎麼處理,所以標 ⚠)。第三方 SDK 最常見的寫法是 Java 物件的 `long nativePtr` 欄位持有原生指標。照這個根集合,這種區塊即使 SDK 物件還活著、正在使用,也會被掃成「沒人指著」。
後果有兩個:
- 暖機之後才第一次建立的合法原生快取或單例,會讓兩次掃描的差值大於 0。預設門檻 0 位元組,第一個真實專案可能直接紅。
- 實驗室 spike 的洩漏樣本是 malloc 後直接丟掉指標,測不出這個差別。spec 的〈代價〉只寫了 SDK 在原生側自己留清單的漏報,沒寫這個誤報方向。
佔位:REVISIT 2027-04-30 才確認真實專案,但 S1 / S18 的人工驗收沒有「Java 物件持有 long 控制代碼、仍在使用」的對照組。
⚠
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/android記憶體與穩定性驗收/r3-snapshot.md:21`

severity: major
blocking: 是,R8 建置(Macrobenchmark 建議的 benchmark 型態通常開 minify)下,預設排除清單擋不到 `androidx.`、`kotlin.`,會製造假紅,而且診斷沒有還原類別名的步驟。
引句:「預設不算 java.、javax.、kotlin.、android.、androidx.、dalvik.、libcore.、sun. 開頭的類別與基本型別陣列」
情境:`java.`、`android.` 是平台類別,不會被混淆。`androidx.` 與 `kotlin.` 是被一起編進 App 的函式庫,R8 會把它們改名成 `a.b.c`,於是前綴比對失效。協程、Compose 的內部物件增長會被當成洩漏列出。spec 只在〈代價〉裡說「宣告的類別要寫 keep 規則或混淆後的名字」,涵蓋 `instances`,沒涵蓋 `java_growth` 的排除清單。L3 / skill 也沒有拿 mapping 檔還原類別名的步驟,所以接手的人看到 `a.b.c` 增長 5 個,無從查起。
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/android記憶體與穩定性驗收/r3-snapshot.md:26`

**WHY 第 31~32 行與 S11 / S19(驅動、來源狀態)**

severity: blocker
blocking: 是,規格自相矛盾,S19 在按規格實作下不可能通過,而且 exits 會在它最該判不過的情境變成「跳過」。
引句:「不是就把 driver 來源記成 failed,整份結果的每一條都列成跳過」
情境:量測輪中 App 崩潰或被殺時,UI Automator 找不到元件(輸出有 `FAILURES!!!`),Maestro 回傳碼非 0。依這條,driver 來源就是 failed,連 exits 與 pids 也全列成跳過。這和 S19「am crash 讓 App 在量測輪中崩潰時,exits 應列成沒過」直接衝突,和 S5「三次 pid 不一樣時列成沒過」也衝突。「崩潰類事件」這一類在真實專案裡幾乎都會同時弄壞驅動。結果是設計要抓的案例,輸出的是「沒判」,而且回 0。
修法方向:driver failed 時,exits、pids 與 strictmode 仍要判,只有依賴量測輪完整性的 native、java_growth、peak、frozen 才跳過。
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/android記憶體與穩定性驗收/r3-snapshot.md:32`、`/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/android記憶體與穩定性驗收/r3-snapshot.md:116`、`/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/android記憶體與穩定性驗收/r3-snapshot.md:124`

severity: minor
blocking: 否,有環境變數可補,但接手的人會撞到。
引句:「驅動指令例:UI Automator 用自己測自己的測試 `adb shell am instrument -w -e class」
情境:`device`(adb 序號)只約束收集腳本自己呼叫的 adb。驅動指令是使用者寫的字串,範例沒帶 `-s`,多台裝置時會報 more than one device。Maestro 也需要 `--device`。spec 沒說收集腳本要不要匯出 `ANDROID_SERIAL` 給驅動子程序。
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/android記憶體與穩定性驗收/r3-snapshot.md:66`

**〈這次要改到的地方〉與資料怎麼流(門檻、收據、消費專案接入)**

severity: major
blocking: 是,消費專案若只有一般 androidTest(targetPackage 是 App 本身),照規格會每次啟動就重啟 App,spec 卻沒有範本或接入說明。
引句:「UI Automator 驅動必須是自己測自己的 instrumentation」
情境:Macrobenchmark 模組預設是 self-instrumenting,所以這條在實驗室成立。真實專案若要用 UI Automator 當驅動,得自己新建一個 self-instrumenting 的測試模組,並寫出讀取 `cycles` 參數的測試類別。〈這次要改到的地方〉只列收集腳本、查詢範本、錄製設定、skill 與實驗室,沒有給消費專案的驅動測試範本或接入步驟。Maestro 那側也沒有 flow 範本,`repeat: times: ${CYCLES}` 要自己摸索。三個月後接手的人會卡在這裡。
補充:Maestro 路徑可寫得出來,`stopApp: false` 與不用 `launchApp` 是對的,`-e CYCLES=` 可傳入 flow。但範本與起點畫面約定得由消費專案自己補。
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/android記憶體與穩定性驗收/r3-snapshot.md:31`、`/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/android記憶體與穩定性驗收/r3-snapshot.md:82`

severity: major
blocking: 是,現行程式在沒有 results_dirs 時直接回「沒接」,條款有寫但實作點散在三處,漏改任一處就得回 2 或靜默不判。
引句:「`.lumos/macrobench.json` 有 `stability` 段時,`results_dirs` 可以不填(只做穩定性的專案);兩個都沒有才算沒接」
情境:現況是 `_macrobench_config` 在沒有非空 `results_dirs` 時回錯誤(`macrobench.json 要有 results_dirs`),`_macrobench_mode` 在 `cfg is None` 時先印「沒接」就 return 0。同一個函式裡的 `_macrobench_collect` 與 `--update-baseline` 也假設有 `results_dirs`。〈這次要改到的地方〉有寫這一條,但沒寫 `--update-baseline`、基準比對在空目錄時的行為。另外,門檻檔驗證與判定現在是先於 `cfg` 判斷的,但輸出格式 `_macrobench_print_thresholds` 直接取 `r['metric']`、`r['stat']`(check 條目沒有這兩個鍵),漏改會 KeyError。
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos:39404`、`/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos:39741`、`/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos:39717`

**收據**

severity: minor
blocking: 否,不影響首版跑通,但「增減由 lumos 算」會讓接手的人找不到實作點。
引句:「兩份快照各寫一條查詢,增減由 lumos 算」
情境:`android-receipt-rerun.sh` 只逐條比對自己的 `expect`,沒有跨查詢算差值的機制,也沒有 lumos 指令讀收據算差。實際上能驗的只有每份快照單一類別的實例數,java_growth 的「增加量」收據驗不到。另一點:`expect` 用 `partition(':')` 取第一欄鍵,類別名裡若出現冒號會被截,Java 類別名一般沒有,所以不是 blocker。
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-receipt-rerun.sh:67`

**圖譜節點與既有決定**

severity: minor
blocking: 否,衝突已被 spec 自己標出來並計畫處理。
引句:「[[Projects/Android逐層診斷_計劃]] 的 S6(沒有保存裁定時停在 L2)與「L3 預設關閉」記成被本計劃的保存規則取代」
情境:S6 是 manual 型驗收,不是綁測試的合約,取代它沒有守衛會翻紅,但要在該節點補 `[status:superseded]` 與 `被取代`。`Systems/macrobenchmark-adapter` 沒有登記合約(`lumos contracts` 回「沒有登記任何動了會壞的合約」),新增 `--stability` 不會破壞它宣稱的行為。「不接裝置」照留,收集腳本掛在新家 `Systems/android-stability-collector`,責任劃分一致。
另外 [[Projects/Android效能判定統計化_計劃]] 的第 6 條在現行目錄已存在,spec 說「加第 6 條」其實是核對,不是新增。
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos:31927`

severity: minor
blocking: 否。S12 的登記要求與現有測試相容。
引句:「[S12] 當收集腳本、兩支查詢範本與錄製設定加進工具鏈時,應帶 SPDX 檔頭、登記在工具組複製清單、跟其他範本一起進消費專案」
情境:`_VENDORED_TREE_FILES` 是精確清單,有一支測試逐檔比對,漏登記會翻紅。spec 寫了登記,但「錄製設定」的副檔名(.pbtxt 或 .cfg)沒定,SPDX 檔頭對沒有註解語法的設定檔需另處理。
佐證 file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos:31926`

**固定席節點**

- `Systems/macrobenchmark-adapter`:已讀。不影響它宣稱的行為。`check` 欄位是選填,沒寫的條目走原驗證,S13 有綁測試。它宣稱的「不接裝置」不被破壞,因為接裝置的是新範本不是 Lumos。需要在它的責任欄補一句「讀收集結果檔判記憶體與穩定性」,spec 已列。
- `Projects/Macrobenchmark驗收門檻_計劃`:已讀,不影響。S5 的回 2 條件只對沒寫 `check` 的條目套用,spec 已列補句。S3 的 `device_model` 篩裝置行為保留。
- 其餘連結節點(`Android介面寫法分流_計劃`、`Android診斷證據接入_調研`):已讀,無 finding。

總結:最高嚴重度 blocker,blocking 共 5 條
