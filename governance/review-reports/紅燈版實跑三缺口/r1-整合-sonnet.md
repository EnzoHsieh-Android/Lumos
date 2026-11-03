severity: major

# 紅燈版實跑三缺口 r1 整合席審稿

一句白話:三個缺口的診斷都屬實,我拿真函式重現過。但修法有三處會讓修完的東西仍然不管用,甚至把以前補好的安全性質弄丟。

## Finding

### F1 〈做法〉1 與 S1:兩邊都要求深度 0 的規則,把「字串裡有不成對括號」整類漏報留了下來
- 引句:「已知不處理:字串裡有不成對的括號時(`"a(b"`),原文深度在字串後面仍是 1」
- 問題:缺口 1 的症狀是字串內容擾亂切參數,導致預期值被改卻漏報。「字串裡有不成對括號」是同一族,而且這份設計明說不處理。
- 我把提議的切法(遮罩與原文兩邊深度都是 0 才切)在真函式旁重現了一遍。切出來仍是單一參數的有:
  - `assertEquals("1) 項目", label(fee))`
  - `assertEquals("結帳(含服務費", label(fee))`
  - `assertEquals('(', sep(fee))`
- 切成單一參數後,`_tg_split_first_arg` 的 `len(args)` 不是 2,`_tg_split_expected` 回 None,預期值被改照樣漏報。
- 這類字串(「1) 」編號、「(含稅」)在 UI 標籤斷言裡並不罕見。
- 〈做法〉1 只要求「模板巢狀引號」不退步,代價是整類漏報被固化。S1 不含這類案例,也沒有 `REVISIT:` 回頭條件(CLAUDE.md 鐵則 4:承認風險要附回頭看的條件)。
- 佐證:file: `scripts/lumos:47979`(`_rg_split_args`)、file: `scripts/lumos:48968`(`_tg_call_parts`)。
severity: major
blocking: 是——同族缺陷整類留下且沒有回頭條件,屬 major。

### F2 〈做法〉3 與 S4:教人加的忽略否定行,在規則住在 docs/.gitignore 時無效
- 引句:「加一行 `!docs/.governance-log.jsonl` 或把那條規則收窄」
- 問題:`lumos init` 產的忽略設定寫在 `docs/.gitignore`,pattern 是 `.governance-log.jsonl`,這正是歷史上會忽略治理帳的位置。
- 我在暫存 repo 實測:
  - `docs/.gitignore` 內有 `.governance-log.jsonl`,根 `.gitignore` 內有 `!docs/.governance-log.jsonl`。此時 `git check-ignore -v` 仍回 `docs/.gitignore:1:.governance-log.jsonl`,rc 0。
  - 更深層的檔案優先權較高,根目錄的否定行蓋不過去。
  - 在 `docs/.gitignore` 裡寫相對路徑 `!.governance-log.jsonl` 才有效。
- 照訊息做的人會改了、再推、還是同一條提醒。S4 只驗「講明並附規則」,沒驗「照改法做會真的解除」。
- 佐證:
  - file: `scripts/lumos:32897`(init 寫 `kg.parent / ".gitignore"`,即 docs/.gitignore)
  - file: `docs/lumos-toolchain-knowledge/Projects/消費專案接入靜默失效_計劃.md:46`(寫明新專案曾建出忽略治理帳的 docs/.gitignore)
severity: major
blocking: 是——改法在常見設定下無效,S4 驗不出來。

### F3 〈做法〉3 與 S4:兩句提醒被整句取代,丟掉「不要刪紅燈版檔」與「git add 紅燈版檔」
- 引句:「被忽略時兩句提醒都換成「治理帳被 git 忽略(來源:行號:規則),規格閘留痕進不了提交」
- 問題:現行孤兒提醒明寫「不要刪這支檔,改拿它的內容來比」。這是代碼審 r2 資安席的修法,理由是照訊息刪檔後改弱會變零候選。
  - Systems/test-guard 的 WHY 寫明「訊息不叫人刪檔」。
  - 既有測試釘死「不要刪」,只在治理帳沒被忽略的情況下釘。新分支不受它保護,S4 也沒要求新措辭保留。
