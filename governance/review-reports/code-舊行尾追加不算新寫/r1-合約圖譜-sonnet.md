severity: major

我逐 hunk 讀完兩份 diff 和共用規則,並在臨時副本(`scratchpad/mut/`)跑測試與改壞實作。所有被條款綁的測試都存在且綠:`t_ns_append*` 65 條、`t_notelines_parse*` 10 條、`t_note_audit_append*` 17 條,另有範本雜湊釘住、舊句檢查帳預算和來源信任方向三支。問題在同步清單沒做完、一支測試沒有前置斷言,以及一個效能點。

**G1 派工詞升到第 2 版,但計劃〈做法〉8 與 [S39] 要求的驗收和回寫都沒做**
severity: major
blocking: 是 — 筆記內容審自己的 RULE 規定改派工詞要升版並重跑驗收、結果記進計劃,diff 只升了版,沒有回寫。
引句:「- [S39] 派工詞改版後 應 重跑判定者驗收並過關 [manual:照〈做法〉4 判定者驗收那段跑回歸組 68 句與補括號組 9 句」
1. 計劃〈做法〉8 列了要改 `Projects/筆記內容審_計劃`:〈判定者能不能用〉補第 2 版結果一列,〈做法〉判定檔格式補 `tail` 欄。diff 完全沒碰這篇。
2. `_NOTE_AUDIT_PROMPT_VERSION` 升到 2,`t_note_audit_judge_template_pinned` 把新雜湊釘死。`Systems/筆記內容審` 的 RULE 寫「改任何一個字要升版號,並重跑 68 句小實驗、結果記進計劃」。
3. 這個 RULE 有 `[since:]` 和 `[retire:]`,但沒有 `[confirmed:]`,所以只算線索。計劃自己的 [S39] 仍沒有結果。
4. 重現:`grep -n 'tail\|第 2 版\|relaxed' docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md`,在被審的 commit `215da06f` 樹上沒有任何輸出。
5. 後果:判定者拿到的「只判句尾」新指令從沒被驗過,測試只釘雜湊。三個月後的人看到版本 2,找不到驗收依據。
6. ⚠ 計劃狀態是 doing,而且第二層沒接進推送前和 CI(天花板 1),可能是刻意延後。但延後沒有寫在任何地方。

**G2 `t_note_audit_append_failure` 沒有前置斷言,把追加標記整個關掉照綠**
severity: major
blocking: 是 — 違反 `Systems/測試假綠形態` 的 INVARIANT(還原翻紅釘要配前置斷言證明現場成立),而且 [S27] 就綁在這支測試上。
引句:「check("例外:照整行送審(沒有追加段)、不失敗", got is not None and items and not any(it.get("appended") for it in items), got)」
1. 這支測試只斷言「有項目且沒有 `appended`」,沒有先證明不炸時這行會被標。
2. 重現:在副本把 `_note_audit_mark_appended` 開頭改成直接 `return`,跑 `python3.14 scripts/test_lumos.py -k t_note_audit_append_failure`,輸出 `✓ 例外:照整行送審(沒有追加段)、不失敗`、`1 passed, 0 failed`。
3. 同一個改壞下 `t_note_audit_append_marks` 會紅(2 條),所以標記本身有守。缺的是例外路徑到底有沒有走到。
4. 對照:第一層的 `t_ns_append_failure` 有 `state == "error"` 和類別名當前置,沒有這個問題。
5. 預期:先在同一專案不炸一次,斷言有 `appended`,再炸。

**G3 〈做法〉8 的同步清單有多項沒改到,現行字句與程式已經對不上**
severity: minor
blocking: 否 — 說明性字句過期,不影響行為。
引句:「RETIRE-IF ①②③ 從本案上線日起分母少了被放寬的行」
1. `Projects/筆記形狀擋_計劃.md` 第 70 行 [S7] 仍寫「沒違規的放行不寫」,但推送時 relaxed 已是例外。綁它的 `t_note_shape_block_message_and_fail_open` 只改了 docstring。同篇 RETIRE-IF ①②③(第 24 行)沒補分母說明。
2. `Projects/否定現況句配回頭條件_計劃.md` 第 169、196、197 行([S8]、[S9] 與其前的重產步驟)仍寫「判定跟正式工具相同」、「逐行相同」。做法 8 要求補例外,diff 只改了「什麼時候記」那一段。
3. 該計劃〈驗收條款〉開頭仍是「(測試待建,先紅後綠…」,測試已經寫好。
4. 程式 docstring 沒改到的有四處:`cmd_note_audit_record`、`cmd_note_audit_skip`、`_note_audit_render_list`(多印兩行)、`_note_audit_parse_verdict`(只有行內註解提到 `tail`)。
5. 重現:`grep -n '逐行相同\|判定跟正式工具相同' Projects/否定現況句配回頭條件_計劃.md`。

**G4 `_gate_event_fit` 丟清單是平方時間,大清理推送會卡住閘**
severity: minor
blocking: 否 — 需要一次推送裡有數千行被放寬才會明顯,場景存在但不常見。
引句:「+    while rows and size() > 4096:」
1. 每丟一筆就重組並序列化整個事件,對 n 筆 `pairs` 是 O(n²)。
2. 實測:`_gate_event_fit` 傳入 1000、5000、20000 筆 `pairs`,分別 0.16 秒、3.76 秒、58.55 秒,最後都剩 54 筆。
3. 它跑在 `cmd_note_shape --diff`(推送前和 CI)的路徑上。計劃〈實務隱患〉效能段只講了配對,沒量記帳。
4. 預期:先估一次平均每筆長度再一次截斷,或二分。

**G5 條款綁定有兩處測試沒真的驗到條款說的行為**
severity: minor
blocking: 否 — 行為在程式裡有實作,只是沒被測試守住。
引句:「- [S32] 當同一小標題下一字不差的兩行一處是補括號、一處是整行新寫,應 兩處都不標追加段、整行送審」
1. `_note_audit_mark_appended` 的標記條件是「有一處沒配,或配到的舊句不同」。S32 與 `t_note_audit_append_scope` ① 只造了「一處沒配」。
2. 重現:把 `or len(set(olds)) != 1` 刪掉,跑 `-k t_note_audit_append`,仍是 17 passed。
3. [S19] 說「提交前、doctor、跳過逃生口 應 不記帳」,但 `t_ns_append_ledger` ② 的跳過是在提交前模式跑的。該模式本來 `relaxed` 就是 None,所以這一條對跳過路徑沒有區辨力。doctor 完全沒測。
4. 好的一面:我另外改壞七處,測試都紅:
   - 括號上限 300 改 400,`t_ns_append_limits` 紅。
   - 純括號群判定放寬,`t_ns_append_limits` 紅(2 條)。
   - 拿掉圍欄判斷,`t_ns_append_context` 紅。
   - 喚醒口徑改壞,`t_ns_append_wake` ② 紅。
   - 提交前也記帳,`t_ns_append_ledger` 紅(3 條)。
   - 另有兩處(涵蓋規則、片段鍵)的結論見下一點。
5. 涵蓋規則的測試也夠用。片段鍵改成只看規則名後測試仍綠,但追加段永遠接在舊引用之後、掃描順序固定,所以這個改法在行為上等價,不算漏。

**G6 新寫的摘要行有幾處在複述程式碼推得出的細節**
severity: minor
blocking: 否 — 違反 repo 寫筆記規則「程式碼推得出的不寫」,但都帶 `[出處:]`,其中 WHY 行還附了決策脈絡。
引句:「_gate_event_fit 是跨閘共用的 4 KB 裁法」
1. 這句後面括號整段是函式做了什麼:量哪個事件、從哪端丟、記哪個欄、丟光後呼叫誰。這些讀函式就知道。真正程式看不出的只有「不另寫第二支」那半句。
2. `Systems/筆記內容閘` 的 WHY 列了「括號限純括號群、去頭尾空白後 300 字內」。常數在 `_NS_APPEND_MAX_TAIL`,300 一改這行就漂。
3. `Systems/存量漂移守衛` 的 WHY 寫了「nodes 截 20 的條件照舊放在這邊的 then」。
4. 沒有行號引用、沒有未帶來源的 FACT/FLOW/DEP,這部分合規。

**圖譜鏡頭固定席逐條判斷**
- `lumos-cli-read`(search 排除 superseded 不排除 stale):不影響。diff 沒碰 search 或濾網。
- `bound-tests-gate`:不影響。它是 code-loop 對綁定測試逐支真跑。diff 新增的 `[test:]` 全部存在且綠,沒有懸空或偽證據。
- `guard-kill`(rc 優先序、`--json` 純淨):不影響。沒有碰 guard kill 的程式。
- `授權與歸屬`:不影響。主程式檔頭沒動,`scripts/templates/note-audit-judge.md` 只改中段,SPDX 檔頭未動,沒新增被複製的檔。
- `測試假綠形態`:受影響,見 G2。其餘新測試都有前置斷言,例如 `t_notelines_parse_git_config` ③、`t_ns_append_context` ③、`t_ns_append_base_read` ①⑤。
- `reversibility-governance-ledger`:新增的 `_gate_event_fit` WHY 與程式一致,見 G6。「放行不寫帳」那句已補 relaxed 例外,這部分一致。
- `pitfalls-code-loop`:只列名,不影響。
- `design-loop`(處置閘第五步,要求審材是 .md 計劃):不影響,計劃是 `.md` 且有 [SN] 條款。
- 只列名的其他節點:不答。

我另外查過計劃〈做法〉各項對照程式,這些都對得上:
- 配對規則、`_ns_viol_key` 分類、`_ns_relaxed_settle` 口徑、`relaxed` 帳欄位。
- `tail` 欄和涵蓋規則、`skip` 與 doctor 不比範圍。
- 派工詞新段(不含 `{{`、不含大寫 Output)、skill 子檔 `03-寫回圖譜.md` 和 `06-代碼審與推送.md`。
- 新測試沒有寫死行號、版本號或時間。`monkeypatch` 全放在 `finally` 還原,repo 根沒有留下檔案。

最高嚴重度 major,blocking 2 條
