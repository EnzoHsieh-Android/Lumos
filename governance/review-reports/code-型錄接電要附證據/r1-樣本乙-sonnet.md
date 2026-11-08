severity: major

我看過 patch 內全部 112 支樣本,對照型錄主表第 3 欄與〈接電證據〉節。判「擋得到」的列逐支看過,判「擋不到」的也全看了。我沒有真跑 Lint 或 detekt,以下都是讀樣本與判定表得到的結論,標「未驗證」的是推測。

1. 列 UI-84(Android Lint 的 ComposeParameterOrder,與 detekt 的 param-order-check 共用同一支樣本)
severity: major
blocking: 是
- 壞寫法欄只寫「modifier 放在必填參數前」,沒有說 modifier 要有預設值。
- 樣本替 modifier 補了 `= Modifier` 才報出來。判定表自己承認這點:「modifier 有預設值才會報。第一版 modifier 沒給預設值,只報 ComposeModifierWithoutDefault」。
- 這正是靠另加的觸發條件才報。兩個標籤的「擋得到」都因此成立,型錄的「批四(CI 範本:Android Lint;推送前:detekt 外掛 compose-rules)」也跟著多宣稱了。
- 要先用沒預設值的版本確認這兩條規則報不報,才能判這一列。
引句:「fun X(modifier: Modifier = Modifier, text: String) {」
佐證:`skills/kotlin-idioms/checks-catalog.md:956`、`skills/kotlin-idioms/checks-catalog.md:957`

2. 列 UI-100(ComposePreviewNaming 與 preview-annotation-naming)
severity: minor
blocking: 否
- 樣本在第一個 `@Preview` 另加了 `uiMode = 0x21`,壞寫法欄寫的是 `@Preview(name = "Dark")`。
- 判定理由沒說這個參數是不是必要。我不知道拿掉會不會報,未驗證。
- 建議拿掉 `uiMode` 重跑一次對照。如果拿掉就不報,這一條要升成 major。
引句:「@Preview(name = "Dark", uiMode = 0x21) @Preview(name = "Light") annotation class DarkLight {」
佐證:`skills/kotlin-idioms/checks-catalog.md:427`、`skills/kotlin-idioms/checks-catalog.md:973`

3. 列 ARCH-79(判擋不到,樣本太窄)
severity: minor
blocking: 否
- 壞寫法欄寫「或大於 120」,是純文字描述。規則要求這種寫法照描述寫最小寫法,但樣本只放了 0。
- 判定理由卻寫「『大於 120』不是程式碼」,把它略過了。
- 應補一個 300 之類的值再跑 ExtendedBluetoothDiscoveryDuration,我猜會報(未驗證)。
- 同一行的 ZeroBluetoothDiscoveryDuration 是 Error 而且報出來了,它登記在型錄第 6 欄,但沒進〈接電證據〉候選。這一列實際擋得到,型錄卻標「未接」,方向安全。
引句:「putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 0)」
佐證:`skills/kotlin-idioms/checks-catalog.md:522`、`skills/kotlin-idioms/checks-catalog.md:1013`

4. 列 ARCH-77(判擋不到)
severity: minor
blocking: 否
- 判定理由自己寫「manifest 那行報了 InsecureStickyBroadcastsPermission」。
- 壞寫法欄第二段就是 manifest 宣告 `android.permission.BROADCAST_STICKY`,這一列有一半壞寫法其實擋得到。
- 候選抽取漏了這一條(第 6 欄的「資安包:A、B」只有第一個帶前綴)。型錄標「未接」是少宣稱,方向安全。
引句:「sendStickyBroadcast(intent)」
佐證:`skills/kotlin-idioms/checks-catalog.md:520`、`skills/kotlin-idioms/checks-catalog.md:1011`

5. 列 ARCH-25(判擋不到)
severity: minor
blocking: 否
- 判定理由說這條檢查「只在 DialogFragment 裡檢查」,所以樣本放一般 Fragment 就不報。
- DialogFragment 也是 Fragment,壞寫法欄標題寫「Fragment 用 LayoutInflater.from(context)」,沒限定一般 Fragment。
- 換成 DialogFragment 的寫法很可能報(未驗證),判擋不到可能過窄。
引句:「LayoutInflater.from(requireContext())」
佐證:`skills/kotlin-idioms/checks-catalog.md:468`、`skills/kotlin-idioms/checks-catalog.md:983`

6. 列 DATA-79(判擋不到)
severity: minor
blocking: 否
- 樣本把壞寫法欄的 `"AIza…"` 連省略號原樣抄進去。
- 判定理由自己說:「"AIza…" 佔位字串不像金鑰;旁證:換成 39 字元真形金鑰就報」。
- 「…」在壞寫法欄是省略,應補成金鑰形狀,補完就報,判擋不到是樣本太窄。
引句:「GenerativeModel(modelName = "…", apiKey = "AIza…")」
佐證:`skills/kotlin-idioms/checks-catalog.md:618`、`skills/kotlin-idioms/checks-catalog.md:1042`

7. 列 UI-87(判擋不到)
severity: minor
blocking: 否
- 壞寫法欄寫「`internal object XDefaults` 給 public `X` 用」。
- 樣本的 X 完全沒用到 XDefaults,判定理由也承認「X 沒有實際用到 XDefaults」。
- 缺了「給 X 用」這一半,樣本可能偏窄。
引句:「internal object XDefaults {」
佐證:`skills/kotlin-idioms/checks-catalog.md:414`、`skills/kotlin-idioms/checks-catalog.md:960`

8. 列 ARCH-88(判擋不到)
severity: minor
blocking: 否
- 壞寫法欄寫「指向 BroadcastReceiver 或 Service」,樣本只放了 Receiver。
- receiver 內改用 `Class.forName` 指到字串路徑的 Activity,不寫成 `Shell76::class.java`。這可能讓檢查解析不到目標,導致 NotificationTrampoline 沒報(未驗證)。
- 同一段另報了 LaunchActivityFromNotification(Warning),代表這個壞寫法確實被別的檢查抓到。
引句:「context.startActivity(Intent(context, Class.forName("wiring.shell.Shell76")).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))」
佐證:`skills/kotlin-idioms/checks-catalog.md:531`、`skills/kotlin-idioms/checks-catalog.md:1022`

9. 列 ARCH-71(判擋得到,manifest 外殼多了條件)
severity: minor
blocking: 否
- 判定理由寫:「manifest 外殼把這個 Activity 設成 exported=true,帶 intent-filter」。
- 壞寫法欄只說「外露元件」。exported 可算外露的描述,但 intent-filter 是額外加的。
- 外殼不在 patch 內,看不出 intent-filter 是不是報出來的必要條件。建議拿掉 intent-filter 對照一次。
引句:「startActivity(intent.getParcelableExtra<Intent>("next"))」
佐證:`skills/kotlin-idioms/checks-catalog.md:514`、`skills/kotlin-idioms/checks-catalog.md:1004`

10. 列 DATA-46(判擋得到,manifest 多宣告權限)
severity: minor
blocking: 否
- 判定理由寫「manifest 宣告了 SCHEDULE_EXACT_ALARM」,壞寫法欄只說「沒檢查 `canScheduleExactAlarms()`」。
- 沒宣告時 ScheduleExactAlarm 報不報我不確定(未驗證)。如果只有宣告後才報,這就是另加的觸發條件。
- 建議移除宣告對照一次。
引句:「am.setExact(AlarmManager.RTC_WAKEUP, t, pi)」
佐證:`skills/kotlin-idioms/checks-catalog.md:585`、`skills/kotlin-idioms/checks-catalog.md:1036`

沒有列入 finding 的另加內容,我認為屬於「補參數、外層宣告讓它編得過」,不算額外觸發條件:
- 建構子參數(ARCH-16、ARCH-21、ARCH-22、ARCH-36)。
- `@Serializable`(ARCH-39,否則 `navigate(Profile)` 編不過)。
- `@Composable` 與 `TODO()`(UI-78、UI-83)。
- UI-88 改用 import 才會報,判定表已誠實交代第一版沒報。

看過的列編號數:112 列。
最高等級 major;blocking 1 條。
