severity: major

本輪鏡頭:邊界與可執行(第 3 版,末輪)。逐節讀完〈做法〉0–5、全部 18 條 [SN]、〈回退〉、〈實務隱患〉、〈誠實界線〉、〈審計修正紀錄〉。方法:把 spec 引用的每個既有函式/指令/欄位/檔案(`_lens_push_base`、`_nodehome_clamp_base`、`_nodehome_golive`、`_nodehome_reader`、`_nodehome_list`、`_nodehome_is_test`、`_nodehome_layout`、`_nodehome_code_kind`、`edit_fm_sync_status_tag`、`atomic_write_verify`、`_vault_write_lock`、`_visible_lines`/`_search_visible_lines`/`_strip_inline_markup`、`_lens_git`、`_gate_event`、`_KNOWN_GATES`、`_BOOKKEEPING_FILES`、`GUARD_MARK_FIELD`、`.lumos/config.json` 既有 gate 命名慣例、guard plan 樣板字串)在對照 repo(`scripts/lumos`)裡逐一開檔核對語意;並在 rtb 唯讀複本上 `git -C` 重驗考卷/改寫檔的一批宣稱。

## F1 guard settle 第四種預告句的比對樣式跟程式碼現況的實際字元不符

severity: major
blocking: 是 — 照這句實作,S4「把 guard plan 寫的四種預告句改成歷史說法」裡第四種句型在真實筆記上永遠找不到固定句型、永遠跳過,settle 的轉正改寫功能對這一句 100% 失效(不是偶發誤判)。
引句:「正文 `做完之後跑 lumos guard settle 轉正…` → `(<轉正日期> 已轉正)`。」

1. `guard plan` 實際寫入的第四種固定句(`scripts/lumos:11573`)是:
   `"做完之後跑 `lumos guard settle` 轉正,不要手改狀態。\n"`
   —— `lumos guard settle` 兩側有反引號、後面接的是「,不要手改狀態。」不是逗號後直接接「轉正」句尾。
2. spec 引句給的比對樣式是「做完之後跑 lumos guard settle 轉正…」——**沒有反引號**。若實作照這個樣式做字面(逐字)比對或以此為前綴,對照的是「做完之後跑 lumos guard settle 轉正」這串沒有反引號的文字,跟磁碟上真正寫出來的「做完之後跑 `lumos guard settle` 轉正」不會相等(反引號的位置擋在 `lumos` 前面就不同)。
3. 對照前三種句型(TEST、WHY、「為什麼還不做:」)逐字核對 `scripts/lumos:11568-11572`,三者的前綴文字都跟 spec 引句一致,只有第四種這句有這個落差——不是筆誤示意、而是真的漏了反引號與逗號後半句。
4. 後果照 S4 自己寫的容錯規則(「找不到固定句型(作者手改過)就跳過那一句並印一行提醒,settle 照樣成功」)會吃掉這個錯——不會拋例外、不會讓測試明顯翻紅在「settle 失敗」這種顯眼的地方,而是每次 `guard settle` 都印一句「這句像是作者手改過」的提醒,但其實沒有任何人手改過,新程式碼從第一天就沒對上自己該認得的句子。⚠ 若 `[test:t_guard_settle_rewrites_planned_prose]` 直接照 spec 引句的字面去斷言比對規則,測試本身也會繼承這個錯,驗不出真實壞掉的地方。
5. 修法:比對樣式要改成含反引號的那一版,或至少把「做完之後跑」到「轉正」之間的比對窄化到不含反引號差異的片段(例如只認 `做完之後跑` 開頭 + `轉正` 結尾、中間不比對反引號),並把「不要手改狀態。」這句尾一併納入改寫後綴插入點的考量(目前 S4 的「行尾已經有『已轉正』就不再加」判斷只講給 WHY 那一句,第四句要在哪裡插入 `(<轉正日期> 已轉正)`——是接在「轉正」後面、還是接在整句最後「不要手改狀態。」之後——spec 沒有明講,也需要一併定案)。

