severity: major

# 第 3 輪 正確性鏡頭(opus)

重現腳本都放在 scratchpad/cr3c/(只 import clone-ns 的 scripts/test_lumos.py 的輔助函式,在 mkdtemp 的臨時圖譜/臨時 git 專案裡跑,沒動任何 repo)。子集 `-k drift_code_review`(30 passed)、`-k guard_settle`(28 passed)在凍結版照綠;rtb 考卷重放結果跟上一版 e72324b8 一模一樣(擋到 3、點到 3、漏 0、誤列 1(E4,計劃已記)、沒誤列 12)。

## F1 settle 的「已有正式行、綁別的測試」分支把「綁了好幾支測試、其中一支就是這支」誤判成別的測試,轉正卡死、照訊息建議做也解不開

severity: major
blocking: 是 — 不該擋卻擋,守衛紀錄轉不了正,到期後逾期會擋推送,唯一出口是 abandon(把其實有測試在守的合約記成不做了)
引句:「if _guard_formal_line(hlines, he, claim, method) is None and _guard_formal_line(hlines, he, claim, None) is not None:」

1. 判「有沒有綁這支測試」用的是 `_guard_formal_line` 裡的字面子字串 `f"[test:{method}]" in tail`(file: `scripts/lumos:11828`),但 `lumos guard bind` 對已有 `[test:…]` 的行是就地併成 `[test:a,b]`(file: `scripts/lumos:12216`)。所以行尾是 `[test:t_a,t_refund]` 時,`_guard_formal_line(…, "t_refund")` 回 None、`(…, None)` 回行號,掉進這輪新加的分支 A,印「綁的是別的測試」。人手寫成 `[test: t_refund]`(TEST_REF_RE 容許冒號後空白)也一樣。
2. 輸入 A(第 1 輪就處理的「同一句先有正式行又被預告一次」情境,只差正式行綁兩支測試):家筆記摘要 `KEY:★INVARIANT★ 大額退費要人工核可 [test:t_a,t_refund]`,`guard plan` 同一句,再 `guard settle <紀錄> --test t_refund`。
   實測:rc 2,stderr「擋下:Systems/Pay.md 已經有同一句的正式合約行、綁的是別的測試;要換測試用 lumos guard bind,這條預告不重複轉正(要不做了走 lumos guard abandon)」,家筆記預告行留著、守衛紀錄仍 pending。上一版這個輸入會走到「只拿掉預告行」那條(第 1 輪修的分支③),現在被分支 A 先攔。照訊息去 `guard bind … t_refund` 會回「已綁 [test:t_refund],無需重綁」,什麼都不變。
3. 輸入 B(做到一半):家筆記已是 `…[test:t_refund]`、守衛紀錄仍 pending(第二步失敗),之後有人 `guard bind Systems/Pay 大額退費要人工核可 t_extra` → 行尾變 `[test:t_refund,t_extra]`;照第二步失敗時印的提示重跑 `guard settle <紀錄> --test t_refund`。
   實測:rc 2,同一句「綁的是別的測試」。這違反筆記宣稱的「settle 第一步做完、第二步失敗時重跑只補第二步」。換成 `--test t_extra` 也一樣回 None(子字串仍對不上),照訊息 bind 任何一支都只會讓清單更長,永遠進分支 A。
4. 重現:`python3 scratchpad/cr3c/r1.py`(兩段都印 `settle rc 2` 加上面那句訊息;A 段印出的家筆記同時留著預告行與 `[test:t_a,t_refund]` 正式行)。
5. 修法方向(不在本報告範圍內驗):判「有沒有綁這支」改用既有的 `invariant_test_refs` / TEST_REF_RE 拆逗號清單比完整名,分支 A 與分支③才分得對。

## F2 c3 拿「解出來幾項」跟「寫了幾種寫法」比,兩邊去重鍵不同:.md 與不帶 .md 混寫時漏列,再加一條解不出/猜不準的連結時反而誤列

