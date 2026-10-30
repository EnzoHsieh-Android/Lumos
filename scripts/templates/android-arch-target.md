# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
<!-- Android 目標架構的開關資料(lumos arch-template android 讀這支;Projects/Android目標架構開關與舊檔畢業_計劃〈做法〉1)。
     改這支等於改產生器的產出:規則與 Konsist 測試的唯一來源在這裡,技能文件只講訪談題目與採用步驟。
     格式:每塊從一行「=== <種類> <條件> [convention]」開始,到下一個 === 行為止;塊頭以外的文字原樣進產出。
       種類:node(節點的非規則部分)、rule(一條 RULE 行,產出時縮兩格放進 summary)、code(測試檔的非測試部分)、
             test(一支 @Test 函式;同名的兩塊條件要互斥);塊頭帶 convention 的測試是命名慣例,不對應 RULE 行。
       條件:* 是一律收;否則寫 開關=選項,多個用逗號連(全部成立才收)。開關與選項以產生器的開關表為準,寫錯產生器會拒絕。
     佔位字(產生器一次掃描替換,表外的佔位字會讓產生器拒絕):
       {{FIELDS}} 規則的必有欄位;{{ROOT}} 根套件;{{SCOPE_LIST}} 範圍目錄的 Kotlin 字串清單;{{SCOPE_TEXT}} 範圍目錄的人讀清單;
       {{NODE_TITLE}} 節點標題;{{SWITCHES}} 這次的開關組合。
     改完跑 python3.14 scripts/test_lumos.py -k arch_template(64 種組合逐一驗 lint、規則數、測試名對得上)。 -->
=== node *
---
type: system
status: doing
responsibility: 照 MVVM 加 DDD 寫的 Android 新功能該遵守的寫法;不管任何程式檔,規則套用的目錄由 .lumos/config.json 的 arch_targets 宣告
aliases:
  - Android 架構規則
  - MVVM 規則
  - 領域驅動設計規則
tags:
  - type/system
  - status/doing
