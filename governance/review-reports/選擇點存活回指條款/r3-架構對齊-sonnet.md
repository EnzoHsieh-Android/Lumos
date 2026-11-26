severity: major

**1. 分層與依賴方向**
大致對齊:`_KillPrep` 由 choice-kill 建、當選用參數交給 `cmd_guard_kill`,沒交時行為不變,形狀同 `_KillMerge`(`scripts/lumos:28975`、`scripts/lumos:28337`)。guard-kill 不反向呼叫 choice-kill 的函式,走的是注入物件這條線,跟 `_KillHooks` 一樣。讀端新增 `_choice_ledger_aux` 旁邊並列 `_choice_ledger_index`,也跟 `scripts/lumos:78787` 的分工一致。治理帳 (gate, kind) 白名單與 `LOOP_NOT_CLOSE_EVENTS` 的登記方式同 `scripts/lumos:21051`。有兩處對不齊:

severity: minor
blocking: 否
引句:「choice-kill 建、交給 `cmd_guard_kill` 新的選用參數 `prep`;guard-kill 在 `_kill_merge_iter` 先量齊基準的同一個位置呼叫它」
說明:這是兩個對不上的做法擠在同一個位置。`_kill_merge_iter` 只在 `merge` 有給時才走(`scripts/lumos:28479` 的 `mctx` 只在 `merge is not None` 時建),而且 `_kill_merge_ready` 判不能合併的平台組會直接 `yield from c.plist`(`scripts/lumos:29337`)。
- 計劃沒寫 `--no-merge`、不能合併的平台組、`LUMOS_SKIP_CHOICE_MERGE` 這三種情況下 `prep` 跑不跑。
- 第一個訊號的回呼也是掛在 `_KillMerge.on_signal` 上(`scripts/lumos:79295`),`prep` 沒有 `mg` 就沒有 `interrupted`,`_kill_run(merge=…)` 也用不了。
- 既有的做法是把新欄位加進 `_KillMerge`,計劃卻另開一個平行參數。
- 請計劃擇一:`prep` 掛在 `_KillMerge` 上,或明說跟 merge 無關、自己建 `mctx` 與訊號回呼。

severity: minor
blocking: 否
引句:「換掉的配方(新壞法,配方編號由 choice-kill 這邊的配方含 `new` 一起算,不跟舊的撞)與每個配方的測試子集」
說明:這是第一個會改變配方集合的注入物件。`_kill_merge_iter` 只重排、略過已知的 `plist`,`hk`、`finish`、`on_row` 都按那份清單算;候選換掉的壞法 `group`、`tests_sha`、列身分怎麼對回,計劃沒交代。這不算第二套做法,但需要在計劃裡寫明對回規則。⚠ 交編排者判。

**2. 命名與錯誤處理**
旗標 `--no-cov` 對 `--no-merge`、`--reach-only` 衝突給 rc2、事件 kind 用連字號(`cov-audit`、`reach-run`)、`reach_why` 用中文字串,都跟 `merge_why`、`merge_kind` 的慣例一致。平台鍵 `coverage`、`compile_cmd` 放在平台條目頂層,跟 `run_cmd` 同一層(`scripts/lumos:6409` 一帶),也一致。引句比對沿用 `_kt_sit_quote_norm`(`scripts/lumos:75356`),不另寫正規化。實字下限 10 與 `_KT_SIT_QUOTE_MIN` 同值(`scripts/lumos:75305`)。不一致的有一處:

severity: minor
blocking: 否
引句:「單筆事件超過 4096 位元組時照 `_gate_event_fit` 截 `reach_clauses`(`reach_more` 補數)」
說明:`_gate_event_fit` 截清單時自己會記 `<key>_truncated`(`scripts/lumos:1884`、`scripts/lumos:1908`)。計劃另有一套上限 20 加 `reach_more`,成了兩套截斷標記。請二選一,或寫明兩者並存的理由。

**3. 第二種做法**

