severity: major

席名:合約圖譜-sonnet。立場:接手的人,預設文件與現實對不上。

範圍:規格 S1–S17 逐條對實作與綁定測試、手冊六處到頂句與 templates.md §9、Systems/loop-retro.md 與 Systems/loop-convergence-recording.md、既有行為(沒有人裁紀錄的迴圈)、圖譜固定席。
做過的實測(全在臨時目錄,沒寫真帳):`python3 scripts/test_lumos.py -k t_cap_retro` 155 過 0 敗;`-k loop_next` 98 過 0 敗;另做三個變異(拿掉 retro_skip 三處、從 `_KNOWN_GATES` 拿掉 loop-retro、讓 doctor I2 不列)與四個重現腳本(放在 /private/tmp/claude-501/capr/)。

### F1 過期或沒有回顧時,閘與提示印出的 `--template > cap-retro.json` 會把已寫好、已記的回顧檔整份蓋掉
severity: major
blocking: 是 — 照工具自己印的指令做就毀掉人工補完的回顧檔(資料損壞),過期態正是「檔案存在而且有內容」。
- 輸入:人裁 extra-round → 起草、補完、`--record` → 之後回顧檔被改一個字(指紋過期),問處置閘。
- 走到哪:`_disposal_retro_step` 的 stale 分支先印「改好、--check 過了重新 --record」,下一行就印 `lumos loop retro crx --template > governance/review-reports/crx/cap-retro.json`;同一支 `_cap_retro_template_cmd` 也被 `canary record` 擋點(過期態)、`loop next`(過期態)、doctor I2(過期態)、retro-stats 名單(過期態)原樣印出。
- 壞在哪:`>` 會先截斷目標檔,骨架 JSON 的 `drafted_by`、`families`、`why_cap` 全是空字串,照提示做回顧檔被洗成空骨架。沒有指紋保存舊檔,`--record` 過的內容也沒進治理帳(帳上只有 sha256),無法從帳復原。三個月後的接手者看到「過期」會順手照貼下一行。`--template` 在有人裁但 rc 2(例如沒有席報告)時,shell 也會先建出 0 位元組的 cap-retro.json。
引句:「print(f"    {_cap_retro_template_cmd(root, loop_id)}")」
- 佐證行: `scripts/lumos:13258`(`_cap_retro_template_cmd`)、`scripts/lumos:13321`(`_cap_retro_record_block` 的 `lines.append(f"  怎麼做:{_cap_retro_template_cmd(root, loop_id)}…`)、`scripts/lumos:13326`(`_disposal_retro_step`)
- 重現(已實跑,/private/tmp/claude-501/capr/exp4.py,用測試檔的 `_cr_repo/_cr_loop/_cr_decide/_cr_write_retro`):
  1. `--record` 之後把 cap-retro.json 的「同一族的出口」改成「同一族出口」,`loop status crx --disposal ...` 輸出末段:`[disposal] 跑滿回顧: ✗ — 回顧過期:...` 然後 `lumos loop retro crx --template > governance/review-reports/crx/cap-retro.json`。
  2. 照貼這行:`"起草-乾淨代理" in p.read_text()` 由 True 變 False,檔案變 1187 位元組的空骨架。
- 修法方向(不在本席職責,只指出缺口):stale 與有檔案的 none 態不該印覆蓋指令(改印「檔案已存在,要重產請先備份」或 `--template` 在目標檔存在時拒寫);規格〈二〉與〈三〉沒有講這條。

