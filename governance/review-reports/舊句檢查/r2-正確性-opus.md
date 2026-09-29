severity: major

# 設計審第 2 輪:正確性-opus(舊句檢查_計劃,凍結版 r2-snapshot.md)

實驗環境:`git clone --shared` 到本席暫存 `osr2/`(頂端 23f75c8d),直譯器 /opt/homebrew/bin/python3;參考實作用 `import old_sentence_exp`(它自己載入同 repo 的 `scripts/lumos`)。沒動 repo 任何檔。

逐節結論摘要:
- 〈依據〉〈PRIOR-ART〉〈RETIRE-IF〉〈REVISIT〉:「以 P4r3 為準」這句的適用範圍太寬(F6);其餘已讀,無 finding。工具鏈 300 個提交的 P4r3 重跑結果見文末〈附:重跑〉。
- 〈範圍〉:已讀,無 finding。
- 〈做法〉1:起點三種(F10)、候選名稱為空時的狀態判定(F1、F2)、git-failed 跟 timeout 分不開(F5)、抽定義字面比參考實作寬(F7)。
- 〈做法〉2:名稱先篩(F4)、家的判法(F9)、切句與整字的邊界細節(F7)。
- 〈做法〉3:表態提示照貼(F3)、治理帳欄位寫法(F8);`_drift_config`、rc 組合、`_DRIFT_SCAN_KINDS`、`_drift_split_acked` 的聯集分支都照程式核過,無 finding。
- 〈做法〉4:`extra.*` 寫法(F8);其餘已讀,無 finding。
- 〈條款〉:S4(F3)、S10(F4)、S11 跟〈做法〉3 打架(F2);其餘已讀,無 finding。
- 〈回退〉:已讀,無 finding(`_drift_load_acks` 確實用 `d.get("kind") in _DRIFT_KINDS` 過濾,舊版讀到 `m1` 行會直接丟掉)。
- 〈實務隱患〉〈誠實界線〉:4 MB 的回頭條件接不上(F2);其餘已讀,無 finding。
- ★INVARIANT★ 逐條看:`Systems/guard-kill` 的兩條(guard kill 的 rc 優先序、`--json` 的 stdout 純度)——`m1` 不碰 guard kill 的程式路徑,不影響;`Systems/lumos-cli-read` 的 search 預設排除 superseded——`m1` 自己掃 superseded 筆記,不經過 `cmd_search`,不影響;`Systems/lumos-cli-write`、`Systems/存量漂移守衛` 都沒有 ★INVARIANT★ 行。`Systems/存量漂移守衛` 第 20 行的 RULE(預設改 block 要三條全過)計劃在〈誠實界線〉最後幾條已經交代;第 22 行 RULE(開關讀被推送的頂端)計劃沿用,不影響。

## F1 沒有候選名稱就回 no-candidates,把時間到與 git 失敗也吞成「不印、不記帳、rc 0」
severity: major
blocking: 是
引句:「另外有起點但沒有候選名稱時回 `no-candidates`(不印、不記帳)」
1. 計劃把候選名稱定義成「過了形狀過濾與消失判定之後的名稱,空的就是 `no-candidates`」。可是判定「消失」要先把**終點語料所有 Python 檔**的定義集合剖完(〈做法〉1「消失」那條),冷快取時這正是最花時間的一步。
2. 情境:CI(永遠冷快取)或本機第一次推送,repo 的 Python 原始碼大到 30 秒剖不完(〈誠實界線〉自己寫了「約 100 MB 量級、CI 機器慢的話更小」)。第 30 秒還在剖終點語料時,候選名稱集合還沒算出來、照字面就是空的 → 判定函式回 `no-candidates` → 照〈做法〉3「不印、不記帳」→ `rc_m1` 是 0。
3. old_sentence=block 時,這就是一條靜默放行的路,跟〈誠實界線〉「block 時照既有規矩算要處理」、以及 S6「時間到時 … block 模式算要處理」直接相反;S6 只在「有候選名稱」時才要求記帳,所以這種時間到連帳都沒有。
4. warn 模式同樣不記帳 → 〈做法〉4 的完成率 = timeout ÷(done + timeout)的分子漏掉最常見的那種時間到 → RETIRE-IF ③(時間到占比 > 5% 就不准改成擋)被系統性低估,兩週後可能在大 repo 還常逾時的情況下判成「可以轉擋」。
5. `git diff --name-status` 或列檔失敗同理:候選名稱算不出來 → 空的 → `no-candidates`,本該是 `git-failed` 的判不了在 block 下被放行。
6. 改法:把 `no-candidates` 限定成「state 是 done、而且候選名稱是空的」;只要 state 是 timeout、git-failed、unreadable 就照那個 state 印、記帳、算判不了,不管候選名稱算到哪裡;S6 的條件改成「有候選名稱、起點是空樹、或 state 不是 done」,S10 或 S6 加一題「終點語料剖到一半就時間到(候選名稱還是空的)→ state=timeout、block 回 1、有帳」。

