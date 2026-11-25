severity: minor

本份設計沒有引入第二種做法,也沒有跨層直呼。有四處跟鄰居不一致,都是 minor。

**1. 分層與依賴方向:對齊**
- 新機制全放在既有合併快篩那一串函式裡:`_KillMerge`(`scripts/lumos:28893`)、`_kill_merge_iter`(約 `:29160`)、`_kill_merge_breaker`(`:29095`)、`_kill_merge_screen`(`:29133`)。沒有新模組或新層。
- 呼叫方向沒變:`_kill_merge_iter` 呼叫 `_kill_merge_screen`,後者呼叫 `_kill_merge_breaker`。
- 第三段的試探快篩直接重用 `_kill_merge_screen`,沒另開一套。
- `whys` 寫在 `_kill_merge_screen` 的 classify 之後,跟 `mg.kinds[(c.plat, group)]`(`:29150` 附近)同一個位置、同一種鍵。
- 狀態仍由 `mg.plats[...]` 單一處記錄,恢復時改回 `(True, "")`,沒另存一份。
- 寫帳路徑沿用 `_ChoiceKillRun` 到 `_choice_event_extra`(`:78768`)。

**2. 命名與錯誤處理:大體對齊,有三條不對齊**
- (a) `trips` 是另存一份跳開次數,跟既有 `tripped` 重複。
  - 既有做法是狀態只存一處,其餘由它算出。`_KillMerge` docstring 寫「run 事件的 merge_off 由它算出,不另存一份」(`:28897`),`_CHOICE_MERGE_TRIPPED` 註解(`:28734`)也是這個意思。
  - 新設計讓 `tripped`(bool)和 `trips`(計數)並存,run 那筆也同時出 `merge_tripped` 和 `merge_trips`。
  - 欄名也很近。`merge_trips` 是字典、`merge_tripped` 是布林,讀帳的人容易混。
  - 引句:「run 那筆:`merge_tripped` 照舊是「這次跳開過」;另記 `merge_trips` {平台: 跳開次數}」
  - 對照:`scripts/lumos:28897`、`:79122`
severity: minor
  - blocking: 否
- (b) 試探間隔 10 沒有說放在哪。
  - 既有慣例是門檻用具名常數,例如 `_CHOICE_MERGE_BREAKER = 5`(`:28735`),再由 `_KillMerge.__init__(…, breaker=…)` 帶入(`:28904`)。
  - 計劃只在〈不做〉寫「試探間隔不給旗標」,沒寫成 `_CHOICE_MERGE_…` 常數,也沒寫要不要像 `breaker` 一樣當建構參數。
  - 引句:「不改斷路器門檻(5)、試探間隔不給旗標:沒有實測依據要調。」
  - 對照:`scripts/lumos:28735`
severity: minor
  - blocking: 否
- (c) 治理帳欄位的讀帳預設寫得比第二段少。
  - 第二段把新欄加進 `_gov_row` 的 choice-kill 或 run 子字典,並寫明缺欄讀法(`:18564`、`:18565`)。
  - 第三段只寫「治理帳欄位型別登記 `merge_why`、`merge_trips`、`merge_reopen` 是字典;`gov` 讀帳缺欄讀成空字典」。
  - 它沒說三欄各進哪個子字典:`merge_why` 屬於壞法那筆,該放 `ck`,跟 `merge_kind` 同層;`merge_trips`、`merge_reopen` 屬於 run 那筆。
  - 驗收條款 S4 的舊帳讀法只提 `merge_why`、`merge_reopen`,漏了 `merge_trips`。
  - 引句:「治理帳欄位型別登記 `merge_why`、`merge_trips`、`merge_reopen` 是字典;`gov` 讀帳缺欄讀成空字典。」
  - 對照:`scripts/lumos:18471`、`:18564`、`:18565`
severity: minor
  - blocking: 否
- 對齊的部分:
  - 欄位名 `cool`、`reopen`、`whys`、`merge_why`、`merge_reopen` 都是「平台為鍵的字典」,跟 `streak`、`unclean`、`kinds`、`merge_kind` 同形。
  - 印字前綴 `⚠ <平台>:` 跟 `:29107` 的跳開那行一致。
  - `_choice_event_extra` 加選用參數 `merge_why`,是現有 `merge_kind=None, single_runs=None` 的寫法(`:78768`)。
  - `cool` 是動詞縮寫,鄰居都是名詞(`streak`、`kinds`),這點只算風格,不列。
- 一個待交編排者確認的點(⚠):計劃寫「沒有就不帶這欄」(`merge_why`),但 `merge_kind` 是每個壞法都帶(缺的平台寫 `none`,`:79043`)。兩者缺值寫法不同,但跟 `aborted`、`judged` 的「有值才帶」寫法一致,我判不準算不算不一致。

**3. 第二種做法:沒有**
- 計數:`cool` 和 `reopen` 沿用 `streak` 的「平台為鍵的字典」做法,沒有另一套計數器。
- 印字:仍走 `print(..., file=sys.stderr)`,恢復那行由 `_kill_merge_breaker` 印。
- 常數:`_CHOICE_MERGE_*` 沒新增,但見 2(b)。
- 只有 2(a) 的 `trips` 接近「另存一份」,已列在第 2 問。

**4. 落點:不合理,偏窄**
- 第三段 `lands_in` 只寫 Systems/guard-kill,連 `merge_why`、`merge_reopen` 這類治理帳欄位都歸到那一篇。
- 第二段對同類欄位另外落在 Systems/規格閘,理由是那一篇管治理帳欄位:`lands_in` 列了 `Systems/規格閘`,〈落點〉寫「run 事件的 `merge_unclean`、`merge_off`;choice-kill 事件的 `merge_kind`、`single_runs`」。
- guard-kill 現況已有 166 行、6 行 KEY,還有 `merge_unclean`、`merge_off` 的鄰居條目。所以放進既有那篇是對的,不必另開;但治理帳欄位該跟第二段一樣補寫 規格閘。
- 第二段還列了「同一提交改的既有句子與測試」和被取代條款的〔已被…取代〕註記。
- 第三段的 WHY 自己寫了會改既有條款與測試:`t_choice_kill_merge_budget_edge` 和 `t_choice_kill_merge_budget_hint` 的期望值,以及第二段 S7 的估算口徑。但〈落點〉沒列這些,也沒有〈舊否決比對〉節。
- 引句:「- [[Systems/guard-kill]]:量基準估算、斷路器半開、結果檔拒收代碼、壞法那筆的 `merge_why` 與 run 那筆的 `merge_reopen`。」
- 對照:`Projects/選擇點變異加速第二段_計劃.md` 的 `lands_in`(第 10–12 行)與其〈落點〉節(約第 88–97 行)
severity: minor
- blocking: 否

不對齊共 4 條,其中 major 0 條
