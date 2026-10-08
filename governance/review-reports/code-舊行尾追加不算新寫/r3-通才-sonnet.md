severity: minor

# 第 3 輪(末輪)通才席報告:筆記形狀擋與筆記內容審「舊行尾補括號」修正段

審的範圍:/tmp/code-tail-r3.patch 全份(1453 行)加 lens.txt。真代碼在 rw 工作樹查證;所有實驗都在 scratchpad 的臨時複本(exp_gen*)做,沒動 repo。
實跑結果:在乾淨複本上 `-k ns_append` 88 項全綠、`-k note_audit` 327 項全綠、`-k nfc`、`-k gate_event`、`disable_external_drivers` 全綠。blocking 級(major 以上)我沒找到;下面三條都是 minor。

## 發現

**U1 整行層級規則一律不扣之後,「回頭條件格式不合」「條件寫錯」也跟著不扣了,但計劃〈做法〉2 還寫著照(規則, 改法)扣**
severity: minor
blocking: 否 — 只影響「舊的壞 REVISIT 行補括號」這一個窄情境,擋下訊息清楚、作者改整行即可;主要是計劃與程式對不上。
引句:「        if v[2] not in _NS_FRAG_KEY_RULES:」
1. 輸入:起點版本有一行不合格式的回頭條件 `REVISIT:盡快處理 這件事`(正文),這次只在句尾補 `(更正:2026-10-02 改成下週 [來源:人工])`。
2. 走到:`_ns_append_subtract` 對違規 `回頭條件格式不合` 命中 `v[2] not in _NS_FRAG_KEY_RULES`,直接 keep,不去比舊行的違規。
3. 壞在哪:實測(臨時複本,用 `_tail_repo(body=old)` 加 `_tail_try`)舊行原封不動時 rc 0,補括號後 rc 1,擋下訊息列出 `A.md:18 回頭條件格式不合`。計劃〈做法〉2 第二條(diff 裡的未改動上下文行)仍寫「`_ns_revisit_violations` 對 N 與 O 各算(兩邊都在圍欄外),鍵(規則, 改法);改法只有「條件寫錯」帶錯誤細節,補一個寫錯的條件會照報」,也就是說明裡回頭條件那組仍是扣的。r2 的理由只點名「SEE 只放連結」「條件寫在不評估的地方」,[S47] 與測試也只測這兩個,沒提 `_NS_REVISIT_RULES` 裡另外兩條(回頭條件格式不合、條件寫錯)一併不扣了。
4. 連帶:`_ns_viol_key` 裡 `if rule in _NS_REVISIT_RULES` 那一支現在只剩算舊行的基數時會走到,新違規端永遠不走,屬於死分支;`t_note_audit_append_scope_more` ③ 還在驗 `_NS_REVISIT_RULES` 的名字,讓這張表看起來仍在用。
5. 要補的:把〈做法〉2 第二條改成與程式一致(回頭條件那組也不扣),並在 [S47] 補一個「舊壞 REVISIT 行補括號照報」的探針;或者反過來承認這組該扣、改程式。兩邊選一邊,現在是矛盾狀態。

**U2 新測試 `t_ns_append_line_rules` 沒有「配對真的成立」的前置斷言,關掉配對照綠;docstring 說的「對照」也不在函式裡**
severity: minor
blocking: 否 — 還原 r1 的做法時這支測試會翻紅(實測),釘得住這次的修法;缺的是測試自己的現場證明,正是上輪才為其他七支測試補的那一類。
引句:「    rc, out = _tail_try(root, summary=see + "(現況:線上已全量切換新閘道 [來源:人工])")」
1. 兩個斷言都是「照報」(`rc == 1 and "SEE 只放連結" in out`、`rc == 1 and "條件寫在不評估的地方" in out`)。整行查本來就報這兩條,所以配對有沒有成立都是紅。
2. 重現(臨時複本 exp_gen2):在 `_notelines_append_pairs` 的 `try:` 之前插入 `return {}, None`(整個配對關掉),跑 `python3.14 scripts/test_lumos.py -k ns_append_line_rules` → `2 passed, 0 failed`。對照(exp_gen3):把 `_ns_append_subtract` 還原成 r1 的「只有現況描述沒寫來源不扣」→ 兩條都 ✗。所以它釘得住「不扣」,但釘不住「現場的配對有成立」。
3. 違反的是 [[Systems/測試假綠形態]] 那條 ★INVARIANT★(還原翻紅釘要配前置斷言證明現場成立)的精神:同一輪其他測試都加了「正常補括號不擋」或「改一個字時照報」的前提,這支漏了。
4. docstring 寫「對照:只扣照片段比的行號引用」,函式本體沒有這一段;補一條「舊行帶行號引用、補括號後引用被扣」的對照(同一個 SEE 或表格列加上 `src/a.py:3`)就能同時解掉前置斷言與 docstring 對不上。

