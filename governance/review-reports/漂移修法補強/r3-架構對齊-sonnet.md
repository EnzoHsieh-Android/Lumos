severity: major

## 四問

**1 分層與依賴方向**:大致對齊。c4 證據頁(drift 區段)往下用 `_SET_COND_SLOT`(set 區段,定義在前)、`_nodehome_git`、`_plan_first_commit`,方向是 drift → set/git 工具,與現況一致(`_drift_c4_print` 已經用 `_SET_COND_SLOT`)。c1 往下呼叫 guard 區段的組字函式,也是既有方向(`_drift_fix_c1` 已呼叫 `_guard_pass_rewrite`)。刪除守衛(`cmd_delguard_check`)呼叫 `_VENDORED_ALL`、`_is_toolchain_repo`(工具自裝檔區段)是往共用小工具走,無跨層直呼。file: `scripts/lumos:27963`、`scripts/lumos:27834`、`scripts/lumos:17822`。唯一要注意:spec 沒寫新常數與新組字函式放哪一區段(見 F2、F3)。

**2 命名與錯誤處理**:大致對齊。c3 的 `--reason` 檢查照既有分工:長度與單行由通用的 `_drift_fix_args_err` 管(對所有 kind 一律套,理由非 None 才驗),佔位字由 kind 專屬函式管,與 c2 同形;`_drift_placeholder_err` 對 None 回 None(`text or ""`),c3 理由選填不會炸。`_drift_fix_c3_args` 回傳「錯誤字串或 None」跟 `_DRIFT_FIX_KIND_ARGS` 表一致。delguard 的 note 欄位用 `key=value` 空白分隔,與既有 `tokens= hits= secs= reason=` 一致。命名瑕疵見 F3(訊息字樣疊字)。file: `scripts/lumos:27689`、`scripts/lumos:27708`、`scripts/lumos:27714`、`scripts/lumos:27732`、`scripts/lumos:29406`。

**3 第二種做法**:有一處實質不對齊(F1:刪除守衛的「哪些是工具自裝檔」)與兩處輕微(F2 佔位字清單兩份、F3 c1 組字函式旁有既有的 settle 組字函式)。set 的佔位字常數:既有 `_SET_COND_SLOT` 在 set 區段(`scripts/lumos:14620`),`_DRIFT_PLACEHOLDER_RE` 在 drift 區段(`scripts/lumos:27619`)且已含 `sha|卷證`;spec 只說「一個模組常數」沒指定位置,也沒說跟後者的關係。c3 的接線(`_DRIFT_FIX_ALLOWED`、`_drift_fix_c3_args`、argparse)照既有形狀,沒有第二種做法。`_nodehome_git` + `_nodehome_split_z` 列提交檔案是既有寫法,沒問題(file: `scripts/lumos:23621`、`scripts/lumos:23634`)。

**4 落點**:lands_in 四篇(存量漂移守衛、lumos-cli-write、guard-kill、delguard)與改動區段對得上;程式都在 `scripts/lumos` 單檔,測試在 `scripts/test_lumos.py`,符合「單檔零依賴」家規,不引入新模組或新依賴。兩處要補的落點:新常數位置(F2)、`vendored-skip` 計數怎麼從 `_delguard_parse_diff` 帶到 `_delguard_log_result`(F4)。

## F1 刪除守衛用純路徑判斷,與四處既有「工具自裝檔」判斷不同口徑
severity: major
blocking: 是
引句:「純路徑判斷,不讀安裝清單、不跑 git,沒有額外時間。」
file: `scripts/lumos:17765`
file: `scripts/lumos:17833`
file: `scripts/lumos:18361`
file: `scripts/lumos:17758`
敘述:
1. 既有做法:消費專案裡「哪些是工具自裝檔」的判斷有兩支——`_vendored_state`(檔名在 `_VENDORED_ALL` 且內容指紋對得上安裝清單才算原封不動;清單不在就一支都不跳,寧可多掃)與包在它外面的 `_vendored_skip`(推送前分級 `scripts/lumos:21261`、代碼審鏡頭 `scripts/lumos:29863`)。技術棧掃描(`scripts/lumos:18361`)也是 `_is_toolchain_repo` 為假才用 `_vendored_state(root)[0]`。三個既有呼叫端全是「指紋對得上才跳、否則多掃」的同一個方向。
2. `_vendored_state` 的 docstring 明講為什麼不能只比檔名:「只比檔名的話,專案自己改了工具裝進來的檔、或把自己的程式放成工具的檔名,風險掃描就完全看不到」(2026-09-10 代碼審 r3 併發資源席的事故根因)。
3. spec 第 5 節在 delguard 直接拿 `_VENDORED_ALL`(只比路徑)當 `skip`,方向相反(漏掃/少提醒,不是多掃)。這就是「同一個問題(這支檔是不是工具裝的)第二種答法」。spec 的 PRIOR-ART 只說借 `_VENDORED_ALL` 與 `_is_toolchain_repo`,沒交代為什麼不直接借 `_vendored_skip`/`_vendored_state`,也沒有一條測試把「delguard 跟 `_vendored_skip` 口徑不同是故意的」釘住。
4. 有合理理由的部分(⚠ 是否足以豁免要人裁):delguard 看的是 staged diff、拆除工具鏈時整支被刪,`_vendored_skip` 需要 `diff_range` 且對起點版本會跑約 17 次 `git show`(有時間成本),spec 因此選擇純路徑。這個理由 spec 沒寫進文字;誠實界線只寫了「工具檔本來就不該在消費專案被改」,沒有承認它與 `_vendored_state` 的指紋口徑相反。
5. 建議方向(不是要求加回被拿掉的東西):要嘛在 spec 明寫「delguard 是有意跟 `_vendored_skip` 不同口徑,理由=advisory、時間上限、拆除場景」並加測試釘住;要嘛用 `_vendored_state(root)[0]`(工作目錄、不跑 git、只讀一個小 JSON)取代 `_VENDORED_ALL`,口徑就一致且仍無 git 成本。

