severity: major

# 第 2 輪代碼審・正確性鏡頭(opus)

審材:r2-snapshot.patch(b9ca00bb → e72324b8)。查證用 clone-ns 的 HEAD e72324b8;舊版行為用 `git -C clone-ns show b9ca00bb:scripts/lumos` 取出對照。重現腳本都放在 scratchpad(r2c_*.sh / r2c_*.py),只建 mktemp 目錄,沒動任何 repo。

## F1 「只剝行尾標記」把合約原文結尾的 [鍵:值] 也當成工具標記:settle 會刪掉另一條合約的預告行、還回報轉正成功
severity: major
blocking: 是 — 已重現:settle 回 0、印「✓ 轉正」,但那條預告的合約從家筆記整行消失,沒有對應的正式行
引句:「_GUARD_TAIL_MARKS_RE = re.compile(r"(?:\s*\[[A-Za-z_-]+:[^\]]*\])*\s*")」

1. 行尾那一串的判準是「任何 `[英文鍵:值]`」,不是「工具接上去的 `[test:…]`/`[audit:…]`」。所以只要家筆記已經有一條正式合約,它的原文是「預告這句 + 結尾的 [鍵:值]」,`_guard_formal_line` 就會把它認成預告那句的正式行。這正是題目問的「合約原文本身結尾就是 [鍵:值]」:原文帶標籤的那條被當成比它短的那條。
2. 重現(`r2c_fl.sh`):家筆記 Systems/Pay 原本就有 `KEY:★INVARIANT★ 大額退費要人工核可 [scope:企業戶] [test:t_refund]`(只管企業戶的那條)。接著 `guard plan Systems/Pay "大額退費要人工核可" …` 預告一條管全部帳戶的合約,然後 `guard settle … --test t_refund`。
   - plan 剛做完,`drift scan` 就印 `c5 1`:「家筆記 Systems/Pay 已經是正式合約行——重跑 lumos guard settle 補完」(誤報,那條合約根本還沒做)。
   - settle 走進「正式行已在、預告行也還在」那一支(`_guard_settle_home`),印「已經有同一句的正式合約行,只把重複的預告行拿掉」,再印「✓ 轉正:…預告行已換成正式合約並綁上 [test:t_refund]」,rc=0。
   - 之後 Pay.md 的摘要只剩 `[scope:企業戶]` 那一條;「大額退費要人工核可」這條既沒有預告行,也沒有正式行,守衛紀錄卻是 `status: pass`。
3. 跟上一版比:b9ca00bb 同樣會認錯(剝掉全部標記後相等),但只是把預告行留著。這一輪加的「拿掉預告行」讓認錯的結果從「留一條孤兒預告行」變成「那條合約整句不見」,而且印的是成功。
4. 圖譜:違反 [[Systems/guard-kill]] 的 RULE「做完 `guard settle` 就地轉正」(since/retire/confirmed 2026-09-22 齊全);也是同一篇 PITFALL(2026-09-22 代碼審 r2 blocker)講的同一型坑——合約原文自己帶方括號標籤時,標記和原文分不開——只是這次出在正式行那一側。新寫的 [[Systems/存量漂移守衛]] PITFALL「只能剝行尾那串標記」宣稱已經處理掉這一型,實際還沒處理完。
5. 修法方向(給作者判斷):行尾只認工具會接上去的鍵(`test`、`audit`),其他 `[鍵:值]` 一律算原文。回歸測試 ① 的 `[test:t_manual] [audit:opus/2026-09-20]` 在這個判準下照樣會過。
file: `scripts/lumos:11803`
file: `scripts/lumos:11995`

## F2 status_replay 題:被算成「點到」的那筆發現,同時又被算成一筆誤報(這一輪才出現)
severity: minor
blocking: 否 — 只影響考試的誤報計數,不是推送閘;三條門檻裡沒有誤報這一項
引句:「hit_kind = next((f["kind"] for f in must + listed if f["path"] == note and f["line"] == line), None)」

