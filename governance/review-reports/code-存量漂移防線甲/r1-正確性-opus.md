severity: major

# r1 正確性席(opus)——存量漂移防線甲

路徑說明:`file:` 行的路徑都相對於 repo 複本 `scratchpad/clone-ns`(b9ca00bb)。重現用的探針測試加在我自己 clone 的臨時複本 `scratchpad/cr1probe.o2SV/r/scripts/test_lumos.py` 最後面(函式名都以 `t_probe_cr1_` 開頭),在那個目錄跑 `python3 scripts/test_lumos.py -k <名字>` 就能重現;沒有改任何 repo 裡的檔。

基線:臨時複本裡 `-k drift` 105 過 0 紅、`-k guard_settle` 28 過、`-k note_audit` 173 過、`-k gate_drift` 5 過。另外在 rtb-exam 上真跑一次 `lumos drift exam`(唯讀),結果是擋到 3、點到 3、漏 0、誤列 1(E4)、要處理誤報 0、只列出誤報 4、噪音最大 1,跟計劃〈考試結果〉記的一致。

## F1 合約文字本身帶方括號標籤時,轉正做到一半的補救路徑失效,c5 也抓不到
severity: major
blocking: 是 — 設計第 1 節第 2 點要的補救路徑([S5])對一類已知常見的合約寫法不成立,會回到 guard-kill 記過的卡死狀態
引句:「if _GUARD_MARKS_RE.sub("", m.group(1)).strip() == claim:」
file: `scripts/lumos:11810`
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:15`

1. `_guard_formal_line` 會把正式行上**所有** `[字母:…]` 形狀的標籤剝掉,再拿去跟合約原文比對。合約原文自己帶這種字樣時(guard-kill 的 PITFALL 行寫著「這個 repo 滿篇都是方括號標籤寫法」,既有測試 `t_guard_claim_with_bracket_tags_still_settles` 用的正是 `預告行一定要帶 [watch:守衛節點] 跟 [due:日期] 兩個標籤`),剝完只剩 `預告行一定要帶 跟 兩個標籤`,永遠不等於原文。
2. 輸入:上面那條合約 → `guard plan` → `guard settle --test t_refund` 成功 → 把守衛紀錄還原回 pending(模擬第二步寫失敗,或照計劃回退節說的「單獨用 git 還原守衛紀錄」)→ 再跑一次 `guard settle`。
3. 走的路:`_guard_settle_home` 裡 `_guard_formal_line(...)` 回 False → 落到 `_guard_planned_line` → 家筆記已經沒有預告行 → rc2。c5 走同一支比對,所以 scan 也不列。
4. 重現:`python3 scripts/test_lumos.py -k probe_cr1_bracket`,輸出:
   `✗ 做到一半重跑 settle 應補完(rc0)  擋下:Systems/Pay.md 裡找不到預告行『預告行一定要帶 [watch:守衛節點] 跟 [due:日期』(被手改過或已經轉正?)`
   `✗ c5 應列出這篇 … "findings": []`
5. 後果:守衛紀錄停在 pending、家筆記已經是正式行。settle 擋、abandon 也對不到預告行而擋,到期後逾期檢查會一直擋推送。計劃回退節寫的「真的還原了,用新程式重跑 settle 補完」對這類合約不成立。修法方向:只剝掉行尾那一串標籤,比照 `_PLANNED_TAIL_RE` 只剝行尾那一對的做法。

## F2 check 擋下時教人「重跑 guard settle 改寫預告句」,但 settle 對已經是 pass 的紀錄什麼都不做
severity: minor
blocking: 否 — 同一段訊息裡另外兩條路(手改、表態)還能走,只是第一條指示是錯的
引句:「轉正後的預告句可以重跑 lumos guard settle 的新版改寫」
file: `scripts/lumos:25536`
file: `scripts/lumos:11953`

1. c1 只會出現在 status 已經是 pass 的守衛紀錄上。這時跑 settle 會先走「`st == "pass"` → 印已轉正,不用再做、回 0」,根本到不了 `_guard_settle_rewrite`。
2. 重現:`-k probe_cr1_rerun`(舊版轉正、留著預告句的 G.md 跑 `guard settle Verification/G --test t_x`),輸出:`settle: 0 已轉正,不用再做:Verification/G.md 已經是 pass`,接著 `✗ 重跑 settle 後預告句應改寫  預告句還在`。
3. 人照著提示重跑,拿到 rc0 和「不用再做」,再推一次照樣被擋。rtb 的 A4–A6 這類存量紀錄剛好就是這種情形。計劃〈回退〉與 [S5] 本來就規定 pass 要早退,所以錯的是這句提示,不是 settle。

## F3 家筆記同時有同一句的正式行與預告行時,settle 走補救分支,預告行沒拿掉卻印「已換成正式合約」
severity: minor
blocking: 否 — 前提是同一句合約已經有正式行又被再預告一次,少見;不過一旦踩到就會卡死(⚠ 發生頻率判不準)
引句:「if _guard_formal_line(hlines, he, claim, method):」
file: `scripts/lumos:11981`

1. 補救判斷排在找預告行前面,只要「有同一句、同一個測試名的正式行」就跳過第一步,不看預告行是不是還在。
2. 重現:`-k probe_cr1_formal`(Pay.md 已經有 `KEY:★INVARIANT★ 大額退費要人工核可 [test:t_refund]`,再 `guard plan` 同一句,然後 `guard settle --test t_refund`),輸出:rc0、`已經是正式合約行(上次轉正做到一半),這次只補守衛紀錄`,接著 `✓ 轉正:Systems/Pay.md 的預告行已換成正式合約…`。實際上家筆記還留著 `KEY:★INVARIANT-PLANNED★ … [watch:…] [due:2099-12-31]`。
3. 結果:守衛紀錄是 pass,預告行留著、到期會被當成逾期。再跑 settle 會回「已轉正」;abandon 寫完後要驗「摘要裡已經沒有這句合約」,正式行還在,所以驗不過而擋。改這支之前,settle 碰到這種輸入會把預告行換掉,不會卡住。另外,這也是「回報成功但沒真的做到」,跟 [[Issues/canary-record未落盤事件]] 同一型。

## F4 表態失效時印的「舊理由」會套到從沒表態過的另一篇
severity: minor
blocking: 否 — 只影響提示文字,不影響擋不擋
引句:「if str(a.get("text", "")).strip() == f["text"] and a.get("kind") == f["kind"]:」
file: `scripts/lumos:25405`

1. `_drift_old_reason` 只比原文和種類,不比路徑。守衛紀錄的四句預告句是樣板,同一天、同一個負責人、同一個期限的兩篇會一字不差。c2、c3、c5 的原文更是組出來的固定字串 `status: open` / `status: pending`,所有同種類的發現都一樣。
2. 重現:`-k probe_cr1_old_reason`(A、B 兩篇同樣板,在同一範圍裡用舊方式轉正;只對 A 的四行表態並提交)。check 對 B 的四筆都印了 `(這一行以前表態過、後來改了或搬了,舊理由:A 篇照留的理由)`。
3. B 從來沒表態過,這句話是錯的,而且在引導人照抄別篇的理由。計劃原文就是「用原文與種類相同找」,所以這是設計和實作共有的洞;印之前至少該排除「路徑不同、而且原本那篇的表態還對得上」的情形。

## F5 欄位層級發現的「原文」不是那一行的實際內容,表態對不上或永不失效
severity: minor
blocking: 否 — c2 到 c5 只列出、不擋;受影響的是 scan 與 doctor Z 一直唸同一筆
引句:「"text": f"status: {st}", "related": [p for p, _d in plans],」
file: `scripts/lumos:25198`
file: `scripts/lumos:25207`

1. c2、c3、c5 的發現原文是組出來的 `status: <值>`,但 `drift ack` 記的是那一行實際的字 `lines[line-1].strip()`。只要那一行寫成 `status: "open"`(或行尾帶註解),兩邊永遠對不上。
2. 重現:`-k probe_cr1_c2_ack`(Issue 寫 `status: "open"`,連到已收尾的計劃):`drift ack Issues/I 3 --kind c2` 回 rc0、說已記下,但 scan 的 JSON 裡那筆 c2 還是 `'acked': False`。
3. c4 碰上清單或多行寫法的 `valid_under`(`lumos set … valid_under a b` 本來就會寫成清單)時,發現原文是鍵那一行 `valid_under:`。表態綁在這一行上,之後條目怎麼改都不會失效,違反計劃「改了那一行就失效」的本意;對真正含「未提交」的那一行表態又對不上發現。

## F6 提交樹上的 Env 排序跟磁碟上的不一樣,同名筆記在 scan 與 scan --at HEAD 會解到不同篇
severity: minor
blocking: 否 — 前提是有同名筆記(doctor 本來就會警告),而且資料夾名稱差在比 / 小的字元
引句:「self.notes = {r: _note_from_text(r, t) for r, t in sorted(self._texts.items())}」
file: `scripts/lumos:423`
file: `scripts/lumos:322`

1. `load_vault` 照 Path 排序(逐層比),`Env.from_texts` 照整串字串排序。`Projects/X.md` 跟 `Projects-old/X.md` 的先後會反過來,因為 `-`(0x2D)比 `/`(0x2F)小。`make_resolver` 對同名筆記取 `hits[0]`,所以兩種 Env 會把 `[[X]]` 解到不同篇。
2. 重現:`-k probe_cr1_tree`(Projects/同名_計劃=done、Projects-old/同名_計劃=doing、Issue 連 `[[同名_計劃]]`,全部提交、工作目錄乾淨)。輸出 `disk: [('c2', 'Issues/I.md')]`、`tree: []`。
3. 「不另寫第二套解析」只做到單篇解析,整份筆記的順序沒對齊。後果是 check/exam(樹)和 scan/doctor(磁碟)對同一個提交給出不同結論。改成 `sorted(..., key=lambda kv: kv[0].split("/"))` 就能跟 Path 排序一致。

## F7 doctor Z 與 scan 的文字輸出把已表態的行整筆拿掉,跟設計寫的「照列、標已表態」不一致
severity: minor
blocking: 否 — 只影響健檢的呈現,不影響閘
引句:「left, _done = _drift_split_acked(_drift_state_findings(env), _drift_load_acks(root), vault_rel)」
file: `scripts/lumos:25596`
file: `scripts/lumos:25578`

1. 計劃第 0 節 `drift ack` 那條寫「scan 與 doctor 對已表態的行照列、標已表態」。實作裡 doctor Z 只算 `left`,已表態的行不出現、也不計數;scan 的文字輸出只在標題附一個 `已表態 N`,不列出是哪幾行(只有 `--json` 帶 `acked: true`)。
2. 如果這是刻意的取捨(怕 doctor 天天唸),[[Systems/存量漂移守衛]] 的「跟設計稿不一樣的兩處」就漏記了這一處。

## F8 只有「判不了」時,擋下訊息寫「有 0 處要處理」
severity: minor
blocking: 否 — 只是訊息自相矛盾,rc 是對的
引句:「這次推送有 {len(must)} 處要處理(存量漂移檢查)」
file: `scripts/lumos:25530`

1. 走 `unknown` 非空、`must` 為空這條路(`t_drift_unknown_blocks_check_not_scan` 就是這個現場)時,stderr 第一行是 `擋下:這次推送有 0 處要處理(存量漂移檢查)——`,下一行才是「判不了:…算要處理」。擋下的理由跟數字互相打架;判不了的條數應該算進去,或者換一句話講。

## 已看,無 finding 的部分
- **load_vault 抽出 `_note_from_text`**:stem 的算法從 `p.stem` 換成「路徑最後一段去掉 `.md`」,對所有 `*.md` 結果一樣。唯一不同的是檔名剛好叫 `.md`(舊的算出 `.md`、新的算出空字串),找不到會出事的情境,不列。讀檔失敗那條路照舊建出帶 `讀檔失敗` 的 Note、mtime=0。BOM 照舊用 utf-8-sig 讀;樹那一側也用 utf-8-sig 解碼。
- **c1 行首前綴**:`_notelines_regions` 回傳的清單跟行數一一對應,`regs[i]` 不會越界。settle 改寫後的四句都不再以原本的前綴開頭,WHY 帶「已轉正)」後綴就不算,`t_guard_settle_rewrites_planned_prose` ⑤ 也驗了「轉正後的推送不被自己擋」。
- **c3**:plan_refs 的每一項都要找得到、是計劃、而且已收尾;空的、壞的、指到 Issue 的,以及守衛紀錄都排除。`lumos set` 連帶待辦的第②項走同一支,並用 override 算「改好之後」的狀態,集合一致。
- **c4 關鍵詞**:三個詞用子字串比對,不看「工作樹」,跟設計一致。
- **settle 兩步**:從磁碟重讀 status,pass 早退、非 pending 擋;第二步 status、標籤和句子同一次 `atomic_write_verify`;失敗訊息附重跑指令。跟舊版 `cmd_set` 比,少的只有 cmd_set 印出的那一行,欄位行為(不改 updated、標籤同步驗證)相同。鎖可重入(`_VAULT_LOCK_HELD`),plan、abandon 內部再呼叫 cmd_append/cmd_set 不會卡死。
- **check 的範圍事件**:pending→pass 共用 `_notes_status_flipped`(逐提交、跟著改名走、起點用改名偵測);計劃收尾沿用原本的函式;touched 用頭尾差異。只有範圍裡轉正的 c1 會進「要處理」,範圍外的 c1 不列(設計說只在 scan/doctor 列)。c2 到 c5 的歸屬比設計列的事件多算了「相關筆記被改到」,只會多列、不會少列。
- **表態比對**:路徑前綴兩邊都用「圖譜相對 repo 根」的算法;check 只讀頂端提交裡的表態檔(⑧ 已驗)。問題見 F4、F5。
- **exam**:三種考法照設計;`note_at_event` 用在 commit 與 status_replay;status_replay 在上一版的樹上、在記憶體裡改 status 再算連帶待辦;不認得的考法回 2;不寫帳。在 rtb 上真跑,結果跟計劃記錄一致。
- **_note_audit_resolve / _notes_status_flipped 參數化**:預設值保留原本的閘名與上線標記,`-k note_audit` 173 支全綠;動態傳入的閘名經 `_gate_event_or_warn` 內的名單檢查,`t_gov_stats_gate_drift` 綠。

## 圖譜鏡頭:固定席節點逐條判
- [[Systems/guard-kill]]:**受影響**。它的 PITFALL(合約文字帶方括號標籤,只能剝行尾)這次在補救比對裡又犯了一次,見 F1。rc 優先序、`--json` 純度兩條合約只管 guard kill,這份 diff 沒動,不影響。
- [[Issues/canary-record未落盤事件]]:「回報成功就等於真的做到」的原則被 F3 違反(印了已換成正式合約,其實沒換)。`drift ack` 走 `_jsonl_append_verified` 讀回自驗,符合。
- [[Systems/reversibility-governance-ledger]]、[[Systems/節點範圍與索引守衛]](新閘名要登記):`drift-check` 已登記進 `_KNOWN_GATES`,漂移釘綠,不影響。
- [[Systems/pitfalls-code-loop]]:簿記白名單多了 `governance/drift-acks.jsonl`,性質跟判定檔一樣,只擴大豁免範圍、不影響既有判定。
- [[Systems/lumos-cli-read]]:search、doctor 的合約靠 load_vault 的結果;單篇解析抽出後內容等價(見上面「已看」),不影響。
- [[Systems/測試假綠形態]](修 bug 的翻紅釘要有前置斷言):新測試裡補救路徑那支有 ① 前置斷言,其餘是新功能,不適用。
- [[Systems/check-t-sentinel]]、[[Systems/check-r-guard]]、[[Systems/doctor-irreversible-hint]]:`INVARIANT_RE` 沒改,只是多一個呼叫點;doctor Z 用 warn_soft,不計入 issues,不改 doctor --ci 的 rc。不影響。
- [[Systems/bound-tests-gate]]、[[Systems/canary-audit]]、[[Systems/loop-convergence-recording]]、[[Systems/design-loop]]、[[Systems/judge-severity-gate]]、[[Systems/cochange-guard]]、[[Systems/lumos-refcheck]]、[[Systems/lumos-cli-lifecycle]]、[[Systems/lumos-deinit]]、[[Systems/授權與歸屬]]、[[Systems/slim-get-一行安裝]]、[[Systems/slim-install-安裝器]]、[[Systems/slim-uninstall-一行卸載]]、[[Systems/core-invariant-baseline]]、[[Projects/雙向門放行_計劃]]、[[Projects/規格落成可驗收條件_計劃]]、[[Projects/逃逸自動記_計劃]]:這份 diff 沒碰它們的程式路徑(閘判定、審計帳、安裝與卸載、授權檔、自裝檔清單、條款閘),只因為同在 scripts/lumos 被拉進來。不影響。

最嚴重等級 major,需要擋下的 1 條(F1),另有 7 條 minor 不擋。