## F2 doctor Z 段「不跑 git」跟同一條款要求的「CI 沒呼叫時照其他閘慣例提醒」互相矛盾

severity: major
blocking: 是 — 兩句話在同一個驗收條款裡,字面上互斥;照著寫測試 `t_doctor_drift_section` 沒辦法同時滿足「這段執行時零 git 呼叫」跟「比照 note-audit 的 CI 提醒(該提醒的實作本身就是一次 git 呼叫)」。
引句:「只讀筆記、不跑 git,印條件式回頭條件、寫錯的條件、寫在不評估的地方的條件、c1–c5 的筆數與前幾筆,gate 不是 block 時印一行,接線後專案 CI 沒呼叫 drift check 時照其他閘的慣例提醒」

1. 〈做法〉第 0 節與 [S14] 都把「doctor Z 段不跑 git」跟「接線後 CI 沒呼叫要提醒」寫在同一句/同一條款裡,第 0 節還把「不跑 git」當成明講的成本理由:「這樣每次推送多出的成本只有讀一遍筆記」。
2. 但「照其他閘的慣例」這句話點名的兩個既有先例裡,跟 drift-check 情境真正對應的是 note-audit(因為兩者都是「這道檢查可能還沒接線進推送前掛鉤」,要先判斷有沒有接線才知道要不要唸 CI 沒呼叫;note-shape 不用判斷接線與否,因為它從 repo 一開始就一定在 pre-commit 裡)。note-audit 的這段判斷寫在 `scripts/lumos:25106`:`hk = _lens_git(root, "show", f"HEAD:{_NOTELINES_PREPUSH}")`,接著在 `scripts/lumos:25107` 用 `_NOTE_AUDIT_GOLIVE_MARK in hk.stdout` 判斷有沒有接線——這是一次貨真價實的 git 呼叫,不是純讀筆記。
3. drift-check 是不是接線(推送前掛鉤裡有沒有出現 `drift check` 那個標記)本質上跟 note-audit 是不是接線同一種問題,同一種答法——要照著「其他閘的慣例」做,doctor Z 段就得跑至少一次 `git show HEAD:<hook 檔>`,跟「只讀筆記、不跑 git」正面衝突。
4. 這不是「兩處各退一步就好」的小事:第 0 節把「不跑 git」寫成效能承諾(每次推送多出的成本只有讀一遍筆記),如果實作為了滿足 CI 提醒功能偷偷加了 git 呼叫,這句效能承諾就是假的,未來有人拿這句話去驗效能會驗錯方向。
5. 修法:要嘛把「CI 沒呼叫時提醒」這半段明講成例外(允許一次輕量 `git show HEAD:<hook>`,並把「不跑 git」的效能承諾改成「不評估 probe 條件」這種更精確的說法,呼應第 0 節其實真正在意的是避免昂貴的 `git grep`/`ls-tree` 逐條件評估,不是零 git 呼叫);要嘛明講「drift-check 的 doctor CI 提醒不比照 note-audit 的先例,改成別的判法(例如只看 `.lumos/config.json` 或某個本地標記檔)」。目前兩句話同時成立不了。

## 已讀、無 finding 的部分(逐項列出核對過的東西)