## F2 只有剖不動或太大的檔被改到時也落進 no-candidates,S11 要印的那行印不出來,4 MB 上限的回頭條件接不上電
severity: major
blocking: 是
引句:「回頭條件接在 `m1` 自己的輸出上」
1. 〈做法〉1 說改到的檔任一版剖不動或太大 → 那支檔不抽候選、印「N 支剖不動」「N 支太大沒剖:<路徑>」;可是〈做法〉3 又說有起點但候選名稱是空的就回 `no-candidates`、不印不記帳。兩句同時照做:一次推送只改了一支剖不動(或太大)的 Python 檔 → 那支不抽候選 → 候選名稱空 → 什麼都不印。
2. S11 的測試「改到的檔任一版剖不動 → 那支不抽候選、印「N 支剖不動」」如果只放這一支檔,照〈做法〉3 會紅;要讓它綠就得另外造一個候選名稱,等於測試迴避了這個矛盾。
3. 〈誠實界線〉最後一條把 4 MB 上限的回頭條件接在「工具鏈推送一印出 `scripts/lumos` 就重量」。工具鏈最常見的推送形狀是只改 `scripts/lumos`(加上測試與筆記):等主程式長過 4 MB,這種推送 `scripts/lumos` 太大不抽候選,測試檔多半沒刪名稱 → 候選名稱空 → `no-candidates` → 那行永遠不印。鐵則四要的「回頭條件要接電」在它設計要抓的那個情境失效,而且那段期間主程式本身的舊句全漏(〈誠實界線〉已承認)卻沒有任何訊號。
4. 推上一個語法壞掉的 `.py`(剖不動)也一樣:什麼都不印,人不知道 `m1` 這次對那支檔沒判。
5. 改法:剖不動支數或太大支數大於 0 時,不回 `no-candidates`(至少照印那兩行;要不要記帳一起寫明);或把 `no-candidates` 的條件寫成「候選名稱空、而且剖不動與太大都是 0」。S11 寫明「只改一支剖不動的檔」這個情境的預期輸出。

