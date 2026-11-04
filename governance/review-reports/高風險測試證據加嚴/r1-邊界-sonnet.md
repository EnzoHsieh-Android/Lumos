severity: major

我只在 `/tmp/lumos-seat-work/高風險測試證據加嚴/邊界-sonnet/` 放了 `t1.py`、`t2.py` 兩支實測小程式,沒動 repo。下面第 2、4、5、7、17 條有用它們實測。

## 逐條 finding

**1. 「真的在實作」的判準沒定義,照現有候選函式的寫法,設計審折審查發現的提交會被當成在實作而擋下**
- 位置:做法 3 第一點(哪些計劃要查),也是作者新改的第二處主幹。
- 引句:「這次推送範圍改到那份計劃檔、同時也改到程式檔」
- 引句:「那份計劃可能還在設計審」
- 問題:spec 沒定義「程式檔」。「程式檔」是指任何一個不在筆記庫底下的檔,還是指和這份計劃有關的程式檔,spec 都沒說。
- 能重現的場景:設計審每一輪折完審查發現,提交都含「改計劃檔 + 帳本」。目前 `git status` 就顯示 `docs/.canary-log.jsonl`、`docs/.governance-log.jsonl` 處於 M(已修改)。再把同一次推送裡任何無關的程式提交算進去,這份還在設計審的風險高計劃就被擋。這正是 spec 自己說「不能擋別人的推送」的情境。
- file: `scripts/lumos:15543` 的 `code = [t for t in touched if not t.startswith(vrel + "/")]` 把所有不在筆記庫底下的檔都算程式檔,帳本、README、測試檔都在內。
- file: `scripts/lumos:38108` 的 `_BOOKKEEPING_FILES` 和 `scripts/lumos:43937` 的 `_NODEHOME_EXCLUDE_GLOBS`(含 `docs/*`)已有「簿記檔、文件不算程式檔」的現成口徑,spec 沒指名要用哪一個。
- 另外,「改到的程式檔」沒有和這份計劃綁在一起。計劃檔 + 任一無關程式檔就觸發。

severity: major
blocking: 是 — 實作者照最近的現成寫法會讓設計階段的風險高計劃被誤擋,和 d1 的初衷相反。

**2. 推送前讀帳用的欄位白名單沒有 `clause_verdicts`,而且現成的讀法只給最後一筆**
- 位置:做法 2、做法 3「查什麼」。
- 引句:「在審查帳這份計劃的所有規格閘留痕裡」
- file: `scripts/lumos:15792` 的 `_SPEC_GATE_PUSH_FIELDS` 沒有 `clause_verdicts`。同處註解寫明「要讀新欄位就加進來,不然讀到的永遠是 None」。
- 後果:不改白名單,每條新行為條款都會判成「沒紅過」,所有風險高計劃一律被擋。
- file: `scripts/lumos:15480` 的 `_spec_gate_latest_records` 和 `scripts/lumos:15519` 的 `_spec_gate_latest_merged` 都只回「每個迴圈最後一筆」。spec 要的「所有留痕」和「首筆」需要另寫索引,spec 沒提。
- 留痕欄位型別不對的情形 spec 沒說。S6 只講「沒有這欄」。`clause_verdicts` 是字串或 null、項目缺鍵時,推送前檢查會丟例外。Python 未捕捉例外的退出碼是 1,`scripts/hooks/pre-push:565-567` 把 rc1 當擋下,還印「風險低計劃的條款測試沒全綠」這句錯話。

severity: major
blocking: 是 — 照 spec 字面實作,上線第一天就全擋。

**3. 推送前只讀審查帳,乾淨 clone 或另一台機器會把生效日前的舊計劃當成新計劃**
- 位置:效能節、名詞「首筆規格閘留痕」、天花板二。
- 引句:「推送前比對只讀審查帳上這份計劃的規格閘留痕與治理帳上的簽核事件」
- 引句:「從沒有留痕的計劃一律當成生效日之後的新計劃」
- 場景:消費專案的審查帳被 gitignore(spec 自己在天花板二承認)。這種專案的乾淨 clone 讀不到審查帳,舊計劃首筆是 None,被當成新計劃。這讓「不回頭擋首筆規格閘留痕早於生效日的計劃」整段失效。
- file: `scripts/lumos:16255` 一帶的 `_spec_gate_push_scan` 為此特地合併兩本帳(註解「B3:消費專案的審查帳被 gitignore」),spec 沒沿用。
- 兩本帳是「各寫一份」,沒說兩份 ts 不同、token 重複時怎麼合。

