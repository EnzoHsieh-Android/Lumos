severity: major

這份是整合/知識同步席的報告,只讀。對照了 `scripts/lumos`、圖譜、skills 與手冊。前掃已報的項目(接力涵蓋所需帳欄位、一處替換不是機械界線、`kill-add` 不限長度)不重報。

## Finding 1
severity: major
blocking: 是 — 第 7 條「代碼審看得到殘留」的前提在程式裡不成立,殘留戳記多半印不出來。
引句:「派工鏡頭附合約行時本來就把整行(含戳記)印出」
問題:派工鏡頭渲染合約行時只印前 200 字,徽章再接在截斷之後。戳記照 `guard audit` 現行寫法接在行尾,長合約行的戳記會被截掉。
失敗情境:我數了圖譜裡有 `[audit:]` 的 ★INVARIANT★ 行,36 條裡有 22 條的戳記起點超過第 200 字。這些合約行補上 `殘留:節點#d12` 後,代碼審席拿到的鏡頭只有被截掉的前半。「看到帶殘留就去讀殘留決策」那句派工詞不會被觸發,整個「交給代碼審」的出口是空的。計劃自己的 S6 只驗範本有這句話,沒驗這句話會被觸發。
佐證:`scripts/lumos:48360-48365`(`lines.append("  " + full[:200] + badge)`)與 `scripts/lumos:47705-47707`(`_lens_contract_lines` 同樣截 200)。計劃的判斷依據是 intake p10 的「派工鏡頭的規則是不轉述自由文字」,它沒查截斷。

## Finding 2
severity: major
blocking: 是 — 殘留只在代碼審被派出時才有人看,而風險分級完全不看合約。
引句:「代碼審派工範本加一句:看到帶殘留的合約,去讀那筆殘留決策」
問題:`_pitfall_tier` 只看風險型樣、新告警和有沒有程式檔,不看改動碰到哪條合約,也不看戳記。tier standard 的推送不強制代碼審,也沒有派工鏡頭。
失敗情境:一個功能提交新增了「不加鎖的快路徑」,這正是計劃列為殘留的那一型。它沒命中風險型樣,於是判成 standard、不跑代碼審,殘留決策沒有人讀。測試抓不到這一型,代碼審又沒派,等於兩道都沒守。RETIRE-IF 與 REVISIT 只數戳記條數和逃逸,沒有任何機制讓「碰到帶殘留合約的改動」升級到 high。
佐證:`scripts/lumos:43677-43690`,tier 只有 high / light / standard 三種結果。

## Finding 3
severity: major
blocking: 是 — 分類與記殘留都由被審方的編排者做,違反本 repo 自己的 maker≠checker 規則,而且可被塑造。
引句:「審計員分類、編排者覆核;判不準的當局部退化」
問題:判準是「設計點名的機制還在不在」,而「設計點名了什麼機制」是寫合約的人在 decisions 與緣起裡寫的。殘留決策、`--residual` 戳記也都由編排者落筆。
失敗情境:想讓三輪內收斂的編排者,把測試抓不到的反例措辭成「繞過設計」,記一筆殘留決策就結案。工具只檢查決策存在、沒標 `valid: false`、內容非空,不檢查分類對不對,也不檢查「第幾輪審計收斂」那句有沒有寫。「判不準當局部退化」只約束判不準的情況,擋不住被審方主動把它判準成繞過。
佐證:`skills/lumos-project-notes/reference.md:534`,理由是「讓提出者自己評必手下留情」。`docs/methodology/圖譜即合約.md:95` 與 `:323` 寫的是「maker≠checker,別讓提鐵則的人自己認證」。計劃只靠編排者「覆核」,沒有獨立的第二個人判分類。

## Finding 4
severity: major
blocking: 是 — 計劃舉的「繞過設計」例子,就是原第 3 問要抓的最常見真違規,而且與 d12 人裁原文不符。
引句:「另開不加鎖的快路徑、拿掉資料庫約束改用程式內互斥並跑多個節點」
問題:d12 的人裁原文是「刻意繞過設計的改法屬於代碼審要擋的範圍」。計劃把「新增一條沒走鎖的路徑」也歸入繞過,但這多半是實作者漏接,不是刻意。合約「所有寫入必經鎖」被這種路徑違反,綁定測試只測原路徑照過,正是原第 3 問的標準情形「違反保證但測試仍過」。
失敗情境:原判準的目的是揪出只測單一函式、看不到新路徑的稻草人測試。改制後,這類測試加一筆殘留就算 `[audit:… 殘留:…]` 通過。`guard list` 與 Check T 把它和乾淨過同樣視為已審,doctor 沒有殘留總數的提醒。
佐證:計劃第 26 行(d12 原意)對 `skills/lumos-project-notes/reference.md:548`(原第 3 問「構造得出=同源/套套邏輯,不合格」)。`scripts/lumos:2105` 與 `scripts/lumos:6722` 只看 `invariant_audit_refs` 是否非空。

## Finding 5
severity: major
blocking: 是 — A 半讓資安席「看過的檔」從實際閱讀變成帳面宣告,而清單本身建立在這個宣告上。
引句:「清單上沒有的檔,處置閘一定判涵蓋」
問題:處置閘的涵蓋是比對該席帳上掛的凍結 patch 檔案與指紋,不是它真的讀了什麼。計劃要求帳上仍掛整份新 patch,派工詞卻叫席只讀清單。`sec-delta` 又用同一套「帳上看過」去推下一輪的清單。
失敗情境:第 1 輪資安席受 1800 行上限所限只讀了一部分,帳上卻掛整份 patch。第 2 輪 `sec-delta` 認定未變動的檔「看過」,不列入。於是一支檔從頭到尾沒有任何資安席讀過,閘卻全數判涵蓋。原本每輪整份重讀,至少會補到它。資安席計劃 r1 兩席各自實跑、用「同檔名內容改掉」繞過涵蓋,才把比對改成比內容,本案等於把同一個洞挖回來。
佐證:`scripts/lumos:26085-26090`(`seen` 來自帳上 `snapshot_path`),以及 `skills/lumos-design-loop/templates.md:211`(§3.1 第 5 步要求每席讀總量超過 1800 行就拆範圍,且「完整改動」要列進 materials)。

