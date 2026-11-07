severity: major

## 逐問結果

### 1. 分層與依賴方向

結論:一致,沒有跨層直呼。

- 新碼全落在 `scripts/lumos` 一支檔,這跟鄰居情境題相同。
- `_kt_rule_hits` 對應 `_kt_situation_segments`(`scripts/lumos:39326`)。計劃要求它用 `_codeloop_disp_range` 取範圍、結果快取記在 `~/.cache/lumos/kt-rule-hits/`。這兩點都沿用既有做法:
  - 範圍函式:`scripts/lumos:73997`。
  - 快取走 `_home_cache_read` / `_home_cache_write`:`scripts/lumos:68603`、`68633`。
  - 快取目錄形狀:`scripts/lumos:39315`。
- 表態核對接在 `_pick` 表,和情境題同一個入口:`scripts/lumos:74387`。
- 型錄兩欄用 check.py 的 `main_rows` 讀,等於沿用 `dt_table` 那條從工具鏈來源找型錄的路(`scripts/lumos:38313`),不是新的跨層。
- `--fp-regress` 與 `REVIEW_FP_PREFIX` 的擴充都留在 check.py 內,自成一層:`configs/ast-grep/kotlin-android/check.py:29`、`754`。

唯一的疑點是新增告警閘那一組函式的邊界不清,放在 Q3 的 F2。

### 2. 命名與錯誤處理

題號 `kt-rule-hits`、治理帳欄 `rule_hits`、旗標 `--rule-hits` 與 `--part`,都對得上鄰居的命名(`kt-situation`、`blind_judge`、`--part`,見 `scripts/lumos:77657` 起)。逾時 fail-open、算不出來擋,與 `_kt_sit_verdict_one` 一致(`scripts/lumos:73675`)。下面兩條是結構對、但錯誤處理與出口跟鄰居不同。

## F1 另寫一套「同分支取最後一筆、同 seg 取最新一筆」的讀帳折法(歸在第 3 問)
severity: major
blocking: 是
引句:「同一分支只取最後一筆表態,避免一個分支推多次被數多次」
file: `scripts/lumos:17117-17131`(`_gov_situation_collect` 對作者表態用 `setdefault`,同一段身分只取最早一筆)
file: `scripts/lumos:73844-73866`(`_kt_bj_cells_add` 與 `_kt_bj_fold`,「每格只認第一筆」,折法由核對、寫入前檢查與 gov 三處共用)
file: `scripts/lumos:74176-74177`(寫入端「同一格已有值不算數,整份都是已有的格就不寫、回 2」)

計劃範圍 6 與範圍 4 另訂了兩條折法:
- 統計「同分支取最後一筆表態」。
- 抽查「同一個 seg 有多筆時取最新一筆」(引句:「同一個 seg 有多筆抽查時取最新一筆」)。

鄰居的做法相反:先到先得,重複寫入拒收,而且折法只有一支共用函式。`_gov_situation_collect` 的 docstring 還寫明,以前另寫一份折法就被審查點成問題(「代碼審 r1 架構對齊 F5」)。

計劃沒說要共用 `_kt_bj_fold`,也沒說明為什麼不能先到先得。我把它判成第二種讀帳做法。要過有兩條路:
- 規則命中的事件走同一支折函式,折法參數化。
- 或在計劃裡寫明為什麼這一題要「最新優先」(例如答案允許被作者更新),並指定寫入端的重複處理。

⚠ 交編排者:最新優先可能有正當理由(`--carry` 會更新答案)。但計劃沒寫理由,我只判得出「跟鄰居不同、也沒交代」。

## F2 新增告警閘「那一組函式」的邊界與實際程式對不上
severity: minor
blocking: 否
引句:「那一組函式(`_lint_new_run_cmds` 那一支,抽兩份快照、只回新增)」
file: `scripts/lumos:42664`(`_lint_new_run_cmds` 只跑命令、回 base/head 兩邊的告警,不抽快照)
file: `scripts/lumos:42592-42658`(`_lint_new_tools`;抽快照 `_lint_new_extract` 與補設定 `_lint_new_support` 內嵌在這支,沒有可單獨呼叫的抽快照函式)

計劃說得像有一支現成函式「抽兩份快照、只回新增」,實際沒有。快照、補設定、清暫存目錄 `.lumos/lintbase-*`、`_lint_new_diff_claims` 都散在 `_lint_new_tools`,而且那支還綁著 `waivers`、`oversize` 與 `cfg["budget_sec"]`(超時擋)。

結構上有兩種走法:
- 抽出共用的「兩份快照跑命令取新增」小函式,規則命中與新增告警閘共用。
- 或複製一份快照邏輯(這就會變成第二種做法)。

計劃沒寫選哪種。建議在計劃寫明抽共用,別複製。

