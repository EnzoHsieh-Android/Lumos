severity: minor

# 設計審 r1 架構對齊-sonnet 席

## 四問

**問 1 分層與依賴方向:對齊。**
- `_conditions_rewrite` 放在 `_set_conditions_locked` 旁(cli-write 那一帶):drift 區段在檔的後面,呼叫前面的 set 函式,方向是 drift 往下呼叫,跟既有的「drift 往下呼叫 guard、guard 不呼叫 drift」一致。
  - file: `scripts/lumos:15128`(`_set_conditions_locked`)、`scripts/lumos:27834`(`_drift_fix_c1` 呼叫 `_guard_pass_rewrite`,註解 `scripts/lumos:12274` 寫明方向)
  - set 區已有 `_SET_COND_SLOT`(`scripts/lumos:14620`)這個為 drift 證據頁而設的常數,但只是字串常數、不是呼叫;新函式只要不 import 或呼叫任何 `_drift_*` 就不破壞方向。
- `_guard_prose_settled` 放 guard 區段,drift 與 `guard settle` 呼叫它:方向對(見 F3 對放在區段裡哪個位置與重用的補充)。
- delguard 呼叫 `_vendored_state`:`cmd_delguard_check`(`scripts/lumos:29423`)在 `_vendored_state`(`scripts/lumos:17765`)之後,往下呼叫,方向對;`_vendored_state(root, "")` 與 `_is_toolchain_repo` 是既有慣用寫法(`scripts/lumos:24477`、`scripts/lumos:24609`、`scripts/lumos:18365`)。
- drift 區段借 `_nodehome_git`、`_nodehome_split_z`、`_nodehome_list`:drift 早就大量呼叫它們(`scripts/lumos:26828`、`scripts/lumos:28031`、`scripts/lumos:28265`、`scripts/lumos:28737`),不算跨層新增。

**問 2 命名與錯誤處理:大致對齊,有兩處不一致(F4、F2)。**
- `_conditions_rewrite(...) → (改後行, 錯誤訊息)` 回傳形狀與 `_guard_pass_rewrite`(錯誤放最後,`scripts/lumos:12274`)、`_drift_fix_by`(link, err)同族,命名 `_xxx_rewrite` 也同族。
- 錯誤訊息原樣沿用會撞前綴(F4)。

**問 3 第二種做法:沒有整套的第二種,但有三處「已有現成的、spec 措辭會另起一支」的地方(F2、F3、F5),另有一處慣用寫法的取捨(F6)。**

**問 4 落點:漏一篇(F1)。** lands_in 三篇對應:c4/c3 → 存量漂移守衛,`_conditions_rewrite` → lumos-cli-write,`_guard_prose_settled` → guard-kill;都是對的家。§5 改的是刪除傳播守衛,家在 Systems/delguard,沒列。

## Findings

## F1 §5 改到的刪除守衛,它的家節點沒列進 lands_in
severity: minor
blocking: 否
引句:「lands_in:   - Systems/存量漂移守衛   - Systems/lumos-cli-write   - Systems/guard-kill」
file: `docs/lumos-toolchain-knowledge/Systems/delguard.md:34`
1. §5 改 `cmd_delguard_check` 與 `_delguard_parse_diff`(加 `skip` 參數、跳過工具自裝檔),管這兩個函式的是 Systems/delguard(about_code 列了 `scripts/lumos`;沒有別篇講 `_vendored_state` 的跳過)。
2. 三篇 lands_in 都不是它;照 spec 落地,刪除守衛的行為變了(消費專案不再抽工具檔名稱),而它的家節點與「已知殘項」沒有任何一句記到,下一個 session 讀 delguard 會以為還是全比對。
3. 該補的一篇:Systems/delguard(計劃 related 已有 code側刪除傳播守衛_計劃,可保留)。delguard 那篇沒有 INVARIANT 行,沒有合約要改,只是補脈絡。

## F2 c3 的 --reason「抽成共用」在程式裡已經是共用的
severity: minor
blocking: 否
引句:「佔位字檢查從 `_drift_fix_c2_args` 抽成 c2、c3 共用」
file: `scripts/lumos:27622`、`scripts/lumos:27689`、`scripts/lumos:27732`
1. 佔位字檢查早已是獨立函式 `_drift_placeholder_err`(`scripts/lumos:27622`),c2 與 ack 兩處都在用(`scripts/lumos:27488`、`scripts/lumos:27699`);「一行、4 到 200 字」也早已在 `_drift_fix_args_err` 對任何 kind 的 `--reason` 統一檢查(`scripts/lumos:27732`,`_drift_fix_reason_ok`)。
2. 照字面「抽出來」實作,容易再包出第三支包裝函式;實際只需 `_DRIFT_FIX_ALLOWED["c3"]` 加 `reason`,`_drift_fix_c3_args` 內呼叫 `_drift_placeholder_err(o["reason"], "--reason")`。
3. 這是措辭問題(結構不用動),但會誤導實作者。

