# Android 的 MVVM 加 DDD 目標架構範本

Android 專案想讓新功能照「MVVM 加 DDD」寫(畫面、ViewModel、用例、Repository 分層,視開關加上聚合與值物件),又不想被架構對齊審查席判成「跟舊鄰居不一樣」時,用產生器 `lumos arch-template android` 開一篇目標架構節點、`.lumos/config.json` 的 `arch_targets` 宣告、(要的話)舊檔清單與 Konsist 架構測試。機制本身見 [06-代碼審與推送.md](06-代碼審與推送.md) 的 `arch_targets` 那一列;規則與測試的唯一來源是工具自帶的開關資料檔 `scripts/templates/android-arch-target.md`,這份文件只講要問什麼、怎麼採用。單源 Projects/Android目標架構開關與舊檔畢業_計劃。

## 先問人六題

採用前由 AI 逐題問人,答案直接對應產生器的旗標。每題附建議答案;拿不準就照建議。

1. **模組怎麼切?** 專案只有一個 app 模組選 `single`;已經或打算拆成 feature、core 這類多個 Gradle 模組選 `multi`(多一條模組依賴規則,由 Gradle 的依賴宣告守)。
2. **舊程式怎麼處理?** 建議 `new-only`:範圍內現有的檔全部列進舊檔清單,照舊鄰居審,只有之後新寫的檔照目標規則審;舊檔重構時從清單刪掉它那一行,同一個分支就改照目標審。範圍內本來就是新寫的程式(或願意一次整理完)選 `all`。只想套用在某幾個目錄,就只給那幾個 `--scope`。
3. **用例層一定要有嗎?** 建議 `required`:ViewModel 只透過用例拿資料。只是轉呼叫 Repository 的流程不想開用例,選 `optional`(ViewModel 可收 domain 的 Repository 介面,但不准碰 data 層的實作與資料來源)。這跟 Android 官方架構指南把領域層標為可選一致。
4. **DDD 做多深?** 業務規則多、有明確的聚合邊界(訂單、購物車)選 `full`;只想要分層與 Repository、不用聚合根與值物件,選 `lite`。
5. **介面怎麼開?** 建議 `deep`:只有一個實作就不開介面(Repository 例外)。團隊習慣一律「介面加 Impl」(例如為了替換假實作)選 `always`。
6. **畫面狀態長怎樣?** 每個 ViewModel 只公開一個 `uiState` 選 `single`;允許公開多個唯讀狀態選 `any`。

## 開關

| 開關 | 選項 | 影響 |
|---|---|---|
| 模組切法 `--modules` | `single` 單模組 / `multi` 多模組 | multi 加一條模組依賴規則,Konsist 測試不減 |
| 舊程式處理 `--legacy` | `all` 範圍內全部套用 / `new-only` 舊檔照舊 | new-only 多產舊檔清單,架構測試會讀它跳過舊檔 |
| 用例層 `--usecase` | `required` 一定要有 / `optional` 可省略 | optional 時 ViewModel 可收 domain 的 Repository 介面,只禁 data 層實作與資料來源 |
| DDD 深度 `--ddd` | `full` 完整 / `lite` 輕量 | lite 拿掉聚合根、識別碼參照、值物件三條規則與三支測試,其餘規則換成不提聚合的版本 |
| 介面策略 `--interfaces` | `deep` 深模組 / `always` 一律開介面 | always 換規則、用例測試認 Impl、多一支「Impl 都實作同名介面」的測試 |
| 畫面狀態 `--ui-state` | `single` 單一 UiState / `any` 不限 | single 換成「每個 ViewModel 只公開一個 uiState」規則與測試 |

六個開關沒有預設值,一律照訪談答案明給。

## 採用步驟

1. 問完六題,跑預覽給人看(範圍照專案實際目錄;多模組每個模組各給一個 `--scope`):

```
lumos arch-template android --root com.example.app --scope app/src/main/java/com/example/app \
  --modules single --legacy new-only --usecase required --ddd full --interfaces deep --ui-state any
```

2. 人同意後,用 `--print <段名>` 取單段原文依序存檔(lumos 不寫檔;用重導向或寫檔工具存):
   - `--print node` → 預覽標的節點路徑(預設 `Systems/Android目標架構`,`--node` 可換),存完 `lumos lint <節點>`。
   - `--print targets` → 併進 `.lumos/config.json` 的 `arch_targets`(已有宣告就合併成一份;第一條命中算數)。
   - `--print legacy` → `.lumos/arch-legacy.json`(只有 new-only 有)。
   - `--print test` → 單元測試目錄的 `ArchitectureRulesTest.kt`(預覽給建議位置),依賴加 `testImplementation("com.lemonappdev:konsist:<版本>")`。
3. 在 domain 套件加兩個標註(ddd=full 才需要;聚合根與值物件靠它們認出來):

```kotlin
@Target(AnnotationTarget.CLASS)
annotation class AggregateRoot

@Target(AnnotationTarget.CLASS)
annotation class ValueObject
```

4. 跑一次架構測試確認綠。new-only 剛採用時範圍內全是舊檔,全綠是正常的;之後新寫的檔才會被抓。

