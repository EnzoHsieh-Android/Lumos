severity: major

# 代碼審修正關卡 設計審 r1:正確性-opus

席名:正確性-opus。鏡頭:正確性與邏輯。實驗都在自己的 clone(`fg-r1-work-正確性-opus/repo`,`git clone --shared`)裡做,主 repo 沒碰。

實驗場景(F1、F2 共用):在 clone 造兩個提交——base 加一支有 bug 的 `_fcdemo_norm(s): return s`;HEAD 把它修成 `s.strip()`、加 `_fcdemo_new()`,並在 `scripts/test_lumos.py` 加三支測試:`t_fcdemo`(弱測試,只驗 `norm("a")=="a"`,修前修後都過)、`t_fcdemo_strip`(真的守住修正)、`t_fcnew_only`(呼叫修前不存在的 `_fcdemo_new`)。照第 4 項字面寫一支模擬腳本(`fg-r1-work-正確性-opus/sim.py`):暫存資料夾、`git worktree add --detach` base、把 base..HEAD 改過且 `_nodehome_is_test` 認得的測試檔換成 HEAD 版、另開一個 HEAD 工作樹、`TMPDIR` 指到暫存資料夾、用設定裡的 `run_cmd` 逐支跑、拿 `_ran_count` / `_ran_evidence_check` 判,最後在 finally 裡收工作樹。輸出:

```
overlay M scripts/test_lumos.py
RED t_fcdemo: rc=1 ran_count=2 skipped=False evidence=True | lumos 測試(2 案例) /   ✗ FAILED t_fcdemo_strip(1 條斷言) / 1 passed, 1 failed
GREEN t_fcdemo: rc=0 ran_count=2 skipped=False evidence=True | lumos 測試(2 案例) / 2 passed, 0 failed
RED t_fcdemo_strip: rc=1 ran_count=1 skipped=False evidence=False | lumos 測試(1 案例) /   ✗ FAILED t_fcdemo_strip(1 條斷言) / 0 passed, 1 failed
GREEN t_fcdemo_strip: rc=0 ran_count=1 skipped=False evidence=True | lumos 測試(1 案例) / 1 passed, 0 failed
RED t_fcnew_only: rc=1 ran_count=1 skipped=False evidence=False | lumos 測試(1 案例) /   ✗ t_fcnew_only EXCEPTION: module '_lumos_inproc' has no attribute '_fcdemo_new' / 0 passed, 1 failed
GREEN t_fcnew_only: rc=0 ran_count=1 skipped=False evidence=True | lumos 測試(1 案例) / 1 passed, 0 failed
status same: True
```

主工作目錄的 `git status` 不變、`git worktree list` 沒有殘留——建樹、收樹的做法本身判得對。下面的發現都出在「怎麼判紅、判綠」。

## F1 先紅的判法不看是哪一支紅:子字串篩選多選到一支,弱測試就被判成「修之前是紅的」
severity: major
blocking: 是
引句:「非 0 結束,而且 `_ran_count` 讀得到跑了至少一支、沒有全被跳過 → 紅,過」
file: `scripts/test_lumos.py:31910`
file: `scripts/lumos:6588`
file: `scripts/lumos:14075`
file: `scripts/lumos:38498`

1. 本 repo 的 runner 篩選用子字串比對(`_args.keyword in t.__name__`)。pytest 的 `-k` 一樣是子字串,jest 的 `-t` 是正則。修正紀錄寫 `t_fcdemo`,實際會連 `t_fcdemo_strip` 一起跑。
2. 上面的實驗:`t_fcdemo` 修前修後都會過,完全沒守住修正;可是在 base 那邊,同時被選中的 `t_fcdemo_strip` 紅了,整次 rc=1,`_ran_count`=2,也沒有跳過。照條款字面這三個條件全中,判成「紅,過」;綠那邊 rc=0、看得到有跑過,判綠。結果這支弱測試通過了先紅後綠。這正是這一項要抓的「測試沒守住」,結果被放過了。
3. 同一個 repo 已經有兩個做對的前例,這份設計都沒有沿用:
   - 規格閘的 `_spec_gate_verdict`:`n >= 2` 而且宣告數不是 1 的時候判 weak(「篩選匹配到 N 支,測試名要唯一」),宣告數用 `_spec_gate_declared` 搭配放寬版的宣告集來數。
   - guard kill 用 `_kill_attribute` 去認紅燈是不是那支綁定測試的,認不出來就記 `killed_unattributed`,算弱證據。
   - 本計劃的 PRIOR-ART ③ 說要照 guard kill 的做法,實際只照了它建、收工作樹那一段。
