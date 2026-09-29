severity: major

審查立場:三個月後照這份 spec 與它產生的訊息做事的人。實驗在 /tmp/x1/r(自建臨時 git repo,未動 clone-ns)。

## F1 RETIRE-IF ① 的 `git log -S 'valid_under'` 找不到任何 c4 修正提交
severity: major
blocking: 是
引句:「用 git 找 5 筆 c4 修正的提交(`git log -S 'valid_under' -- <驗證紀錄目錄>`)」
file: `scripts/lumos:15128`(`_set_conditions_locked`:整欄重寫只換各項內容,`valid_under:` 這個鍵名在檔內出現的次數不變)
1. `-S` 是「字串出現次數有增減」才算命中。c4 修正的內容是把「還沒提交」那一項換成「提交 <sha>;代碼審見 …」,`valid_under` 這個詞在檔內次數沒變。
2. 實測:建一篇帶 `valid_under:` 兩項清單的驗證紀錄、提交;再把第一項改成「提交 abc;代碼審見 x」提交。`git log -S valid_under` 只列出建檔那筆,改寫那筆沒有;`git log -G valid_under` 一樣只列建檔那筆(鍵名那行沒被改到,清單各項行才變);只有 `-G '還沒提交'` 兩筆都列。
3. 照抄這條指令的人會拿到「建檔提交」而不是「c4 修正提交」,永遠湊不到 5 筆修正,結論只會落在「樣本不足、順延兩個月」,RETIRE-IF ① 永遠不會觸發撤除也不會確認,等於沒接電。
4. 附帶:c4 修正完成後 finding 就消失,`drift fix --kind c4` 不能再跑一次「重印證據頁」;RETIRE-IF 要人對照「同提交清單」,spec 沒寫改用什麼指令重現(可用 `git show -z --name-only --diff-filter=AR --format= <首次提交>`,我實測輸出與證據頁該清單同源),照抄的人得自己想。

## F2 RETIRE-IF ② 與第二個 REVISIT 的量法在工具鏈 repo 裡永遠量到 0,而且帳上沒有「抽 5 次」需要的資料
severity: major
blocking: 是
引句:「REVISIT:2026-11-30 量上面兩個數:①照上面的 `git log -S` 找樣本(rtb 那邊由本工具鏈的會談用跨會談訊息請 rtb 會談回報);②`grep 'vendored-skip=' docs/.governance-log.jsonl`」
file: `scripts/lumos:1242`(`_append_governance_log`:帳檔寫在 `vault.parent/.governance-log.jsonl`,也就是被提交那個專案自己的 docs/)
file: `scripts/lumos:29423`(`cmd_delguard_check`:工具鏈本身 `skip` 為空,不會寫 `vendored-skip=`)
1. `vendored-skip=` 只會在消費專案(rtb 等)的提交時寫,寫進那個專案自己的 `docs/.governance-log.jsonl`。在工具鏈 repo 跑這條 grep,`skip` 為空、從不加這個字樣,結果恆為 0(我在 clone-ns 的帳檔實測 `grep -c vendored-skip` = 0)。①有寫「請 rtb 回報」,②沒寫,照抄跑出 0 次,會被讀成「累計不到 20 次、沒事」。
2. 就算在 rtb 那邊跑,RETIRE-IF ② 後半要「抽 5 次被跳過的檔、看同一次提交刪掉的名稱」:帳上該事件只有 `commit`(= pre-commit 當下的 HEAD,即上一個提交,不是這次要提交的那個)、`nodes`、`note`(計畫只加一個支數)。被跳過的是哪幾支檔、被刪的名稱是哪些,都沒記;要事後重建得猜「HEAD 之後的下一個提交」,提交被中止再重來或另一個工作樹先提交就對不上。spec 沒說怎麼從帳事件回到那次提交。
3. 判準「有任一次是真的過期舊句 → 改回全比對」沒定義什麼算真的過期舊句。工具更新那種整批換檔的提交,刪掉的名稱拿去 `lumos search` 幾乎必定撞到某些筆記,「任一次」在 5 次抽樣裡近乎必然成立,會把剛拿掉的誤報整個換回來。
4. 帳事件本身:`vendored-skip=` 只加在 `_delguard_log_result`(掃完的 ok/部分結果)那條路;超時降級走 `_delguard_log_degraded`,note 只有 reason 與 tokens,spec 沒說降級時要不要帶跳過數,累計會漏這類事件。