severity: major
blocking: 是
引句:「結果(rc、尾段、秒數、逾時、不確定)直接寫進 guard-kill 的基準快取,鍵用 guard-kill 自己組的那條測試指令」
說明:計劃另寫了一個「單支基準迴圈」(覆蓋基準),跟既有的 `_kill_merge_singles`(`scripts/lumos:29158`)重複。
- 兩個迴圈的時間政策不同。既有的在每次量完後用實測平均重估剩餘時間,比剩下時限多就整組收手;不計第一支冷編譯;被時限截斷而逾時的那支不寫進基準。計劃的版本是「每支開跑前看 `--max-seconds` 剩下多少,不夠就停,沒跑到的算不明」。
- 超時的處置不同。既有的走 `_KillHalt` 或收手退回逐支;計劃的走「不明、續跑」。
- 訊號處理不同。既有的規定「單支基準與逐支流程照現在等那一支跑完」,計劃的覆蓋基準卻要求第一個訊號就當場收。
- 這個坑已有紀錄:`Systems/guard-kill` 的 PITFALL 寫過「量基準把總時限吃光、一個壞法都不判」,而且是代碼審 r1 到 r4 才收斂的。新迴圈沒有承接任何一條。
- 計劃自己說覆蓋基準「就是合併快篩本來要先量齊的那一輪」。對齊的做法是讓 `_kill_merge_singles` 帶一個可換的指令與 init script,而不是平行再寫一個迴圈。若確有理由不同,請把差異逐項寫進計劃。

severity: minor
blocking: 否
引句:「準備物件把這一批所有壞法同時套到樹上、跑一次編譯任務」
說明:既有套壞法是 `_kill_merge_apply` 一次一個壞法,含 `_kill_wait_new_second` 與 `mstate` 錯開,還原是 `_kill_merge_restore`(`scripts/lumos:29202`、`scripts/lumos:29068` 一帶)。
- 計劃只說「最後還原」,沒說沿用它們。
- 批次套多個壞法在既有函式上不能直接用,因為它們一次只處理一個。
- 若自寫一套,就是「另一套套壞法與還原」。請寫明是泛化既有兩個函式,還是自寫。

severity: minor
blocking: 否
引句:「寫進 `_note_audit_work_dir` 同一套工作目錄規則下的 `choice-cov/<at_sha>/`(符號連結拒用、自帶 `.gitignore`、14 天清檔)」
說明:`_note_audit_work_dir` 把路徑寫死成 `.lumos/note-audit`,只清頂層的 `*.md`,超過 14 天才刪(`scripts/lumos:56728`)。`choice-cov/<sha>/*.json`、`.exec`、`choice-layer/*.json` 在子資料夾裡、也不是 `.md`,「14 天清檔」對它們不成立。要嘛擴充那支函式(連同 `_note_audit_safe_dir`、`scripts/lumos:56689`),要嘛就是第二套清檔。請計劃明講是哪一種。

severity: minor
blocking: 否
引句:「每筆判讀全文存成 `governance/choice-layers/<內容雜湊>.json`」
說明:這是混合了兩種先例。
- blind-judge 明文「紀錄只有治理帳一份」、不寫標記檔(`scripts/lumos:76331`)。
- reread 只有檔、沒有帳上事件。
- 計劃是檔加帳上事件加雜湊指回,為什麼不走 blind-judge 的純帳,計劃沒寫(推測是 4096 位元組上限)。
- 檔名用內容雜湊,而 `_note_audit_write_verdict` 是 `<時間>-<uuid>.json` 加原子換名、`max_bytes`、讀端單份上限(`scripts/lumos:56689` 一帶,`_NOTE_REREAD_VERDICT_MAX`)。計劃沒說沿用,也沒給讀端單份上限。
- 請寫明沿用 `_note_audit_write_verdict`,或說明為何另寫。

分份方面:`choice-layer --template` 的份清單檔是「重算式」的 `code-loop blind-judge --part` 之外的另一種做法,但 note-audit 的清單檔已有先例,所以這條我判為對齊,不單獨列。

**4. 落點**

severity: minor
blocking: 否
引句:「參數:呼叫端交進準備物件,在建樹後、跑配方前呼叫,沒交時行為不變」
說明:既有慣例是 guard-kill 那棵樹裡的機制寫在 `Systems/guard-kill`:`_KillMerge`、`_kill_merge_iter`、scratch 初始化腳本、`on_first` 訊號,各有一條詳細 WHY(該篇第 55 到 68 行)。choice-kill 一側的記帳與判定寫在 `Systems/規格閘` 第 97、98 行一帶。
- 準備物件的合批編譯、逐測試覆蓋基準、續跑、斷路器都在 guard-kill 那棵樹裡做。
- 照既有切法,這些該以同樣深度寫進 guard-kill,而不是只補一句。
- 此外 guard-kill 沒寫負責範圍,計劃只補規格閘的 responsibility。
- 規格閘已有 232 行;判讀材料、判讀記錄、判讀有效性這一條線,最近的先例是筆記內容審、盲判各有自己的家。⚠ 交編排者判:是否另開一篇。

不對齊共 8 條,其中 major 1 條
