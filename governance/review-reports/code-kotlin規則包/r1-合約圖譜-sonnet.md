severity: major

**審查席:合約圖譜(sonnet)。** 範圍:`r1-pack-docs.patch`。對照的程式在 `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater`,版本為 `44c2b417e`。

**已用程式實數核對、對得上的項目:**
- 規則包共 208 條,其中 `rules/` 159 條(error 34、warning 125),`rules-hints/` 49 條。
- 型錄共 473 列,各主題列數(API 36、FLOW 32、STATE 28、CO 44、UI 111、ARCH 67、DATA 78、TEST 38、PERF 39)與統計節相符。
- 形狀類 367、語意類 106、人裁 3、出處不全名稱 28、決策表 D-1 起共 56 列,都相符。
- 「TEST 形狀類 18 列」也對:有批一告警的 TEST 形狀列正好 18。
- 規則包自我檢查 `check.py` 回報「規則 208 條,問題 0 個」。
- `t_kotlin_rulepack_messages_cite_catalog`、`t_kotlin_catalog_rows_wired`、`t_lint_new_include_test_paths`、`t_lint_block_message_shows_fix`、`t_kotlin_rulepack_samples_not_scanned_as_code`、`t_lint_new_astgrep_kotlin_two_files` 都存在,前四支我實跑為綠。`t_lint_new_astgrep_kotlin_two_files` 只確認存在、沒有實跑。
- 擋下訊息印 120 字的說法對得上:`_LINT_MSG_SHOW = 120`,SARIF 解析也截 120。
- CI 已釘 `ast-grep-cli==0.51.1`。
- 範圍 ⑤:linter 精選目錄的範本,我用 ast-grep 0.51.1 在臨時專案實跑,擋下了 `response.body()!!`,訊息為 `[API-15]…`,可用。範本裡的 `$HOME/harness/lumos-toolchain/configs/ast-grep` 這台機器上還不存在,要等合併後才有。
- 範圍 ③:取 10 個不同網域實開。以下均對得上:ktor.io、dagger.dev、sqlite.org、lysine.dev(OkHttp callTimeout 預設 0)、developer.android.com、kotlinlang.org(retryWhen)、mrmans0n.github.io、besthub.dev、detekt.dev。只有 robolectric.org 對不上,見 finding 4。

severity: major
blocking: 是
引句:「規則包自我檢查 `configs/ast-grep/kotlin-android/check.py`;測試 `t_kotlin_rulepack_samples`、`t_kotlin_rulepack_messages_cite_catalog`、`t_kotlin_catalog_rows_wired` 都另把複本逐項改壞、驗檢查各自抓到。」
`t_kotlin_rulepack_samples` 在目前的樹上是紅的。這支測試的改壞步驟寫死要把 `'**/src/test/**'` 改成 `'**/test/**'`。驗證紀錄中寫的「路徑過濾全面改成 `src/test*`」後,規則檔裡已經沒有那個字串。這會擋推送前閘與 CI(CI 已強制裝 ast-grep,不會略過)。
重現:在 PATH 加入 `/Users/enzo/lumos-scratch/android-checks/venv/bin` 後執行 `python3.14 scripts/test_lumos.py -k t_kotlin`,輸出:
`✗ t_kotlin_rulepack_samples EXCEPTION: …/gctl-ktpack-…/configs/ast-grep/kotlin-android/rules/coroutines.yml 找不到要改的字:'**/src/test/**'`
`41 passed, 1 failed`
`rules/coroutines.yml` 第 362 行現為 `files: ['**/src/test*/**', '**/src/androidTest*/**']`。
多篇文件把這支測試當成已綠的守護綁定:母計劃 S1 與實作紀錄、`Systems/kotlin規則包` 的兩條 PITFALL 摘要行 `[test:t_kotlin_rulepack_samples]`。我已刪除這次跑出的 `gctl-run-*` 暫存現場。

severity: major
blocking: 是
引句:「一律寫成錨在 `src/` 底下的 `**/src/test/**`、`**/src/androidTest/**`、`**/src/testFixtures/**`。」
母計劃範圍 2 與 `linter精選目錄` 的「路徑過濾的天花板」仍寫舊的 `**/src/test/**` 錨。實作與 `Systems/kotlin規則包` 已改成 `src/test*`、`src/androidTest*`。照母計劃做會把 `src/testDemo` 當正式碼,這正是實測抓到 nowinandroid 誤報的原因。同一個根因,母計劃、linter 目錄與測試都要跟著改。

