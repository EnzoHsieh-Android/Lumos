severity: minor

鏡頭:簡化/反過度設計。未重裁「兩種都給、至少選一」與「舊表態從上線日起算 30 天」。圖譜鏡頭:派工時未附上合約/事故節點,無固定席可判,此項不適用。

## F1 失效句另造 dead_ack,與既有 prev_ack 打印路徑重複
severity: minor
blocking: 否 只是多一個欄位與多一條印法,不影響行為正確。
spec 段落:做法 4、6。
引句:「帶 `dead_ack={reason, why}`(取最新一筆),印的地方多一句。」
問題:既有 c2/c3 已有「以前表態過、現在不算了」的機制:`_drift_split_acked` 對沒涵蓋的發現帶 `prev_ack={related, reason}`,`_drift_prev_ack_line` 負責印,兩處呼叫(file: `scripts/lumos:35595`、`scripts/lumos:36768`);另有 `_drift_old_reason` 的第三種舊理由句(file: `scripts/lumos:35596`)。spec 再造 `dead_ack`、再加第四種印句,`_drift_print_findings` 會有三個互斥分支變四個,而且 `cmd_drift_scan` 另一處印法(`scripts/lumos:36768` 附近)也要同步補,漏一處就只在推送檢查看得到。
更小的改法:沿用 `prev_ack`,多放一個 `why` 鍵(失效原因字串即 `dead`),`_drift_prev_ack_line` 內依有沒有 `related` 分兩種句型。少一個欄位、少一個印的分支、兩處呼叫點自動同步。
具體例:rtb 一筆 probe 照留到期 → 預期只要印「以前照留過(理由…),已過期限 …」;spec 版要新增欄位並在兩個印點各補一次,實際最容易漏的是 drift scan 那個印點(S2 只驗 scan)。

## F2 LEGACY 常數與 legacy 旗標在 2026-11-06 之後是死碼,spec 沒寫撤除
severity: minor
blocking: 否 不影響行為,是維護債。
spec 段落:做法 1、3、4;REVISIT。
引句:「舊表態(兩個欄位都沒有)在 2026-11-06(上線日 +30 天)以前照舊全部有效」
問題:舊表態在 11-06 後一律失效,`_DRIFT_ACK_LEGACY_UNTIL`、`legacy=True` 旗標、`_drift_split_acked` 裡「還沒失效的舊表態」那條分支、S3 測試,11-06 之後全部只會走「過期」那一格,等於永遠不可達。新寫的表態都有 `until` 或 `tracked_in`,沒有欄位的只可能是舊檔。spec 的 REVISIT 只排 2026-12-06 看消費專案行為,沒排「11-07 之後拆掉 legacy 分支」。專案鐵則四要求這類會過期的東西綁回頭條件。
更小的改法:不存 `until` 欄位,改用表態已有的 `date` 欄(file: `scripts/lumos:34548` 的 rec 已記 `date`)在判斷時算 `date + 30`,舊表態另取 `max(date+30, LEGACY)`;或更直接,加一行 `REVISIT:2026-11-07 刪 _DRIFT_ACK_LEGACY_UNTIL、legacy 旗標與 S3`。後者零成本。
具體例:2026-11-07 起 grep `legacy` 仍有 3 處分支與 1 支測試,新人讀不懂為何存在。

## F3 不需要新存 until 欄位:ack 已有 date,「今天+30」可在判斷時算
severity: minor
blocking: 否 多一個新欄位而已。
spec 段落:做法 2、3;S1。
引句:「沒帶就記 `until` = 今天 + 30 天。」
問題:`cmd_drift_ack` 的紀錄已含 `date`(寫入日,file: `scripts/lumos:34548`)。`_DRIFT_ACK_DAYS` 又是固定常數(spec 自己「不做」可自選天數)。存 `until` 等於把「date + 常數」物化一次,還衍生「期限格式壞 → 已失效」這條只為手改壞檔而生的特例,與「`legacy`=沒有 until」的判定。若不存,`dead` 只需:有 `tracked_in` 看那篇;沒有則 `today > date + 30 天`;`date` 壞就當失效——一個分支取代三個(until 缺、legacy、期限格式壞),且改常數天數時舊表態自動跟著算(存死值反而改不動)。
代價:舊表態「11-06」仍需一個常數,見 F2。
具體例:把 `_DRIFT_ACK_DAYS` 從 30 改 45,存了 `until` 的舊筆不跟著變,調參要另想遷移;不存就無此問題。

