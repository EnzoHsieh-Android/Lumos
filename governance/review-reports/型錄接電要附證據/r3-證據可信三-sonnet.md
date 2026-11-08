severity: major

以下是這一輪的審查發現。我沒有實際跑 lint 或 detekt,所有判斷都來自讀快照、`pilot.md`、`linter精選目錄.md` 範本段和 `configs/detekt/compose.yml`。

**1.** 自檢沒有檢查「判定」和「等級」是否一致,「擋得到」可以搭配 Hint 或「沒報」過關。
severity: major
blocking: 是
- 失敗場景:自檢只驗判定值、等級值各自屬於固定集合,沒有規定「擋得到」必須搭配等級 Fatal、Error 或 Warning。實作者把 UI-96 寫成「擋得到 | Hint」,或把 UI-49 寫成「擋得到 | 沒報」,自檢照樣 0 問題。
- 這正是 pilot 已經看到的情況:UI-96 的 ArcAnimationSpecTypeIssue 是 Hint,UI-49 沒報。S2 只測了「把判定改成擋不到而通電批次不動」,沒測等級和判定矛盾。
- 另一個語意不清處:`warningsAsErrors` 升級之後,報告裡的等級欄寫的是升級後的 Error,還是檢查原本的 Warning?計劃沒規定。我沒有實測 lint XML 在升級後的寫法。
- 計劃若要求記升級後的等級,等級欄就不會出現 Warning。若要求記原本的等級,範圍 1 又寫「報告裡等級是 error」。兩邊對不上。
- 為什麼標 major:這是判定表的核心合約,缺了就讓實作者能寫出自相矛盾卻通過的判定。
引句:「判定對不到候選、編號不在主表、同一三元組兩筆、固定值以外的值,各報指名那一列」
佐證:file: `sweep/pilot.md:UI-96、UI-49 兩列`(都在 android-unwired-sem/governance/review-reports/型錄接電要附證據/ 底下)

**2.** 「擋得到」的定義是照 Android Lint 寫的,detekt 套不上去,「推送前」那個標籤依哪個執行環境真跑也沒寫。
severity: major
blocking: 是
- 失敗場景:detekt 的 SARIF 等級是 error、warning、info,不是 Fatal、Error、Warning、Hint、Informational。detekt 預設把規則報成 warning,任務是否失敗看 `build: maxIssues`(預設 0)和規則是否 `active`,不看等級。
- 照字面實作,等級欄對 detekt 候選填不出固定集合內的值,「報告裡等級是 error」也永遠不成立,compose-rules 全部會被判成擋不到。
- 反過來,若實作者自行改成「有報且 rc 非 0」,又沒有寫進計劃,不同人會判出不同結果。
- 執行環境:「推送前:detekt 外掛 compose-rules」的真實機制是 CLI 命令列,加 `--disable-default-rulesets`、`compose.yml` 和新增告警閘。範本裡的 Gradle `detektDebug` 屬於 CI 段,兩者不同。
- 計劃只寫「detekt 照範本設定加 compose-rules 外掛」,沒說用 CLI 還是 Gradle 任務。
- `compose.yml` 已經把 `PreviewNaming`、`UnstableCollections`、`Material2` 設為 `active: false`。計劃只用「預設關」一詞,沒要求 detekt 一側以這份設定為準,UI-100 這類列的判定會因執行環境而異。
- 為什麼標 major:detekt 候選占相當比例,定義套不上去會讓整批判定表無法產出,或產出互不一致的結果。
引句:「報告裡等級是 error(warning 經 `warningsAsErrors` 升成 error 也算)、會讓 lint 或 detekt 任務失敗」
佐證:file: `configs/detekt/compose.yml:1-20`;file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:134-138`(`--build-upon-default-config` 與 `--disable-default-rulesets` 的 CLI 命令);file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:147-158`(Gradle 範本)

