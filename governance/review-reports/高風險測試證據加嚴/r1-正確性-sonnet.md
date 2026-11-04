severity: blocker

我把 F1–F18 全文重交,內容、severity、blocking、佐證都沒改,只在每條加了逐字引句行。總結行的條數上一版寫得混亂,這版改正:blocker 1、major 13、minor 4,blocking 共 14 條。

圖譜鏡頭(內容不變):
- **guard-kill 兩條 INVARIANT:** 不影響。這份設計不碰 `guard kill` 的 rc 優先序和 `--json` 輸出。
- **lumos-cli-lifecycle 的 re-inject INVARIANT:** 不影響。這份設計不碰 sentinel 之間的注入邏輯。
- **test-quality-evidence 與 test-quality-cli:** spec 只借 `test_quality.py` 的 `junit()` 與斷言白名單,不改檔,部署指紋(`_TEST_QUALITY_BUNDLE_DIGESTS`)不受影響。但借用的介面不夠用,見 F2、F3。

**F1.** 沒有 `[SN]` 條款的計劃,永遠拿不到規格閘留痕,卻會被推送前判成「沒留痕就擋」,而且無解。
- 位置:做法 3 末句,加上「候選計劃」的取法。
- 引句:「沒有任何留痕的,擋下並請它先跑規格閘。」
- 問題:候選計劃取的是推送範圍內任何 `Projects/*.md`(含 `_調研`、舊計劃),不限 `_計劃`。這類筆記的門判定預設是風險高,而且規格閘不會替它寫留痕。
- 重現:推送同時改到 `Projects/世界解重新註解2026-10_九類之外_調研.md` 和任一程式檔。
  - 我跑了 `lumos spec-gate "Projects/世界解重新註解2026-10_九類之外_調研" --no-run`,印出「計劃風險: 高」和「計劃無 [SN] 條款,沒有東西可驗」,不會留痕。
  - 照 spec 的規則,這次推送被擋,訊息叫人先跑規格閘,但跑了仍沒有留痕,擋下永遠不會解除。
- 另有三條路也不會留痕:
  - 相依回歸沒過,`cmd_spec_gate` 在寫留痕前就 `return 1`。
  - 平台設定讀不動,提早 `return 0`。
  - 帶 `--no-run`。
- 佐證:file: `scripts/lumos:15002`(無條款提早回 0)、file: `scripts/lumos:15415`(回歸沒過先回 1)、file: `scripts/lumos:15534`(`_spec_gate_touched_plans` 只認 `Projects/*.md`)。
severity: blocker
- blocking: 是。實作者照寫會做出永遠擋不掉的推送。

**F2.** 判法 b 與 c 無法用 spec 指定的 `_secev_junit_facts` 區分,a 的「讀失敗內文」也做不到。
- 位置:做法 1 的判法 a–c。
- 引句:「用 `_secev_junit_facts` 讀成 `{身份: (狀態, 是否斷言失敗)}`」
- 問題:`_secev_junit_facts` 只回 `(狀態, 是否斷言失敗)`。「有失敗型別但不是斷言」(b)和「根本沒有型別」(c)在這個結構裡都是 `False`。內文也不在回傳裡。
- 佐證:file: `scripts/lumos:8883`。`junit()` 的 `reason` 在 file: `scripts/test_quality.py:238` 被截成 4000 字。我造了一份 400 行堆疊後才出現 `Caused by: kotlin.NotImplementedError` 的報告,讀回的 `reason` 裡沒有這個字,a 會誤判成「斷言」。
- 影響:`test_quality.py` 不准改,實作者得另寫一支 XML 讀法或猜,做法要補上。
severity: major
- blocking: 是。實作者要自行決定,而且很可能做錯。