1. `in_list` 在 status_replay 刻意不要求行號相同(`f["line"] == line or ev == "status_replay"`),但新的 `hit_kind` 要求行號相同。題目那一行不是 status 欄那一行時(例如題目指到 Issue 正文裡「等計劃做完就解了」那一句),`hit_kind` 是 None;`_drift_exam_others` 只排除「行號相同」的那筆,於是 c2 在 status 那一行的那筆發現:讓這題判成「點到」,又被算進 `other_listed`。
2. 重現(`r2c_sr.py`):上一版計劃 doing、Issue open 且正文第 7 行連到計劃;失效提交把計劃改成 done。題目 `{"exam_event":"status_replay","note":"Issues/I.md","line":7,"status_targets":["Projects/P"]}`。新版 `_drift_exam_one` 回 `('點到', 0, 1, 0)`,舊版 b9ca00bb 回 `('點到', 0, 0, 0)`。
3. 現在這份 rtb 考卷的 E1/E2 題目行號剛好就是 status 那一行(第 3 行),所以這次考試的分數沒受影響(實跑 E1 的 1 筆誤報是另一篇 Issue,是真的誤報)。題目行號只要不是 status 那一行,這個計數就會多算。
file: `scripts/lumos:25765`

## F3 plan_refs 對同一份計劃寫了兩種寫法時,c3 與連帶待辦都靜默漏掉(這一輪才出現)
severity: minor
blocking: 否 — 只列出的檢查少列一筆,不會誤擋
引句:「if len(plans) != len({link_target(x) for x in refs}):」

1. 比的是「解出來的筆記有幾篇」和「連結的寫法有幾種」。`[[Projects/退款_計劃]]` 和 `[[退款_計劃]]`(同名只有一篇)解到同一篇:解出來 1 篇,寫法 2 種,判成「有解不出的」→ 回 None。
2. 重現(`r2c_c3.py`,純記憶體):驗證紀錄 pending,plan_refs 兩項如上。計劃 doing 時 `_drift_plan_followups(e, "Projects/退款_計劃.md", "done")` → 新版 `[]`,舊版列出 `('驗證紀錄', 'Verification/V.md', …)`。計劃改成 done 後 `_drift_state_findings` → 新版沒有 c3,舊版有 c3。
3. 這筆也不會出現在「猜不準」那一項,因為 `[[退款_計劃]]` 解得出來、不算 ambiguous,所以是完全沒被列出。`lumos append` 的去重用 `link_target` 做完整比對,兩種寫法不會被當成重複,實際上寫得進去。
4. 比對應該是「每一項都有落點(解出來的,或 ghosts、ambiguous、scalars 裡對得到這個來源和欄位的)」,不是比兩個數字。
file: `scripts/lumos:25217`

## F4 正式行已在時,「預告行有兩條一樣的」被當成「上次做到一半」,settle 回報成功、兩條預告行都留著
severity: minor
blocking: 否 — 要先有手改或合併衝突留下的重複預告行;重現過
引句:「print(f"{home_rel} 已經是正式合約行(上次轉正做到一半),這次只補守衛紀錄")」

1. 新的那一支只看 `_guard_planned_line` 的回傳是不是 None,不分原因。那支在「找不到」「同一句有好幾行預告,分不清是哪一條」「檔打不開」三種情況都回 None。沒有正式行時,同一個錯誤會被擋下(「擋下:…分不清是哪一條」);有正式行時,同一個錯誤卻被當成「做到一半」。
2. 重現(`r2c_dup.sh`):家筆記已有 `KEY:★INVARIANT★ 大額退費要人工核可 [test:t_refund]`,`guard plan` 同一句,再手動把那行預告複製一份。`guard settle … --test t_refund` 印「已經是正式合約行(上次轉正做到一半)」與「✓ 轉正」,rc=0;家筆記留著兩條 `★INVARIANT-PLANNED★`,守衛紀錄是 pass。這兩條預告行就是 r1 修正想消掉的「到期被當逾期」殘留。
3. 圖譜:[[Systems/guard-kill]] PITFALL(設計審 r3 外家席)寫的「第一步做完、第二步失敗時重跑只補第二步」,前提是第一步真的做完;這裡第一步沒有做完。
file: `scripts/lumos:11996`

## F5 doctor Z:全部已表態時照樣印 ⚠「N 項要看」,表態之後這一段永遠不會安靜
severity: minor
blocking: 否 — 只是提醒段的呈現,不影響閘
引句:「out.append(f"[{k}] {_DRIFT_KIND_NAMES[k]}:{nd} 筆都已表態")」