## F2 佔位字清單再多一份,位置與既有正規式沒說清楚
severity: minor
blocking: 否
引句:「三個字串放一個模組常數,跟證據頁印的同一份」
file: `scripts/lumos:14620`
file: `scripts/lumos:27619`
敘述:
1. 既有兩份:`_SET_COND_SLOT`(單一字串,set 區段)與 `_DRIFT_PLACEHOLDER_RE`(`<為什麼…>`、`<sha>`、`<卷證>`,drift 區段,供 `--reason/--new` 用)。spec 新增的「三字串常數」跟後者在 `<sha>`、`<卷證>` 上重複,將來範本再加佔位字要改兩處。
2. spec 沒指定常數放哪。`_set_conditions_locked`(`scripts/lumos:15128`)在 drift 區段之前,常數必須定義在 set 區段(取代 `_SET_COND_SLOT` 位置)drift 才能引用;放 drift 區段會變成 set 往後依賴 drift。建議明寫「放在 `_SET_COND_SLOT` 原位、`_DRIFT_PLACEHOLDER_RE` 的 `sha|卷證` 由它組」或至少寫一句兩份的關係。
3. 沒有具體出錯場景(現在三字串都在,行為正確),所以只標 minor。

## F3 c1/settle 組字函式:既有 settle 已有單一出口,而且字樣會疊字
severity: minor
blocking: 否
引句:「改用同一支組字函式,字樣改成」
file: `scripts/lumos:12556`
file: `scripts/lumos:27839`
file: `scripts/lumos:12552`
file: `scripts/lumos:12014`
敘述:
1. settle 側其實已經有單一出口 `_guard_settle_missing_say`(兩個呼叫點 `scripts/lumos:12438`、`scripts/lumos:12572`);c1 側 `scripts/lumos:27839` 自己 `join` `_GUARD_PROSE_NAMES`。spec 說「新的一支組字函式」,沒說是擴充 `_guard_settle_missing_say` 還是另起一支。另起會變成三個地方各有一份組字邏輯。⚠ 建議:把 c1 與 settle 共用的字樣抽成 `_GUARD_PROSE_NAMES` 旁邊的單一函式,`_guard_settle_missing_say` 改呼叫它。
2. 字樣疊字:`_GUARD_PROSE_NAMES` 的值本身已含「預告句」或引號句(「摘要的 TEST 預告句」、「正文「為什麼還不做:」」),套 spec 的「找不到〈那一種〉的預告句」會變成「找不到摘要的 TEST 預告句的預告句」。實作時要嘛去掉「的預告句」,要嘛改 `_GUARD_PROSE_NAMES`。
3. `scripts/lumos:12014` 另有第三種措辭(「找不到預告行『…』(被手改過或已經轉正?)」,是 settle 找家節點預告行的 err 字串),spec 沒說它算不算「同一種訊息」;若不算,S3 的「兩處字樣相同」要限定範圍。

## F4 `vendored-skip=` 計數的傳遞路徑沒寫
severity: minor
blocking: 否
引句:「跳過時在既有 delguard 治理事件的 `note` 裡加 `vendored-skip=<這次 diff 碰到並跳過的工具檔支數>`」
file: `scripts/lumos:29222`
file: `scripts/lumos:29401`
file: `scripts/lumos:29494`
敘述:
1. `_delguard_parse_diff` 回傳 `{"tokens","vault_diffs"}`,既有測試都用 `["tokens"]` 取值(`scripts/test_lumos.py:19787` 等),加一個新鍵相容;但 spec 只說 `skip` 進、沒說「碰到幾支」怎麼出。`_delguard_log_result` 簽章固定(`gr, kind, n_tokens, hits, secs, reason`),note 是函式內組的字串,要加欄位就得加參數;spec 也沒提。
2. 記帳只發生在 `_delguard_log_result` 的 ok/部分結果路徑;超時、內部錯誤走 `_delguard_log_degraded`(`scripts/lumos:29411`),那兩條不會帶 `vendored-skip=`,而 RETIRE-IF 是靠 `grep 'vendored-skip='` 累計 ≥20 次,降級那幾次的跳過不會被算到。屬於量測口徑,不影響行為,標 minor。

## 審查完畢

不對齊共 4 條,其中 major 1 條
最高等級:major;blocking 共 1 條
