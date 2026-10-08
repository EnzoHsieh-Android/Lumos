severity: minor

# 第 3 輪(末輪)審查:邊界輸入席(sonnet)

審查範圍:/tmp/code-tail-r3.patch(只有上一輪的修正那一段)。實驗都在臨時目錄做(把 repo 複製一份到暫存區,另用 `35de50ac` 的 `scripts/lumos` 當「修之前」的對照),沒有動 repo、沒有跑會改狀態的 git 指令。

跑過的測試(都在臨時副本、Python 3.14):`-k ns_append` 88 過、`-k ns_nfc_clash` 6 過、`-k gate_event_fit` 3 過、`-k note_audit_dispute_scope` 6 過、`-k note_audit_append` 24 過,全綠。所以下面幾條都不是「測試現在紅」,而是「修法改了行為卻沒被任何測試釘住」或「計劃與程式對不上」。

## 固定席節點

lens.txt 只有前 8 篇附了合約行,其餘 18 篇只列名(超出上限);列名的我用關鍵字掃過(note-shape、舊行尾、relaxed、治理帳),沒命中的判不影響,有命中的下面分組講。

- `Systems/lumos-cli-read.md`(search 預設排除 superseded、不排除 stale):這份 diff 沒碰 search 與濾網。不影響。
- `Systems/bound-tests-gate.md`(code-loop check 對固定席合約綁的測試逐支真跑):diff 只新增、改名測試,沒動 `code-loop check` 的跑法或 `t_bound_tests_g…` 那幾支。新增的 4 條條款([S47]–[S50])與改寫的 [S43]–[S46] 所綁的測試名(`t_ns_append_line_rules`、`t_ns_append_ledger_dedupe`、`t_ns_nfc_clash_errs`、`t_note_audit_dispute_scope`、`t_ns_append_caps`、`t_gate_event_fit_bisect`、`t_note_audit_append_scope_more`、`t_ns_append_r1_minor_folds`)都在 diff 裡有定義,沒有懸空。不影響。
- `Systems/guard-kill.md`(guard kill 的 rc 優先序與 `--json` 純度):diff 沒碰 guard kill 的任何函式。不影響。
- `Systems/授權與歸屬.md`(授權檔不得進 `_VENDORED_TOOLKIT`;`scripts/lumos` 檔頭要有 SPDX 兩行與 MIT 全文):diff 的 `scripts/lumos` 變更都在檔案中段(約 27530 行以後),沒動檔頭,也沒新增會被複製的檔。不影響。
- `Systems/測試假綠形態.md`(還原翻紅釘要配前置斷言,證明被測那條路真的走到):這份 diff 本身就是在補這條(把「沒帶來源的括號」探針換成「舊行就有的行號引用 + 帶來源的括號」並加前置斷言),方向對,七支配對測試我在臨時副本重跑都綠。但修法裡有兩處新程式沒有被翻紅釘住,見 B2、B3;[S43] 的「推送時記 capped」只有直接呼叫記帳函式的測試,沒有走整條路。這條合約的精神在這兩處沒做到,不是被破壞,而是還沒補上。
- `Systems/reversibility-governance-ledger.md`、`Systems/pitfalls-code-loop.md`(風險類,無合約行):治理帳寫入者的登記沒變(仍是 `_gate_event_or_warn`);去重改讀帳不新增寫入者。去重行為與計劃寫的有出入,見 B4。其餘不影響。
- `Systems/design-loop.md`(處置閘第五步,計劃有 [SN] 時條款要綁測試):[S39] 用 `[manual:]`,其餘條款都綁得到存在的測試。不影響。
- 只列名的:`loop-convergence-recording`、`節點範圍與索引守衛`、`doctor-irreversible-hint` 只有零星提到治理帳或 note-shape 字樣,內容與這份 diff 的行為無關;`逃逸自動記_計劃` 提到 relaxed 帳與共用 4 KB 裁法,與 diff 一致(diff 沒改裁法本身)。`規格落成可驗收條件_計劃` 有 12 處提到 note-shape 相關字樣,是條款句式與綁定的規則,這份 diff 的新條款句式([S47]–[S50])照「當…應…」寫、有綁測試,不衝突。其餘 11 篇掃不到相關字樣,不影響。

## Findings

