severity: major

# 整合與知識同步鏡頭審查(d1,對 /tmp/照留表態-r1.md)

程式碼對照 repo:/Users/enzo/harness/lumos-b1(唯讀;未跑測試,只讀原始碼)。以下 `scripts/lumos`、`scripts/test_lumos.py` 都在該 repo 下。

## F1 首次擋下沒有「照留要綁去處」的提示,照擋訊息貼指令會原地打轉
severity: major
blocking: 是——實作照 spec 寫會讓使用者依訊息操作後仍被擋,判準是主要使用流程走不通。
spec 段落:做法第 6 點、驗收 S4。
引句:「同一次推送補了沒綁去處的照留時,drift check 應 照擋並印」
問題:第 6 點只在 `dead_ack` 存在時才印那句提示(`born_now` 而且那筆照留沒綁去處);但 `dead_ack` 要「有對得上的照留」才有。第一次擋下時還沒有任何照留,走的是現有固定提示:`scripts/lumos:34713`(probe 改法)、`scripts/lumos:34717`(retire 改法)、`scripts/lumos:35722`(retire 固定段)、`scripts/lumos:35771`(c1~probe 固定段),四處都印 `lumos drift ack <節點> <行號> --kind probe|retire --reason "<為什麼照留>"`,完全沒有 `--tracked-in`。
具體例:rtb 推送新寫一行條件已成立的 REVISIT → 擋下 → 照貼指令表態 → 帶 30 天 `until`、提交 → 再推 → 因 `born_now` 只認 tracked_in,又被擋,這時才第一次看到「要綁去處」。S4 的測試只驗「補了沒綁去處的照留 → 擋並印」,不驗第一次擋下的提示,測不到這個缺口。
要補:`born_now` 的發現第一次列出時就印帶 `--tracked-in` 的指令與原因;上述四處提示(含 `_drift_fix_hint` 的 probe/retire 兩支)都要改,spec 一處也沒列。

## F2 說明文字與 skill 速查沒列,而且有一條現有說法會變成錯的
severity: major
blocking: 是——知識同步清單漏列,三個月後讀說明的人會被舊句誤導;`04-自檢與健康.md` 那句直接與新規則矛盾。
spec 段落:做法第 7 點(只列 Systems/存量漂移守衛、Systems/lumos-cli-lifecycle)。
問題:要同步卻沒列的地方:
- `scripts/lumos:46102` 的 help 字典 `"drift ack"` 說明(沒提 `--tracked-in`、30 天期限)。
- `scripts/lumos:46999` 起 argparse `dra` 的新旗標 help。
- `scripts/lumos:2674` doctor 的 advice 字串 `照留:lumos drift ack <節點> <行號> --kind <種類> --reason "…"`。
- `scripts/lumos:34532` `cmd_drift_ack` docstring。
- `skills/lumos-project-notes/commands/04-自檢與健康.md:13`(「這一行確定照留」那列)寫「表態後標記照印,不會因表態消失」「被標了就改成真的會發生的條件或刪掉,不是表態」,新規則下 probe/retire 的 born 可以綁去處照留、會到期失效,這句要改;`skills/lumos-project-notes/SKILL.md`、`commands/03-寫回圖譜.md:52`(「條件已成立、但待辦還要留著提醒,用 `lumos drift ack` 表態」)也提到 drift ack,都要補期限與 `--tracked-in`。
- Systems/lumos-cli-lifecycle:我 grep 該節點沒有 `drift ack`/`照留`,第 7 點「若列了…先查」的答案是沒列,spec 應直接寫「不動」而不是留著條件句。
- Systems/存量漂移守衛:至少有第 36、38、39 行的 WHY 寫「已表態的照 scan 慣例列在已表態」「表態記接回續行的整條」,新規則讓這幾句不再完整;spec 只說「寫回表態失效規則、兩個新欄位」,沒說要改既有句,也沒提要加 `[test:]` 綁新測試。

