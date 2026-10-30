severity: major

## F41 清單收檔的「第一個 /src/」修補沒有任何測試資料能分辨新舊寫法
severity: major
blocking: 是
歸因：有證據的修復回歸（修補本身宣稱要擋的錯，測試守不住）
引句:「    name = p.split("/src/", 1)[1] if "/src/" in p else f」
佐證: file: `scripts/test_lumos.py:109700`（`konsist_scans` 與測試資料）；`scripts/lumos` 的 `_arch_tpl_konsist_test`
1. 哪個輸入、走到哪一行：路徑 `feature/cart/src/main/java/src/test/Z.kt`。
   - Konsist 取第一個 `/src/` 之後的段，得到 `main`，所以會掃這支檔，這支檔該進清單。
   - 舊正規式用 `search` 找任一處 `src/<含 test>/`，會把它判成測試而漏收。
   - 漏收的後果是採用後這支舊檔被架構測試當新檔檢查而紅。
2. 測試缺口：`t_arch_template_android_legacy_modes` 的 13 支檔裡沒有任何一支能分辨新舊寫法。
   - 新加的 `src/androidTest/java/x/test/H.kt`，第一個 `src/` 段就是 androidTest，兩種寫法都判成測試。
   - `mysrc/test/Q.kt` 不是以斜線為界的 `src/`，也分辨不出來。
   - 作者的對照判準 `konsist_scans` 寫法不同，但對這批資料的答案跟新函式一樣。
3. 最小重現（改壞而測試照綠）：
   - 修前：把 `_arch_tpl_konsist_test` 的函式本體換回 `return bool(re.search(r"(?:^|/)src/[^/]*test[^/]*/", f, re.I))`。
   - 修後：在修後提交的臨時工作樹跑 `python3.14 scripts/test_lumos.py -k arch_template_android_legacy_modes`。
   - 結果：`8 passed, 0 failed`，F23 的修補等於沒人守。
4. 同一案例的兩版輸出：repo 內有 `feature/cart/src/main/java/src/test/Z.kt`，跑 `lumos arch-template android --scope feature/cart --print legacy --legacy new-only ...`。
   - 修前 83828dd9：清單沒有 Z.kt，漏收。
   - 修後 fa48a3bc：清單有 Z.kt，正確。
   - 所以程式修對了，缺的是釘住它的測試資料。

## F42 沒有 /src/ 的路徑，lumos 照「第一段」判，Konsist 實際判成空字串
severity: minor
blocking: 否
歸因：有證據的修復回歸
引句:「    return "test" in name.split("/", 1)[0].split(":")[-1].lower()」
佐證: file: `com/lemonappdev/konsist/core/provider/KoSourceSetProviderCore$DefaultImpls.getSourceSetName`（反組譯 0.17.3）：`projectPath.substringAfter("/src/").substringBefore("/")`，兩者都沒給缺值時的預設值，所以退回整串。`projectPath` 是絕對路徑去掉根路徑前綴，留著開頭的 `/`。
1. 哪個輸入、走到哪一行：scope `tests/app`，檔案 `tests/app/N.kt`（路徑沒有 `/src/`）。
   - Konsist 的 `substringAfter` 找不到分隔符，退回整串 `/tests/app/N.kt`。
   - 再取第一個 `/` 之前，得到空字串，不含 test，所以會掃這支檔。
   - lumos 走 `else f` 的分支，取第一段 `tests`，判成測試。
   - `_arch_code_file` 對 `tests/` 目錄也回 False，所以這支檔被兩邊都排除。
   - 後果是採用後它被架構測試當新檔檢查。
2. 同一案例的兩版輸出：
   - 修前：清單有 `tests/app/N.kt`，因為舊正規式要有 `src/` 才算測試。
   - 修後：清單沒有它。
   - 函式 docstring 與計劃寫的「沒有 /src/ 就是第一段」跟 Konsist 實際算法不符。
3. 同函式另一處不一致：Konsist 取第一個冒號之後，lumos 的 `split(":")[-1]` 取最後一個冒號之後。目錄名含兩個以上冒號時兩邊不同。多收一支不掃的檔無害，所以只附帶一提。
4. 限制：Konsist 只靠反組譯判斷，沒有實跑。

## F43 測試在 JDK 11 到 16 的機器上轉紅，不是跳過
severity: minor
blocking: 否
歸因：有證據的修復回歸（這段是修補新加的）
引句:「HexFormat hx = HexFormat.of();」
佐證: file: `scripts/test_lumos.py:109418` 附近的 `_ARCH_TPL_JAVA_READER`，與 `_arch_tpl_java_legacy_read` 的 `if r.returncode != 0: return ["java 失敗:" ...]`
1. 哪個輸入、走到哪一行：PATH 上的 `java` 是 JDK 11（`HexFormat` 是 Java 17 才有）。`shutil.which("java")` 找得到，所以不走跳過分支。編譯失敗後 `returncode != 0` 回傳 `["java 失敗…"]`，S8 那條斷言轉紅。
2. 實測：
   - 修後（JDK 11.0.16）：`17 passed, 1 failed`，訊息是 `cannot find symbol HexFormat`。
   - 修前同環境：`16 passed, 0 failed`。
   - JDK 17 兩版都全綠。