severity: major
blocking: 是 — 另一台機器上推送會追溯擋舊計劃,和「不追溯」矛盾。

**4. 判法 c 把「找到但沒失敗」的 testcase(passed 或 skipped)也判成紅**
- 位置:做法 1 的 a/b/c/d 判法,涉及 S1 到 S4。
- 引句:「找得到、但報告沒有失敗型別」
- 實測(`t2.py`):`tq.junit()` 對 passed 的 testcase 回 `('C::foo()','passed',False)`,對 skipped 的回 `skipped`,兩者都沒有失敗型別,都落進 c,被記成「紅、紅因未判」。
- 現實觸發路徑:file: `scripts/lumos:33390` 的 Gradle 指令是 `--tests '*{method}'`,後綴比對。目標測試沒失敗,但同尾碼的另一支測試失敗,退出碼為紅。被擋在外面的目標本身是 passed 或 @Ignore。這支測試被記成「紅過」,先紅這個憑證形同虛設。
- 弱證據的定義(spec 第 63 行)本來包含「被跳過」,判法四條卻沒有 passed/skipped 這個分支。

severity: major
blocking: 是 — 讓「先紅」這個機械憑證可以在測試沒紅時成立。

**5. 借用的 `_secev_junit_facts` 提供不了判法 a、b、c 要的資料**
- 位置:做法 1 第一點、S4。
- 引句:「再讀那一筆 testcase 的失敗內文」
- file: `scripts/lumos:8883` 的 `_secev_junit_facts` 只回 `{id: (狀態, bool(assertion_failure))}`,沒有失敗內文,也沒有「有沒有型別」。判法 b 和 c 的區別正取決於後者。
- 要拿內文只能直接用 `tq.junit()` 的 `reason`,但 file: `scripts/test_quality.py:238` 把 `reason` 截成 4000 字。實測(`t2.py`):200 幀堆疊後才出現 `Caused by: kotlin.NotImplementedError`,`reason` 長度正好 4000,`NotImplementedError` 不在其中,例外鏈檢查會漏掉,錯判成斷言紅。
- S4 的前提也和程式現況對不上:file: `scripts/test_quality.py:129` 的 `if not kind:` 已在判裝置報告(沒型別欄)。實測:裝置報告的 `AssertionError` 文字回 `assertion_failure=True`,裝置的 `kotlin.NotImplementedError` 文字回 False。
  - 前者會落進判法 a,不是 S4 說的「未判」。
  - 後者沒有型別欄,依判法 c 會被當紅收下,正是 d2 要擋的 `TODO()` 假紅。

severity: major
blocking: 是 — 「只借不改」的承諾兌現不了,實作者得自行決定怎麼判型別有無。

**6. 借來的斷言型別白名單漏掉常見的斷言失敗,而且 spec 禁止改它**
- 位置:d2、判法 b。
- 引句:「測試品質模組已有實測過的斷言型別白名單」
- 引句:「那支檔有部署指紋釘住,只借不改」
- 實測(`t1.py`,用 `tq.junit()`):以下型別的 `assertion_failure` 都是 False,會被判成「非斷言 → 弱證據」。
  - `org.mockito.exceptions.verification.WantedButNotInvoked`
  - `...junit.ArgumentsAreDifferent`
  - `org.opentest4j.MultipleFailuresError`(JUnit 5 的 `assertAll`)
  - `org.assertj.core.error.AssertJMultipleFailuresError`
  - `io.kotest.assertions.MultiAssertionError`
