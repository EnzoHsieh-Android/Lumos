severity: major

審查範圍：快照 r2-snapshot.md，對照 sweep/pilot.md 與 registry-lint31.13.2.tsv。我另外拿型錄現成規則欄的檢查 id 去對 registry，結果是 17 個資安包 id、5 個 navigation id、4 個 Slack id 讀不到。除 Slack 四條外，這些都不是版本問題，而是 registry 沒載入該套件。

**1.**
severity: major
blocking: 是
為什麼標 major：照字面實作，會把整個資安包和 navigation 的候選全部判成擋不到，通電批次因此被改掉。

「清單裡讀不到的檢查 id 判擋不到」這句，和同段前一句「沒載入的套件讀官方檢查頁的 Severity 與預設欄」互相打架。後一句本來是為沒載入的套件留的路。「清單」指的是 lint-api 讀出的 608 條，還是指「已載入套件的清單」，快照沒寫。

具體失敗場景：registry 的 608 條裡沒有 navigation 套件，也沒有 `com.android.security.lint`。型錄有 19 列寫 `資安包:`，我數到 17 個資安包 id 不在 registry，例如 DefaultCleartextTraffic、StrandhoggVulnerable、LogInfoDisclosure。另外有 5 條 `androidx.navigation(.compose)` 的 id 不在 registry：EmptyNavDeepLink、WrongNavigateRouteType、MissingSerializableAnnotation、ComposableNavGraphInComposeScope、UnrememberedGetBackStackEntry。
- 實作者照「讀不到就判擋不到」做，這些候選全部寫成「範本版本沒有這條」，通電批次被降成只標批一。
- 但資安包 1.0.4 其實有這些檢查，連 linter精選目錄 都寫了「它 24 條的檢查頁都沒寫預設關」，所以降級是誤判。
- 預期值表 S3 只列了 18 列要降級，沒有任何一列是資安包或 navigation。S1 又要求「批四標籤恰好等於判定擋得到的標籤」，兩者對不起來，實作者不知道該信哪一邊。
- 這還會讓資安包「掛在 Android Lint 同一步跑」這條既有合約悄悄失效。

引句：「清單裡讀不到的檢查 id 判「擋不到」,理由寫「範本版本沒有這條」。」
佐證：file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/governance/review-reports/型錄接電要附證據/sweep/registry-lint31.13.2.tsv:1`，第四欄只有 builtin、compose-lint-checks-1.4.2、runtime、ui、fragment-1.8.9、work-runtime 等，沒有 navigation，也沒有資安包。
file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:186`，寫明資安包 1.0.4 是 `lintVersion='31.5.1'`，不需要 lint-api 31.13.2 也能載。
改法：把「讀不到」限定成「該套件已載入、但清單裡沒有這個 id」。套件沒載入的，要嘛補載入，要嘛強制走官方頁。

**2.**
severity: major
blocking: 是
為什麼標 major：抽樣沒有判斷門檻，也不涵蓋「判擋不到」的那一邊，驗收條款會把沒驗過的判定當成已驗證。

具體失敗場景：計劃只從「讀頁判擋得到」的判定裡隨機抽 30 筆真跑。
- 讀頁判定的錯誤都是「判擋得到、實際擋不到」（先導 23 列約一半對不上），也可能有「判擋不到、其實擋得到」的反向錯誤。抽樣框只含前一類，後者量不到。
- 沒寫不一致率超過多少就要全數重跑。30 筆不一致的以真跑改判，其餘沒抽到的判定維持原樣，也過 S1 與型錄自檢。
- 若抽樣顯示 40% 不一致，沒抽到的約 87 筆仍被當成「擋得到」，而自檢只驗格式與一致，驗不出來。
- 「先導 23 列」與「抽 30 筆」是否去重也沒寫。抽到先導已跑過的列，等於重複量測，實際抽樣數變少。

