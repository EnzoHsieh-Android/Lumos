severity: major

先講結論:鎖本身包得對,但鎖只對「同樣上鎖的人」有效,而 `decision-add` 沒上鎖。另外新的嚴格讀法裡有一條平方級的正規式。

鎖範圍與測試的答案(都已實測,不另列 finding):
- 兩支指令的鎖範圍是對的。`with _vault_write_lock(env.vault):` 從 `_pq_load_for_write` 重新讀檔,到算題號、驗、`atomic_write_verify` 寫入,整段都在鎖裡。
- 鎖是可重入的。`atomic_write_verify` 和 `_pq_commit` 都不再拿別的鎖,鎖內沒有會卡住的呼叫。
- 本篇的決策走 `self_fm=new_fm`,用的是鎖內重讀的內容。
- 測試 ⑦ 抓得到沒鎖。我在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/併發資源-sonnet/B` 把兩支指令的鎖換成 `nullcontext`,跑 `-k qfm_commands` 三次,⑦ 三次都紅:12 個程序只留下 11 題。有鎖版本(目錄 A)30 項全過。
- ⑦ 只測 `question-add` 對 `question-add`,沒測 `question-set`,也沒測和 `decision-add` 並行。

1. `decision-add` 沒上鎖,會把同時寫進去的待決問題整題蓋掉。
severity: major
blocking: 是
- 時序:`cmd_decision_add` 先讀檔,`question-add` 在鎖內寫完,`decision-add` 再用舊內容整檔 `os.replace`。`pending_questions` 和 `decisions` 在同一篇計劃的同一份開頭欄位,所以兩個指令互相讀改寫同一個檔。
- 後果:被蓋掉的題兩邊都回 0,沒有任何訊息。標阻塞的題一旦消失,規格閘就攔不到它。
- 計劃 §實務隱患寫「並行會談」已處理,只對兩支新指令成立。
引句:「並行會談:兩支指令讀改寫整段上鎖(S3 有兩個程序同時寫的測試)」
- 最小重現(已跑,在 A 目錄用 `scripts/lumos`):空計劃先 `question-add q0`,再同時起 12 個 `decision-add` 加 12 個 `question-add`。三回合的結果是 Q 剩 11/13、13/13、12/13,decision 剩 10/12、12/12、12/12,所有程序 rc 都是 0。
- 修法方向:讓 `cmd_decision_add` 和 `decision-supersede` 等也走同一把鎖。至少測試要加一條 `decision-add` 與 `question-*` 並行。

2. `_strict_list_scan` 對沒有冒號的頂格長行是平方級回溯,而且對全圖每篇筆記的 lint 都會跑。
severity: major
blocking: 是
引句:「        elif re.sub(r"""^["']|["']?\s*:.*$""", "", s).lower().startswith(key[:-1].lower()):」
- 輸入:開頭欄位裡一行頂格、後面接一長串空白、之後到行尾都沒有冒號。例如 `"k" + " "*N + "b"`。`re.sub` 在每個空白位置都先吃完整串空白再失敗。
- 實測(`perf.py`,直接呼叫 `pq_parse`):N=20k 要 2.0s,40k 要 5.6s,80k 要 33s。
- 端到端比較(同一份 40KB 的 `big_計劃.md`):舊版 `62cbac45` 的 `lint` 是 1.2s、`spec-gate` 是 1.6s;新版分別是 9.3s、9.8s。
- 這條路徑在 `_nl_rule_pending_questions` 裡對每篇筆記都跑,沒有 `pending_questions` 欄位的筆記也一樣;`pitfalls --stage` 和 `spec-gate` 也走它。
- 計劃緣起說正文解析就是死在「正規式對長行平方級回溯」,這裡又長出同一類。
- 修法方向:用 `s.partition(":")[0].strip("\"' \t")` 之類的線性寫法取鍵名,不要用沒錨定的 `re.sub`。

3. 推送前提醒對每份計劃跑兩次 `git show`,沒有上限也沒有逾時。
severity: minor
blocking: 否
引句:「        present, nq, ne = pq_parse(*_pq_fm_of_text(_pq_git_show(rr, head, path)))」
- 時序:新分支首推且 `push-range` 算不出起點時,範圍會退成空樹 `..sha`,`touched` 就是整個 repo。
- 本 repo 有 274 份 `_計劃.md`,約 548 次 `git show`。我量到每次約 70ms,整批約 31 秒,全部卡在 pre-push。
- 空樹那一版的 `git show` 必失敗(rc128),純屬浪費。
- `subprocess.run` 沒有 `timeout`。git 出錯時回傳 `""`,等於靜默放行,沒有「提醒不了」的訊息。
- 修法方向:用 `git cat-file --batch` 一次讀,或先用 `git diff --name-only -S pending_questions` 之類縮小範圍。

4. 推送前提醒的範圍處理有兩個落差。
severity: minor
blocking: 否
引句:「    m = re.fullmatch(r"(.+?)\.\.\.?(.*)", git_range)」
- 單一提交或單一 ref(例如 `HEAD~3`):`spec-gate --push-check HEAD~3` 的 `git diff --name-only` 合法,但這支正規式不匹配,直接 `return`,整段提醒靜默消失。
- `a...b`:`base` 直接用 `a`,不是 merge-base。主線在分岔後新增的題會被報成「這一版不見了」。
- 提醒的決策狀態用工作樹的 `env.notes`,不是被推送那一版。從別的分支推 `local_sha` 時,可能多報或漏報。
- 以上都只影響提醒,不影響回傳碼。

5. 對全圖跑 lint、spec-gate 時,決策查詢是「題數乘決策數」。
severity: minor
blocking: 否
引句:「        for why in _pq_rule_problems(env, rel, q):」
- 每題的 `_pq_decision_state` 都重新 `parse_decisions` 一次整份決策。
- 實測一篇計劃的題數與決策數同時加倍時,`lint` 從 1000 題 100 決策的 2.9s 變成 2000 題 200 決策的 11.3s,約 4 倍(500 題 50 決策是 2.0s)。
- 每篇只要解析一次決策就好。

6. 跨篇決策的狀態用的是鎖外載入的舊資料。
severity: minor
blocking: 否
引句:「        node, did = env.resolve(pr[0]), pr[1]」
- 本篇的 `#dN` 用 `new_fm`(鎖內重讀),但 `<節點>#dN` 其他篇走 `env.notes`,是指令啟動時載入的。
- 時序:`question-set` 在排隊等鎖的 60 秒內,別的程序把那條決策作廢了。這邊仍判「結了」並寫成已決。
- 之後 lint 和規格閘用新資料判成「指到已作廢」,所以是 fail-closed,只是誤寫入。反方向則是剛新增的決策被誤拒。