- Mockito 的 `verify` 在 Android 單元測試很常見。用這類斷言的新行為條款永遠拿不到紅。判法 b 印的補法(空殼改回傳預設值)對它們無效。
- file: `docs/lumos-toolchain-knowledge/Systems/test-guard.md`(凍結提交內)已有一條 WHY:catch 接斷言失敗「照型別名字的字尾認(…Error、…Failure、Throwable),不逐一列各框架的子類別」。理由是字表一直漏 `MultipleFailuresError` 這類 AssertionError 子類別。d2 反向借用了字表,和已有決策衝突。

severity: major
blocking: 是 — 一批常見測試風格被永久擋下,又因 `test_quality.py` 被釘住而無法在 spec 範圍內修。

**7. 報告裡「這支測試」的比對規則沒定義**
- 位置:做法 1 第一點。
- 引句:「找名字對得上這支測試的那一筆」
- 比對對象是 `classname::name`,spec 只說「比方法那一段」。
- file: `scripts/lumos:6017` 的 `KOTLIN_TEST_RE` 抓到的 Kotlin 測試名會連反引號一起收進來。
- 報告端的 name 格式,spec 一個字都沒說。我判斷 Gradle 對 JUnit 5 的 name 帶括號與參數(`foo()`、`foo(int)[1]`),但 repo 裡沒有實測樣本可證 ⚠。若是如此,精確比對會讓所有 JUnit 5 測試都落進判法 d。
- 同名或多筆的情形沒規則:`--tests '*{method}'` 後綴比對會選到 `computeTotal` 和 `shouldComputeTotal`。同名方法出現在不同類別時,「那一筆」不唯一。找第一筆則受檔案列舉順序影響,結果不穩。

severity: major
blocking: 是 — 不補規則就會誤判 JUnit 5,或結果隨列舉順序跳動。

**8. 讀報告的位置沒定出來:共用函式沒有計劃資訊,也沒有每支測試的開跑時間**
- 位置:做法 1 第一點、S5。
- file: `scripts/lumos:15105` 的 `_spec_gate_judge_items(rr, items, per_prof, loose_for)` 有四個呼叫端:`15130` 規格閘條款、`15162` 相依回歸、`16191` 推送前風險低、`22036` 修正關卡。函式簽名沒有計劃或首筆留痕資訊,S5「早於生效日不讀報告」無法在函式內判。
- file: `scripts/lumos:69029` 的 `_run_bound_tests` 先把所有 job 跑完才回傳,回傳只有 `(rc, tail, secs)`,沒有開跑時間。每支測試會展開成各自的 Gradle 指令。
- `bound_tests.parallel`(`scripts/lumos` 的 `_bound_tests_parallel`)可到 16,同一個 `build` 目錄同時有多個 Gradle。
- 「誤擋二」只討論兩個規格閘同時跑,沒提程序內並行。
- ⚠ 未驗證:Gradle 每次執行是否會清掉上次的 XML,這決定了「全部跑完再讀」是否會丟掉前面的測試的報告。請編排者查證。

severity: major
blocking: 是 — 實作者必須自己決定在哪裡讀、拿什麼當開跑時間,而 spec 暗示的位置做不到。

**9. 逾時一律變成「未判」,而「未判」在推送前算紅,弱證據變放行**
- 位置:效能節、天花板處理、做法 1。
- 引句:「逾時就把沒判完的當未判、印一句」
- 做法 1 的 d(找不到報告)是 fail-closed(判弱證據),效能節的逾時卻 fail-open(判未判,而未判在做法 3 算紅)。目錄很多的大 repo、慢磁碟會讓整道檢查變成只看退出碼。
- 測試本身逾時也有同樣問題:file: `scripts/lumos:69150` 的 `if to:` 把逾時記成 `red`(「超時」)。
- 已有的先例都不把逾時當真紅:file: `scripts/lumos:14345`「逾時的紅不算」;`Systems/guard-kill.md` 的 `timed_out_weak`(「不再計為 killed,舊版歸 killed 是假強殺」)。
- 預設逾時是 180 秒(`LUMOS_TEST_TIMEOUT`),Android 冷啟動 Gradle 很容易超過,所以這個漏洞不罕見。

severity: major
blocking: 是 — 慢機器上「先紅」憑證幾乎不設防。

