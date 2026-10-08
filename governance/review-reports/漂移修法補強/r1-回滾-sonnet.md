severity: major

審查立場:上線後要收拾殘局的人。程式碼路徑 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos`(下稱 `lumos`)。前置掃描已報過的(--values 要加 argparse/ALLOWED、`--dry-run` 是否做乾淨檢查、`_vendored_skip` 不能直接用、set 錯誤訊息由誰印、c3 三種寫法)不重報。

## F1 --values 改寫後的值只要還含「未提交」類字,寫入成功卻被判驗證失敗,筆記被改髒、修復帳沒記、還被叫去 git checkout
severity: major
blocking: 是
引句:「用 `_conditions_rewrite(lines, fe, "valid_under", vals)` 算改後內容(有錯回 2);`res` 照 drift fix 的鍵組:`check=lambda f: _conds(f.get("valid_under")) == vals`、`handled=_drift_no_kind("c4")`」
file: `scripts/lumos:26376-26380`(c4 判定是 valid_under 全文含 `_DRIFT_UNCOMMITTED_WORDS` 就成立)
file: `scripts/lumos:28105-28119`(`_drift_fix_verify` 用 `handled` 重算,不過就回「寫入後內容跟預期不同…退回上次提交的版本」)
file: `scripts/lumos:28122-28150`(記帳在 verify 之後,verify 失敗就不記)
敘述:
1. c4 的判定是「valid_under 任何一項含 未提交/還沒提交/uncommitted」。人改寫時很自然會把舊說法引成歷史,例如「本工作樹(原寫未提交,已於 abc123 提交)」或保留「uncommitted」英文詞。`_conditions_rewrite` 只擋空值、多行、佔位字,不擋這個;spec 也沒有在寫入前先預測「改後 c4 還在不在」。
2. 走到 `_drift_fix_write` 時 `atomic_write_verify` 的 `check`(`_conds(...)==vals`)會過、檔案真的寫進去;接著 `_drift_fix_verify` 用 `handled=_drift_no_kind("c4")` 重建圖譜,c4 還在 → 回錯誤「寫入後內容跟預期不同(或這一筆還沒處理掉)」,rc2,並叫人 `git checkout --` 退掉。
3. 結果:(a) 人給的合法整句被工具當成「寫壞」,訊息完全沒說是哪個詞觸發;(b) 筆記已髒、修復帳沒有這一筆;(c) 因為帳上指紋對不上,同一篇下一次任何 drift fix 都被乾淨檢查擋下(「有未提交的改動(不是 drift fix 自己留下的)」),只能先 checkout。
4. `--dry-run` 在 spec 裡只預覽差異、不跑 handled 判定,所以預覽看不出會失敗。
5. 這是新路徑獨有的洞:舊流程(證據頁 + `lumos set`)不做寫後 handled 驗證,同樣的值 set 會成功。回退時也帶不走:修法要在 `_drift_fix_c4` 寫前預跑 c4 判定,那是新增邏輯,不在〈回退〉列的任何一項裡。
建議:寫入前先對算出的內容判 c4(或在 `_conditions_rewrite` 外加一道「新值含關鍵詞就擋下並點名是哪個詞」),擋在寫檔之前;條款 S2 補這一格。

## F2 〈回退〉c4 那一條漏列的實作點與測試/文件,照抄拿不乾淨
severity: major
blocking: 是
引句:「c4 退回只印 `lumos set` 指令(`_drift_c4_print` 的指令與 `--values` 一起拿掉,`_conditions_rewrite` 可以留著,set 行為不變)」
file: `scripts/lumos:27678-27680`(`_DRIFT_FIX_OPTS`、`_DRIFT_FIX_ALLOWED["c4"]`)
file: `scripts/lumos:37587-37598`(argparse `--values`)、`scripts/lumos:38093-38098`(dispatch 組 `o` 字典)
file: `scripts/lumos:27792`(`_drift_fix_load` 的 `kind != "c4"` 乾淨檢查排除)
file: `scripts/lumos:27653`(`_drift_fix_hint` c4 那行「列證據、範本與預填好的 lumos set 整欄指令」,drift check/scan/doctor 共用)
file: `scripts/test_lumos.py:53466-53510`(`t_drift_fix_c4_evidence_then_replace`,斷言 ②③④⑤都依賴「證據頁印 lumos set 指令」)
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:18`(WHY 綁 `[test:t_drift_fix_c4_evidence_then_replace]`)
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:44,77`、`skills/lumos-project-notes/commands/04-自檢與健康.md:11`(都寫「c4 只列證據與一條預填好的 lumos set 指令」)
敘述:
1. 〈回退〉只點了 `_drift_c4_print`、`--values`、`_conditions_rewrite`。實際要動的還有:ALLOWED/OPTS 兩個常數、argparse、dispatch 字典、`_drift_fix_load` 的乾淨檢查條件(--values 上線要改它,回退要改回)、`cmd_drift_fix` 的 `res is None` 分支(c4 回傳形狀變了)、`_drift_fix_c4` 的雙形狀回傳。漏改任何一個,回退後 `--values` 仍被 argparse 收下但走不到有意義的路徑,或 `_DRIFT_FIX_ALLOWED["c4"]` 殘留導致 `drift fix --kind c4 --values` 靜默被當成證據頁(不寫檔卻 rc0)。
2. 現有測試 `t_drift_fix_c4_evidence_then_replace` 斷言證據頁印的是 `lumos set` 指令。上線後這支必須改寫(spec 條款只新增測試名,沒說既有測試怎麼處理);回退時要還原回舊版。它同時是 lumos-cli-write 那條 WHY(set 擋 `<整項新內容>` 佔位字)的綁定測試:改寫或改名會讓那條綁定失效或變成不再真的執行 `lumos set` 擋佔位字,回退也要一起還原。〈回退〉沒列測試與這條綁定。
3. 三處文件(存量漂移守衛 PITFALL/操作段、04-自檢與健康、`_drift_fix_hint` 的 c4 說明)現在都講「只列證據 + lumos set」。〈做法〉只說證據頁改印 drift fix 那條,沒列這些文件要同步;`_drift_fix_hint` 尤其重要:drift check/scan/doctor 印的「改法」還是舊字,上線後說謊(說會印 set 指令,實際印的是 drift fix --values 指令),〈回退〉也沒把它算進來。

## F3 混版:新版證據頁印出的 `--values` 指令拿到舊版機器跑,直接 argparse 失敗;而且反方向沒有降級路徑
severity: minor
blocking: 否
引句:「不帶 `--values`:照舊只列證據與預填指令,不做乾淨檢查;指令改成 `lumos drift fix <節點> <行號> --kind c4 --values …`」
file: `scripts/lumos:37589-37596`(舊版 `drift fix` 沒有 `--values`)
file: `scripts/lumos:27725-27727`(舊版對不認得的旗標另有「不收」錯誤)
敘述:
1. 證據頁被複製到另一台仍是舊版的機器(rtb 與工具鏈 repo 兩台機器版本本來就會不同步;分發靠各自安裝)時,指令跑出 argparse 的「unrecognized arguments: --values」rc2,沒寫任何東西,安全但訊息無從得知是版本問題。
2. 證據頁一旦改成只印 drift fix 條,舊版機器上的人就沒有 `lumos set` 可貼;spec〈做法〉寫「`lumos set … 照舊可用`」卻不在證據頁提,新版使用者遇到乾淨檢查擋下(筆記有未提交改動;c4 新流程要求乾淨,舊流程不要求)時也沒有印出的退路。建議證據頁末行保留一句「筆記不乾淨或版本較舊:改用 lumos set <節點> valid_under …」。
3. 反向(舊工具讀新工具寫的修復帳)沒問題:舊版只讀 `path`/`after_sha256`/`seq`(`_drift_fix_last_sha`、`_drift_next_seq`),多出的 `reports`、`reports_via`、`template_used` 鍵與 `kind: c4` 都被忽略;`lumos:21481` 只把整檔列為簿記白名單。已驗,不構成 finding。

## F4 RETIRE-IF ① 的量法會把「本來就沒有卷證」誤算成找法失敗;RETIRE-IF ② 沒有任何能被觀察到的觸發
severity: minor
blocking: 否
引句:「①修復帳裡 c4 的 `reports_via` 在工具鏈與 rtb 合計有一半以上是 `none`(兩種找法都查不到)→ 撤掉同提交找法、改回只給範本」
引句:「②刪除守衛因工具檔跳過而漏掉真的過期句(有人回報)→ 改回全比對、另找降噪法」
file: `scripts/lumos:26379-26381`(c4 只看「valid_under 寫還沒提交」,跟這條變更有沒有走過代碼審無關)
敘述:
1. c4 出現的原因是「前提寫了還沒提交」,跟這次改動有沒有代碼審卷證沒有關係;light 級改動根本沒有 `governance/review-reports/<目錄>`。這種情形兩種找法必定都是 `none`。`reports_via: none` 混合了「找法失敗」與「本來就沒有」,一半以上 none 就撤機制,會把運作正常的找法撤掉。撤掉條件需要分母是「有卷證目錄存在的 c4 筆」,帳裡目前沒有這個資訊(要不要另記一欄 `reports_expected`)。
2. 兩個月的樣本量:rtb 2026-09-30 一次修 26 筆只有少數 c4,「一半以上」在 N 很小時單筆就翻盤;REVISIT 沒寫最小 N。
3. 帳只在帶 `--values` 寫入時才寫,只看證據頁的不會留帳,量出來的是「有人採用了證據」的子集,偏向找得到的情形。
4. ② 的觸發是「有人回報漏掉」,但守衛是「只提醒不擋」,漏報在定義上就是沒有輸出,沒有人看得到自己漏了什麼;〈誠實界線〉REVISIT:2026-11-30 又只等「拆除工具鏈被誤報」,那是另一個方向(誤報,不是漏報)。〈CLAUDE.md〉鐵則 4 要求承認風險要附能接電的回頭條件:這裡沒有。可行的接電法:被跳過的工具檔在治理帳記一筆「delguard 跳過 N 支/被刪 token M 個」,回頭時抽樣看被跳過的 token 有沒有在 vault 裡被提到。

## F5 c1/settle 新判定:回退時訊息與測試同源,另有既有程式已處理一半,〈做法〉寫得像全新需求
severity: minor
blocking: 否
引句:「WHY:沿用既有 `why-done` 的辨認(行尾「(日期 已轉正)」);whynot:正文有「預告當時」開頭的行;settle:正文有「(日期 已轉正)」那一行,或既有 `settle-del` 已判出下一行是手補的「已轉正」段。」
file: `scripts/lumos:12136-12162`(`_guard_settle_rewrite` 已把 `why-done`、`settle-del` 記進 `seen`,不會進 `missing`)
file: `scripts/lumos:12552-12558`(`_GUARD_PROSE_NAMES` 與 settle 的「找不到…(被手改過?)」原句)
敘述:
1. WHY 與 settle-del 兩種「已轉正」目前根本不會出現在 `missing`,所以現行訊息只會對 TEST 與 whynot 與(日期 已轉正)那條 settle 句誤報。新判定實際只需要補 TEST、whynot、settle-done 三種;WHY 與 settle-del 那兩列是冗餘,實作者照字面再寫一次會與 `_guard_settle_rewrite` 的 `seen` 邏輯產生兩套判定,回退或日後改預告句樣板時容易只改到一邊。
2. 回退:「c1 與 settle 的訊息各自拿掉」沒列測試 `t_drift_fix_c1_already_settled_message`(新)以外,還有既有斷言「找不到…被手改過」字樣的測試需要跟著改回;兩處(c1 的 `找不到{names},沒改` 與 settle 的 `_guard_settle_missing_say`)字串不同,要各自還原。
建議:〈做法〉3 的判定改成單一「在 `_guard_settle_rewrite` 裡多辨認已轉正的三種形狀,算 seen」,訊息端不另設第二支 `_guard_prose_settled`。

## F6 刪除守衛跳過工具檔:對「安裝清單沒一起提交」與「回退」兩個場景沒說
severity: minor
blocking: 否
引句:「不是才取 `_vendored_state(root, "")[0]`(讀索引裡的檔與 `.lumos/vendored.json`),得到「跟安裝清單一致」的工具檔集合。」
file: `scripts/lumos:17765-17818`(`ref=""` 走 `git show :<path>`,清單也讀索引版)
file: `scripts/lumos:24477,24609`(同慣用法已有兩處呼叫,這條前提已驗)
敘述:
1. 已驗:`_vendored_state(root, "")` 讀索引是既有慣例(筆記形狀擋兩處同用法),`_json_at_ref(root, "", …)` 得到 `git show :.lumos/vendored.json`,可用。
2. 消費專案升級工具時,若只 `git add scripts/lumos` 而沒把更新後的 `.lumos/vendored.json` 一起加進索引,索引裡工具檔是新版、清單是舊指紋,`_vendored_state` 判不一致,不跳過,回到全部誤報。這是「寧可誤報」的安全方向,不是 bug;但〈誠實界線〉只說「清單壞掉」,沒說「清單與工具檔沒一起暫存」這個最常見的原因。文件精度。
3. 回退:`_delguard_parse_diff` 加 `skip` 參數、兩遍改動、`cmd_delguard_check` 呼叫端各一處;拿掉時 `skip` 預設空集合本身向下相容,單獨還原沒有牽連。已驗,回退乾淨。

## 已驗、判不影響的合約
- `Systems/guard-kill` 的兩條 ★INVARIANT★(rc 優先序、`--json` 成功時 stdout 恰一行 JSON):這份設計不碰 `guard kill`、不改它的輸出與 rc,不影響。
- `Systems/lumos-cli-write`:沒有 ★INVARIANT★ 行,但有一條 WHY 綁 `t_drift_fix_c4_evidence_then_replace`(set 擋佔位字)。〈做法〉2 把佔位字檢查搬進 `_conditions_rewrite`、set 呼叫它,行為不變則不破壞;但綁定的測試要改寫時該條 WHY 的綁定會受影響(見 F2 第 2 點)。
- 舊工具讀新修復帳:安全(見 F3 第 3 點)。
- 消費專案升級後 `lumos set` 舊習慣:仍可用、行為不變,但不記修復帳;之後同一篇再跑 drift fix 會因帳上指紋對不上而被乾淨檢查擋下(既有行為,新流程不改變也不新增這個坑;證據頁不再提 set 之後,這個提醒也消失了,見 F3 第 2 點)。

## 沒有問題的節
- 〈範圍〉、〈實務隱患〉(金流/對外送出/併發:c4 走既有鎖與指紋比對、卷證目錄名印前過 `_esc_clean`):已讀,無 finding。
- 〈做法〉1 的 git 呼叫(`--format=` 去標頭、`core.quotePath=false`、`-z`):已讀,無 finding(`_lens_git` 固定 20 秒逾時,「有逾時」屬實)。

最高等級:major;blocking 共 2 條
