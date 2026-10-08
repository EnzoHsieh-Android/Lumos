severity: major

前輪修復清單驗收:
- 第 1 項:沒到位,見 I1
- 第 2 項:到位
- 第 3 項:到位(S19 的計數口徑含糊,見 I5)
- 第 4 項:到位
- 第 5 項:到位
- 第 6 項:到位(docstring 清單仍漏 `_note_audit_render_list`、`_ns_negation_hints`、`_ns_negation_collect`,見 I4)
- 第 7 項:到位
- 第 8 項:到位(〈回退〉的措辭有矛盾,見 I6)

固定席:這份稿沒有附尾端固定席,不判。

**I1 「本機推送前與 CI 同一個起點」對新分支首推不成立**
severity: major
blocking: 是 — 第 1 項修復宣稱的等價,對新分支首推不成立,S22 又只測同一範圍,測不出。
引句:「推送前掛鉤與 CI 的筆記形狀擋起點相同(都經 `_lens_push_base` 再截到上線點」
1. 輸入:新分支首次推送。這個分支從另一條已推上遠端的分支 F 切出,F 的頂端有一行舊句 L。分支上有一個提交只在 L 句尾補括號。
2. 本機掛鉤對新分支不給 40 個 0。它先找「不在任何遠端上的最早提交」,再用它的上一版當起點(`scripts/hooks/pre-push:335-344`,`_hrange="$(git rev-parse "$_hold^")..$_lsha"`)。
3. `_lens_push_base` 拿到真實 sha,原樣回傳(`scripts/lumos:38535` 起,`a` 不是全 0 就直接 `return s`)。起點是 F 上的提交,L 在起點版本裡,所以配對成功、放寬。
4. CI 給的是 `$BEFORE`,新分支首推時是 40 個 0(`.github/workflows/ci.yml:140`)。`_lens_push_base` 於是改走跟主線的分岔點。L 不在那個版本裡,整行照查。
5. 預期:同一次推送,本機與 CI 的配對結果一樣。實際:新分支首推時,兩邊起點不同,配對結果可能不同。〈跨環境〉與〈做法〉1 都斷言「配對結果一樣」。S22 只用同一個 `$BEFORE..$SHA` 跑兩次,模擬不出這個差別。
6. 要補的:把斷言限縮成「已存在的分支」,或在 S22 加新分支首推的一組。

**I2 `_gate_event_fit` 的簽名不夠撐起宣稱的「行為不變」**
severity: minor
blocking: 否 — 實作者一動手就會發現並自行補參數,S36 會擋回歸。
引句:「把 `_drift_m1_fit` 拆成共用的 `_gate_event_fit(repo_root, gate, kind, note, extra, list_key)`」
1. 現行 `_drift_m1_fit(root, kind, note, hard, tip, nodes, extra)` 量長度時要帶 `hard`、`head_sha=tip`、`nodes`(`scripts/lumos:33635-33650`)。新簽名都沒有。
2. 現行函式會把截過的 `nodes` 回傳給呼叫端。新簽名沒有回傳值。`then(extra)` 只收 `extra`,也截不到 `nodes`。
3. 預期:簽名與回傳值足以讓舊句檢查帳逐位元組不變。實際:照字面做不出來,實作者得自己加參數和回傳值。

**I3 〈做法〉7 的括號註解把第二層的起點算法套到第一層**
severity: minor
blocking: 否 — 只影響 doctor 的說明,實作者讀程式就會發現。
引句:「(既有:要掃的提交超過 `_NS_DOCTOR_SCAN_CAP` 個時,起點改成最近那批之前,不是上線點。)」
1. 這是第二層 doctor 的行為:`scripts/lumos:34440-34443`,超過上限時 `base = b2`。
2. 第一層 doctor 不改起點。它固定用 `gl`,只用 `max_count` 限制逐提交的文字來源(`scripts/lumos:28535`)。
3. 這句放在第一層的段落裡,實作者可能照它把第一層的配對起點也改掉。

**I4 涵蓋規則只講 prepare、check、doctor、skip,漏了 record;docstring 清單也漏項**
severity: minor
blocking: 否 — 只影響 record 的輸出文字,不影響擋不擋。
引句:「`_note_audit_fold` 照(編號, `tail` 或沒有)分開取最重。」
1. `cmd_note_audit_record` 結尾用 `fold.get(it["id"])` 印「還沒被涵蓋」清單(`scripts/lumos:29561-29566`)。fold 改成按(編號, `tail`)分開之後,稿裡沒說這支呼叫端怎麼判。
2. 照字面,只判尾巴的判定寫完後,record 會把這些行當成「沒判過」印出來。
3. skip 的 `left` 與 `uncommitted`(`scripts/lumos:29601-29607`)同樣沒交代。
4. 〈做法〉8 的 docstring 清單另外漏了 `_note_audit_render_list`(多印兩行)、`_ns_negation_hints` 與 `_ns_negation_collect`(新增參數)。

**I5 S19 與〈做法〉5 對「喚醒的行不算進減掉的條數」的口徑含糊**
severity: minor
blocking: 否 — 只影響帳上的數字。
引句:「被放寬的行若被新程式檔喚醒那一路照報(〈做法〉2、6),不算進減掉的條數。」
1. 扣減發生在喚醒之前(〈做法〉2)。喚醒那一路只報指向新程式檔的片段,而且排除「現況描述沒寫來源」(`scripts/lumos:28459-28464`)。
2. 所以同一行被放寬的違規(例如沒寫來源)和被喚醒報出的違規,規則不同。稿沒說「不算進」是整行的扣減都不算,還是只扣掉同規則的。
3. S19 的測試因此寫不出確定的期望值。

**I6 〈回退〉先說解析器修洞「會一起退回」,又說拆兩個提交可避免**
severity: minor
blocking: 否 — 只是措辭,結論(只還原後一個提交)是清楚的。
引句:「解析器的兩個修洞也會一起退回——退回後 `++ x` 與上下文行錯位的舊洞重現,所以實作分成兩個提交」
1. 前半句是「只有一個提交時」的後果,後半句是拆提交的結論,讀起來像拆了仍會一起退回。
2. 稿也沒寫 `_ns_diff` 的兩個新旗標和 `_notelines_parse_hunks` 歸哪個提交。
3. 預期:明寫兩者在第一個(解析器)提交,還原第二個提交時留著。

最高嚴重度 major,blocking 1 條
