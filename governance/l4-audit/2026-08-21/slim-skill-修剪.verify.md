C1 [✅] slim/skills/lumos-project-notes/{SKILL.md,reference.md} 存在,且首次交付 commit 訊息自陳「對直接複製的…逐條裁決」,證同源複製 | 證據: slim/skills/lumos-project-notes/SKILL.md, reference.md 存在;git commit cf209d6 訊息(`Task 4: 對直接複製的 slim/skills/lumos-project-notes/{SKILL.md,reference.md} 逐條裁決…`)

C2 [✅] 首次交付 commit 訊息明記初次候選 129 條 | 證據: git log -1 cf209d6:「逐條裁決 129 條懸空引用候選(改寫50/刪78/初裁假陽性1)」

C3 [✅] 對 c9808bf 的父提交(d59f201)重跑 scripts/slim-scan.py,候選數實測為 14 | 證據: `python3 scripts/slim-scan.py`(c9808bf~1 快照)輸出 total:14

C4 [✅] 現行與歷史(cf209d6)狀態下,單獨掃 slim/skills/lumos-project-notes/SKILL.md 皆為 total:0 | 證據: `python3 scripts/slim-scan.py slim/skills/lumos-project-notes/SKILL.md --json` → total:0(現行與 cf209d6 快照皆同)

C5 [✅] 「子命令全覽」段落於 cf209d6 快照:完整版 53 支(skills/lumos-project-notes/reference.md:85)→精簡版 24 支(slim/…/reference.md:60),分類數 12+4+7+1=24 逐項核對相符 | 證據: cf209d6 快照 skills/lumos-project-notes/reference.md:85「53 個頂層命令」;slim/skills/lumos-project-notes/reference.md:60「本精簡版 24 支頂層命令」,讀取/導航12(context show contracts search links backlinks map export decisions stale recent stats)+巡檢/治理4(doctor lint sync-verified-by rel-cascade)+寫入7(set append new archive decision-add decision-supersede decision-reindex)+合約守衛1(guard)

C6 [✅] 三處刪除皆核對屬實:① `pitfall_when` 說明僅存在完整版 skills/lumos-project-notes/reference.md:173-178,精簡版無命中 ② 完整版 reference.md:719 起「對抗設計審計的 canary」整節,精簡版全無 `canary` 字樣 ③ 完整版 reference.md:77-84 三列安裝/生命週期表(install/uninstall/update/bootstrap 四支),精簡版同段(reference.md:59)改寫成單句聲明「皆未交付」,原表格已刪 | 證據: skills/lumos-project-notes/reference.md:173,719,77-84 vs grep slim/…/{SKILL.md,reference.md} 均無命中(pitfall_when/canary)

C7 [❌] 行號現已漂移:目前 `npx playwright install` 在 reference.md:343,非第 340 行(340 行現為 markdown 表格結尾```);但在最初交付當下(commit cf209d6)確實精準落在第 340 行,且該掃描候選確為當時掃描結果中唯一 prose 形態、與 lumos 指令無關的真假陽性 | 證據: 現行 `grep -n "npx playwright install"` → 343:...;cf209d6 快照同 grep → 340:...(後續多次補修插入段落使全檔行號下移 3 行)

C8 [✅] reference.md 第 60 行(對應 2026-07-31 終審 C1 修復當下狀態,commit c9808bf)確實新增「doctor 建議跑 lumos init／lumos update／lumos self-audit,這三支未交付」段落 | 證據: c9808bf 快照 slim/skills/lumos-project-notes/reference.md:60「⚠ `doctor` 的某些檢查會建議跑 `lumos init`／`lumos update`／`lumos self-audit`……這三支未交付,看到請忽略」(現行檔案因 2026-08-19 補交付 update,該段已改寫為僅列 init/self-audit/signoff,位移至第 61 行——與 C8 所指的 2026-07-31 版本仍一致)

C9 [✅] reference.md 第 18 行現行內容正是「vendored 情境下不等價、禁用 python3 scripts/lumos」的改寫句 | 證據: slim/skills/lumos-project-notes/reference.md:18「★不要用 `python3 scripts/lumos`★——若你所在的專案本身 vendored 了完整版…那個寫法會呼叫到完整版全部指令…走錯路徑後果不同」

C10 [✅] c9808bf 修復前後實測 `python3 scripts/lumos` 前綴出現次數為 37→0,精確符合「37 處改為 lumos」 | 證據: c9808bf 父提交快照 `grep -o "python3 scripts/lumos" reference.md \| wc -l` → 37;c9808bf 快照同指令 → 0

C11 [✅] 終審修復(c9808bf,含 C1+C4)後對 slim/skills/lumos-project-notes/{SKILL.md,reference.md} 重跑 scripts/slim-scan.py,候選數精確為 21,對照修復前(14)確為 14→21 | 證據: c9808bf~1 快照 total:14;c9808bf 快照 total:21(皆用 c9808bf 當時的 scripts/slim-scan.py + scripts/lumos --help 現算,非現行版本掃描器回溯)

C12 [✅] commit 7eae1de(2026-08-01)於 reference.md 第 679 行將原指向 `Projects/from-scratch重生守衛_計劃`/`governance/golden/fromscratch-m1/` 的句子改寫為「★本精簡版沒有交付那些檔案★」,且現行 slim/ 目錄下查無 fromscratch-m1/golden 路徑 | 證據: 7eae1de 快照 slim/skills/lumos-project-notes/reference.md:679 全文比對;commit message 自陳「reference.md 指向本包未交付的設計全文與 golden 語料路徑(接手者查無此檔)」;`find slim -iname "*golden*" -o -path "*fromscratch-m1*"` 無結果

C13 [✅] scripts/slim-scan.py 的 scan_line() 僅實作五種指令名形態比對(prefixed/bare-token/span-with-args/skill-name/prose),無任何路徑字串(如 `docs/…-knowledge/`、`governance/…`)比對邏輯 | 證據: scripts/slim-scan.py:60-97(五段 for/re.finditer,皆比對 token 對 `removed` 指令集合,無 path 或 `/` 分段比對)

C14 [❌] claude-block.md 確有補一段含正確 YAML 範例(frontmatter `summary: \|-` 完整 code fence)的警告;但 slim/skills/lumos-project-notes/SKILL.md 對應段落(第 89-96 行)只在散文中提及 `` `summary: \|-` `` 這個 code span,並無完整 YAML frontmatter 範例區塊(無 `---`/`type: system` 等圍欄) | 證據: slim/claude-block.md:20-29(含 ```yaml 圍欄,`type: system`/`summary: \|-`/KEY 行範例);slim/skills/lumos-project-notes/SKILL.md:93(僅「★位置是 frontmatter 的 `summary:` 欄位…不是 body 裡開一個 `## Summary` 標題★」一段散文,無 yaml 圍欄範例;檔內 grep ` ``` ` 圍欄清單(36/38/110/113/123/126/156/167 行)均非此主題)

C15 [✅] 首次交付 commit 訊息精確載明改寫50+刪78+初裁假陽性1=129 | 證據: git log -1 cf209d6:「129 條懸空引用候選(改寫50/刪78/初裁假陽性1)」

✅11 ❌3 ❓0 ⏭0