- 「還沒提交」那句,新文字只講改忽略規則,沒講還要 `git add` 那支紅燈版檔。照做後下一次推送又會碰同一條候選。
- 佐證:
  - file: `scripts/lumos:49764`(孤兒訊息)
  - file: `scripts/lumos:49679`(還沒提交訊息)
  - file: `scripts/test_lumos.py:122714`(釘「不要刪」)
  - file: `docs/lumos-toolchain-knowledge/Systems/test-guard.md:41`(WHY:訊息不叫人刪檔)
severity: major
blocking: 是——在新分支重新打開已修過的資安 finding。

### F4 〈做法〉2 與 S2、S6:修完後推送前會真的在平板上跑,沒人的時候照樣紅並再記一筆假逃逸
- 引句:「推送前照前綴的平台指令跑那一支」
- 問題:修完後 `device:名` 會用 device 平台指令跑,執行上要有接著的平板。`_spec_gate_push_one` 把所有 `v != "green"`(含弱證據)一律當 reds,接著呼叫 `_auto_escape`。
  - 沒接平板時(例如 Gradle 儀器測試回 No connected devices,⚠ 此行為我沒在考場驗,依一般 connectedAndroidTest 行為推斷)就是紅,擋推送並再記一筆「假逃逸」。這正是缺口 2 要消除的症狀,只是原因從「找不到測試」換成「沒平板」。
  - 單測逾時預設 180 秒。pre-push 是唯一的閘,CI 的 ci.yml 並不跑 `--push-check`。
- 設計沒寫:沒平板時該判紅、判弱還是略過,也沒寫要不要記逃逸。實務隱患節也沒有這一類。
- 佐證:
  - file: `scripts/lumos:15947`
  - file: `scripts/lumos:15963`(自動記逃逸)
  - file: `scripts/lumos:68668`(`_run_bound_tests`,`LUMOS_TEST_TIMEOUT` 預設 180)
severity: major
blocking: 是——根因治好後,同一個「假紅加假逃逸」會被環境缺席重新觸發,設計沒答。

### F5 〈做法〉1 與 S1:S1 只覆蓋 assertEquals,串接寫法與同樣吃這個切法的其他規則沒有測試
- 引句:「`_rg_split_args` 加一個選填的遮罩參數(長度同原文)」
- 問題:`_tg_call_parts` 在 48976 切主呼叫、在 48983 切串接呼叫,兩處都要帶遮罩。設計只提了前者,S1 的案例也只有 assertEquals。
- 真函式重現:
  - `assertThat(x).isEqualTo("a, b")` 的串接參數被切成 `['"a','b"']`。
  - `_tg_split_chain` 用 `",".join` 回併,空白被吃掉,得 `"a,b"`。
  - 所以把 `"a, b"` 改成 `"a,b"` 的竄改,現況與只修主呼叫的版本都看不出來。
- 同一支切法還餵 `_tg_const_stmt`(49044)與 `_tg_pair_key`(49087)。修後「含逗號字串的常值斷言」、配對鍵會連帶改變,多出新候選。〈實務隱患〉相容條只談留痕,沒談 tq/ 候選的變化。
- 若實作漏掉串接那處,S1 不會翻紅。
- 佐證:file: `scripts/lumos:48983`
severity: minor
blocking: 否——是驗收覆蓋缺口與相容面漏列,修法方向本身沒錯。

### F6 〈做法〉2:留痕 tests 的來源集合沒說清楚
- 引句:「呼叫端另把 `_spec_gate_items` 算出的 (條款, 平台, 方法) 傳進來」
- 問題:現行 `tests` 取自 `names`(所有條款,含懸空的引用,見 `_spec_gate_prepare`)。`_spec_gate_items` 只收 `state == "bound"` 的條款。
- 改用 items 時,風險高計劃的懸空引用會從 tests 消失。`manual_only: not tests` 與 `small_change_rule` 會跟著翻成「全靠人驗」。
- `_ledger_has_manual_only`(60910)掃的就是 `"manual_only": true`,會因此多印「審查帳有全靠人驗的風險低留痕」的提示。
- 設計沒指定要維持哪個集合,S2 也沒驗。
- 佐證:
  - file: `scripts/lumos:14183`
  - file: `scripts/lumos:15104`
  - file: `scripts/lumos:14887`
severity: minor
blocking: 否——只影響風險高留痕的輔助欄位與提示,不影響放行判定。

