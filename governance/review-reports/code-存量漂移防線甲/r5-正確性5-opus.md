severity: major

# 第 5 輪 正確性席(opus)

範圍:只看第 4 輪修正差異(r5-snapshot.patch)。相關測試子集在 clone 上全綠:t_drift_code_review_r4(11)、r3(14)、t_doctor_drift_section、t_guard_settle(28)、t_doctor_summary_admits_soft、t_drift_exam_scores、t_note_audit(167)。

## F1 嚴格路只把「歷史各版」解不開算判不了,起點那一版解不開照樣當成沒有狀態,轉正事件漏掉、c1 整筆消失

severity: major
blocking: 是 — 同一族(嚴格時讀不出來要算判不了)這輪宣稱補齊,卻留了一個洞,block 模式可端到端放行
引句:「if strict and any(b is not None and not _utf8_ok(b) for b in blobs):」
file: `scripts/lumos:24586`
file: `scripts/lumos:24634`
file: `scripts/lumos:25556`

1. 這輪只在 _note_history_states 對「範圍裡各提交的那一版」檢查 UTF-8;起點那一版由 _note_base_status 讀,最後一行照舊是 `_note_audit_status_of(bb[0])[1]`,不是 UTF-8 時回 status=None,嚴格也不回 None。
2. 情境:起點提交裡守衛紀錄 G 是 pending、正文夾一個非 UTF-8 位元組(例如被 Big5 編輯器存過);範圍裡一個提交把編碼修好、同時把 status 改成 pass(舊版 settle 的轉正),預告句照留。序列變成 [None, 'pass'],flip 要 pending→pass,判成沒有轉正;_drift_check_core 對 c1 只收 `p in ev["passed"]`,其他 c1 直接 continue——不擋、也不列、也不進「判不了」。頂端那一版是 UTF-8,所以 tenv 的讀不出清單也抓不到。
3. 重現(端到端,block 模式):`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r5c/e2e_base_undecodable.py` → `rc = 0`、無任何輸出;對照組只拿掉那個位元組 `python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r5c/e2e_control.py` → `rc = 1`、列出 4 筆 c1。
4. 單元層重現:`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r5c/base_undecodable.py` → `seq(strict) = [None, 'pass']`、`passed(strict) = []`(期望兩者都是 None)。
5. 同一族的第三個位置(起點)沒掃到;_note_status_seq 的 docstring「歷史裡有一版解不開也回 None」與計劃「讀不到算判不了」都沒涵蓋起點版。修法只需在 _note_base_status 的 strict 分支對 bb[0] 做同一個 _utf8_ok 檢查,並補一條「起點解不開」的回歸釘。

## F2 settle 改成只認完全相同的測試名後,家筆記已是帶平台前綴的正式行時,settle 擋下的訊息說「綁的測試裡沒有」,照它指的 bind 走會原地打轉

severity: minor
blocking: 否 — 方向是擋(不會寫錯),只在多平台專案加手動轉正時卡住
引句:「if (bool(refs) if method is None else method in refs):」
file: `scripts/lumos:11826`
file: `scripts/lumos:12011`

1. 家筆記:`KEY:★INVARIANT★ 大額退費要人工核可 [test:ios:t_refund]`(手動換成正式行、用 `lumos guard bind … --platform ios` 綁的長相),守衛紀錄還是 pending。c5 會指示「重跑 lumos guard settle 補完」。
2. `lumos guard settle <G> --test t_refund` → rc 2「已經有同一句的正式合約行、綁的測試裡沒有 t_refund;要加這支用 lumos guard bind」;照做 `lumos guard bind Systems/Pay 大額退費要人工核可 t_refund --platform ios` → 「已綁 [test:ios:t_refund],無需重綁」;再 settle → 同一句擋下。settle 本身沒有 --platform 參數,能走出去的只剩綁一支不帶平台的 t_refund(多平台下歸預設平台,正是「不猜」想避免的綁錯平台)或手改狀態(樣板寫明不要手改)。
3. 重現:`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r5c/settle_prefixed.py` 三行輸出 rc 2 / rc 0 已綁 / rc 2。
4. r4 之前的 endswith 比對會讓這個情境走「只補守衛紀錄」。「不猜」本身沒錯,錯的是訊息把「綁了但帶平台前綴」說成「沒有」、並指到一條走不出去的路;至少擋下訊息要分出「有帶平台前綴的同名綁定」這一種。

## F3 doctor 的開關提醒:設定檔寫壞、或 gate 寫成 null 時說「沒寫設定」;gate 拼錯時說來源是 drift_check.gate,與 docstring「寫壞了也算寫了」不一致

severity: minor
blocking: 否 — 只是提醒行的說明錯,判定用的 mode 對
引句:「src = "(.lumos/config.json 的 drift_check.gate)" if explicit else "(沒寫設定,這是預設值)"」
file: `scripts/lumos:25855`
file: `scripts/lumos:25685`