summary: |-
=== rule *
RULE:domain 套件是純 Kotlin:不 import android、androidx、Room、Retrofit 或序列化框架的型別,也不收 Context。違反長怎樣:Order 加了 Room 的 @Entity,或用例建構子收 Context 去讀 SharedPreferences [test:domainHasNoAndroidImports] {{FIELDS}}
=== rule ddd=full
RULE:業務不變規則只寫在聚合根的方法裡;聚合對外不露 var 與可變集合,外部不得直接改聚合內部欄位或子物件。違反長怎樣:ViewModel 裡 cart.lines.add(line),或用例裡 order.status = PAID [test:aggregateRootsHideMutableState] {{FIELDS}}
=== rule ddd=full
RULE:聚合之間只用識別碼參照,一次操作只改一個聚合;跨聚合的連動由用例分兩步做。違反長怎樣:Order 直接持有 Customer 物件,並在同一個用例裡改 Customer 的點數 [test:aggregatesReferenceOthersByIdOnly] {{FIELDS}}
=== rule ddd=full
RULE:Repository 介面放在 domain、實作放在 data,以聚合為單位整包載入與存回;回給上層的是領域物件,不是 Room 實體或 API 傳輸物件。違反長怎樣:OrderRepository.updateLineQty(orderId, lineNo, qty),或介面回傳 OrderEntity [test:layersDependOnlyInward] {{FIELDS}}
=== rule ddd=lite
RULE:Repository 介面放在 domain、實作放在 data;回給上層的是領域物件,不是 Room 實體或 API 傳輸物件。違反長怎樣:OrderRepository 回傳 OrderEntity,或 domain 的介面方法收 Retrofit 的 Response [test:layersDependOnlyInward] {{FIELDS}}
=== rule ddd=full
RULE:值物件不可變,建構時就驗證合法性(init 裡 require),相等性看值。違反長怎樣:Money 有 var amount,或可以建出負數金額再於別處檢查 [test:valueObjectsAreImmutable] {{FIELDS}}
=== rule ddd=full,usecase=required
RULE:用例一個類別做一件事,對外只有一個 operator fun invoke,只做協調(載入聚合、呼叫聚合的行為方法、存回),不寫業務判斷。違反長怎樣:用例裡 if (order.total > 1000) 打折,或一個 OrderUseCases 類別塞五個公開方法 [test:useCasesExposeSingleInvoke] {{FIELDS}}
=== rule ddd=lite,usecase=required
RULE:用例一個類別做一件事,對外只有一個 operator fun invoke,只做協調(經 Repository 取出領域物件、呼叫它的方法、存回),不寫業務判斷。違反長怎樣:用例裡 if (order.total > 1000) 打折,或一個 OrderUseCases 類別塞五個公開方法 [test:useCasesExposeSingleInvoke] {{FIELDS}}
=== rule ddd=full,usecase=optional
RULE:有用例時,一個類別做一件事,對外只有一個 operator fun invoke,只做協調(載入聚合、呼叫聚合的行為方法、存回),不寫業務判斷;只是轉呼叫 Repository 的流程可以不開用例。違反長怎樣:用例裡 if (order.total > 1000) 打折,或一個 OrderUseCases 類別塞五個公開方法 [test:useCasesExposeSingleInvoke] {{FIELDS}}
=== rule ddd=lite,usecase=optional
RULE:有用例時,一個類別做一件事,對外只有一個 operator fun invoke,只做協調(經 Repository 取出領域物件、呼叫它的方法、存回),不寫業務判斷;只是轉呼叫 Repository 的流程可以不開用例。違反長怎樣:用例裡 if (order.total > 1000) 打折,或一個 OrderUseCases 類別塞五個公開方法 [test:useCasesExposeSingleInvoke] {{FIELDS}}
=== rule usecase=required
RULE:ViewModel 建構子只收用例與執行期參數,不收 Context、Activity、Fragment、View,也不直接收 Repository 或資料來源。違反長怎樣:ViewModel 收 OrderRepository 自己存檔,或持有 Activity 去開對話框 [test:viewModelDependsOnUseCasesNotFrameworkOrRepository] {{FIELDS}}
=== rule usecase=optional
RULE:ViewModel 建構子只收用例、domain 的 Repository 介面與執行期參數,不收 Context、Activity、Fragment、View,也不收 data 層的實作(RepositoryImpl)或資料來源(DataSource、Dao、Api)。違反長怎樣:ViewModel 收 OrderDao 自己查資料庫,或持有 Activity 去開對話框 [test:viewModelDependsOnDomainNotFrameworkOrData] {{FIELDS}}
=== rule ui_state=any
RULE:ViewModel 對外只露唯讀的 UI 狀態(StateFlow 加不可變的狀態類別),可變的狀態容器一律 private;畫面不能改 ViewModel 的狀態。違反長怎樣:公開 val state = MutableStateFlow(...),或 Fragment 裡 viewModel.state.value = ... [test:viewModelExposesReadOnlyState] {{FIELDS}}
=== rule ui_state=single
RULE:每個 ViewModel 對外只公開一個 uiState(StateFlow 加一個不可變的 UiState 類別),可變的狀態容器一律 private;畫面不能改 ViewModel 的狀態。違反長怎樣:同時公開 val loading 與 val items 兩個 StateFlow,或 Fragment 裡 viewModel.uiState.value = ... [test:viewModelExposesSingleUiState] {{FIELDS}}
=== rule ddd=full
RULE:ViewModel 只把領域層給的結果翻成畫面要的狀態(格式化、組合、錯誤訊息),不寫業務規則;規則要搬進聚合根。違反長怎樣:ViewModel 裡算折扣、判斷庫存夠不夠能不能下單 {{FIELDS}}
=== rule ddd=lite
RULE:ViewModel 只把領域層給的結果翻成畫面要的狀態(格式化、組合、錯誤訊息),不寫業務規則;規則要搬進 domain 的領域物件。違反長怎樣:ViewModel 裡算折扣、判斷庫存夠不夠能不能下單 {{FIELDS}}
=== rule *
RULE:畫面(Activity、Fragment、Composable)只渲染 UI 狀態並把使用者操作轉成 ViewModel 的方法呼叫;不直接呼叫用例或 Repository,也不寫業務判斷。違反長怎樣:Composable 裡 if (cart.total > 1000) 顯示免運,或 Fragment 直接呼叫 repository.save() {{FIELDS}}
=== rule ddd=full,interfaces=deep
RULE:模組邊界劃在聚合與用例(深模組):不為只有一個實作的用例或 Repository 以外的類別另開介面,也不為每個值物件開 Factory。違反長怎樣:AddToCartUseCase 介面加 AddToCartUseCaseImpl,裡面只是轉呼叫 {{FIELDS}}
=== rule ddd=lite,interfaces=deep
RULE:模組邊界劃在用例與 Repository(深模組):除了 Repository 介面,不為只有一個實作的類別另開介面。違反長怎樣:AddToCartUseCase 介面加 AddToCartUseCaseImpl,裡面只是轉呼叫 {{FIELDS}}
=== rule interfaces=always
RULE:用例與 Repository 一律寫成介面加實作:介面放 domain,實作類別名是介面名加 Impl 並實作那個介面;其他類別(ViewModel、資料類別)不另開介面。違反長怎樣:AddToCartUseCaseImpl 沒實作 AddToCartUseCase,或替 CartViewModel 開一個 CartViewModelContract 介面 [test:implementationsImplementSameNameInterface] {{FIELDS}}
=== rule ddd=full
RULE:領域測試只經由聚合根與用例的公開方法驗結果,用純 JVM 單元測試;ViewModel 測試驗它吐出的 UI 狀態,Repository 用假實作;不讀寫內部欄位、不 mock 自己的領域物件。違反長怎樣:測試斷言 viewModel._state,或 mock 掉 Cart.add() 再驗用例 {{FIELDS}}
=== rule ddd=lite
RULE:領域測試只經由用例與領域物件的公開方法驗結果,用純 JVM 單元測試;ViewModel 測試驗它吐出的 UI 狀態,Repository 用假實作;不讀寫內部欄位、不 mock 自己的領域物件。違反長怎樣:測試斷言 viewModel._state,或 mock 掉 Cart.add() 再驗用例 {{FIELDS}}
=== rule modules=multi
RULE:模組依賴照分層走:畫面(feature)模組只依賴 domain 模組、不依賴 data 模組;有獨立的 domain 模組時它是純 Kotlin 模組(不套 Android 外掛);只有組裝依賴注入的 app 模組同時依賴 domain 與 data。違反長怎樣:feature/cart 的 build.gradle.kts 寫 implementation(project(":core:data")),或 core/domain 套了 com.android.library {{FIELDS}}
=== node *
---
# {{NODE_TITLE}}

