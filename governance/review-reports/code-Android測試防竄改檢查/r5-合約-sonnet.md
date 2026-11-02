severity: major

縮範圍的文件有一部分沒跟上。我實跑工具核對過:標準裡有兩句仍承諾建置檔改動會被列成候選,實際不會。工具說明表、計劃規則表也有舊說法。

我跑了 `-k tq_guard`(173 條)、`-k lint_new`(82)、`-k lint_waive`(31)、`-k rg_methods`(19),全綠。`lint` 跑過 5 篇筆記,都是 0 問題。兩個 manifest 實算指紋都對得上。「抓不到」那條我抽出來和 `test-guard` 輸出逐字比對,完全相同。修前版本我用 `git archive fcd27439` 解到暫存目錄跑,修前修後對照見各條。

### F1 標準仍說建置檔改動「推送前會被列成作弊候選」,實際不列
severity: major
blocking: 是 — 照標準做的人會以為有守衛,實際沒有,而且與同一篇「抓不到」那條互相矛盾
引句:「專案把它們關掉時,退出碼 0 不代表有跑,要數 XML 裡的案例(關掉它的改動推送前會被列成作弊候選,要附理由放行)」
file: `skills/lumos-project-notes/commands/test-quality-standard.md:162`(同檔 `:138` 另有「推送前的防竄改檢查會把它列成候選」)
後果:`isFailOnNoMatchingTests = false`、`isReturnDefaultValues = true` 現在都不列。標準第 39 行卻寫「建置檔…這一批不比」。三個月後接手的人會照第 138 行把理由寫在放行理由裡,而根本不會有放行這件事。
重現:在暫存 repo 的 `app/build.gradle.kts` 加 `unitTests.isReturnDefaultValues = true`、`filter { isFailOnNoMatchingTests = false }`、`ignoreFailures = true`,另在 `.github/workflows/ci.yml` 加 `-x test || true`。跑 `lumos test-guard --diff HEAD~1..HEAD`,輸出「作弊候選 0 條」,rc=0。
兩版對照:修前 `isReturnDefaultValues` 與 `isFailOnNoMatchingTests=false` 各列 `tq/build-config`;修後兩者皆為 `[]`。
歸因:有證據的修復回歸(這兩句在修前是真的,縮範圍時沒跟著改;計劃〈四〉也留著同樣的句子)。

### F2 `lumos test-guard --help` 的說明還說會抓「放寬 Gradle 或 CI 的測試設定」
severity: major
blocking: 是 — 使用者進場看到的第一句說明與工具行為相反
引句:「AI 改了測試或建置設定之後,想知道有沒有加跳過標記、刪測試、把斷言改弱、改預期值、寫出沒斷言的測試、放寬 Gradle 或 CI 的測試設定(推送前新增告警閘也會跑)。」
file: `scripts/lumos:70965`
後果:`python3.14 scripts/lumos test-guard --help` 照印這句。S23(`t_test_guard_registered`)只檢查有提到指令,不檢查內容,所以抓不到。
重現:`python3.14 scripts/lumos test-guard --help | head -4` 印出上面那句,上面 F1 的重現同一指令對建置檔與 CI 改動回 0 條。
歸因:有證據的修復回歸。

### F3 計劃規則表 `tq/snapshot-changed` 仍寫建置檔的比對門檻字樣會列
severity: minor
blocking: 否 — 這是規則表的精度問題,不影響推送也不會讓人照做出錯
引句:「或測試檔、建置檔裡 `changeThreshold`、`maxDistance`、`ImageComparator`、`roborazzi.test.record` 的命中次數差大於 0」
file: `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:126`
後果:同一份計劃的〈三類檔〉說建置檔這一批不比,這一列卻說會比。只有 `_tg_test_hits` 掃這組字樣,`scripts/lumos:48870`。
重現:建置檔加 `roborazzi.test.record = true` 與 `val changeThreshold = 0.5` 回 `[]`;同樣一行放進測試檔回 `tq/snapshot-changed`。
歸因:有證據的修復回歸(這一輪只改了 `tq/timeout-raised` 那列,漏了這一列)。