## F3 既有測試會翻紅,spec 驗收只列新測試、沒列要改哪幾條舊測試
severity: major
blocking: 是——spec 的 S5 與兩條既有測試的斷言直接相反,不改測試就是紅的,推送前的閘過不了。
spec 段落:驗收條款 S5、S4;範圍「推送檢查…與 drift scan…只認綁了去處」。
問題與具體例(只讀判斷,未實跑):
- `scripts/test_lumos.py:57724` 附近(t_drift_born_true_scan ④):對寫下時就成立的行用 CLI `drift ack --kind probe`(沒帶 tracked_in),然後斷言那行 `(已表態)`。新規則下 `born_now` + 沒綁去處 = 列在要處理,斷言紅。
- `scripts/test_lumos.py:32163`(t_slots_doctor_reminders ⑦):rule 與 `src/new.py` 同一個提交推入(寫下當下就成立),`_rt_ack` 用 CLI 沒帶 tracked_in 表態後斷言 `另一條` 的 `f["acked"]`。scan 對 retire 也標 born(同 57716 ③ 的測試證實 retire 走同一套),所以會翻紅。
- 32013、32025、32331 附近的 retire 表態測試:rule 先在 base、檔後加,`old` 為真,不是 born_now,不受影響(這幾條我判不影響)。
- 63923 附近手寫表態檔的只有 m1 種類,不受影響。
還有一個定時炸彈:舊表態 2026-11-06 之後失效是用「本機今天」算,凡是日後新增的測試若手寫沒有 until/tracked_in 的 probe/retire 表態,會在那天之後翻紅;spec 的 S3 測試要用可注入的日期(例如把今天當參數或打補丁),不然 t_drift_ack_routed_legacy 自己在 2026-11-06 起就會從綠變紅。spec 沒講日期怎麼注入。

## F4 失效照留的「舊理由」輸出與既有「以前表態過、後來改了或搬了」衝突,drift scan 的印出位置也寫錯
severity: major
blocking: 是——spec 指定的修改位置不會讓 S2 通過,另外會印出自相矛盾的兩句。
spec 段落:做法第 6 點。
引句:「`_drift_print_findings` 與 drift scan 的已表態說明處,`dead_ack` 存在就印」
問題:
(a) 失效的照留對應的發現是被列回「要處理」(沒表態那一邊),不在「已表態」那邊;drift scan 的文字輸出在 `_drift_scan_print`(`scripts/lumos:36759` 起),它不呼叫 `_drift_print_findings`,只在 `if not acked:` 底下印 `_drift_prev_ack_line`;`dead_ack` 要加在那個分支,spec 說的「已表態說明處」不是那裡。
(b) `_drift_print_findings`(`scripts/lumos:35589`)對沒有 `prev_ack` 的發現會呼叫 `_drift_old_reason(f, acks, alive)`;該函式只要同原文同種類就回舊理由,`alive` 為 None 時不跳過。retire 推送路徑 `_drift_retire_print`(`scripts/lumos:35720` 前後)呼叫時沒傳 alive,過期的 retire 照留會同時印「這一行以前表態過、後來改了或搬了,舊理由:…」與新加的 `dead_ack` 那句——前一句對「過期失效」是錯的說法。spec 要寫明 `dead_ack` 存在時略過 `_drift_old_reason`。
(c) 驗收 S2 只驗 scan 輸出,沒有一條驗推送路徑(probe 與 retire 兩條)的印出。

