severity: major

我讀完 diff、`lens.txt` 和計劃檔〈天花板〉,並在複製出來的臨時 repo 實測。能重現的兩條附了指令與輸出。

**U1 舊行本來就缺來源時,補在句尾括號裡的新現況句不會被第一層查**
severity: major
blocking: 是 — 違反「新寫的內容照查」的目的,而且第二層補不上這個洞
引句:「base[v[1]] = collections.Counter(_ns_viol_key(r, f, x) for r, f, x in old_viol(o, v[1]))」
1. 輸入:起點版本有一條沒帶來源的舊摘要行 `FACT:部署在三台機器上`。新版本只在句尾補一段括號:`FACT:部署在三台機器上(後來擴到五台,另加一個新的 region)`。
2. 走到哪:`_note_shape_eval` 先對整行跑 `line_viol`,得到 `現況描述沒寫來源`。接著 `_ns_append_subtract` 用 `_ns_viol_key` 對這條規則取 `(rule,)`,也就是只看規則名。舊行已有同名違規,新行的這條就被扣掉,rc 0。
3. 壞在哪:這條規則是整行判定,不分舊句還是括號,所以括號裡新寫的、沒來源的現況句被一起放過。要放過的只該是舊句本來就有的違規。
4. 第二層補不上:第二層判的是「程式碼推不推得出來」。部署台數這類現況屬於 CONTEXT,會被判涵蓋,不會被當成缺來源。計劃檔天花板 1 寫「沒寫來源要靠第二層單獨判括號」,但第二層沒有「缺來源」這個判法。
5. 文件也誤導:`skills/lumos-project-notes/commands/03-寫回圖譜.md` 寫「只看補的那段」,但缺來源這類整行規則並沒有看補的那段。
6. 對照:`SEE 只放 [[連結]]` 規則同理。舊 SEE 行已違規時,補一整句話一樣被扣掉。
7. 重現(臨時 repo,用 `test_lumos._ns_repo`、`_ns_note`、`_ns`):
   - 提交 `summary=FACT:部署在三台機器上`,再提交 `summary=FACT:部署在三台機器上(後來擴到五台,另加一個新的 region)`。
   - 跑 `note-shape --diff base..HEAD`,輸出 `rc 0`。
   - 補一個對照:同樣的括號改成 `(見 \`src/a.py:5\`)`,輸出 rc 1。行號引用是片段鍵,所以只有它被擋。
   - 這個洞以整行規則的身分仍存在:舊行有 `現況描述沒寫來源` 時,括號裡的新現況句就是漏網的那種。

**U2 放寬沒套用時被擋的訊息只講舊句的違規,不說是括號的問題**
severity: minor
blocking: 否 — 擋是對的,只是使用者看不出該怎麼辦
引句:「return len(t) <= _NS_APPEND_MAX_TAIL and _ns_paren_groups_only(t)」
1. 三種情境會讓放寬失效:
   - 提交後又改自己剛補的括號。
   - 多次提交各補一段,推送時累計超過 300 字。
   - 單段括號超過 300 字。
2. 實際輸出:三種都只印 `現況描述沒寫來源 FACT:部署在三台機器上(…)`,改法欄寫「只准寫程式碼答不了的現況並帶 [來源:…]」。
3. 使用者沒寫過那句舊話,訊息沒說「括號 ≤300 字、且要接在沒動過的舊句後面才只查括號」。`03-寫回圖譜.md` 也沒提 300 字上限和累計規則。
4. 重現(臨時 repo,`_ns_repo`、`_ns`):
   - 提交 `O+(a)` 時 `--staged` 為 rc 0。
   - 再暫存 `O+(b)`,`--staged` 為 rc 1,訊息如上。
   - 暫存 `O+(` 加 301 個字 `)`,也是 rc 1,訊息同樣沒有上限提示。

**U3 範本新段落的「confirmed」跟 CODE 定義的「confirm or refute」不一致**
severity: minor
blocking: 否 — 沒有確定性的重現,只是照字面讀會誤判
引句:「CODE if what it asserts can be confirmed by reading the code, CONTEXT if not, MIXED if both.」
1. `note-audit-judge.md` 前段對 CODE 的定義是「could confirm or refute… judge the TYPE of claim, not whether it is correct」。新段落改成「can be confirmed」。
2. 照字面讀,一句已經過時、為假的程式碼主張「確認不了」,會被判成 CONTEXT 放行。這正是第二層要抓的那類句子。
3. 新段落應改成「can be confirmed or refuted」,或明寫沿用上面的定義。
4. 範本升版、雜湊釘的測試都得跟著動。
5. 跟規則 2、5、7 的關係:
   - 新段落自己聲明優先於規則 2 和 5,這點清楚。
   - 規則 7 對同編號多處取較重,沒衝突。
   - 規則 6 沒被提到。舊句裡若有對判定者說話的字,是否仍觸發規則 6,沒講清楚。「its own claims must not change the label」只說了主張,沒說指令。這點判不準,標 ⚠。
6. 「舊句」「只判這次補在句尾的」兩行的字樣,我逐字比過 `_note_audit_render_list` 和範本,一致。

**圖譜鏡頭逐條判**
- `lumos-cli-read` 的 INVARIANT(search 不排除 stale):不影響。diff 沒碰 search 路徑。
- `bound-tests-gate`(code-loop check 逐支真跑綁定測試):不影響。diff 沒動綁定測試的跑法或判定邏輯。
- `guard-kill`(rc 優先序、`--json` 輸出):不影響。diff 沒碰 guard kill。
- `授權與歸屬`:不影響。`scripts/lumos` 檔頭 SPDX 和 MIT 全文沒動,範本檔頭兩行 SPDX 還在,沒有新增被複製的檔。
- `測試假綠形態`(還原翻紅釘要有前置斷言):不影響。diff 本身不含測試。
- `reversibility-governance-ledger`、`pitfalls-code-loop`、`design-loop`:不影響。
  - 新增的 `relaxed` 帳是追加一筆,不改既有帳的判定。
  - `_drift_m1_fit` 抽成共用的 `_gate_event_fit`,我逐步比過:只在整行超過 4096 位元組後才截 nodes,只在超過 20 個時才截,行為與原本相同。

最高嚴重度 major,blocking 1 條
