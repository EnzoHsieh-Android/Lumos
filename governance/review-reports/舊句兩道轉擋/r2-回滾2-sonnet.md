severity: major

派工未附固定席節點,所以沒有逐條判固定席的項目。

## 逐節結論

- 原問題與範圍:見 F3、F8。
- 開關:見 F4、F11。
- 重讀:候選與兩層:見 F1、F3、F6、F10。
- 回傳碼與判不了:見 F4、F12。
- 輸出:見 F9。
- 照留表態:見 F2。
- 掛鉤與 CI:見 F13。
- 要一起改的說法:已讀,無 finding。
- 對消費專案的影響:已讀,無 finding。出路是在 `.lumos/config.json` 寫 `note_reread.gate` 為 warn,不需要 `--no-verify`。設定從被推頂端讀,所以同一次推送就能生效。
- 驗收條款:缺 F2 的「兩個 PR 各自表態」與 F1 的「provenance 為假後重派」兩個場景。
- 實務隱患:見 F3、F8、F12。
- 回退:見 F4、F5。
- 審計修正紀錄:已讀,無 finding。

備註:F7 的編號已併入 F3,沒有獨立 finding。

## Findings

### F1 第一層要求 provenance_ok 為真,但判定入口和 prepare 都只認檔名,擋下時印的指令派不出新項目檔

severity: major
blocking: 是
判準:照 spec 實作,擋下後照印出的 prepare 指令做會走進死路,只剩單次略過或改設定。

- spec 段落:〈重讀:候選與兩層〉第一層、〈輸出〉第二條、驗收條款 S6。
- 場景:
  - 判定者報告開頭四行抄錯,`reread-record` 照收,只印一句「提醒」,rc 為 0,記成 `provenance_ok: false`。
  - 作者提交後推送,第一層判成「沒對照」並擋下,印 prepare 指令。
  - 作者照貼執行,prepare 因為同指紋已有紀錄,回「都對照過這一版程式了,不產項目檔」。
  - 能產出新項目檔的只有 `--all`,但擋下訊息和 `_note_reread_cmdline` 都沒印這個旗標。
- 壞在哪:spec 沒列「`_note_reread_committed` 要讀內容」或「prepare 要改略過口徑」這兩項改動。判定者換模型、模型沒回報頭四行的情況常見,這條死路會反覆遇到。
- 佐證:
  - file: `scripts/lumos:34696-34709`。`_note_reread_committed` 的 docstring 寫「只列目錄、比檔名,不讀內容」。
  - file: `scripts/lumos:34774-34790`。prepare 用同一個 `done` 集合略過已有紀錄的篇。
  - file: `scripts/lumos:34726-34731`。`_note_reread_cmdline` 不帶 `--all`。
  - file: `scripts/lumos:34877-34886`。record 對 `provenance_ok` 為假只印提醒。

引句:「候選的對照指紋沒有任何已提交、而且 `provenance_ok` 為真的判定紀錄」

引句:「第一層 → prepare 指令(派判定者、record、提交)」

### F2 「reread 併入 `_DRIFT_BOUND_KINDS`」做不成,兩個 PR 各自表態時,合併後的主線 CI 會紅

severity: major
blocking: 是
判準:spec 指定的機制與現有程式的行為不相容,又沒定義多份紀錄時表態怎麼算數,不先補就會實作出錯誤行為。

- spec 段落:〈照留表態〉第二條、S11、S12。
- 程式面三處不相容:
  - `cmd_drift_ack` 對 `_DRIFT_BOUND_KINDS` 的種類會呼叫 `_drift_current_finding`。reread 不是 `_drift_state_findings` 產的發現,所以永遠回 2「現在不是 reread」。file: `scripts/lumos:37500-37506`、`scripts/lumos:37552-37558`。
  - `_drift_ack_buckets` 只收有 `related` 欄且 `seq` 合法的表態。reread 表態帶的是 `verdicts`,沒有 `related`,會被靜默丟掉,永遠對不上。file: `scripts/lumos:37278-37290`。
  - `_drift_split_acked` 只取同鍵 `seq` 最大那幾筆,且「全部都涵蓋」才算已表態。file: `scripts/lumos:37264-37272`、`scripts/lumos:37321-37326`。