3. 影響：預設 java 較舊的開發機，本機閘會被誤擋，而且訊息不指向「java 太舊」。

## 三問與正向主張證據

**①原問題的修復效果有何行為證據？**
- **J1 讀清單的正規式在 Java 的行為：已修復。**
  - input：用 Java 實跑產出 Kotlin 內的 `legacyDoc`，`-Xss512k`，單行與縮排兩種格式的 50000、500000 條清單。
  - expected：讀得進去、不溢位。
  - case_source：我自己寫的 `R.java`，不是作者的測試。
  - before：舊正規式 3000 條就 `StackOverflowError`。
  - after：3000、50000、500000 條都成功，分別約 3、15、103 毫秒。尾逗號、尾巴多一個 `x` 的壞輸入也在 100 毫秒內回「不認」，沒有慢回溯。
  - 歸因：有證據的修復。
- **J1 的 `\z`、佔有式量詞、BOM 三項各自有測試守住。**
  - 方法：逐項改壞後跑 `-k arch_template_android_konsist_legacy_shape`。
  - `\z` 改回 `$`：紅，點名 U+0085、U+2028、U+2029。這要靠 Java 實跑那條才抓得到。
  - `*+` 改回 `*`：紅，5 萬條溢位（`SOE`）。
  - 拿掉 `\uFEFF?`：紅（Python 側與 Java 側都紅）。
- **J2 收檔算法：程式修對，測試沒守。** 見 F41、F42。
- **J3 領域層測試：已修復。** 規則寫的 android、androidx（含 Room）、Retrofit、序列化框架，測試前綴都有對應，且測試釘了這幾個前綴。限制：規則寫的是「序列化框架」，測試只列舉 kotlinx.serialization、moshi、gson、jackson 四種，`org.json` 或 protobuf 不會被擋。這屬於設計上的列舉，沒有另立項。
- **J4 找 repo 根：已修復。** `_lens_repo_root(None)` 在非 git 目錄回 None，走 fail 的 rc 2，行為跟舊寫法一致。

**②修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？**
- 正常路徑：`-k arch_template_android` 修後 90 個斷言全過（JDK 17）。
- 相鄰路徑：空陣列、CRLF、方括號星號、NFD、BOM、尾逗號的既有必讀與必拒清單仍成立，也被 Java 實跑同批輸入驗過。
- 例外：F42（無 `/src/` 的路徑）與 F43（舊 JDK）。
- Kotlin 屬性初始化順序已逐行看過：`scopeDirs`、`repoRoot`、`legacyFiles`、`all`、`scope` 依序，`nfc` 是函式，沒有讀到未初始化的屬性。

**③新發現的同一案例在修前、修後各是什麼結果？**
- F41：Z.kt 修前漏收，修後收；舊寫法改回去，測試仍綠。
- F42：`tests/app/N.kt` 修前收，修後漏；Konsist 實際掃它。
- F43：JDK 11 下修前全綠，修後紅一條。

**未驗範圍**：
- Konsist 沒有實跑，只有反組譯，因為這台機器沒有 kotlinc。
- Gradle 根目錄不等於 repo 根時，`/src/` 位置的差異沒驗。
- 清單檔含非法 UTF-8 時，Kotlin 的 `readText` 會用替代字元讀，lumos 的嚴格讀法會判讀不懂。這只在人手改壞清單時發生，沒有實跑，所以沒有列為發現。
- 64 組開關條件對照計劃〈做法〉9：資料檔逐塊核對過，lite、optional、always、multi 四種語意都對得上，`all_combos` 測試通過，但沒有 64 組逐一實跑。

## 圖譜鏡頭固定席判定
- `lumos-cli-read`（search 排除 superseded）：diff 沒碰 search 路徑，不影響。
- `測試假綠形態`（還原翻紅釘須配前置斷言）：Java 實跑那條有「前置：抽得到兩條正規式」，且逐項改壞會紅，符合。J2 的修補沒有翻紅釘，見 F41。
- `design-loop`、`lumos-cli-lifecycle`、`guard-kill`、`bound-tests-gate`：diff 只新增子命令與模板，沒改這些合約，不影響。
- `pitfalls-code-loop`：沒有碰到那一帶的程式，不影響。
- `授權與歸屬`：新模板 `scripts/templates/android-arch-target.md` 開頭有兩行 SPDX，加進 `_VENDORED_TREE_FILES` 合規。主程式檔頭沒動。LICENSE 沒進白名單。

總結:共 3 條。