- 條件文法(第 0 節「條件標記的文法」):`[when-<鍵>:<值>]` 只認 file/symbol/test/status 四鍵、值到第一個 `]` 為止、不含 `]` 與換行——跟既有的 `SINCE_REF_RE`/`UNTIL_REF_RE`/`STATUS_REF_RE` 等「每個標記各自一支 `\[鍵:...\]` regex」慣例(`scripts/lumos:2930-2934`)同構,不會被既有的 `\[status:...\]`(RULE 欄位用)regex 誤吃(`[when-status:...]` 裡「status:」前面是 `-` 不是 `[`,對不上 `STATUS_REF_RE` 的 `\[status:`)。
- `-e <值>` 與 `--` 隔開路徑防選項注入:既有 `git grep -w -F -e name <sha> -- <path>`(`scripts/lumos:31615`)、`git grep -c -F -e s tip -- path`(`scripts/lumos:24600`)已是established 慣例,drift 的 symbol/test/status 評估照抄可行。
- 「只在正文與摘要可見行生效」:`_notelines_regions`(`scripts/lumos:23522`)已經把每一行分類成 body/summary/decisions/other,decisions 欄位裡非結構鍵的行仍會被歸類成 `decisions`(不是 `other`),讓「條件標記寫在 decisions 欄要被擋」這條規則有明確的判準可用;圍欄/表格排除走 `_visible_lines`/`_search_visible_lines`(`scripts/lumos:3236`、`3298`),行內反引號排除有 `_strip_inline_markup`(`scripts/lumos:166`)可借——三者都已存在,不用重刻。
- 「同一行怎麼認」(改名對回、逐字比對):`_notelines_new` 的 `old_by`/`texts_by`(`scripts/lumos:23926` 起)已經是「範圍裡新寫、且終點版本還在」的既有實作,`_ns_diff` 帶 `-M`(`scripts/lumos:23570`)做改名偵測——跟 spec 描述的機制一致。
- `_nodehome_golive`/`_nodehome_clamp_base` 的 `mark`/`hook` 參數(`scripts/lumos:22956`、`22967`):spec 在 PRIOR-ART 段明講「推送前掛鉤裡的標記,不是提交前掛鉤」,對照 note-audit 傳入 `_NOTE_AUDIT_GOLIVE_MARK, _NOTELINES_PREPUSH`(`scripts/lumos:25127`)而非用預設值 `_NOTELINES_PRECOMMIT`——drift check 要仿照 note-audit 這處明寫 `hook=_NOTELINES_PREPUSH`,spec 文字已經講清楚要這樣做,無 finding。
- 閘名/開關命名慣例:`_KNOWN_GATES`(`scripts/lumos:6604`)目前沒有 `drift-check`,`.lumos/config.json` 既有 `note_shape`/`note_audit`/`node_home` 都是 `<snake_case>.gate`(`scripts/lumos:23511`、`24208`、`22309`)——`drift_check.gate` 符合既有命名法;`_BOOKKEEPING_FILES`(`scripts/lumos:20348`)目前沒有 `governance/drift-acks.jsonl`,但既有的都是逐一列舉單一 jsonl 路徑(如 `.kill-log.jsonl`),`governance/drift-acks.jsonl` 可直接比照加入,不用改資料結構。三者都是「現在沒有、要新增」的正常待實作項,不是 spec 缺陷。
- `LUMOS_SKIP_DRIFT_CHECK=1` 只認字面 `"1"`:跟既有 `LUMOS_SKIP_NOTE_SHAPE` 只認 `"1"` 的既有慣例(`_note_shape_config`/`cmd_note_shape` 呼叫處,`scripts/lumos:24099`)同構,無 finding。
- 淺層 clone 跳過:`git rev-parse --is-shallow-repository` 已在 note-shape(`scripts/lumos:24112`)、note-audit(`scripts/lumos:24414`)重複使用,drift check 借同一支可行。
- `guards` 欄位名:`GUARD_MARK_FIELD = "guards"`(`scripts/lumos:11459`)跟 S6/S7/S8 引用的「`guards` 欄」一致。
- `drift <子命令>` 的兩層 argparse 結構(check/scan/ack/exam):跟既有 `guard <gcmd>`(`scripts/lumos:33202-33203`)、`note-audit <nacmd>` 的巢狀 subparser 慣例一致,不會跟既有的單詞指令 `drift-history`(`scripts/lumos:33354`,連字號、非巢狀)衝突——兩者是不同的 argparse 節點,`args.cmd == "drift"` 與 `args.cmd == "drift-history"` 不會互相覆蓋。
- rc0/rc1/rc2 語意:跟既有 `note-shape`(`scripts/lumos:24081` docstring「有新違規 rc1,沒有 rc0;跳過 rc0」)、CLI 層 `--staged`/`--diff` 二擇一錯誤回 2(`scripts/lumos:33887-33894`)同構。
- c3/c4/c5 一致檢查判準跟 r2 折入的修正版一致:c3 排除空的/找不到的/非計劃的 `plan_refs`、排除帶 `guards` 欄的(對應 [S7]);c4 拿掉「工作樹」誤判(對應 CLAUDE.md 的「釘在某提交的乾淨工作樹」合法寫法);c5 新增。三者跟做法第 1.4 節文字一致,無交叉引用缺口。