- 場景:
  - 兩個 PR 同時改同一篇筆記,各自記判定。A 的紀錄指紋是 fpA,B 的是 fpB,兩邊都點出同一條 `RULE:` 行。
  - 兩邊各自 `drift ack`,表態分別綁 `[fpA]` 和 `[fpB]`。
  - 兩邊都從同一份檔尾取 `seq`,所以同號。`_drift_bound_latest` 註解寫的就是「兩個工作樹各自追加後合併可能同號」。
  - 合併後頂端同時有兩份紀錄、兩筆表態。照 BOUND 的比對,兩筆同號表態都得涵蓋這條行,但各自只涵蓋自己的那份。
  - 結果這條行被判「要處理」,主線 CI 第二層紅。〈設計〉特地用「只在本機擋第一層」避開主線修不掉的紅燈,這裡又走回去。
- 要補什麼:spec 要明講第二層是「每份點出的紀錄各自要有表態涵蓋」的聯集語意,不能照 c2/c3 的取最新。實作也要走獨立分支,不是改 tuple。

引句:「reread 加進 `_DRIFT_BOUND_KINDS` 那一類的比對:第二層只認 `verdicts` 含點出那一列的紀錄指紋的表態」

### F3 第一層的指紋幾乎每次推送都變,「提醒形同虛設」的主因被誤讀,而且 RETIRE-IF 量不到第一層

severity: major
blocking: 否
判準:這是營運成本和量測缺口,有 RETIRE-IF 和設定退路,但上線後會馬上變成大量略過。

- spec 段落:〈原問題與範圍〉、〈實務隱患〉第四條、RETIRE-IF。
- 場景:
  - 對照指紋含每支 `about_code` 的 blob。`scripts/lumos` 被約 70 篇筆記列為 `about_code`(證據:`Projects/守檔筆記對照改動_計劃.md:27`)。這支檔幾乎每個提交都改,所以所有這類家筆記的指紋隨之全變。
  - 生產帳(`docs/.governance-log.jsonl`)裡 18 筆 `reminded` 全是「已對照 0 篇」。同一篇 `Systems/guard-kill.md` 在相鄰推送的指紋是 c7c57483、6ef99b4f、8fe141d7、c4d8901c,每次都不同。35 筆 `note-reread` 事件裡 `covered` 為 0。
  - 18 次推送共有 47 篇要判定,實際只記了 5 份。
  - 「提醒之後只有不到三成去記錄」是因為判定完只要再改一行程式,指紋就作廢,不只是人懶。spec 只把原因歸給「合併主線」。
  - 改成擋之後,每個加修正的推送都要重派判定者並提交紀錄。RETIRE-IF 只量第二層誤報、略過累計 3 次和舊句檢查,沒量第一層的擋下次數與重判次數。
- 建議:RETIRE-IF 加「第一層 blocked 次數、每次推送平均重判篇數」。判準寫「`covered` 比例」,不只看略過。

引句:「提醒之後真的去跑判定並記錄的不到三成,提醒形同虛設,是改擋的主因」

引句:「合併主線讓指紋變:本機推送前第一層會要求重判,這是刻意的」

### F4 「只改設定就完整退回 warn」不成立:設定讀到之前的失敗仍然擋,本機與 CI 都一樣

severity: minor
blocking: 否
判準:`LUMOS_SKIP_REREAD_CHECK` 能解本機,但 CI 沒有對應出路,而回退節宣稱的是完整退回。

- spec 段落:〈開關〉末句、〈回傳碼與判不了〉第三類、〈回退〉首句。
- 場景:
  - `_note_reread_check` 在讀設定之前先做範圍終點解析,也就是 `_lens_full_sha`(`scripts/lumos:34943-34953`)。
  - 照 spec 這步失敗歸「判不了」,block 回 1。專案即使寫了 `gate: off` 或 `warn`,這一步也擋。
  - 頂層沒預料的例外同樣照 block 處理。
  - 本機有 `LUMOS_SKIP_REREAD_CHECK` 可繞。CI 那一步沒有略過手段,改設定也解不掉。
- 建議:設定讀到之前的失敗,先用工作樹或 `HEAD` 版設定判斷,或一律照 warn。

引句:「設定讀不到之前就發生的例外,照 block 處理(預設就是 block)」

引句:「兩道都只要把設定改成 warn 就回到提醒(本機與 CI 都讀同一份設定)」

### F5 回退把版本號倒回 v1.2,已升級的消費專案不會被提示更新

severity: major
blocking: 否
判準:整案回退在工具鏈 repo 做得到,但消費端沒有訊號,擋人的 v1.3 會一直留著。

- spec 段落:〈回退〉。
- 場景:
  - 消費專案已 `lumos update`,`CLAUDE.md` 哨兵是 v1.3。工具鏈 revert 後來源回到 v1.2。
  - `_version_nudge` 在「CLAUDE 版本大於或等於來源」時回 None,不提示。file: `scripts/lumos:22274-22305`。
  - 沒有任何訊號叫它們「再 update 一次」。
  - `CHANGELOG` 也會刪掉已對外的 v1.3 段,CHANGELOG 又只記對外放出的版本。
