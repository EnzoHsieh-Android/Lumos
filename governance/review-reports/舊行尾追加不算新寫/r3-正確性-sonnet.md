severity: major

前輪修復清單逐項驗收:
- 第 1 項:到位。唯一不準的是〈做法〉7 的括號說明,見 F5(minor)。
- 第 2 項:沒到位,見 F3、F4。
- 第 3 項:到位。取得函式、扣減排在喚醒之前、喚醒那一路照報,三處都與 `scripts/lumos:28440` 的 `seen` 建法相容。
- 第 4 項:到位。字面上只有「半形全形」的寫法有疑義,見 F6(minor)。
- 第 5 項:到位。
- 第 6 項:沒到位,見 F1。
- 第 7 項:沒到位,見 F2。
- 第 8 項:到位。68=55+13、9=3×3 的算術都對得上,版本常數與雜湊釘法照抄 `t_note_audit_reread_template_pinned`。我查過 `scripts/test_lumos.py:51412`,它寫死「版本 1 換成 0」,spec 已點名要改。

固定席:這次投稿沒有附。

**F1 共用 4 KB 裁法的簽名做不出舊句檢查帳的裁法**
severity: major
blocking: 是 — 照字面實作,[S36] 指定的既有測試 `t_drift_m1_events_and_budget` 會紅
引句:「再呼叫可選的參數 `then(extra)` 做下一步裁法」
1. spec 把裁法定成 `_gate_event_fit(repo_root, gate, kind, note, extra, list_key)`,`then` 只收 `extra`。
2. 現行 `scripts/lumos:33635` 的 `_drift_m1_fit` 另外需要 `hard`、`tip`、`nodes`。
   - `size()` 組事件時要帶這三個(`scripts/lumos:33640`)。
   - 它的回傳值是被截過的 `nodes`,呼叫端用回傳值寫帳(`scripts/lumos:33705`)。
3. `nodes` 不在 `extra` 裡(`_gate_event_build` 把它當獨立參數,`scripts/lumos:1147`)。
   - 照 spec 的簽名,`then(extra)` 改不到 `nodes`。
   - `size()` 量事件時也不含 `nodes` 與 `hard`,量的跟寫的不是同一行。
4. 測試 `scripts/test_lumos.py:59336` 要求「rows 丟光還超過 → nodes 截到 20」,照簽名做不出來。
5. 預期:簽名帶 `hard`、`nodes`,回傳截過的 `nodes`,或 `then` 能改 `nodes`。實際:spec 沒給。

**F2 推上去後「改寫括號內容照配」做不到,S38 後半句不可能綠**
severity: major
blocking: 是 — 驗收條款 S38 與給作者的處理指引照字面都是錯的
引句:「改寫括號內容(還是舊句加一段括號,照配)」
1. 舊句 O 已推上去的是 `O(甲)`,作者想改成 `O(乙)`,於是遠端頂端(也就是推送起點)的那一行是 `O(甲)`。
2. 配對條件是「N' 以 O' 開頭而且比 O' 長」,O' 是起點版本的那一行。`O(乙)` 並不以 `O(甲)` 開頭,配不上。
3. 起點版本裡根本沒有單獨的 `O`,所以改寫括號和「另開提交整段刪括號」一樣,都是整行照查。
4. 預期:改寫照配(S38 後半句、天花板 9 末句、skill 子檔 `06-代碼審與推送.md` 的處理指引都這麼寫)。實際:整行照查,舊句原有的違規全部回來,這正是本案要消除的情境。
5. 實作者寫 `t_ns_append_push_range` 的「改寫括號」那段會紅。補救指引要改成只有推送前 amend 或壓提交才有效;已推上去的括號只能在原括號尾巴再追加。

**F3 第二層:有 `tail` 欄的判定怎麼和略過、`skip` 的「已判重判定」檢查合併,沒定義**
severity: major
blocking: 是 — 這是放行路徑,實作者會各自猜,而且可以猜出讓 CODE 判定被略過
引句:「略過(SKIP)照舊不分範圍」
1. 現行 `_note_audit_fold` 回 `{id: class}`,SKIP 只在該編號沒有任何判定時才 `setdefault`(`scripts/lumos:29066`)。
2. `_NOTE_AUDIT_WEIGHT` 只有 CONTEXT/MIXED/CODE,沒有 SKIP(`scripts/lumos:28727`)。spec 要「整行判定與 `tail`=h 判定取最重」,整行那邊若是 SKIP 就沒有權重可比。
3. `cmd_note_audit_skip` 用 `judged = set(fold)`、`fold.get(it["id"]) in (CODE, MIXED)` 來擋已判重的行(`scripts/lumos:29644`)。fold 改成以 (編號, `tail`) 為鍵後:
   - 這兩個檢查對帶 `tail` 的 CODE 判定全部查不到。
   - 具體輸入:一行補括號的項目,判定者回 CODE,record 寫 `{id, class: CODE, tail: h}`。作者跑 `note-audit skip`,`todo` 會包含它,「已經判了推得出,不能略過」的警告也不出。
   - 寫出 `{id, SKIP}` 之後,check 若照「SKIP 不分範圍」就放行了被判 CODE 的那行。
4. spec 在〈做法〉4 只定義了 prepare、check、doctor 的涵蓋,沒寫 `skip` 與 record 結尾 `left`(`scripts/lumos:29618`)的算法,也沒寫 SKIP 與 `tail` 判定同時存在的優先序。
5. 預期:SKIP 只能蓋「該項目所有範圍都沒有判定」的情況,`skip` 的 heavy 檢查要看任何 `tail` 下的 CODE/MIXED。實際:spec 沒寫。

**F4 doctor「編號有任何判定就算」字面包含 CODE/MIXED**
severity: minor
blocking: 否 — 判準是措辭,測試 S34 寫明的是 CONTEXT 情境
引句:「編號有任何判定就算」
1. 現行 doctor 的涵蓋是 `_note_audit_covered(cls)`,只認 CONTEXT/SKIP(`scripts/lumos:29073`、`scripts/lumos:34471`)。
2. 照字面,編號下有一列 `tail` 的 CODE 判定,doctor 也算涵蓋,事後掃描會從此不唸被判推得出的行。
3. 預期:先在各 `tail` 之間取最重,再套 `_note_audit_covered`。這句要寫明。

**F5 〈做法〉7 對第一層 doctor 的起點說明不符現行程式**
severity: minor
blocking: 否 — 只是描述不準,不影響配對正確性
引句:「起點改成最近那批之前,不是上線點」
1. 第一層 doctor 在超過上限時,仍把 `gl`(上線點)當 `base_where` 傳進 `_note_shape_eval`,只用 `max_count` 限提交數(`scripts/lumos:34303`)。
2. 起點改成最近那批之前的是第二層 doctor(`scripts/lumos:34440`)。
3. 對配對沒壞處,因為配對用淨差異,只是 spec 把兩層寫混了。

**F6 括號群定義裡兩種括號寫成同一個字元**
severity: minor
blocking: 否 — 純文件精度
引句:「半形全形視為同一種、可以混用、可以巢狀」
1. 〈做法〉1 的條件寫「從 `(` 或 `(` 開始」「`)` 或 `)`」,我用位元組檢查,兩邊都是 U+0028 與 U+0029。全篇沒有任何全形括號 U+FF08/U+FF09,[S10] 的「半形全形混用」也沒有具體字元。
2. 實作者只能猜,要把全形字元寫進條款。

最高嚴重度 major,blocking 3 條
