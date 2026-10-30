# Android 的 MVVM 加 DDD 目標架構範本

Android 專案想讓新功能照「MVVM 加 DDD」寫(畫面、ViewModel、用例、聚合、Repository 分層),又不想被架構對齊審查席判成「跟舊鄰居不一樣」時,用這份範本開一篇目標架構節點,再在 `.lumos/config.json` 的 `arch_targets` 宣告哪些目錄照它審。機制本身見 [06-代碼審與推送.md](06-代碼審與推送.md) 的 `arch_targets` 那一列;形狀跟 [target-arch-ddd-template.md](target-arch-ddd-template.md) 一樣,DDD 那幾條換成 Android 的寫法、另加 MVVM 四條。單源 Projects/Android的MVVM與DDD目標架構範本_計劃。

## 採用步驟

1. 開節點:`lumos new system Android目標架構 --responsibility "照 MVVM 加 DDD 寫的 Android 新功能該遵守的寫法;不管任何程式檔,規則套用的目錄由 .lumos/config.json 的 arch_targets 宣告"`(不帶 `--code`:它規範的是範圍內的寫法,不是自己的程式檔)。
2. 把下面範本區塊的 `summary` 十二條 RULE 行貼進那篇的摘要,正文照需要貼。**套件名照專案實際改**(範本寫的是 `domain`、`data`、`presentation`);用不到的規則整行刪掉。
3. **把 `<採用日>` 換成今天、`<回頭日>` 換成打算回頭檢查的日期(建議一年後)**——沒換就照抄,`lumos lint` 會逐條印「日期要寫成 YYYY-MM-DD」警告(筆記格子目前只提醒不擋,所以要自己換掉)。
4. 在 `.lumos/config.json` 加宣告(路徑照專案實際目錄改;第一條命中算數,範圍內還留著的舊碼用前面一條 `none` 切回鄰居基準;第一段不能是萬用字元):

```json
{
  "arch_targets": [
    {"path": "app/src/main/java/com/example/app/legacy/**", "node": "none"},
    {"path": "app/src/main/java/com/example/app/**", "node": "Systems/Android目標架構"}
  ]
}
```

5. 結構那一半交給機器:照下面〈Konsist 骨架〉加一支架構測試,再把測試名用 `[test:<測試名>]` 掛到對應的 RULE 行。

宣告與規則只讀「分支從主線分出來那一刻」的版本:加宣告的那次推送照舊比鄰居,合進主線之後才生效。

## 為什麼是這十二條

- **前六條是 DDD 的骨架換成 Android 的寫法**:領域層是純 Kotlin(不碰 Android、Room、Retrofit)、不變規則守在聚合根、聚合之間用識別碼、Repository 介面在領域層且不把資料庫實體或傳輸物件往上丟、值物件不可變、用例只協調。
- **中間四條是 MVVM**:ViewModel 不持有畫面元件也不越過用例拿資料來源、對外只給唯讀的 UI 狀態、不寫業務規則只把用例結果翻成畫面要的樣子、畫面只渲染狀態並把操作轉成 ViewModel 方法呼叫(單向資料流)。業務判斷的歸屬因此只有一個答案:聚合根。
- **最後兩條壓住副作用**:深模組(不為每個用例開只有一個實作的介面)與測試邊界(領域從聚合根與用例的公開方法驗,ViewModel 驗它吐出的 UI 狀態)。理由同 DDD 範本。

審查席判得出「違反長怎樣」的才寫成規則;「模型要貼近業務語言」這類審不動的不寫。協程、Flow、Compose 重組這類寫法慣例不在這裡,歸 kotlin-idioms。

## 範本