> 白話:這篇是「照 MVVM 加 DDD 寫的 Android 新功能」該長什麼樣的規則清單。專案在 .lumos/config.json 的 arch_targets 宣告哪些目錄照這篇審,架構對齊審查席就改拿上面的 RULE 行當標準,不再要求新程式跟舊鄰居長得一樣;範圍外的舊碼照舊比鄰居。

這篇由 `lumos arch-template android` 產出,開關:{{SWITCHES}}。範圍目錄:{{SCOPE_TEXT}}。

- 換開關:用新的開關重跑產生器,換掉這篇與架構測試兩份;舊檔清單不要重產(重產會把採用後新寫的檔也凍成舊檔)。
- 新增模組:`.lumos/config.json` 的 arch_targets 與架構測試裡的 `scopeDirs` 各加一個目錄。
- 帶 `[test:]` 的規則由架構測試守,其餘是語意,留給審查席。
=== code *
// 架構規則測試(lumos arch-template android 產出;開關:{{SWITCHES}})
// 用 Konsist 讀原始碼,把目標架構的結構約定變成會紅的單元測試(只掃正式程式,不掃測試)
package {{ROOT}}.arch

import com.lemonappdev.konsist.api.Konsist
import com.lemonappdev.konsist.api.verify.assertFalse
import com.lemonappdev.konsist.api.verify.assertTrue
import java.io.File
import java.text.Normalizer
import org.junit.Test

class ArchitectureRulesTest {
    private val appRoot = "{{ROOT}}"
    private val forbiddenInViewModel = setOf("Context", "Activity", "Fragment", "View")