### F2 到頂提示與手冊六處「先記 cap-decision」對循序單審、light、舊帳也照講,而 cap-decision 對它們一律回 2
severity: minor
blocking: 否 — 擋下訊息講得清楚、不損資料,只是接手者照手冊走會撞牆。
- 輸入:code- 開頭、standard、循序(列不帶輪次)的代碼審,帳上 3 筆未收斂,`loop next --spec ...`。
- 走到哪:階段 cap-reached,新增的 `_cap_retro_next_lines` 無條件第一行印「人裁要破例再開一輪或接受剩下的風險,先記人裁:lumos loop cap-decision code-seq --decision extra-round|accept-risk …」;照做 `cap-decision code-seq` 回 2「不在人裁紀錄的範圍…(light、循序單審、舊迴圈不記)」。
- 壞在哪:規格〈適用範圍〉明講循序、light、舊帳不涵蓋,但〈三〉3 與〈五〉的手冊句都沒有分流;手冊兩處恰好緊接「錨定 standard 的循序 3 筆」「light 2 筆」才講「人裁結果先記 cap-decision」,等於指到必被拒絕的指令。S6 條款本身也沒限範圍,所以測試只用多席迴圈、測不出。
引句:「人裁要破例再開一輪或接受剩下的風險,先記人裁:lumos loop cap-decision」
引句:「人裁結果先記 `cap-decision`,繼續之前先寫跑滿回顧:」
- 佐證行: `skills/lumos-code-loop/reference.md:211`(同段先寫「錨定 standard 的循序 3 筆」);`skills/lumos-design-loop/SKILL.md:65`(同段先寫「light 2 筆」)。
- 重現(已實跑 /private/tmp/claude-501/capr/exp6.py):`loop next code-seq` 印出上述指令,隨後 `cap-decision code-seq --decision extra-round --note …` rc=2。S7 測試(`t_cap_retro_decision_preconditions`)已證 seq 回 2。

### F3 帳壞 + 最新人裁是 accept-risk 時,擋下訊息與圖譜筆記都說可用 `--skip` 出口,實際 `--skip` 解不了
severity: minor
blocking: 否 — 另有出口(修帳、或改記 extra-round),只是訊息講的那條走不通。
- 輸入:人裁 `accept-risk`,審查帳之後有一列輪次不是字串;`retro --skip` 成功(rc 0);再 `canary record --round r4`。
- 走到哪:`_cap_retro_record_block` 的 `if err:` 分支只在 `dec == "extra-round" and state == "skipped"` 才放行,accept-risk 一律回 `cap-ledger-bad`;訊息仍印 skip_cmd 當出口。
- 壞在哪:S17 寫「出口是修帳或 --skip」、S2 寫「--skip 解不了 accept-risk」,兩條在 accept-risk 加帳壞的交集互相矛盾;實作照 S2,但訊息與 `Systems/loop-retro.md` PITFALL(「出口是修帳或 --skip」)照 S17。接手者按訊息 `--skip` 之後再記仍被擋,而且每次再落一筆 `canary blocked`。
引句:「f"  出口:修好審查帳再記;或人裁決定不寫回顧:{skip_cmd}"])」
- 佐證行: `docs/lumos-toolchain-knowledge/Systems/loop-retro.md:22`(PITFALL 帳壞那行「出口是修帳或 --skip」)
- 重現(已實跑 /private/tmp/claude-501/capr/exp2.py,需 `LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26`):skip rc 0 後 `canary record` 仍 rc 2 並印同一句「出口:…--skip」。

### F4 S14 綁的 `t_gov_stats_gate_drift` 驗不到 loop-retro 有沒有登記,也驗不到「loop list 關門判定不受影響」
severity: minor
blocking: 否 — 其他條款的測試(S7 等)會因寫不進帳而紅,風險被間接蓋住;但條款文字本身沒有被它綁的測試驗到。
- 輸入:從 `_KNOWN_GATES` 拿掉 `"loop-retro"`。
- 走到哪:`t_gov_stats_gate_drift` 只掃 `"gate": "字面值"` 與動態寫點數量;新程式走 `_gate_event(root, "loop-retro", ...)` 傳參數,不是字面值。
- 壞在哪:S14 前半「新增 loop-retro 閘名,drift 應維持綠」是空真(該測試本來就不看它);後半「loop list 的關門判定不受這個閘的事件影響」沒有任何測試——`LOOP_CLOSE_EVENTS`/`t_loop_close_kinds_classified` 只看 design-loop、code-loop 兩個閘。
引句:「2026-10-05 審查跑滿回顧:人裁紀錄、回顧已記、跳過」
- 佐證行: `scripts/test_lumos.py:6458`(`t_gov_stats_gate_drift` 全函式)、`scripts/lumos:10316`(`LOOP_CLOSE_EVENTS`)
- 重現(已實跑):複製 scripts/ 到臨時目錄,刪掉 `_KNOWN_GATES` 裡的 `"loop-retro"`,`python3 scripts/test_lumos.py -k t_gov_stats_gate_drift` → 5 passed, 0 failed。

