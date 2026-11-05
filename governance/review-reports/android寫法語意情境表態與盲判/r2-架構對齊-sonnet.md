severity: major

整體是對齊的:推送前不呼叫模型、先寫治理帳再寫標記檔、事件種類登記進 `LOOP_NOT_CLOSE_EVENTS`、`--branch` 和 `--at-sha` 與 `dispositions` 同旗標、情境題併進既有 `kt` 題表。這些都是第 1 輪「第二套題目表」那條的修法,已折,不重報。以下只列第 2 版新增範圍 8 和其餘新增處。

## 問 1:分層與依賴方向
對齊:
- 情境題併入 `_STACK_QUESTION_SPECS["kt"]` 並一起編譯。
  - file: `scripts/lumos:37448`(題目表,局部 `(?-i:…)` 先例)
  - file: `scripts/lumos:37667`(`_STACK_TRIGGERS` 載入時編譯)
- `android_only` 平台排除走既有路徑。
  - file: `scripts/lumos:37848`
- 核對併進表態那一道。
  - file: `scripts/lumos:70657`(`_dispositions_verdict` 一帶)

跨層疑點(⚠):範圍 8 要「命令的告警不進『新增告警就擋』那一道,改進這一道」,這會讓新增告警閘的結果被表態閘分流。這個機制見問 3 的第一條 finding。

## 問 2:命名與錯誤處理
對齊:
- 事件種類 `blind-judge` 與 `dispositions`、`recall-miss` 同形,去重鑑別子用 `written_at`。
  - file: `scripts/lumos:17003`
  - file: `scripts/lumos:19357`
- 寫入沿用 `_codeloop_dispositions_gov_log`、`_codeloop_write_dispositions` 的「先帳後標記檔、暫存加 `os.replace`」寫法。
  - file: `scripts/lumos:70155`
  - file: `scripts/lumos:70176`
- 讀側「標記優先、退治理帳」同 `_codeloop_read_dispositions`。
  - file: `scripts/lumos:70198`

severity: minor
blocking: 否
引句:「讀表函式 `_kt_decision_table`(新增)跟第二批共用」
- 命名與既有 `_kt_*`、`_STACK_*` 前綴大致對齊。
- 但「型錄讀不到或格式壞 → 不加這一題」與既有退化方向相反,第 1 輪已報過,本版仍是靜默放行。
  - file: `scripts/lumos:38143`(壞的 `stack_questions.gate` 值退回預設、多問)
- 本版新增了「提醒只在 `pitfalls --diff`、表態樣板與 `code-loop check` 碰到 kt 改動時印一行」。這算部分回應,不重列。

## 問 3:第二種做法

severity: major
blocking: 是
引句:「段身分=`sha256(檔路徑 + 規則 id + 命中行前後各 3 行原文)` 前 16 碼」
- 既有新增告警閘已經替每一筆告警算好身分:`_lint_new_key` 取規則、檔案、正規化後的命中片段。放行檔、基準比對都以它為鍵。
  - file: `scripts/lumos:39673`(`_lint_new_key`)
  - file: `scripts/lumos:39698`(`_lint_new_diff_claims`,按次數比差)
  - file: `scripts/lumos:39729`(`_lint_waivers_load`,以 `key` 為鍵)
- 範圍 8 說「新增命中由新增告警閘既有的基準比對算」,又另定一套身分:原文加前後 3 行、不做空白正規化、不含 `_lint_new_key` 的 `~msg~` 退路。同一筆告警從此有兩把鑰匙。
- 範圍 8 同時寫「照新增告警既有的放行指令放行」。`lint-waive` 收的是 `_lint_new_key` 的指紋,盲判記錄卻以段身分為鍵。
  - file: `scripts/lumos:38859`(`lint-waive` 寫入放行檔)
- 計劃沒說放行檔裡的指紋怎麼讓「判 real 就擋」那一道認得。照字面,放行後盲判核對還會繼續擋,出口形同無效。
- 建議:覆核段的身分直接用 `_lint_new_key`,或在記錄裡同時存兩把鑰匙並寫明對照規則,別另起一套。

severity: major
blocking: 是
引句:「命令的告警不進「新增就擋」那一道,改進這一道。」