## 考卷與改寫檔重驗(rtb 唯讀複本,`git -C`)

1. `rtb-2026-09-28.json` 33 題確認為列表、長度 33,`exam_event` 四種(commit/status_replay/probe/current_state)與 mechanism1_experiment 分布跟 README〈更正紀錄〉描述一致;B1 `invalidating_commits` 只剩 `['8ff8c95']`(單一提交,對應 r2 鏡像核對已補的修正),B3 已改成 `['f183cd8']`。
2. 重驗 A4:`note_at_event` 給的長檔名路徑在 `e606947` 確實存在(`git show e606947:"docs/.../2026-09-22_事故-F1-....md"` 讀得到),`git log --follow` 顯示它在 `e8ea7d0` 被改成短檔名——跟 README「A4、A5 的筆記在失效那時還是長檔名(之後 e8ea7d0 才改短)」的更正紀錄相符。
3. 重驗 B3(`rtb-2026-09-28-probes.json`):改寫後的 `[when-status:Projects/RTB_Phase12一鍵展示與HTML報告_計劃=doing|done]` 對應 `f183cd8` 新建 Phase 12 計劃筆記,`git show f183cd8:<路徑>` 讀到 `status: doing`(建立當下就是 doing,不是後來才改)——跟 probes 檔 `why` 欄「f183cd8 建立時 status 就是 doing」的說法一致。
4. 重驗 A6:`16136d6` 提交訊息「重複投遞的合約轉正,落在執行迴圈」跟 A6 對應的機制③(狀態指令連帶處理,考卷分類 mechanism=3)相符。
5. `status` 鍵的節點值(如 `Projects/RTB_Phase12一鍵展示與HTML報告_計劃`)是 vault-relative stem,不含 `docs/<project>-knowledge/` 前綴、不含 `.md`——跟 `link_target()`(`scripts/lumos:216`)的既有慣例一致,drift check 用同一套解析可行。

## 邊界輸入補充(低於 major 門檻,附一句判準,供實作留意)

- ⚠ `status` 鍵的節點值、`file`/`symbol`/`test` 鍵的路徑值,是直接從筆記正文文字取出、沒有經過 `nfc()` 正規化,而拿來比對的 `_nodehome_list` 回傳的樹路徑一律先 `nfc()` 過(`scripts/lumos:22536` 附近 `path = nfc(os.fsdecode(p))`)。中文檔名若因外部工具(非本機 git、非 macOS `core.precomposeunicode`)寫成 NFD,條件值跟樹路徑比對會不相等而靜默判成「不成立」——不是危險失敗(頂多條件永遠不觸發,不會誤擋人),拿不出會誤擋人或造壞資料的具體場景,只有「永遠不觸發」這種安全方向的靜默失效,spec 沒有明講這裡要不要 `nfc()` 正規化。
- 空檔:`_nodehome_parse_note`/`split_frontmatter` 對空字串會落到 `text.startswith("---")` 為 False 的分支、整篇當 body 處理(`scripts/lumos:6210` 附近邏輯的既有寫法),drift 的 REVISIT/probe 掃描對空檔只是找不到任何可見行,不會拋例外——沒問題。
- `[when-symbol:::foo]`(空路徑、`::` 出現在值最前面):spec 的路徑規則「不准 `/` 開頭、不准 `..` 段」對空字串是 vacuously true,沒有明講空路徑算不算「寫錯的條件」——這種寫法會被人手打出來的機率極低,拿不出具體誤判場景,不標成 finding,只留一句給實作者:建議明講「路徑段落若存在則不能是空字串」以避免行為未定義。

## 總結

最高等級 major,blocking 共 2 條(F1、F2)。