- 建議:回退走前進版本,例如 v1.4 加「撤回」說明,不要倒回 v1.2。

引句:「已經 `lumos update` 的消費專案要再 update 一次才回退」

### F6 空引句、極短引句沒有下限,第二層會把整篇規則類行都算成被點出

severity: major
blocking: 否
判準:行為未定義且朝擋人方向失效,但有略過和設定可退,而且要判定者給出空引句才會發生。

- spec 段落:〈重讀:候選與兩層〉第二層第一、二條,〈照留表態〉。
- 場景:
  - `_note_reread_rows` 讓 `quote` 缺則補空字串,`line` 只驗 1 到筆記行數。判定者行號偏一行指到空行、又沒給引句,記錄的 `text` 就是空行。
  - 照 spec,引句退回整行 `text`,去頭尾空白後是空字串。空字串是任何一行的子字串,所以每條規則類行都被「點出」。
  - 逐條 `drift ack` 也能過,因為判斷用同一個函式。但一篇可能有幾十條,要一條一條表態。
  - 範本寫的是「原句(節錄即可)」,短引句會同時命中別的規則類行。
- 另一方向:改寫過或加了「…」的引句找不到,直接算處理過。這是失效但不擋人的方向,風險較小。
- 建議:定義引句長度下限,空引句或空白行視為點不出。

引句:「引句 = 那一列的 `quote`(去頭尾空白);`quote` 缺或空時退回整行 `text`。」

### F8 spec 新增的兩個數字宣稱沒有查證,其中一個和實際不符

severity: minor
blocking: 否
判準:會誤導上線時程評估,不影響功能。

- 「上線那次推送就要處理一次」:
  - 我用目前樹逐列對過 5 份紀錄共 6 列。4 列的引句已經不在筆記裡。
  - 剩下兩列分別是一般的「白話:」摘要行(`筆記內容閘.md` 第 57 行),以及一條沒帶 `[test:` 的 `WHY:` 行(`存量漂移守衛.md` 第 46 行)。
  - 所以現存的規則類行是 0,不是「要處理一次」。
- 「現在 5 份約 20 KB」:
  - 實測 `wc -c governance/reread-verdicts/*` 共 7855 位元組,約 7.7 KB。
- 治理帳的 18、5、12 和 35 次,我對過是相符的。

引句:「上線前已提交的 5 份紀錄裡點出的規則類行,上線那次推送就要處理一次」

### F9 第二層的出路「改掉那句」會讓已通過的代碼審留痕失效

severity: minor
blocking: 否
判準:不是擋死,但多一輪審查,且 spec 的逃生說明沒提醒順序。

- spec 段落:〈輸出〉第二條。
- 場景:
  - 掛鉤順序是 code-loop check 先、reread 後。高風險推送的代碼審已通過,再被第二層擋下。
  - 按擋下訊息「改掉那句」改筆記,筆記不在簿記白名單,留痕作廢,要重審。file: `scripts/lumos:26909-26913`,簿記只收 `governance/reread-verdicts/` 和 `drift-acks.jsonl`。
  - 手冊 06 第 94 行早就寫了「先重讀、後代碼審留痕」的順序,但新的擋下訊息沒帶這個提醒。
- 建議:擋下訊息在改筆記的選項旁註明會作廢留痕。

引句:「印逃生:第一層 → prepare 指令(派判定者、record、提交);第二層 → 改掉那句」

### F10 以環境變數 `CI` 判斷是否擋第一層,等於一條不留帳的本機繞道

severity: minor
blocking: 否
判準:繞道存在且不被 RETIRE-IF 計入,但需要有人主動設環境變數。

- spec 段落:〈重讀:候選與兩層〉第一層。
- 場景:
  - 本機 `CI=1 git push` 就跳過第一層。
  - 已存在的 `LUMOS_SKIP_REREAD_CHECK` 會記 `skipped-env`,這條不會,RETIRE-IF 的略過累計看不到。
  - 某些容器或代理環境預設就有 `CI` 值,第一層會被靜默關掉。
  - 現有程式也只把 `CI` 當記帳標籤,沒用它改判定。file: `scripts/lumos:34987`。
- 建議:改用明確的旗標(`--ci`)判斷,掛鉤和 CI 各自傳。

引句:「環境變數 `CI` 有值時第一層只印、不擋」

### F11 總開關 off 時舊句檢查也不跑,和現行「各管各的」及即將標廢的 RULE 在顯式設定上不一致