引句：「真跑先導另隨機抽 30 筆「讀頁判擋得到」的判定真跑一次,量讀頁判定的準確率,不一致的以真跑為準改判定、寫進〈天花板〉。」
佐證：sweep/pilot.md 的 TSV 有 46 個「沒報」，涵蓋 18 個列編號，其中 API-9、PERF-1、PERF-36 等在讀頁階段都被判過。
file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/governance/review-reports/型錄接電要附證據/r1-intake.md:29`，全表核對寫「擋得到 117、擋不到 9、預設關或 Hint 3」。擋不到只有 9 筆，抽樣框沒包含它們。

**3.**
severity: major
blocking: 是
為什麼標 major：S4 只驗樣本檔存在，而 pilot 的實際情況是，「報」常常要靠改寫過的變體才成立。

具體失敗場景：「擋得到」的定義寫「會報壞寫法欄裡至少一個例子」。pilot 顯示好幾列只有改寫過的變體才報：
- UI-11 的原文不報，要改成 `MyScreen(vm){ MyList(vm) }` 往下傳才報。
- ARCH-28 的 androidx Fragment 不報，要改成平台 `android.app.Fragment` 才報。
- UI-49、PERF-1、TEST-25、DATA-32 也是同樣情形。

實作者把變體樣本放進 `samples/lint-wiring/`、判成擋得到、出處寫〔真跑〕，S4 只檢查檔案存在，一樣過關。這就違反了前面的定義：擋的是變體，不是型錄的壞寫法欄。計劃也沒要求樣本內容要等於壞寫法欄原文，或要有報告輸出可對照。

引句：「出處是〔真跑〕的每筆 應 指到存在的樣本檔」
佐證：sweep/pilot.md 的 UI-11、ARCH-28、UI-49、PERF-1 各列，都有「照抄不報、變體才報」的對照。
改法：樣本檔要逐字等於壞例原文，變體要另開列標明，不能當作該列擋得到的出處。

**4.**
severity: minor
blocking: 否
為什麼標 minor：對照關係不清楚但不會直接做出錯誤行為，風險限於實作者誤用先導報告當證據。

計劃寫了預設開關來自檢查的 `isEnabledByDefault`（註冊時的設定），但沒說〔真跑〕樣本要用什麼設定跑。先導報告在所有列都開了 `checkAllWarnings`，所以 UI-80 的 Warning 預設關，在 pilot 裡也「報」。TEST-25 的 ExpensiveAssertion 預設關，AssertionSideEffect 預設開，兩個檢查在同一個變體裡一起報。同一欄混了「檢查預設開」和「checkAllWarnings 強制開」兩種情況。

計劃只在 PRIOR-ART 提到旗標，範本裡也沒有 `checkAllWarnings`，沒寫真跑時要不要關掉。實作者若直接引用先導的 TSV「有沒有報」欄當〔真跑〕出處，UI-80 這類列會看起來像「擋得到」，只有預設欄把它擋回去。

引句：「等級與預設開關:lint 的檢查物件自帶 defaultSeverity 與 isEnabledByDefault,先導用同版 lint-api 載入各套件的檢查清單機械讀出」
佐證：sweep/pilot.md 的 UI-80（報、Warning、預設關）與 TEST-25（開/關）。
file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:175`，範本只開 `warningsAsErrors`，沒有 `checkAllWarnings`。

**5.**
severity: minor
blocking: 否
為什麼標 minor：天花板寫的偏誤方向不對，會誤導下一個讀的人，但不會直接做出錯誤行為。

天花板說「消費專案裝更新的版本時,可能多擋」。這只講了一個方向。登記表的版本是本機快取剛好有的：material3 1.4.0、fragment 1.8.9、compose 1.11.4、work 2.10.5、lifecycle 被拉成 2.9.4。androidx 的 lint 檢查跟著函式庫版本走，範本並不決定它。
- 範本沒有釘 androidx 版本，所以快取版本不是「範本支援的最舊那一段」。
- 消費專案若用 BOM 較舊的 Compose，pilot 判成擋得到的新檢查，在該專案實際不存在，批四標了卻擋不到。
- 例如 UI-24 的 ConfigurationScreenWidthHeight，以及 UI-49 的 ConstantContentStateKeyInItemsCall，都屬於較新的 Compose 才有的檢查。

引句：「等級與預設照範本最低支援的版本讀;消費專案裝更新的版本時,可能多擋(新版加的檢查),判定表不會反映。」
佐證：sweep/pilot.md 〈版本與偏離〉列出 material3 1.4.0、fragment 1.8.9、compose 1.11.4、work 2.10.5。
file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/governance/review-reports/型錄接電要附證據/sweep/registry-lint31.13.2.tsv:1`，第四欄是各 androidx 套件的快取版本。
建議：天花板改成雙向（多擋與少擋），並要求判定表的「出處」欄記錄各 androidx 套件的版本。

最高等級 major；blocking 3 條