1. 已接線(推送前掛鉤有 `# lumos drift check`)、`.lumos/config.json` 是 `{"drift_check": {"gate": "block"},}`(多一個逗號):doctor 印「存量漂移檢查是 warn(沒寫設定,這是預設值)」,同一次 doctor 別段卻說 config.json 讀不了(JSONDecodeError)——使用者明明寫了 block。
2. `{"drift_check": {"gate": null}}` 或 `{"drift_check": {}}`:_drift_config 走 `if g is None` 回 explicit=False,已接線時同樣印「沒寫設定」;沒接線時整行不印。docstring 寫「專案有沒有自己寫 drift_check(寫壞了也算寫了)」,這兩種都寫了 drift_check 卻算沒寫。
3. `{"drift_check": {"gate": "blokc"}}`:印「是 warn(.lumos/config.json 的 drift_check.gate)」,讀起來像設定檔寫的是 warn;_drift_config 回的警告 `_w` 在 doctor 被丟掉,看不到「你寫的是 'blokc'」。
4. 重現:`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r5c/doctor_msg.py`,三個情境各印出上述那一行。

## F4 考試重放碰到讀不出來的計劃靜默跳過,這題被記成「漏」而不是「略過」

severity: minor
blocking: 否 — 只影響考試計分的歸類,方向是保守(多算漏)
引句:「if txt is not None:          # 讀不出來的計劃(不是 UTF-8)沒辦法在記憶體裡改狀態,跳過(代碼審 r4 正確性席)」
file: `scripts/lumos:25927`

1. status_replay 題的 status_targets 指到上一版樹裡不是 UTF-8 的計劃:_drift_exam_replay 跳過它、回空集合,_drift_exam_one 把這題判成「漏」。同一函式裡 git 讀不出上一版時卻回「略過:git 讀不出上一版」——兩種「讀不出來」歸類不一致,而且考試輸出看不出有跳過。
2. 重現:`python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/r5c/exam_skip.py` → `('漏', 0, 0, 0)`;同一題改成樹讀不出 → `('略過:git 讀不出上一版', 0, 0, 0)`。
3. 考試結果是「預設改 block 要三條全過」的依據(Systems/存量漂移守衛 的 RULE 行),漏被多算會讓人去查一個不存在的機制缺口;這種題應回「略過:計劃讀不出來」並計入略過數。

## 其他重點看過的地方

- _note_flipped_one 三值:不嚴格時頂端讀不到、歷史 git log 失敗都回 False、只丟那一篇(①釘對);嚴格時頂端讀不到回 None(⑦釘對)。不嚴格的呼叫端(筆記內容審)不帶 deadline,`None if strict else False` 不會把逾時吞成 False。已看,無 finding(起點版見 F1)。
- _note_history_states:批次讀失敗、歷史某版非 UTF-8 的嚴格判不了正確;blob 為 None(該提交刪了檔)不算解不開,合理。已看,無 finding。
- _drift_config 三值回傳:scripts/lumos 內兩個呼叫端(25719、25848)都改成三元拆包;測試裡沒有二元拆包的舊呼叫;_drift_gate_explicit 已刪、無殘留引用。已看,無 finding(說明文字見 F3)。
- _drift_tree_env 改 deadline:所有呼叫端(check 傳 deadline、scan/exam 不傳=60 秒)與測試替身(50700 行吃 **k 或 timeout 預設)都相容。已看,無 finding。
- settle 各分支:method 受 IDENT_RE 限制,settle 自己寫的 `[test:{method}]` 與 bind 不帶平台時寫的名字都能完全相同地認回;有同句正式行但不含這支→擋、預告行重複→擋、只剩正式行→只補紀錄,t_guard_settle 28 筆全綠。已看,只有 F2。
- c3 空連結:我把那個條件從副本拿掉跑⑥的現場,c3 會被列出(翻紅成立),不帶空連結的前置情境照列 c3。已看,無 finding。

## 圖譜鏡頭(LUMOS-IMPACT 85d5fada..eec46033)

- Systems/存量漂移守衛:新寫的 WHY 行(不嚴格只丟一篇)與程式一致;但 PITFALL/WHY 描述的「嚴格讀不到算判不了」在起點版不成立,見 F1。
- Projects/存量漂移防線_計劃:[S14] 與〈做法〉第 0 節的新條件跟 _drift_gate_doctor_lines 一致;「專案自己寫了開關」的判法在壞 JSON / null 的邊界上與說明文字對不上,見 F3。
- Systems/guard-kill:合約是 guard kill 的 rc 與 JSON 純度,這份 diff 沒動 guard kill;settle 的比對變嚴會在多平台情境卡住,見 F2,不破壞它的合約。
- Systems/bound-tests-gate:它說 ★INVARIANT★ 的 [test:] 用 resolve_test_refs 解平台前綴;這輪 settle 改成不猜平台與它一致,不影響。
- Systems/測試假綠形態:要求還原翻紅釘有現場;r4 釘的①⑤⑦⑧我逐條推過還原後會翻紅,⑥實際拿掉修法跑過翻紅,不破壞。
- Systems/lumos-cli-read(d1 讀指令不寫帳):diff 沒在 scan/doctor 加寫帳,不影響。
- Systems/筆記內容審:共用段只在不嚴格路把「一篇讀失敗整道放行」改成「只丟那一篇」,更貼近它的宣稱,不破壞。
- 其餘固定席(lumos-cli-lifecycle、授權與歸屬、design-loop、pitfalls-code-loop、loop-convergence-recording、節點範圍與索引守衛、lumos-deinit、check-r-guard、reversibility-governance-ledger、cochange-guard、check-t-sentinel、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim-*、雙向門放行、規格落成可驗收條件、逃逸自動記、core-invariant-baseline、judge-severity-gate):diff 只動 guard settle、存量漂移與筆記內容審共用段的函式,沒碰到這些節點管的程式路徑,不影響。

總結:最嚴重是 major,blocking 共 1 條(F1),另有 3 條 minor。