## F3 S4 要求照貼 m1 提示的指令 rc 0,但提示裡的佔位理由會被既有守衛擋成 rc 2
severity: major
blocking: 是
引句:「照 `m1` 提示印出來的指令原樣貼上(名稱是 `--restore` 時)rc 0」
file: `scripts/lumos:27483`
file: `scripts/lumos:27619`
1. 〈做法〉3 規定 `m1` 的提示是 `lumos drift ack <節點> <行號> --kind m1 --name=… --reason "<為什麼照留>"`。`_drift_ack_args_err` 最後一步是 `_drift_placeholder_err(reason, "--reason")`,它的正則 `<(?:為什麼[^<>\n]{0,30}|sha|卷證)>` 正好認得 `<為什麼照留>`。
2. 實跑:`_drift_ack_args_err("probe", "<為什麼照留>")` 回「--reason 裡還留著提示的佔位字「<為什麼照留>」——換成真的內容再跑」,也就是 rc 2。`m1` 走同一支檢查(〈做法〉3「`_drift_ack_args_err` 多一個名稱參數」),照 S4 字面「原樣貼上」必定 rc 2。
3. 照字面實作的人要讓 S4 綠,最省事的做法是把 `m1` 提示裡的佔位字換成守衛不認得的寫法(例如 `<理由>`)——那就重開了存量漂移改法代碼審 r1 合約圖譜席修掉的洞(照貼提示把佔位字記成理由);`Systems/存量漂移守衛` 第 45 行 PITFALL 也寫明佔位字「原封不動照貼會被擋下」是刻意的。
4. 改法:S4 與〈做法〉3 的例子改成「把 `<節點>`、`<行號>` 以外的佔位理由換成真理由、其餘原樣照貼 → rc 0;連佔位理由原樣貼 → rc 2(佔位字守衛)」,兩個斷言都放進 `t_drift_m1_ack_binds_name`。

## F4 名稱先篩照 _DriftNames 的做法會篩掉緊貼中文的旗標與路徑、非 ASCII 名稱,跟 P4r3 與〈做法〉2 的整字規則都對不上
severity: major
blocking: 是
引句:「照既有 `_DriftNames` 的做法(全文先切成集合查;帶 `-` `/` `.` 的名稱看每一段都在集合裡)」
file: `scripts/lumos:26919`
1. 參考實作 P4r3 沒有先篩,直接用 `_mk_rx` 逐行掃;所以先篩必須是「掃得到 ⇒ 先篩一定留下」的必要條件,不然就少列。計劃只寫了「切詞改 ASCII」,其他照 `_DriftNames`,有兩個地方會漏:
2. `_DriftNames.has` 對帶標點的名稱,第二步是對全文跑 `(?<![\w])名稱(?![\w])`——Python 的 `\w` 含中文字與 ①② 這類字。實跑(集合改用 ASCII 切、其他照原樣):「加了--restore旗標還在用」→ `_mk_rx` 列出 `--restore`,先篩回空;這跟〈做法〉2「中文字緊貼照算提到」相反。工具鏈圖譜現在就有 28 處旗標前後緊貼這類字(例:`Issues/init-force-slug誤用basename` 第 20 行「①--name ②既有」、`Projects/design-loop重設計_實作計畫` 第 18 行「③--disposal」)。
3. 字面「每一段都在集合裡」如果照 `-` `/` `.` 切段:`--restore` 切成 `['', '', 'restore']`,空字串不在集合 → **所有旗標**都被篩掉;`tools/匯出報表.py` 的 `匯出報表` 段不在 ASCII 集合 → 被篩掉(參考實作列得出,已實跑)。
4. 沒有 `-` `/` `.` 的名稱「全文先切成集合查」:Python 允許非 ASCII 識別字,`def 計算_總額()` 被刪後,筆記「呼叫 計算_總額 算錢」參考實作列得出,先篩查集合查不到 → 篩掉(已實跑)。
5. S10 只釘「改了foo_bar函式」這一種,上面三種都不會讓測試紅。
6. 改法:先篩寫成「名稱裡每一段 `[A-Za-z0-9_]+` 都在集合裡就留下(沒有任何 ASCII 段的名稱不篩),之後一律交給 `_mk_rx` 判,不再用 `\w` 邊界對全文跑第二次」;S10 補「加了--restore旗標」「`tools/匯出報表.py`」兩例要列。