### F5 S5 的測試沒綁住 `loop replay` 三個呼叫點的 `retro_skip=True`;拿掉三處測試仍全綠
severity: minor
blocking: 否 — 產品碼現在是對的;缺口是回歸守衛,合約候選「回放與凍結任一趟印 —」靠這三個參數。
- 輸入:把 `cmd_loop_replay` 裡三處 `retro_skip=True` 全拿掉。
- 走到哪:`t_cap_retro_out_of_scope_not_checked` 直接呼叫 `_loop_status_disposal(..., retro_skip=True)` 驗函式本身,真跑凍結/回放時帳上有 `result_sha256`,第二、三趟的 `spec_sha_override` 有值,第八步靠 override 就印 —,所以三個呼叫點的參數有沒有帶,結果相同。
- 壞在哪:規格〈三〉2 明說「帳上沒有 `result_sha256` 時第二趟的 `spec_sha_override` 會是空的,不能只靠它」,這個情形正是 retro_skip 存在的理由,測試資料沒造它。
引句:「readonly=True, result_out=out, retro_skip=True)   # 第八步(跑滿回顧)凍結不判」
- 佐證行: `scripts/test_lumos.py:69120`(S5 測試的凍結段;帳列由 `_cr_loop` 造、含 result_sha256)
- 重現(已實跑 /private/tmp/claude-501/capr/exp7.py,mut3 是拿掉三處的副本):
  1. 在 mut3 跑 `-k t_cap_retro_out_of_scope_not_checked` → 9 passed, 0 failed。
  2. 造一個帳上列沒有 result_sha256、有人裁紀錄、沒回顧的迴圈:原版 `loop replay crx --freeze` 凍成 `verdict {'rc': 1, 'fails': ['G3', '條款綁定']}`;mut3 凍成 `fails: ['G3', '條款綁定', '跑滿回顧']`——凍結判定被第八步污染,而測試不紅。

---

## 其餘逐條判定(沒有 finding 的部分)

規格條款對實作與測試(逐條):
- S1/S2:`_cap_retro_record_block` 照規格;test 有斷言走到(不寫帳、落事件、同輪第二席、沒人裁迴圈、跳過後放行)。未發現走不到的斷言。
- S3/S4:四態與「早於最新人裁不算」有真跑;S3 還比對其餘七步行相同。
- S5:見 F5(沒人裁、沒資料夾、空資料夾三個分支都有真實斷言;缺口只在呼叫點)。
- S6:有 --json、不合格、合格三態。
- S7:五種不合格與寫不進去都有;寫不進去那支在 root 環境會走「略過」分支(`check(..., True)`),本機非 root 才真測,屬環境限制,不標。
- S8:十四個缺陷逐項點名並檢查「多缺陷逐條列出」;證據正規化三種寫法有驗。
- S9:五種壞檔、retro-stats 與 doctor 不中斷有驗。
- S10/S11/S12/S13/S17:有驗結構化欄位、stdout/stderr 分流、context=null、狀態與閘一致、不計入 issues、非字串輪次與非 UTF-8 兩種帳壞。我用變異讓 doctor I2 不列清單,`t_cap_retro_doctor_lists_missing` 會紅,不是空真。
- S15:只是在測試內重跑六支既有測試並比 FAIL 計數,不是基準比對;`-k loop_next` 另跑 98 過,未見回歸。
- S16:手冊六處(實際改了七個位置:code reference 兩處)、指令速查三列、templates.md §9 都在;指令名、旗標(`--template/--check/--record/--skip --note`、`cap-decision --decision extra-round|accept-risk --note`)、事件名(loop-retro 的 cap-decision/recorded/skipped、canary blocked 三個原因碼)、退出碼(2/1/0)與實作一致。§9 派工詞沒有 avoid/changes/completed_by 欄,有「不要填」明列。附註:§9 給起草者看收貨紀錄(編排者寫的),與「不含編排者結論」有張力,但規格〈五〉明文如此,不標。

圖譜與程式一致性:
- `Systems/loop-retro.md`:指令、事件種類、擋點、凍結不涵蓋第八步、`_retro_has_dossier` 的 PITFALL 都與程式一致;唯一不一致是 F3 那句「出口是修帳或 --skip」。
- `Systems/loop-convergence-recording.md` 新 WHY:原因碼、第八步位置(第七步之後)、三趟印 —、`cap_retro` JSON 欄、retro_skip 理由,與程式一致。
- MOC 已補 loop-retro。