## F5 讀綁定節點的失敗模式:整批讀不到被判成「綁的 X 不在了」,逾時固定 60 秒
severity: major
blocking: 是——git 暫時失敗會把本來有效的照留判失效,推送檢查因此誤擋,且訊息說的原因是假的。
spec 段落:做法第 3 點。
引句:「一次讀完所有綁的節點」
問題:`_drift_cat`(`scripts/lumos:33252`)在 git 跑不起來時整批回 None,spec 的「讀不到 → 不在了」沒區分「那篇真的不在」與「git 讀失敗/逾時」。後者應該是判不了(推送檢查的慣例是判不了照擋但訊息講真話,見 `scripts/lumos:35739` 的 unknown 路徑;retire 則是判不了只列出不擋),不是「不在了」。另外 spec 寫死 `timeout=60`,但撤除條件那支自己的預算是 `_DRIFT_RETIRE_BUDGET_SEC = 20`(`scripts/lumos:35637`),推送核心 `_DRIFT_BUDGET_SEC` 另有預算;`_drift_load_acks` 沒有 deadline 參數,在預算之外多花最長 60 秒,違反既有「每一步開始前都看預算」的設計(`_drift_probe_check` docstring)。
具體例:retire 判定在 20 秒預算內,綁的節點讀取卡 40 秒 → 整個 pre-push 比預算多出 40 秒,而 spec 說 retire 判不了只列出不擋,這裡卻變成可能把照留判失效而擋下。
另:`_drift_load_acks` 被 m1 report(`scripts/lumos:36671`)與 doctor(`scripts/lumos:36801`)也呼叫;spec 說「doctor 不評估…不受影響」,但在 `_drift_load_acks` 裡一律算 `dead` 會讓這兩處也多讀一次綁定節點。要讓 `dead` 只在 probe/retire 用的呼叫點才算(例如獨立函式,或參數 `resolve=True`)。

## F6 消費專案:舊表態期限是寫死的日期,落後的安裝點一升級就沒有緩衝
severity: major
blocking: 是——「從上線日起算 30 天」是 Enzo 的裁定,寫死成固定日期在消費專案升級較晚時違反該裁定。
spec 段落:範圍第 2 條、做法第 1 點 `_DRIFT_ACK_LEGACY_UNTIL`。
引句:「舊表態(兩個欄位都沒有)在 2026-11-06(上線日 +30 天)以前照舊全部有效」
問題:lumos 靠 symlink 分發、安裝要重跑(記憶:lumos-update-distribution),消費專案升級時間不一。rtb 若 11-10 才升級到含本案的版本,所有舊 probe/retire 照留(rtb 11 筆)當天就全數失效,沒有任何 30 天緩衝;而且「上線日」在 spec 寫死 11-06,實際合併日若晚於 10-07,窗口就短於 30 天。spec 沒寫消費專案端怎麼過渡(例如第一次讀到沒有期限的舊表態時記下首見日,或升級時批次補寫 until)。
另一個混版本情形:同一個專案本機用新版、CI 用舊安裝(或相反)時,同一筆推送兩邊判定不一樣(新版擋 born_now 沒綁去處的、舊版放行);spec 的「回退」只談退回提交,沒談版本不一致時 CI 與本機的落差,也沒提醒升級要兩邊一起。舊版讀新欄位(忽略多出的鍵)我確認 `scripts/lumos:34365` 只過濾 path/kind,不會壞。

## F7 `born_now` 用「`old` 為假」,沒有起點(None)與改名沒對上時整批誤標
severity: major
blocking: 是——spec 的前提宣稱不成立,2026-11-06 後會讓無關推送被擋。
spec 段落:做法第 5 點、實務隱患「舊表態一起到期」。
引句:「`_drift_probe_check` 的 must 裡 `old` 為假(起點沒有同一條)的發現加 `born_now: True`」
問題:`_drift_probe_old`(`scripts/lumos:33690` 前後)在沒有起點(`benv is None`、`base` 為空,例如新分支首推從空樹掃)時回 None,None 也是「為假」。此時所有現在成立的條件都是候選、`old` 都是 None,全部會被標 `born_now`。另外筆記改名偵測沒對上、或圖譜資料夾改名(`_drift_layout_changed` / `_drift_vault_rel`)時,同一條也會被當新寫。這些情形今天靠表態還能過;新規則(舊表態期限過後)會要求每一條都綁去處。
spec 的隱患段寫:

引句:「推送檢查只看這次推送讓條件成立的行,不會因此擋住無關的推送。」

但上述情形推送沒有讓條件「成立」,是起點資料缺或對不上,與事實不符。要明確寫 `old is False` 才標(None 不標),並加一條測試:起點為空樹時已表態的條件不因 born_now 被擋。