### F7 〈做法〉2:新前綴會在平台改名或移除後,讓推送前直接丟 ValueError
- 問題:`resolve_test_refs("[test:device:foo]")` 在 device 平台不存在時會 raise,我用真函式驗證過。
- `_spec_gate_push_one:15947` 沒有 try。`_cli` 只接 `WriteBlocked`,所以結果是 traceback、rc 1。pre-push 把 rc 1 當「條款測試沒全綠」記一筆阻擋。
- 觸發路徑:`.lumos/config.json` 改了平台名,條款文字沒動所以指紋不變。設計自己也承認「條款指紋不含平台設定」。
- 舊格式(只有名字)不會有這個崩法。
- 佐證:
  - file: `scripts/lumos:6472`(`_split_test_ref_ex` 的 raise)
  - file: `scripts/lumos:15947`
  - file: `scripts/lumos:73989`
severity: minor
blocking: 否——需要平台改名這個罕見操作,結果是擋下而非放行,但訊息誤導。

### F8 〈做法〉2:「預設平台照舊寫名字」把缺口 2 的根因留在新留痕裡
- 引句:「預設平台照舊寫名字(舊讀者不受影響)」
- 問題:舊讀者其實本來就認前綴(`_spec_gate_push_one` 走 `resolve_test_refs`,我在 F7 的驗證中確認過),所以「舊讀者不受影響」不是不一律加前綴的理由。
- 只要 `default_platform` 在留痕後改了,裸名字會在讀取時被重新解成新預設平台。這和缺口 2「平台資訊在記錄時丟失」同一根因,只是搬到預設平台。
- 佐證:file: `scripts/lumos:6419`(`resolve_test_refs`)
severity: minor
blocking: 否——需要改預設平台的設定變動,而且另一側已有 S3 的推斷補救。

### F9 〈做法〉3:只在兩處症狀貼提醒,治理帳被忽略的根因沒有單一偵測點
- 引句:「規格閘寫出紅燈版時也照同一個判法問一次,被忽略就多印一行同樣的提醒。」
- 問題:治理帳被忽略的影響遠不只紅燈版。
  - 代碼審留痕在 CI 靠治理帳讀(`_codeloop_read_from_ledger`)。
  - 規格閘留痕的推送前檢查也讀治理帳(`_spec_gate_push_no_record` 的提示「本機帳不在、或從沒跑過規格閘?」同樣指錯方向)。
- 這些在治理帳被忽略的專案都會靜默失效,只有跑紅燈版的人會看到新提醒。
- `_local_ledger_doctor_msgs` 已經是「帳檔已追蹤/沒被忽略」的 doctor 單一偵測點,而且 pre-push 與收工都會跑 doctor。
- 設計的「舊否決比對」與 PRIOR-ART 沒考慮在這裡加一條「治理帳被忽略」的偵測。
- 佐證:
  - file: `scripts/lumos:1752`
  - file: `scripts/lumos:2910`(doctor 呼叫處)
  - file: `scripts/lumos:15997`(`_spec_gate_push_no_record`)
  - file: `scripts/lumos:67894`
severity: minor
blocking: 否——現行三缺口的症狀仍會被修到,這是治本與治標的取捨,沒有具體新失敗。

### F10 〈做法〉3:`check-ignore` 的失敗行為與逾時沒寫
- 問題:設計要連呼叫 `git ls-files`、`check-ignore -q`、`check-ignore -v` 共 2 到 3 次。`_lens_git` 預設單次逾時 20 秒,沒有算進比對工具的 deadline(同檔 `_tg_rb_pending` 有先例)。
- 設計沒寫:這幾次 git 回 None 或 rc 128 時,是退回舊措辭還是靜默。`_local_ledger_doctor_msgs` 的先例是 continue,不提醒。
- 解析 `-v` 輸出的 `來源:行號:規則` 時,來源路徑含非 ASCII 會被 quotePath 引號包住,沒說要用 `-z` 或 `quote=True`。
- 佐證:
  - file: `scripts/lumos:64953`(`_lens_git`)
  - file: `scripts/lumos:1752`
severity: minor
blocking: 否——都是實作細節缺口,不影響設計方向。

