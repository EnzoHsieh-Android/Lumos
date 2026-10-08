severity: minor

沒有 blocker 或 major。逐 hunk 讀完整份 diff,也跑過 `scripts/lumos doctor` 和相關測試子集。派工尾端沒有附固定席筆記,只有 `LUMOS-IMPACT: 2f9cb94f..384f4574` 標頭,所以下面「圖譜鏡頭」一節是我用 `lumos impact --diff` 自己列出受影響節點後判的。

**實跑結果**
- repo 自己跑 `lumos doctor --verbose`,rc=0,0 issues。
- S16 仍列 6 條,跟前一版(2f9cb94f)逐條一致,接回續行沒有造成誤報或漏報。
- S17、S18、S19 在 repo 上都是綠色通過,沒有誤報。三段排在 S16 之後、S8 之前,位置紀律沒破。
- 通過的測試:`t_slots_doctor_reminders`(含 `_edges`)、`t_doctor_lists_stale_rules`、`t_doctor_summary_admits_soft_reminders`、`t_doctor_soft_sections_truncate_by_default`、`t_doctor_drift_section`、`t_slots_retire_issue_followups`、`t_slots_retire_when_push`。
- 四篇改到的筆記 `lumos lint` 都是 0 問題。

**findings**

1. 新增的契約子句與 S16 接回續行沒有綁到測試。
severity: minor
blocking: 否 — 行為本身實作了、也有測試,只是測試沒綁進驗收條款,spec-trace 看不到。
引句:「度量符合(暖機、檔尾不夠長、閘關掉時不判;寫法不合的列成提醒不判)」
   - `[S13]` 只綁 `[test:t_slots_doctor_reminders]`。「寫法不合的列成提醒不判」只在新測試 `t_slots_doctor_reminders_edges` 裡斷言。
   - 那支新測試在 docs、skills 全文都沒被任何條款引用(grep 只命中它自己的定義)。
   - S16 改成接回續行,對應的 `⑩` 斷言也只在這支新測試。`[S6]` 綁的 `t_doctor_lists_stale_rules` 沒有續行案例。
   - `[S6]` 的條款字面仍成立,筆記裡沒有任何一句寫過 S16 是逐實體行判,所以沒有說法被推翻。
   - file: `docs/lumos-toolchain-knowledge/Projects/筆記格子寫法與過期檢查_計劃.md:212`
   - 建議:`[S13]` 補綁 `t_slots_doctor_reminders_edges`。

2. S18 外層的 try/except 沒有測試釘住。
severity: minor
blocking: 否 — 只是守衛沒被測試釘住,正常路徑不受影響。
引句:「度量式撤除條件這次算不出來,跳過(fail-open:{type(_e18).__name__})」
   - 我在臨時 clone 把 `except Exception` 改成只接 `ZeroDivisionError`,等於拿掉兜底。`-k t_slots_doctor` 的 27 支全綠。
   - 原因是超大週數的崩潰已經被前置的 `_slot_retire_err` 擋掉,現在沒有任何測試會讓 `_doctor_metric_lines` 丟例外。
   - `Systems/lumos-cli-read` 宣稱「整段包住,算不出來只講一句」,但沒有 `[test:]` 支撐。
   - 建議補一個 monkeypatch 讓 `_doctor_metric_lines` 丟例外的案例,斷言 doctor 不崩。

3. 「先記帳再印」的順序沒有任何測試釘住。
severity: minor
blocking: 否 — 順序只影響「印到一半被中斷」這種窄情境,判定和帳的筆數都不受影響。
引句:「先記帳再印(印到一半被中斷,擋下的那筆帳也已經在;r1 併發資源席)」
   - 我在臨時 clone 把 `_drift_retire_report` 的記帳區塊挪到印出之後。`-k t_slots_retire` 的 34 支全綠,包含 `t_slots_retire_issue_followups` 的 ② 與 ②b。
   - `Systems/存量漂移守衛` 的說法「推送那支 rc 判完就定,先記帳再印」因此只有註解撐著。
   - 建議加一個讓印出丟 `KeyboardInterrupt` 之類不被接住的例外的案例,斷言帳已經在。

4. 計劃裡有兩句沒跟著表格一起改,「doctor 不評估條件」仍是無限定的說法。
severity: minor
blocking: 否 — 表格已經釐清是只指 `when-*`,這兩句是殘留的字面不一致,不會誤導實作。
引句:「不放 doctor——既有決定是 doctor 的漂移段不評估 `when-*` 條件、只讀筆記」
   - diff 把表格列改成限定 `when-*`、並註明「度量另走 doctor」。
   - 同篇「天花板」第 13 條仍寫「doctor 不評估條件(既有決定)」。
   - 同篇「實務隱患/效能」仍寫「doctor 不評估撤除條件,度量一次只讀一遍治理帳檔尾」。這句本身前後矛盾,因為度量就是撤除條件的一種。
   - file: `docs/lumos-toolchain-knowledge/Projects/筆記格子寫法與過期檢查_計劃.md:185`,以及該篇「實務隱患」的效能那一行。
   - `存量漂移防線_計劃` 的 `[S14]` 說 doctor 的漂移段 Z 不評估條件,那是 Z 段,跟 S18 不衝突,不必改。