## Finding 6
severity: minor
blocking: 否 — 屬於範圍與句子漏同步,補列即可。
引句:「§3.1 第 5 步末句「資安席對最後完整快照的覆蓋規則仍照原制」保留」
問題:A 半只列了 §3.1 第 5 步和 §7.8,漏掉下面這些:
- `templates.md:398`(§7.8 開頭)寫「要它看過的檔涵蓋最後一版凍結 patch 的全部檔——修正時新碰到的檔,要對最新的凍結 patch 再派一次」,與新規則同段對打。
- `skills/lumos-code-loop/SKILL.md:31` 與 `skills/lumos-code-loop/reference.md:587`。
- 處置閘失敗訊息「接下來:對最新的凍結 patch 再派一席資安」(`scripts/lumos:26095`),照做會回到整份重審。

B 半漏掉下面這些:
- `docs/methodology/圖譜即合約.md:95` 與 `:323`。
- `skills/lumos-project-notes/reference.md:672`(`[audit:]` 說明)。
- `skills/lumos-project-notes/commands/06-代碼審與推送.md:18`(`guard audit` 指令表,要補 `--residual`)。
- `docs/lumos-toolchain-knowledge/Systems/design-loop.md:69-70` 的 KEY 行(五問、防應試化)。
- `reference.md:524` 起 `guard kill` 補救順序。

還有守衛問題:沒有任何 `t_*` 釘住 reference.md 的五問字句,S5 是 `[manual:]`。唯一釘 §7.8 的 `t_templates_security_seat_section` 只驗關鍵詞,不驗涵蓋規則的字句。B 的核心規則改動沒有機械守衛。
失敗情境:手冊、訊息與範本各說各的,下一個會談照舊句子做,回到整份重審。

## Finding 7
severity: minor
blocking: 否 — 影響有限,補掛即可。
引句:「合約審計第 3 問照 2026-10-13 那次人裁的判準」
問題:`lands_in` 只列 `Systems/loop-convergence-recording` 與 `Systems/guard-kill`。B 半的主要程式落點是 `guard audit`、doctor 戳記檢查、Check T,現況它們沒有明確的家。`check-t-sentinel` 寫的其實是 Check K(COMBO)。計劃沒有說這些落在哪一篇。鐵則 5 要求改到的每支檔先有家,否則提交前被擋。

## Finding 8
severity: minor
blocking: 否 — 有三輪上限與人裁兜底,風險是被誘導成改標而非卡死。
引句:「`survived` 就補測試;`killed_unattributed`、`timed_out_weak` 算沒殺掉」
問題:`killed` 才算處理完這個門檻,和現行機制有兩處對不上。一是 `kill-add --try` 的試跑一定是弱證據(筆記剛寫沒提交,見 `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:83`),計劃沒寫要先提交才能得到強證據。二是配方只有一檔、一處恰好命中的替換,表達不了多檔或時序型的局部退化(例如少呼叫兩處、競態)。
失敗情境:表達不了的局部退化殺不掉,編排者就有誘因把它改標成「繞過設計」收尾,與 Finding 3 疊加。每輪反例都存成永久配方,`guard kill` 的負擔也會累積(未量測)。

## Finding 9
severity: minor
blocking: 否 — 屬於流程順序問題。
引句:「沒有殘留照舊 `[audit:模型/日期]`」
問題:`guard audit` 重審是整串覆蓋舊戳記(`scripts/lumos:18746-18750`)。第二、三輪審計若編排者忘了再帶 `--residual`,殘留標示就靜默消失,帳上看起來是乾淨過。
另有未驗證的疑點:殘留決策存放在計劃節點。計劃做完後會被 `cmd_archive`(`scripts/lumos:22819`)歸檔或被改名,「節點存在」的 doctor 檢查是否會因此誤報,我沒有驗證。

## Finding 10
severity: minor
blocking: 否 — 只是驗收條款寫得過滿。
引句:「兩邊用同一支比對函式,不會不一致」
問題:處置閘還有其他失敗條件,例如帳上報告 sha 不對、patch 抓不到任何檔名。清單空不等於閘一定判涵蓋。S2 把「清單為空」當成「閘判涵蓋」的充要條件,對照處置閘實作並不精確。
佐證:`scripts/lumos:26070-26080`。

## Finding 11
severity: minor
blocking: 否 — 與防應試化的第二道直接相衝,但目前沒有造成誤放行。
引句:「派工時照那一段的防應試化規則改述措辭,不逐字貼」
問題:防應試化第二道是約每 5 次審計抽 1 次不帶 rubric 的開放判定,並比較落差。新規則下 rubric 組允許帶殘留通過,開放判定組不受這套分類約束,落差會被系統性地拉大,拿它當「評分表儀式化」的訊號就失真。新增的兩類分法本身又成了一份固定的評分細則,計劃沒說抽考怎麼對應。
佐證:`skills/lumos-project-notes/reference.md:553`。

已讀,無 finding:資安席計劃的生效日、凍結閉包與回放相容,以及舊版 `[audit:]` 讀者的回溯相容(`AUDIT_REF_RE` 為 `[^\]]+`,帶殘留的戳記照舊判為已審,S4 方向正確)。

最高等級 major,共 11 條 finding,其中 blocking 5 條(Finding 1、2、3、4、5)。