宣告與規則只讀「分支從主線分出來那一刻」的版本:加宣告的那次推送照舊比鄰居,合進主線之後才生效。舊檔清單的畢業是唯一例外:宣告一字不改時,從清單刪掉的檔在同一個分支就照目標審。

## 改主意怎麼做

- **換開關**:用新的開關重跑產生器,換掉節點與架構測試兩份;**舊檔清單不要重產**(重產會把採用後新寫的檔也凍成舊檔)。
- **new-only 改成 all**:刪掉 `.lumos/arch-legacy.json`,用 `--legacy all` 重產架構測試。
- **all 改成 new-only**:先用 `--legacy new-only --print legacy` 產一次舊檔清單(這時範圍內的檔全部凍成舊檔),再換節點與架構測試;只換測試不產清單,架構測試會因為找不到清單整支紅。
- **新增模組**:`arch_targets` 加一條 `<新目錄>/**`,架構測試裡的 `scopeDirs` 加同一個目錄。
- **舊檔重構完**:從舊檔清單刪掉它那一行,跟重構放在同一個分支。刪的是最後一行時,前一行結尾的逗號要一起拿掉:清單是 JSON,多一個逗號 lumos 會判讀不懂(清單整份不起作用、全部照目標審),架構測試也會紅。
- **採用分支開著時主線進來的舊式檔**:合併前補進舊檔清單,不然合進去之後它照目標審、架構測試也會抓它。

## 已照舊範本採用的專案怎麼升級

舊範本(2026-10-29 那份照抄的十二條)產出的節點與宣告照常運作,不升級也可以。要升級時,先把舊節點改名或刪掉、把 `arch_targets` 裡指向它的那幾條拿掉,再照〈採用步驟〉跑產生器;舊的 `ArchitectureRulesTest.kt` 整份換成新產出。

## 舊檔清單與 none 的分工

- **none** 是目錄級的長期排除:`arch_targets` 裡 `node` 寫 `none` 的那條用樣式比對,命中的檔一律照鄰居審,不看舊檔清單。
- **舊檔清單**是採用當下凍結的逐檔名單:整條路徑照字面比對(兩邊先轉 NFC),不當萬用字元;只對被宣告判給目標節點的檔有作用。產生器收範圍內架構對齊會審或架構測試會掃的每支檔。
- 手改舊檔清單時照產生器的形狀:只有 `files` 一個欄位、一行一個路徑、字串裡沒有反斜線。架構測試只認這個形狀(lumos 收任何合法 JSON),不認時測試紅並說明。
- 為什麼不在 `arch_targets` 每條多加一個欄位:宣告形狀只收 `path` 與 `node` 兩欄,舊版 lumos 讀到多一欄的宣告會整份不用;獨立的檔舊版會直接忽略。

## Konsist 那一半

規則裡帶 `[test:<測試名>]` 的由架構測試守,其餘是語意,留給審查席。產出 2026-10-30 在 macrobench-lab 示範專案跑過:預設組與六個開關全反那組都編譯得過;`new-only` 剛採用時全綠,舊檔與新檔各埋一條違規只有新檔紅,從清單刪掉舊檔後兩支都紅,清單不存在時紅並說明。前身(2026-10-29 的固定範本)另驗過 16 種改壞寫法各自只讓對應的那一條紅。

- **Konsist 0.18 起綁 Kotlin 2.4 標準庫,專案的 Kotlin 外掛低於 2.4 時編譯會失敗,改用 0.17.3。**
- 測試自己往上找含 `.lumos/config.json` 的資料夾當 repo 根(Gradle 子模組的工作目錄不是 repo 根也找得到;找不到就紅),只檢查相對根落在 `scopeDirs` 底下、又不在舊檔清單上的檔;聚合根名單這類「被參照的對象」照全部正式程式算。
- 分層那支用 import 判斷,沒用 Konsist 的 `assertArchitecture`:後者只要有一層在範圍內一支檔都沒有就直接失敗,`new-only` 剛採用(範圍內全是舊檔)時整支紅;它的 `dependsOn` 也只表示「可以依賴」,禁止的方向要另寫 `doesNotDependOn`。自己加分層規則時照產出的寫法。
- 新增規則時,至少把樣本改壞一次確認那條會紅;全綠不代表規則有在抓(篩選條件一個類別都沒選中時也是綠的)。
- 架構測試不在 `.lumos/config.json` 預設平台的目錄底下時(例如預設平台是儀器測試、架構測試在 app 的單元測試),先在 `platforms` 宣告那個平台,再把節點裡的 `[test:<測試名>]` 改成 `[test:<平台>:<測試名>]`。
- 領域層若拆成純 Kotlin 模組(不套 Android 外掛),Android 與 AndroidX 那部分由編譯器擋;`domainHasNoAndroidImports` 還擋 Retrofit 與序列化框架(純 Kotlin 模組照樣能依賴它們),不要拿掉。

## 調整與撤除

- 用不到某條就刪掉那一行,或加 `[status:superseded]` 並寫 `[被取代:…]`;架構對齊席只看沒作廢的 RULE 行。
- 到回頭日(`until`)要人裁一次還留不留;過期的規則照樣附給審查席,但會加註「已過 until,待人裁」。
- 撤掉整套:刪 `arch_targets` 整段(全部回到比鄰居),節點、舊檔清單、架構測試可一起刪。