4. 綠那邊有同一個洞。目標測試在 HEAD 被跳過、一條斷言都沒跑,但同名前綴的別支過了,輸出還是有 `N passed`,`_ran_evidence_check` 就判成跑過。兩邊加起來,只要測試名剛好是另一支新測試的前綴,整項就形同沒驗。
5. 還有一個分支沒定義:`_ran_count` 走 `count_re` 那條路時,skipped 的意思是「輸出裡有任何一支被跳過」,不是「全被跳過」。所以「非 0、支數 ≥1、skipped=True」(兩支被選中,一支紅、一支跳過)不屬於第 4 項四種情況的任何一種。
6. 改法:紅、綠兩邊都要先套 `_spec_gate_verdict` 的支數規則——選中 ≥2 支而宣告數不是 1 就不過,並寫明要換一個不會互為子字串的名字;能歸因的棧(本 repo 的 runner 每支紅都印 `✗ FAILED <名>` / `✗ <名> EXCEPTION`)再要求紅燈要歸因到那一支。另外要補一條 S4 的情境:「弱測試加上同前綴的真測試 → 回 1」。

## F2 「匯入就失敗會標看不出跑了幾支」對 python 棧不成立:兩種 runner 都讀得到支數,假紅不會帶標記
severity: major
blocking: 是
引句:「或要測的函式在修之前不存在而匯入就失敗、或選中 0 支)→ 算紅」
file: `scripts/lumos:38495`
file: `scripts/lumos:38498`
file: `scripts/test_lumos.py:31932`

1. 本 repo 的 runner:實驗裡的 `t_fcnew_only` 要測的函式在 base 不存在,結果 `_ran_count`=1,判成乾淨的紅,沒有標記。原因是測試透過 `_load_lumos_inproc()` 在執行時才取屬性,錯誤發生在跑測試的時候,不是匯入的時候;而 runner 先印「lumos 測試(1 案例)」,才跑那一支。
2. pytest(本機 CommandLineTools python3,pytest 8.4.2)實測:`tests/test_x.py` 開頭寫 `from mod import norm, new_helper`,`new_helper` 在 base 不存在,`test_plain` 完全不碰修正。`pytest tests -k test_plain` 回 rc=2,輸出 `collected 0 items / 1 error`、`Interrupted: 1 error during collection`、`1 error in 0.10s`。`_ran_count('python', 輸出)` 回 `(3, False)`:`_PYTEST_SUMMARY_RE` 把三處 `1 error` 加總了。照條款判成「讀得到跑了至少一支 → 紅,過」,也不帶「看不出跑了幾支」的標記。
3. 後果:python 專案的修補很常「新加一支輔助函式,測試檔開頭匯入它」。這時同一個測試檔裡每一支測試(包括完全沒守住修正的那幾支)在 base 都是乾淨的紅,而且不會有標記。〈實務隱患〉講的「在輸出看得到,由人判斷是不是假紅」,在 python 這棧剛好不成立。
4. S4 寫「匯入就失敗時應算紅並標看不出跑了幾支」。真實的 python runner 不會走到那條路,所以這條條款的測試只能拿一個什麼都不印的假 runner 來寫——條款綠了,可是在真實輸入上那條行為是錯的。
5. 改法:pytest 輸出裡有 `error during collection` / `errors?` 而且沒有 passed 也沒有 failed,就歸成「看不出」(或直接不過);本 repo 的 runner 照 F1 要求歸因到目標測試的 `FAILED` / `EXCEPTION` 行。S4 的「匯入失敗」情境改用真的 pytest 收集錯誤、或本 repo 的 runner 輸出來釘。

## F3 每條折入的發現都得有先紅後綠的測試;改文件、改流程那類折入一定過不了
severity: major
blocking: 是
引句:「每組至少一條 `fixed` 路徑;每條 `fixed` 至少一支測試」
file: `scripts/lumos:8652`

