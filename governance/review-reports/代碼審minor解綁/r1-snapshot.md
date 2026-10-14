---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/design-loop
  - Systems/pitfalls-code-loop
related:
  - "[[Projects/probe輪退場_計劃]]"
  - "[[Verification/2026-10-14_修補大小與下一輪major回放]]"
  - "[[Projects/改動與修補拆小_計劃]]"
---
# 代碼審minor解綁_計劃

代碼審的處置閘現在規定:輪內任一席 severity 是 major 以上,這輪的 accepted 必須是空的——不只 major 要折,連同輪的 minor 也一條都不准附理由放行。帳本顯示這讓 minor 大量進入修補:77 個同時有 major、恰一筆載體、每條都標了逐條嚴重度的輪次裡,176 條 minor 有 174 條被折入;卷證裡有「為了折一條 minor 新加了通道、下一輪因為新通道缺測試被判 major」的完整鏈條(`code-週評通知` r2→r3)。這份計劃把這條連帶拿掉:major 以上照舊一律折,minor 可以附理由放行;並把「哪些問題算 major」寫清楚。

WHY:代碼審處置閘改成「accepted 裡每條的逐條嚴重度都必須是 minor 或 clean」,不再因同輪有 major 就禁止放行任何條 [出處:2026-10-14 使用者裁;[[Verification/2026-10-14_修補大小與下一輪major回放]];Codex 交叉診斷 `governance/review-reports/收斂診斷/codex-gpt-6-astra.md`] [因:連帶規則讓 minor 修補進入當輪、修補膨脹又帶出新的驗證義務;舊裁定 d2 要對齊的 panel 時代判準是「存活最高 ≤minor」——major 修掉、minor 可以留著,現行規則比它更嚴] [不選:維持現制;把 major 也開放附理由放行(代碼審 major=會做出錯行為,必修);只改手冊不改閘]
PRIOR-ART: Google Engineering Practices 的審查標準把必要的改正與可選的細節(Nit)分開處理(https://google.github.io/eng-practices/review/reviewer/standard.html);本 repo 散文設計審早就允許 non-blocking 附理由接受([[Projects/設計審收斂重定義_計劃]] d5,probe輪退場 d2 原文亦載「散文設計審維持 d5 現制」)。逐條嚴重度欄位(`--finding-severity`,帳上 `finding_severities`)與報告嚴重度解析(`_report_severities`)都已存在,沿用不另做。
RETIRE-IF: 上線後若出現「被放行的 minor 其實是 major、事後以逃逸記帳」累計 3 筆,或使用者回頭審放行理由覺得在放水,就恢復舊規(只改回處置閘那一個條件)。

## 範圍

- 做:①處置閘的代碼審輪級條件改成逐條判,並在同一處加一道數量檢查,防止把 major 標成 minor 來放行;②記帳加一個選填的降級清單(辯方用證據把 major 降成 minor 時記);③派工範本的嚴重度判準補三類常見爭議(測試抓不住錯、第二種寫法、文件不一致)何時算 major;④手冊同步。
- 不做:不改 blocker 規則(輪內有 blocker 照舊 accepted 必空);不開放 major 附理由放行;不改散文設計審;不改三輪上限、必派席與架構對齊席的嚴重度錨(架構對齊「引入第二種做法或跨層直呼算 major」是使用者先前定的,要動另裁);不改「原始報告不可改」——不做「編排者下調嚴重度後放行」。

## 做法

- **處置閘(代碼審)**:現在的條件是「`code-` 迴圈且輪內任一席 severity 是 major 或 blocker 時,accepted 非空就擋」。改成:
  - 輪內有 blocker 席:照舊 accepted 必空(這條本來就對所有迴圈成立,不動)。
  - 輪內有 major 席、載體帶 `finding_severities`:accepted 裡每個 id 的逐條嚴重度都必須是 minor 或 clean;有任一條是 major 或 blocker 就擋,訊息點名那幾個 id。
  - 輪內有 major 席、載體沒帶 `finding_severities`:照舊 accepted 必空(舊帳與不標逐條嚴重度的照舊判,回放結果不變)。
- **防放水檢查(處置閘,同一處)**:輪內有 major 席且 accepted 非空、載體帶 `finding_severities` 時,再算一個上限:
  - 分子:accepted 裡逐條嚴重度標成 minor 或 clean 的 id 數。
  - 分母:同輪各席最新一筆帳(跟處置閘取 `latest` 同一套,含載體自己)的報告,用 `_report_severities` 去掉檔級那行後,數 minor 與 clean 的宣告行;同一席同一份報告只算一次(鍵 `(auditor, report_sha256)`);再加上載體降級清單的條數。
  - 分子大於分母 → 處置集合判不過,訊息說明「標成 minor 的放行條數比報告裡的 minor 多」。報告讀不到時照處置閘既有的留痕重驗判不過(fail-closed)。
  - 這擋的是數量,不保證每條對應正確;對應正確靠收貨紀錄與審查。放在處置閘而不在記帳時,是因為載體不一定最後記,記帳當下拿不到同輪全部的報告。
- **降級清單**(`canary record` 載體筆的選填旗標 `--downgraded-set id=理由`,可重複):辯方附證據把某條原報 major 的發現降成 minor 時記。比照既有 `--refuted-set` 的檢查:每個 id 要在 `findings_set` 裡、逐條嚴重度要標 minor 或 clean、理由至少 4 字含實字、要帶 `--intake` 且 id 在收貨紀錄的重現表同一列出現(整字比對)。沒有降級就不帶。
- **沒標逐條嚴重度**:有 major 席、accepted 非空、載體沒帶 `finding_severities` → 照舊判不過(走舊規則)。所以「要放行 minor 就得標齊逐條嚴重度」不用另加記帳檢查,`--finding-severity` 維持選填。
- **放行理由**:放行的 minor 理由除了既有的「至少 4 字含實字」,手冊要求寫明去向——不修的理由,或延後到哪個 Issue。機械只驗既有條件,去向靠人。
- **嚴重度判準**(`skills/lumos-design-loop/templates.md`〈編排者判讀規則〉的 severity 錨補一段代碼審適用的判準,§3 派工詞的嚴重度一句指向它):
  - 測試抓不住錯:受影響的是合約行(★INVARIANT★ 等)或計劃驗收條款綁的測試、而且能舉出一個合理的改壞照綠 → major;一般測試完整度的改善 → minor。
  - 第二種寫法:照架構對齊席既有的錨判(不在這份計劃改);其他席報的「重複 helper」若講不出具體行為或維護風險 → minor。
  - 文件不一致:照文件做會做出錯的操作、或跟合約衝突 → major;措辭、精度、歷史數字 → minor。
- **手冊**:`skills/lumos-code-loop/SKILL.md` 第 7 步「code 迴圈輪內任一席 severity ≥ major 則 accepted 必空」改寫成新規則一句,同一步「架構對齊席與棧別檢核題…minor 可 accepted」那段一併收斂(新規則下已是常態);`reference.md` 新增一段:放行 minor 要寫去向、要帶 `--finding-severity`、降級清單怎麼記、防放水檢查擋什麼。
- **回放**:`loop replay` 跟 `loop status --disposal` 用同一支處置判定,新規則上線就套到回放。舊帳的載體都沒在 major 輪帶 `finding_severities` 放行 minor(有兩份凍結判定 `code-待決問題改存開頭欄位` r9、`code-審查跑滿回顧` r4 放行過、但沒帶逐條嚴重度,照舊判不過),所以判定不變;回放引擎版本號 `_REPLAY_ENGINE_REV` 不 bump。

## 驗收條款

- [S1] 當代碼審某輪有 major 席、載體帶逐條嚴重度、accepted 只含 minor 或 clean 的 id 且理由齊時,處置閘的處置集合 應 判過 [test:t_disposal_code_minor_accept]
- [S2] 當同樣情況但 accepted 含一個逐條嚴重度是 major 的 id 時,處置集合 應 判不過並點名那個 id [test:t_disposal_code_minor_accept]
- [S3] 當代碼審某輪有 major 席、載體沒帶逐條嚴重度、accepted 非空時,處置集合 應 照舊判不過 [test:t_disposal_code_minor_accept]
- [S4] 當輪內有 blocker 席、accepted 非空時,不論逐條嚴重度,處置集合 應 照舊判不過 [test:t_disposal_code_minor_accept]
- [S5] 當代碼審某輪有 major 席、accepted 裡標成 minor 或 clean 的 id 數,多於同輪各席報告的 minor 與 clean 宣告數加降級清單條數時,處置集合 應 判不過並說明 [test:t_disposal_code_minor_accept]
- [S8] 當記載體筆帶 `--downgraded-set` 而 id 不在 findings-set、逐條嚴重度不是 minor 或 clean、理由太短、或沒帶 `--intake`/收貨紀錄找不到該 id 時,`canary record` 應 以 rc 2 擋下 [test:t_canary_record_downgraded_set]
- [S6] 當用現有帳本對既有已凍結的迴圈跑 `loop replay` 時,判定 應 與改動前相同(舊帳在 major 輪放行過的載體都沒帶逐條嚴重度,走照舊分支);`_REPLAY_ENGINE_REV` 應 不變 [test:t_disposal_code_minor_accept]
- [S7] 當讀派工範本嚴重度一段與代碼審手冊時,三類爭議的判準與新的處置規則 應 寫在上面、跟程式一致 [manual:對照 templates.md §3 嚴重度一段與 SKILL.md 第 7 步、reference.md 的放行去向說明]

## 回退

- 處置閘:把那一個條件改回「`code-` 且任一席 ≥major → accepted 必空」,數量檢查一起拿掉;降級清單旗標可以留著不用(帶了也不影響舊規則)。改回後,上線期間在 major 輪放行過 minor 的迴圈會判不過,要改折入重記或攤人裁。
- 文件:還原範本嚴重度一段與手冊兩處。

## 實務隱患

已排除:金流:只改審查流程的判定與文件,不碰付款
已排除:對外送出:不連網、不寄送
已排除:不可逆:帳本只往後加,規則改回後新帳照舊判;沒有資料會被刪改
- 守衛面:處置閘是推送前的審查留痕依據,放寬會讓少修的輪也能過閘。防線:major 以上照舊必折;放行 minor 必須標逐條嚴重度,且記帳時數量檢查擋住把 major 標成 minor;舊帳回放判定不變(S6)。誤擋的逃生口:數量檢查若誤擋(例如一條報告的發現被編排者拆成兩個 id、或辯方降級沒記進降級清單),把多出來的那條改成折入、或補記降級清單就過,不需要繞過旗標;這次不新增任何略過旗標,所以沒有新的繞過路徑要留痕。
- 放水風險:編排者可能把該修的 minor 都放行。去向寫明靠人;RETIRE-IF 以逃逸帳與使用者回頭審判斷。
- 與另一個會談 spec-gate-nondo 的程式衝突:它把處置閘判定抽成 `_disposal_judge`、改了呼叫路徑;本計劃的實作接在它合併之後,改它抽出後的那段。

REVISIT:2026-11-14 看上線後代碼審放行 minor 的件數、理由寫了去向的比例、有沒有逃逸帳指回被放行的 minor,交使用者裁留或撤