**10. 某些設定下紅永遠產生不出來,而擋下沒有放行出口**
- 位置:誤擋一、做法 3、`--no-verify` 以外無出口。
- 引句:「找不到報告,紅會變弱證據」
- 以下情形會讓「先紅」憑證無法產生:
  - Maven:file: `scripts/lumos:33392` 骨架明寫支援 `mvn -Dtest='...' test`,報告在 `target/surefire-reports`,不在 `build` 下。
  - 自訂 `buildDir` 或 `outputLocation`。
  - `run_cmd` 沒有 `{method}`:file: `scripts/lumos:15099` 的 `_spec_gate_runnable` 直接「略過」,不跑、不判紅。
  - 平台設定讀不動:file: `scripts/lumos:15277` 的 `return 1 if door == "low" else 0`,風險高回 0 而且沒寫留痕。S8 叫人「先跑規格閘」,但規格閘根本寫不出留痕,死循環。
- 這幾種都只剩 `git push --no-verify`。而全域規則禁止在沒問過使用者時繞過檢查。
- 對比 android-e2e 放行、lint-waive 這類已有放行指令的閘,這裡沒有任何依計劃或平台的放行機制。

severity: major
blocking: 是 — 這些專案的風險高計劃會永久推不上去。

**11. 零條款、全標 `[keeps]`、全標 `[manual:]` 的風險高計劃完全繞過紅、表、簽三關,而 spec 對「零條款會被擋」的說法是錯的**
- 位置:做法 4 第二點、新行為條款名詞。
- 引句:「那些情況本來就會擋或沒有新行為條款」
- file: `scripts/lumos:15003` 到 `15007` 顯示零條款只對風險低回 1,風險高印「沒有東西可驗」並回 0。所以「本來就會擋」對風險高不成立。
- 新行為條款定義為「沒標 `[keeps]`、綁了 `[test:]`」。全標 `[keeps]` 或全改 `[manual:]`,新行為條款數為 0,所有檢查空轉通過。
- 風險低有對應防線:file: `scripts/lumos:14210` 附近的 `_spec_gate_twoway_static` 擋「全部都標 keeps」,並要求 keeps 的測試在計劃建立前就存在。spec 沒把這兩道搬到風險高。
- 這份計劃的目標就是 AI 寫的風險高計劃,AI 標 `[keeps]` 的成本是零。

severity: major
blocking: 是 — 加嚴的目標群體可以零成本繞過。

**12. 回退機制和「沒有留痕一律視為新計劃」互相矛盾**
- 位置:回退節、名詞第 71 行。
- 引句:「從沒有留痕的計劃一律當成生效日之後的新計劃」
- 引句:「三組生效日各一個常數(初值同一天)」
- 回退寫「推送前『風險高要先紅』那組設成遠未來就不查」。但沒有任何留痕的計劃不看生效日,照樣當新計劃查,所以回退後這類計劃仍被擋。

severity: major
blocking: 是 — 回退路徑在最需要它的情形(沒留痕的計劃)上失效。

**13. 推送前的「風險高」用哪個來源判沒有說,取現場判門會讓人自己把門改成低來躲開**
- 位置:做法 3 第一點。
- 引句:「風險高、首筆規格閘留痕晚於生效日(或沒有任何留痕)」
- file: `scripts/lumos:16278` 現有寫法是 `_rec_plan_risk(rec) == "low"`,用最新留痕的風險值。沒有留痕時才需要現場重判(`_door_judge`)。
- spec 只寫「風險高」。若實作者取現場重判,把〈實務隱患〉改成四行已排除、拿掉硬訊號,計劃現場判成低,就跳過先紅、表、簽。「那四行通常由 AI 自己寫」是決策 d9 自己的承認,先紅表、簽這道正是要擺脫它。
- 沒說有留痕時信哪邊、現場判與留痕不一致時以誰為準。

severity: major
blocking: 是 — 兩種實作都合 spec,其中一種可被計劃作者輕易繞開。