    // 範圍目錄(相對 repo 根):要跟 .lumos/config.json 的 arch_targets 同步,新增模組時兩邊各加一個
    private val scopeDirs = listOf({{SCOPE_LIST}}).map { nfc(it) }

    // repo 根:往上找含 .lumos/config.json 的資料夾(Gradle 子模組的工作目錄不是 repo 根也找得到);找不到就讓測試紅,不靜默變綠
    private val repoRoot: File = generateSequence(File(System.getProperty("user.dir")).canonicalFile) { it.parentFile }
        .firstOrNull { File(it, ".lumos/config.json").isFile }
        ?: error("往上找不到含 .lumos/config.json 的資料夾:架構測試不知道 repo 根在哪,沒辦法判斷哪些檔在範圍內")
=== code legacy=new-only

    // 舊檔清單:採用當下凍結的逐檔名單,照舊鄰居審、這裡跳過;檔不存在或讀不出 files 陣列就讓測試紅
    private val legacyFiles: Set<String> = readLegacyFiles(File(repoRoot, ".lumos/arch-legacy.json"))
=== code *

    // 全部正式程式:被參照的對象(聚合根名單)照這份算
    private val all = Konsist.scopeFromProduction()

    // 受檢查的範圍:相對 repo 根的路徑落在某個範圍目錄底下(以斜線為界)的檔
    private val scope = all.slice { inScope(it.path) }

    private fun nfc(s: String): String = Normalizer.normalize(s, Normalizer.Form.NFC)

    private fun relPath(path: String): String = nfc(File(path).canonicalFile.relativeTo(repoRoot).invariantSeparatorsPath)
=== code legacy=all

    private fun inScope(path: String): Boolean {
        val rel = relPath(path)
        return scopeDirs.any { rel == it || rel.startsWith("$it/") }
    }
=== code legacy=new-only

    private fun inScope(path: String): Boolean {
        val rel = relPath(path)
        return scopeDirs.any { rel == it || rel.startsWith("$it/") } && rel !in legacyFiles
    }

    // 舊檔清單只認產生器寫出的形狀:只有 files 一個欄位、字串裡沒有反斜線與控制字元、逗號照 JSON。不為一個清單加 JSON 函式庫,
    // 用兩條正規式讀,只用 Java 與 Python 意思相同的語法:lumos 的測試把這兩條原文抽出來,拿一批輸入跟標準 JSON 的讀法逐案比對。
    // 比 lumos 嚴(lumos 收任何合法 JSON):lumos 讀得懂、這裡不認的清單會讓測試紅並說明,不會靜默照讀。
    // 正規式放在函式裡:舊檔清單那個欄位在前面初始化時就會叫這支,放成後面的欄位會還沒初始化。
    // \A、\z 是整份字串的頭尾(Java 的 $ 會停在 U+2028 這類行終止符前面,Python 的不會);開頭的 BOM 在正規式裡處理;
    // 外層重複群組用佔有式 *+:Java 對一般的重複群組逐次遞迴,清單兩千多條就堆疊溢位(代碼審 r3 實測)
    private fun readLegacyFiles(f: File): Set<String> {
        check(f.isFile) { "找不到舊檔清單 ${f.path}:這支測試照 new-only 產出,要靠它跳過舊檔(要全部照目標審,用 --legacy all 重產這支測試)" }
        val legacyDoc = Regex("""\A\uFEFF?[ \t\r\n]*\{[ \t\r\n]*\x22files\x22[ \t\r\n]*:[ \t\r\n]*\[[ \t\r\n]*((?:\x22[^\x22\\\x00-\x1F]*\x22(?:[ \t\r\n]*,[ \t\r\n]*\x22[^\x22\\\x00-\x1F]*\x22)*+)?)[ \t\r\n]*\][ \t\r\n]*\}[ \t\r\n]*\z""")
        val legacyItem = Regex("""\x22([^\x22\\\x00-\x1F]*)\x22""")
        val text = f.readText(Charsets.UTF_8)
        val doc = legacyDoc.find(text)
            ?: error("舊檔清單 ${f.path} 的形狀架構測試不認:只能是 {\"files\": [\"路徑\", …]},字串裡不能有反斜線或控制字元,逗號不能多也不能少(刪掉最後一行時,前一行的逗號要一起拿掉)")
        return legacyItem.findAll(doc.groupValues[1]).map { nfc(it.groupValues[1]) }.toSet()
    }
=== test *

