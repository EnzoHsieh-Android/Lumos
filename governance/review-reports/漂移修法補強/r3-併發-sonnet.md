severity: major

審材:r3-snapshot.md 全文;對照 clone-ns 的 `scripts/lumos`。逐項驗「不新增寫入路徑」:成立。c3 `--reason` 走既有 `_drift_fix_write`(鎖內比指紋、`atomic_write_verify`);set 擋佔位字在 `cmd_set` 取鎖之後的 `_set_conditions_locked` 第一行,擋下時檔案沒動;c4 證據頁的兩次 git 查詢(`_plan_first_commit`、`git show`)在 `_drift_fix_c4` 裡跑,c4 不進 `_drift_fix_write`,整段在鎖外且不寫檔;刪除守衛只多一個跳過集合與 note 欄位。以下是仍找到的洞。

## F1 範本句的 sha 寫法沒定死,照字面做會繞過 set 的佔位字守衛
severity: major
blocking: 是
引句:「範本句改成「提交 <已知就填 sha>;代碼審見 <卷證>」——卷證一律放佔位字」
file: `scripts/lumos:27962`(現況:`sha[:12] if sha else '<sha>'`)、`scripts/lumos:27622`(`_DRIFT_PLACEHOLDER_RE` 只認精確字串 `<sha>`)
1. 這一句把範本寫成字面 `<已知就填 sha>`,不是 `<sha>`。[S1] 只釘了「卷證一律是 `<卷證>`」,沒說 sha 未知時印什麼。
2. 第 2 節與 [S2] 擋的是精確子字串 `<整項新內容>`、`<卷證>`、`<sha>`。`<已知就填 sha>` 不含 `<sha>`(少了緊貼的左尖括號),不會被擋。
3. 輸入:sha 查不到(shallow、git 逾時、驗證紀錄尚未進歷史)的 c4 證據頁。照字面實作,範本印出「提交 <已知就填 sha>;代碼審見 <卷證>」。使用者只換掉 `<卷證>`、忘了前半,`lumos set` 放行,`valid_under` 就寫進「提交 <已知就填 sha>」這種句子。範本句本來就是「整句貼進 set 時要被擋下」這個設計的唯一防線,防線和範本的字面不一致。
4. 實作者若自行沿用現有的 `<sha>` 就沒事,但 spec 沒寫、[test:t_drift_c4_reports_from_first_commit] 與 [test:t_set_conditions_blocks_drift_placeholders] 也都沒釘「sha 未知時的字面」。需要在 spec 裡寫死 sha 未知時就是 `<sha>`,並讓 S2 的測試以證據頁實際印出的範本句整句貼進 set 來驗。

## F2 「併發:不碰」漏掉 c4 走 set 之後,同一篇驗證紀錄的 c3 修正與 c4 修正互相卡住、以及錯誤建議會洗掉 set 的修改
severity: minor
blocking: 否
引句:「併發(不碰):不新增寫入路徑;set 的寫入與鎖照舊」
file: `scripts/lumos:27761`(`_drift_fix_clean_err`)、`scripts/lumos:27882`(`_drift_fix_verify` 的還原建議)
1. c4 的條件(valid_under 寫「還沒提交」)與 c3 的條件(plan_refs 都已收尾)常落在同一篇驗證紀錄上。c4 依 spec 只走 `lumos set`,不進修復帳、不留指紋。
2. 先 `lumos set` 改 c4、再 `drift fix --kind c3`:`_drift_fix_clean_err` 看到那一篇跟 HEAD 有差,而修復帳最後一筆指紋對不上,回「有未提交的改動(不是 drift fix 自己留下的)——先提交或還原再修」。使用者必須在兩種修正之間插一次提交。反過來先 c3、再 set:set 沒有乾淨檢查會寫成功,但那一篇的下一筆 drift fix 一樣被同一道檢查擋下。spec 的〈誠實界線〉只說「c4 不進修復帳」,沒講這個順序限制。
3. 最壞時序:會談 A 的 `drift fix c3` 剛完成 `_drift_fix_write`、鎖已放掉、還沒進 `_drift_fix_verify`;此時會談 B(同一工作目錄,鐵則允許)貼上 c4 的 `lumos set`(鎖是空的,立刻成功)。A 的驗證看到磁碟內容不等於預期,印出「在 repo 根目錄跑 git checkout -- … 退回上次提交的版本」。照做會把 B 剛用 set 寫進去的 c4 修正一起洗掉;這段警語只提到「這一篇之前用 drift fix 改過的」會一起退,沒提 set 的修改。時窗是毫秒級,機率低,但 c4 改走 set 之後這條路才真的開通。
4. 要求:誠實界線補一句順序(同一篇有 c3 與 c4 時,先提交再修下一項),不必加新機制。

