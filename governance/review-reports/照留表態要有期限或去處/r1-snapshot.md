---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/存量漂移守衛
related:
  - "[[Projects/交接2026-10-03_計劃]]"
  - "[[Projects/回頭條件寫下時就成立_計劃]]"
  - "[[Projects/存量漂移防線_計劃]]"
summary: |-
  WHY:回頭條件與 RULE 撤除條件成立後的「照留」表態要嘛綁一篇還開著的 Issue 或計劃(`--tracked-in`,那篇收尾就失效),要嘛 30 天後失效重新列;寫下時就已成立的條件,照留只認綁了去處的表態 [出處:2026-10-06 rtb 第三輪提案 B1、B2 與 rtb 會談回覆的實例;Enzo 2026-10-06 裁「兩種都給、至少選一」「舊表態從上線日起算 30 天」] [因:照留沒期限等於永久消音——rtb 有 11 筆理由寫「還沒補/還沒評估」,表態後 drift scan 不再列、也沒排進任何地方;推送時「新寫就已成立」雖然會擋,同一次推送補一筆照留就放行(rtb 一次改寫 33 行、當場照留 11 行)] [不選:只給 30 天(到期後理由照貼再表態一次,等於延長消音);只收綁去處(「還沒評估」這種得先硬開一篇 Issue);新寫就成立的一律不收照留(條件已成立但真的排進某篇計劃時沒路走)]
---
# 照留表態要有期限或去處_計劃

白話:回頭條件(某個事件發生就該回頭看的提醒)成立之後,如果事情還沒做,可以用 `lumos drift ack` 表態「這行照留」,之後健檢就不再列。問題是這個表態永遠有效,等於把提醒關掉。這次改成:照留時要嘛說清楚「排進哪一篇」(那篇收尾,照留就失效、重新列出來),要嘛不說,30 天後自動失效、重新列。另外,推送時新寫進去、寫下時就已成立的條件,本來就會擋,但補一筆照留就能過——這種只認說清楚排進哪一篇的照留。

依據:Enzo 2026-10-06 裁定兩題(做法:兩種都給、至少選一;舊表態:從上線日起算 30 天)。rtb 會談回覆的實例:Systems/Mock-DSP 第 80 行、Systems/共用行程基礎 第 57、60 行(rtb repo),都是「條件成立了但事還沒做」的照留。

PRIOR-ART: 同工具 c2/c3/c6 的照留已經綁「當時連著的已收尾計劃」,清單多了新的就重新列(`_drift_split_acked` 的 related/seq);REVISIT 本身有 `[by:日期]` 期限、doctor 到期會唸。本案沿用兩者的形狀:綁一篇節點的狀態、或一個日期,不另造第三種失效機制。表態檔、讀提交裡的筆記(`_drift_cat`)、frontmatter 解析(`split_frontmatter`/`parse_frontmatter`)、寫下時就成立的判定(`_drift_born_annotate`、`_drift_probe_judge` 的新寫分支)都沿用。
RETIRE-IF: 連續 60 天,所有消費專案的 probe/retire 照留到期重列後都是理由照貼再表態(沒有任何一筆改綁去處或真的處理)——表示期限只增加操作、不改行為,改回單純的照留並另想辦法。

## 範圍

