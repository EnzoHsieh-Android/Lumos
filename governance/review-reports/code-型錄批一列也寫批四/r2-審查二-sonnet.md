severity: major

## 摘要
- 修補差異本身沒有回歸。
- 抓到一列(STATE-5)是這次新標批四,但那條現成檢查擋不到它的壞寫法。
- 兩處說明文字沒跟著 `_B4_SKIP` 更新。

## 查證

**1. `_B4_SKIP` 多三個字,全型錄重算。** 我載入 `configs/ast-grep/kotlin-android/check.py`,對 532 列用舊四字與新七字各算一次接電標籤。
- 結果不同的只有 UI-1、TEST-23、PERF-2,三列已退回只標批一。
- 含這三字的段落只有 4 處:UI-1 兩段、TEST-23、PERF-2,外加 CO-2 的「Sonar 相關規則代號待查」。CO-2 那段本來就含「待查」,沒有誤排除。
- 逐段比對沒有互相影響:UI-1 那段「(相關:…)」括號內沒有「;」「、」,不會被切散。
- `catalog_problems()` 回傳空。
- `python3.14 scripts/test_lumos.py -k kt_catalog_batch4`:24 passed。

**2. 抽查留下批四的列,共 6 列。** 我讀了 googlesamples 的檢查頁。
- UI-10(`vm-injection-check`)、UI-16(`UnrememberedMutableState`)、ARCH-16(`FragmentLiveDataObserve`)、ARCH-44(`StaticFieldLeak`):擋得到壞寫法,沒問題。
- UI-3:`cr:compose:lambda-param-in-effect` 只管 lambda 參數,擋得到一部分,「只管」照算,合口徑。
- API-9:`UnsafeRepeatOnLifecycleDetector` 管 Fragment 用 `lifecycleScope` 而非 `viewLifecycleOwner`,只部分相關,可接受。
- STATE-5、ARCH-17 見下面的 finding。

**3. 測試。** 新增的單元斷言與型錄複本改壞斷言都實際約束了 `_B4_SKIP` 的三個字,沒找到改壞而照綠的情形。
- 拿掉任一字,對應的單元斷言就紅。
- 三列的註記被刪掉時,S4 逐列比對會報。

## Findings

### 1. STATE-5 的批四標籤沒有對應的現成檢查
file: `skills/kotlin-idioms/checks-catalog.md`(STATE-5 列)
severity: major
blocking: 是

STATE-5 的現成規則欄裡,唯一被口徑認得的規則碼是 `androidx:RepeatOnLifecycleWrongUsage`,所以 `batch4_expected_tags` 回傳 Android Lint。其他段(`SC … lint …`、`detekt:ForbiddenMethodCall`)的前綴都不在 `_B4_LINT`,不貢獻標籤。

這條檢查擋不到 STATE-5 的壞寫法。官方檢查頁寫的是「repeatOnLifecycle 應在 Activity 的 `onCreate`、Fragment 的 `onViewCreated` 呼叫」,管的是 `repeatOnLifecycle` 放錯生命週期方法。STATE-5 的壞寫法是 `collectAsState()`,以及 `lifecycleScope.launch { flow.collect {} }` 沒包 `repeatOnLifecycle`,也就是根本沒呼叫它。

這跟上一輪退回的 TEST-23、UI-1、PERF-2 是同一類:現成檢查擋不到這列,卻寫成接電。照型錄說明做的人會以為接了 CI 範本就擋得住這條壞寫法。

最小重現(標籤由規則欄機械算出,但「擋不到」要靠上述檢查頁判斷,沒有指令能翻紅):

```
python3.14 -c "import importlib.util as u;s=u.spec_from_file_location('c','configs/ast-grep/kotlin-android/check.py');m=u.module_from_spec(s);s.loader.exec_module(m);print(m.batch4_expected_tags('androidx:RepeatOnLifecycleWrongUsage;P18 現成規則待查'))"
```

輸出 `['CI 範本:Android Lint']`。

建議在該段補「(相關:只管 repeatOnLifecycle 放錯生命週期方法,擋不到沒包)」並退回只標批一,與 UI-1 一致。

引句:「告警帶寫法=批一、批四(CI 範本:Android Lint)」
引句:「androidx:RepeatOnLifecycleWrongUsage;P18 現成規則待查」

佐證:
- 官方檢查頁 `https://googlesamples.github.io/android-custom-lint-rules/checks/RepeatOnLifecycleWrongUsage.md.html`
- file: `skills/kotlin-idioms/checks-catalog.md`(STATE-5 列)

### 2. 函式說明與錯誤訊息還是舊的四個字
file: `configs/ast-grep/kotlin-android/check.py:127`、`configs/ast-grep/kotlin-android/check.py:358`
severity: minor
blocking: 否

`batch4_expected_tags` 的 docstring 寫「而且那段不含待查、預設關、相近、opt-in」。`_batch4_problems` 的錯誤訊息寫「口徑判成還沒接上(預設關、opt-in、待查或沒有規則碼)」。實際排除字是七個,型錄〈輸入與口徑〉已經寫了七個。

具體場景:有人看到自檢報「寫了接電標籤但口徑判成還沒接上」,按訊息只去找預設關、opt-in、待查,找不到原因,其實是那段含「相關」。

引句:「而且那段不含待查、預設關、相近、opt-in,規則碼」
引句:「口徑判成還沒接上(預設關、opt-in、待查或沒有規則碼)」

佐證:file: `configs/ast-grep/kotlin-android/check.py:119`

### 3. ARCH-17 的「只管」註記撐起整個批四標籤
file: `skills/kotlin-idioms/checks-catalog.md`(ARCH-17 列)
severity: minor
blocking: 否

ARCH-17 的壞寫法是 `lifecycleScope.launchWhenStarted { flow.collect {} }`。唯一貢獻標籤的 `androidx:UnsafeLifecycleWhenUsage` 只在 `finally`/`catch` 裡碰 UI 時才報。單純呼叫 `launchWhenStarted` 並不會被擋。

註記寫了「只管…」,依口徑照算,所以沒違反規則。但寫成「批一、批四」,會讓人以為這個棄用 API 的呼叫本身被擋。這條標 minor,是因為口徑明講「只管」照算;若要更準,可在註記加上「不管單純呼叫」。

引句:「androidx:UnsafeLifecycleWhenUsage(只管 finally/catch 碰 UI)」

佐證:官方檢查頁 `https://googlesamples.github.io/android-custom-lint-rules/checks/UnsafeLifecycleWhenUsage.md.html`

## 圖譜鏡頭
- `Systems/kotlin規則包.md` [家],牽連 `check.py`:不破壞合約,它記的是型錄自檢行為,這次是口徑擴充。
- `Systems/測試假綠形態.md` ★INVARIANT★(還原翻紅釘要有前置斷言):新增斷言有前置檢查(`i_b1cr` 用 `next(...)` 找不到會直接丟錯,不會靜默略過),不影響。
- 其餘固定席節點(授權與歸屬、lumos-cli-read、design-loop 等)只因牽連 `scripts/test_lumos.py` 列入。這次只在 `t_kt_catalog_batch4_wiring` 加斷言,不碰它們宣稱的行為。

## 角色鏡頭
後端卡 `be-api-compat`、`be-authz`:這次改的是型錄與自檢腳本,沒有對外 API 欄位,也沒有端點授權,兩題不適用。

最高等級 major;blocking 1 條(finding 1)
