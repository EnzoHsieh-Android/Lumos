severity: major

## F1 範本腳本說 stability 是 run 目錄下的子目錄,收集腳本做不到
severity: major
blocking: 是(照字面做不出 S12 要的目錄形狀,judge 找不到記憶體輸入)
引句:「底下的 ui、visual、macrobench、stability 四個子目錄」
spec 段落:〈資料怎麼流〉第 1 步與 S12。
問題:`android-stability-collect.sh` 的 run-id 只收 `[A-Za-z0-9._-]+`,不能帶斜線。它把 `stability.json`、`logcat.txt`、`*.pftrace`、`record.pbtxt` 直接寫進 `.lumos/artifacts/android/<run-id>/` 根目錄,沒有 `stability/` 子目錄。要放進子目錄只有兩條路,spec 都沒選:改收集腳本(它已過五輪代碼審,spec 又說「借用」),或收完再搬檔。搬檔的話,`macrobench --stability <路徑>` 與 judge 的讀取路徑也要跟著定。收集腳本還有一條:run 目錄裡已有 `stability.json` 就 die。腳本若先 `mkdir` 或預先放了東西,這條檢查要不要放行,spec 沒說。
file: `scripts/templates/android-stability-collect.sh:382-384`(目錄與重用檢查)、`scripts/templates/android-stability-collect.sh:547`(結果檔寫在根目錄)

## F2 Macrobenchmark 這塊沒有「這一次跑」的輸入,會吃到上次留下的舊結果
severity: major
blocking: 是(舊的效能結果會被當成這次的;judge 沒有可讀的 `macrobench/` 目錄)
引句:「專案的 Macrobenchmark(預設 20 輪)跑完,`lumos macrobench --json`」
spec 段落:〈四塊〉毫秒類效能列、〈資料怎麼流〉第 1 步。
問題:`lumos macrobench` 沒有 run 目錄參數。它從 `.lumos/macrobench.json` 的 `results_dirs`(Gradle 的產出目錄)用 `_macrobench_collect` 收檔。spec 說原始輸出放 run 目錄的 `macrobench/`,但這個目錄沒人讀,哪個程式把結果搬進去也沒寫。Macrobenchmark 這次沒跑成時,`results_dirs` 裡上次的舊 JSON 還在,照樣被判成「這次」的 regressions 與門檻結果。spec 沒要求跑前清空,也沒要求檢查結果檔時間。毫秒類雖然只提醒,但記憶體類門檻的 `scenario` 與裝置條目是共用的,notices 會誤導人。
file: `scripts/lumos:40217`(`_macrobench_collect(repo, cfg)` 不帶 run 目錄)、`scripts/lumos:40195-40240`

## F3 judge 讀的「原始輸出」沒定義格式,S3、S4、S6 寫不出會紅也會綠的測試
severity: major
blocking: 是(條款文字要的輸入根本沒落地)
引句:「應在回傳碼是 0、報告裡至少一個測試案例而且沒有失敗時才算這支 flow 過」
spec 段落:S3、S4、S6、〈資料怎麼流〉第 2 步。
問題:judge 只「讀四塊的原始輸出」,但回傳碼不是檔案,spec 沒說腳本把 `maestro` 與 `visual-check.sh` 的回傳碼存到哪、用什麼格式。以下 UI 流程的資料也都沒定義:
- 第一次失敗與重跑各留哪份 junit。同名 `<名>.xml` 會被覆蓋,judge 就看不出「第一次沒過、重跑過」,無法標不穩定。
- 「工具沒跑成」(S6 的找不到 maestro、裝置斷線)和「這塊根本沒被跑」怎麼分。S6 只說「輸出檔不在」,但 `visual` 沒設定時輸出檔本來就不在,而且要記「未設定」。
- visual 的 `visual-check.sh` 輸出(相符率那行)存哪。
在這些介面定好之前,三條條款的測試只能自己發明格式。