1. 第 1 項要求「這輪折入的每個發現都落在某一組」,每組至少一條 `fixed`,每條 `fixed` 至少一支測試,而且那支測試在第 4 項必須在 base 紅、在 HEAD 綠。沒有任何豁免。
2. 審查帳實際統計(clone 的 `docs/.canary-log.jsonl`,`code-` 開頭、帶 `finding_kinds` 的載體席共 240 筆):折入的發現裡 code 1748 條、spec 72 條、process 50 條;**48 輪(20%)至少折入一條非程式的發現**——像是註解或手冊寫錯、計劃筆記漏一段、留痕格式。
3. 這類修正通常寫不出「修之前紅、修之後綠」的測試。`at` 也要「函式名在那支檔裡整字找得到」,Markdown 檔沒有函式。照字面,這兩成的輪次修得完全正確,`fix-check` 還是回 1,而且同一個缺陷每輪都會重來。這會直接推高 RETIRE-IF 的「跳過比例超過三成」。
4. 根因類別固定清單裡也沒有「文件/流程」這一類。
5. 改法:路徑狀態加第三種,例如 `doc-only`,要求寫理由、不要求測試;或者載體席 `finding_kinds` 標成 spec/process 的發現免掉測試要求。要配一支條款測試:折入一條 `finding_kind=process` 的發現,紀錄寫 `doc-only` 加理由 → 這項過。

## F4 受波及合約測試這一項沒有過濾探針的退路:沒實測過輸出樣式的六種棧,一支都沒跑也判綠
severity: major
blocking: 是
引句:「判法:`green` 過;`red`、`unproven`(回成功但看不出跑過)、`no-cmd`、懸空、只在文字裡出現的都不過」
file: `scripts/lumos:38665`
file: `scripts/lumos:38840`
file: `scripts/lumos:38467`

1. `_run_bound_tests` 只在 `_ran_evidence_check` 回 False 時判 `unproven`。profile 沒實測過的時候它回 `(None, "")`,這時 rc=0 就直接判 `green`。
2. `_RAN_EVIDENCE` 只有 swift-xctest / csharp-xunit / node-jest / python 四種;TEST_PROFILES 另外還有 dart、java-junit、kotlin-junit、maestro、node-vitest、playwright 六種沒有。
3. 推送前的合約測試閘(`_bound_tests_check`)在 `_run_bound_tests` 之後,會對這六種棧補跑 `_bound_tests_filter_probe`,不可信就判 `unfilterable`,不報綠。第 5 項只寫「用 `_run_bound_tests` 真跑」、「`green` 過」,沒有這一步。
4. 結果:kotlin 專案的過濾條件對不到任何測試(跑 0 支、回 0)時,推送前閘說「證不出測試真的跑過」,`fix-check` 第 5 項卻說「全綠」。兩道閘對同一批測試給出相反的結論,而且放水的是這一道。第 4 項綠那邊有寫退回過濾探針,第 5 項漏了,前後不一致。
5. 改法:第 5 項照抄 `_bound_tests_check` 的探針那段(先別呼叫 `_bound_tests_check` 本身,它會另外寫 `bound-tests` 治理事件,把推送前閘的統計弄亂);補一支條款測試:profile 是 kotlin-junit、run_cmd 對任何名字都回 0 → 這項不過。

## F5 照字面把 `tests` 補進 `_GOV_FIELD_TYPES`,gov 會靜默丟掉 81 筆既有審查帳
severity: major
blocking: 是
引句:「`_GOV_FIELD_TYPES` 同步補上新欄位的型別」
file: `scripts/lumos:7577`

1. `_GOV_FIELD_TYPES` 是七本帳共用的一張表(那段註解寫明「同名欄位在各帳的意思與型別一樣」),`load()` 對每一本帳的每一行都套 `_gov_event_types_ok`,型別不對整行跳過。
2. 這份設計把 `tests` 定成「測試支數」,是整數。可是審查帳裡已經有 81 筆規格閘留痕(`kind: spec-gate`)帶 `tests` 欄,型別是測試名清單,例如 `{'loop': '雙向門放行', 'kind': 'spec-gate', 'tests': ['t_doctor_escape_by_door', …]}`。
3. 實測(clone 裡把模組載進來改表):審查帳 2603 行裡通過型別檢查的,從 2603 掉到 2522,少了 81 行。`lumos gov` 跟 `gov --stats` 會靜默少讀這些審查帳列,沒有任何提示。
4. 改法:新欄位取一個不跟既有欄位撞名的名字,例如 `fix_tests` / `fix_groups`;或者把 `tests` 型別寫成 `(int, list)`。要配一支測試:gov 讀到帶 `tests` 清單的 spec-gate 列,筆數不變。另外查過:現有治理帳裡沒有任何一行帶最上層的 `token` 欄,所以把 `token` 加進去重鍵不會動到既有統計。