**F3.** 借來的斷言白名單會把常見的合法紅判成「非斷言」,而且 spec 給的補法無效。
- 位置:d2 與判法 b。
- 引句:「Truth、AssertJ、kotlin.test、MockK 的 verify 都丟 `AssertionError` 子類」
- 我拿 `test_quality.junit()` 實測 `assertion_failure`:

  | `type` | 結果 |
  |---|---|
  | `org.mockito.exceptions.verification.WantedButNotInvoked` | False |
  | `org.mockito.exceptions.verification.opentest4j.ArgumentsAreDifferent` | False |
  | `org.opentest4j.MultipleFailuresError`(JUnit5 `assertAll`) | False |
  | `org.assertj.core.error.AssertJMultipleFailuresError` | False |
  | `io.mockk.MockKException` | False |
  | `org.opentest4j.AssertionFailedError`、`java.lang.AssertionError`、`org.junit.ComparisonFailure` | True |

- 重現:新行為測試用 Mockito 的 `verify` 或 `assertAll`,空殼回傳預設值,測試在斷言上紅。這支測試永遠判成弱證據(非斷言),spec 印的補法「空殼改回傳預設值」沒有用,推送前也永遠擋。
- 佐證:file: `scripts/test_quality.py:108`。spec 調研段說 MockK 等都丟 `AssertionError` 子類,但白名單比對的是型別字串結尾,不看繼承。
severity: major
- blocking: 是。

**F4.** 判法 a 的內文比對可能誤傷合法斷言。
- 位置:判法 a。
- 引句:「例外鏈出現 `NotImplementedError` 或 `UnsupportedOperationException` 就判非斷言」
- 問題:可取得的只有失敗內文字串,斷言訊息裡的預期值和實際值也在其中。
- 重現:新行為是把 `UnsupportedOperationException` 對應成 HTTP 501,測試 `assertEquals("UnsupportedOperationException", mapped)` 在斷言上紅,訊息含該字樣,被判成非斷言。
- 做法沒寫要限定在 `Caused by:` 行或 `type` 屬性。
severity: major
- blocking: 是。同樣是合法紅被永久擋,沒有出口。

**F5.** 報告讀取時機與 `_run_bound_tests` 的資料流對不上,同一測試類別裡的多條條款會互相覆蓋報告。
- 位置:做法 1 第一句。
- 引句:「規格閘跑完一支 Kotlin/Java 測試、退出碼判紅時,在 repo 裡名叫 `build` 的目錄底下找這次跑出來的報告」
- 問題:`_run_bound_tests` 先把所有測試跑完,才回傳逐支結果,中間沒有逐支的鉤子。
- Gradle 用 `--tests '*{method}'` 每支跑一次,報告檔名是 `TEST-<類別>.xml`,後跑的會覆蓋先跑的。
- 重現:`[S1]` 綁 `FooTest.a`、`[S2]` 綁 `FooTest.b`,規格閘批次跑完後只剩 `b` 的報告,`a` 被判 d(沒跑到)而變弱證據,先紅證據永遠湊不齊。
- 平台設定允許並行跑,同一個 build 目錄下並行的報告也互相覆蓋。
- 誤擋二只談「兩個規格閘同時跑」,漏了這個單一規格閘內部的情形。
- 佐證:file: `scripts/lumos:69029`(`_run_bound_tests` 的 jobs / results 流程)、file: `scripts/lumos:15105`。
severity: major
- blocking: 是。

**F6.** 判法 c 沒處理「找得到但狀態是 passed/skipped,而退出碼非 0」。
- 位置:做法 1 判法 c。
- 引句:「找得到、但報告沒有失敗型別(跑在手機上的測試報告就是這樣):照退出碼判紅」
- 問題:passed 的測試也沒有失敗型別,會落進 c 被判成紅(未判)。
- 重現:多模組專案跑 `./gradlew test --tests X`,別的模組因「No tests found」讓整體退出碼非 0,但報告裡該測試已經 passed,於是被記成紅。這正是先紅要擋的假紅。
- 判法應補一條:報告顯示 passed 或 skipped 時,不算紅。
severity: major
- blocking: 是。