**14. `clause_verdicts` 一條條款只能記一支測試,但條款可以綁多支**
- 位置:做法 2、S6、做法 3「查什麼」。
- 引句:「每條條款記」
- file: `scripts/lumos:15137` 的 `_spec_gate_run_clauses`:一條條款的 `verdicts[cid]` 只留第一個非綠的那一支(`(v, why, method)`)。
- file: `scripts/lumos:14263` 的 `_spec_gate_record` 說明:多平台專案的 tests 一律寫成「平台:名字」。
- 推送前找「同一個條款編號、同一個測試名」的紅,在多測試條款上無從比對。條款綁 A(新)與 B(既有且綠)時,B 永遠沒紅,規則要求每支還是任一支沒講。
- 測試名是否含平台前綴也沒說。

severity: major
blocking: 是 — 多測試條款在推送前要不是永久擋、要不是比對失敗。

**15. 預期值表的格式邊界一個都沒定義,而且 repo 裡沒有現成的 Markdown 表解析可借**
- 位置:做法 4 第一點、S10、S13。
- 引句:「底下一張表,表頭固定四欄」
- 已確認 repo 沒有可重用的 Markdown 表解析函式(grep 找不到)。「借用」清單也沒列。未定義的邊界:
  - 儲存格內的管線字元(`\|`、`||`)。
  - 欄數不是 4、多一欄「備註」、表頭欄名寫錯或順序不同(spec 只說「固定」,沒說不符時怎麼辦)。
  - 同一節有兩張表、重複的標題、`###` 層級。
  - 表寫在程式碼圍欄裡。spec 自己在該節的範例就用反引號寫。若解析器不排除圍欄,圍欄內的示範列會被當成真的列,讓條款覆蓋檢查被偽造通過。
  - 條款欄寫多條(`[S1][S2]`)、寫不存在的條款(`[S99]`)。
  - 對齊列 `|:--|`、省略外側管線。
- 後果有兩種:錯列使真列被丟,條款被當缺而擋下(誤擋)。或圍欄內示範列滿足覆蓋(偽通過)。
- 來源欄的「至少 4 個實字」沒定義實字(英文字母、數字算不算),`TBD1`、`待補充來源` 都能通過。

severity: major
blocking: 是 — 表解析是 S10 與 S13 的底座,邊界不定會同時產生誤擋與偽通過。

**16. 列指紋的「改了任何一個字,指紋就變」不成立**
- 位置:名詞「列指紋」、S12。
- 引句:「改了任何一個字,指紋就變」
- 實測(`unicodedata.normalize('NFKC', ...)`):`2⁵` 變成 `25`、`m²` 變成 `m2`、`①` 變成 `1`。表裡的數字單位在這些寫法互換時指紋不變,不用重簽。
- 連續空白壓成一個,也會讓字串常值的預期值(例如兩個空白對一個空白)改了而指紋不變。
- 兩個都是對表的語意改動不觸發重簽的缺口,位置正好是預期值的數字。

severity: minor
blocking: 否 — 不影響主幹,缺口是數字上標與字串空白這類窄情形。

**17. 一列指紋出現在多筆簽核事件時,人簽或 AI 簽的歸屬沒定義,影響 RETIRE-IF 的統計**
- 位置:做法 5、S14、RETIRE-IF。
- 引句:「算預期值表每一列的列指紋,寫一筆治理帳事件」
- 引句:「AI 簽的列數連續 90 天佔 100%」
- 每次簽核寫的是整張表所有列的指紋(含沒改的列)。人簽整張表,之後 AI 只為一列改動重簽,事件裡所有列又以「ai」寫一次。同一列指紋出現在 human 和 ai 兩筆事件。「N 列由 AI 簽」與 `lumos gov --stats` 的人/AI 列數怎麼算(取最新、取任一人簽、逐事件加總)沒說。逐事件加總會重複計。
- RETIRE-IF 的第二條撤除條件直接建立在這個統計上。

severity: minor
blocking: 否 — 影響統計精度與撤除判斷,不影響擋或放行。