**U3 [S43] 宣稱「推送時 應 記一筆 state capped 的放寬帳」,但從 `_ns_relaxed_settle` 到記帳的那條線沒有任何測試釘住**
severity: minor
blocking: 否 — 我手動跑過整條線是通的(見下),缺的只是機械釘住。
引句:「    m._ns_relaxed_record(root, head, "tipsha", {"capped": True, "by_line": {}})」
1. `t_ns_append_caps` ③ 是手捏一個 `{"capped": True, "by_line": {}}` 直接餵 `_ns_relaxed_record`,沒經過 `_note_shape_eval` → `_ns_relaxed_settle` 設 `relaxed["capped"] = pairs.capped` 這一步。
2. 重現(臨時複本 exp_gen5):把 `_ns_relaxed_settle` 裡的 `relaxed["capped"] = pairs.capped` 改成 `relaxed["capped"] = False`,跑 `-k ns_append` → `88 passed, 0 failed`。也就是 S43 這一半的承諾斷了線測試照綠。
3. 我另外用 in-process 把 `_NS_APPEND_MAX_FILES` 設成 1、兩篇都補括號、跑 `cmd_note_shape(diff_range=...)`:rc 1、stderr 印出提醒、治理帳多一筆 `relaxed/capped`;上限調回後 rc 0、記一筆 `done`。所以現在實作是對的,只是沒被釘住;往後有人動 settle 會無聲壞掉。
4. 補法:加一個走 `cmd_note_shape --diff` 的端到端案例(把 `_NS_APPEND_MAX_FILES` 暫時調成 1),斷言治理帳出現 `state == "capped"`。

## 固定席節點

lens 檔列的節點逐條判斷(只有前 9 篇附了合約行,其餘 11 篇只列名,我沒逐篇讀全文,只就名字與這份 diff 的牽連面判斷):