severity: minor
blocking: 否 — c3 只列出不擋;但會做出錯的列出判定,也會算進考卷的誤列/漏
引句:「if len(got) != len({link_target(x) for x in refs}):」

1. `got` 來自 build_typed_index 的 fwd,去重鍵是去掉別名與小標題、★保留 .md★ 的字面(file: `scripts/lumos:515`、`scripts/lumos:518`);右邊 `link_target` 會把 .md 去掉(file: `scripts/lumos:224`)。兩邊對「同一份計劃的不同寫法」數法不一樣。
2. 輸入(記憶體 Env,Projects/P 是 done,Verification/V 是 pending):
   - plan_refs 只有 `[[Projects/P]]` → `['c3']`(對照組)
   - `[[Projects/P.md]]` + `[[Projects/P]]` → `[]`:got 兩項、link_target 集合一項,判「有一項解不出」,漏列。上一版(比 `set(fwd)`)這題是列的,這輪修 ⑥ 時換成了這個洞。
   - 上一題再加 `[[Projects/Ghost]]`(不存在)→ `['c3']`:got 2、集合 2,數字剛好相等,Ghost 解不出卻被當成「每一項都解得出」,違反函式說明「有任一項解不出就不算——講不準就不列」。
   - 上一題的 Ghost 換成同名猜不準的 `[[Dup]]`(Projects/Dup 是 doing、Issues/Dup 也在)→ `['c3']`:印「plan_refs 指的計劃都已收尾」,實際上可能指的那份還在 doing。
   - 對照:`[[Projects/P]]` + `[[Projects/Ghost]]` → `[]`(沒有 .md 混寫時照規矩不列)。
3. 同一支也被 `lumos set` 的連帶待辦用(`_drift_plan_followups` 以 override 呼叫),三種錯法一樣會出現在收尾計劃時的清單。
4. 重現:`python3 scratchpad/cr3c/r2.py`,輸出 `a ['c3'] / b [] / c ['c3'] / d ['c3'] / e []`。

## F3 逐提交讀狀態的批次讀失敗改回「算不出」後,筆記內容審是整道放行(連一般新寫的行都不審),不是筆記寫的「完成審跳過」

severity: minor
blocking: 否 — 觸發要 cat-file 批次讀失敗或逾時、或已收尾計劃檔名含換行,少見;筆記內容審本來就是判不了放行,但筆記對放行範圍的描述跟程式不一致
引句:「完成審照既有判不了的規矩跳過並印原因(代碼審 r2 外家席)」

1. `_note_status_seq` 現在批次讀失敗回 None → `_notes_status_flipped` 回 None → `_note_audit_closed_plans` 回 None → `_note_audit_items` 在 `if closed is None: return None` 整支回 None(file: `scripts/lumos:24583`)→ 推送前那道印「git 算不出這次的筆記行,跳過(fail-open)」回 0(file: `scripts/lumos:25108`)。上一版同一個情況只是「沒有狀態翻轉」:完成審那份計劃沒審到,但同一次推送裡其他筆記新寫的行照審。
2. 輸入:臨時 git 專案,起點提交有 Systems/A 與 Projects/P_計劃(doing);下一個提交在 A 新寫 `FACT:新寫的一句現況,函式 foo 回傳 3`、同時把 P_計劃 改成 done。正常時 `_note_audit_items` 列出 P_計劃 的完成審行與 A 的 FACT 行;只讓 `_note_status_seq` 裡那次批次讀回 None 時,整支回 None——A 的 FACT 行也不審了。
3. 重現:`python3 scratchpad/cr3c/r3.py`,輸出第一行列出含 `Systems/A.md … FACT:新寫的一句現況` 的三項,第二行 `計劃歷史那批讀失敗: None`。
4. Systems/筆記內容審 新加的那句要嘛改成「整道判不了、放行」,要嘛讓完成審單獨降級(只丟掉 closed、照審一般新寫的行)。兩種擇一,現在是筆記與程式對不上。

