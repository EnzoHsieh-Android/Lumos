severity: major

## F51 清單收檔的 Konsist 判法(J2)改寫後,測試資料沒有一筆能分辨新舊算法,改回舊正規式測試照綠
severity: major
blocking: 是
歸因:有證據的原有漏查(r3 要修的症狀「多個 src/ 段時新舊判法不同」在修前、修後都沒有測試釘住;修補沒有補上)

引句:「                f"{sc}/src/androidTest/java/x/test/H.kt", "feature/cartx/src/main/java/x/Z.kt"):」
佐證:file: `scripts/lumos:57913`(`_arch_tpl_konsist_test`,取第一個 `/src/` 之後那段)

1. 新增的 `H.kt` 路徑是 `src/androidTest/.../test/H.kt`。舊正規式 `(?:^|/)src/[^/]*test[^/]*/` 與新算法對它都判「測試」,所以它分不出新舊。
2. 新舊判法只在「路徑出現兩個以上 `/src/` 段」時不同。測試資料裡最接近的 `src/main/java/mysrc/test/Q.kt` 沒有第二個 `/src/` 段(`mysrc` 前面不是斜線),新舊都判「會掃」。
3. 具體輸入:`feature/cart/src/main/java/x/src/test/Q.kt`。
   - 舊正規式判「測試、不掃」,檔不進清單。
   - 新算法取第一個 `/src/` 之後的 `main`,判「會掃」,檔進清單。
   - 這就是 J2 要修的行為差異。
4. 實測:我在修後工作樹把 `_arch_tpl_konsist_test` 的回傳換回舊正規式,跑 `python3.14 scripts/test_lumos.py -k arch_template_android_legacy_modes`,結果 8 passed, 0 failed,測試照綠。
5. 測試裡 `konsist_scans` 用同一份 Konsist 描述重寫,但沒有任何一筆資料讓它和舊寫法分歧。「獨立判準」成立,可是沒有分辨力。
6. 為什麼會出錯:舊算法的實作若回來,多 `/src/` 段的正式 `.kt` 檔會漏出清單,採用後被架構測試掃到而變紅。
7. 最小補法:在 `legacy_modes` 的檔案清單加一筆 `f"{sc}/src/main/java/x/src/test/Q.kt"`,並把期望清單與 `len(tracked) == 13` 同步改。

證據:
- claim:J2 已把判法換成「第一個 /src/ 之後那段」。
- input:`feature/cart/src/main/java/x/src/test/Q.kt`。
- expected:會掃,因此在清單上。
- case_source:本席依 Konsist 描述(計劃與 Systems 筆記所寫)自擬。
- before:修前 83828dd 的碼就是舊正規式,判「測試」。我沒有另外在 83828dd 跑測試。
- after:新算法判「會掃」。把碼改回舊正規式後,同一個測試照綠(上面 4. 的實測)。
- comparison:程式行為有差(Python 一行直接比出 old=True、new=False),測試輸出沒差,所以修補的測試沒有分辨力。

## F52 用真的 Java 跑那段:機器上的 java 不能用時直接紅,逾時卻被當成「沒有 java」默默跳過
severity: minor
blocking: 否
歸因:有證據的修復造成(修前 83828dd 沒有這段 Java 實跑,修後才有)

引句:「    except (OSError, subprocess.TimeoutExpired):」
佐證:file: `scripts/test_lumos.py`(測試檔裡 `_arch_tpl_java_legacy_read`,patch 第 784 行)

1. 計劃與測試的設計是「沒有 java 就印一行跳過」,判斷只用 `shutil.which("java")`。
2. macOS 沒裝 JDK 時 `/usr/bin/java` 是存根,`which` 找得到,執行回 rc 1,走到 `return ["java 失敗:" + ...]`。
3. 實測:我在 PATH 前面放一支印出 "Unable to locate a Java Runtime" 並 `exit 1` 的假 `java`,跑 `-k arch_template_android_konsist_legacy_shape`。結果 17 passed, 1 failed,紅的是「S8:真的 Java 跑同一批輸入…」。
4. 結果是沒裝 JDK 的 macOS 開發機被誤擋推送,與「沒有 java 就跳過」的說法不一致。
5. 反方向:`subprocess.TimeoutExpired` 與 `OSError` 回 `None`,呼叫端會印「這台機器沒有 java,跳過…」。120 秒逾時(例如 CI 很慢、5 萬條)因此被當成沒有 java,守衛靜默失效,訊息還說錯原因。
6. CI 的 `.github/workflows/ci.yml` 沒有 `setup-java`,靠 ubuntu-latest 映像內建的 java。映像移除 java 時,這個守衛同樣只印一行就跳過。

證據:
- claim:有 java 才實跑,否則跳過。
- input:PATH 上的 `java` 執行失敗(rc 1)。
- expected:跳過。
- case_source:本席自擬。
- before:83828dd 沒有這段測試,無從比較。
- after:紅。
- comparison:屬修補新引入的環境相依;逾時那條路只由讀碼得出,我沒有實際跑出逾時。

