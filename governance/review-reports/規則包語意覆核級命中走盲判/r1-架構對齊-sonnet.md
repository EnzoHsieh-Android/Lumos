severity: major

我對照了 `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos` 與 `configs/ast-grep/kotlin-android/check.py`。有 1 條 major(`review` 段放進 lint.json),另有 5 條 minor。

**Finding 1**
severity: major
blocking: 是
- spec 位置:〈範圍〉做 1 把 `review` 段塞進 `.lumos/lint.json`,當成保留鍵,再讓所有讀 lint.json 的地方特判跳過。
- 引句:「其他讀 lint.json 的地方(detekt 提醒、`--smoke`、Android CI 提醒)一律跳過 `review` 鍵,不把它當副檔名」
- 既有做法:專案已經有兩處明寫的共識,非「副檔名→命令清單」的宣告一律不進 lint.json。
  - 依賴層(deps)另開 `.lumos/lint-deps.json`,理由是 r1 架構對齊席指出同一個檔不能混兩種語意。file: `scripts/lumos:41890`
  - 新增告警閘的設定放 `.lumos/config.json` 的 `lint_new`,理由是多一個鍵會讓 lint-check 與 doctor 對每個採用的專案判紅。file: `scripts/lumos:42010`
  - lint-watch 也是同一個理由另開檔。file: `scripts/lumos:41892`
  - 現行驗證器對每個頂層鍵都當成副檔名嚴格驗。file: `scripts/lumos:39607`
- 這是引入第二種做法。spec 〈回退〉自己也承認後果:舊版驗證器看到 `review` 鍵會對消費專案報錯,所以要在驗證器留一行「認得就略過」。這正是上面那兩條共識要避開的坑。
- 建議對齊:宣告改放獨立檔(例如 `.lumos/lint-review.json`),照 `_lint_deps_load` 與 `_lint_new_cmd_targets` 的 deps 路徑做。`_lintcheck_validate` 與 S1 就不必特判,〈回退〉那段也能刪。

**Finding 2**
severity: minor
blocking: 否
- spec 位置:〈範圍〉做 2 與做 5 沒說「盲判判定併進擋停」發生在哪一層。
- 引句:「`_lint_new_classify` 的「有新增就擋」只看一般段」
- 既有做法:`_lint_new_verdict` 與 `_lint_new_classify` 是 `lint-new` 指令、工作樹模式與推送閘共用的純判定。它們沒有 branch,也不讀治理帳。file: `scripts/lumos:42401`
  - 情境題的盲判核對由代碼審那一層讀帳(`_kt_bj_read` 加 `_kt_bj_check`)。file: `scripts/lumos:73712`
  - 新增告警閘在代碼審的步驟是 `_codeloop_lint_new_step`。file: `scripts/lumos:74561`
- spec 若讓 `review_new` 在 `_lint_new_verdict` 內部去讀帳,就是 lint 層直讀 gov 帳的跨層。
- 建議對齊:明寫判定函式只回 `review_new` 與 `review_undone`,「對帳、real 擋、未判擋」放在 `_codeloop_lint_new_step` 這一層,照情境題的分工。S2 指名 `code-loop check` 是對的,範圍 2 和 5 要補這句。

**Finding 3**
severity: minor
blocking: 否
- spec 位置:〈範圍〉做 4 的「材料」,`--template` 當下重跑覆核命令。
- 引句:「資料來源是 `--template` 當下用同一個改動範圍重跑覆核命令」
- 既有做法:現行 `blind-judge --template` 只從 git 讀段材料,不跑任何外部命令。file: `scripts/lumos:74154`
- 風險有兩個。
  - 材料指令得重做 `_lint_new_tools` 內部的基準版與當前版抽檔、暫存目錄與預算這一套。
  - 重跑可能因為預算或逾時,跟推送閘那次算出不同的 seg 集合。