## F6 `loop next` 的提醒不看提交:通過之後再改程式,提醒就不會再出現,到頂那條路也被舊的通過紀錄滿足
severity: major
blocking: 是
引句:「最後一輪的修補沒有下一輪審查會看到,推之前跑一次修正關卡是唯一的機械檢查」
file: `scripts/lumos:1172`

1. 提醒的比對鍵只有迴圈、輪次、`record_sha256`、kind `passed`。`_gate_event_build` 每一筆事件都會自動寫 `head_sha`,但這份設計的比對沒用它。
2. 情境:第 3 輪(到頂)在提交 A 上 `fix-check` 過了;編排者接著又改了一次程式(提交 B,例如順手再修一處,或修補時打錯),修正紀錄沒動。`loop next` 判 cap-reached,找到同輪、同 sha256 的 `passed` 事件,就不印提醒。提交 B 從頭到尾沒被修正關卡驗過,而設計自己說這一步是推之前「唯一的機械檢查」。
3. 〈跟提案不同〉說「`fix-check` 驗的就是跑的當下那個提交,治理帳記它」——帳上確實記了,讀端卻不比。日後轉成擋的 `fix-check-pending` 也用同一個條件,到時候就是放錯。
4. 改法:比對再加一條——事件的 `head_sha` 等於現在的 HEAD,或者 `head_sha..HEAD` 只改到 `governance/`、筆記、帳本(沿用先決條件那套程式檔、測試檔的判法)。S8 加一個情境:通過之後再提交一次程式改動 → 照樣印提醒。

## F7 帶了 `--record <其他檔>` 的輪,第 2 項找不到前一輪,`loop next` 也一直誤報
severity: major
blocking: 是
引句:「審查帳上這一輪的前一輪(照帳上輪次出現的順序)有修正紀錄」
file: `scripts/lumos:11090`

1. 修正紀錄可以用 `--record` 放在任何地方(只有不帶的時候才讀 `governance/review-reports/<迴圈>/<輪>-fix.json`)。第 2 項卻沒說「前一輪的修正紀錄」去哪裡找;治理帳只記 `record_sha256`,沒記路徑,實作的人只能去讀預設位置。
2. 放水的情境:r1 用 `--record /tmp/r1.json` 跑(類別 `escaping`);r2 又是一組 `escaping`,收了 major,沒寫 `prior`。第 2 項去讀 `r1-fix.json`,不存在 → 判「前一輪沒有修正紀錄」→ 不要求 `prior` → 過。同類連兩輪的規則被一個合法的旗標靜默繞掉。
3. 誤擋/誤報的情境:同一個 r1,`fix-check --record /tmp/r1.json` 通過了。`loop next` 沒有 `--record`,只能去讀預設位置 → 檔不存在 → 照「修正紀錄檔不存在也印」持續提醒要先寫紀錄,其實已經寫了也過了。
4. 改法:擇一——拿掉 `--record`,一律放預設位置;或者治理帳事件多記 `record_path`,第 2 項與提醒都用事件裡的路徑找,而且第 2 項找不到前一輪紀錄、但前一輪有折入時,判不過或至少印出來,不要當成「沒有」。

## F8 個別嚴重度缺值一律當 major,沒看輪級 severity;整輪都是 minor 也被要求寫 `prior`,跟 S6 打架
severity: major
blocking: 是
引句:「沒記個別嚴重度就當 major 算,寧嚴」
file: `scripts/lumos:8681`

1. `--finding-severity` 是選填,但寫側要求「要嘛每條都標、要嘛都不標」(`set(sevs) != F` 回 2)。所以沒有個別嚴重度的輪,整輪都沒有;不過載體席一定有輪級的 `severity`,而它是那一輪的最高值。
2. 輪級 severity=minor,就代表每一條發現都 ≤ minor。這時「當 major 算」不是寧嚴,是跟帳上已有的事實矛盾。S6 自己寫「同類但收的全是 minor 時不要求」,同一個情境下兩條規則判法相反。
3. 帳上統計:code 迴圈的載體席 315 筆,只有 66 筆帶個別嚴重度;輪級是 minor/clean、有折入、又沒有個別嚴重度的有 36 筆。這些輪碰到同類連兩輪會被判回 1(擋錯)。
4. 改法:缺個別嚴重度時退回輪級 severity——輪級 ≥ major 才要求 `prior`,輪級 minor/clean 不要求;S6 加這個情境。

