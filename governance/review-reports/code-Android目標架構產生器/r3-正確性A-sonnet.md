severity: major

## F21 產出的 Kotlin 讀舊檔清單的正規式在清單約 2300 條以上時丟 StackOverflowError
severity: major
blocking: 是
歸因：有證據的修復回歸（修前是逐字元迴圈，沒有條數上限；修後改成整份文件一條帶重複群組的正規式。修前 Kotlin 無法在此環境編譯，我用 Java 逐行移植該迴圈來跑，所以「修前」是移植結果，不是原檔實跑）
引句:「val legacyDoc = Regex("""^[ \t\r\n]*\{[ \t\r\n]*\x22files\x22[ \t\r\n]*:[ \t\r\n]*\[[ \t\r\n]*((?:\x22[^\x22\\\x00-\x1F]*\x22(?:[ \t\r\n]*,[ \t\r\n]*\x22[^\x22\\\x00-\x1F]*\x22)*)?)[ \t\r\n]*\][ \t\r\n]*\}[ \t\r\n]*$""")」
佐證: file: `scripts/templates/android-arch-target.md:readLegacyFiles`（開關資料檔，修後版）；計劃〈做法〉4 寫「清單沒有條數上限」。

失敗場景：
1. 輸入：`--legacy new-only` 產出的 `.lumos/arch-legacy.json`，範圍內 git 已追蹤的 .kt、xml、gradle、png 等超過約 2300 支。範圍包含資源檔，中型 app 的單一模組就會到這個量。
2. 路徑：`private val legacyFiles = readLegacyFiles(...)` 在類別初始化時呼叫 `legacyDoc.find(text)`。外層 `(?:...)*` 的內容是變長的，Java 的 java.util.regex 對它每一輪遞迴一層，所以堆疊深度跟條數成正比。
3. 結果：丟 `StackOverflowError`（Error，不是 Exception），類別初始化失敗，整份架構測試紅。訊息是 ExceptionInInitializerError，不是「形狀不認」的說明。使用者拿到的清單是 lumos 自己產的、合法的。
4. 同一份文字 Python 的 `re` 不遞迴，所以工具鏈那支「把正規式抽出來在 Python 跑」的測試永遠看不到。「Java 與 Python 同義」只涵蓋語法，不涵蓋資源行為。

兩版證據（同一案例：條目形如 `"feature/cart/src/main/java/com/example/ClassN.kt"`，一行一條）：
- 修後：把資料檔裡的 `legacyDoc` 原文抽出，用 JDK 17 的 `java.util.regex.Pattern` 跑（預設堆疊）。100 條、1000 條回 true。二分查出 2274 條是上限，3000、5000、10000、50000 條都丟 StackOverflowError。
- 修前（Java 移植版）：同樣的案例，50000 條解析成功，輸出 `before-port entries 50000`。
- 最小重現：Java 的 Pattern.compile(上面那條原文) 加上 3000 條清單，呼叫 `matcher(s).find()`。