(原文是「新增告警就擋」,上面的引句是略寫,逐字引句改用下一行。)

引句:「命令的告警不進「新增告警就擋」那一道,改進這一道」
- 既有 `.lumos/lint.json` 以副檔名為鍵宣告命令。命令跑完後所有新增告警一律進同一個 `out["new"]`,由 `_lint_new_classify` 判擋與否。
  - file: `scripts/lumos:40074`(`_lint_new_run_cmds` 把 `base_claims`、`head_claims` 併成一串)
  - file: `scripts/lumos:39827`(`_lint_new_classify`:`hard = bool(out["new"]) …`)
- 告警資料裡沒有「來自哪條命令」這個標記。同一個 `kt` 鍵下加第二條命令後,審查級的命中會混進 `out["new"]` 被當成硬擋。
- 既有只有一個「宣告了但不擋」的降級機制,是 `report_only`,判準是沒有 `{LINT_FILES}` 佔位。
  - file: `scripts/lumos:39319`(`_lint_gate_covers`)
- 範圍 8 等於新增第二種分流,要在這幾個函式裡改。計劃沒寫:靠什麼辨識(命令、規則 id 前綴還是 sgconfig 路徑)、`out` 加哪個欄位、`lint_new` 留痕要不要帶。
- 建議:沿用 `report_only` 同形的 `review_tier` 欄位,在 `_lint_new_run_cmds` 就分流,並把這條寫進計劃。

severity: minor
blocking: 否
引句:「`lumos code-loop situation-waive <段身分> --reason "<理由>"`」
- 計劃說這跟既有新增告警的放行「同一個形狀」。
- 既有 `lint-waive` 有三樣東西,`situation-waive` 都沒有:
  - 放行前問終端是不是人本人(`_waive_origin_tty`);
  - 記錄 `origin: ai|human`;
  - 沒人看過的 AI 放行會在 doctor、推送前小結持續列出,直到 `--ack`。
  - file: `scripts/lumos:38783`
  - file: `scripts/lumos:38805`(`_lint_waiver_ai_unacked`)
- 計劃的隱患節寫「AI 也能自己放行……依單人威脅模型不另防」。不防本身有依據,但「同一個形狀」這句與事實不符。
- 兩條放行路的差別應明寫,或複用 `_waive_origin_tty`,不然下一個人會問為何一邊要 ack、一邊不用。
- 這條偏命名與流程不一致,結構上是複製同形指令,所以判 minor。

severity: minor
blocking: 否 ⚠
引句:「盲判代理判 `{seg, verdict: "real"|"false-positive", reason}`」
- 情境段的盲判結果是 `{seg, row, followed, reason}`。覆核段是 `{seg, verdict, reason}`。兩種結果共用「同一個標記檔、同一個事件種類」,但欄位形狀不同。
- 計劃沒寫標記檔以什麼區分兩類段(`first` 格裡混兩種物件),也沒寫統計怎麼分開。
- 既有 `dispositions` 的格子都是同一個 shape。
  - file: `scripts/lumos:70162`
- 建議:事件裡加 `type` 欄,或覆核段另用 `kind`。

## 問 4:落點

severity: minor
blocking: 否
引句:「宣告方式是專案在 `.lumos/lint.json` 另加一條指向 `sgconfig-review.yml` 的命令」
- `lands_in` 只列棧別提問表態閘、pitfalls-code-loop、kotlin規則包三篇。
- 範圍 8 要改新增告警閘本體(`_lint_new_*`)。這些函式目前掛在 `Systems/pitfalls-code-loop`。
  - file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`(提到 `_lint_new_run_cmds`、`lint-waivers.json`)
- 沒有獨立的新增告警閘節點,所以落在 pitfalls-code-loop 勉強對。但該篇已是最肥的一篇(KEY 20 行),計劃沒說是否另開。
- `sgconfig-review.yml` 和 `rules-review/` 屬於 `Systems/kotlin規則包`。
  - file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:11`
- 該篇現在只寫到 `sgconfig-hints.yml`,還沒寫 `rules-review/`。落點對,但它是工作樹裡尚未提交的改動(`git status` 顯示 `sgconfig-review.yml` 未追蹤),屬計劃自己要補的。

不對齊共 6 條,其中 major 2 條