```markdown
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
  RULE:domain 套件是純 Kotlin:不 import android、androidx、Room、Retrofit 或序列化框架的型別,也不收 Context。違反長怎樣:Order 加了 Room 的 @Entity,或用例建構子收 Context 去讀 SharedPreferences [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:業務不變規則只寫在聚合根的方法裡;聚合對外不露 var 與可變集合,外部不得直接改聚合內部欄位或子物件。違反長怎樣:ViewModel 裡 cart.lines.add(line),或用例裡 order.status = PAID [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:聚合之間只用識別碼參照,一次操作只改一個聚合;跨聚合的連動由用例分兩步做。違反長怎樣:Order 直接持有 Customer 物件,並在同一個用例裡改 Customer 的點數 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:Repository 介面放在 domain、實作放在 data,以聚合為單位整包載入與存回;回給上層的是領域物件,不是 Room 實體或 API 傳輸物件。違反長怎樣:OrderRepository.updateLineQty(orderId, lineNo, qty),或介面回傳 OrderEntity [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:值物件不可變,建構時就驗證合法性(init 裡 require),相等性看值。違反長怎樣:Money 有 var amount,或可以建出負數金額再於別處檢查 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:用例一個類別做一件事,對外只有一個 operator fun invoke,只做協調(載入聚合、呼叫聚合的行為方法、存回),不寫業務判斷。違反長怎樣:用例裡 if (order.total > 1000) 打折,或一個 OrderUseCases 類別塞五個公開方法 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:ViewModel 建構子只收用例與執行期參數,不收 Context、Activity、Fragment、View,也不直接收 Repository 或資料來源。違反長怎樣:ViewModel 收 OrderRepository 自己存檔,或持有 Activity 去開對話框 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:ViewModel 對外只露唯讀的 UI 狀態(StateFlow 加不可變的狀態類別),可變的狀態容器一律 private;畫面不能改 ViewModel 的狀態。違反長怎樣:公開 val state = MutableStateFlow(...),或 Fragment 裡 viewModel.state.value = ... [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:ViewModel 只把用例的結果翻成畫面要的狀態(格式化、組合、錯誤訊息),不寫業務規則;規則要搬進聚合根。違反長怎樣:ViewModel 裡算折扣、判斷庫存夠不夠能不能下單 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:畫面(Activity、Fragment、Composable)只渲染 UI 狀態並把使用者操作轉成 ViewModel 的方法呼叫;不直接呼叫用例或 Repository,也不寫業務判斷。違反長怎樣:Composable 裡 if (cart.total > 1000) 顯示免運,或 Fragment 直接呼叫 repository.save() [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:模組邊界劃在聚合與用例(深模組):不為只有一個實作的用例或 Repository 以外的類別另開介面,也不為每個值物件開 Factory。違反長怎樣:AddToCartUseCase 介面加 AddToCartUseCaseImpl,裡面只是轉呼叫 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:領域測試只經由聚合根與用例的公開方法驗結果,用純 JVM 單元測試;ViewModel 測試驗它吐出的 UI 狀態,Repository 用假實作;不讀寫內部欄位、不 mock 自己的領域物件。違反長怎樣:測試斷言 viewModel._state,或 mock 掉 Cart.add() 再驗用例 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
---
# Android目標架構

> 白話:這篇是「照 MVVM 加 DDD 寫的 Android 新功能」該長什麼樣的規則清單。專案在 .lumos/config.json 的 arch_targets 宣告哪些目錄照這篇審,架構對齊審查席就改拿上面的 RULE 行當標準,不再要求新程式跟舊鄰居長得一樣;範圍外的舊碼照舊比鄰居。
```

## Konsist 骨架