5. Issue 內文的修法描述與實際做法順序相反,diff 沒有說明為什麼改。
severity: minor
blocking: 否 — 結案句已經寫了實際做法,只是項目 2 的「改法」那句沒更新。
引句:「修法(2026-10-02,跟第 3 步一起):續行行號擋下;rc 判完就定、先記帳再印」
   - 同一篇項目 2 的「改法:記帳挪到印完之後,或兜底只在還沒記過帳時寫」沒改。
   - 實作是先記帳再印,理由只在程式 docstring 裡(印到一半被中斷,擋下的帳要已經在)。
   - 筆記裡看不到為什麼偏離項目 2 提的方向。
   - file: `docs/lumos-toolchain-knowledge/Issues/撤除條件檢查末輪遺留四項.md:28`
   - 建議在修法句補一句理由。

6. ⚠ `_doctor_cfg_bytes` 的「統一」說法略誇大。
severity: minor
blocking: 否 — 純文字範圍問題,doctor 行為沒有因此出錯。
引句:「讀 .lumos/config.json 統一走 _doctor_cfg_bytes(捷徑不跟)」
   - 三處抄本確實都換成 `_doctor_cfg_bytes`,原本的出處(同 `_nodehome_config`、r1、r2 架構對齊席)有保留在新函式 docstring,沒丟。
   - S18 的 `_metric_gate_off("lint-new")` 另走 `_lint_new_config(root)`,自己讀設定,不是這支。
   - 我沒驗證它對捷徑的處理是否同樣嚴,所以標 ⚠。
   - file: `scripts/lumos:3567`

**逐項對照結果,判成立的**
- `[S13]` 子句對照實作與測試:
  - S17 只看標了作廢的行,`⑥--ci` 不跑。
  - S18 的重驗寫法、超大週數與拼錯閘名,均有 `_edges` 測試。
  - 「已表態的列在已表態」有 `⑦` 斷言。
  - S19 照軟段上限(預設 3 條加總數)是程式實況,warn_soft 的軟段計數改成吃完整清單,`t_doctor_summary_admits_soft_reminders` 綠。
- 表格三列與程式一致:retire 列「已 `drift ack` 的照 scan 慣例列在已表態」、`[被取代:]` 列只看作廢行、FACT/FLOW/DEP 列 `--ci` 也跑且上限同 doctor 軟段。
- skill 子檔 `04-自檢與健康.md` 新寫的三句都對得上程式:
  - 給續行行號會被擋(`scripts/lumos:31438`)。
  - scan 的 retire 不列已作廢、已表態的照列。
  - S17、S18 在 `--ci` 不跑,S19 照跑。
- 新筆記行(`lumos-cli-read` 與 `存量漂移守衛` 的 WHY)的 `[出處:]` `[因:]` `[test:]` 格子齊全,沒有用反引號寫別人家的檔,lint 0 問題。
- 增速段改走 `_drift_jsonl_parse`:只在 `\n` 切行,壞行與非物件略過,行為等價且更嚴謹,`⑤` 有斷言。

**圖譜鏡頭:受影響節點逐組判斷(固定席必答)**
- `Systems/lumos-cli-read`(INVARIANT 在 search 預設排除 superseded、context、contracts 等):這份 diff 只動 doctor 的 S16 到 S19 與增速段,不碰那些行為,不影響。這篇自己的 S16 WHY 沒提接回續行,算輕微漏寫,併入 finding 1。
- `Systems/節點範圍與索引守衛`(INVARIANT:新段必須排在 E3 之後、H 之前,軟段只印三條):S17、S18、S19 的位置沒變,`t_doctor_soft_sections_truncate_by_default` 綠。S19 改用 warn_soft 的預設截斷,更貼近該合約,不破壞。
- `Systems/reversibility-governance-ledger` 與 `Systems/存量漂移守衛`(放行不寫帳、doctor 不寫帳、drift-check 閘帳欄位詞):
  - S17 到 S19 不寫帳,符合「doctor Z 段也不寫」的精神。
  - retire 那支只在 `must or unknown` 時記帳,放行不寫帳不變。
  - 記帳與印出各自兜底、不改 rc,帳欄位詞(handle、listed、base_sha)不變,兜底條數改記 null。不破壞合約,順序測試缺口見 finding 3。
- `Projects/存量漂移防線_計劃` `[S14]`(Z 段不評估條件):S18 是另一個 doctor 段,不影響。
- 其餘固定席(`guard-kill`、`bound-tests-gate`、`測試假綠形態`、`design-loop`、`pitfalls-code-loop`、`lumos-cli-lifecycle`、`slim-*` 安裝器等):判不影響。這份 diff 沒碰它們管的指令或機制,只動 doctor 的 S16 到 S19 與增速段、drift retire 的帳與印出順序,以及新增測試。

最高嚴重度 minor,blocking 0 條