## F3 「同提交」清單不驗目錄現在還在不在、也沒有統一 Unicode 寫法,「兩者」標記與去重可能錯
severity: minor
blocking: 否
引句:「證據頁全部列出、每個標來源(兩者、同提交、計劃名),排序:兩者 → `code-` 開頭 → 其他,同級照字母」
file: `scripts/lumos:27946`(計劃名清單用磁碟 `iterdir` 的名字)、`scripts/lumos:23631`(`_nodehome_split_z` 用 `os.fsdecode`,保留 git 裡的拼法)
1. 同提交清單來自歷史,計劃名清單來自現在的磁碟。歷史裡的目錄之後被改名或整理掉(governance 底下常整理),證據頁仍列出一個已不存在的路徑,沒有標「已不存在」。使用者從清單挑了就把死路徑寫進 valid_under,沒有東西檢查。
2. 兩份清單求交集、去重時,spec 沒寫先過 `nfc`。git 側的中文目錄名可能是 NFD 拼法(專案本身就為此有 `_git_paths_nfc`),磁碟側是另一種拼法時,同一個目錄會出現兩列、且都不標「兩者」。
3. 需在 spec 寫明:同提交清單先 NFC、再與磁碟存在性合併;不存在的標「(現已不存在)」。

## F4 `vendored-skip=` 的計數口徑與寫入位置會讓 RETIRE-IF ② 與 REVISIT 量到錯的東西
severity: minor
blocking: 否
引句:「`vendored-skip=<這次 diff 碰到並跳過的工具檔支數>`(沒碰到就不加)」
file: `scripts/lumos:29401`(`_delguard_log_result`)、`scripts/lumos:29383`(`_delguard_log_degraded`)、`scripts/lumos:29244`(`skip` 判定裡的 `.md`)
1. `_delguard_parse_diff` 現有的 `skip` 已包含 `.md` 結尾的檔,`_VENDORED_ALL` 有兩支 `scripts/templates/*.md`。這兩支即使不跳過也抽不出名稱,但依 spec 會被算進「跳過支數」。只改 templates 的更新提交會記出 `vendored-skip=2`,而實際沒有任何名稱被漏掉。RETIRE-IF ②「累計 ≥20 次」因此被空計數灌水,抽 5 次去看被刪名稱會找不到東西。口徑應寫成「真的因此少抽了名稱的檔」或至少排除 `.md`。
2. delguard 有三處寫治理事件:`_delguard_log_result`(ok/partial)與 `_delguard_log_degraded`(超時、內部錯誤,兩個呼叫點)。spec 只說「既有 delguard 治理事件的 note」,沒說降級那條要不要帶。整批工具檔更新(38k 行的 `scripts/lumos`)正是最容易撞 15 秒預算的提交;降級事件若不帶計數,就丟掉最需要計的那批。`_delguard_log_result` 目前也沒有可傳計數的參數,`_delguard_parse_diff` 的回傳(現在只有 tokens、vault_diffs)要多一個鍵,spec 沒寫接線。