十二條裡有七條的結構面寫得成架構測試,交給 [Konsist](https://docs.konsist.lemonappdev.com/)(讀 Kotlin 原始碼的架構測試庫,跑在一般 JVM 單元測試裡)守;其餘是語意,留給審查席。骨架 2026-10-29 在 macrobench-lab 示範專案跑過:合規樣本全綠,16 種改壞寫法各自只讓對應的那一條紅。

| 規則 | 測試名 |
|---|---|
| domain 純 Kotlin | `layersDependOnlyInward`、`domainHasNoAndroidImports` |
| 聚合根不外露可變狀態 | `aggregateRootsHideMutableState` |
| 聚合之間只用識別碼 | `aggregatesReferenceOthersByIdOnly` |
| 值物件不可變 | `valueObjectsAreImmutable` |
| 用例只有一個 operator invoke | `useCasesExposeSingleInvoke` |
| ViewModel 不收畫面元件與 Repository | `viewModelDependsOnUseCasesNotFrameworkOrRepository` |
| ViewModel 只露唯讀狀態 | `viewModelExposesReadOnlyState` |
| (命名慣例,不對應 RULE) | `viewModelsAreNamedAndPlaced` |

接法:

- 依賴寫 `testImplementation("com.lemonappdev:konsist:<版本>")`。**Konsist 0.18 起綁 Kotlin 2.4 標準庫,專案的 Kotlin 外掛低於 2.4 時編譯會失敗,改用 0.17.3。**
- 聚合根與值物件靠兩個自訂標註認出來,放在 domain 套件:

```kotlin
@Target(AnnotationTarget.CLASS)
annotation class AggregateRoot

@Target(AnnotationTarget.CLASS)
annotation class ValueObject
```

- **分層只寫 `dependsOn` 擋不住依賴別層**:它只表示「可以依賴」,資料層引用畫面層照樣綠。禁止的方向要另寫 `doesNotDependOn`(骨架已寫)。
- 新增規則時,至少把樣本改壞一次確認那條會紅;全綠不代表規則有在抓(篩選條件一個類別都沒選中時也是綠的)。
- 骨架只在「類別依層分套件」(`com.example.app.domain`、`.data`、`.presentation`)的單一模組專案跑過;依功能分套件或多模組時,`Layer` 的套件寫法要照實際結構改,沒驗過。

```kotlin
// 架構規則測試:用 Konsist 讀原始碼,把 MVVM 與 DDD 的結構約定變成會紅的單元測試(只掃正式程式,不掃測試)
package com.example.app.arch

import com.lemonappdev.konsist.api.Konsist
import com.lemonappdev.konsist.api.architecture.KoArchitectureCreator.assertArchitecture
import com.lemonappdev.konsist.api.architecture.Layer
import com.lemonappdev.konsist.api.verify.assertFalse
import com.lemonappdev.konsist.api.verify.assertTrue
import org.junit.Test

class ArchitectureRulesTest {
    private val scope = Konsist.scopeFromProduction()
    private val appRoot = "com.example.app"   // 換成專案的根套件
    private val forbiddenInViewModel = setOf("Context", "Activity", "Fragment", "View")

    // 分層:領域層不依賴任何層;畫面層與資料層只能依賴領域層,彼此不准互相依賴
    // dependsOn 只表示「可以依賴」,不會擋依賴別層(實測資料層引用畫面層照樣綠),所以禁止的方向要另外寫 doesNotDependOn
    @Test
    fun layersDependOnlyInward() {
        val domain = Layer("Domain", "$appRoot.domain..")
        val data = Layer("Data", "$appRoot.data..")
        val presentation = Layer("Presentation", "$appRoot.presentation..")
        scope.assertArchitecture {
            domain.dependsOnNothing()
            data.dependsOn(domain)
            data.doesNotDependOn(presentation)
            presentation.dependsOn(domain)
            presentation.doesNotDependOn(data)
        }
    }

    // 領域層是純 Kotlin:不准 import Android 或 AndroidX
    @Test
    fun domainHasNoAndroidImports() {
        scope.files
            .filter { it.packagee?.name?.startsWith("$appRoot.domain") == true }
            .flatMap { it.imports }
            .assertFalse { it.name.startsWith("android.") || it.name.startsWith("androidx.") }
    }

    // MVVM:繼承 ViewModel 的類別名稱以 ViewModel 結尾,且放在 presentation 套件
    @Test
    fun viewModelsAreNamedAndPlaced() {
        scope.classes()
            .filter { it.hasParentWithName("ViewModel") }
            .assertTrue { it.name.endsWith("ViewModel") && it.resideInPackage("..presentation..") }
    }

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

    // MVVM:ViewModel 不持有畫面元件,也不直接拿存取介面(改動要走用例)
    @Test
    fun viewModelDependsOnUseCasesNotFrameworkOrRepository() {
        scope.classes()
            .filter { it.hasParentWithName("ViewModel") }
            .flatMap { it.primaryConstructor?.parameters.orEmpty() }
            .assertFalse { param ->
                val type = param.type.name.substringBefore('<').substringBefore('?')
                type in forbiddenInViewModel || type.endsWith("Repository")
            }
    }

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

    // DDD 值物件:所有屬性都是 val,也不能用可變集合
    @Test
    fun valueObjectsAreImmutable() {
        scope.classes()
            .filter { it.hasAnnotationWithName("ValueObject") }
            .flatMap { it.properties(includeNested = false) }
            .assertTrue { prop -> prop.isVal && prop.type?.name?.startsWith("Mutable") != true }
    }

    // DDD 聚合根:對外不能有 var 或可變集合,改狀態只能透過自己的方法
    @Test
    fun aggregateRootsHideMutableState() {
        scope.classes()
            .filter { it.hasAnnotationWithName("AggregateRoot") }
            .flatMap { it.properties(includeNested = false) }
            .filter { it.hasPublicOrDefaultModifier }
            .assertTrue { prop -> prop.isVal && prop.type?.name?.startsWith("Mutable") != true }
    }

    // DDD 聚合根:指向別的聚合只能存對方的識別碼,不能直接持有對方物件
    @Test
    fun aggregatesReferenceOthersByIdOnly() {
        val roots = scope.classes().filter { it.hasAnnotationWithName("AggregateRoot") }
        val rootNames = roots.map { it.name }.toSet()
        roots.forEach { root ->
            val others = rootNames - root.name
            root.properties(includeNested = false).assertFalse { prop ->
                val typeName = prop.type?.name.orEmpty()
                val referenced = Regex("[A-Za-z_][A-Za-z0-9_]*").findAll(typeName).map { it.value }.toSet()
                (referenced intersect others).isNotEmpty()
            }
        }
    }
}
```

## 調整與撤除

- 用不到某條(例如專案沒有領域層、ViewModel 直接用 Repository)就刪掉那一行,或加 `[status:superseded]` 並寫 `[被取代:…]`;架構對齊席只看沒作廢的 RULE 行。
- 規則有對應的架構測試(例:下面骨架的 Konsist 測試)時,在那一行加 `[test:<測試名>]`,讓機器守、審查席補看;架構測試不在 `.lumos/config.json` 預設平台的目錄底下時(例如預設平台是儀器測試、架構測試在 app 的單元測試),先在 `platforms` 宣告那個平台,再寫成 `[test:<平台>:<測試名>]`。
- 領域層若拆成純 Kotlin 模組(不套 Android 外掛),第一條由編譯器擋,`domainHasNoAndroidImports` 可以拿掉。
- 到回頭日(`until`)要人裁一次還留不留;過期的規則照樣附給審查席,但會加註「已過 until,待人裁」。
