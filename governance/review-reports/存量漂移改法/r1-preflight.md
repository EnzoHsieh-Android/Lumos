# 存量漂移改法_計劃 r1 機械掃描報告

掃描對象:clone-ns/governance/review-reports/存量漂移改法/r1-snapshot.md;程式 scripts/lumos(行號為該 clone 內)。

## ① 未定義的詞

- 無真正未定義的專有詞。`c1/c2/c3/c4/c5` 沒在本計劃內展開,但 scripts/lumos:25980 `_DRIFT_KIND_NAMES` 與 [[Projects/存量漂移防線_計劃]] 有定義;`plan_refs`、`valid_under`、`fixed.txt`(存量漂移防線_計劃〈修復結果〉有)都查得到。
- 輕微:「結案狀態」(對 Issue)沒明講是哪幾個值。程式裡有兩個不同集合:`QUERY_CLOSED_STATUSES`(13702,done/pass/superseded/resolved/wontfix/abandoned)與 `_DRIFT_CLOSED`(25974,只有 done/superseded,專給計劃用)。〈做法〉5 只寫 QUERY_CLOSED_STATUSES,S7「結案狀態」與〈範圍〉⑤ 未指明,實作者可能取錯集合。
- 輕微:「連帶待辦」「表態」「家節點」靠上下文可懂,不算缺。

## ② 壞引用

- `[[Projects/存量漂移防線_計劃]]`:存在。
- `[[Projects/最低Python版本改3.14_計劃]]`:存在。
- lands_in 的 `Systems/存量漂移守衛`、`Systems/guard-kill`:存在。
- 函式名找不到:
  - `_drift_acks_load`(〈實務隱患〉向後相容):**不存在**。實際是 `_drift_load_acks`(scripts/lumos:27051)。
  - `_drift_findings`(〈做法〉1「`_drift_findings` 或對應的種類函式」):**不存在**。實際是 `_drift_state_findings(env, only=None)`(26078,c1 到 c5 都由它出,c1 在 `_drift_guard_findings` 26122)。計劃留了「或對應的種類函式」,但寫成程式名的那個是錯的。
- 其餘都存在:`_guard_settle_rewrite`(12086)、`_guard_planned_prose`(12022)、`_drift_split_acked`(27079)、`_drift_old_reason`(27089)、`edit_fm_scalar`(14450)、`edit_fm_sync_status_tag`(14470)、`atomic_write_verify`(14695)、`_vault_write_lock`(14765)、`QUERY_CLOSED_STATUSES`(13702)、`cmd_set`(14814)。
- 測試名 `t_drift_fix_*` 等九個在 scripts/test_lumos.py 都還不存在(設計階段正常,提醒要新寫)。
- 舉例錯誤:〈做法〉5 拿 [[Projects/最低Python版本改3.14_計劃]] 的 lumos.cmd 那條當「已收尾的計劃刻意留著的回頭條件」。該計劃 status 是 `doing`(不是收尾),lumos.cmd 那條是 `REVISIT:2026-12-29`(未到期,該檔約 117 行)。此例不能證明「已結案卻留著回頭條件」。

## ③ 範圍自相矛盾

