severity: minor

我對照了 `scripts/lumos` 裡的鄰居:`_codeloop_pass_mech`、`_codeloop_guard_verdict` 的 `mech_only`、`_choice_push_round` 一族、`_choice_range`、`_gov_rows_at`。結論是沒有第二種做法,也沒有跨層直呼,只有 3 條 minor。

## 1. 分層與依賴方向

大致跟鄰居一致。

- **接點位置**:新增告警與表態兩道的接點在 `_codeloop_pass_gate`,先跑 `_codeloop_pass_mech`,再進 `_codeloop_pass_verify`。file: `scripts/lumos:73396`、`scripts/lumos:73375`。計劃把 `_codeloop_pass_choice` 放在兩者之間,位置合理。
- **判定本體**:`_choice_push_round` 目前只有 `_spec_gate_push_check` 一個呼叫端。file: `scripts/lumos:17448`、`scripts/lumos:78838`。計劃讓 pass 這邊再多一個呼叫端,並加參數分流。這跟 `_codeloop_guard_verdict` 用 `mech_only` 分流是同一種寫法,沒有另寫一套判定。file: `scripts/lumos:79620`。
- **`env` 參數**:`_choice_push_round(env, …)` 的函式本體沒有讀 `env`,計劃傳 `None` 不會出事。
- **範圍**:`_choice_range` 是 `choice-points` 的範圍,內部用 `_push_range_start`,算不出來回原因。file: `scripts/lumos:77837`。計劃拿它當 pass 的範圍,與推送前同一套。
- **帳的來源**:帳讀工作目錄靠 `_gov_rows_at(rev=None)`。file: `scripts/lumos:65600`。既有呼叫端也這樣讀,例如 `scripts/lumos:15415`。計劃沿用。

**finding**
severity: minor
blocking: 否
引句:「新的一道照同形狀接在後面;判定直接重用推送前那一圈 `_choice_push_round`」
- 鄰居的兩道機械檢查是走 `_codeloop_guard_verdict(mech_only=True)`。它用 `kg.hit(..., reason_kind=…)` 收集擋下,再由 `_cl_say_block` 印出。file: `scripts/lumos:79531`、`scripts/lumos:73385`。
- 新的一道改成在 pass gate 層直接呼叫選擇點那一圈,自己印、自己記 `blocks`。這跟鄰居「走 guard verdict 的收集模式」的結構不同。
- 這是在 code-loop 層加一個轉接函式,不算跨層直呼,所以只判 minor。
- 計劃的 `blocks` 要帶新的種類 `choice`。`scripts/lumos:79513` 有註解寫「每種擋下的一句話原因只有推送前掛鉤 pp_cl_reason 那一份」。計劃沒說 `choice` 這個種類要不要補進那份對照。
- ⚠ 請編排者確認:`pp_cl_reason` 缺 `choice` 時,推送前掛鉤是否會漏字或出錯。

## 2. 命名與錯誤處理

**finding 1**
severity: minor
blocking: 否
引句:「多一個欄位 `site: "pass"`;推送那邊不帶這欄」
- 同一個 gate `choice-kill` 的事件裡,「來源」欄位既有叫 `via`。它標驗證結果怎麼來,值是 `run` 或 `_SITUATION_RULE_SOURCE`。file: `scripts/lumos:17971`。
- 其他治理帳事件用 `origin` 或 `scope` 標來源。file: `scripts/lumos:42775`、`scripts/lumos:17719`。
- 全檔沒有任何事件欄位叫 `site`。
- 參數名 `site` 本身沒問題。問題在事件欄位:計劃另造一個名字,而不是沿用 `origin`。
- 結構是對的:仍是 `extra={…}` 加欄位,舊帳沒欄位算推送。

**finding 2**
severity: minor
blocking: 否
引句:「範圍:`_choice_range(rr, None, None)`,也就是 `lumos choice-kill` 不帶 `--diff` 時的同一套」
- `_choice_push_round` 吃的是 `git_range` 加 `push`,內部再呼叫 `_choice_push_range` 重新導出範圍與說明。file: `scripts/lumos:78638`。
- 計劃沒寫 pass 怎麼把 `_choice_range` 的結果餵進去。
- 照字面餵 `A..B` 且 `push=None`,範圍說明會變成「推送範圍」,跟 pass 場合不符。
- `_choice_range` 回原因時「印一行原因、放行」的文字格式,也沒說跟 `P` 前綴那一族是否一致。
- 錯誤處理的方向跟鄰居相同(算不出來放行),只缺接法的描述。

## 3. 第二種做法

沒有引入新做法。

- 以 `site` 把一支判定在 pass 與推送前之間分流,等同 `mech_only` 的「同一支判定、模式參數分流」。
- 工作目錄讀帳是既有的 `rev=None` 模式。
- 擋下記 `code-loop-pass` 的 `blocks`,與 `_codeloop_pass_mech` 同形狀。file: `scripts/lumos:73391`。
- 統計用 `_gov_choice_count_one` 的 `blocked` 分支加一個子計數,是同一種寫法。file: `scripts/lumos:17947`。
- `site` 穿過 7 個私有函式,比 `mech_only` 只在一個函式裡分流更寬。但那些函式是同一族,不判第二種做法。

## 4. 落點

- 規格閘節點現有的 `choice-kill` 說明就在那裡,`_choice_push_round` 也屬於它,選它合理。pitfalls-code-loop 管 `code-loop pass`,選它也合理。
- 兩篇的 `about_code` 都是 `scripts/lumos`。

**finding**
severity: minor
blocking: 否
引句:「lands_in:  - Systems/規格閘  - Systems/pitfalls-code-loop」
- `Systems/測試執行器.md` 與 `Systems/guard-kill.md` 也寫到 `choice-kill`,但不在 lands_in 裡。
- 計劃只改 pass 預判,不改 `choice-kill` 本身,所以多半不用動。
- 只提醒:如果 `gov --stats` 那段或「處置指示」的說明寫在那兩篇,要一併同步。

不對齊共 4 條,其中 major 0 條