1. `_drift_doctor_lines` 在某一種只剩已表態的筆數時,也回一行,run_doctor 就開 Z 段,並用 `warn_soft` 印成「⚠ 1 項要看(只列出、不擋;某一行確定照留就表態)」。
2. 重現(`r2c_z.sh`):計劃 done、Issue open 並連到它,`drift ack Issues/I 3 --kind c2 --reason …`,再跑 `doctor`,輸出是 `[Z] … ⚠ 1 項要看 … • [c2] 計劃收尾了、連著的 Issue 還開著:1 筆都已表態`。
3. 內部不一致:run_doctor 在 Z 段前的註解寫「全靜默:沒有發現、也沒有要提醒的就整段不印」;提醒文字叫人「確定照留就表態」,但表態完這段還是在,而且照樣算成「要看」。設計第 0 節說 doctor 對已表態的「照列、標已表態」,但沒說只剩已表態的時候要開段、要算成要看。⚠ 設計原意是哪一種判不準;至少「N 項要看」不應該把已表態的算進去。
file: `scripts/lumos:2038`

## 已看,無 finding
- **_guard_formal_line 改成回行索引**:呼叫端只有兩處(`_guard_settle_home`、`_drift_guard_findings` 的 c5),都改成 `is not None`;迴圈從 1 開始,不會回 0 被當成假。`_notelines_regions` 與 `load_raw_for_edit` 都用 `split("\n")` 切行,而且 BOM 和 CRLF 在讀檔時就擋掉了,兩邊的行號對得齊。
- **只看摘要**:regs 用行範圍判,其他欄位裡的同一句不算(回歸 ② 綠)。
- **樹上排序**:`kv[0].split("/")` 逐層比,跟 `sorted(Path)` 在 3.9–3.13 的逐段比一致;rglob 也會讀隱藏資料夾,兩邊收到的筆記是同一批。
- **欄位發現的實際文字、c4 行號**:`_drift_line_text` 和 `cmd_drift_ack` 都是 `split("\n")[ln-1].strip()`,表態鍵對得上;pred 只在那個鍵的值範圍裡找,遇到下一個頂層鍵就停。
- **解不開的筆記**:`_nodehome_list` 回來的路徑已經 nfc,`bad` 和 `touched` 用的是同一種寫法,比對得上;回歸 ⑧⑬ 綠。
- **候選篩選後的 passed/closed**:`only` 用 `pre + nfc 相對路徑`,比對時用 `nfc(p)`;改名時 `git log --name-only -M` 在改名那個提交給的是新路徑,等於頂端的路徑,所以留得住;`_note_status_seq` 是原本逐行搬過去的,`_note_audit_closed_plans` 的行為不變(only/deadline 預設 None)。
- **考試誤報排除規則**:commit 題按「同篇同種」排除是對的(F2 只出在 status_replay 那種寬鬆比對);考卷形狀的先驗和缺欄位略過都沒問題(回歸 ⑦ 綠)。
- **舊理由 alive**:`alive` 來自 `_nodehome_list` 的全部路徑(repo 相對、nfc),表態的路徑也是 repo 相對,比對一致。git 失敗時退回舊行為(照借),方向可以接受。
- **預算**:`_left()` 沒給期限時是 60;逾時後 `max(1, …)` 還留 1 秒給批次讀取;逾時與 git 失敗的訊息分得開。
- 實跑 `python3 scripts/test_lumos.py -k drift_code_review_r1`:18 passed,repo 狀態沒變。實跑 rtb 考卷:擋到 3、點到 3、漏 0,跟 F2 的說明一致。

## 圖譜鏡頭(逐節點)
- [[Systems/guard-kill]] RULE「做完 guard settle 就地轉正」:**會被破壞**,見 F1(合約消失卻回報轉正)。PITFALL「只能剝行尾那一對」:F1 是同一型坑出在正式行那一側。PITFALL「做到一半重跑只補第二步」:F4 讓不是做到一半的情況也走這條路。WHY「settle 改寫四種預告句」:這輪沒動句型比對,不影響。
- [[Systems/存量漂移守衛]]:新的 PITFALL「只剝行尾那串標記」宣稱已經修好,F1 顯示還沒修完;RULE「沒寫設定預設 warn」與 RULE「開關讀被推送頂端」都不影響,這輪沒改設定的讀法;「考試誤報不算同一篇同一種的兄弟句」這一段的描述,在 status_replay 題上跟程式對不上(F2)。
- [[Systems/筆記內容審]] 與 [[Projects/筆記內容審_計劃]]:`_note_audit_closed_plans` 還是呼叫 `_notes_status_flipped`,沒帶 only/deadline,逐提交讀狀態那段是原封不動搬進 `_note_status_seq` 的,收尾計劃的判定不變,不影響。
- `.lumos/lint-waivers.json` 拿掉 `_notes_status_flipped` 那條豁免:函式已經拆短,豁免本來就不需要了,不影響正確性。

最嚴重為 major;會擋的 1 條(F1),另有不擋的 4 條(F2–F5)。