**18. 簽核流程的邊界:30 秒逾時、指紋計算時機、空表、風險低計劃**
- 位置:做法 5 第三點。
- 引句:「沒有互動終端或 30 秒沒回」
- 人慢慢看一張很多列的表,30 秒沒回就被記成 AI 簽。這又直接餵給 RETIRE-IF 的 AI 佔比。file: `scripts/lumos:34193` 的 `_confirm_tty` 預設 30 秒(`LUMOS_TTY_TIMEOUT`)。
- 指紋是在印表之前還是答 y 之後算,spec 沒說。並行會談改表的情形下,簽的是人沒看過的列。
- 表是空的或沒有 `## 預期值表` 時,簽出零列事件,沒有拒絕。對風險低計劃也能簽。
- 事件裡的計劃鍵沒規定,是路徑、迴圈編號,還是要 NFC 正規化。計劃改名或搬動後簽核事件對不上(留痕用 `_loop_id_for_plan`,是檔名主幹)。

severity: minor
blocking: 否 — 都是可在實作時補上的操作細節。

**19. S9 的句子有兩種讀法,而且多個條款共用同一支測試名**
- 位置:S9;S1/S2/S5、S3/S4、S7/S8、S11/S12、S13/S14 的 `[test:]` 綁定。
- 引句:「每條新行為條款都紅過,或推送範圍只因連到同一個系統節點而碰到它」
- S9 把首筆早於生效日、全紅過、只因連結碰到,三件事用頓號和「或」串成一個條件。讀成三者任一則「全紅過但表沒簽」會不擋,和 S13 矛盾。讀成 A 且 B 則「早於生效日但沒全紅過」沒被覆蓋,與「不回頭擋」不一致。
- S1、S2、S5 綁同一支 `t_spec_gate_red_reason_assert`,三種行為綁一支測試,一支測試很難在三個情境都失敗。

severity: minor
blocking: 否 — 措辭問題,由實作時再拆即可。

**20. 生效日是日期還是時間點、「晚於」是否含當天,都沒說**
- 位置:名詞「生效日」、做法 1、做法 3。
- 引句:「這份計劃合併上主線的那天,寫成程式常數」
- 先例是帶時區的時間點:file: `scripts/lumos:13714` 的 `_SPEC_GATE_SINCE = "2026-09-18T00:00:00+08:00"`,比對用 `>=`。spec 寫「那天」。
- 帳裡有混時區的 ts:`2026-10-04T08:54:10+00:00` 等多筆,和 +08:00 的字串比較不一致。
- 同一天邊界:合併日當天的留痕在合併前後都可能。這份計劃自己就是例子,建立日與預計合併日同一天,它自己的首筆規格閘留痕落在哪一邊沒有答案。
- ts 解不開時(`_loop_ts_key` 回 None)被跳過,所謂「首筆」可能變成 None,被當成新計劃。
- spec 的「首筆規格閘留痕」(kind=spec-gate)和現有 `_loop_first_ts_key`(迴圈任一筆帳)不同,沒說明為何不沿用。

severity: minor
blocking: 否 — 邊界落在合併日當天與少數壞 ts,影響面小。

**21. 候選裡的計劃檔狀態:被刪、被改名**
- 位置:做法 3 第一點。
- `git diff --name-only` 會列出被刪的計劃檔。file: `scripts/lumos:16108` 的 `_spec_gate_push_nogo_only` 開頭有 `if not p.is_file(): return None`,spec 沒說新檢查要不要同樣處理。
- 計劃改名(`_計劃` 後綴拿掉、搬資料夾)後,留痕以舊迴圈編號為鍵,新檔名沒有任何留痕,被當新計劃。生效日前的舊計劃改名後就失去豁免。

severity: minor
blocking: 否 — 影響罕見的改名與刪檔推送。

**22. 讀報告的資源邊界:檔數、檔案大小、重複掃描**
- 位置:效能節。
- 找 `build` 目錄要走整個 repo,spec 沒有排除清單(`node_modules`、`.git`、`Pods`),只設總時間上限。
- 每支測試各一次 Gradle,每次後都再走一遍目錄。條款多的計劃會重複走很多遍。
- 單個 XML 沒有大小上限。file: `scripts/lumos:8593` 只有 `_SECEV_FACTS_MAX = 100000` 案例數上限;安全證據閘本身有 `_SECEV_FILE_MAX`(16MB),spec 沒說比照。
- 有一份報告被整檔拒收(重複身份、`zero_cases`、`suite_error`)就影響同檔所有測試。實測(`t2.py`):同一檔內兩個同名 testcase,`junit()` 整檔拒收(`report_duplicate_identity`)。一支無關的重複名測試會讓該檔所有測試落進判法 d。多個報告檔裡一檔被拒收時,判法 d 是只對該檔還是整批,spec 沒說。