**B1 整行層級規則一律不扣,連「回頭條件格式不合」「條件寫錯」也一起停扣,計劃〈做法〉2 的回頭條件那句沒改,跟程式對不上**
severity: minor
blocking: 否 — 行為偏嚴(只會多擋,不會放過),作者把舊 REVISIT 行修好就能過;問題是計劃與程式互相矛盾、而且沒有測試釘住這個行為變化。
引句:「`_ns_revisit_violations` 對 N 與 O 各算(兩邊都在圍欄外),鍵(規則, 改法);改法只有「條件寫錯」帶錯誤細節,補一個寫錯的條件會照報。」
1. 輸入:起點版本正文有一行舊的 `REVISIT:盡快處理 這件事`(第一個位置不是日期也不是條件標記,屬「回頭條件格式不合」),只在句尾補 `(更正:2026-10-02 改成下週 [來源:人工])`,提交前跑 `note-shape --staged`。
2. 走到:`_ns_append_subtract` 改成 `if v[2] not in _NS_FRAG_KEY_RULES: keep.append(v); continue`,而 `_NS_FRAG_KEY_RULES` 只有「程式行號引用」「釘版本不合法」,`_NS_REVISIT_RULES` 的三條(回頭條件格式不合、條件寫錯、條件寫在不評估的地方)全部落進「整行不扣」。
3. 對照實驗(臨時副本):`35de50ac` 版同一輸入 rc 0(舊行的格式債被扣掉);現行版 rc 1,印 `A.md:18  回頭條件格式不合 REVISIT:盡快處理 這件事(更正:…)`。
4. 壞在哪:diff 裡的計劃第 102 行(上面引句,diff 內是未改動的上下文行)仍寫「回頭條件對 N 與 O 各算、鍵(規則, 改法)」,但同一份計劃第 101 行新寫的是「整行層級的規則一律不扣」,[S47] 又只列 SEE 與「條件寫在不評估的地方」兩種。前兩條回頭條件規則的去向沒人講;`_ns_viol_key` 裡 `_NS_REVISIT_RULES` 那個分支現在是死碼(只有片段規則會走到算鍵);測試也只覆蓋「條件寫在不評估的地方」(`t_ns_append_line_rules` ②),「回頭條件格式不合」「條件寫錯」停扣後的行為沒有測試。⚠ 我判不準作者是有意把這兩條也算整行層級(第 101 行字面「固定改法」可以涵蓋「回頭條件格式不合」),所以只標計劃內部不一致加沒釘住,不標行為錯。

**B2 推送時記 capped 帳的接線沒被任何測試釘住:拿掉 `relaxed["capped"] = pairs.capped` 全套相關測試仍綠**
severity: minor
blocking: 否 — 現行接線實測是對的(見下),只是回歸了沒人知道;屬於測試沒釘住新程式。
引句:「+    relaxed["capped"] = pairs.capped」
1. 現況實測:把 `_NS_APPEND_MAX_FILES` 設成 0 後,對真的 repo 跑 `cmd_note_shape(diff_range=base..tip)`,stderr 印了「候選太多…」一次、治理帳多一筆 `state=capped`、仍照整行擋(rc 1)。接線目前是對的。
2. 翻紅實驗:在臨時副本刪掉 `_ns_relaxed_settle` 裡的 `relaxed["capped"] = pairs.capped` 這一行,跑 `-k ns_append_caps`(5 過)、`-k ns_append_ledger`(10 過)、`-k ns_append_ledger_dedupe`(4 過)、`-k ns_append_r1`(3 過)、`-k ns_append_failure`(3 過),全綠。
3. 壞在哪:[S43] 寫「推送時應記一筆 state capped 的放寬帳」,但 `t_ns_append_caps` ③ 是自己湊一個 `{"capped": True, "by_line": {}}` 直接餵 `_ns_relaxed_record`,中間 `_NotelinesPairs.capped` → `_ns_relaxed_settle` → `relaxed` 容器 → `cmd_note_shape` 這段沒有任何測試走過。上一輪就是因為「探針配不配都紅」才改測試,這一處是同型:測試只驗了終點函式,沒驗接線。

**B3 讀被刪摘要行補上的兩個切法旗標沒有測試釘住:拿掉後相關測試全綠**
severity: minor
blocking: 否 — 旗標只在本機設了 `diff.interHunkContext` 或 `diff.algorithm` 才有差,且讀法已經照 `@@` 計數走,不致錯位;但「跟 `_ns_diff` 一樣」這個宣稱沒有東西守。
引句:「"--inter-hunk-context=0", "--diff-algorithm=myers", "--src-prefix=a/", "--dst-prefix=b/", *args)」
1. 翻紅實驗:在臨時副本把 `_ns_deleted_summary_lines` 裡的這兩個旗標拿掉(只動這一處,`_ns_diff` 不動),跑 `-k notelines_parse_git_config`(4 過)、`-k ns_append_r1`(3 過),全綠。
2. 壞在哪:`t_notelines_parse_git_config`(S30)只量 `_ns_diff` 的輸出;`t_ns_append_r1_minor_folds` ② 用預設設定,看不到旗標有沒有。既有的 PITFALL(新寫 git 呼叫忘了帶旗標,守衛才抓到)就是這型,守衛 `t_lumos_content_diffs_all_disable_external_drivers` 只查外部差異程式的旗標,不查切法旗標。

