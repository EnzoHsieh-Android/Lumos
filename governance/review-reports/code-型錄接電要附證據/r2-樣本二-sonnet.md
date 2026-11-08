severity: major

我讀了 patch 的樣本與判定表改動,也讀了 worktree 裡的現行樣本檔來看完整內容。我沒有重跑 Android Lint 或 detekt,所以所有「報不報」都照判定表信,只核對樣本寫法、行號與壞寫法欄對不對得上。

**逐支結論(上一輪點名的五處):**
- UI-84:modifier 的預設值拿掉了,現在是 `fun X(modifier: Modifier, text: String)`。照欄,判擋不到。已改正。
- UI-13:改成明確的 `s.value` 讀與寫,第 11、12 行。已改正。
- UI-100:`uiMode = 0x21` 拿掉了。已改正。
- ARCH-71:`intent-filter` 拿掉了,只剩 `exported=true`。已改正。
- DATA-46:判定理由改成「manifest 拿掉 SCHEDULE_EXACT_ALARM 後沒報」,判擋不到。已改正。

**其餘樣本逐支看過、沒挑出問題的:**
- API-23:兩種寫法都放了,UsingHttp 判擋不到合理。
- API-47:程式裡的 `const val` 與 `strings.xml` 都放了。
- API-44:第二種是 targetSdk 23。minSdk 改 23 只是讓它建得起來,不是壞寫法欄沒說的觸發條件。
- ARCH-79:300 對應欄裡的「大於 120」。
- ARCH-88:同時寫 Receiver 與 Service,欄裡本來就寫了「BroadcastReceiver 或 Service」。
- DATA-79:補成 39 字元的金鑰形狀,是照 `…` 佔位補最小真值。網址寫成字串字面值,也照欄抄。
- UI-16:`SimpleDateFormat`、`Regex` 欄裡有。
- UI-23:`getString` 欄裡有。
- UI-3:`delay` 欄裡有。
- UI-87:X 使用 XDefaults,欄裡寫「給 public X 用」。

**接電證據的行號:** 我逐行對過上面這些樣本的判定行號(例如 UI-3 的第 11 行是函式簽名那行,參數 `onTimeout` 宣告在那裡),沒有對不上的。

**型錄計數:** 我數了 〈接電證據〉:248 筆,擋得到 166,擋不到 82,與 patch 的統計行一致。

---

1. UI-54(`ComposeModifierMissing` 與 `modifier-missing-check`):樣本另加了 `Text(title)` 本體才報得出來
severity: major
blocking: 是
- 壞寫法欄(第 3 欄)只寫簽名 `@Composable fun Card(title: String)`。
- 上一輪的判定是本體空的就不報,所以判擋不到。這輪樣本補了 `Text(title)` 這個會發出畫面的本體,兩個標籤都變成擋得到,型錄第 10 欄從「未接」改成「批四」。
- 補一個空的 `{}` 本體才算「讓它編得過」。補 `Text(title)` 是靠「發出 UI」這個欄裡沒寫的觸發條件才報。
- 辯方說法:第 8 欄(形狀)寫了「發出 UI 的 composable」。但規則只認第 3 欄。
- 改法二選一:(a)用空本體重判,擋不到就改回「未接」;(b)把壞寫法欄本身改成帶 `Text(title)` 的寫法。
引句:「報在第 4 行(Slack compose-lint-checks 1.4.2)」
佐證:`skills/kotlin-idioms/checks-catalog.md:381`、`skills/kotlin-idioms/checks-catalog.md:922`、`skills/kotlin-idioms/checks-catalog.md:923`

2. UI-54:第 11 欄(實測狀態)留著舊話,與新判定矛盾
severity: minor
blocking: 否
- 第 11 欄仍寫「真跑沒報 ComposeModifierMissing……本體空的元件不報」。
- 同列 〈接電證據〉 現在判擋得到,同列第 10 欄是批四。理由與判定對不上。
- 若第 1 條改回擋不到,這句才成立,所以兩處要一起處理。
引句:「未測;Android Lint 照這列壞寫法真跑沒報 ComposeModifierMissing(2026-11-08,見〈接電證據〉;本體空的元件不報)」
佐證:`skills/kotlin-idioms/checks-catalog.md:381`、`skills/kotlin-idioms/checks-catalog.md:922`

3. ARCH-25(`UseGetLayoutInflater`):另寫 `DialogFragment` 才報,判成擋得到
severity: major
blocking: 是
- 壞寫法欄只寫 `LayoutInflater.from(requireContext())`,形狀欄寫「Fragment 內」,沒有 DialogFragment。
- 一般 Fragment 版(樣本第 9 行)沒報;只有另寫的 `class D : DialogFragment()`(第 15 行)才報。
- 判定理由自己寫了這點。所以這列靠欄裡沒有的觸發條件才擋得到,型錄第 10 欄改成「批四(CI 範本:Android Lint)」是多宣稱:欄裡那種一般 Fragment 的寫法,CI 擋不到。
- 改法:照欄只留 Fragment 版,判擋不到;或把壞寫法欄改成「DialogFragment 內」再判。
引句:「只報在 DialogFragment 版第 15 行,Fragment 版那行沒報(fragment 1.8.9)」
佐證:`skills/kotlin-idioms/checks-catalog.md:468`、`skills/kotlin-idioms/checks-catalog.md:990`

