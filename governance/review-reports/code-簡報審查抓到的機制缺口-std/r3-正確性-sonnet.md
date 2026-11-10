severity: major

我逐 hunk 讀完 r3-pack.patch,並在自己的 clone 實跑 ast-grep 0.51.1(和 CI 釘的版本相同)。規則邏輯、逐例表的命中數與行號、README 兩版都沒有問題。唯一的發現是:新逐例表對規則原有的偵測比對樣式沒有任何會翻紅的例子。

## 發現

### 1. 逐例表的「不報」例沒有「同形狀在畫面類別裡會報」的對照,規則原有的 launchIn 分支整段刪掉,測試全綠
severity: major
blocking: 是
引句:「lifecycleScope.launch(Dispatchers.IO) { repo.more.collect { upload(it) } }」
file: `configs/ast-grep/kotlin-android/rules/state.yml:195`(規則的偵測比對樣式,這一帶沒被這次 diff 改動)
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:66`(專案自己的規則:自寫規則逐例測試要逐項拿掉每個比對樣式,每項都要有例子變紅)
歸因:有證據的原有漏查。規則的偵測部分在基底、修前、修後完全相同。基底 45f294c4 的 `scripts/test_lumos.py` 有 0 處提到這條規則;修前 0f2989d0 與修後 771f6c11 的突變結果相同,詳見下方「兩版查證」。

白話:新測試只證明「Service 裡的收集不報」。但「不報」可能是例外生效,也可能是規則根本沒認出那種寫法,兩者測試分不出來。

最小重現,以固定版本 771f6c11 為例:
1. 把 state.yml 中 `kt-lifecycle-collect-without-repeat` 的第二個 `- all:` 整段(`$F.launchIn(lifecycleScope)` 與 `$F.launchIn($O.lifecycleScope)` 那支)刪掉。
2. 跑 `LUMOS_AST_GREP=<ast-grep> python3.14 scripts/test_lumos.py -k kotlin`。
3. 結果是 `919 passed, 0 failed`。

我另外逐項突變的結果如下:

| 突變 | `-k kotlin_rulepack_security_rules` | `-k kotlin_rulepack_samples` |
|---|---|---|
| 拿掉整個 launchIn 分支 | 449 passed, 0 failed | 27 passed, 0 failed |
| 同時拿掉 `lifecycleScope.launch($$$) { $$$ }` 與 `$O.lifecycleScope.launch($$$) { $$$ }` | 449 passed, 0 failed | 27 passed, 0 failed |
| 拿掉 `$F.collect($$$)` 與 `$F.collectLatest($$$)` | 449 passed, 0 failed | 沒跑(單獨拿掉其中一個在 samples 也是 27 passed) |

9 個偵測比對樣式裡,只有 `lifecycleScope.launch { $$$ }` 與 `$O.lifecycleScope.launch { $$$ }` 兩個有例子會變紅(C231、C233、C235、C237、C238、C240、C241 等)。

為什麼 C227、C229 擋不住:C227 的 `launch(Dispatchers.IO)` 與 `launchIn` 兩行、C229 的 `launchIn` 都預期 0 次,所以樣式不存在時照樣綠。壞例樣本只要求至少命中兩處,不核對是哪幾行。

同一案例在畫面類別裡的實跑結果(`class F : Fragment()`,ast-grep 直接掃):

| 輸入 | 完整規則 | 拿掉 launchIn 分支 | 拿掉 `launch(args)` 兩式 |
|---|---|---|---|
| `a.onEach { }.launchIn(lifecycleScope)` 與 `launchIn(viewLifecycleOwner.lifecycleScope)` | 報第 5、6 行 | 報 0 行 | 報第 5、6 行 |
| `lifecycleScope.launch(Dispatchers.IO) { a.collect { } }` | 報第 5 行 | 報第 5 行 | 報 0 行 |

這個缺口之所以算必要行為:計劃範圍 1 與型錄 STATE-5 都把這兩個分支列為規則的偵測對象。專案規則(kotlin規則包 WHY,66 行)也要求每個比對樣式都要有例子變紅。

兩版查證:
- 修前 `git -C repo_before` 在 0f2989d0:拿掉 launchIn 分支、拿掉 `launch(args)` 兩式、單拿掉 `launch(args)` 一式,`-k kotlin_rulepack_security_rules` 都是 `445 passed, 0 failed`。
- 修後 771f6c11:同樣的突變都是 `449 passed, 0 failed`。
- 結論:修補沒引入也沒補到這個缺口。

## 三問

**① 原問題的修復效果**

修補是補 C240、C241 兩列,加上 README、樣本註解和計劃文字。state.yml 在 0f2989d0 與 771f6c11 位元相同,所以證據是「測試能抓到改壞」,不是規則行為變了。

| 項目 | 內容 |
|---|---|
| claim | 前綴限定(非 androidx 同名 Service 照報)與括號比對(介面委派照報)有例子守住 |
| input / expected | C240:`class S : com.acme.LifecycleService()` 內 `lifecycleScope.launch { repo.changes.collect {…} }`,報 1 次、第 6 行。C241:`class F : Fragment(), MediaSessionService.Listener by impl()` 內的 launch+collect,報 1 次、第 5 行 |
| case_source | 逐例表 C240、C241;預期值寫死,來自計劃預期值表,不是從規則算 |
| before(0f2989d0) | 測試檔有 0 處提到 C240、C241。突變 I「前綴放寬成 `(\w+\.)*`」與突變 J「括號前改 `.*\(`」都是 `445 passed, 0 failed`(改壞存活) |
| after(771f6c11) | 突變 I:`447 passed, 2 failed`,紅的是 C240。突變 J:`447 passed, 2 failed`,紅的是 C241。未突變:`449 passed, 0 failed` |
| comparison | 同一對突變,修前綠、修後紅,因果落在 C240、C241。規則在 base、before、after 三版對這兩段輸入的掃描結果相同(C240 報第 6 行,C241 報第 5 行) |

**② 修補處的正常、錯誤與相鄰路徑**

| 項目 | 內容 |
|---|---|
| claim | 既有 13 例(C227~C239)與樣本檢查沒有被破壞 |
| 結果 | 修後 `-k kotlin_rulepack_security_rules` 跑 449 passed;`-k kotlin` 跑 919 passed;`-k kotlin_rulepack_samples` 跑 27 passed;`-k readme` 跑 9 passed |
| before / after | 壞例樣本修前修後都命中 6 處,行號整體偏移 +1(多了一行 `// case:` 註解);修前 `-k kotlin_rulepack_samples` 27 passed |
| 逐例表核對 | 15 例的命中數與行號逐一和寫死的預期值比對,全部相符。例如 C231 第 5、C232 第 6、C233 第 6、C238 第 12、C241 第 5 |

我另外重放了 docstring 宣稱的改壞,每一條都成立:
- 「has 往本體找」只讓 C233 紅。
- 「換不存在的名字」或「inside 拿掉 stopBy」都讓 C227~C230、C233、C234、C236、C238、C239 紅。
- 拿掉 media3 前綴讓 C228 紅。
- 拿掉 lifecycle 前綴讓 C234 紅。
- 拿掉 `^` 讓 C235 與 C240 紅。
- 拿掉括號讓 C231 與 C241 紅。
- 拿掉空白那段讓 C239 紅。
- 前綴放寬成任意套件讓 C240 紅。
- `.*\(` 讓 C241 紅。

另外加的兩個突變也被抓到:把 `Application` 加進名單會讓 C232 紅,把名單改成 `\w*Service` 會讓 C235 紅。

docstring 對「只拿掉 `^`」與「只拿掉括號」寫成單一例紅,其實各多紅一例(C240、C241)。這是說少了,不影響結論,所以不標。

**③ 新發現在修前、修後的結果**:見發現 1 的兩版查證,修前修後結果相同,屬原有漏查。

## 本案特定鏡頭

- (a) regex 對 delegation_specifier 文字的比對:我實跑 18 種邊界,沒有誤判。
  - 照預期不報:多行繼承清單、前後有行註解或 KDoc、泛型加主建構子、`@AndroidEntryPoint`、`Foo by bar` 並列、帶 `androidx.media3.session.` 前綴的 MediaLibraryService、`this.lifecycleScope`、括號前換行。
  - 照預期報:`object : LifecycleService()`、匿名物件、頂層 `fun LifecycleService.f()`、import alias `as LS`、舊 `android.arch.lifecycle.` 前綴、自寫基底類別的子類別、`@Foo LifecycleService()`。這些都是看寫法認不出,屬罕見寫法或計劃已記的天花板。
  - Service 的 companion 不報,Fragment 的 companion 照報。Service 裡的內部 Fragment 不報,與計劃〈實務隱患〉一致。
  - 唯一沒被守住的是把 `\s*` 改成 ` *`(只剩空格),但它只影響 tab 或換行,實務不會出現。
- (b) C227~C241 的命中數與行號:全部相符,細節見問②。
- (c) 五處說法:行為描述一致,沒有互相矛盾。
  - 計劃 S1 條款、計劃預期值表、規則包 WHY 行、測試 docstring、壞例樣本註解,說的是同一組行為。
  - S1 條款與範圍 1 的「照報」清單沒列非 androidx 同名 Service 和介面委派兩類,只在預期值表出現。這是文件完整性問題,而且測試會擋住,所以不標。
  - 新筆記 `lumos lint` 都是 0 問題;`lumos spec-gate` 回報「條款綁定 ✓ 2 條全標(綁了 1/靠人 1)」、「S1 綠」。
- (d) README 中英兩版與原始紀錄一致。
  - 數字:Haiku 4.5 只看程式碼 20/25、現行 12/25;Opus 的四組(只看程式碼、現行、丙、丁)各 25/25,原紀錄寫「在天花板」。
  - 80 場:四題各組各 5 場;只有 H06 有鑑別力(只看程式碼 0/5、三組合計 8/15);H01 與 H05 四組都 5/5,H04 為 5/3/4/5,「大多接近滿分」成立;「只測 Haiku」有據。
  - repo 內沒有其他地方殘留舊句。
- 計劃引的兩個官方出處,我都重讀過:
  - LifecycleService 頁:「A Service that is also a LifecycleOwner」,已知直接子類別 MediaSessionService、間接子類別 MediaLibraryService。
  - ProcessLifecycleOwner 頁的原文,以及 repeatOnLifecycle 那句「only when the UI is visible on the screen」。
- 新增的第一份 Issue(同檔放行綁指紋)我在臨時 repo 重現過:ruff BLE001 同檔兩行一樣的 `except Exception:`,放行其中一條的指紋後,`lumos lint-new --diff main..HEAD` 回報 clean。第二份 Issue(輕量審查放行高風險)我讀了 `scripts/lumos` 的 `code-loop check` 第 4 道,確實只比對留痕的 sha 與狀態,沒看定錨分級。

## 圖譜鏡頭的固定席

- 測試假綠形態(INVARIANT):還原翻紅釘要配前置斷言證明現場成立。本案的「不報」例靠突變重放證明例外有效,但「被保護的形狀本身會被規則認出」缺前置斷言,這就是發現 1。
- test-quality-handbook(測試品質手冊):預期值獨立、寫死;缺的是第 4 點「讓情境真的成立」,同樣是發現 1。
- 授權與歸屬(INVARIANT):不影響。diff 沒新增 scripts/ 檔、沒動 `_VENDORED_TOOLKIT`,也沒碰主程式檔頭,只在測試檔加資料列和 docstring。
- design-loop(INVARIANT,處置閘第五步):不影響。審材是 .md 計劃,S1 綁測試,spec-gate 結果見上。
- lumos-cli-read(INVARIANT):不影響。diff 沒碰 search 的排除邏輯。
- arch-alignment-lens(架構對齊):風格與架構歸架構對齊席,本席未評。
- 回頭重讀指紋、推送前一次列出兩份計劃(RISK):不影響。diff 沒改回頭重讀或推送前閘的程式。
- 超出上限只列名的節點:沒逐一展開,diff 也沒改它們管的程式。

## 未驗範圍

- 沒跑全套測試,只跑 `-k kotlin`(919)、`-k readme`(9)、安全規則與樣本子集。
- 沒跑 `lumos doctor`。
- 沒驗 media3 MediaLibraryService 的繼承鏈,只讀到 LifecycleService 頁的「間接子類別」列。
- 第二份 Issue 的重現只讀碼,沒實跑。
- 臨時目錄 `/tmp/lumos-seat-work/code-簡報審查抓到的機制缺口-std/正確性-sonnet/`(含兩個 clone 與一個臨時 repo)留給編排者收貨後刪除,我這邊沒有程序還開著。

總結:本報告最高嚴重度為 major