## F5 批次讀用剩下的時間當上限,逾時被記成 git-failed 而不是 timeout
severity: minor
blocking: 否
引句:「`git-failed`(git 列檔、diff 或批次讀失敗)」
file: `scripts/lumos:26496`
file: `scripts/lumos:23996`
1. 〈做法〉1 說批次讀「以剩下的時間為上限」;`_drift_tree_env` 用 `max(1, deadline - now)` 當逾時,`_nodehome_cat_blobs` 在 `TimeoutExpired` 時回 None,`_drift_tree_env` 再回 None——跟 git 真的失敗同一個回傳值。
2. 情境:冷快取剖檔用掉 29.5 秒,接著讀終點圖譜(工具鏈上千篇)給 1 秒逾時 → 讀不完回 None → 照〈做法〉3 的分類是 `git-failed`。rc 不受影響(兩者都算判不了),但〈做法〉4 的完成率只數 timeout,這類時間到被分到「另列」的 git-failed,RETIRE-IF ③ 又被低估一點。
3. 改法:寫明「批次讀回 None 時,若當下已過截止時間就記 timeout,否則記 git-failed」,S6 或 S10 加一題。

## F6 「以 P4r3 為準」的範圍沒限定,跟計劃刻意偏離參考實作的幾處互相打架
severity: minor
blocking: 否
引句:「凡是本計劃的字面跟 P4r3 不一樣,以 P4r3 為準、並回頭改計劃」
1. 參考實作(`Push.tip_all_defs`)對終點語料裡剖不動的檔**什麼都不做**;計劃〈做法〉1 與 S11 要求對它們跑 `_drift_py_def_re` 與引號旗標的文字比對。照「以 P4r3 為準」,實作者可以合法地拿掉這個退路,S11 就沒有依據。
2. 同類刻意偏離還有:4 MB 不剖(參考實作不限)、接 MemoryError(參考實作只接三種)、讀不出的筆記算判不了(參考實作一律 `decode("utf-8", "replace")` 照掃)、名稱先篩與 200 個一批(參考實作一條正則掃全部)、時間上限(參考實作沒有)。
3. 改法:把那句收窄成「判定結果(哪些名稱消失、哪幾行列出、哪一層)以 P4r3 為準;下列幾處是刻意偏離,以計劃為準:…(列上面那幾項)」。

