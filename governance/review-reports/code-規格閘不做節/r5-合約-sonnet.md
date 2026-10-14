severity: major

severity: major
blocking: 是 — 新增的「改到的計劃一律重判」檢查,會把一類合法推送擋死,而且它印出的解法做不出來。
引句:「先敲 lumos spec-gate {_sh_quote(Path(prel).stem)},再照它印的指令走輕量設計審」
問題:`_spec_gate_push_nogo_only` 把範圍改到的計劃不論狀態都重判。判成風險低、不做清單略過危險詞、帳上沒有風險低留痕時,就擋並叫人先跑 `lumos spec-gate`。但 spec-gate 的風險低放行要求至少一條新行為,也就是沒標 keeps 的測試要紅。已 done 或已實作完的計劃,測試全綠,所以跑 spec-gate 會 rc1,而且不寫留痕。這條擋下沒有出口,只剩補 `plan_risk: high` 或拿掉危險詞。
具體失敗情境:
- 某份計劃先前因為不做節的「退款」被判風險高(帳上留痕是 high),也就是本功能要修的原始 bug。後來它做完、改成 done,測試全綠。
- 之後任何推送碰到這個檔(改名、`lumos set`、批次改檔),現在判成風險低且略過危險詞,帳上沒有風險低留痕。
- 推送前擋下,叫人跑 spec-gate;spec-gate 因為沒有紅的條款而失敗,擋下的原因永遠消不掉。
- 測試 `t_prepush_nogo_plan_not_skipped` 的 ① 與 ③ 只用「規格閘留痕還在」或「紅測試的 doing 計劃改名」的情境,沒涵蓋這條路。
佐證:程式在 ``scripts/lumos:8852`` 的 `_spec_gate_print_twoway` 與 `_spec_gate_twoway_run_verdict`,要求沒標 keeps 的條款各自紅;擋下訊息在 ``scripts/lumos:9317`` 附近的 `_spec_gate_push_nogo_only`。

severity: minor
blocking: 否 — 手冊與模板的舊說法與新行為有出入,不影響程式判定。
引句:「風險低不派審,這裡是它唯一的閘」
問題:這次只改了 SKILL、reference、templates、05、INDEX,這幾處都有補「不做清單略過危險詞時要一筆輕量審」。下面這幾處仍寫「風險低過了直接實作不派審」,沒帶例外:
- ``AGENTS.md:90``
- ``CLAUDE.md:89``
- ``scripts/templates/graph-discipline.md:87``(會被注入各消費專案,是 session 最先讀到的版本)
- ``docs/lumos-toolchain-knowledge/Systems/規格閘.md`` 的 FLOW 行(PASS(風險低)不派審)
- ``docs/lumos-toolchain-knowledge/Systems/design-loop.md:49``(風險低計劃不會進處置閘(不派審))
- ``docs/心智模型.md:178`` 的圖說「風險低綁上會紅的測試直接實作」
具體失敗情境:新 session 只讀注入的紀律區塊,照「風險低就直接實作」做完,推送時才被輕量審擋下。

severity: minor
blocking: 否 — 能走通,但要手動記帳,手冊沒講。
引句:「ratchet;改了計劃重跑規格閘才會重開」
問題:推送前把 ratchet 和帶輪次紀錄的判定縮到「最近一筆規格閘留痕之後」的窗口,同一個迴圈編號重審就能通過。但 `lumos loop next` 和 `loop status --light` 看的是整個編號的紀錄。窗口前有 major,它回 escalate 並叫人改開「編號-std」。light 上限是 2 筆,通才加架構對齊席已經用掉 2 筆,第二次審就回 cap-reached,而且 `record_cmd` 只在 plant-canary 階段才印。推送前只認不帶 -std 的編號,所以照 loop next 的建議做,推送前永遠找不到那筆審。
具體失敗情境:第一次審後作者改了不做清單並重跑規格閘,再敲 loop next 拿不到記帳範本,只能手寫 `canary record` 旗標。templates.md 只說「照 loop next 印的 record_cmd 記帳」,沒寫這個例外。測試 S19 和 midway_edit 用的是直接 record,沒走 loop next 這一步。
佐證:``scripts/lumos:15963``(escalate)、``scripts/lumos:16021``(cap-reached)。

severity: minor
blocking: 否 — 條款與決策紀錄跟程式有小出入,沒有條款覆蓋這幾條新行為。
引句:「略過了危險詞的計劃每份多一席輕量審(通才加架構對齊席)」
問題:
- d1 trade_offs 寫「通才加架構對齊席」,SKILL.md 第 13 行與 templates.md 寫「派一席通才」,SKILL.md 第 16 行寫「單人+架構對齊席」,三處不一致。程式只要求窗口內有一席非架構對齊、綁好、沒出事的席,所以兩種都放行,但天花板描述不精確。
- r4 新增的行為沒有 [SN] 條款綁測試:shell 引號 `t_nogo_light_cmd_quotes`、欄位型別壞掉回 bad `t_light_gate_fails_bad_types`、超深巢狀行 `t_prepush_nogo_light_deep_nested_line`、NFC 編號 `t_prepush_nogo_light_nfc_loop`、照範本走一次 `t_prepush_nogo_light_review_template_flow`。其中 `template_flow` 正是「合法流程不被擋死」的守衛,卻沒有條款管它。
- 條款 S16 到 S20 與測試一一對上了。

最高等級 major,blocking 1 條。