**F7.** 推送前只驗列指紋,不重驗預期值表本身是否還在,刪表就繞過。
- 位置:做法 5 推送前檢查,對照做法 4(S10 只在規格閘擋)。
- 引句:「預期值表每一列的列指紋都要出現在這份計劃的某筆 `expected-sign` 事件裡」
- 問題:規格閘通過並簽核後,把 `## 預期值表` 整節刪掉,或只刪掉對不利條款的列。剩下的列(零列時是空集合)指紋全已簽過,推送前放行。
- 高風險路徑沒有類似低風險 `clause_sha` 的過期檢查,也不重驗「每條新行為條款至少一列、來源至少 4 字」。
severity: major
- blocking: 是。整道簽核可被一次刪除繞過。

**F8.** 高風險計劃可以把新行為條款標成 `[keeps]`,整套先紅、預期值表、簽核全部豁免。
- 位置:名詞「新行為條款」與做法 3。
- 引句:「風險高也叫 `_spec_gate_keeps_rows` 算 keeps」
- 問題:低風險計劃有 `_spec_gate_twoway_static`:標 keeps 的測試必須在計劃建立前就存在,且要綠。spec 只借解析,沒有借這個檢查。
- 佐證:file: `scripts/lumos:15258`。`_spec_gate_front` 對高風險直接給 `keeps = set()`,不跑 twoway。
- 做法也沒規定「全部條款都標 keeps 或 manual」時要怎麼辦,這時新行為條款為零,所有檢查空轉通過。
severity: major
- blocking: 是。

**F9.** 「首筆規格閘留痕」的判定,在多種帳面狀態下會誤判。
- 位置:名詞「首筆規格閘留痕」、做法 1 與 4 的觸發條件。
- 引句:「規格閘跑完才寫留痕,被擋下(rc1)的那次不寫;從沒有留痕的計劃一律當成生效日之後的新計劃」
- 引句:「治理帳被 git 忽略的消費專案」
- 以下各情形,spec 都沒寫該讀哪本帳、該怎麼取最早:
  - **只有被擋的跑過:** rc1 不寫留痕,生效日前就開始、一直被擋的在途計劃,通過那天被當新計劃。這是 spec 刻意選的,但與做法 1 的「在途不追溯」互相矛盾。
  - **迴圈編號改過:** 迴圈編號由檔名推導(`_loop_id_for_plan`)。計劃改檔名後,舊留痕在舊編號下,新編號的首筆在生效日後,舊計劃被當新計劃。紅證據也跟著斷。
  - **留痕只在審查帳、不在治理帳:** 消費專案的審查帳被 gitignore(file: `scripts/lumos:33128` 附近的 scaffold 註解)。乾淨 clone 或 worktree 讀不到早期留痕,首筆晚於生效日,誤判成新計劃。
  - **反過來:** 做法 3 寫「在審查帳…找紅的紀錄」,只讀審查帳的話,消費專案在別台機器上一律是「沒留痕」。要用審查帳與治理帳合併的讀法,spec 要寫。
- 另一處不一致:天花板二寫「治理帳被 git 忽略的消費專案」,與名詞段「治理帳設計上進版控」相反,實際被忽略的是審查帳。
severity: major
- blocking: 是。

**F10.** 現有的讀帳介面不夠用,實作者照 spec 字面做會得到「全部沒紅」。
- 位置:做法 3 第二段。
- 引句:「在審查帳這份計劃的所有規格閘留痕裡」
- 佐證:file: `scripts/lumos:15792`。推送前讀審查帳時用 `_SPEC_GATE_PUSH_FIELDS` 白名單過濾欄位,不含 `clause_verdicts`。治理帳那份保留整筆。只讀審查帳索引會永遠看不到任何紅,所有候選計劃被擋。
- `_spec_gate_latest_merged` 只回每條迴圈最後一筆(file: `scripts/lumos:15519`),spec 需要的是全部留痕與最早一筆,沒有現成函式。
severity: major
- blocking: 是。