severity: major
blocking: 否
引句:「要綁變數名的放 `configs/semgrep/kotlin-android.yml`(新增);」
這支檔不存在(`configs/semgrep/` 整個目錄都沒有)。範圍 2 的「API-1 只放 semgrep 版」、範圍 4 的「semgrep 那條同形」範本、型錄 API-1 的「自寫 semgrep(提示級)」都落空。實作改成用 ast-grep 的 `all` 排序,放在 `rules-hints/api.yml` 的 `kt-sequential-independent-await`。實作紀錄與「不做」都沒交代這項變更。

severity: major
blocking: 否
引句:「PAUSED looper(預設)+ 明確 `shadowOf(getMainLooper()).idle()`;固定 `@Config(sdk = [34])`」
TEST-33 沒有標「(出處不全)」,來源 `ROBO` 只指向 `https://robolectric.org/` 首頁。我實開首頁,頁面沒有提到 PAUSED 預設、`@Config(sdk=…)` 或 `idle()`。這違反母計劃「每列標準寫法要有真的打開讀過的權威出處,否則標出處不全」的條款。TEST-33 對應規則 `kt-robolectric-legacy-looper` 是會擋的 warning 級,按條款此列只准提示級。`check.py` 只查來源欄有網址,抓不到「網址沒寫該寫法」。

severity: minor
blocking: 否
引句:「`Projects/Android協程與API寫法機械檢查標準_計劃` 的 40 條(API-1~13、FLOW-1~7、STATE-1~6、CO-1~6、UI-1~3,編號照舊)」
母計劃「舊版初稿的去向」明寫「型錄裡寫『40 條』的地方一併改成 35」。型錄第 7 行與第 12 行仍寫 40,而統計節寫 35,列舉的範圍相加也是 35。同一行還提到 `sg/rules/extras.yml`(會談暫存路徑),`check.py` 的暫存區正規式沒涵蓋它,所以沒被抓到。

severity: minor
blocking: 否
引句:「規則 kt-sequential-independent-await(hint):規則包樣本裡沒有它會命中的壞例,未實測」
這句已過期。我實跑 `ast-grep scan --config sgconfig-hints.yml` 對 `samples/bad/kt-sequential-independent-await`,命中 2 處;`check.py` 也強制每條規則壞例至少命中 2 處。STATE-16 那列的「kt-value-assign-background(hint):樣本實測中壞例,好例誤報 2 筆」同樣過期:我實跑好例得到 0 筆,壞例 2 筆。

severity: minor
blocking: 否
引句:「A 級現成規則(202 列,其中約 166 列只靠現成規則接電)在批四之前不擋,也帶不了型錄編號;只靠 hint 規則的列(約 30 列)在預設範本下不響。」
我用程式數:「告警帶寫法=批四」是 176 列,「批一(只有提示級規則,預設不接)」是 39 列,另有 19 列「未接(還沒有規則)」。母計劃的「約」數字與實數有出入,且沒有交代未接的 19 列。

severity: minor
blocking: 否
引句:「只找到一半或查無的列名稱標「(出處不全)」,共 28 列」
同一節前面寫的分類只有 18 列「只找到一半」加 4 列「查無」,共 22 列。差的 6 列(以及「引用它們的 5 條規則降提示級」的 5)文件沒有交代來源。這點用程式驗不出,我只能標示為對不上。

severity: minor
blocking: 否
引句:「先看文末〈情境決策表〉認出這段程式屬於哪個情境,再照那一列寫」
`SKILL.md` 這句不準確:〈情境決策表〉在型錄第 662 行,後面還有〈待查證〉與〈統計〉,不在文末。

severity: minor
blocking: 否
引句:「鉤子 `main()` 一開始就記下開跑時刻(`_BUDGET_START`,讓既有那道的「已耗時」含這道)」
第二批計劃把 `_BUDGET_START` 寫成要新增的東西。`scripts/hooks/claude/check-graph-sync.py:685` 已經有這個全域變數(第一次用到時才記),差別只在「改成 main 一開始就記」。措辭容易讓人重複新增。

**總結:** 型錄與統計數字大致對得上。最大問題是規則的測試路徑過濾改成 `src/test*` 後,母計劃、linter 目錄與 `t_kotlin_rulepack_samples` 沒跟著改,這支測試現在是紅的,會擋推送與 CI(2 個 blocking 的 major)。其餘是 semgrep 檔缺席、TEST-33 出處不實,以及幾處過期的數字與描述。
