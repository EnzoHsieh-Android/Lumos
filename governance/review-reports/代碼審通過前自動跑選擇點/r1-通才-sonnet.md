severity: major

審查範圍:spec 全文逐節讀完,並對照 `scripts/lumos` 的 `_codeloop_pass_gate`、`_codeloop_pass_mech`、`_choice_push_round` 一族、`cmd_choice_kill`、`_choice_kill_base`、`_choice_kill_ledger`、`_gov_rows_at`。交叉引用已核對:`Projects/留痕驗過審查_計劃`、`Android寫法寫完當下自動檢查_計劃`、`改動選擇點都要有需求守住_計劃`(含其 S12 與〈跟代碼審的先後〉)、`Verification/2026-11-15_改動選擇點真實Android端到端驗收`、`Systems/規格閘`、`Systems/pitfalls-code-loop` 都存在。`_gov_event_types_ok` 存在。`_codeloop_pass_choice` 與 `_CHOICE_PASS_SECONDS` 是新增項,現況本來就沒有。

severity: major
blocking: 是(照字面實作,vault-free 專案的 `code-loop pass` 在新增這一道後會直接崩潰)
- spec 段落:〈做法〉圖譜物件
- 問題:spec 只寫「生效日已過、範圍內有 `.kt` 改動時才建 `Env(_vault_in(repo_root))`」,沒有處理 `_vault_in` 回 None(專案沒有 vault)。pass 路徑明確把 vault-free 當成相容邊界:`_codeloop_pass_verify` 在沒有審查帳時直接放行,`_codeloop_guard_verdict` 的波及計算遇到 `_vault_in(...) is None` 回 `no-vault`。照字面實作,有 kotlin-junit 平台、改了 `.kt`、但沒有 `docs/*-knowledge` 的專案,會走到 `Env(None)`,而 `Env.__init__` 呼叫 `load_vault(None)` 會做 `None.rglob`,拋 AttributeError。
- 後果:`code-loop pass` 以 traceback 結束,既不記通過也不記擋下。照現有程式結構,這道位於 `_codeloop_pass_verify` 之前,連原本能通過的 vault-free 專案也被擋死。
- 佐證:file: `scripts/lumos:969`(`Env.__init__` 無條件呼叫 `load_vault`);file: `scripts/lumos:73486`(`_vault_in(repo_root) is None` 的相容邊界);file: `scripts/lumos:73354`(`_codeloop_pass_verify` 對沒有審查帳的處理);file: `scripts/lumos:73375`(`_codeloop_pass_mech`)。
- 引句:「生效日(`_choice_since()`)已過、而且範圍內有 `.kt` 改動時才建 `Env(_vault_in(repo_root))`(建一次約 4.7 秒),否則這一道直接放行。」
- 建議:補上 vault 為 None 就靜默放行,並新增對應條款與測試。

severity: minor
blocking: 否(措辭與文件精度問題,不會做出錯行為;但三個新參數的實作清單不完整,會漏接線)
- spec 段落:〈範圍〉做②、〈做法〉判一次(`label` 參數)
- 問題:spec 說 `label` 是「訊息前綴與範圍說明,預設 `[spec-gate 推送前]`/『推送範圍』」。實際上「推送範圍」這個說明字串是 `_choice_push_range` 回傳的 `how`,不是 `_choice_push_round` 內部組的。`_choice_push_range` 不在 spec 列出的「要穿過 label」的函式清單裡。前綴 `P = "[spec-gate 推送前]"` 也是各函式各寫一份常數,共有 `_choice_push_round`、`_choice_push_scan`、`_choice_push_read`、`_choice_push_verdict`、`_choice_push_unverified` 五處,另有 `_choice_push_part_unverified` 經 `_choice_push_unverified` 傳遞。
- 佐證:file: `scripts/lumos:78632`(`_choice_push_range` 的 `"推送範圍"` 與 `f"推送範圍({why})"`)。`ledger` 的來源讀取則落在 `_choice_push_ledger`(file: `scripts/lumos:78659`)。spec 的穿線清單沒列 `_choice_push_range`,實作時 `how` 的字樣會停在「推送範圍」,與 spec 自己的 `label=(..., "分岔點..HEAD")` 不符。

