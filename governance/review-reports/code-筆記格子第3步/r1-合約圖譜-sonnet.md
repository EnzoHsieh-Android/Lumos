severity: major

審查範圍:/tmp/code3-r1.patch 全 892 行逐 hunk 讀完。我另把 repo 複製到 `/tmp/rvw3`(它已在 2f9cb94f,含這份變更),跑了 `slots_doctor_reminders`、`slots_retire`、`doctor_soft` 三組子集(33 + 14 + 4 筆)全綠。固定席的 LUMOS-IMPACT 筆記沒有附在派工文字裡(只有一行範圍標頭),所以我自己 grep 了受牽連的筆記來判,見最後一節。

**G1** 新的 S17 在 repo 自己的 doctor 上就有一條誤報,出在本 diff 新寫的筆記行。
- 筆記 `Systems/lumos-cli-read` 的新 WHY 行在敘述文字裡寫了 `[被取代:]`(空值)。`_doctor_replacement_lines` 把它當成「作廢行的接手處」去查,結果判成「寫法認不出」。
- 重現:在 `/tmp/rvw3` 跑 `python3.14 scripts/lumos doctor`,[S17] 印出「Systems/lumos-cli-read.md:14:[被取代:] 寫法認不出(要 [[節點]]、節點路徑#dN 或 無 <理由>)」。
- 原因:`_slot_replacement_dead` 對空值沒有略過。S17 又沒有先確認該行有 `[status:superseded]`,所以任何在敘述裡提到這個鍵名的行都會中。
- 計劃 S13 只要求「指不到或已作廢」才提醒。這是新段落一上線就在自家圖譜製造的噪音。
- 處理方向:空值不判,或 S17 只看有 `[status:superseded]` 的行;並補一支測試。
- 引句:「+  WHY:doctor 接在 S16 後面多三段筆記格子的過期提醒,都不計入問題數、不寫治理帳:S17 作廢行的 [被取代:] 指到的節點或決策不在、或也作廢了(只看一跳,判法照 E3 讀決策);」
- file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:14`、`scripts/lumos:3507`
severity: major
- blocking: 是 — 新增的提醒對本 repo 自己的新筆記誤報,且測試沒涵蓋「敘述文字裡提到鍵名」這條路徑。

**G2** 計劃的 [S13] 條款與〈格子欄位的過期檢查〉表沒跟著改,和程式與綁定測試相反。
- 程式與 `t_slots_doctor_reminders` ⑦ 是「已表態的照 scan 慣例列在『已表態』」,JSON 的 `acked` 為 true,測試也斷言這點。
- 計劃只在分期第 3 步的「進度」行補了說明。[S13]、表格列 137(「已 `drift ack` 的不列」)和列 141(只寫 FACT)都沒改。
- [S13] 是綁了 `[test:t_slots_doctor_reminders]` 的條款,條款字面與綁定測試現在互相矛盾。下一個讀 S13 的人會照字面把「已表態的不列」做回去,把測試弄紅。
- 同類落差:S19 實際掃 FACT/FLOW/DEP,[S13] 與列 141 只寫 FACT,只靠進度行解釋。
- 引句:「+   - 進度(2026-10-02):第 3 步實作中——`drift scan` 多一種 retire(已表態的照 scan 既有慣例列在「已表態」、不算要處理,沒有另開「不列」的規則);」
- file: `docs/lumos-toolchain-knowledge/Projects/筆記格子寫法與過期檢查_計劃.md:137`、`:141`、`:212`
severity: major
- blocking: 是 — 綁定條款的字面與綁它的測試相反,而且條款本文和計劃表格兩處都沒改。

**G3** 程式裡的註解還在說 scan 兜底「還沒接、先不列」,但同一個 hunk 已經把 retire 列進 scan。
- 它是 diff 裡沒動到的上下文行,緊鄰被改的 `_DRIFT_SCAN_KINDS`。
- 引句:「# retire(RULE 撤除條件,筆記格子第 2 步)的 scan 兜底在第 3 步才接,先不列」
- file: `scripts/lumos:30034`
severity: minor
- blocking: 否 — 只是註解過期,行為正確,順手改即可。

**G4** 使用說明書沒補上 retire。
- 技能子檔 `04-自檢與健康.md` 第 10 行描述 `drift scan` 是「五種狀態一致檢查(c1–c5)加條件式回頭條件(probe)全列」。這次多了 retire,也多了 doctor 的 S17、S18、S19,說明書一個字沒提。
- 掃描輸出的標題也從「[回頭條件的問題]」改成「[回頭條件與撤除條件的問題]」。我 grep 了 scripts、skills、docs,沒有別處引用舊標題,這點安全。
- 引句:「+        print(f"[回頭條件與撤除條件的問題] {len(probs)} 處(寫錯、沒帶期限、指不到、寫在不評估的地方、判不了):")」
- file: `skills/lumos-project-notes/commands/04-自檢與健康.md:10`
severity: minor
- blocking: 否 — 說明書落後,不影響行為。

**G5** ⚠ 「doctor 不評估條件」這個既有決定的字面現在和 S18 有張力。
- 程式裡 `_drift_doctor_lines` 的說明是「不評估條件、不跑 git,只讀筆記」。S18 讀治理帳與設定檔,去判 RULE 的度量式撤除條件。
- 計劃列 189 另有「doctor 不評估撤除條件,度量一次只讀一遍」,把度量當成例外,但沒把這個例外寫進 [S14] 的字面。
- 新的 WHY 寫「doctor 照舊不評估條件」,沒限定是 `when-*`,同一節點的 lumos-cli-read 卻寫 doctor S18 判度量成立。兩句並讀會讓人以為互相打架。
- 建議在存量漂移守衛那句改成「doctor 不評估 when-* 條件(度量另走 S18)」。
- 引句:「+  WHY:drift scan 也評估 RULE 的 [retire:when-*](同一支 _drift_probe_scan 換抽取函式,排在回頭條件之後、共用 60 秒預算與同一棵樹),當推送那次判不了或被跳過的兜底;」
- file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:33`
severity: minor
- blocking: 否 — 措辭不精確,行為沒壞。

**G6** ⚠ 遺留四項的 Issue 在第 3 步代碼審之前就標成 done。
- 計劃進度行還寫「實作中」。Issue 內也拿掉了 `REVISIT:2026-10-16`,改成「結案」。
- 若審查折回修改,Issue 已經關了,沒人回頭。
- 引句:「+結案(2026-10-02):四項跟第 3 步一起修了——續行行號擋下、印完才記帳且印出出錯不改判定、兜底條數記 null、記帳的斷言補齊,測試 t_slots_retire_issue_followups。」
- file: `docs/lumos-toolchain-knowledge/Issues/撤除條件檢查末輪遺留四項.md:35`
severity: minor
- blocking: 否 — 狀態可在審過後再改,四項的行為我都驗到了。

**已查過、判不成問題的項目**
- 「不寫治理帳」和 S16 寫 `check-s16` 不衝突。新筆記已寫明理由(同一批每次重唸會變成週報噪音),且 S17、S18、S19 沒有人寫帳。
- 位置紀律:S17、S18、S19 插在 S16 之後、S8 之前。`t_doctor_soft_sections_truncate_by_default` 切的 [S]→[E1] 窗口沒被動到,該測試通過。
- 收尾行的軟段計數:整份 doctor 實跑,「另有 27 段、共 257 條」正常,0 issues。
- 讀指令不寫帳(lumos-cli-read d1):`cmd_drift_scan` 仍不寫帳,沒被弄壞。
- `_gov_tail_bytes` 抽出後,doctor 的帳增速段保留了 `_from` 的語意。
- 推送那支的邊角:`_drift_retire_report` 搬到 try 之外,但 `_gate_event_or_warn` 不拋例外,寫帳不會讓流程崩。印出出錯的兜底、`handle: None` 都有測試釘住。
- 續行行號的擋下:只套用在 `--kind retire`,其他種類不受影響。
- 新寫的 WHY 行格子齊全(出處、因、測試),也沒有寫別人家的路徑。三篇改到的筆記 `lumos lint` 都是 0 問題。
- 效能:三個新函式在本 repo(約 620 篇)各約 0.5、0.16、0.23 秒,可接受。

最高嚴重度 major,blocking 2 條