**F11.** 候選計劃的挑法同時誤擋與漏查。
- 位置:做法 3「哪些計劃要查」。
- 引句:「這次推送範圍改到那份計劃檔、同時也改到程式檔;或那份計劃的 status 已經是 done」
- 引句:「最後把 status 改成 done 的那次推送會查」
- **誤擋:** 條件只要求「計劃檔被改到,而且推送裡有任何程式檔」,不要求程式檔屬於這份計劃。設計審階段的高風險計劃(測試還沒寫,當然沒有紅)只要與不相干的程式修正同批推送,就被擋。spec 自己說「不能擋別人的推送」,與此矛盾。
- **漏查:** 現有 `_spec_gate_push_candidates` 的註解(編排者實測 E2)說,實作提交常只動程式檔與 Systems 家,不動計劃檔。這種提交完全不查。
- **永遠不查:** 計劃一直停在 doing、從不翻成 done,就永遠不被檢查。天花板四只承認「翻 done 那次會查」。
- 另:做法 3 的「status 已是 done」條件,在現有候選機制下只有計劃檔被碰到才會成立;措辭暗示不碰也查,實作者可能擴大候選。
severity: major
- blocking: 是。

**F12.** 紅因對應的資料結構沒定義。
- 位置:做法 2 的 `clause_verdicts` 與做法 3 的「同一個條款編號、同一個測試名」。
- 引句:「每條條款記 `{判定, 紅因, 測試名}`」
- 問題:
  - `_spec_gate_run_clauses` 的聚合規則(file: `scripts/lumos:15127`)是每條條款只留一個 `(判定, 原因, 方法)`,而且「紅蓋過弱證據」。
  - 一條條款綁兩支測試時,記一個測試名。推送前若逐支比對,另一支永遠找不到紅;若只比一支,另一支可以是永不紅的空測試。
  - 多平台時,留痕的 `tests` 是「平台:名字」,`clause_verdicts` 的「測試名」用哪種沒寫。
  - 紅因只有三種值(斷言、未判、非斷言),判法 d 的弱證據沒有對應值。
  - 現有 `rows` 元組沒有紅因,要擴欄,四個呼叫端都受影響。
severity: major
- blocking: 是。

**F13.** 簽核事件的人簽/AI 簽統計會被去重吃掉,逐列歸屬也沒定義。
- 位置:做法 5 最後一條。
- 引句:「`lumos gov --stats` 分開算人簽與 AI 簽的列數」
- 佐證:
  - file: `scripts/lumos:17056`。治理帳統計去重鍵是 `(commit, nodes, gate, kind, token, check)`。`signoff --expected` 在同一個 HEAD 簽兩次(中間沒有提交),事件被折成一筆。spec 只提到 `_gov_row` 要加欄位,沒提去重鍵要加 token。
  - 一筆事件帶整張表的指紋、一個簽核人類別。人簽五列後,改一列再由 AI 簽,AI 事件含全部五列的指紋。「表裡有 AI 簽的列」的歸屬規則沒定義,AI 簽列數會灌水。
  - RETIRE-IF 第二條(AI 簽 100%)就靠這個統計。
severity: major
- blocking: 是。

**F14.** 回退不是三組各自獨立。
- 位置:回退段。
- 引句:「紅因判讀那組設成遠未來,規格閘回到只看退出碼(`clause_verdicts` 欄留在舊留痕無害,讀側當沒記)」
- 引句:「第一批各塊各自可退,三組生效日各一個常數(初值同一天)」
- 問題:把紅因判讀組設到遠未來,規格閘回到只看退出碼,而且「讀側當沒記 `clause_verdicts`」。推送前先紅那組(第 2 組)仍開著,就會找不到任何紅,所有高風險推送被擋。
- 必須先退推送前那組,或規定 `clause_verdicts` 在第 1 組退掉後仍照寫(紅因記未判)。
severity: major
- blocking: 是。

**F15.** 列指紋的正規化會讓意思不同的兩列相同。
- 位置:名詞「列指紋」與 S12。
- 引句:「預期值表一列的四格各自去掉頭尾空白、連續空白壓成一個、全形半形統一(NFKC)之後,用 Tab 接起來算 sha256」
- NFKC 把上標與帶圈數字折成普通數字:`unicodedata.normalize('NFKC', 'r²')` 等於 `'r2'`,`'①'` 變 `'1'`,`'㎡'` 變 `'m2'`。公式或單位寫成「面積 r²」與「面積 r2」的指紋相同,語意改了不必重簽。
- 其他缺口:
  - 「空白」是否含 Tab 沒定義。Tab 若在格內保留,而 Tab 又是接合字元,`("a\tb","c")` 與 `("a","b\tc")` 相撞。
  - 表格解析沒寫:轉義的 `\|`、少於或多於 4 格的列、分隔列。多出第 5 格時,改它不會改指紋。
  - 預期與輸入欄允許為空,只檢查來源 ≥4 字。