## F8 時區敘述方向相反,且推送結果可能是「本機擋、CI 過」
severity: minor
blocking: 否——只影響邊界那一天的誤判描述,不影響放行規則。
spec 段落:實務隱患第一條。
引句:「期限當天的照留可能本機算有效、CI 算失效」
問題:台北(UTC+8)的本機日期不會比 UTC 的 CI 早;凌晨 0–8 點本機日期比 CI 多一天,所以是本機算過期、CI 算有效(本機擋、CI 過)。方向反了才會是「本機有效、CI 失效」,那是 UTC 以西的消費專案。兩種都會讓推送前掛鉤與 CI 判定不一致,spec 的「多列一筆(不是放行)」只對後一種成立;前一種是 CI 多放行一筆。建議改成「期限以 UTC 日期算」(`datetime.datetime.now(datetime.timezone.utc).date()`),就沒有這個分叉。

## 其他呼叫點逐項查證(spec 問到的路)
- 推送檢查扣表態的路:四條各自呼叫 `_drift_split_acked`——(1)probe+c1~c5 在 `_drift_check_c`(`scripts/lumos:35741-35743`),(2)撤除條件在 `_drift_retire_guarded`(`scripts/lumos:35667-35668`),(3)m1 在 `_drift_m1_report`(`scripts/lumos:36671-36673`,不受影響),(4)考試與歷史重放走 `_drift_check_core`(`scripts/lumos:36960`、`36991`、`37150`)但不讀表態檔。spec 第 5 點把 `born_now` 放在 `_drift_probe_check` 一處,probe 與 retire 兩條推送路徑因此都涵蓋,這一點正確。
- 考試與歷史重放:`_drift_check_core` 回傳的發現多一個 `born_now` 鍵,不影響筆數與「噪音基準」(spec 沒提這點,屬 `_drift_check_core` 註解 `scripts/lumos:35785` 說的不可改基準,我判不影響,但 S1~S6 沒有一條驗考試輸出不變)。
- drift fix:`cmd_drift_fix` 的 `--keep` 呼叫 `cmd_drift_ack(env, rel, line, "c2", …)`(`scripts/lumos:35473`),簽名加 `tracked_in` 預設 None 就相容,spec 已寫,已讀無 finding。
- CI:CI 跑同一支 `drift check`,spec 沒有獨立列 CI,但除時區(F8)與版本落差(F6)外,無額外路徑。
- 治理帳:`cmd_drift_ack` 會 `_gate_event_or_warn(... "acked", …)`(`scripts/lumos:34574`),spec 的成功訊息要不要把 tracked_in/until 帶進帳,沒寫;不影響判定,minor 不另立。

## 逐節
- front matter 與白話/依據/PRIOR-ART/RETIRE-IF:已讀,無 finding(連結到的 `Projects/交接2026-10-03_計劃` 等未逐一開檔,與本鏡頭無關)。
- 範圍:F6、F7 引到。
- 做法 1(常數):已讀,無 finding(`_STATUS_ENUM` 的開著值我核對過:project 含 todo/doing、issue 含 open/doing,吻合)。
- 做法 2(argparse 與 cmd_drift_ack):F2 引到;`_drift_ack_args_err(kind, reason, names)` 只有 `cmd_drift_ack` 一個呼叫點(`scripts/lumos:34536`),加參數安全。
- 做法 3、4:F5、F4、F6 引到。
- 做法 5:F7。做法 6:F1、F4。做法 7:F2。
- 實務隱患:F7、F8;其餘(舊表態一起到期、綁的節點改名)已讀,無 finding。
- 驗收條款:F3(舊測試要改、日期注入)、F1(首次擋下提示)、F4(推送路徑印出)。
- 回退:F6 補版本落差。天花板:已讀,無 finding。

## 實務隱患(本功能碰到的風險類)
- 時間/時區:F8。
- 外部依賴失敗(git 讀取):F5。
- 版本相容/分發:F6。
- 金流、對外送出、不可逆:無,只改筆記治理工具與追加式表態檔(同意 spec)。
- 併發:`cmd_drift_ack` 已在 `_vault_write_lock` 內追加;新欄位不改寫入路徑,無新增風險。
- 圖譜合約節點:派工時未附合約/事故節點清單,本席未做逐節點判定;僅就 Systems/存量漂移守衛 的 WHY 行(F2)判「需補寫、不破壞合約」。

總結:最嚴重 severity 為 major,blocking 7 條(F1~F7),minor 1 條(F8)。