1. 〈範圍〉⑤ 寫「doctor E5 對已結案筆記的到期回頭條件標出『這篇已結案』」,〈誠實界線〉又說「結案 Issue 的過時提醒照樣會唸,只是多了標記」。這兩處一致,但「已結案」的判準取 QUERY_CLOSED_STATUSES,包含 `pass`、`done`(計劃、驗證紀錄、守衛紀錄也算)。所以標記不只標 Issue,計劃也會標。〈範圍〉標題只談 Issue,範圍比字面大。且 doing 的計劃不標,前面舉的例子(見②)不會被標。
2. 〈範圍〉⑥「c2 的表態記下當時連著的已收尾計劃」與〈範圍〉標題「c2 表態會蓋掉之後的新情況」一致,但〈做法〉6 又「c3 同理」,〈範圍〉⑥ 沒提 c3(S8 有)。範圍漏列 c3。
3. 〈做法〉1「c2、c5 與其他:回 2」與〈不做〉「c2、c5 的自動改法」一致;但 argparse 的 `--kind` 若限制 `c1|c3|c4`,c2/c5 會被 argparse 直接以 rc2 擋掉且印的是 argparse 用法訊息,不是「指到 drift ack」。[S1] 要求「指到 drift ack 或 guard settle」,所以 `--kind` 必須接受全部 `_DRIFT_KINDS`(現有 `drift ack` 的做法,36523 一帶 choices=_DRIFT_KINDS),再由函式回 2。計劃沒寫清,有實作歧義。
4. 〈回退〉「c2/c3 表態的 related:回退時比對忽略這個欄位即可」與〈實務隱患〉自我治理「新寫的一律帶清單」相容,無矛盾。
5. S3 與〈做法〉2:`guard settle` 對 pass 補做第二步,但 CLI 的 `--test` 是必填(36073,`required=True`),`cmd_guard_settle` 還會先驗 method 合法(12200)。對 pass 節點補改句根本用不到 method,計劃沒說「pass 補改時 `--test` 還要不要給」。要嘛維持必填(使用者得亂給一個名字),要嘛改選填,兩種都是行為決定,計劃沒選。

## ④ 機械宣稱驗語意