## F4 沒有任何東西把「驗到的 APK」綁到「被指紋的程式」
severity: major
blocking: 是(漏擋:沒驗到這版程式也會得 pass)
引句:「紀錄記它的 sha256(另記裝置上實際安裝那份的 sha256)」
spec 段落:〈設定〉apk、〈資料怎麼流〉第 1、2 步、〈查證紀錄〉環境。
問題:兩個 sha256 只被記錄,判定規則從不拿來比對,有三種非惡意的情況會得到 pass。
1. `adb install` 失敗(簽章衝突、版本降級、裝置離線)。安裝不是四塊之一,S6 管不到它,UI 流程會對裝置上舊版 App 跑,仍然 pass。
2. `apk` 路徑指向舊的 build 產物,沒重建。
3. 指紋只算被推送提交的檔案樹,APK 卻是從有未提交改動的工作目錄建的。judge 沒有 commit 參數,算的是哪個提交也沒寫。
其中一種代價就是現有 `截圖基準驗收流程_計劃` 已經踩過的「舊版畫面拿到綠燈」。至少要規定:設定的 APK sha256 與裝置上的不等,result 不得是 pass;工作目錄在 `app_dirs` 有未提交改動時,judge 要拒絕寫紀錄。
file: `docs/lumos-toolchain-knowledge/Projects/截圖基準驗收流程_計劃.md:84`(假通過的前例)

## F5 紀錄放在 app_dirs 底下就永遠對不上指紋;紀錄從哪裡讀沒說
severity: major
blocking: 是(兩種設定或做法會讓 S7、S10 失效)
引句:「找對得上指紋的紀錄:結果是通過、或有人放行 → 這道過」
spec 段落:〈資料怎麼流〉第 2、3 步、S1、S2。
問題有兩個。
1. S1 沒禁止 `app_dirs` 包住 `.lumos/e2e-records/`。設 `"."`、`".lumos"` 或專案根時,提交紀錄檔會改變指紋,紀錄永遠對不上,每次都被擋。S1 應拒絕 `app_dirs` 與紀錄目錄重疊。
2. 判定從哪裡讀紀錄沒寫:被推送提交的檔案樹,還是工作目錄。指紋明說「不看工作目錄」,紀錄卻沒講。讀工作目錄的話,未提交的紀錄會讓本機 pre-push 放行、CI 擋下。而且 pre-push 推的 ref 不一定是目前 checkout 的那個。
S7 的測試要先決定這一點才寫得出來。

## F6 工具失敗、未跑、記憶體塊缺輸入時,result 該是 fail 還是 unjudged,條款互相打架
severity: major
blocking: 是(同一輸入在 S5 與 S6 下結果不同)
引句:「judge 應把那一塊記成失敗、result 不得是 pass」
spec 段落:S5、S6、〈查證紀錄〉result。
問題有三處。
1. 收集腳本失敗(rc 2、沒寫 `stability.json`)。S6 說記成「失敗」,但這一塊的規格是 `macrobench --stability` 對缺檔會把每條 check 記成 `沒給 --stability 結果檔` 的 skipped,即 unjudged。result 是 fail 還是 unjudged,條款沒定。
2. 毫秒類塊工具沒跑成。S6 說任一塊都算失敗、result 不得是 pass,但這塊是「只提醒」。是不是要 notices、會不會讓 result 變 fail,沒定義。
3. result 的四個值只用「會擋的」判,Macrobenchmark 塊的失敗被算成什麼完全沒覆蓋。
file: `scripts/lumos:40065-40070`(`stab is None` 回「沒給 --stability 結果檔」,歸 skipped)、`scripts/lumos:39795-39830`

## F7 threshold_failures 混著毫秒類與記憶體類;只設部分 check 的專案會靜默得 pass
severity: major
blocking: 是(一種是誤擋毫秒類,一種是漏擋記憶體洩漏)
引句:「列在 threshold_failures 算沒過;列在 threshold_skipped」
spec 段落:〈四塊〉記憶體與穩定性列、S5、〈設定〉最後一條。
問題有兩個。
1. `lumos macrobench --json` 把毫秒類門檻與記憶體 check 都併進同一個 `threshold_failures`,後者靠有沒有 `check` 欄位分。S5 沒寫 judge 要依這個欄位分流,也沒寫 `check == "frozen"` 要轉進 notices。照字面把 `threshold_failures` 一律當擋,會讓毫秒類門檻沒達變 fail,等於違背「毫秒類第一版只提醒」。
2. 專案的 `.lumos/macrobench-thresholds.json` 只寫了 `exits`、沒寫 `native_unreachable`、`java_growth`,這時只有 `exits` 進清單,其餘兩類不在任何清單裡。judge 只看「failures/skipped」,result 是 pass,洩漏類根本沒判卻通過。S1 的 check-config 也沒要求 `macrobench.json` 的 `stability` 段或門檻檔存在或涵蓋哪幾類。
file: `scripts/lumos:39795-39830`、`scripts/lumos:40060-40062`(七種 check 名,`frozen` 與 `strictmode` 在內)、`scripts/lumos:40201-40243`