## F4 RETIRE-IF 與 REVISIT 的時間對不上,且 RETIRE-IF 沒有量測手段
severity: minor
blocking: 否 判準本身講得出,只是排程矛盾與缺量法。
spec 段落:PRIOR-ART/RETIRE-IF 與文末 REVISIT。
引句:「REVISIT:2026-12-06 看消費專案 probe/retire 照留到期後是改綁去處、真的處理,還是照貼再表態(對照 RETIRE-IF)」
問題:RETIRE-IF 要「連續 60 天」觀察,舊表態 11-06 才集體到期,12-06 只過 30 天,頂多看到一個週期;無法對照 60 天條件。另外「理由照貼再表態、沒有任何一筆改綁去處」沒有指令能算(表態檔是追加帳,要自己比對同路徑同原文的連續兩筆理由是否相同),沒寫怎麼量,等於承認一個沒機械檢查的撤除條件。
修法:REVISIT 改 2027-01-06(11-06 起 60 天),並寫一句用表態檔怎麼數(同 `_drift_ack_key` 的鍵、後一筆 reason 與前一筆相同且沒有 tracked_in 的筆數 / 全部再表態筆數)。
具體例:2026-12-06 到期時只有一輪資料,看起來「全部照貼」,誤判該撤。

## F5 born_now 在 drift scan 側再開一條,但推送檢查已是真正的閘
severity: minor
blocking: 否 可選的縮減,不是錯。
spec 段落:做法 5 後半、S5。
引句:「drift scan 的發現 `born.state == "true"` 時也加 `born_now: True`」
問題:born_now 要擋的洞是「同一次推送補一筆照留就放行」(spec 因欄位),洞在推送檢查(`_drift_probe_check` 的 `old` 為假)。drift scan 側的 born_now 只影響掃描顯示,而任何沒綁去處的照留 30 天後本來就失效重列(F本案核心);掃描側加分支只是讓「寫下時就成立」的那幾行早 30 天回到清單。代價是 `_drift_born_annotate` 後多一個接點、`_drift_split_acked` 多一個「born_now × legacy」交叉分支、S5 一支測試,而這個交叉(legacy 要豁免 born_now)正是 intake 前掃已抓到過一次矛盾的地方(`r1-intake.md` 表中 ③)。
更小的改法:只留推送檢查側的 born_now(S4),scan 側不做、S5 刪除;推送閘被 `LUMOS_SKIP_DRIFT_CHECK` 繞過的那種情況,就讓它走一般 30 天。若作者要保留,需舉今天的具體案例:有哪一筆 scan 側的 born 發現在「推送閘沒擋」的情況下被 30 天照留蓋住且傷害超過 30 天。
具體例:rtb 這輪 11 筆都是推送閘放行後的存量(舊表態),scan 側 born_now 對它們在 11-06 前根本豁免,對新表態又有推送閘擋——scan 側分支兩種情境都沒觸發。

## F6 ROUTE_OPEN 兩份開著值常數,未與 _STATUS_ENUM 機械連動
severity: minor
blocking: 否 同類既有守衛可借。
spec 段落:做法 1。
引句:「`_DRIFT_ACK_ROUTE_OPEN = {"issue": ("open", "doing"), "project": ("todo", "doing")}`(取自 `_STATUS_ENUM` 的開著值)」
問題:`_STATUS_ENUM`(file: `scripts/lumos:16850`)新增或改名狀態,這張手抄表不跟著變;spec 說「取自」卻沒說是衍生還是手抄。已有 `_DRIFT_SETTLED = frozenset(_DRIFT_CLOSED) | _ISSUE_CLOSED_STATUSES`(file: `scripts/lumos:32234`)這種「不另寫一份」的先例。
更小的改法:`ROUTE_OPEN` 由 `_STATUS_ENUM[type] - _DRIFT_SETTLED` 算(Issue 與計劃兩個 type),不手寫;若算出來含 rejected/deferred 之類不要的值(前掃已確認 Systems/驗證有這類),才退回手寫並加一支測試比對 `_STATUS_ENUM`。
具體例:有人給 Issue 新增狀態 `blocked`,手抄表不認 → 綁在 blocked Issue 上的照留被當失效,使用者看到「已收尾」的誤導訊息。

## 各節逐條
- frontmatter / 白話 / 依據 / PRIOR-ART:已讀,F4 針對 RETIRE-IF;PRIOR-ART 說沿用 c2 的 related,但實作選了反向(綁開著而非已收尾)、並另立 dead/dead_ack,與「不另造第三種失效機制」自述有落差,已併入 F1。
- 範圍:已讀,無獨立 finding(「只認 Issue 與計劃」為必要:前掃已查 `_DRIFT_SETTLED` 不含驗證紀錄等值,收窄合理;兩種失效原因「到期」「綁的已收尾」各對應一個選項,都必要)。
- 做法 1-7:F1、F2、F3、F5、F6。步驟 7「先查」`lumos-cli-lifecycle` 為作業項目,無 finding。
- 實務隱患:已讀,無 finding。UTC/本機日期差一天的接受理由具體(只多列一筆)。風險類:金流、對外送出、不可逆三類已排除理由成立。
- 驗收條款:已讀,無 finding(S5 見 F5)。
- 回退:已讀,無 finding。
- 天花板:已讀,無 finding;兩條都講得出,第 2 條與 RETIRE-IF 一致。

總結:最嚴重 severity 為 minor,blocking 0 條。