## F3 「從 lint.json 推命令」另寫了一條改寫路徑
severity: minor
blocking: 否
引句:「命中題就用同一條命令、把那個參數換成同目錄的 `sgconfig-review.yml` 與 `sgconfig-hints.yml` 各跑一次」
file: `scripts/lumos:41979`(`_lint_new_cmd_targets` 是專案現有的「從 lint.json 推出要跑哪些命令」的函式)
file: `scripts/lumos:42664-42670`(`_lint_gate_covers(cmd)` 決定命令能不能進閘)

目前 `scripts/lumos` 裡完全沒有 `sgconfig` 字樣,核心程式不認識任何規則包檔名。計劃把「認 `--config` 指向 `sgconfig.yml`、換成兄弟檔名」寫進核心。

這跟既有函式做的是不同的事(推命令對改命令),所以我判成 minor,不算第二種做法。但計劃沒說:
- 改寫放在 `_lint_new_cmd_targets` 之內還是另開一支。
- 換完的命令要不要再過 `_lint_gate_covers`。

⚠ 交編排者:這屬於實作細節,設計審階段不一定要定死。

## F4 抽查結果檔「略過一筆、其餘照記」,和鄰居「整份拒收」不同
severity: minor
blocking: 否
引句:「`seg` 不在當下答 `fp` 的命中裡的那一筆略過並印一行,其餘照記」
file: `scripts/lumos:74176-74177`(情境題盲判寫入:整份驗證,形狀不對整份拒收、rc 2)
file: `scripts/lumos:73831-73841`(`_kt_bj_event_ok`:一處不對整筆不算)

計劃是有意不同(解 r2 邊界 5)。但同一個子指令 `blind-judge` 變成兩種錯誤語意,而且結果檔已經依鍵(`segments` 對 `rule_hits`)分流。建議計劃明寫哪種鍵走哪種容錯,寫進手冊,免得使用者以為都一樣。

## F5 誤擋的出口與鄰居不同:答 fp,不走放行檔
severity: minor
blocking: 否
引句:「不新增放行出口:誤擋的出口就是答 `fp`;不寫放行檔」
file: `scripts/lumos:73049`(`_kt_sit_shape` docstring:情境題的誤擋出口是段放行 `lumos lint-waive kt-situation:<段身分>`)
file: `scripts/lumos:4201-4217`(doctor 數「還沒人看過的 AI 放行」,情境段放行共用同一份放行檔與同一套計數)

這是表態題內建的出口,在該題範圍內自洽。但兩種出口並存:
- 新增告警與情境題共用放行檔,doctor 有計數。
- 規則命中題不進放行檔,doctor 看不到。

結構沒壞,只是跟兩個鄰居都不同。建議計劃明寫「這一題的出口不進 doctor 的 AI 放行計數,由 `gov --stats` 的覆核規則段承接」。

### 3. 第二種做法

- 讀帳折法:見 F1(判為第二種做法)。
- 新增告警閘的呼叫邊界:見 F2。
- 命令改寫:見 F3。
- 快取沒有第二套:`kt-rule-hits` 用同一組 `_home_cache_*`,走 `~/.cache/lumos/<子目錄>`。
- 結果檔驗證沒有第二套:仍進治理帳的 `code-loop` 閘、種類 `blind-judge`,舊讀者因缺 `role` 而略過。
- 自檢沒有第二套:誤報樣本沿用 `review-fp-` 前綴,只擴大範圍。

### 4. 落點是否合理

## F6 SKILL.md 與 06 手冊的家不在 lands_in 裡
severity: minor
blocking: 否
引句:「同步改 `skills/lumos-code-loop/SKILL.md` 與 `skills/lumos-project-notes/commands/06-代碼審與推送.md` 的表態段與盲判段」
file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:10`(about_code 列 `skills/lumos-code-loop/SKILL.md`)
file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:12`(about_code 列 `skills/lumos-project-notes/commands/06-代碼審與推送.md`)

鐵則 5 要求「改到的每支檔都得先有家,說明寫進家」。這兩支檔唯一的家是 `Systems/每輪修補差異派工`,計劃的 `lands_in` 沒列它。這樣提交時會被「改程式要寫說明」那道閘點名。建議加列它,或在計劃寫明這兩處只改一句指路、不寫進該節點。

其餘落點判斷如下:
- `scripts/lumos` 的現況說明應寫進 `Systems/棧別提問表態閘`(`about_code` 含 `scripts/lumos`,kt-situation 在那裡有 9 筆,在 `Systems/pitfalls-code-loop` 只有 1 筆)。`Systems/pitfalls-code-loop` 也管 `scripts/lumos`(`:170-171`),列進去不算錯,但主體應在表態閘那篇,不要兩邊各寫一份。
- `check.py` 與 `checks-catalog.md` 的家是 `Systems/kotlin規則包`(`:9`、`:12`),落點對。
- `Systems/linter精選目錄` 只管 detekt 設定檔(`:35-37`),計劃只改它正文的一句範本說明(`:198`),不寫程式說明,可以。
- 不需要另開新節點。

不對齊共 6 條