**B4 同一次推送的放寬帳去重只認(路徑, 行號),兩條分支各自在同一行補不同括號時第二條完全沒記;計劃寫「只多記、不少記」不成立**
severity: minor
blocking: 否 — 帳只用來統計「放寬用了幾次」(RETIRE-IF ②),少記一筆不影響判定;但計劃明講只會多記。
引句:「if d.get("gate") == "note-shape" and d.get("kind") == "relaxed" and d.get("attempt_id") == att[:64]:」
1. 輸入:起點版本 A.md 有一行舊的 `DEP:付款走舊閘道 `src/a.py:3` 還沒換掉`;分支 bx 從起點出發補 `(更正:甲 [來源:人工])`,分支 by 也從起點出發補 `(更正:乙 [來源:人工])`;同一個 `LUMOS_PUSH_ATTEMPT=att-s` 對兩條分支各跑一次 `note-shape --diff 起點..tip`(兩個 rc 都是 0)。
2. 走到:`_ns_relaxed_record` → `_ns_relaxed_recorded` 讀帳,第一條分支記的 `[A.md, 14]` 已在 `seen`;第二條分支的 `by_line` 只有同一個 `(A.md, 14)`,全被濾掉,`fin` 為空,不記。
3. 實測輸出:治理帳只有一筆 `('done', '077eb92', 1)`(bx 的 tip),by 的 tip `3436b62` 沒有任何 relaxed 紀錄;兩條分支的括號內容與終點都不同。
4. 壞在哪:去重鍵沒有帶起點/終點,所以「同一行、不同分支」被當成同一件事。計劃〈做法〉5 只對「`pairs` 被裁掉的行」說「只多記、不少記」,這個場景是少記。另外 `capped`(以及 git-failed/error)那幾種帳不走這個去重,同一次推送逐分支呼叫時每條分支各記一筆,[S48] 只寫了行的去重,沒寫這幾種。

## 沒問題的項目

- NFC/NFD 並存的偵測(`_ns_nfc_clash_errs`):確認吃的是 `_nodehome_list` 第二個回傳值(逐筆 NFC 化、不去重),`t_ns_nfc_clash_errs` ④ 前提斷言在暫存區真的造出兩筆同名並存,⑤ 端到端 rc 1;沒新行或只有一種寫法不擋(②③);空清單、單一路徑都不出錯。`_note_audit_items` 那邊 `items` 空時不多叫一次 `_nodehome_list`。
- 總量上限:篇數、對數、位元組三道都回 `"cap"` 且 `failed` 為假;位元組恰好等於 32 MiB 不算超過(用 `>`);提醒只印一次(`_t` 只在第一次呼叫算);單篇超過 524288 的不計入總和,後面讀的時候自己會回 None,不會被重複計。
- 申訴範圍(`_note_audit_dispute_for`):整行申訴換掉每一種範圍、句尾申訴只換同一句尾、兩種都有取最重、`row.get("tail")` 為 None 時集合退化成 `{None}` 不重複;`t_note_audit_dispute_scope` 六條斷言我逐條對過程式。顯示用語三種分支的順序正確(先判編號有沒有出現,再看項目有沒有 tail)。
- 讀治理帳去重的成本:實測本 repo 的 `docs/.governance-log.jsonl`(16.7 MB、約 10.5 萬行)讀加解析約 0.26 秒;帳檔不存在、是資料夾都落進 `OSError` 回空集合;沒有推送編號時直接回空集合、不讀檔。每條分支多這一次讀,沒有放大。
- 測試的牆上時鐘門檻改成數呼叫次數與相對倍數:`t_gate_event_fit_bisect` 用計數包裝 `_gate_event_build` 驗 ≤ 40 次(二分約 15 次),`t_ns_append_r1_minor_folds` 取三次最快、比 30 倍,本機重跑都綠。
- 配對測試的探針換成「舊行就有的行號引用 + 帶來源的括號」:`t_ns_append_old_line` ①a、`t_ns_append_bypass` ①、`t_ns_append_edits` ①、`t_ns_append_context` ①a/③、`t_ns_append_eol`、`t_ns_append_push_range` ①(前提:起點換成寫完那次時照配)都有前置斷言,證明探針真的在「配得上就扣、配不上就報」兩邊分得開。
- CRLF、檔尾沒換行:`t_ns_append_eol` 兩個情境(CRLF 舊行、檔尾沒換行的最後一行)在新探針下仍配上、不擋,改一個字時照報。
- 計劃/筆記文字:`Systems/筆記內容審.md`、`Systems/筆記內容閘.md`、`否定現況句配回頭條件_計劃`、`筆記內容審_計劃` 的改動與程式一致(skip 比範圍、doctor 與 skip 的 CODE/MIXED 檢查不比範圍、量測程式多算要人工剔除);`skills/.../03-寫回圖譜.md` 那格新增的「候選太多會印提醒」「SEE 行夾句子照報」與程式行為對得上。

總結最高 severity:minor