### F11 〈回退〉與〈實務隱患〉不可逆條:換身分字的回退方向沒檢查
- 引句:「兩句提醒的身分字換掉不影響既有放行」
- 問題:這句只證明往前換不失效。若修完後有人在考場或消費專案用新身分字(孤兒、還沒提交)放行了候選,〈回退〉第 3 項把身分字「改回原樣」會讓這些放行失效。
- 〈不可逆〉的排除理由只驗了單向。
- 佐證:file: `scripts/lumos:49658`(指紋含 `ident or reason`)
severity: minor
blocking: 否——只影響修後回退時重新放行一次,不影響安全性。

### F12 S6:人工驗收的判準與涵蓋對不上
- 引句:「回 mOrangePos 考場重跑結帳服務費完整流程的結果應符合 S1、S2、S4」
- 問題:
  - 同份設計說舊留痕在實作完成後重跑規格閘不會被重寫(`_spec_gate_low_not_red`)。照「修好後再跑一次規格閘」這步,驗到的是 S3 而不是 S2。
  - 步驟列沒有寫明哪一步產生新格式留痕,S2 與 S3 驗到哪個取決於從頭重跑還是沿用舊現場。
  - 考場是「只留本機」的分支,別人無法重現。通過判準只寫「結果寫進驗證紀錄」,沒有寫應看到的具體輸出。
  - `lumos loop escape --withdraw` 還需要 token 與 `--withdrawn-by`,步驟沒寫。
- 佐證:
  - file: `scripts/lumos:15167`(`_spec_gate_low_not_red`)
  - file: `scripts/lumos:19891`(`--withdraw` 的必填參數檢查)
severity: minor
blocking: 否——是驗收文字模糊,不影響程式修法。

## 逐節與固定席結論

### 逐節
- 名詞段:已讀,無 finding。
- 問題與最小解:已讀。缺口 1、2 的因果與引用我都核對成立:切參數在 48976 用原文、`names` 在 `_spec_gate_prepare` 丟平台、`_spec_gate_low_not_red` 條件。缺口 3 屬實,見 F2、F3、F9。
- 做法 1 到 4:見 F1、F5(1);F4、F6、F7、F8(2);F2、F3、F9、F10(3);F12(4)。
- 驗收條款:S1 到 S5 各自能對應一支測試,但覆蓋缺口見 F1、F2、F4、F5、F6。S6 見 F12。我確認 5 個 [test:] 名在 `scripts/test_lumos.py` 都還不存在,是待寫,不是撞名。
- 回退:見 F11。
- 實務隱患:
  - 排除的金流、對外送出、不可逆三條理由成立,不碰收費、不寄信。「不可逆」那條見 F11。
  - 守衛面、效能、相容三條已讀。相容條只談留痕的 tests 欄,漏了切法變更對 tq/ 候選的影響(F5)。
  - 併發:無,治理帳寫入沿用既有原子寫入,這次只加唯讀 git 查詢。
  - 資源:見 F10。
  - 回滾:見 F11。
- 審計修正紀錄:空節,已讀。

### 跨設定行為
- 單平台:S2、S3 不變(單平台時平台恆等於預設,無前綴)。S1 切法改變對所有設定生效(F5)。
- 多平台:行為改變就是 S2、S3 本身。風險見 F4、F7、F8。
- 治理帳本來就進版控:S4、S5 不觸發,現行訊息不變,我確認既有測試不受影響。
- 舊工具讀新格式:舊的推送前驗收本來就認 `平台:名字`,沒問題(F8 引用的證據)。
- `lands_in` 與程式檔的家:改動全在 `scripts/lumos`,四個節點各管一段,對得上。有一個既有矛盾:`Systems/規格閘` 的 responsibility 寫自己負責 `--push-check`,KEY 行卻寫那段的家在 `Systems/bound-tests-gate`。這是既有的,不是這份設計造成的,但落地時要選一篇寫。
- 其他讀者/手冊:`skills/lumos-project-notes/commands/06-代碼審與推送.md:15` 只講紅燈版沒提交就 `git add`,不說治理帳被忽略。這不構成說錯話,但設計沒列入同步清單。

### 固定席
派工尾端沒有附合約或事故節點,所以沒有逐條判的對象。

最嚴重 severity:major,blocking 共 4 條(F1、F2、F3、F4)。