## F53 技能文件說「領域層拆成純 Kotlin 模組可拿掉 domainHasNoAndroidImports」,但這支測試現在還擋 Retrofit 與序列化框架
severity: minor
blocking: 否
歸因:未判定(那句話修前就有,見下;J3 擴大了測試範圍,讓這句更不準)

引句:「- 領域層若拆成純 Kotlin 模組(不套 Android 外掛),第一條由編譯器擋,`domainHasNoAndroidImports` 可以拿掉(連同節點那一行的 `[test:]`)。」
佐證:file: `scripts/templates/android-arch-target.md:27`(RULE 寫 Retrofit 與序列化框架,綁 `domainHasNoAndroidImports`)

1. J3 把 `domainHasNoAndroidImports` 擴成擋 `retrofit2.`、`kotlinx.serialization.`、moshi、gson、jackson。
2. 純 Kotlin 的 JVM 模組可以照常依賴這些函式庫,編譯器不會擋。
3. 照文件把測試與 `[test:]` 拿掉,Retrofit 與序列化框架這部分的機械守衛就消失,RULE 行還在宣稱它們不得出現。
4. 修前 83828dd 的文件已有「可以拿掉」那句,當時測試只擋 android,所以那句當時更不準。

證據:
- claim:技能文件的「可以拿掉」與規則/測試範圍一致。
- input:`core/domain` 是純 Kotlin 模組,內有 `import retrofit2.Call`。
- expected:`domainHasNoAndroidImports` 仍紅。
- case_source:本席自擬。
- before:測試只擋 android,同樣擋不到 Retrofit。
- after:測試擋得到,但依文件被拿掉。
- comparison:只由讀碼得出,我沒有跑 Kotlin。

## 三問
1. **原問題的修復效果:**
   - J1(Java 堆疊溢位):有行為證據。
     - 我用 83828dd 的兩條正規式放進同一支 Java 讀法,1000 條回 Y,2000 條和 3000 條都回 SOE。
     - 修後把 `*+` 改回 `*`,`-k arch_template_android_konsist_legacy_shape` 紅在 SOE。
     - 把 `\z` 改回 `$`,紅在 U+0085、U+2028、U+2029 三筆被讀進去。
     - 修後原樣 18 passed。
   - J2:沒有行為證據,見 F51。
   - J3:只有文字釘住(`frameworkPrefixes` 的七個前綴與 `.any` 呼叫),Kotlin 編不到,屬已知限制。
   - J4:`_lens_repo_root(None)` 等於原來的 `_lens_git(Path.cwd(), "rev-parse", "--show-toplevel")`,不在 git 專案時都回 None,行為等價。
2. **修補處的正常、錯誤與相鄰呼叫路徑:**
   - 正常路徑成立:`-k arch_template` 90 passed,`-k arch_target_android` 8 passed(修後)。
   - 錯誤路徑:BOM 不在最前面、開頭雜字、檔尾 U+2028 等輸入都被真的 Java 擋下,Java 與 Python 兩邊結果一致。
   - 相鄰路徑:java 不可用或逾時見 F52,Konsist 判法見 F51。
3. **新發現的同一案例修前、修後:**
   - F51:修前是舊正規式判測試(不掃),修後新算法判會掃;兩版測試都綠,我只在修後工作樹用回退實驗跑過。
   - F52:修前沒有這段測試,修後假 java 時紅。
   - F53:修前測試較窄,修後較寬,文件那句不變。

## 正向主張證據(已驗)
| claim | input | expected | case_source | before | after | comparison |
|---|---|---|---|---|---|---|
| Java 堆疊溢位已修 | 2000/3000/5 萬條清單 | 讀得進去 | 本席自擬(含作者資料檔) | 83828dd 正規式 2000 條起 SOE | 5 萬條通過 | 有行為差異 |
| `\z` 錨點生效 | 檔尾 U+0085/2028/2029 | 不認 | 測試既有輸入 | `$` 版會讀進去(回退實驗) | 不認 | 測試能抓回退 |
| 找 repo 根改用既有函式不改行為 | 非 git 目錄與 git 目錄 | 同前 | 讀碼對照 | 等價 | 等價 | 讀碼得出,沒另外實跑 |

**未驗範圍:**
- Kotlin 實際編譯與 Konsist 真實算法,我沒驗。
- 83828dd 的 `-k` 測試輸出,我沒跑。
- 逾時路徑,我沒實際觸發。
- 驗證紀錄裡 macrobench-lab 的人工實跑結果(BOM、5000 條、U+2028 九支全紅),我無法從程式與產出對上。

## 圖譜鏡頭(固定席)
- lumos-cli-read、lumos-cli-lifecycle、guard-kill、授權與歸屬、bound-tests-gate、design-loop 這些節點的合約與 search、re-inject、guard kill、授權檔等行為無關,本次沒有碰它們的程式路徑,沒有破壞。
- 測試假綠形態的 ★INVARIANT★(還原翻紅釘要配前置斷言證明現場成立):新的 Java 實跑有前置(正規式抽得到、輸出筆數等於輸入筆數),符合。F51 正是 J2 沒有現場分辨力,與該不變量同精神,但它綁的測試名不在本次範圍,不算破壞合約。
- pitfalls-code-loop、其餘只列名的節點,我沒逐篇讀,未判定。

總結:共 3 條