    // 分層:領域層不依賴其他兩層;資料層不依賴畫面層;畫面層不依賴資料層(只能經領域層)
    // 用 import 判斷、不用 Konsist 的 assertArchitecture:後者只要有一層在範圍內一支檔都沒有就直接失敗,
    // new-only 剛採用(範圍內全是舊檔)或只寫了領域層時整支紅(2026-10-30 在 macrobench-lab 實測)
    @Test
    fun layersDependOnlyInward() {
        val forbidden = mapOf(
            "$appRoot.domain" to listOf("$appRoot.data", "$appRoot.presentation"),
            "$appRoot.data" to listOf("$appRoot.presentation"),
            "$appRoot.presentation" to listOf("$appRoot.data"),
        )
        scope.files.forEach { file ->
            val pkg = file.packagee?.name.orEmpty()
            val banned = forbidden.entries.firstOrNull { (layer, _) -> pkg == layer || pkg.startsWith("$layer.") }?.value.orEmpty()
            file.imports.assertFalse { imp -> banned.any { imp.name == it || imp.name.startsWith("$it.") } }
        }
    }
=== test *

    // 領域層是純 Kotlin:不准 import Android、AndroidX(含 Room)、Retrofit 或常見的序列化框架
    @Test
    fun domainHasNoAndroidImports() {
        val frameworkPrefixes = listOf(
            "android.", "androidx.", "retrofit2.", "kotlinx.serialization.",
            "com.squareup.moshi.", "com.google.gson.", "com.fasterxml.jackson.",
        )
        scope.files
            .filter { it.packagee?.name?.startsWith("$appRoot.domain") == true }
            .flatMap { it.imports }
            .assertFalse { imp -> frameworkPrefixes.any { imp.name.startsWith(it) } }
    }
=== test * convention

    // MVVM:繼承 ViewModel 的類別名稱以 ViewModel 結尾,且放在 presentation 套件
    @Test
    fun viewModelsAreNamedAndPlaced() {
        scope.classes()
            .filter { it.hasParentWithName("ViewModel") }
            .assertTrue { it.name.endsWith("ViewModel") && it.resideInPackage("..presentation..") }
    }
=== test ui_state=any

    // MVVM:ViewModel 對外的屬性要明寫型別,而且不能是可變的狀態容器(外面只能看、不能改)
    @Test
    fun viewModelExposesReadOnlyState() {
        scope.classes()
            .filter { it.hasParentWithName("ViewModel") }
            .flatMap { it.properties() }
            .filter { it.hasPublicOrDefaultModifier }
            .assertTrue { prop ->
                val type = prop.type?.name
                type != null && !type.startsWith("Mutable")
            }
    }
=== test ui_state=single

    // MVVM:每個 ViewModel 對外只公開一個 uiState,型別是唯讀的 StateFlow(可變容器一律 private)
    @Test
    fun viewModelExposesSingleUiState() {
        scope.classes()
            .filter { it.hasParentWithName("ViewModel") }
            .assertTrue { vm ->
                val exposed = vm.properties(includeNested = false).filter { it.hasPublicOrDefaultModifier }
                exposed.size == 1 && exposed.single().let { it.name == "uiState" && it.type?.name?.startsWith("StateFlow") == true }
            }
    }
=== test usecase=required

    // MVVM:ViewModel 不持有畫面元件,也不直接拿存取介面或資料來源(改動要走用例);不比用例可省略那版鬆
    @Test
    fun viewModelDependsOnUseCasesNotFrameworkOrRepository() {
        val dataSuffixes = listOf("Repository", "RepositoryImpl", "DataSource", "Dao", "Api")
        scope.classes()
            .filter { it.hasParentWithName("ViewModel") }
            .flatMap { it.primaryConstructor?.parameters.orEmpty() }
            .assertFalse { param ->
                val type = param.type.name.substringBefore('<').substringBefore('?')
                type in forbiddenInViewModel || dataSuffixes.any { type.endsWith(it) }
            }
    }
=== test usecase=optional

