severity: minor

回滾與相容鏡頭。已實跑核對:既有 kill-add 呼叫端(測試 20186–20262、59789–59935 等)只檢查回傳碼與 stderr 子字串,沒有逐字比對或要求 stderr 為空;`--json` 只屬 `guard kill`,kill-add 沒有 `--json`,多一行 stderr 不碰純度測試;新段放 P 之後不影響 `t_doctor_advisory_sections_do_not_block`(只要用 warn_soft)與 `t_doctor_summary_admits_soft_reminders`(本 repo 唯一配方 `canary-audit` 的原文在 `scripts/lumos` 恰出現 1 次);精簡版靠 run_doctor 的可達閉包,新函式會一起帶進去。

## F1 設定讀不了的那一句沒指定用哪支印法,抄錯會讓收尾計數或「不擋」守衛翻紅
severity: minor
blocking: 否
引句:「(比照 doctor 既有幾段的寫法)」
file: `scripts/lumos:2628`
1. doctor 既有「算不出來」的寫法是 `warn_soft([], "這一段算不出來(...),先跳過")`(2628、2678、2749 行),另有純 `print("(…算不出來…)")` 不帶 ⚠(1309–1321 行);兩種都叫「既有幾段」。
2. 照純 print 且帶 `⚠` 實作:`t_doctor_summary_admits_soft_reminders` 的「軟段數 = 印出的 ⚠ 段數」會差一;照 `warn([],…)`(Check F 的寫法)實作:`t_doctor_advisory_sections_do_not_block` 掃到標題含「不擋」的段落裡有 `warn(` 而翻紅。
3. 建議條款寫死:用 `warn_soft([], …)`,且 S4 的測試要涵蓋這條路徑。

## F2 kill-add 的提醒插在判重之前,重複被擋時會印「照舊寫入」卻什麼都沒寫
severity: minor
blocking: 否
引句:「在配方組好之後、判重迴圈之前跑判斷函式」
file: `scripts/lumos:12952`
1. `cmd_guard_kill_add` 在判重迴圈裡遇到同一條配方會 `return 2`(擋下);插在它前面的提醒文字是「…先照現在的程式改寫原文再宣告」,而 S1 說「照舊寫入」。
2. 輸入:已有配方 X,再次 kill-add 同一條 X(沒帶 covers,原文已失配)→ 先印 ⚠ 提醒,再印「已經有了」並 rc2。使用者看到兩段互相無關的訊息;自動化若以「有 ⚠ 即警告成功」判讀會誤判。
3. 同理 `_kill_read_recipes` 回錯(`return 2`)在判斷函式之前或之後,spec 沒講:插入點只說「組好之後、判重之前」,而 `_kill_read_recipes` 的失敗返回夾在兩者之間。需明寫:提醒只在確定會走到寫入(或 covers 更新)時才印,或接受並在文字上註明。

## F3 〈回退〉說 revert 即可,漏講 revert 後計劃條款的 test 綁定會懸空、REVISIT 會懸著
severity: minor
blocking: 否
引句:「revert 實作提交即可:doctor 少一段、kill-add 少一行提醒;筆記與配方都沒被改過。」
file: `scripts/lumos:2367`
1. 計劃條款 S1–S6 的 `[test:…]` 綁了實作時才建的測試;doctor 的 S5 段(2367 行)會唸「計劃條款寫的測試名程式碼裡找不到」。若計劃本檔在實作提交之前已獨立提交(本 spec 現在就是這個狀態),只 revert 實作提交會讓這些測試名重新懸空、doctor 每次多唸一段,而〈回退〉沒提。
2. 同理:`REVISIT:2026-10-15` 要求 rtb 回報 P2 輸出,revert 後 rtb 端的 vendored 舊/新版若不一致,這個回頭點沒有退場說明。
3. 另外,doctor 每次跑會往 `docs/.governance-log.jsonl` 的 doctor-run 事件寫 `soft=N`;revert 後歷史行的 soft 數會比新跑的多一段,屬於無害殘留,但「沒留任何東西」不成立。建議〈回退〉補一句:revert 時連同計劃條款的 `[test:]` 與 REVISIT 一併處理(或改狀態為 abandoned)。

## F4 S6 說「輸出不變」,綁的測試只驗回傳碼,「多一行提醒」以外的輸出沒人守
severity: minor
blocking: 否
引句:「判定、輸出與回傳碼除了多一行提醒之外應不變」
file: `scripts/test_lumos.py:20177`
1. `t_guard_kill_rc_precedence` 內全部斷言只比 `r.returncode`(僅 20260 行的 `assert … , r.stderr` 在失敗時印 stderr),完全不讀 stdout/stderr 內容。
2. 因此 S6 前半(輸出不變)與後半(恰好多一行、而且只在失配時多)都沒有機械驗證:實作若在恰好 1 次的健康配方也多印一行,或誤動 `cmd_guard_kill` 的輸出,此條測試仍綠。
3. 建議 S6 拆成兩個可驗句:健康配方的 kill-add stderr 為空(S1 已涵蓋恰 1 次不印,應直接引用);`cmd_guard_kill` 輸出綁到會比對輸出的測試(如 `t_guard_kill_json_purity` 的一行 JSON 斷言),或另寫逐字快照。

## F5 「設定檔讀不了」在 load_platforms 只有 ValueError 路徑,JSON 壞掉會靜默退回 legacy 並用錯的根驗原文
severity: minor
blocking: 否
引句:「設定檔讀不了或平台不在設定裡:印一行」
file: `scripts/lumos:4517`
1. `load_platforms` 遇 `.lumos/config.json` 不是合法 JSON 時不 raise,只往 stderr 印一行提醒並退成 legacy(root=專案根);只有「platform 不是物件、profile 名未知」才 raise `ValueError`(4540、4543 行)。
2. 輸入:config.json 有一個逗號錯誤,多平台設定的 root 是 `./app` → kill-add 與 doctor P2 都拿專案根當平台根驗 `file`(`app/x.py` 這種相對 root 的路徑會變成 `missing`),整段列出一排假失配,而不是 S2/S4 說的「沒驗/這一段算不出來」。guard kill 同樣會用 legacy,但它不是提醒清單。
3. 另外 `load_platforms` 對不存在的 root 會自己往 stderr 印「⚠ 平台 … root 不存在」(4547 行),doctor 與 kill-add 各多印一次,對照 S1「恰好 1 次時應不印這條提醒」的測試要預期這行雜訊。
4. 建議:判斷 JSON 是否讀得動由呼叫端自己先 `json.loads` 一次,或在條款寫明「JSON 壞掉算設定讀不了」並測它;S4 的測試 fixture 要選 ValueError 路徑與 JSON 壞兩種。

最高等級:minor;blocking 共 0 條