## F4 scan 新增落 degraded 帳,但 scan 的說明還寫「不寫帳」

severity: minor
blocking: 否 — 內部不一致,行為本身照設計 [S2]
引句:「_gate_event_or_warn(root, "drift-check", "degraded", f"scan 判不了 {len(bad)} 篇(不是 UTF-8 或讀不了)")」

1. `cmd_drift_scan` 說明寫「不擋、不寫帳;修復階段產清單、回退時清點用」(file: `scripts/lumos:25700`),這輪在同一支裡加了 degraded 落帳。計劃第 0 節與 [S2] 要的是寫一筆 degraded,所以錯的是說明那句,不是程式。
2. 文字輸出只印 `bad[:10]`,超過 10 篇時沒有「另 N 篇」提示(JSON 的 unknown 是全的)。這點只是順帶一提,不另外列一條。

## 其他重點區塊

- settle 分支③(正式行已在、預告行重複):擋下訊息與不寫檔都正確;「找不到預告行」靠錯誤字串比對分辨,現有三種錯誤訊息裡只有那一種含這幾個字,已看,無 finding(F1 以外)。
- 行尾只認 test/audit/kill:全檔會自動接在合約行尾的只有 bind(file: `scripts/lumos:12220`)、kill-add(file: `scripts/lumos:12324`)、audit(file: `scripts/lumos:12740`)三處,跟正規式一致;`[rollback:]`/`[guard:]` 是人寫在 IRREVERSIBLE/CHECKPOINT 行上的,不在這支比對範圍。已看,無 finding(F1 是綁定名比對,不是剝標記)。
- `_note_status_seq` 拆出的兩支:`_note_base_status` 回 `(status,)` 一元組,起點沒有這篇時是 `(None,)`,跟失敗的 None 分得開;`_to()` 過期後給 1 秒,下一篇之前 `_notes_status_flipped` 會再看預算回 None。已看,無 finding(F3 是呼叫端的放行範圍)。
- status_replay:上一版用自己的圖譜位置、點到的那筆與同篇同種不算誤報;rtb E1/E2 結果與上一版相同。已看,無 finding。
- scan 判不了清單:磁碟那一側靠 load_vault 的「讀檔失敗」、樹那一側靠 undecodable,兩邊都收得到;JSON 多了 unknown。已看,無 finding(F4 以外)。
- doctor Z 全靜默:只剩已表態時整段不開,有未表態時仍附「另 N 筆已表態」。已看,無 finding。

## 圖譜鏡頭

- [[Systems/guard-kill]] RULE(since 2026-09-22、confirmed、retire 齊)「做完 guard settle 就地轉正」與 PITFALL「settle 第一步做完、第二步失敗時重跑只補第二步」:**受 F1 影響**。兩個輸入都寫在 F1,正式行綁多支測試時兩句都不成立。
- [[Systems/存量漂移守衛]] 新 PITFALL「已有同一句的正式行綁別的測試…settle 擋下不猜」:**受 F1 影響**,「別的測試」的判法把「含這支在內的多支」也算進去。第二條 PITFALL(只剝 test/audit/kill)與程式一致;doctor 段的改寫與 `_drift_doctor_lines` 一致;預算那句「最壞比預算多一次呼叫的時間」和新加的逐步預算檢查一致。
- [[Systems/筆記內容審]] 新增的 2026-09-29 那句:**與程式不一致**,見 F3。
- [[Projects/存量漂移防線_計劃]]:c3「講不準就不列」的規格被 F2 的 c、d 兩種輸入違反;scan 記 degraded 符合 [S2];考卷結果與計劃第 218 行的表一致。

總結:最嚴重是 major,要擋的共 1 條(F1),另外 3 條 minor 不擋。