    // MVVM(用例可省略):ViewModel 可以收 domain 的 Repository 介面,但不持有畫面元件,也不碰 data 層的實作與資料來源
    @Test
    fun viewModelDependsOnDomainNotFrameworkOrData() {
        val dataSuffixes = listOf("RepositoryImpl", "DataSource", "Dao", "Api")
        scope.classes()
            .filter { it.hasParentWithName("ViewModel") }
            .flatMap { it.primaryConstructor?.parameters.orEmpty() }
            .assertFalse { param ->
                val type = param.type.name.substringBefore('<').substringBefore('?')
                type in forbiddenInViewModel || dataSuffixes.any { type.endsWith(it) }
            }
    }
=== test interfaces=deep

    // 用例:放在領域層,只有一個公開函式,而且是 operator invoke
    @Test
    fun useCasesExposeSingleInvoke() {
        scope.classes()
            .filter { it.name.endsWith("UseCase") }
            .assertTrue { useCase ->
                val publicFunctions = useCase.functions().filter { it.hasPublicOrDefaultModifier }
                useCase.resideInPackage("..domain..") &&
                    publicFunctions.size == 1 &&
                    publicFunctions.single().let { it.name == "invoke" && it.hasOperatorModifier }
            }
    }
=== test interfaces=always

    // 用例:放在領域層,只有一個公開函式,而且是 invoke(實作類別覆寫介面的 operator invoke 時可以不重寫 operator)
    @Test
    fun useCasesExposeSingleInvoke() {
        scope.classes()
            .filter { it.name.endsWith("UseCase") || it.name.endsWith("UseCaseImpl") }
            .assertTrue { useCase ->
                val publicFunctions = useCase.functions().filter { it.hasPublicOrDefaultModifier }
                useCase.resideInPackage("..domain..") &&
                    publicFunctions.size == 1 &&
                    publicFunctions.single().let { it.name == "invoke" && (it.hasOperatorModifier || it.hasOverrideModifier) }
            }
    }
=== test interfaces=always

    // 介面一律開:每個 Impl 結尾的類別都實作去掉 Impl 的同名介面
    @Test
    fun implementationsImplementSameNameInterface() {
        scope.classes()
            .filter { it.name.endsWith("Impl") }
            .assertTrue { impl -> impl.hasParentWithName(impl.name.removeSuffix("Impl")) }
    }
=== test ddd=full

    // DDD 值物件:所有屬性都是 val,也不能用可變集合
    @Test
    fun valueObjectsAreImmutable() {
        scope.classes()
            .filter { it.hasAnnotationWithName("ValueObject") }
            .flatMap { it.properties(includeNested = false) }
            .assertTrue { prop -> prop.isVal && prop.type?.name?.startsWith("Mutable") != true }
    }
=== test ddd=full

    // DDD 聚合根:對外不能有 var 或可變集合,改狀態只能透過自己的方法
    @Test
    fun aggregateRootsHideMutableState() {
        scope.classes()
            .filter { it.hasAnnotationWithName("AggregateRoot") }
            .flatMap { it.properties(includeNested = false) }
            .filter { it.hasPublicOrDefaultModifier }
            .assertTrue { prop -> prop.isVal && prop.type?.name?.startsWith("Mutable") != true }
    }
=== test ddd=full

    // DDD 聚合根:指向別的聚合只能存對方的識別碼,不能直接持有對方物件(聚合根名單照全部正式程式算,不只範圍內)
    @Test
    fun aggregatesReferenceOthersByIdOnly() {
        val rootNames = all.classes().filter { it.hasAnnotationWithName("AggregateRoot") }.map { it.name }.toSet()
        scope.classes().filter { it.hasAnnotationWithName("AggregateRoot") }.forEach { root ->
            val others = rootNames - root.name
            root.properties(includeNested = false).assertFalse { prop ->
                val typeName = prop.type?.name.orEmpty()
                val referenced = Regex("[A-Za-z_][A-Za-z0-9_]*").findAll(typeName).map { it.value }.toSet()
                (referenced intersect others).isNotEmpty()
            }
        }
    }
=== code *
}