圖譜鏡頭:
- `Systems/lumos-cli-write.md` 的「寫入鎖的安全邊界」只講過期鎖接手,沒涵蓋「誰上鎖誰不上鎖」。新增段仍把 `decision-add` 寫成「沒鎖」的參照物,卻沒說它現在會蓋掉 `pending_questions`(見第 1 條)。
- `_write_lf` 說明寫「其他寫入指令仍是 last-write-wins」,與兩支新指令上鎖不一致,是過期字句。
- `atomic_write_verify` 的不變式是「記憶體 re-parse 斷言該 key 寫成目標值」。兩支新指令傳 `lambda _f: True`,跳過了這條。不過 `_pq_commit` 之前已用 `pq_parse(new_fm)` 驗過同一份內容,我找不到失敗場景,所以不列 finding。
- `lumos-cli-read.md`、`規格閘.md`、`pitfalls-code-loop.md` 與程式一致。我沒找到與併發或資源有關的矛盾,只有第 2、3、5 條的效能成本沒被它們提到。
- 其餘牽連只列名:bound-tests-gate、guard-kill、lumos-cli-lifecycle、reversibility-governance-ledger。

總結:兩支新指令自己的鎖是對的;`decision-add` 沒鎖會靜默蓋掉待決問題(第 1 條),`_strict_list_scan` 有平方級回溯(第 2 條),這兩條要在合併前處理,其餘四條是效能與提醒範圍的小問題。