既有行為(沒有人裁紀錄的迴圈):
- `canary record`:不讀治理帳(`_cap_retro_status` 在 di is None 就返回),擋點對它放行;退出碼與寫帳不變。
- 處置閘:rc 與 PASS/FAIL 橫幅不變,但每次多印一行 `[disposal] 跑滿回顧: —(沒有人裁紀錄,不需要回顧)`,凍結/回放輸出也多一行。這是 S5 明文要求,與〈合約候選〉最後一條「行為完全相同」在輸出文字層面有出入;沒找到解析這些行的消費者(skills、hooks 皆無),不標。
- `loop next`:非 cap-reached 路徑不變;cap-reached 階段名與 rc 不變,多印與 `--json` 多 `cap_retro` 欄(S6 要求)。
- 凍結:判定不變,F5 描述的是測試缺口。
- 實測舊版(ce2a961)與新版對同一個「report_path 含 NUL 的絕對路徑」迴圈,處置閘同樣在步驟③丟 ValueError,不是新回歸。

## 圖譜鏡頭(LUMOS-IMPACT: ce2a961..HEAD;固定席逐條)
派工尾端沒有附筆記,我自己跑 `lumos impact --diff ce2a961..HEAD` 取固定席 27 篇,逐條判:
- Issues/canary-record未落盤事件:不影響。新擋點在寫 rec 之前就 rc 2、不印成功行;`_jsonl_append_verified` 讀回驗證路徑沒動。
- Systems/design-loop(★INVARIANT★ 處置閘第五步):不影響。第八步接在第七步之後,第五步的判定與印出沒動;沒有人裁紀錄的迴圈第八步印 — 不入 fails。
- Systems/loop-convergence-recording(RISK·守衛面):已隨本次更新;與程式一致(見上)。
- Systems/canary-audit(★INVARIANT★ record 成功⟺落盤、second 純 telemetry):不影響。擋下發生在寫入前且不印 ✓;`canary second` 路徑沒改,新讀帳函式對 kind 一視同仁、不寫 canary 帳。
- Systems/reversibility-governance-ledger(RISK·守衛面,多寫者鎖 PITFALL):不影響。新事件走既有 `_gate_event` 的 append,沒有新增鎖也沒有宣稱鎖安全;計劃〈實務隱患〉已如實寫「各自 append 一行」。
- Projects/雙向門放行_計劃:不影響。新讀帳函式跟 `_loop_records` 一樣濾掉 kind=spec-gate。
- Projects/規格落成可驗收條件_計劃、Systems/節點範圍與索引守衛:不影響。本計劃每條 S 都有 [test:]/[manual:]、有〈回退〉;新增 loop-retro 筆記已進 MOC;loop-convergence-recording 新增的是 WHY 行不是合約行,不碰 10 條合約門檻。
- Systems/lumos-cli-read(doctor 全圖巡檢):不影響。新增 [I2] 段只用 `warn_soft`,不計 issues(S13 測試驗過)。
- Systems/lumos-cli-lifecycle(★INVARIANT★ re-inject 只覆蓋 sentinel 內):不影響,本次沒動 CLAUDE.md 注入路徑。
- Systems/bound-tests-gate、guard-kill、測試假綠形態、check-r-guard、check-t-sentinel、cochange-guard、doctor-irreversible-hint、lumos-refcheck、lumos-deinit、pitfalls-code-loop、judge-severity-gate、core-invariant-baseline、Projects/逃逸自動記_計劃:不影響。它們的合約都在各自函式或另一組子指令,本 diff 只在 scripts/lumos 新增函式與三個既有函式的尾端/參數;測試假綠形態的「前置斷言證明現場成立」要求,新測試多數有前置斷言(例:`check("S1 前置:人裁記得進去"…)`),F5 是少數沒蓋到的。
- Systems/授權與歸屬(檔頭 SPDX+MIT):不影響,檔頭沒動。
- Systems/slim-get-一行安裝、slim-install-安裝器、slim-uninstall-一行卸載:不影響。slim/ 已凍結、本 diff 不碰 slim/。

總結:最嚴重 major,blocking 1 條
