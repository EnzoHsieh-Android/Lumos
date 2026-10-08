---
type: project
status: doing
created: 2026-10-01
updated: 2026-10-01
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/guard-kill
related:
  - "[[Projects/殺傷力配方失配提醒_計劃]]"
  - "[[Projects/漂移防治路線圖_計劃]]"
  - "[[Systems/guard-kill]]"
---
# 殺傷力配方修補體驗_計劃

白話:殺傷力配方失配提醒上線當天,rtb 照 `lumos doctor --verbose` 的 P2 段(逐條數配方原文出現幾次、列出失配的那段)列出的 10 條第一次完整走完「列出 → 移除 → 重加 → 驗殺傷力」,回報四個不順的地方。Enzo 2026-10-01 裁「先做 2、3 再做 1、4」:這份計劃只做 rtb 回報的第 2 條(kill-rm 印的重加範本不再抄舊壞法)與第 3 條(每條配方都查得到短身分:kill-rm 不帶 --id 時列出、guard kill 結果行附上);第 1 條(重加後當場試跑那一條)與第 4 條(doctor P2 段也列出真跑沒抓到的配方)另開計劃,排在這份之後。

依據:
- rtb 會談 2026-10-01 回報(rtb 提交 c531ac7,修完 10 條、guard kill 全部 killed;過程記在 rtb 的 `Issues/存量筆記漂移等工具修復`)。第 2 條原話大意:kill-rm 印的範本把舊的 `--new` 原樣抄過去,程式改過之後舊壞法常常也得跟著改(例:原文多了一個參數,舊的 `--new` 已經套不上),建議 `--new` 也標成待填。第 3 條:原文對得上的配方 P2 不列、沒有任何指令印得出它們的短身分,要移除自己寫錯的兩條時只能匯入 scripts/lumos 自己算。
- Enzo 2026-10-01 裁「先做 2.3 再做 1.4」。

PRIOR-ART: 兩件都是既有指令的輸出調整,沒有外部輪子可借:①範本留空欄位的寫法照 kill-rm 既有的 `--old '<照現在的程式填原文>'`;②短身分用既有的 `_kill_recipe_id`(P2、kill-add 提醒、kill-rm 共用),列出時人寫的欄位照既有 `_kill_show` 跳脫。
RETIRE-IF: 這份做完就 done;「kill-rm 不帶 --id 時列出」這個功能,連續兩次 rtb 回報都沒人用到就撤掉(guard kill 結果行已附短身分,夠用)。
REVISIT:2026-10-15 跟殺傷力配方失配提醒同一天,看 rtb 回報有沒有人用到不帶 --id 的列出、範本待填欄有沒有被抱怨。

## 範圍

- 做:kill-rm 範本的 `--new` 改成待填;kill-rm 不帶 `--id` 時列出這篇所有配方的短身分;guard kill 的人讀輸出每條結果附短身分。
- 不做:重加後當場試跑(rtb 第 1 條)、健康檢查列出真跑沒抓到的配方(第 4 條)——另開計劃;guard kill 的判法、回傳碼、`--json` 輸出內容(`recipe_id` 欄本來就有)都不改。

## 做法

- **範本**:`_kill_add_template` 的 `--new` 一律印 `'<照新原文改寫的壞法>'`(現在是把舊壞法原樣抄進去);舊的壞法照樣在上一行「要移除的配方(完整內容):」那行的 JSON 裡看得到,人可以對照改。
- **kill-rm 不帶 --id**:argparse 的 `--id` 從必填改成選填;`cmd_guard_kill_rm` 開頭先分流——沒帶 `--id` 走唯讀列出(不拿寫入鎖、不寫檔),帶了照既有驗證與移除。列出:找不到筆記照既有擋下回 2;整欄解析不了照既有擋下回 2;沒有配方印「這篇沒有殺傷力配方」回 0;否則逐條印一行到標準輸出、回 0:`<短身分前 12 字元>  平台 <platform 或預設>  檔 <file>  原文 <old 前 30 字>  test <test>`,各欄經 `_kill_show`(會帶引號);不是物件的元素整個印 `_kill_show(json 原樣)`。最後印一句「移除:lumos guard kill-rm <節點> --id <短身分>」。
- **guard kill 的人讀輸出**:每條結果行在 `[<test>]` 之後、說明之前加 `id=<短身分>`(說明可能很長,放後面會被吃掉)。★短身分要在建結果之前用原始配方算★:`cmd_guard_kill` 每筆結果是 `{**原配方, platform, verdict, …}`,事後還原不出原配方;結果裡本來就有的 `recipe_id` 是 `_kill_recipe_key` 算的,配方格式壞時(缺 old、file 是數字)跟 kill-rm 用的 `_kill_recipe_id` 不同。所以在組結果時用原配方算 `_kill_recipe_id`,存成底線開頭的旁路欄(照 `_logged` 的做法在 `--json` 輸出前濾掉);`--json` 內容與既有 `recipe_id` 欄都不變。

## 條款

- [S1] 當 kill-rm 移除配方時,印出的 kill-add 範本的 `--new` 應是待填字樣、不應出現舊配方的壞法原文;完整內容那一行仍應印出舊壞法 [test:t_guard_kill_rm]
- [S2] 當 kill-rm 沒帶 `--id` 時,應逐條列出那篇每條配方的短身分(跟 P2 與 kill-add 提醒同一支算法,前 12 字元)、檔與原文開頭,回傳 0、筆記不變;格式壞的配方也應列出且身分可直接拿去 `--id` 移除;沒有配方時應印「這篇沒有殺傷力配方」;人寫的欄位不應原樣印出控制字元 [test:t_guard_kill_rm_lists_ids]
- [S3] 當 guard kill 不帶 `--json` 跑時,每條結果行應在 `[<test>]` 之後附 `id=<短身分>`,而且該短身分拿去 `kill-rm --id` 應對得到那一條(格式壞的配方也一樣);帶 `--json` 時標準輸出應只有 JSON、各筆結果的欄位跟改動前相同 [test:t_guard_kill_prints_recipe_id]

## 回退

- revert 實作提交:範本回到抄舊壞法、kill-rm 回到 `--id` 必填、guard kill 結果行不附身分;筆記與配方都沒被這次改動自動改過。
- revert 之後本計劃條款綁的 `[test:]` 會懸空,status 改 superseded 或在〈實作紀錄〉記一句「已撤回」。

## 實務隱患

- **既有測試要一起看的**:`t_guard_kill_rm` 沒有斷言比對舊壞法(前掃查過),不用改,S1 是新增反向斷言(範本不含舊壞法、完整內容仍含)。guard kill 的既有測試只用子字串比對結果行;drifted、開檔失敗、逃逸三句說明字面是從 `--json` 的 detail 讀,不受人讀行影響;「worktree 無殘留」那支要求人讀輸出維持單行(加 id 後仍單行)。另有文件守衛測試從 `cmd_guard_kill` 原始碼抽 verdict 值域,別在函式體內新增 `"verdict": "…"` 字面。
- **要同步的文件**:[[Systems/guard-kill]] 的 kill-rm 用法與範本說明;skill 的 `commands/06-代碼審與推送.md` 那一列與 `scripts/lumos` 裡 kill-rm 的 HELP_WHEN 與 argparse help。
- **`--json` 純度**:guard kill 的 `--json` 有既有合約(標準輸出只有 JSON),這次只動人讀那支。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀本機檔,不連網
- 已排除:不可逆:只改輸出與一個選填參數;revert 就回得去
- 已排除:守衛面:不擋任何推送、提交或宣告,guard kill 判法與回傳碼不改

## 實作紀錄

(實作後補)