severity: minor
blocking: 否(只是多印誤導訊息,最終仍會擋下)
- spec 段落:〈做法〉自動跑
- 問題:觸發條件是「第一次判下來有任何擋下原因」。但〈範圍〉做③與 `_choice_push_judge` 的原因集合還包括「表壞」「無規格」「帳不在」「帳讀不了」「不唯一」,以及存活但守的測試沒變(`_choice_kill_pick` 會把它們放進 `carried`、不重跑)。這幾類原因跑 `choice-kill` 都不會改變結果:
  - 「表壞」「無規格」會讓 `choice-kill` 自己在前置檢查印一段 rc 2 的原因再返回,pass 接著再印一次擋下訊息,使用者看到同一件事兩段不同措辭。
  - 「不唯一」「carried 存活」則是白白付一次 Env 建置與 `choice-kill` 的掃描、計劃解析成本。
- 佐證:file: `scripts/lumos:78265`(`_choice_kill_pick` 對 `not_unique` 與 carried survived 的處理);file: `scripts/lumos:78292`(`_choice_kill_base` 的前置檢查)。
- 建議:只在原因含「缺紀錄」「過期」「跑不出結果」,或存活且守的測試雜湊變了時才自動跑。

severity: minor
blocking: 否(耗時風險 spec 已承認,但缺可操作的邊界)
- spec 段落:〈實務隱患〉耗時、〈做法〉自動跑時限
- 問題:`_CHOICE_PASS_SECONDS`=600 只在配方之間檢查,spec 也承認單支基準另算、冷編譯耗時沒量,再加 Env 建置約 4.7 秒、掃描與第二次判定。在對話裡跑 `code-loop pass` 時,前景 Bash 逾時上限是 600 秒,實際耗時很容易超過這個上限。結果是 `code-loop pass` 被工具逾時砍掉,留下 choice-kill 的隔離工作樹與未判完的帳。spec 的〈中斷〉只涵蓋 Ctrl-C,沒有涵蓋被 SIGKILL 的情況。
- 建議:時限預設值要為這幾個固定開銷留餘量,或在手冊明說要放背景跑。

severity: minor
blocking: 否(行為與既有手冊一致,只是 spec 沒講清楚兩份讀取來源不一致)
- spec 段落:〈做法〉判一次、〈實務隱患〉讀工作目錄的帳
- 問題:第二次判定讀「工作目錄的帳」,但放行檔與計劃、守的測試讀 HEAD。`cmd_choice_kill` 自己的挑行(`_choice_kill_ledger`)用的是 `_lint_waivers_load`,讀工作目錄的放行檔。所以放行檔改了、沒提交時:`choice-kill` 認為已放行、不跑,pass 的判定(讀 HEAD)仍擋「存活」。這個情況 spec 沒列為條款;訊息只說「處置後提交」,沒說明為什麼已放行仍被擋。
- 佐證:file: `scripts/lumos:78659`(`_choice_push_waivers` 讀 `at_sha`)與 file: `scripts/lumos:78516`(`_choice_kill_ledger` 內的 `_lint_waivers_load`);skill 與計劃本身已說放行檔要先提交。
- 建議:補一條 S 條款,或在擋下訊息明講「放行檔要提交才算」。

實務隱患鏡頭
- 守衛面:有風險,即第一條 major。擋錯代價是 `code-loop pass` 記不進去,vault-free 這條路徑目前沒有退路。
- 併發與交易:單人使用,不考慮。
- 不可逆:無,擋下時不寫留痕。
- 金流、對外送出:無,spec 已排除,查證屬實。
- 效能:已讀;耗時段見第三條 minor。
- 繞過:`code-loop skip` 仍是現有旁路,spec 明列「不新增略過旗標」,屬於刻意範圍,不算 finding。

最嚴重等級 major,blocking 共 1 條