## F3 範本句的 `<已知就填 sha>` 是哪個字串沒講清楚,字面實作不會被 set 擋
severity: minor
blocking: 否
引句:「範本句改成「提交 <已知就填 sha>;代碼審見 <卷證>」——卷證一律放佔位字」
file: `scripts/lumos:27619`(`_DRIFT_PLACEHOLDER_RE` 只認 `<sha>`、`<卷證>`、`<為什麼…>`)
1. 現行程式在查不到提交時印 `<sha>`(`_drift_c4_evidence`),查到就印 12 碼 sha。spec 寫的「<已知就填 sha>」是描述還是要印的字面?若被字面實作,印出的 `<已知就填 sha>` 不含 `<sha>` 子字串,第 2 節新增的檢查與 `_drift_placeholder_err` 都擋不到,照貼會把佔位字寫進 valid_under。
2. 測試 `t_drift_fix_c4_evidence_then_replace` 目前對「查不到提交」那支沒有案例,收斂的字串要在 [S1]/[S2] 的測試裡各釘一次。

## F4 c1 與 settle 訊息「找不到〈那一種〉的預告句」會疊字,而且兩處現在的輸出形狀不同
severity: minor
blocking: 否
引句:「字樣改成「找不到〈那一種〉的預告句——可能已經是轉正後的說法(不用改),或被手改過(看一下)」」
file: `scripts/lumos:12552`(`_GUARD_PROSE_NAMES`:值本身已是「摘要的 TEST 預告句」「摘要的 WHY 預告句」)
file: `scripts/lumos:12558`(`_guard_settle_missing_say`:每種缺的各印一行)
1. 名稱表的 test、why 兩項已含「預告句」,照字面套會印出「找不到摘要的 TEST 預告句的預告句」;whynot、settle 兩項是「正文「…」」,後面接「的預告句」也不通順。
2. `_drift_fix_c1` 把 missing 用「、」串成一句、settle 是一種一行,「同一支組字函式」要能同時做兩種呼叫,spec 沒講函式簽章(收 list 還是單一種),兩處「字樣相同」的 S3 測試只比字樣時可能各寫各的。
3. rtb 第三條實際結果:訊息不再像出錯,但 c1 的 `msg` 仍以「沒改」收尾(「;找不到…,沒改」),spec 回退段也保留這個字;人讀到「沒改」加「不用改」,兩句並排意思有點打架,可由測試釘句。

## F5 證據頁「全部列出」與實際印出被截斷不一致;預填指令超長時貼出去會壞
severity: minor
blocking: 否
引句:「證據頁全部列出、每個標來源(兩者、同提交、計劃名)」
file: `scripts/lumos:27953`(`_drift_c4_print`:`_esc_clean(... , 300)` 與 `_esc_clean(f"lumos set …", 2000)`)
1. 現行每種清單過 `_esc_clean(…, 300)`,同提交清單遇到整批匯入(首次提交常是專案骨架提交)可能上百個目錄,300 字後直接「…」,標來源與 >3 提示的排序只有前面幾個看得到,「全部列出」不成立。spec 沒說改成一行一項或加上限說明。
2. 預填指令 `_esc_clean(…, 2000)`:valid_under 各項合計超 2000 字時,指令被截成半句加「…」;整欄重寫的 lumos set 若剛好切在兩項之間(「…」黏在最後一個字上),貼出去少掉後面各項、整欄被改短,而且 set 不會發現。spec 說「這次不改它的展開與長度處理」,但證據頁要人「照貼」,截斷時至少該印警告,不然是無聲丟項。機率低,只在長前提出現。