## F7 幾條「照參考實作」的規則,計劃的字面比參考實作寬或窄,驗收數字對不上時沒有依據
severity: minor
blocking: 否
引句:「tuple/list 拆包的每個名稱」
1. 抽指派:參考實作 `_assigns` 只收一層拆包裡的 `Name`。實跑 `A_ONE, (B_TWO, C_THREE) = …`、`FIRST_X, *REST_Y = …` 只收到 `A_ONE`、`FIRST_X`;`except*`(`ast.TryStar`)裡的指派、`type Alias_T = int`、`COUNT_N += 1` 都不收。計劃字面「每個名稱」「try(含 else、except、finally)」會讓實作者多收巢狀與星號拆包、`except*`。
2. 括號裡的切句:參考實作 `_clause_has_hist` 在括號內容裡**也**用 `。;;!?!?` 切;計劃寫「只看包住它的最內層那對的內容」。實跑「現況(原本叫 x。foo_bar_x 還在用)」參考實作判沒有歷史字眼(照列),照計劃字面整段括號內含「原本」會不列。
3. 沒關上的括號:參考實作只看最後一個沒關上的 `(`,它在名稱後面就當成括號外;實跑「(說明 foo_bar_x 還在 (x」參考實作走括號外。計劃「行裡有沒關上的 `(` 在名稱前面」會取第一個。
4. ASCII 字眼大小寫:參考實作 `HIST_RX2` 大小寫敏感,實跑「Removed in v2」不命中、「removed in v2」命中;計劃只寫「整字比」。
5. 整字的兩組邊界:`_mk_rx` 用「沒有 `--` 開頭、沒有 `/`、沒有 `.`」分組,`-` 不在判準裡(`Tool_x-v2` 這種根目錄檔名走識別字邊界);而且交替正則是識別字組在前,同一位置 `run_all` 會先吃掉 `run_all.sh`。計劃寫「含 `-`、`/`、`.` 的」走另一組,再加上超過 200 個名稱才分批——分批後兩個名稱在不同批會都列出,同一行的名稱集合跟不分批時不同,表態的子集判斷會因為這次推送候選多寡而變。
6. 改法:這幾條改寫成「逐字照參考實作 `<函式名>`」並各補一個例子進 S2、S8、S10;或明寫刻意偏離並列進 F6 那份清單。

## F8 計劃寫 extra.check、extra.base_sha,但 _gate_event 把 extra 攤平到最外層
severity: minor
blocking: 否
引句:「`--pairs` 每行一組 `<base_sha>..<head_sha>`(從帳的 `extra.base_sha` 與 `head_sha` 抽」
file: `scripts/lumos:1217`
1. `_gate_event` 是 `ev.update(extra)`:寫進帳的是最外層的 `check`、`state`、`base_sha`、`handle`、`rows`,沒有 `extra` 這個鍵。REVISIT 那天照〈做法〉4 用 `ev["extra"]["base_sha"]` 抽會拿不到東西;S6 的測試照字面寫 `ev["extra"]["check"]` 會紅,實作者可能因此把 `extra` 包一層傳進去(`extra={"extra": {...}}`),那樣 `grep '"check": "old-sentence"'` 又對不上寫法。
2. 改法:計劃裡的 `extra.xxx` 一律寫成「事件的 `xxx` 欄(經 `_gate_event` 的 extra 參數寫入、攤平在最外層)」,S6 寫明斷言的是最外層欄位。

## F9 「家」照參考實作算,跟既有的唯一家對照算法不同,superseded 的 Systems 也算家
severity: minor
blocking: 否
引句:「起點樹或終點樹任一邊的 about_code 列了它」
file: `scripts/lumos:23807`
1. 既有 `_home_map_from_notes` 註明是「家對照表的唯一算法」:只認 `type: system`、status 在 doing/done/stale,about_code 過 `_nodehome_key` 正規化。參考實作 `homes_any` 不看類型與狀態、只做去引號去反引號。
2. 情境:`Systems/舊模組` 已 superseded、about_code 還列著 `a.py`;這次刪掉 `a.py` 的 `old_func`,那篇正文講 `old_func` 的行 → 照計劃是要處理(block 時擋),照既有家算法它不是家、只列出。superseded 筆記裡講舊名稱本來就是歷史,這一類在要處理層是誤報方向。
3. ⚠ 驗收數字是照 `homes_any` 量的,改用既有算法要重跑;至少在〈誠實界線〉寫明兩套家算法的差別與這個誤報方向,REVISIT 抽判時把「superseded 筆記的要處理」單獨分類。

## F10 起點那節說 resolve 回整數時「帳只有既有那筆 skipped」,有幾條整數路徑根本不記帳
severity: minor
blocking: 否
引句:「整支 check 在那裡就回了,`m1` 不跑,帳只有既有那筆 skipped」
file: `scripts/lumos:25776`
1. `_note_audit_resolve` 回整數的路徑裡,只有淺層 clone(`skipped-env`)與 `_lens_push_base` 回 None(`skipped`)會記帳;範圍終點全 0(刪除分支)、`_nodehome_list` 失敗、這個專案沒有圖譜都回 `(None, 0, None)` 而不記帳,範圍寫錯回 2 也不記。
2. 行為上 `m1` 照樣不跑,不會做錯;只是 REVISIT 對帳時會以為每次沒跑都有一筆 skipped。改成「照既有的那幾條路徑處理(有的記 skipped、有的不記)」即可。

## 附:重跑

- 工具鏈 300 個提交(頂端 40c1fe0d)用參考實作 P4r3、P4r2 逐提交重跑(本席暫存 `tcrun.py`),結果見下一行;9 題與 rtb 需要 rtb 唯讀複製,本席沒有,沒重跑。
- 重跑結果(255 秒):P4r3 共 1 筆、只列出、要處理 0——b4060e37 的 `Issues/code-loop-pass自失效追尾` 第 54 行,名稱 `_BOOKKEEPING_DIR`;P4r2 逐筆相同。跟〈依據〉寫的「工具鏈 300 個提交 1 筆只列出、要處理 0,跟 P4r2 逐筆相同」一致。

最高等級:major;blocking 共 4 條