severity: minor
blocking: 否 — 屬效能與資源邊界,正常規模專案影響有限。

**23. 交叉引用核對:三處主幹的引用與 d3 的引文**
- d1 引用的目標都存在:
  - `Systems/規格閘` 有「風險高照半套:紅綠只印不擋」,在 KEY 第 39 行。
  - `Projects/規格閘紅燈測試快照_計劃` 〈四、不做〉第 93 行有「不改風險高計劃『不強制先紅』的規則」。
  - 該 KEY 綁 `t_spec_gate_oneway_keeps_halfset`,spec 保留規格閘「紅綠只印不擋」,所以這條 KEY 仍成立。
- d3 引用的 d9 存在,在 `Projects/規格落成可驗收條件_計劃` 第 71 到 72 行,內容是「Enzo 裁不補人簽門」,範圍確為風險低四行已排除理由,跟 d3 區分正確。
- d3 對 `Projects/業務簽核留痕_計劃` 的引文是「何時該簽由人判,工具不擋」,原文(該檔第 23 行)是「何時該簽由人/流程判,工具不擋」。少了「/流程」,依引文 grep 找不到那句。
- 第三處主幹「推送前檢查只在 pre-push 跑」:`.github/workflows/ci.yml` 沒有呼叫 `spec-gate --push-check`,與 spec 一致。
- 已讀,其餘引用(三條反引號路徑、`Projects/Android測試防竄改檢查_計劃`、`Systems/test-guard` 等)存在,無問題。

severity: minor
blocking: 否 — 只是引文漏字,不影響行為。

## 圖譜鏡頭(固定席節點)

- `Systems/test-guard`:不破壞它宣稱的行為與合約,第一批不碰它的比對函式。第二批的 REVISIT 與它同日(2026-12-15),一致。但它已記下「catch 接斷言失敗照型別名字的字尾認,不逐一列字表」的決定,d2 借白名單方向相反(見第 6 條)。
- `Systems/test-quality-evidence`:不影響。spec 只借不改 `test_quality.py`。借用面不足見第 5 條。
- `Systems/guard-kill`:兩條 INVARIANT(rc 優先序、`--json` 純度)不影響。第一批不改 guard kill 的程式。`_run_bound_tests` 的呼叫端是規格閘判定與推送前合約測試(`scripts/lumos:15111`、`69374`),不是 guard kill。第二批「不自動產生變異」的衝突,spec 已明文處理並延後。
- `Systems/test-quality-cli`:不影響。它的 WHY(裝置報告含堆疊樣行與 `Caused by:` 時判成不是斷言)與第 5 條相關。
- `Systems/lumos-cli-lifecycle`(INVARIANT:re-inject 只覆蓋 sentinel 之間):不影響。本計劃不碰 CLAUDE.md 注入。
- `Verification/測試品質第四輪修補驗證`:不影響。

## 實務隱患逐類

- 併發:並行會談改簽核表(第 18 條,指紋計算時機);`bound_tests.parallel` 讓同一 `build` 目錄同時有多個 Gradle(第 8 條);兩個規格閘同時跑,spec 自己的「誤擋二」已列。
- 效能:找 `build` 目錄的全 repo 走訪與重複掃描(第 22 條);讀兩本共約 27MB 的帳,每次推送新增一次(量級可接受,不單獨列為 finding)。
- 資源:XML 檔數與大小沒有上限(第 22 條)。
- 回滾:第 12 條,沒有留痕的計劃不受常數控制,回退不成立。
- 帳本完整性:欄位型別不對導致例外被 hook 當擋下(第 2 條);兩份帳的合併規則缺(第 3 條)。
- 繞過:第 11 條(零條款、全 keeps、全 manual)、第 13 條(改風險來源)。

最嚴重的 severity 是 major,blocking 共 15 條(第 1 到 15 條)。第 16 到 23 條為 minor、blocking 否。
