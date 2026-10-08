severity: major

**[1] 事件的 `gate` 欄沒定義**
severity: major
blocking: 是 照字面實作,新事件會被 `_gate_event` 拒寫,背書永遠查不到。
- `_gate_event` 要求 gate 在 `_KNOWN_GATES` 名單內;名單沒有 guard-kill、contract-evidence,只有 kill 與 code-loop。新增要過漂移釘 t_gov_stats_gate_drift。
引句:「再用既有的治理帳寫入(`_gate_event_or_warn`,不改變呼叫端判定)為每條配方各寫一筆 `kind=guard-kill`」
file: `scripts/lumos:1215` 不在 `_KNOWN_GATES` 就 return False。
file: `scripts/lumos:6943` 名單沒有這兩個閘名。

**[2] `commit` 欄:欄位衝突與格式不明**
severity: major
blocking: 是 祖先比對的輸入值沒定義清楚。
- `_gate_event_build` 預設 commit=head_sha[:7](repo_root);cmd_guard_kill 的 commit 是 proot 的 --short HEAD;跨 repo 平台的 sha 屬另一個 repo;多平台只記最後一組,與「每條配方各寫一筆」矛盾;短碼撞碼沒規定;現行跨 repo root 只做工作樹那道,新規則沒有對應分支。
引句:「欄位 `node`、`invariant`、`test`、`platform`、`verdict`、`commit`(跑的當下 HEAD)、`files`(配方改到的檔)」
file: `scripts/lumos:1163` commit 預設為 head_sha[:7]。
file: `scripts/lumos:13058` commit 取自 proot 的 --short HEAD。
file: `scripts/lumos:37219` 跨 repo root 直接放行第二道。

**[3] `files` 路徑基準與「改動偵測」不對齊**
severity: major
blocking: 是 會讓過期偵測失效或誤報。
- 配方 file 相對平台 root,檢查在 repo_root 跑 git diff;files 空集合等於永久有效;改名偵測不到;測試檔本身與受測程式沒涵蓋。
引句:「從那筆的 `commit` 到被推送版本之間,`files` 裡任一支檔有改動 → 「背書過期,要重跑破壞測試」。」

**[4] 「最新一筆 killed」忽略同測試多配方與新舊交錯**
severity: major
blocking: 是 會讓背書被未涵蓋的配方頂替。
- 之後的 survived/drifted 被忽略;舊配方過期不提醒;事件沒有綁題目 id,任何咬得住任意壞法的測試都能替所有被標題目背書。
引句:「找同一個測試名、`verdict=killed` 的最新一筆:」

**[5] 測試名比對未正規化**
severity: major
blocking: 是 會讓多平台專案合法的表態被誤判。
- 表態 test:<平台>:<名> 或裸名;配方 test 可能帶前綴、裸名或反引號;跨平台同名會混或誤判。
引句:「找同一個測試名、`verdict=killed` 的最新一筆:」
file: `scripts/lumos:36954` 平台切分規則。
file: `scripts/lumos:13077` 方法名反引號處理。

**[6] 讀帳來源未定:工作樹或推送樹?**
severity: major
blocking: 是 本機與 CI 會判出不同結果。
- 讀工作樹:本機過、CI 判沒有背書;讀 at_sha 樹:剛跑完未提交也沒有背書。帳可手寫偽造 killed,沒有簽章;files 是事件自報。
引句:「表態檢查(`_dispositions_verdict` 走到被標題目的 satisfied)讀治理帳,找同一個測試名、`verdict=killed` 的最新一筆:」
file: `scripts/lumos:36139` 現行讀法讀工作樹。

**[7] 淺層 clone / 取不到祖先 / 第一個提交**
severity: major
blocking: 是 CI 常見情境下 block 模式會誤擋。
- 淺層 clone 時物件不存在,無法區分「不是祖先」與「物件缺席」;沒有第三態;at_sha 為空或第一個提交沒說。
引句:「那筆的 `commit` 不是被推送版本的祖先 → 「沒有背書」(在別的分支跑的不算)。」
file: `scripts/lumos:37150` 既有祖先判定的錯誤訊息只考慮壓提交與 rebase。