| # | 計劃原句(逐字) | 程式位置 | 判定 | 程式實際 |
|---|---|---|---|---|
| 1 | 「c1 的改句邏輯現成(`_guard_settle_rewrite`,guard settle 第二步)」 | 12086、12297(`_guard_settle_record`) | 屬實 | `_guard_settle_rewrite(lines, today, home_link)` 回 `(改寫後的行, 找不到的句型清單)`;`today` 是字串參數,所以可注入 `--date`。只動 `_guard_planned_prose` 認得的四種句型。 |
| 2 | 「`guard settle` 對 pass 直接回『已轉正』」(〈修復結果〉)/「沒有預告句照舊印『已轉正,不用再做』」(〈做法〉2) | 12222-12225 | 屬實 | status == pass 時印「已轉正,不用再做:{rel} 已經是 pass」rc0,完全不看預告句還在不在。 |
| 3 | 「同一篇的四種預告句是一組,只改一句會留下自相矛盾的半套」/「只改 `_guard_planned_prose` 認得的四種句型,其他行一字不動」 | 12022-12040、12086-12110 | 屬實 | 認四種:test、why、whynot、settle(`_GUARD_PROSE_KINDS`,12019);其餘行 `out.append(ln)`。 |
| 4 | 「已 pass 但預告句還在」重跑 `_guard_settle_rewrite` 安全 | 12049、12022(`settled_ok=True`) | 屬實 | 改寫後的句子都不會再被認成預告(WHY 尾巴 `已轉正)` 走 why-done 原樣;TEST/為什麼還不做/settle 句改寫後開頭不同),冪等。括號是 ASCII `)`,與 `_GUARD_SETTLED_TAIL_RE`(12018)相符。 |
| 5 | 「跟手補的段不疊:…如果它後面(跳過空行)下一段已經以『<日期> 已轉正』開頭,就刪掉這句而不是換成『(日期 已轉正)』」 | 12103-12104 | 不屬實(現狀無此行為,屬新增) | 現在 settle 句一律換成 `({today} 已轉正)`,不看後文。計劃把它當要新做的事寫,可接受;但要注意:刪掉 settle 句時該行是「刪一行」不是「原地替換」,而 `_guard_settle_rewrite` 是逐行一對一輸出,需改成可刪行;兩支同時要共用,計劃已說共用。 |
| 6 | 「找不到的句型照 settle 現在的做法印提醒(`missing`),不當錯誤」 | 12305、12318-12321 | 屬實 | `missing` 由 rewrite 回傳,印「提醒:…裡找不到…」,rc 仍 0。 |
| 7 | 「照 guard settle『做到一半可以補完』的既有做法」 | 12197-12205、12261-12262 | 部分屬實 | 現有的「補完」指的是家節點已是正式行、守衛紀錄仍 pending(12261 `這次只補守衛紀錄`)。「pass 但預告句還在」是另一種狀態,現在被 2 擋成「已轉正」,不屬於既有補完。是新行為,不是照既有做法。 |
| 8 | 「`_drift_split_acked` 比對:路徑+原文+種類」(〈做法〉6「表態本來就不綁行號(比的是路徑+原文+種類)」) | 27075-27086 | 屬實 | key = `(nfc(path), text.strip(), kind)`,不含行號、heading。ack 記錄有 `line` 與 `heading` 欄位但比對不用。所以「同篇上面插幾行照樣對得上」現狀成立。 |
| 9 | 「表態帶 `related` 的,要現在的清單是它的子集才算對得上」 | 27079 | 現況無此欄位(屬設計) | `cmd_drift_ack` 的記錄(27101 起)只有 id/path/text/kind/reason/date/heading/line,沒 `related`;`_drift_split_acked` 只用 key。發現物本來就有 `related`(26078-26120:c2 是排序後的收尾計劃路徑,c3 是 plan_refs 的計劃),所以取值來源現成;但發現的 `related` 是 vault 內相對路徑(不含 `vault_rel/` 前綴),ack 的 `path` 有前綴,計劃沒寫 related 要存哪一種,兩邊要一致。 |
| 10 | 「現在多出新的收尾計劃就重新列出,並印舊理由供參考(`_drift_old_reason`)」 | 27089-27098、27176-27184 | **不屬實** | `_drift_old_reason` 的 `alive` 參數會跳過「表態原路徑現在還在」的表態(27095)。而三個呼叫者(27217、27220-27223)都傳 `alive`。related 失效時,表態原路徑當然還活著,`_drift_old_reason` 會 `continue` 略過,回 None,不會印舊理由。且印出的字是「這一行以前表態過、後來改了或搬了,舊理由:…」(27183),語意是改名,不是「新增了計劃」。要達成計劃說的,需另加一條路徑(或給 `_drift_old_reason` 加一個「同路徑但 related 失效」的分支),計劃把它當現成函式直接用,不成立。 |
| 11 | 「表態檔多一個欄位,舊版 lumos 讀到會忽略(`_drift_acks_load` 只取需要的鍵),不會壞」 | 27051-27072 | 部分屬實 | 函式名錯(實際 `_drift_load_acks`)。它不是「只取需要的鍵」:讀 JSON 行後整個 dict 原樣回傳,只驗 `path` 有值且 `kind` 在 `_DRIFT_KINDS`(27069)。多的欄位不會壞,因為所有下游只用 `a["path"]`、`a.get("text")`、`a["kind"]`、`a.get("reason")`;結論(不會壞)成立,理由(只取需要的鍵)不成立。 |
| 12 | 「`QUERY_CLOSED_STATUSES` 在 doctor E5 用」(〈做法〉5:「來源筆記的 status 在 `QUERY_CLOSED_STATUSES` 的」) | 13702 | 屬實(值) | 值為 {done, pass, superseded, resolved, wontfix, abandoned}。E5 現在完全不看 status(2205-2262),迴圈只有 `_n5.stem`,`_n5.fields` 可取 status,可行。 |
| 13 | 「doctor E5:到期清單裡…照樣列、照樣計數」(現在行為) | 2205-2262 | 屬實 | 現在 E5 不看狀態,已結案筆記的 REVISIT 也照列照計(`_rv_due`),`gov_events` 的 nodes 用 stem。所以「加標記」只需在 `_lines5` 那行組字串處加,計數不變。 |
| 14 | 「`lumos set` 把 Issue 改成結案狀態時列連帶待辦…同計劃收尾時列連帶待辦的做法」 | 37036-37043、26149、26193 | 部分屬實 | 現有的「計劃收尾列連帶待辦」是在 main 分派處(37040-37043)`cmd_set` 成功後呼叫 `_drift_print_followups`,不在 `cmd_set` 內;且 `_drift_plan_followups` 對非 project 或非 `_DRIFT_CLOSED` 直接回 []。所以 Issue 結案要新加分支,且 `cmd_set` 也被別處呼叫時(如 guard settle 走 `edit_fm_scalar` 而非 `cmd_set`)不會列。「只印、不擋、不改」與現有做法一致。 |
| 15 | 「寫入一律拿筆記庫寫入鎖(`_vault_write_lock`)、用 `atomic_write_verify` 寫」 | 14765-14795、14695 | 屬實(可重入) | 鎖是可重入(`_VAULT_LOCK_HELD`,14770-14775 一帶),`cmd_guard_settle`(12195)整段包鎖後內部再走 `atomic_write_verify` 沒問題。`atomic_write_verify(path, new_lines, key, expected_check)`:先讀原檔,`expected_check(fields)` 驗開頭欄位,失敗丟 RuntimeError,不改原檔;只驗開頭欄位。 |
| 16 | 「寫入…改完重讀自驗」(用在 c1、c4 這類只改**正文**的寫入) | 14695-14712 | 部分屬實 | `atomic_write_verify` 的自驗只解析開頭欄位 + 檢查 lint 指紋沒增加。c1 只改正文行、c3 主要驗 status;c1 的自驗 `key/expected_check` 要自訂(如 `_guard_settle_record` 用 status),對「正文句子真的被改了」沒有讀回驗證。計劃說「改完重讀自驗」,c1(正文)實際上驗不到正文,需另寫一段重讀比對,計劃未說。 |
| 17 | 「c3:status 用 `edit_fm_scalar` + `edit_fm_sync_status_tag`(同 `cmd_set`)」 | 14450、14470、14830-14862 | 屬實 | `cmd_set` 正是這兩支加 `atomic_write_verify`;`edit_fm_sync_status_tag` 回 `(fm, 有無 status/* 標籤)`,沒有 tags 時不發明。`_check` 用 `tag_synced` 判斷標籤同步。加正文一行則 `cmd_set` 沒有,要自己 append 到 `lines`(注意檔尾換行),計劃只有文字。 |
| 18 | 「c3 ...改 status 為 `pass|fail`」搭配 `edit_fm_scalar` | 14356、14454 | 部分屬實 | `SCALAR_KEYS` 含 status,`edit_fm_scalar` 不驗值域(值域檢查由別處/lint 管),`pass|fail` 是計劃自己限定,程式不擋;`fail` 是否為驗證紀錄合法 status,計劃沒指出程式出處,未在本次核對。 |
| 19 | 「c4:把 valid_under 裡含『未提交/還沒提交/uncommitted』的那一項換成新句子(清單欄位只換那一項,純量欄位整欄換)」 | 26078-26120、14356 | 部分屬實 | 偵測用 `_DRIFT_UNCOMMITTED_WORDS`(25977,三個詞相符)對 `" ".join(as_list(valid_under))` 比對(26111)。`valid_under` 是 COND_KEYS,現有寫入路徑 `_set_conditions_locked`(14895 一帶)是**整欄換**,沒有「只換一項」的現成工具,要新寫。欄位有單行、清單、多行區塊三種寫法(該函式 docstring 明講),計劃只提「清單/純量」兩種,漏了多行區塊。 |
| 20 | 「c4 的證據:那篇驗證紀錄第一次被提交的提交編號與日期(`git log --diff-filter=A`)」 | 1816、5846 | 屬實(可借) | 程式裡已有 `git log --diff-filter=A` 用法(1816、5846),可仿。 |
| 21 | 「c1 的轉正日期:`git log -S` 找最早那筆」「shallow clone 推不準時也擋」 | 全檔無 `-S` 用法;4861 `_git_is_shallow` | 部分屬實 | 現成有 `_git_is_shallow(repo_root)`(4861)可用來擋 shallow。`git log -S` 在 scripts/lumos 沒有先例(新寫)。要注意:家節點中正式行是 `KEY:★INVARIANT★ <claim> [test:…]`,`-S` 拿 claim 文字會同時命中預告行(`PLANNED_MARK`)第一次出現的那筆,而預告行比正式行早出現;不能直接取「最早一筆」,要取「正式行(帶 ★INVARIANT★ 且無預告標記)第一次出現」,計劃寫的是「正式行第一次出現」,方向對,但 `git log -S <claim>` 的語意不區分預告或正式,實作要另外過濾。 |
| 22 | 「先用跟 `drift scan` 同一支判定(`_drift_findings` 或對應的種類函式)確認『這一行現在確實是這一種發現』」 | 26078、27332、27266 | 部分屬實 | scan 走 `_drift_state_findings`(+ 乙的 probe);函式名錯(見②)。發現物的 `line`、`text`、`kind` 可直接對照。c1 的 `line` 是 1 起算的檔案行號(`i + 1`),c3/c4 的 `line` 是 `_drift_field_line` 的欄位行。所以「指定行號 + kind」比對可行。 |
| 23 | 「c1:… 家節點裡這條合約的正式行(`KEY:★INVARIANT★ <預告的合約> [test:…]`)」 | 12266-12268、12028-12066 | 屬實 | `_guard_settle_home` 寫出的正式行格式即 `  KEY:★INVARIANT★ {claim} [test:{method}]`;`預告的合約:` 行取 claim(12234 `re.search(r"^預告的合約:(.+)$"`)。存量 pass 節點該行仍在守衛紀錄正文,可取。 |
| 24 | 「家節點改過名或那行被改寫過,推出來的是改寫那天」 | — | 屬實(邏輯) | 與 `git log -S` 語意一致。 |
| 25 | 「`lumos set` 收尾計劃時列連帶待辦」(〈做法〉5 末) | 26193-26202、37040-37043 | 屬實 | 只印、不擋、不改;印的是「連帶待辦(…只列出、不擋…)」。 |
| 26 | 「c2 的表態記下當時連著的已收尾計劃」(來源) | 26109-26120 | 屬實(資料現成) | `_drift_c2` 發現物的 `related` = 已收尾且連著的計劃(排序後);c2 的已收尾判準是 `_DRIFT_CLOSED`(done/superseded),不是 QUERY_CLOSED_STATUSES。兩處「收尾」集合不同,計劃兩處都用「已收尾/已結案」,對 c2/c3 取 `_DRIFT_CLOSED`、對 E5/S7 取 QUERY_CLOSED_STATUSES,計劃沒分清。 |
| 27 | 「c3 同理(清單是 plan_refs 裡已收尾的計劃)」 | 26034-26065、26095-26099 | 屬實 | c3 發現物 `related` = `plans`,且 `_drift_c3_hit` 只在**全部** plan_refs 都已收尾才成立,所以清單 = 全部 plan_refs 解出的計劃。「子集」比對對 c3 意義有限:c3 只有全收尾才出,清單不會「多出新的」除非 plan_refs 被加新項且新項也已收尾。 |
| 28 | 「已排除:對外送出:…只讀本機 git」 | — | 屬實(設計) | 新功能只用 git 讀。 |
| 29 | 「〈回退〉:照 fixed.txt 可以找出來(rtb 與工具鏈的修復都要求留 fixed.txt)」 | 存量漂移防線_計劃〈修復結果〉 | 部分屬實 | fixed.txt 是該計劃〈修復結果〉列的檔,寫在 governance/audits/2026-09-29-drift-scan/,是那一次手工修復的產物;新指令 `drift fix` 本身**不會**自動寫 fixed.txt,計劃寫的是「要求留」,靠人。「照 fixed.txt 可以找出來」對之後用 `drift fix` 改的筆記不成立,除非指令自己記帳。 |

## 小結(優先度)

1. 不屬實:#10(`_drift_old_reason` 在 related 失效時會因 `alive` 過濾而不印舊理由,訊息文字也是「改了或搬了」)。
2. 壞引用:`_drift_acks_load`、`_drift_findings` 兩個函式名不存在。
3. 部分屬實需補寫:#7、#11、#14、#16、#19、#21、#29(見表)。
4. 範圍缺口:〈範圍〉⑥ 漏 c3;「結案狀態」兩個集合(`QUERY_CLOSED_STATUSES` 與 `_DRIFT_CLOSED`)沒分;`guard settle --test` 對 pass 節點的必填問題沒交代;舉例 [[Projects/最低Python版本改3.14_計劃]] 現在 status 是 doing、REVISIT 未到期,不能當「已收尾卻留回頭條件」的例子。