severity: minor
- blocking: 否。實作者能補。

**F16.** 找報告的範圍有三處與實況不符。
- 位置:做法 1、實務隱患的誤擋一與效能。
- 引句:「走目錄的時間另設上限,逾時就把沒判完的當未判、印一句」
- 引句:「在 repo 裡名叫 `build` 的目錄底下找這次跑出來的報告」
- 問題:
  - 平台的 `root` 可以在 repo 外(file: `scripts/lumos:21967` 有「平台根在樹外」),報告會落在 repo 外。
  - Gradle 自訂 `buildDir` 名稱(不只 `outputLocation`)也會找不到,誤擋一只談到後者。
  - 逾時時「把沒判完的當未判」是紅,與找不到時的 d(弱證據)方向相反,是 fail-open。檔案系統慢時,`TODO()` 空殼會被當成紅放行。
severity: minor
- blocking: 否。

**F17.** 名字比對與模組衝突沒定義。
- 位置:做法 1「比方法那一段」。
- 引句:「找名字對得上這支測試的那一筆」
- 問題:
  - JUnit5 在 XML 的測試名帶 `()`,參數化測試帶 `[n]`,spec 沒寫正規化。照字串相等比,Jupiter 測試全落在 d。
  - 不同模組同名方法時取哪一筆沒寫。
  - 單一壞報告(如 `report_duplicate_identity`)是只影響該檔,還是讓整批變 d,也沒寫。
  - `_secev_tq()` 回 None(配套缺檔)時的行為沒寫。
- 我沒有本機的 Gradle 可以驗 `()` 這點。
severity: minor
- blocking: 否。

**F18.** 其他小處。
- 位置:做法 3 末條、做法 5、名詞、做法 4。
- 引句:「pre-push 掛鉤與 `_spec_gate_push_check` 各一處」
- 擋下訊息寫死「風險低」的地方不是「各一處」:pre-push 有兩行(file: `scripts/hooks/pre-push:581`、`:582`,一行 echo 和一行 `pp_record_block` 的理由),`_spec_gate_push_check` 有表頭和結尾兩句。結尾那句「把條款的測試做綠再推」對高風險是錯的補法。
- `signoff --expected` 對沒有預期值表的計劃、風險低計劃、生效日前的計劃的行為沒寫(空事件會被記成簽核)。
- 「迴圈編號最早」字面可讀成編號字串最小,應寫成 ts 最早。
- 來源欄 ≥4 字的檢查,「見計劃內文」就過了,只是個象徵性門檻。
severity: minor
- blocking: 否。

**實務隱患鏡頭(逐類,內容不變)**
- **併發:** 有隱患。見 F5(同類別報告覆蓋、並行 worker)。簽核事件追加寫入各自一行,無新隱患。
- **效能:** 有小隱患。walk 逾時變 fail-open(F16)。推送前新增一次整檔讀治理帳(本庫約 20MB),可併進現有讀取,影響不大。每個 XML 沒有大小上限,`tq.junit` 是串流且深度上限 64,風險低。
- **資源:** 無實質新增。沒有新增暫存檔、子程序或長駐程序。
- **回滾:** 有隱患。見 F14。
- **誤擋/漏放:** 見 F1、F3、F4、F6、F7、F8、F11。
- **相容(舊資料):** 見 F9、F10。舊留痕沒有 `clause_verdicts` 的處理本身是對的。

**其餘各節已讀,無 finding:** 調研結論、不做、驗收條款的格式(S1–S14 各綁一個測試名,測試名只是待建立,不是缺口)。

總結:最嚴重 severity 是 blocker,blocking 共 14 條(F1 為 blocker,F2–F14 共 13 條為 major),另有 4 條 minor(F15–F18)為 blocking 否。
