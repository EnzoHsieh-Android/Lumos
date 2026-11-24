severity: minor

我沒找到會讓呼叫端壞掉或拿掉守衛的缺陷。審了這個包的八個角度,逐項結果如下。

- **逐行與被刪掉的行為:** 把 `cmd_guard_kill` 原本逐支迴圈裡「套壞法、等新的一秒、還原、讀回修改時間、記弱證據」逐段對照 `_kill_merge_apply`、`_kill_merge_restore`、`_kill_merge_emit`,不變式都補回了。
  - 守衛順序沒變:`old` 守衛、`_count_overlapping`、`new` 守衛、`_kill_mutated`。
  - 弱證據的三個來源都在:單支基準帶不明、還原後修改時間沒錯開、已有還原沒錯開的檔。
  - 還原失敗會讓這組作廢。
  - 單支基準不綠仍交 abort 列。
  - `flaky`、整套一起跑這兩種情況在 `_kill_merge_ready` 就擋掉不合併。
- **跨檔追蹤:** 改過簽名或回傳形狀的函式,我都找了呼叫端。
  - `_kill_run`、`_situation_rule_signals`、`_choice_event_extra` 的新參數都放在最後且有預設值。
  - `_choice_kill_ledger` 回傳多一格,唯一呼叫端 `cmd_choice_kill` 已同步改。
  - `_ChoiceKillRun` 在測試裡直接建構,新參數 `merge` 預設為 True,不影響。
  - 「存活(合併快篩判)」只出現在 `choice-points` 的顯示,沒有程式拿它跟字串比對。
  - `_gov_event_types_ok` 只在讀端驗型別,寫端沒有欄位白名單,新欄位不會被擋。
- **手冊與筆記:** `--no-merge`、撤放行的路徑 `_LINT_NEW_WAIVERS_REL`、四個 `[test:]` 測試名都對得上。

以下是剩下的候選,都是 minor。

1. 判法記了兩份,其中一份沒人讀,另一份有死分支
severity: minor
blocking: 否
引句:「row["judged"] = "merged" if res.get("group") in self.merge.survived.get(res.get("platform"), ()) else "single"」
file: `scripts/lumos:28701`
- 這行把 `row["judged"]` 放進交給 `on_row` 的列。`_ChoiceKillRun.on_row` 沒讀它。
- 真正記帳用的是 `finish()` 自己用 `merge.survived` 重算的 `judged`。
- `finish()` 裡 `p.get("plats") if p.get("plats") is not None else {...}` 的後半段是死碼,因為 `add()` 一律會設 `p["plats"]`。
- 代價:判法有兩個推導處,日後改判準只改一邊,列上的值和帳上的值就會分岔。
- 建議:要嘛讓 `finish()` 從列取判法,要嘛刪掉列上那一欄。

2. 合併快篩對「這個壞法沒有任何單支基準綠的測試」也照開一次,而且記成 merged
severity: minor
blocking: 否
引句:「judged = "merged" if self.merge is not None and plats and all(loc in self.merge.survived.get(q, ()) for q in plats) else "single"」
file: `scripts/lumos:78914`
- 走到的路徑如下。
  - 一個壞法在該平台的測試基準全紅,其他壞法的測試基準有綠。
  - `lane` 是整個平台組的聯集,所以 `_kill_merge_screen` 照樣套壞法、跑一次完整合併呼叫。
  - 通過後 `_kill_merge_emit` 只交 abort 列,同時把該壞法的 group 加進 `mg.survived`。
  - `finish` 判成 no_result 的「基準不綠」,卻把 judged 記成 merged,run 那筆的 `merged` 計數也多一。
- 原本逐支流程對這種壞法不會花任何 Gradle 時間。
- 代價:白花一次完整合併呼叫,而且 RETIRE-IF 讀的 merged 數被灌水。
- 建議:套壞法之前先看這個 chunk 有沒有任何在 `lane` 裡的測試,沒有就直接交 `abort` 列、不開快篩。

3. 斷路器不計「有失敗」,被殺掉的壞法每個都多花一次完整合併呼叫,沒有自動關閉的機制
severity: minor
blocking: 否
引句:「計數的那幾類加一,到門檻就這次呼叫這個平台停用合併;其餘不計不歸零」
file: `scripts/lumos:28970`(補丁中 `_kill_merge_breaker` 的 docstring,行號為新檔近似值)
- 情境:多數壞法其實會被測試殺掉。
  - 每個壞法先跑一次完整合併呼叫得到 fail,再走原本逐支流程。
  - 開跑前還要先量齊全部單支基準和合併基準,原本是用到才量。
- 兩個壞法都在第一支測試被殺時,舊流程是 1 次基準加 2 次壞法;新流程是 N 次基準加 1 次合併基準加 2 次完整快篩加 2 次逐支。
- 目前的守衛只有「少於 2 個壞法不合併」和時限,斷路器完全不看 fail 的比例。
- 這是設計取捨,「加速重點在存活」的前提在殺掉率高時不成立。
- ⚠ 交編排者決定要不要加一條「連續 fail 太多也停用」的回頭條件。

4. 第一個訊號在 Popen 完成到登記之間到來,收不掉合併程序
severity: minor
blocking: 否
引句:「proc._lumos_merge = True   # 先標再登記:回呼看得到它時一定已帶標記」
file: `scripts/lumos:28194`
- 走到的路徑如下。
  - `proc = ... _popen()` 回來後、`_KILL_RUN_LIVE[proc.pid] = proc` 之前,Python 的訊號處理器可以插進來。
  - `on_signal` 掃 `_KILL_RUN_LIVE` 看不到這支程序,就不會 `_kill_proc_group`。
  - 這次合併呼叫會跑完整個 2.5 到 5 分鐘,才在 `mg.interrupted` 檢查點丟 `_KillHalt`。
- 「先標再登記」只補了標記和登記之間的空窗,Popen 到登記之間的空窗還在。
- 機率低,後果是拖過對話工具的寬限期。
- 我沒有重現,只是順著程式走出來的。

5. 筆記 WHY 帶了過程紀錄與已過時的複雜度數字
severity: minor
blocking: 否
引句:「[出處:2026-11-23 代碼審派審前 lint-new]」
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md`(補丁第 34 行那條 WHY)
- 專案 `CLAUDE.md` 寫「過程紀錄(哪天做了什麼、第幾輪折了什麼)不寫進筆記」。
- 那條 WHY 的 `[因:]` 還列了「_kill_merge_screen 17、_choice_merge_classify 13」這兩個拆分前的數字。
- 代價:`_choice_merge_classify` 目前仍存在、沒有被拆成別的函式,下一個讀的 AI 會以為那個數字是現況。
- 建議:把「新增告警閘擋複雜度超過 10、先例是拆函式」留作因,拿掉日期和數字。

總結:最高嚴重度 minor