- 建議對齊:把「跑 review 段、算 `review_new`」抽成一支共用函式。推送閘與 `--template` 都呼叫它,不要在 `code-loop` 命令裡複製一份。另外,spec 沒說型錄讀不到時(`_KT_DT_ERR`)規則命中這條路怎麼辦。現行 `_cmd_codeloop_blind_judge` 在 `_KT_DT_ERR` 時整個擋下,該不該連帶擋規則命中要講明。file: `scripts/lumos:74188`

**Finding 4**
severity: minor
blocking: 否
- spec 位置:〈範圍〉做 5 的 `unsure` 仲裁,新增 `--template --unsure`。
- 引句:「`--template --unsure`(本案新增)只印第一判是 `unsure` 的那幾筆」
- 既有做法:盲判材料的「選哪些」已經有模式機制。`--missing` 與 `--disagreements` 是 argparse 的 `store_const`,落在同一個 `cl_bj_mode`,角色由 `mode == "disagreements"` 決定。file: `scripts/lumos:77662`;`scripts/lumos:74140`
- 建議對齊:把 `unsure` 做成第三個互斥模式,走同一個 `mode` 參數與同一條 `role == "arbiter"` 判斷。`_kt_bj_validate` 對仲裁要求「已有第一盲判」的檢查,也要對 `rule_hits` 做一份,不另造旗標路徑。

**Finding 5**
severity: minor
blocking: 否
- spec 位置:〈範圍〉做 4 的「讀型錄主表」。
- 引句:「用 importlib 借 `configs/ast-grep/kotlin-android/check.py` 的 `main_rows`」
- 既有做法:專案載入 check.py 只有一支載入器,即共用的 `_load_hook_file`,它在 `scripts/lumos:38350` 被固定成 `required=("dt_table",)`。`main_rows` 在 check.py 內確實存在。
- 建議對齊:沿用同一次載入的模組,把 `required` 擴成 `("dt_table", "main_rows")`,不要另開一個載入呼叫。
- 補充:spec 的「一條規則只對一列」是靠 2026-11-07 的一次性核對。`main_rows` 遇到重複編號是「後面那列為準」,這個前提沒有機械守衛,建議 S6 或自檢補一條。

**Finding 6**
severity: minor
blocking: 否
- spec 位置:〈用詞〉的「人複查」、〈範圍〉做 5 的 `false` 放行與做 7 的統計。
- 引句:「記帳那一步(`lumos code-loop blind-judge <結果檔>`)替它寫一筆放行」
- 既有做法:同一個 `false` 判定會在兩處留痕,spec 沒說兩邊對不上時誰為準。
  - 治理帳有 `rule_hits` 判定事件。
  - `.lumos/lint-waivers.json` 有一筆 origin ai 的放行。
  - 放行檔的 `_lint_waivers_add` 遇到「指紋已放行過」會直接回失敗。file: `scripts/lumos:42297`
  - 新增告警閘在 `_lint_new_tools` 先用放行檔過濾,被放行的命中到不了 `review_new`。file: `scripts/lumos:42592`
- 另有一個資料源問題:`gov --stats` 目前只讀治理帳(情境段放行來自帳裡的 `sit_waive` 事件),不讀放行檔。file: `scripts/lumos:17606`
  - 現行 `lint-waive --ack` 只改放行檔,不寫帳。file: `scripts/lumos:41192`
  - 做 7 要統計「被人複查幾筆、`overturn` 幾筆」,等於給 `gov --stats` 新增讀放行檔這條路。
- 建議對齊:先定一條規則。擋停以治理帳判定為準,放行檔只當「待人看」佇列。放行檔已有同指紋時,記帳要有明確處理(略過並記帳,不報錯)。人複查的 `--verdict` 同時寫一筆帳,像 `lint-waive` 放行時 `_gate_event_or_warn` 那樣。這樣統計仍只讀帳,也是現行做法。
- 這條要不要升 major,我判不準,標 ⚠ 交編排者。

**總結:** `review` 段放進 lint.json 違反專案已有兩次的共識,要改成獨立檔,這是 major。其餘 5 條是層次與資料源要在 spec 裡寫死:誰讀帳、誰跑命令、`false` 的真相放哪、`--unsure` 與型錄載入沿用既有機制。