## F8 visual-check.sh 的真實介面與 spec 對不上:門檻、裝置、鎖
severity: major
blocking: 是(`visual_threshold` 與 `adb_serial` 設了也不生效;殘留鎖目錄會讓每次 rc 1)
引句:「不得低於 99.5(toolkit 的 `visual-check.sh` 收到更低的門檻會回 2)」
spec 段落:〈設定〉visual_threshold、adb_serial、〈四塊〉截圖比對列、S4。
問題有三個。
1. toolkit 的門檻只認環境變數 `THRESHOLD`(不是參數)。spec 的呼叫列沒說腳本要 `THRESHOLD=<visual_threshold>`,設定欄位等於沒接上。
2. 裝置選擇走 `.maestro/visual-env.sh` 的 `DEVICE`,不是 `adb_serial`。spec 說 `adb_serial`「傳給 Maestro、收集腳本與 adb」,沒包含 toolkit,多台裝置時 toolkit 跑在另一台。
3. `visual-check.sh` 用 `mkdir .maestro/.lock-<DEVICE>` 當鎖,鎖被占用回 1。前一輪被 Ctrl-C 殺掉、trap 沒跑時鎖目錄殘留,之後每次都 rc 1,而 spec 把 1 一律算「不相符或環境問題」且擋。
還有一點:EVID 第二個參數放在 `cd "$(dirname "$0")/.."` 之後才用,傳相對路徑會落在專案根下,不是呼叫者的目錄。
file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:15-26`(`THRESHOLD`、鎖)、`/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:5`(`cd` 到專案根)

## F9 分岔點算不出來時範圍怎麼辦沒定義
severity: minor
blocking: 否(邊界缺口,CI 對應步驟已有同類慣例可抄)
引句:「從這個分支跟主線的分岔點,到這次被推送的提交」
spec 段落:〈資料怎麼流〉第 3 步範圍。
問題:本地沒有主線 ref(CI 淺 clone 缺 `origin/main`)、新分支首推、主線自己被推時,分岔點可能算不出或等於頂端。spec 沒寫三種情況。照 CI 現況,算不出時別的判定用空樹,放到這裡等於「整個專案的 app_dirs 都算改過」,每個沒紀錄的分支都被擋。主線被推時分岔點等於頂端,E2E 完全不要求,而 spec 沒說這是有意的。
file: `scripts/hooks/pre-push:42-46`(`pp_block_range_for` 對新分支首推的處理)、`.github/workflows/ci.yml:217-221`

## F10 judge 覆蓋會抹掉放行;紀錄本身沒驗證
severity: minor
blocking: 否(語意缺口,不會漏過現有擋下)
引句:「同一個指紋再跑一次就覆蓋成新的那份」
spec 段落:〈資料怎麼流〉第 2、4 步、S9。
問題有兩處。
1. `waive` 對已存在的紀錄「加上放行」並把 result 改成 waived。之後有人再跑一次 judge,新紀錄整份覆蓋,放行就消失,spec 沒說是有意的,也沒說放行是否要在重跑時保留。
2. gate 沒要求讀出的紀錄內部的指紋欄位等於檔名,也沒驗 result 在四個合法值內、waived 一定帶 `waiver`。手動複製或改名的紀錄會被當成這一版的紀錄。

## F11 新的擋下種類在 pre-push 沒有對應的文案與種類名
severity: minor
blocking: 否(文案缺口,擋不擋不受影響)
引句:「判定回 2 時 CI 步驟是否算紅要在實作時確認並寫進家節點」
spec 段落:〈資料怎麼流〉第 3 步位置、〈實務隱患〉。
問題:這句其實已經能答。`ci.yml` 對 rc 非 1 直接 `exit "$rc"`,所以判定回 2 時 CI 是紅的。pre-push 的 `pp_cl_reason` 只認五種 `reason_kind`,新增 E2E 這種擋下要有種類名,否則落到預設「代碼審判定擋下(細節在上面)」;固定的「逃生路」那段文字也沒有 `android-e2e waive`。spec 只寫「印出要跑的指令」,沒指定種類名,也沒改 pre-push。
file: `.github/workflows/ci.yml:221-229`、`scripts/hooks/pre-push:138-146`

## F12 S9 的「少於 10 個字」與「誰」沒定義
severity: minor
blocking: 否(邊界缺口,能補)
引句:「lumos 應在理由少於 10 個字時回 2」
spec 段落:S9。
問題:「字」是字元、去掉空白後的字元、還是位元組,沒定。全空白的 10 個字元算不算也沒定。「誰(git 設定的使用者)」在 `user.name` 沒設時怎麼辦(回 2 還是記空白)也沒寫。測試無法寫出會紅的邊界案例。

## F13 指紋的算法與 app_dirs 的涵蓋有缺口
severity: minor
blocking: 否(邊界缺口,不改變主流程)
引句:「被推送那個提交的檔案樹裡,`app_dirs` 底下的檔,依路徑排序後」
spec 段落:〈查證紀錄〉指紋、S2。
問題有三處。
1. 「路徑+內容一起算」沒指定分隔或長度前綴,路徑 `a` 配內容 `bc` 與路徑 `ab` 配內容 `c` 會撞出同一個 sha256。S2 的測試要明講編碼。
2. `app_dirs` 的項目可以是檔(例 `app/build.gradle.kts`)也可以是目錄,尾端斜線、符號連結、git 子模組(gitlink)的處理沒定。
3. 多模組專案的 `gradle/libs.versions.toml`、根 `build.gradle`、其他 module 若沒列進 `app_dirs`,依賴升版不需要紀錄。這是使用者設定的責任,但 check-config 與 skill 沒提醒。

## F14 tag 推送與非 refs/heads 的推送不跑這道
severity: minor
blocking: 否(設計取捨,但 spec 沒承認)
引句:「`code-loop check` 的 Android E2E 判定應在找不到被推送提交指紋的紀錄」
spec 段落:S7、〈資料怎麼流〉第 3 步。
問題:pre-push 對 `refs/tags/*` 只跑 `--security-only`,CI 的 tag 工作也只跑安全證據。release tag 指到沒驗過的程式時,E2E 判定不會跑。`〈不做〉` 與〈實務隱患〉都沒提,屬於會過期的承認缺口,卻沒有 REVISIT。
file: `scripts/hooks/pre-push:626-655`、`.github/workflows/ci.yml:23-43`

## 固定席節點(派工附帶)
- `Systems/pitfalls-code-loop`:會碰到,會談目錄已有。spec 要在 `code-loop check` 的判定入口多加一道,不影響既有行為,但順序、LUMOS-BLOCKS 種類名、`pp_cl_reason` 文案要一併補(見 F11)。
- `Systems/macrobenchmark-adapter` 與 `Systems/android-stability-collector`:會談目錄沒有這兩篇,只在凍結提交裡。我以程式為準讀了現況,判斷是 spec 沒破壞它們宣稱的行為,但「不改」的前提被 F1 打破:收集腳本輸出位置與 spec 的子目錄不一致。
- 不影響之處:`lumos macrobench` 的 `--json` 欄位與 `stability_unjudged` 語意 spec 引用正確;CI 的 `exit "$rc"` 與 pre-push 的非 1 放行,spec 描述正確。

## 實務隱患(風險類)
- 金流、對外送出、不可逆:無。判定只讀輸出,不碰交易;`gh` 不在審查範圍;紀錄只進專案 git。
- 守衛面:有,見 F4、F6、F7(漏擋)與 F8(誤擋)。
- 時間:有,spec 已列;F2 的舊結果與 F8 的殘留鎖會讓人改走略過檢查。
- 工具鏈相容:`maestro test --device` 實測可接受(`--udid` 與全域 `--device` 皆通過解析),spec 這點沒錯。

總結:最嚴重為 major,blocking 共 8 條