**[8] gate=off / high-only 讓 contract_evidence 被整段跳過,與「互不影響」矛盾**
severity: major
blocking: 是 block 會被 gate=off 靜默吞掉。
引句:「跟既有的 `stack_questions.gate`(控制整個表態閘 all/high-only/off)並列、互不影響。」
file: `scripts/lumos:37265` 早退條件。

**[9] warn 模式「不改回傳碼」的實作通道不存在**
severity: major
blocking: 是 照字面接進 problems 會變成擋。
- `_one` 回傳全進 problems、blocked=bool(problems);warn 需要獨立通道;每次 check 都寫一筆 contract-evidence 沒去重,吃 ledger-growth 預算。
引句:「`warn`:沒有背書或背書過期時,`code-loop check` 印提醒並寫一筆治理帳 `kind=contract-evidence` 事件(題目 id、原因),不改回傳碼。」
file: `scripts/lumos:37349` `_one` 的回傳全進 problems。

**[10] 設定值大小寫與型別**
severity: minor
blocking: 否 可由既有慣例推得。
引句:「設定寫壞照預設,並照 `_stack_questions_config` 既有慣例把說明放進回傳的 warnings」
file: `scripts/lumos:21417`

**[11] 被觸發題目但專案沒有任何合約 / 沒有 docs**
severity: minor
blocking: 否 逃生門刻意保留。
- 沒合約只能 na/todo;沒有 docs/ 的「不做背書判定」沒有驗收條款;tension 繞過路徑。
引句:「na(理由 ≥10 字)、todo(連 Issue)、tension 不受影響」

**[12] 派工鏡頭:簽名不夠,快取鍵算法未定**
severity: major
blocking: 是 `_lens_dispositions_lines(lines, rec)` 沒有 repo_root、at_sha,照寫無法用同一支函式算狀態。
- 快取 extra 怎麼併、TTL 1200 秒、鏡頭預算沒算進。
引句:「現行附表態的 `_lens_dispositions_lines` 只讀表態標記、不讀治理帳,所以要多讀一次治理帳的 `guard-kill` 事件」
file: `scripts/lumos:34822` 現行簽名。
file: `scripts/lumos:35878` 呼叫點。
file: `scripts/lumos:34841` extra 參數。

**[13] 讀取成本:帳本上萬筆 × 每題一次**
severity: minor
blocking: 否 已有預算與 fail-open 兜底。
- 應一次讀入建索引;超預算 fail-open 等於靜默略過背書檢查。
引句:「表態檢查每題多一次讀治理帳加一次 `git diff --name-only`;治理帳大時讀取成本要量」

**[14] 驗收條款 [S1]~[S12] 覆蓋缺口**
severity: major
blocking: 是 幾個宣稱的行為沒有任何測試能驗到。
- S2 沒驗 --json 純度與無 docs;S4 測不到較新 survived;S5 沒淺層/物件缺席/跨 repo;S6 沒 files 空、改名;S7/S8 沒涵蓋 gate=off;S9 斷言方式;S11 沒驗快取失效;S12 manual;回退沒條款。
引句:「[S9] 若設定為 off,code-loop check 應 完全不做背書檢查 [test:t_contract_evidence_off_mode]」

**[15] 「強證據」不含「這支測試真的跟題目有關」**
severity: minor
blocking: 否 語意缺口,靠人審補。
引句:「而且治理帳裡要有一筆「這支測試的破壞測試是強證據」的紀錄,且沒過期」

**[16] 引用核對**
severity: minor
blocking: 否 已讀,僅記事實。
- 抽驗函式皆存在;4 筆屬實;忽略清單屬實(`scripts/lumos:18250`)。

實務隱患:併發寫入沿同一函式但見 [1];相容成立;帳可偽造見 [6];輸出純度無測試守見 [14];淺層與跨 repo 見 [2]、[7]。

最嚴重 severity:major,blocking 共 11 條([1]、[2]、[3]、[4]、[5]、[6]、[7]、[8]、[9]、[12]、[14])。