## F9 隔離工作樹裡沒有不進版控的相依目錄,需要 node_modules / .venv 的棧綠那邊一定失敗
severity: major
blocking: 是
引句:「開兩個隔離工作樹(建法照 guard kill:暫存資料夾 + `git worktree add --detach <路徑> <版本>`」
file: `scripts/lumos:23590`

1. `git worktree add` 只檢出受版控的檔。jest / vitest 要 `node_modules`,run_cmd 寫 `.venv/bin/pytest` 的 python 專案要 `.venv`,這些都不進版控。
2. 這時紅那邊跑不起來,算成「看不出跑了幾支 → 算紅」;綠那邊也跑不起來 → 不過。這類專案不管修正對不對,第 4 項永遠回 1。修正明明對,卻一律判不過。
3. 同一個 repo 已經碰過這件事:新增告警閘的快照用 `_LINT_DEP_DIRS = ("node_modules", ".venv", "venv")`,用連結指回真的專案,註解寫「2026-09-13 真專案實測」。guard kill 沒做,但它在 baseline 紅的時候會判 `abort`,看得出是環境問題;修正關卡的紅那邊沒有 baseline,環境壞掉看起來就像修之前是紅的。
4. 未實測,依據是讀碼(本機沒有 jest 專案)。⚠ 這份設計會不會在第一個 node 消費專案上用,交編排者判斷;要是會,建樹後要照 `_LINT_DEP_DIRS` 補連結,或在〈實務隱患〉明寫這一棧不支援。

## F10 條款釘不住幾條關鍵的分支:拿掉實作,條款測試照樣綠
severity: major
blocking: 是
引句:「在現在的提交失敗時應回 1;跑完主工作目錄的 `git status` 跟跑之前一樣」
file: `scripts/lumos:38524`

1. S4 只寫到「在現在的提交失敗時應回 1」。第 4 項綠那邊的「0 結束、但 `_ran_evidence_check` 認不出跑過 → 不過」(例如目標測試在 HEAD 被跳過)沒有條款。實作漏掉這個檢查,S4 照樣綠。
2. F1 的「選中多支」、紅那邊「逾時 → 不過」、「`run_cmd` 沒有 `{method}` → 這支判不過」、疊回測試檔時「現在已刪掉的就刪掉」,都沒有條款釘住。
3. S8 只說「沒有同輪同 sha256 的 passed 事件時應印」、「有 passed 事件時不印」。條款寫法不逼測試放一筆「sha256 不同的 passed 事件」或「kind failed 的事件」——實作只看「有沒有 fix-check 事件」也會通過 S8。sha256 那條比對正是〈實務隱患〉講的「紀錄改過就要重跑」。
4. S5 只釘紅的那條路。第 5 項的 `unproven` / `no-cmd` / `diff-unavailable` / `no-config` 判不過、`no-pins` / `no-bound` / `no-vault` 判過,都沒有條款;把 `no-pins` 誤寫成不過,所有沒有合約的專案每次都回 1,也沒有一條條款會紅。
5. 先決條件裡的「迴圈編號不是 `code-` 開頭 → 回 2」與「紀錄不是合法 JSON → 回 2」,S2 沒涵蓋。
6. 改法:S4 拆成紅、綠兩條,各把上面的分支寫成情境;S8 加「sha256 不同的 passed」與「failed」兩個仍要印的情境;S5 補 unproven 不過、no-pins 過;S2 補非 code 迴圈與壞 JSON。

## F11 沒帶輪次的代碼審(standard 循序、light)沒辦法定址
severity: minor
blocking: 否
引句:「`<輪>` 是審查帳上那一輪的 `round` 字串」
file: `scripts/lumos:11597`
file: `scripts/lumos:11609`

1. `loop next` 認得兩種不帶 `round` 的代碼審:standard 循序(`seq`)與 light(帶了 `--round` 反而 rc2)。帳上最近一個不帶輪次的代碼審是 2026-09-29(`code-最低python版本改3-14-ci修正`);還有 1 個不帶輪次、但帶了 `--findings-set` 的代碼審迴圈(`code-兩席相反時端出張力`)。
2. 這類迴圈的 `--round` 沒有值可填,先決條件「找得到這一輪的載體席」永遠回 2;提醒要比對的「同一輪」也沒有定義,實作的人只能自己猜。要寫明:「只對帶輪次的代碼審」,或者「不帶輪次時用第幾筆」。

## F12 第 5 項在主工作目錄跑,會吃到別的會談留下的未追蹤檔,跟先決條件的理由自相矛盾
severity: minor
blocking: 否
引句:「未追蹤的檔不看(同一個 repo 常有別的會談留下的未追蹤檔」
file: `scripts/lumos:38606`

1. 先決條件不看未追蹤檔,理由是同一個 repo 常有別的會談留下的未追蹤檔。可是第 5 項在主工作目錄真跑,pytest 這類「收集整個目錄」的 runner 會把別的會談未追蹤的 `tests/test_wip.py` 一起收集;子字串一對上,或匯入失敗,第 5 項就判紅。這是擋錯的方向。
2. 第 3 項「測試索引掃的是工作目錄……等於現在的提交」,對未追蹤的測試檔也不成立(索引會掃到它);只是第 4 項綠那邊用乾淨的工作樹會攔下來,所以不放水,但那句敘述是錯的。
3. 改法:第 5 項也在第 4 項那個 HEAD 工作樹裡跑(`_run_bound_tests` 的平台根換成工作樹 + 相對路徑),順便讓「跑的就是現在的提交」真的成立。

## F13 base 不是祖先的時候,`base..現在` 會把主線的改動一起算進來
severity: minor
blocking: 否
引句:「範圍 `base..現在`,兩個端點比對,不要求祖先關係」
file: `scripts/lumos:38720`

1. 情境:分支在修正之後 rebase 到比較新的 main。兩個端點直接比對的話,main 那段時間的所有改動都會被算成這次的差異(`_bound_tests_range` 的註解就記過同一件事:「主線獨有的改動會被反向算進這次推送」)。
2. 對第 5 項來說,多算進來的合約測試是在 HEAD 跑的,紅了就是 HEAD 真的壞了,不會放錯;但會多跑很多測試,紅的時候也會怪到這次修正頭上。對第 4 項來說,疊回 base 的測試檔會帶進 main 新加、引用 main 新程式的測試,假紅變多,而且照 F2 不會帶標記。第 2 步殺傷力重跑也會跑到主線改到的配方。
3. 〈實務隱患〉要補一句這個代價;或者 base 不是祖先時印一行「範圍包含了 rebase 帶進來的主線改動」。

## 實務隱患鏡頭
- 時間:F1 修法要多數一次宣告(讀一次測試索引,幾乎不花時間)。另外,本 repo 每跑一次 `-k` 都要匯入六萬行的測試檔,實驗裡三支測試、兩邊各跑一次,總共約一分鐘,跟〈實務隱患〉的估計一致。無 finding。
- 隔離與清理:實驗確認照 guard kill 的做法建樹、收樹(`worktree remove --force` + prune)後,主工作目錄的 `git status` 不變、沒有殘留的工作樹;本 repo 的 runner 紅的時候,現場留在 `TMPDIR` 底下,設計把 `TMPDIR` 指到自己的暫存資料夾是對的。無 finding。
- 相依環境:見 F9。
- 帳本相容:見 F5。去重鍵加 `token` 對既有的帳沒有影響(查過:治理帳裡沒有任何一行帶最上層的 `token`)。
- 金流、對外送出:無,理由同快照〈已排除〉。

## 各節核對
- 〈名詞〉:已讀,無 finding(載體席「一輪只准一筆」:帳上有 2 個舊迴圈同一輪有兩筆載體席,都是處置閘之前的舊帳,不影響新迴圈)。
- 〈範圍〉:已讀,無 finding。
- 〈修正紀錄〉:見 F3、F11。
- 〈fix-check〉先決條件:見 F10 第 5 點、F12;逐項驗:見 F1、F2、F3、F4、F7、F8、F9、F13;記帳:見 F5。
- 〈loop next 的提醒〉:見 F6、F7、F10 第 3 點。
- 〈canary record --regression-set〉:已讀,無 finding(對照了 `cmd_canary` 那串「要跟 `--findings-set` 一起給」的檢查,加進去的位置正確)。
- 〈第 2 步〉:已讀;S11 沒有釘 `drifted` / `error` / `abort` 判不過、`killed_unattributed` 不算不過(跟 F10 同一型,第 2 步審查時一起補)。
- 〈上線〉〈跟提案不同〉〈回退〉:已讀,無 finding。

最高等級:major,blocking 共 10 條