- 做:`lumos drift ack --kind probe|retire` 多一個 `--tracked-in <節點>`;沒帶就自動記 30 天後的期限。
- 做:判斷照留還算不算數時(推送檢查與 drift scan 共用同一支;doctor 不評估回頭條件、只數條數,不受影響),probe 與 retire 的照留要「綁的那篇還開著」或「期限還沒到」;舊表態(兩個欄位都沒有)在 2026-11-06(上線日 +30 天)以前照舊全部有效——包括下一條「寫下時就已成立」的那些——之後一律失效。
- 做:「綁的那篇還開著」只認 Issue(狀態 open、doing)與計劃(狀態 todo、doing);綁驗證紀錄、Systems 節點、或沒有狀態欄的筆記,表態時擋、判斷時當失效。
- 做:推送檢查裡「這次新寫(或改了條件)、條件已經成立」的發現,與 drift scan 裡標「寫下時就已成立」的發現,只認綁了去處、而且那篇還開著的照留(舊表態在 2026-11-06 以前例外,照上一條)。
- 做:失效的照留在發現清單下面多印一句:以前照留過、理由是什麼、為什麼失效(到期日/綁的那篇已收尾)、要繼續照留怎麼帶 `--tracked-in`。
- 不做:c1–c6、m1、count 的照留(c2/c3/c6 已經綁 related;其餘本來就是改掉才會消失,rtb 這輪沒有實例)。
- 不做:讓 `--until` 可以自己選天數(固定 30 天;要更長就綁一篇去處)。
- 不做:把到期的照留自動從表態檔刪掉(表態檔只追加;失效只在判斷時算)。

## 做法

1. 常數:`_DRIFT_ACK_DAYS = 30`、`_DRIFT_ACK_LEGACY_UNTIL = "2026-11-06"`、`_DRIFT_ACK_ROUTED = ("probe", "retire")`、`_DRIFT_ACK_ROUTE_OPEN = {"issue": ("open", "doing"), "project": ("todo", "doing")}`(取自 `_STATUS_ENUM` 的開著值)。
2. argparse 的 `drift ack` 加 `--tracked-in`;`_drift_ack_args_err` 多收 tracked_in:kind 不在 `_DRIFT_ACK_ROUTED` 又帶了擋 rc2。`cmd_drift_ack` 收 `tracked_in`:帶了就 `env.find` 解析,找不到擋、type/狀態不在 `_DRIFT_ACK_ROUTE_OPEN` 擋,記 `tracked_in` 成 repo 相對路徑(跟 `path` 同形);沒帶就記 `until` = 今天 + 30 天。成功訊息印出是哪一種(綁哪篇/到哪天)。`drift fix --keep` 也呼叫 `cmd_drift_ack`,但 kind 固定 c2、不帶 tracked_in,行為不變。
3. `_drift_load_acks(root, where)` 讀完表態後,替 kind 在 `_DRIFT_ACK_ROUTED` 的每筆算 `dead`(失效原因字串;還有效是空字串):
   - 有 `tracked_in`:用同一個 where 讀那篇——where=None 直接讀工作目錄的檔(同本函式讀表態檔的寫法,符號連結不跟);給提交就用 `_drift_cat(root, where, paths, timeout=60)` 一次讀完所有綁的節點——讀不到 → 「綁的 X 不在了」;`split_frontmatter`+`parse_frontmatter` 取 type 與 status,不在 `_DRIFT_ACK_ROUTE_OPEN` → 「綁的 X 已收尾或不是 Issue/計劃(狀態)」;否則有效。
   - 沒有 `tracked_in`:期限取 `until`,沒有就取 `_DRIFT_ACK_LEGACY_UNTIL`(另記 `legacy=True`);今天(本機日期)晚於期限 → 「已過期限 YYYY-MM-DD」;期限格式壞 → 當成已失效(「期限寫壞了」)。
   - 只讀一次:同一批綁的節點一次讀完。
4. `_drift_split_acked`:kind 在 `_DRIFT_ACK_ROUTED` 的照留,`dead` 不是空字串的不算;發現帶 `born_now`(下一點)時只算有 `tracked_in` 而且沒失效的,或還沒失效的舊表態(`legacy`)。沒算上的發現若有對得上(同路徑同原文同種類)的照留,帶 `dead_ack={reason, why}`(取最新一筆),印的地方多一句。
5. 新寫就已成立的標記:`_drift_probe_check` 的 must 裡 `old` 為假(起點沒有同一條)的發現加 `born_now: True`;drift scan 的發現 `born.state == "true"` 時也加 `born_now: True`(在 `_drift_born_annotate` 之後、扣表態之前)。
6. `_drift_print_findings` 與 drift scan 的已表態說明處,`dead_ack` 存在就印:「以前照留過(理由:…),{why};還沒做就 lumos drift ack <節點> <行號> --kind <k> --tracked-in <排進的那篇> --reason "…"」;`born_now` 而且那筆照留沒綁去處,why 寫「寫下時就已成立,照留要綁去處」。
7. 寫回 [[Systems/存量漂移守衛]](表態失效規則、兩個新欄位);[[Systems/lumos-cli-lifecycle]] 若列了 drift ack 的選項一併補(先查)。