## F6 文件同步清單漏列幾處會過期的地方
severity: minor
blocking: 否
引句:「[[Systems/存量漂移守衛]]、[[Systems/lumos-cli-write]]、[[Systems/guard-kill]]、[[Systems/delguard]] 的新句子與 lumos-project-notes 的 commands/04、commands/08 對應處一起改回」
file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:11`(講 `lumos set valid_under` 的行,新擋兩個佔位字要寫)
file: `skills/lumos-project-notes/commands/04-自檢與健康.md:11`(c3 只寫 `--status <值> [--by <節點>]`,少 `--reason`)
file: `skills/lumos-project-notes/commands/02-動手前算波及.md:15` 與 `skills/lumos-project-notes/commands/INDEX.md:17`(講 delguard 的行,消費專案不看工具自裝檔)
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:19`(講 guard settle 的行,訊息字樣改了)
1. 04、08 之外,上面這四處也會描述被改的行為,03 是 `lumos set` 的家、04 的 c3 參數列表是照抄就會用到的地方(照 04 寫的 `--status … --by …` 的人不會知道有 `--reason`)。
2. `_drift_fix_hint` 對 c3 印出的預填指令(`scripts/lumos:27660` 一帶)只有 `--status <…>`,新增 `--reason` 後 spec 沒說提示要不要帶,rtb 第四條要能被發現,得在提示或 04 其中一處寫到。
3. `Systems/存量漂移守衛` 的 WHY 行(41 行)現在還寫「c4 只給證據由人給要換的片段」,跟現況(預填 lumos set 整欄)已不同,這次改 c4 段落時要一併改,spec 沒點名。
4. 第 1 節 c4 的回退寫「範本自動填目錄」,但現況範本已經會自動填(`_drift_c4_evidence`),回退句正確;但 RETIRE-IF ① 撤除後沒有說證據頁要不要一併不印「同提交」標籤,實際回退步驟以「回到只用計劃名」為準,不需另處理。

## rtb 五條照這版做完的實際結果

1. c4 卷證目錄找不到:改成同提交與計劃名兩種都列、標來源、範本留 `<卷證>`,由人挑。前提是「驗證紀錄第一次被提交」的提交裡同時有卷證;我用臨時 repo 實測 `git show -z --name-only --diff-filter=AR --format=`:中文目錄名照原樣、改名進來的列新路徑、根提交也能列;`diff.renames=false` 時改名會以 A 出現,一樣被收。屬實,誠實界線的說法成立(驗證紀錄另外提交時同提交清單為空,只剩計劃名比對)。
2. c4 帳上少紀錄:沒有補帳,c4 走 `lumos set`,稽核靠 git(而 F1 顯示要靠 git 找也得換指令)。誠實界線的寫法屬實。
3. c1 訊息像出錯:只改字,判定與 `msg` 的「沒改」仍在(見 F4)。
4. c3 沒辦法寫理由:接線後可用,但提示與 04 文件不會告訴人有 `--reason`(見 F6)。
5. 刪除守衛誤報工具檔:只在 `_is_toolchain_repo` 為假的消費專案生效,且要 rtb 先 `lumos update` 換到新版 pre-commit 才有效;誠實界線第 4 條講到不看工具檔,沒講「跳過數只計在消費專案自己的帳」(見 F2)。

## 其他節
- 範圍、依據、PRIOR-ART、條款 S1–S5 內部交叉引用:已讀,無 finding。
- 實務隱患各類(不可逆、金流、對外送出、守衛面、資安、效能、併發):已讀,無 finding;資安一項我核對 `_esc_clean` 已用於目錄名,範本不自動帶目錄名屬實。
- ★INVARIANT★:guard-kill 兩條(rc 優先序、--json 純度)這份設計不碰 `guard kill` 的路徑,不影響;lumos-cli-write 沒有 ★INVARIANT★ 行(以 grep 確認)。

最高等級:major;blocking 共 2 條
