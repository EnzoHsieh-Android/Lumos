severity: minor

這批沒有破壞合約行,也沒有 blocker。圖譜與手冊跟程式一致,但有兩處文件敘述沒有測試守住,另有兩處小的舊說明沒改。

**核對過的事**
- 設計〈實作清單〉第 6、7 點列的文件都改到了,內容也對得上程式:
  - 06 手冊的 `code-loop check` 列、`lumos-code-loop` SKILL、`bound-tests-gate`、`pitfalls-code-loop`、`存量漂移守衛`、`筆記內容閘`、`棧別提問表態閘` 與其計劃、`全repo審視_計劃` #12 的取代註記。
  - `scripts/lumos` 判定函式的「序列早退」註解也改成兩種模式的說明。
- 預演的句子只出現在計劃筆記裡(第二批的設計與 REVISIT),其他七份文件、手冊和程式註解裡都沒有。這符合「這批不含預演指令」。
- 舊測試 `t_prepush_gates_stop_on_signal` 已併進新測試。其餘提到它的圖譜地方都是歷史敘述,沒有 `[test:]` 綁定。
- `t_docs_enumeration_drift` 和 `anchor verify` 通過,`lumos doctor --ci` 的圖譜健康 0 issues。
- 相關 lint 與測試子集也都綠:
  - 六篇改過的筆記 lint 沒有問題。
  - `t_bound_tests_gate`(`bound-tests-gate` 節點的 ★INVARIANT★ 綁定測試)、`guard_kill_rc`(`guard-kill` 的合約)、`code_loop_check`、`keep_going` 都綠。
  - `prepush_cheap_gates`、`prepush_and_ci_wire`、`prepush_new_branch_block`、`prepush_hook_calls_spec`、`prepush_stops_without` 也都綠。
- 整組 `-k prepush` 全套跑超過 9 分鐘,我中途停掉沒等結果。

**破壞測試(在複本裡改掛鉤與 `scripts/lumos`)**
- 把掛鉤彙總裡的裁判簽名提示句改掉或拿掉,新增的 6 支測試仍全綠。
- 把代碼審「審查」種類的對照表原因句換成別的字,同樣全綠。
- 把「取最後一行」改成取第一行,同樣全綠。

severity: minor
blocking: 否 — 只是提示句沒被測試釘住,不影響擋或放。
引句:「彙總裡有它時最前面多一行講明代碼審與雙向門放行這次跑的測試用的是沒簽名的測試檔」
問題:`bound-tests-gate` 把這句 WHY 綁在 `t_prepush_each_gate_blocks_alone`,但沒有任何測試斷言這句提示。
失敗情境:有人改壞或刪掉 `_PUSH_SUMMARY_ANCHOR_NOTE` 或掛鉤簡版彙總那一行,測試全綠。使用者就不會被告知「代碼審與雙向門放行的綠燈這次不算數」。
佐證:``file: `scripts/lumos:47516` ``、``file: `scripts/hooks/pre-push:126` ``。

severity: minor
blocking: 否 — 影響的是彙總裡的原因文字,不影響回 1。
引句:「原因用掛鉤寫死的對照表,查不到用通用句」
問題:`pitfalls-code-loop` 那條 WHY 綁 `t_prepush_mixed_versions`,但沒有測試比對對照表四種原因的文字。「有多行取最後一行」這條規則也沒被測試驗到,因為假 lumos 永遠只印一行 `LUMOS-BLOCKS:`。
失敗情境:`pp_cl_reason` 的種類與句子對錯位,例如審查顯示成表態不完整,彙總會講錯原因,測試仍綠。取第一行而不是最後一行也不會被抓到。
佐證:``file: `scripts/hooks/pre-push:134` ``、``file: `scripts/hooks/pre-push:559` ``。

severity: minor
blocking: 否 — 只影響手冊找指令的入口。
引句:「各道的處理方式在上面各自那一段」
問題:06 手冊新增了 `push-summary` 的一列,`reference.md` 的子命令全覽也列了它。但 `commands/INDEX.md` 第 38 行的 06 路由清單列了 `push-range`、`ci-status`,卻沒有 `push-summary`。設計第 4 點要求把它登記進說明表。
失敗情境:只看 INDEX 找路由的人找不到這個指令。
佐證:``file: `skills/lumos-project-notes/commands/INDEX.md:38` ``。

severity: minor
blocking: 否 — 屬註解與標籤的小處漂移。
引句:「陷阱裡不 exit(舊寫法)→ ⑤⑥⑦紅」
問題:
- `t_prepush_interrupt_stops_every_gate` 的翻紅釘寫 ⑤⑥⑦,實際只有 ④⑤⑧三組斷言,標籤對不上。
- 掛鉤建暫存目錄處的註解還寫「高風險那條路 rc1 會直接 exit 1」,現在已改成記下、統一在判斷點才 `exit 1`。
- `anchor-integrity.md` 第 56 行和 `每支檔有家.md` 第 24 行的「rc1 擋」沒補收集語意。計劃第 6 點沒列這兩份,大意仍成立。

失敗情境:下個人照這些舊說明找翻紅點或理解流程時會被誤導。
佐證:``file: `scripts/test_lumos.py:64555` ``、``file: `scripts/hooks/pre-push:288` ``。

最高等級 minor,共 4 條,blocking 0 條。