## 實務隱患

- **日期取本機**:`date.today()` 依本機時區;CI 在 UTC,台北凌晨 0–8 點推送時兩邊可能差一天,期限當天的照留可能本機算有效、CI 算失效。只差邊界那一天,影響是多列一筆(不是放行),接受。
- **舊表態一起到期**:2026-11-06 之後消費專案的舊 probe/retire 照留會同時重列(rtb 11 筆);只在 drift scan 出現(doctor 不評估回頭條件),推送檢查只看這次推送讓條件成立的行,不會因此擋住無關的推送。
- **綁的節點改名**:改名後舊路徑讀不到 → 判「不在了」重列;理由會印出來,重綁一次即可。不追改名(同 c2 的 related 不追)。
- 已排除:金流:只改筆記治理工具,不碰任何金流
- 已排除:對外送出:不連網、不送任何東西出去
- 已排除:不可逆:表態檔只追加,失效只在判斷時算;退回提交即恢復舊行為
- 守衛面:會讓推送檢查多擋一種情況(新寫就成立 + 沒綁去處的照留),屬收緊不放寬;放寬面只有「舊表態」原本永久有效改成有期限,也是收緊。

## 驗收條款

- [S1] 當 `drift ack --kind probe` 沒帶 `--tracked-in` 時,表態檔那筆 應 記 `until` 為今天 + 30 天、不記 `tracked_in`;帶了指到一篇還開著的筆記 應 記 `tracked_in`、不記 `until`;指到不存在或已收尾的筆記 應 rc2 不寫;`--kind c2` 帶 `--tracked-in` 應 rc2 [test:t_drift_ack_routed_fields]
- [S2] 當 probe 照留的期限已過、或綁的那篇已收尾或不在了,drift scan 應 把那一行列回「要處理」並印出舊理由與失效原因;期限沒到、或綁的那篇還開著 應 照舊列在已表態 [test:t_drift_ack_routed_expiry]
- [S3] 當表態沒有 `until` 也沒有 `tracked_in`(舊表態)時,判斷 應 以 2026-11-06 為期限,期限前連寫下時就已成立的發現也算已表態 [test:t_drift_ack_routed_legacy]
- [S6] 當 `--tracked-in` 指到驗證紀錄、Systems 節點或沒有狀態欄的筆記時,drift ack 應 rc2 不寫;已記下的照留綁的那篇之後變成這幾種時 應 當失效 [test:t_drift_ack_routed_fields]
- [S4] 當推送新寫一條寫下時就已成立的回頭條件、同一次推送補了沒綁去處的照留時,drift check 應 照擋並印「照留要綁去處」;照留綁了一篇還開著的筆記 應 放行 [test:t_drift_check_born_needs_routed_ack]
- [S5] 當 drift scan 的發現標了寫下時就已成立而且照留沒綁去處時,那一行 應 列在要處理 [test:t_drift_scan_born_needs_routed_ack]

## 回退

退回本案的提交即可:表態檔的新欄位舊程式不讀(多出來的鍵忽略),舊程式照舊把所有照留當永久有效;不需要搬資料。

## 天花板

1. 「綁的那篇還開著」只看類型與狀態欄,不驗那篇真的提到這件事;綁一篇無關但長期開著的 Issue 一樣能消音。
2. 期限固定 30 天,到期後理由照貼再表態一次就能再消音 30 天——只能讓它每月出現一次,不能逼人處理。

REVISIT:2026-12-06 看消費專案 probe/retire 照留到期後是改綁去處、真的處理,還是照貼再表態(對照 RETIRE-IF)