severity: minor
blocking: 否
判準:只影響同時顯式寫了兩個開關的專案,但回退後行為又會變回去。

- spec 段落:〈開關〉第一條。
- 場景:
  - 專案寫了 `gate: off` 加 `old_sentence: block`。
  - 現況:`_drift_check_c` 在 gate off 時印「舊句檢查另有開關…照跑」。file: `scripts/lumos:38738-38745`;`存量漂移守衛.md:82` 的 RULE 也這樣寫。
  - 照 retire 的先例(`rt_mode = ... if mode != "off" else "off"`,`scripts/lumos:38615`),顯式值也會被總開關壓成 off。
  - spec 只寫「總開關 off 時 m1 也不跑」,沒說只對沒寫的情形,還是連顯式值也壓。
- 建議:明講,並補一條對應測試。

引句:「總開關 off 時 m1 照 retire 的先例也不跑」

### F12 判定紀錄沒有汰除機制,任何一份壞檔都會讓所有推送「判不了」

severity: minor
blocking: 否
判準:修法是刪檔再提交,可恢復,但短期內有人踩到會誤認是全面壞掉。

- spec 段落:〈重讀:候選與兩層〉最後一條、〈實務隱患〉第三條。
- 場景:
  - 讀檔要先解析才知道 `note` 欄,所以任何一份讀不懂、超過 256 KB 的檔,都讓所有帶候選的推送判不了。
  - 上限是總量 8 MB,但沒有汰除。第一層的指紋一變就要新增一份紀錄。
  - 估算:18 次推送要判定 47 篇,每份約 1.6 KB。按這個速度約一百週觸到 8 MB,到了就整批判不了。
  - 擋下訊息只說「修好或刪掉」,沒說誰負責清。
- 建議:加保留期限或只讀與候選有關的檔名前綴,並在 REVISIT 加上限接近門檻的提醒。

引句:「每次推送要讀全部判定紀錄找 `note` 欄:現在 5 份約 20 KB」

### F13 掛鉤改成不丟標準錯誤、128 以上停下,和原註解刻意的設計相反

severity: minor
blocking: 否
判準:是取捨,但 spec 沒說明為什麼要推翻原設計。

- spec 段落:〈掛鉤與 CI〉、〈輸出〉第一條。
- 場景:
  - 現行 pre-push 刻意 `2>/dev/null`,理由是舊版工具不認子指令時 argparse 的說明會印在那裡,不給人看雜訊。file: `scripts/hooks/pre-push:531-533`。
  - 現行只有 130 才停下,其他訊號(例如記憶體不夠被砍)照推。file: `scripts/hooks/pre-push:533-541`。
  - 新設計讓 137 這類 128 以上的碼停下整個推送,外部砍掉也會擋。
  - 舊工具搭新掛鉤(或相反)的部分更新狀態,會印一整頁用法說明。
  - 另外,掛鉤和 CI 的註解不准出現筆記內容審的上線字串,spec 沒提醒改寫時要守這條。

引句:「掛鉤那一段不再丟掉標準錯誤」

## 實務隱患鏡頭

- 金流:無。只動檢查的回傳碼,不碰付款或計費。
- 不可逆:大致無。表態檔只追加,紀錄和帳留著對舊版無害。我核對了 `_drift_load_acks` 只收 `_DRIFT_KINDS` 裡的種類(`scripts/lumos:37232`)。舊版 `_note_reread_committed` 只比檔名,也不受影響。唯一例外是 F5 的版本號倒退。
- 對外送出:閘本身不送資料。但第一層要求每次推送都送筆記全文加最多 10 萬字元的程式 diff 給判定模型。F3 顯示這幾乎每次推送都要重送。
- 守衛面:
  - 設定從被推頂端讀,可在同一提交自我解除(spec 已承認)。
  - F10 的 `CI` 環境變數繞道。
  - `drift ack` 的 `--reason` 只要 4 個字以上就過。
- 併行會談:
  - `drift-acks.jsonl` 沒有 union 合併屬性,兩個分支各自追加最後一行會文字衝突。
  - 同號 `seq` 見 F2。
  - 工作目錄裡別的會談留下的未提交紀錄,會被 `drift ack` 讀進 `verdicts`,但無害。
- 可觀測:CI 內的 `blocked` 事件寫在 runner 的帳,不會進版控,RETIRE-IF 的抽樣只看得到本機。

最嚴重的是 F1 和 F2:第一層派不出新項目檔造成死路,以及 reread 併入 BOUND 做不成又沒定義多份紀錄的語意,導致合併後主線 CI 會紅。blocking 共 2 條(F1、F2),其餘 major 為 F3、F5、F6,minor 共 8 條。