### F4 計劃做法一的幾段敘述還把建置檔與 CI 當成會執行的程式
severity: minor
blocking: 否 — 措辭與精度,有「第二批」的標記在別處
引句:「建置檔、正式程式檔只剝註解、留字串(`exclude("…Test…")`、`dependsOn("test")`、`"robolectric"` 要看字串內容);CI 的 yml 不走 C 式剝法」
file: `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:84`
後果:同檔還有三處沒標第二批:
- `:132`:「建置檔用(規則代號、所在區塊的開頭、正規化後的那一行);CI 檔用(…)」
- `:135`:「建置檔與 CI 的區塊開頭用堆疊一趟算」
- 開頭〈白話〉:「改建置設定」

程式裡也還留著舊註解(`scripts/lumos:49091`「正式程式、建置檔、CI 是逐行線性的判讀」)。對照 `_tg_kind`,這些都沒有對應程式了。
歸因:有證據的原有漏查(前四輪就寫在那裡,縮範圍只改了表格與定義兩行)。

### F5 驗證紀錄、評測摘要、S21 仍把建置檔與 CI 當成已驗的規則
severity: minor
blocking: 否 — 已有「縮範圍說明」補在文末,但讀前段的人會先讀到舊結論
引句:「15 個壞改動各從考場同一個提交長出來(用暫存索引造提交,不碰考場工作目錄),**每一個都被對應規則抓到**」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-02_Android測試防竄改檢查實跑.md:23`
後果:
- 公開的 `cases.json` 仍有 `"got": ["tq/build-config"]` 與 `"tq/ci-config"` 共三筆,這兩個規則代號在工具裡已不存在。
- 計劃 `[S21]`「每條規則的壞改動…每條都應被對應規則抓到」沒改。
- 驗證紀錄末尾的 REVISIT 還在等「有 CI 測試步驟」的第二個考場。

重現:`python3.14 -c "import json;print([x['got'] for x in json.load(open('governance/eval/results/android-test-guard-drill-20261102/cases.json'))][9:12])"`
歸因:有證據的修復回歸(補了更正段,沒動正文與 S21)。

### F6 第二批的回頭條件寫「上面五項」,現在是六項
severity: minor
blocking: 否 — 數字過期
引句:「REVISIT:2026-12-15 第二批計劃開了沒有;沒開就把上面五項逐項開成計劃或 Issue」
file: `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:225`(第二批小節內)
後果:這一輪在最前面新增「建置檔與 CI」一項,第二批頂層共 6 項,「逐項開成計劃」的人會漏掉最後一項。
歸因:有證據的修復回歸。

### F7 `tq/catch-no-fail` 的「該確認」建議對新子規則不適用
severity: minor
blocking: 否 — 措辭,有 assertThrows 那個選項可走
引句:「改用 assertThrows/assertFailsWith,或在 try 結尾加 fail()」
file: `scripts/lumos:48968` 附近 `_TG_WHY["tq/catch-no-fail"]`(本輪 `r5-repair-code.patch:616` 原樣保留)
後果:計劃規則表新增的子情況是「try 結尾已經有 fail(),catch 接得住 AssertionError 卻不檢查」。照訊息「加 fail()」做不到任何事,候選照列。
重現:新增 `@Test fun b() { try { foo(); fail("x") } catch (e: Error) { println(e) } }`,輸出為:

    [tq/catch-no-fail] 例外被 catch 或 runCatching 接住…
    該確認:改用 assertThrows/assertFailsWith,或在 try 結尾加 fail()

歸因:有證據的原有漏查(r3 加了這個子規則,訊息一直沒跟上)。

### F8 這一輪新增的測試案例,綁定的條款沒寫到它們;S16 的標籤也不對
severity: minor
blocking: 否 — 條款—測試—程式三方有缺口
引句:「父型別行尾逗號換行的類別路徑還在」
file: `scripts/test_lumos.py`(`r5-repair-tests.patch` 內 `t_rg_methods_expression_body_and_backtick` 末段,新增 `S16 r4` 檢查)
後果:
- `S16 r4` 測的是 test-guard 的 `_tg_functions` 類別路徑,卻放在綁 Room 守衛切法的 `[S16]` 底下,該條款全文沒提類別路徑。
- `S1 r4`(字串常值多空白要列、一行寫完的 assume 不吞下一支)、`S6 r4`(catch 用 shouldBe、check(、require( 不列)、`S13 r4`(三個自動放行出口各寫原因)、`S15 r4`(`--list` 的檔名與規則欄清控制字元)也都沒寫進對應條款。
- 這些行為目前只有測試和計劃規則表的片段描述。

歸因:有證據的修復回歸(新增案例時沒補條款)。

### F9 工具輸出與標準寫「移到第二批」,沒說第二批在哪
severity: minor
blocking: 否 — 措辭
引句:「建置檔與 CI 讓測試不跑或失敗不算(ignoreFailures、enabled = false、-x test、|| true、continue-on-error)這一批不比,移到第二批」
file: `skills/lumos-project-notes/commands/test-quality-standard.md:39`
後果:這句同時印在消費專案的 `test-guard` 輸出裡,消費專案看不到本 repo 的計劃,「第二批」無從查起。只有〈升級說明〉那句帶了「在計劃的第二批」。另有一個錯字:`Systems/test-quality-cli.md` 的 PITFALL 寫「從從第一個堆疊行起(含這一行)才找」。
歸因:有證據的修復回歸(措辭是這輪新寫的)。

## 圖譜鏡頭

`lumos impact --diff 047031883..5516466eb…` 能跑,固定席列了 `test-quality-cli`、`test-quality-multilang`、`pitfalls-code-loop`、`測試假綠形態`(INVARIANT)等。`Systems/test-guard` 因為 `about_code` 是 `scripts/lumos`,排在多個 INVARIANT 家之後,不在前幾名。

`Systems/測試假綠形態` 唯一的合約綁在「修 bug 的還原翻紅釘」,這輪沒改到。不過 `S11 r4` 的「建置檔與 CI 改了不出候選」只斷言 `got23 == []`,沒有同一提交裡一個必會被列的對照。若 `_tqg_cands` 壞到永遠回 `[]`,只剩 `_tg_kind` 單元斷言能抓。這點是 ⚠,我沒把它當 finding。

筆記格式方面:
- 新增的 WHY 帶 `[出處][因][不選][代價][test]`,PITFALL 作廢帶 `[repro][status:superseded][被取代]`,lint 全過。
- 沒有別家檔名。
- 去識別化:這一輪新增或改到的公開檔裡,沒掃到私有套件名、類別名、提交編號、本機路徑。`mOrangePos` 與 `develop` 是計劃明列可寫的專案名與主線名,`com.example.pos.*` 是代稱。

## 三問

1. 原問題的修復效果有沒有行為證據:有。
   - 建置檔與 CI 改動:修前 `tq/build-config`/`tq/ci-config` 列出,修後 `[]`。
   - `catch` 裡用 `check(`:修前列,修後不列。
   - assume 字串裡有左括號只改下一行:修前誤列 `tq/skip-added`,修後不列。
   - 字串常值多一個空白:修前 `[]`,修後列。

   `-k tq_guard` 173 條全綠。真實歷史「44 條不變」我無法重現,因為考場是私有 repo;`history.json` 的 44 條規則分布(26/14/2/1/1)沒有建置檔或 CI 規則,與 README 的說法一致。

2. 修補處的正常、錯誤與相鄰路徑是否仍成立:程式行為成立。
   - 我抽驗了 `@Disabled`、`@DisabledOnOs`、`@EnabledIf…`、`TruthJUnit.assume`、`Assume.assumeNoException`、`Assumptions.assumeTrue`、`@Config(sdk`:都列。
   - 註解裡的 `@Ignore` 與 `Assumptions.abort()`:不列。
   - `catch (e: Exception)` 不列,catch 接 `AssertionError` 或 `Error` 只印出會列。
   - 這些都與計劃規則表一致。

   文件面不成立,見 F1 至 F6。

3. 新發現的同一案例在修前修後各是什麼結果:
   - F1 的 `isReturnDefaultValues` 與 `isFailOnNoMatchingTests=false`:修前列,修後 `[]`。
   - F3 的建置檔 `roborazzi.test.record`:修前修後都是 `[]`。
   - F7 的「try 結尾 fail 加 catch Error println」:修前修後都列,訊息文字沒變。
   - F2:`--help` 的說明文字修前修後相同,是工具行為在變,說明沒變。

   F1、F2、F3、F5、F6、F8、F9 歸為修復回歸,F4、F7 歸為原有漏查。

我不能確認的是考場重跑(44 條不變、18 筆不變)是否如實,那需要私有考場。

九條 finding 中 major 只有兩條(F1、F2),其餘七條(F3 至 F9)為 minor。兩條 major 都是縮範圍後,標準與 `--help` 仍承諾建置檔與 CI 改動會被列成候選,實際不會。