## F5 c1 與 settle 「同一支組字函式」的字樣,套上現有名稱表會出現重複與對不上的詞
severity: minor
blocking: 否
引句:「字樣改成「找不到〈那一種〉的預告句——可能已經是轉正後的說法(不用改),或被手改過(看一下)」」
file: `scripts/lumos:12552`(`_GUARD_PROSE_NAMES`)、`scripts/lumos:12557`(settle 逐項各印一行)、`scripts/lumos:27839`(c1 把名稱用「、」串成一句)
1. 名稱表的值已經含「預告句」:「摘要的 TEST 預告句」,照 spec 字樣套進去成「找不到摘要的 TEST 預告句的預告句」。另兩項「正文「為什麼還不做:」」、「正文「做完之後跑 lumos guard settle 轉正」」根本不是「預告句」這個詞。〈那一種〉沒定義成名稱表的哪個欄位。
2. settle 現在一個缺項印一行,c1 把全部缺項串成一個訊息。「同一支組字函式」沒說輸入是單一鍵還是整批,S3 只測 c1,沒有覆蓋 settle 那條的字樣相同。
3. 另外,「可能已經是轉正後的說法(不用改)」對 c1 只在「缺的是別種句子」時成立(finding 本身是某一句預告句,所以存在的那句一定沒被判缺);若四種全缺則改寫結果與原檔相同,走到 `_drift_fix_verify` 會印「還沒處理掉…git checkout --」,跟新措辭「不用改」矛盾。這條屬既有行為,但新措辭放大了矛盾。

## F6 「工具檔本來就不該在消費專案被改」沒查證,而現有程式的說明寫的是相反
severity: minor
blocking: 否
引句:「工具檔本來就不該在消費專案被改(更新靠 `lumos update`)。」
file: `scripts/lumos:17726`(`_VENDORED_TREE_FILES` 上方 2026-09-10 註解)、`scripts/lumos:17765`(`_vendored_state` 說明)
1. 現有註解記錄 2026-09-10 代碼審 r1、r3:消費專案「自己改了工具裝進來的檔、或把自己的程式放成工具的檔名」是實際發生過的事,所以推送閘才驗指紋。名單裡的 `scripts/hooks/pre-commit`、`scripts/hooks/post-commit`、`scripts/hooks/pre-push` 是很常見的自家 hook 名稱。
2. 縮小成純路徑判斷是 r2 後的刻意裁決,我不建議加回指紋檢查。但誠實界線那句是無出處的斷言;要嘛換成「已知放過的情形:消費專案改過這些檔時」並保留 REVISIT,要嘛刪掉「本來就不該」這個前提。這條只影響提醒的精度(advisory、恆 rc0),所以不升級。

## 其餘節
- ★INVARIANT★ 合約行:Systems/guard-kill 兩條(rc 優先序、`--json` 純輸出)只碰 `guard kill`,這份設計不動 guard kill,不影響;Systems/lumos-cli-write、Systems/delguard、Systems/存量漂移守衛 沒有 ★INVARIANT★ 行,「delguard 恆 rc0」的 KEY 行沿用,設計沒有新增會回非 0 的路徑。
- c3 `--reason`:接線(`_DRIFT_FIX_ALLOWED`、`cmd_drift_fix` 分派已經把 `reason` 放進 `o`)沒有洞;理由過 `_drift_fix_shape_err`(因為併進 `texts`)。已讀,無 finding。
- 第 2 節 set 擋佔位字的位置(鎖內、第一道、檔案沒動):已讀,無 finding。整段機率極低的合法值被擋,誠實界線已寫。
- 實務隱患各類(不可逆、金流、對外送出、資安、效能):已讀,除上列外無 finding;`git show -z --name-only --diff-filter=AR --format=` 我在 clone 上實跑過,輸出是乾淨的 NUL 分隔路徑,合併提交不會被 `_plan_first_commit` 選為第一次提交。

最高等級:major;blocking 共 1 條