## F22 Kotlin 與 lumos 對清單尾端的換行判法不同（`$`）
severity: minor
blocking: 否
歸因：有證據的原有漏查（正規式是修補新寫的，但修前的逐字元讀法也比 lumos 寬；兩版查證只靠程式碼比對，修前 Kotlin 未跑）
引句:「[ \t\r\n]*\][ \t\r\n]*\}[ \t\r\n]*$""")」
佐證: file: `scripts/templates/android-arch-target.md:readLegacyFiles`；檔案內註解與 `Systems/android-arch-template` 都宣稱「不會比 lumos 寬」。

失敗場景：
1. 輸入：手改過的清單，結尾是 `}` 加 U+2028、U+0085 或 U+2029（編輯器貼上或換行轉換造成）。
2. 路徑：Java 的 `$` 在非 MULTILINE 下，會比對到「最後一個行結束符之前」，行結束符包含這三個字元。Python 的 `$` 只認 `\n`。
3. 結果：Kotlin 的 `find` 回成功，架構測試照清單跳過舊檔。lumos 的 `json.loads` 回 "Extra data"，清單整份不起作用，改動檔全照目標審。兩邊判法相反，正是這條修補想消除的分岔。
4. 工具鏈測試的 `must_reject` 沒有這類輸入，而且只在 Python 跑，看不到。

證據（同一案例 `'{"files":["a"]}' + 尾字元`）：
- 修後 Java：尾字元為 `\n`、U+2028、U+0085、U+2029 時 `find()` 都回 true（`\u000B` 回 false）。
- 修後 Python，抽出的同一條正規式加 `json.loads`：`\n` 時兩者都成功；U+2028、U+0085、U+2029 時正規式回 None，`json.loads` 丟 ValueError。
- 修前：逐字元迴圈只讀到第一個 `]` 就 return，不看後面。比 lumos 更寬，且沒有被這條修補修好。

## F23 舊檔清單收檔的「大小寫」半邊沒有測試釘住
severity: minor
blocking: 否
歸因：未判定（修補同時新寫程式與測試。我只對修後版做了改壞實驗；修前沒有這個函式，沒有可比對的版本）
引句:「_ARCH_TPL_KONSIST_TEST_RE = re.compile(r"(?:^|/)src/[^/]*test[^/]*/", re.I)」
佐證: file: `scripts/test_lumos.py:t_arch_template_android_legacy_modes`（測試裡的 `konsist_scans` 把同一條正規式又寫了一次）。

失敗場景：
1. 輸入：`feature/cart/src/androidTest/java/x/test/H.kt`。路徑有 `test/` 段，`_arch_code_file` 回 False。原始碼集 androidTest 在 Konsist 的 `isTestSourceSet`（轉小寫、比對 `.*test.*`）下是測試，不掃。S3 規定兩邊都不看的不收。
2. 路徑：`_arch_tpl_legacy_file` 靠 `re.I` 認出 androidTest。把 `re.I` 拿掉，它會被收進清單。
3. 測試資料裡沒有「測試原始碼集底下又有 test 段」的檔。androidTest/B.kt、integrationTest/I.kt 都因為 `_arch_code_file` 為 True 而被另一邊收進來，所以拿掉 `re.I`，整個子集仍是 `8 passed, 0 failed`。
4. 影響較小：清單多出不會被掃的條目，不會有漏掃。但違反 S3 寫的「兩邊都不看的不收」。測試裡的 `konsist_scans` 還是實作的拷貝，不是獨立判準。

兩版證據（同一案例 H.kt）：
- 原修後：`_arch_tpl_legacy_file(H.kt)` 回 False。
- 拿掉 `re.I` 的改壞版：回 True。
- 改壞版跑 `python3.14 scripts/test_lumos.py -k arch_template_android_legacy_modes`：8 passed, 0 failed。

## F24 領域層規則寫了 Retrofit 與序列化框架，綁的測試只擋 android 與 androidx
severity: minor
blocking: 否
歸因：未判定（這條規則與測試在本輪修補差異外；我沒有跑修前版，不能說誰引入）
引句:「RULE:domain 套件是純 Kotlin:不 import android、androidx、Room、Retrofit 或序列化框架的型別,也不收 Context。」
佐證: file: `scripts/templates/android-arch-target.md`（`domainHasNoAndroidImports` 測試塊：`it.name.startsWith("android.") || it.name.startsWith("androidx.")`）。

失敗場景：
1. 輸入：domain 套件的檔案寫 `import retrofit2.Response` 或 `import kotlinx.serialization.Serializable`。
2. 路徑：規則帶 `[test:domainHasNoAndroidImports]`。節點內文說「帶 `[test:]` 的規則由架構測試守，其餘留給審查席」，審查席因此會當它已被機械守住。
3. 結果：測試只比對 `android.`、`androidx.` 前綴，這兩種 import 都過，測試綠。Room 因為在 androidx.room 底下才被擋到。

兩版證據：未判定，沒有修前版比對。我只讀了修後的資料檔原文。

---

## 三問與正向主張

**① 原問題的修復效果**
- 「Kotlin 讀得進去，json.loads 一定讀得進去」：對一批輸入成立，包含尾逗號、前逗號、少逗號、多欄位、巢狀、跳脫、控制字元、非字串、NBSP、尾巴多字。我跑了 `python3.14 scripts/test_lumos.py -k arch_template`，在修後版 88 passed, 0 failed。但 F22 的 U+2028、U+0085、U+2029 結尾輸入推翻了「一定」。
- 舊檔清單收檔：
  - 修後 `want` 含 `mysrc/test/Q.kt` 與 `src/integrationTest/.../I.kt`，不含 `src/test`、`.md`、`cartx`。測試通過。
  - 我另外查了 Konsist 0.17.3 的 jar：`scopeFromProduction` 用 `file.sourceSetName` 呼叫 `isTestSourceSet`。該函式把名稱轉小寫（Locale.ROOT），先取 `:` 之後的部分，再比對 `.*test.*`。作者的描述與此一致。
  - 源碼集名稱的取法是 `projectPath` 先取 `/src/` 之後，再取到第一個 `/` 之前（Kotlin 的 substringAfter 預設缺分隔時回原字串）。這是第一個 `/src/` 之後那段。本修補的正規式是在整條路徑任何位置搜尋，兩者在「路徑裡 `/src/` 出現不只一次」時可能不同。我沒有造出可信的真實檔名，這部分未驗。

**② 修補處的正常、錯誤與相鄰呼叫路徑**
- 正常路徑（空陣列、CRLF、BOM、方括號星號、NFD、產生器寫出的清單）成立，證據在上一項的 88 通過。
- 錯誤路徑：形狀不對時 `error(...)` 帶說明訊息，成立。大清單時沒有說明、直接 SOE，這是 F21。
- 相鄰路徑：
  - 初始化順序：`readLegacyFiles` 是函式、正規式在函式內建立，不依賴還沒初始化的欄位。`legacyFiles` 在 `all`、`scope` 之前。成立。
  - `$` 在 Kotlin 原始字串：`$` 之後接 `"`，不會被當成樣板，成立。
  - 清單檔名過濾：`_path_special_chars` 的 Cc、Cf、Zl、Zp 完全涵蓋正規式拒收的字元，成立。
  - Java 和 Python 對 `\x22`、`\x00-\x1F`、字元類裡的 `\\` 的語意一致：我用 Java 17 直接跑出的接受與拒絕結果與 Python 一致，除了 F22 與 F21。

**③ 新發現的修前、修後**
- F21：修前（Java 移植版）50000 條成功，修後 3000 條起丟 SOE。
- F22、F23、F24：見各自的證據欄。

**已驗主張的證據（claim、input、expected、case_source、before、after、comparison）**
- claim：產生器寫出的合法清單，Kotlin 讀得進去。
  - input：100、1000 條的清單。
  - case_source：我自建。
  - before：移植版迴圈成功。
  - after：Java 正規式成功。
  - comparison：兩版一致。這個主張在 ≥2274 條時不成立（見 F21）。
- claim：`mysrc/test/Q.kt` 回到清單。
  - input：`_arch_tpl_legacy_file`。
  - after：True。
  - before：未驗，沒有修前版的跑法。

**未驗範圍**
- 沒有 kotlinc，所有 Kotlin 行為都是用 Java 17 的 Pattern 加 Python 近似推得。Gradle 測試執行緒的實際堆疊大小未量（我用預設 1MB）。
- 名稱碰撞（含 `/src/` 兩次以上的路徑）與 Python re.I 的 Unicode 大小寫摺疊（如 ſ）和 Konsist 的 toLowerCase(ROOT) 的差異，未驗。
- 64 組條件與計劃〈做法〉9 的逐項對照，我只靠 `t_arch_template_android_all_combos` 通過來信任，沒有獨立對一次。

## 圖譜鏡頭固定席判定
- `lumos-cli-read`、`測試假綠形態`、`design-loop`、`lumos-cli-lifecycle`、`guard-kill`、`bound-tests-gate`、`授權與歸屬`：這份 diff 只新增 `cmd_arch_template` 與資料檔，另在 `_VENDORED_TREE_FILES` 加一行。不碰 search 的 superseded 篩選、re-inject 的 sentinel、guard kill 的 rc 優先序、處置閘第五步，也沒有授權檔進白名單。判不影響。
- `授權與歸屬` 要求的 SPDX 兩行：新資料檔頭有。
- `bound-tests-gate` 的綁定測試要真跑：本次新增的測試我已跑，88 通過。
- `測試假綠形態`：F23 屬於「改壞照綠」類。還原翻紅釘的前置斷言這條，在 F23 的測試資料中沒有走到被測分支，與其方向一致。
- `pitfalls-code-loop`、`arch-alignment-lens`、其餘超出上限只列名的節點：未讀，無法判定。

總結:共 4 條