- `Systems/reversibility-governance-ledger`(家,RISK):這次動到放寬帳的寫入端(新增 `capped` 事件、去重改讀治理帳、`pairs` 清單不變)。`_gate_event_fit` 沒被改,4 KB 裁法與 `pairs_truncated` 旗標不受影響;新增的是「讀」帳(`_gov_tail_bytes` 取檔尾 24 MB),不是新寫入者。實測 24 MB 帳讀完約 0.18 秒、記憶體約 100 MB,不構成新風險。判:不破壞它宣稱的行為。
- `Systems/lumos-cli-read`(INVARIANT:search 預設排除 superseded、不排除 stale):diff 沒碰 `search`。判:不影響。
- `Systems/bound-tests-gate`(INVARIANT:綁定測試逐支真跑):diff 新增的 S43 到 S50 條款綁的測試名(`t_ns_append_caps`、`t_ns_append_ledger_dedupe`、`t_ns_nfc_clash_errs`、`t_ns_append_line_rules`、`t_note_audit_dispute_scope`)都在測試檔裡存在,且實跑皆綠,沒有懸空。判:不影響;但 U3 提到的是「綁了但沒釘住線路」,不是懸空。
- `Systems/guard-kill`(INVARIANT:rc 優先序、--json 純度):diff 沒碰 guard kill。判:不影響。
- `Systems/授權與歸屬`(INVARIANT:LICENSE 不得進白名單、主程式檔頭帶 SPDX 與 MIT):diff 對 `scripts/lumos` 只改函式本體,檔頭不動、沒新增被複製的檔。判:不影響。
- `Systems/測試假綠形態`(INVARIANT:還原翻紅釘要配前置斷言):這是這份 diff 最貼近的一篇。上輪的修法補了七支測試的前置斷言,實跑驗證有效;唯一漏的是新測試 `t_ns_append_line_rules`(見 U2)。判:大部分符合,U2 一處不符。
- `Systems/pitfalls-code-loop`(RISK):diff 沒碰 pitfalls 分級與審查迴圈。判:不影響。
- `Systems/design-loop`(INVARIANT:處置閘第五步,條款定義要綁測試):新增條款 S47 到 S50 都帶 `[test:…]`,S43 到 S46 改寫後仍帶;沒有未綁條款。判:不影響。
- 只列名的 11 篇(lumos-cli-lifecycle、loop-convergence-recording、節點範圍與索引守衛、lumos-deinit、check-t-sentinel、cochange-guard、check-r-guard、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim 三篇與幾篇計劃等):就名字與這份 diff 看,牽連面只有「節點範圍與索引守衛」(它管路徑 NFC 鍵;`_ns_nfc_clash_errs` 的做法與它一致:用不去重的路徑清單數並存),其餘與這次改動無直接關係;沒讀全文,所以只判「沒看到牽連」,不是逐條驗過。

## 沒問題的項目

上輪修法逐項驗過、照預期運作的:

- 只扣照片段比的規則:`_ns_append_subtract` 的行為與 `_NS_FRAG_KEY_RULES` 一致;「SEE 只放連結」「條件寫在不評估的地方」不再借舊行的債(實測還原後翻紅)。
- 總量上限回 "cap":候選篇數、對數、位元組總和三種都能觸發(`t_ns_append_caps` ② 三輪皆驗);提醒每個 `_NotelinesPairs` 物件只印一次;不算 failed、不記 git-failed/error。端到端我手動確認治理帳會記 capped(但測試沒釘,見 U3)。
- NFC 與 NFD 並存:`_ns_nfc_clash_errs` 用 `_nodehome_list` 的第二個回傳值(不去重)數得到並存;第一層(`_note_shape_eval`)與第二層(`_note_audit_items`)都接了,端到端測試 `t_ns_nfc_clash_errs` ④⑤⑥ 在暫存區真的造出兩種寫法並擋下。`skip` 不吞掉這條錯誤(`check` 的 `if not left and not errs: return 0` 仍會擋)。
- 放寬帳去重改讀治理帳:`attempt_id` 欄位名與 `att[:64]` 截法跟 `_gate_event_build` 寫的一致;`_gov_tail_bytes` 讀不到檔回 OSError 被接住;去重只影響記帳、不影響判定。
- 句尾申訴:`_note_audit_dispute_for` 取 {None, 該列 tail} 兩種鍵的最重,`t_note_audit_dispute_scope` ① 到 ⑥ 覆蓋整行 CODE 不被句尾申訴蓋掉、整行申訴換掉每一種範圍、兩者並存取最重、三種顯示用語。
- 讀被刪摘要行補上 `--inter-hunk-context=0` 與 `--diff-algorithm=myers`,`t_lumos_content_diffs_all_disable_external_drivers` 守衛照綠。
- 測試改法:前置斷言版的 `t_ns_append_old_line`、`bypass`、`edits`、`context`、`rename_binary`、`base_read`、`eol`、`push_range` 在乾淨複本都綠;牆上時鐘門檻改成數 `_gate_event_build` 呼叫次數(≤ 40)與相對倍數(< 30 倍),在這台機器上穩定通過。
- 範本版本說明(第 2 版改字發生在第一次推送之前):查 `git log -- scripts/templates/note-audit-judge.md`,改字的提交都在尚未進主線的分支上(merge-base 是 2db51cc4),說法成立。

最高 severity:minor