**3.** 「外層函式或類別」的放行範圍,讓樣本可以把會觸發檢查的呼叫端補進去,上一輪(r2 的 g3)要堵的洞沒有關上。
severity: major
blocking: 是
- 失敗場景 A:UI-11 的壞例是 `MyList(vm)`,裡面只用 `vm.onClick()`。pilot 的結果是照抄不報,必須有另一個 composable 把 `vm` 往下傳,ComposeViewModelForwarding 才報。
- 實作者寫 `fun MyScreen(vm){ MyList(vm) }` 包住原句,原文一字未動,自檢通過,真跑報 Error,判成「擋得到」。型錄壞例本身其實擋不到。
- 同樣的缺口還有 PERF-1(需另寫自標 `@WorkerThread` 的函式並呼叫它)和 TEST-25(需另寫會改狀態的函式)。
- 失敗場景 B:ARCH-28 的壞例 `class DetailFragment(val id: Long) : Fragment()` 一字不改。補 `import android.app.Fragment` 時 ValidFragment 報 Error。補 androidx 的 Fragment 時不報。
- 「可以補 import」沒有規定補哪一個,判定隨實作者的選擇翻轉。
- 計劃的〈天花板〉第二條只承認「原文照留、旁邊再加會報的變體」只能靠代碼審看,但這就是 pilot 已經實證的 4 個以上的列,不是罕見情況。
- 為什麼標 major:r2 已經把這個缺口列為 major 並宣稱折掉,現在的折法只防「整段換掉」,對已知案例無效,驗收不成立。
- 建議:樣本只准是純外殼,不准新增呼叫例子的語句。判定的理由欄要寫明用了哪個 import。
引句:「樣本照抄壞寫法欄的例子(可以補 import、外層函式或類別讓它編得過,例子那一行本身不准改)」
佐證:file: `sweep/pilot.md:UI-11 兩列、ARCH-28 變體 c、PERF-1 變體、TEST-25 變體`;file: `skills/kotlin-idioms/checks-catalog.md:338`(UI-11 壞例原文);file: `skills/kotlin-idioms/checks-catalog.md:471`(ARCH-28 壞例原文)

**4.** 「真跑」描述的 lint 區塊和實際範本不一致。
severity: minor
blocking: 否
- 範本的 lint 區塊有 `baseline = file("lint-baseline.xml")`、`warningsAsErrors`、`checkDependencies`、`sarifReport`。計劃寫「只開 `warningsAsErrors`」。
- 基準線的行為會影響真跑:若最小專案先產了基準線,同一條檢查的既有位置會被壓掉,報告看起來像沒報。
- 範本沒有寫 `abortOnError`(AGP 預設 true)。計劃也沒說「讓任務失敗」怎麼判:是看 rc,還是看報告裡有 Error。
- 同一專案跑 23 列以上的樣本時,任務失敗無法歸因到單一檢查,只能靠報告逐筆讀。
- 為什麼標 minor:實作者多半能自行補全,不補也不會做出錯的行為,但「真跑」的定義應該寫齊。
引句:「lint 區塊只開 `warningsAsErrors`,不開 `checkAllWarnings`;detekt 照範本設定加 compose-rules 外掛」
佐證:file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:173-178`(範本 lint 區塊)

**5.** 〈天花板〉漏寫了一種假的「擋不到」:樣本缺依賴時,依賴型別的檢查靜默不報。
severity: minor
blocking: 否
- 失敗場景:Android Lint 對未解析的型別不一定報編譯錯誤,依賴型別的偵測器會靜默跳過。
- 最小專案缺少 `androidx.work` 或 `fragment` 這類依賴時,例如 DATA-32 的 WorkerHasAPublicModifier 或 UI-11 的 ViewModel 型別,檢查靜默不報,會被判成「沒報」,也就是擋不到。這不會觸發「樣本編不過」的查證路徑。
- pilot 本身就踩過依賴問題:material3、M2 material、ui-tooling-preview 改用本地 aar,lifecycle 被 Compose 拉成 2.9.4,androidTest 變體被關掉,Slack 只有 1.4.2 一個版本可用。
- 方向是少宣稱,比較安全,所以只標 minor。
- 建議:天花板補一條「型別解析不到時靜默不報,會被誤判成擋不到」。理由欄在「沒報」時要記樣本的依賴清單。
引句:「樣本編不過的候選退回讀官方頁判,準確率沒有真跑那麼高;清單與筆數寫在這裡(實作後補)。」
佐證:file: `sweep/pilot.md:版本與偏離段`;file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:31`(detekt 沒給型別資訊時,要型別的規則靜默不報)

最高等級 major;blocking 3 條
