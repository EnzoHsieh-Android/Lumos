severity: minor

我只讀樣本、型錄主表第 3 欄和判定表,沒有重跑 Android Lint 或 detekt。判定結果(報或沒報)照判定表信,我只核對樣本寫法、行號和理由對不對得上。

**逐支結論(10 支都判照欄寫,沒有另加壞寫法欄沒說的觸發條件)**
- **UI-54**:`@Composable fun Card(title: String) {}`,只補了 `import androidx.compose.runtime.Composable` 和空本體。上一輪另加的 `Text(title)` 已拿掉。判擋不到,和第 10 欄「未接」、第 11 欄「本體空的元件不報」一致。
- **ARCH-25**:只剩 `class F : Fragment()` 裡的 `LayoutInflater.from(requireContext())`,DialogFragment 版已拿掉。判擋不到,理由與樣本對得上。
- **ARCH-39**:欄裡三項都寫到了。`navigate(Detail::class)` 在第 13 行,`navigate(Profile)`(Profile 有參數)在第 14 行,`createGraph(startDestination = Profile)` 在第 18 行。第三項是文字描述,這樣寫是最小寫法。行號 13、14、18 我逐行數過,對得上。
- **ARCH-40**:判無 major。
  - 欄裡明寫 `data class Detail(val id: Long)` 和 `object Home` 當路由沒有 `@Serializable`。「當路由」要成立,就得有 `composable<Detail>` 和 `composable<Home>` 把它們當路由用,這是同一條子句的最小外殼。
  - 欄裡另一項「enum 參數 minify 下沒 `@Keep`」是文字描述。要有「enum 參數」,就得有一個帶 enum 欄位的路由類別(`Filter(val kind: Kind)`)。`Kind` 沒有 `@Keep`,所以欄裡寫的內容有寫到。
  - `Filter` 上的 `@Serializable` 是讓它成為合格的型別安全路由用的,不是在製造欄外的壞寫法。
  - 判定表的理由「報在第 9 行 enum class Kind」和第 5、7 行 Detail、Home,與樣本對得上。
  - 小提醒:判定理由沒說明 `Filter` 不加 `@Serializable` 時 `MissingKeepAnnotation` 報不報。這是推測,我沒驗證,不列為發現。
- **ARCH-41**:`navDeepLink { }`(第 6 行)和 `activity("a") { deepLink(...) }` 兩項都寫到了。下面第 1 條提一個疑點。
- **ARCH-70**:`getActivity(ctx, 0, intent, 0)`(第 6 行)和 `FLAG_MUTABLE` 配 `Intent()`(第 7 行)都寫到了,行號對得上。
- **ARCH-72**:`startActivity(Intent())`(第 8 行)和 `Intent("wiring.arch_72.OPEN")`(第 9 行)都寫到了。`Target72` 加 manifest 宣告 `exported=false` 加 intent-filter,這是欄裡第二項「隱式 Intent 對到同一個 App 不外露的元件」的最小外殼。沒有 intent-filter,隱式 Intent 就沒有對象。獨立模組是真跑環境的外殼,不是樣本多加的壞寫法。判定理由與樣本對得上。
- **ARCH-73**:欄裡的項目都有寫到,行號 3、4、5、6 和 manifest 的 `grant-uri-permission` 都對得上。
  - `root-path` 的 `path="."`、`files-path` 的 `path="/"`、`grant-uri-permission` 的 `path="/"` 都在。
  - 新補的 `cache-path` `path="."` 對應欄裡獨立列出的 `path="."`,新補的絕對路徑對應「寫死絕對路徑」。
  - 判定表說 root-path 上的 `path="."` 不報 DotPathAttribute,補一個非 root-path 的 `path="."` 是照欄的合理寫法。
- **ARCH-81**:`startForegroundService`(第 7 行,API 26 方法)和 `View.AUTOFILL_TYPE_TEXT`(第 12 行,API 26 常數)兩項都寫到了,與欄裡「方法或常數」相符。
- **ARCH-86**:判無 major。欄裡三項都寫到了:`@IntRange` 傳 20(第 14 行)、`getColor(R.string.name)`(第 7 行)、「只收特定常數的參數傳別的整數」(第 25 行 `m(3)`)。第三項是文字描述,要有「只收特定常數的參數」就得有 `@IntDef` 標的參數,所以 `@IntDef(1, 2)`、`annotation class Mode` 加 `m(@Mode x: Int)` 是最小寫法。`@Retention(SOURCE)` 是 IntDef 標註的慣例外殼,不是額外條件。

**通電批次改動**
ARCH-25、UI-54 改回「未接」,與判定表的「擋不到」一致。ARCH-39、40 維持批四,ARCH-41 維持批四(因 EmptyNavDeepLink 擋得到)。ARCH-70、72、73、81、86 的批四與判定表一致。

1. ARCH-41 `DeepLinkInActivityDestination`:判擋不到,但只試了 Kotlin DSL 寫法
severity: minor
blocking: 否
- 欄裡寫的是「deep link 掛在 activity 目的地」,沒限定是 DSL 還是 XML 導航圖。
- 樣本只寫了 `activity("a") { deepLink("app://a") }` 這一種,真跑沒報就判整列擋不到。
- 我沒查到這條規則的原始碼,所以推測它可能只看導航 XML 資源。**這是推測,不是驗證。** 若成立,CI 在 XML 導航圖上其實擋得到,「擋不到」就判得太保守。
- 同一批的 ARCH-73 已經在 `.kt.txt` 裡內嵌 XML,有先例可循。
- 改法:補一份 `<activity>` 內含 `<deepLink>` 的導航 XML 重跑。若報,改判擋得到。若沒報,在理由裡寫明已試過兩種寫法。
引句:「NavGraphBuilder.activity("a") { deepLink("app://a") } 沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:484`、`skills/kotlin-idioms/checks-catalog.md:1004`、`configs/ast-grep/kotlin-android/samples/lint-wiring/ARCH-41.kt.txt:10`

看過的列數:10 支樣本、10 列型錄主表壞寫法欄、19 列判定表改動、通電批次與計劃筆記修正紀錄各 1 處。最高等級 minor;blocking 0 條。