4. ARCH-39:`WrongStartDestinationType` 判擋不到,但樣本沒寫欄裡的寫法
severity: minor
blocking: 否
- 壞寫法欄第三項是「startDestination 型別不符」,屬文字描述,應照描述寫最小寫法。
- 樣本沒寫,理由也承認「樣本沒有 startDestination」。
- 沒做出該寫法就判擋不到,結論沒有根據。我推測補上會報,但沒驗證。
引句:「樣本沒有 startDestination,沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:482`、`skills/kotlin-idioms/checks-catalog.md:1001`

5. ARCH-40:`MissingKeepAnnotation` 同上
severity: minor
blocking: 否
- 壞寫法欄寫「enum 參數 minify 下沒 `@Keep`」,樣本只有 `data class Detail` 與 `object Home`。
- 缺 enum 參數的寫法就判擋不到。
引句:「樣本沒有 enum 參數,沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:483`、`skills/kotlin-idioms/checks-catalog.md:1002`

6. ARCH-41:`DeepLinkInActivityDestination` 同上
severity: minor
blocking: 否
- 壞寫法欄第二項是「deep link 掛在 activity 目的地」,樣本只有 `navDeepLink { }`。
- 缺那一項就判擋不到。
引句:「樣本沒有 activity 目的地,沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:484`、`skills/kotlin-idioms/checks-catalog.md:1004`

7. ARCH-70:`MutableImplicitPendingIntent` 同上
severity: minor
blocking: 否
- 壞寫法欄第二項是「`FLAG_MUTABLE` 配沒指定元件的 Intent」,樣本只寫了旗標為 0 的那一項。
- 這條檢查針對的就是第二項。這個判擋不到不成立。
引句:「樣本 flags 是 0、沒有 FLAG_MUTABLE,沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:513`、`skills/kotlin-idioms/checks-catalog.md:1015`

8. ARCH-72:`UnsafeImplicitIntentLaunch` 同上
severity: minor
blocking: 否
- 壞寫法欄第二項是「隱式 Intent 對到同一個 App 不外露的元件」,樣本只有 `startActivity(Intent())`。
- 檢查針對第二項,樣本沒寫就判擋不到,結論不成立。
引句:「startActivity(Intent()) 沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:515`、`skills/kotlin-idioms/checks-catalog.md:1019`

9. ARCH-73:`HardcodedAbsolutePath`(另含 `DotPathAttribute`)判擋不到,樣本沒寫欄裡的寫法
severity: minor
blocking: 否
- 壞寫法欄列了「寫死絕對路徑」,樣本沒有。
- `DotPathAttribute` 的樣本把 `path="."` 放在 `<root-path>` 上,同行已被 `ExposedRootPath` 蓋過。欄裡的 `path="."` 是獨立一項,應另放在別的元素上驗。
- 兩個都是樣本窄,不能算檢查擋不到。
引句:「樣本沒有寫死的絕對路徑,沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:516`、`skills/kotlin-idioms/checks-catalog.md:1023`、`skills/kotlin-idioms/checks-catalog.md:1020`

10. ARCH-81:`InlinedApi` 判擋不到,樣本沒寫常數
severity: minor
blocking: 否
- 壞寫法欄寫「API 26 才有的方法或常數」,樣本只有方法 `startForegroundService`。
- `InlinedApi` 針對常數,沒寫常數就判擋不到不成立。
引句:「樣本只有 API 26 方法沒有常數,沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:524`、`skills/kotlin-idioms/checks-catalog.md:1034`

11. ARCH-86:`WrongConstant` 判擋不到,樣本沒寫欄裡的寫法
severity: minor
blocking: 否
- 壞寫法欄第二項是「只收特定常數的參數傳別的整數」,樣本只有 `@IntRange` 與 `getColor(R.string.name)`。
- 判定理由自己承認缺這一項。
引句:「樣本沒有只收特定常數的參數,沒報」
佐證:`skills/kotlin-idioms/checks-catalog.md:529`、`skills/kotlin-idioms/checks-catalog.md:1044`

**另外的觀察(不算 finding):**
- ARCH-79 的 Zero 與 Extended 兩條、ARCH-77 的 `InsecureStickyBroadcastsPermission`,觸發它的那段都是壞寫法欄寫的(0 與 300,`BROADCAST_STICKY` manifest 宣告),判擋得到成立。
- ARCH-84 的 `Instantiatable` 與 `MissingClass` 也成立:A84、`Outer84$Inner`、`Gone84` 都是欄裡的寫法,行號順序與樣本註解的順序一致。但 `P84`(非 public)沒報,判定理由已寫,型錄第 10 欄仍整列標批四。
- PERF-15 的 `NestedWeights`、`InefficientWeight`、`TooDeepLayout` 成立。
- UI-16 的 `LazyListState`、`Paint`、`SimpleDateFormat`、`Regex` 都沒被報,批四只靠其中幾種寫法撐住。
- 這三列(ARCH-84、UI-16、PERF-15)的批四是部分覆蓋,型錄第 10 欄沒交代。

看過 17 支修正樣本與 38 個新候選裡的相關列,共約 50 列(含判定表逐筆行號)。最高等級 major;blocking 2 條(第 1、3 條)。