## F3 `_guard_prose_settled` 的辨認式該重用既有常數、放在寫入端旁,並讓「找不到」文字只有一處
severity: minor
blocking: 否
引句:「guard 區段加一支共用判定 `_guard_prose_settled(lines, kind)`:四種預告句各自的「轉正後說法」在不在」
file: `scripts/lumos:12030`、`scripts/lumos:12042`、`scripts/lumos:12212`、`scripts/lumos:12558`、`scripts/lumos:27839`
1. 檔內 12030 行的註解立下的規矩是「settle 改寫與 c1 找殘留用同一支比對,各寫一份會被自己擋」。「轉正後的說法」現在只出現在寫入端(`_guard_settle_rewrite` 輸出的 `預告已轉正`、`預告當時`、`(日期 已轉正)`),辨認端(`_guard_planned_prose`)只認預告句;spec 加的辨認式是第二份、與寫入端各自維護,寫入端的字樣改了它就悄悄失效。
2. WHY 與 settle 兩種既有常數已可用:`_GUARD_SETTLED_TAIL_RE`(`scripts/lumos:12036`)、`_GUARD_MANUAL_SETTLED_RE`(`scripts/lumos:12212`,`(2026-09-30 已轉正)` 也符合它);spec 沒說重用,只說「沿用既有 why-done 的辨認」。TEST 與 whynot 兩種要新寫,應放在 `_guard_planned_prose` 同一段、和寫入端字樣同處。
3. 「找不到」的字樣目前有兩處各自組:`_guard_settle_missing_say`(`scripts/lumos:12558`)與 `_drift_fix_c1`(`scripts/lumos:27839`);spec 讓兩處各自去問新函式。更貼近既有做法:在 `_guard_pass_rewrite`(兩邊共用的入口)內就把 missing 分成「已轉正」與「真的找不到」再回傳,兩個呼叫端不用各問一次。

## F4 `_conditions_rewrite` 原樣回傳的錯誤訊息,經 drift fix 印出會雙重前綴、且帶 set 專屬指示
severity: minor
blocking: 否
引句:「錯誤訊息整句原樣回傳;`_set_conditions_locked` 讀檔 → 呼叫它 → 有錯就照原樣印到 stderr、回 2」
file: `scripts/lumos:15134`、`scripts/lumos:28182`
1. 現有三道檢查的訊息本身以「擋下:」開頭、以「檔案沒動」結尾,且第三道寫「要寫多條就給多個值:lumos set <筆記> …」(`scripts/lumos:15134`-`scripts/lumos:15142`)。
2. drift fix 的慣例是 `(None, err)` 回傳、由 `cmd_drift_fix` 統一印 `擋下:{err}`(`scripts/lumos:28182` 一帶)。c4 `--values` 走這條路時,使用者會看到「擋下:擋下:值裡還留著…」,而且被指示去用 `lumos set` 的多值寫法,而不是 `--values`。
3. 同一批訊息要兩個呼叫端共用,該讓函式回不帶前綴、不帶指令的核心句,前綴與「檔案沒動」由各端加(set 端照原樣加回去,S3 才能一字不變)。

## F5 c4 列提交檔案清單:drift 區段自己的 git 包裝是 `_ns_git`,spec 手動加 quotePath 旗標
severity: minor
blocking: 否
引句:「`_nodehome_git(root, "-c", "core.quotePath=false", "show", "-z", "--name-only", "--diff-filter=A", "--format=", <提交>)`」
file: `scripts/lumos:24739`、`scripts/lumos:24485`、`scripts/lumos:24065`
1. drift 區段讀「路徑不加引號」的 git 輸出用的是 `_ns_git`(內含 `quote=True`,`scripts/lumos:24739`;`scripts/lumos:26538`、`scripts/lumos:27096`、`scripts/lumos:28734` 都這樣用);「提交加了哪些檔」在 `scripts/lumos:24485` 已有先例:`_nodehome_git` 加 `show --diff-filter=AR --name-only --format= -z`,沒有手加 `-c`。spec 又手寫一種 `-c core.quotePath=false`,而且用了 `-z`(`-z` 本身就不轉義路徑,旗標多餘)。
2. 另外 `_nodehome_commit_groups`(`scripts/lumos:24065`)已處理合併提交(章魚合併、無 `--first-parent` 的空輸出);spec 自己在 §1 承認「第一次進歷史的是合併提交」只能退回,是另一種做法而沒有說為什麼不借它。⚠ 判不準這是設計取捨還是漏看,標 minor。
3. 建議:用 `_ns_git`(或照 24485 行先例只用 `-z`),不另加旗標。

## F6 §5 用第五份內嵌 skip 寫法,而「工具檔跳過」另有共用的 `_vendored_skip` 且多處理拆除
severity: minor
blocking: 否
引句:「不是才取 `_vendored_state(root, "")[0]`(讀索引裡的檔與 `.lumos/vendored.json`),得到「跟安裝清單一致」的工具檔集合。」
file: `scripts/lumos:17832`、`scripts/lumos:24477`、`scripts/lumos:24609`、`scripts/lumos:18365`
1. 既有兩種寫法:範圍型的 `_vendored_skip(root, diff_range)`(推送分級、代碼審鏡頭共用,含「拆除工具鏈也跳」),與內嵌的 `frozenset() if _is_toolchain_repo(root) else _vendored_state(root, X)[0]`(`scripts/lumos:18365`、`scripts/lumos:24477`、`scripts/lumos:24609` 各一份)。spec 選內嵌那種,是既有先例,不算引入新做法。
2. 但同一件事(該不該跳工具檔)在拆除提交上出現兩種答案:推送分級跳、刪除守衛照舊抽,spec 的誠實界線與 REVISIT 已承認;⚠ 我不判這是缺陷,只點出內嵌的寫法已經第四處重複,新加第五處時值得抽一支「索引或某版本」的小函式一起收(`scripts/lumos:24477`、`scripts/lumos:24609` 同形)。屬整理建議,不阻擋。

---
不對齊共 6 條,其中 major 0 條。
最高等級:minor;blocking 共 0 條
