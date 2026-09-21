severity: major

## F1 範本改寫時整段刪掉「查 0 筆不代表沒記、斷言『不存在』前要先驗證」的守衛規則,九個消費專案 `lumos update` 後都會少這道保護

severity: major
blocking: yes

被砍的整段(AGENTS.md/CLAUDE.md/scripts/templates/graph-discipline.md 三處同步刪除,均在 patch 的「-」行內)原本規定兩件事:①查 0 筆時要換同義詞重查、換三次還不到才能問人、不准直接轉去用 grep;④要說「沒有／缺／不存在／沒人做過」之前,如果那句話會決定要不要動手做東西,必須先派一個乾淨 agent 拿「原始問題」去對答案,不能把自己的結論丟給它驗證。

引句:「換同義詞再查，換三次還不到再問人」
引句:「判斷錯本來就要重查一次，這一步只是提前付」

怎麼重現:在本輪凍結 patch 涵蓋的三個檔(AGENTS.md、CLAUDE.md、scripts/templates/graph-discipline.md)裡搜尋上面兩句引句,只在「-」(刪除)行出現;搜尋新版「+」內容與整份新增的兩篇計劃節點,兩句話、以及規則④的核心動作(「先派一個乾淨 agent」「不要把你的結論丟給它」)全部消失,沒有被移到別處、也沒有留下替代規則。我在唯讀 worktree(`/tmp/seat-通才-sonnet`,detach 自本 repo HEAD)裡跑過機械驗證:
`grep -n "先派\|乾淨 agent\|不要轉頭去\|換三次" scripts/templates/graph-discipline.md CLAUDE.md AGENTS.md` → 零命中;同一指令對 `git show 9b12f994:scripts/templates/graph-discipline.md` → 命中舊版那整段。

為什麼是 bug 不是風格:這道規則不是「圖譜先行 vs 程式碼為主」立場之爭的產物——它管的是任何一個 AI 在說「這個功能/這個坑沒人記錄過/不存在」之前要不要先驗證,兩種定位下都同樣需要,而且正是本 repo 自己記憶庫裡明文記過的教訓(`docs/lumos-toolchain-knowledge/Verification/2026-08-22_缺席推論探針題組.md:160-161` 原話就是被刪的那句規則的出處;`docs/指令參考.md:32` 也單獨記著「0 筆不代表沒記」的版本)。這份範本是 `lumos update` 注入到**每一個消費專案**的單一來源,砍掉之後這些專案的 CLAUDE.md/AGENTS.md 會同步失去這道守衛,而新增的兩篇計劃節點裡完全沒有一句話交代「這條規則我們決定不要了,理由是什麼」——不符合 CLAUDE.md 本身鐵則 4 要求的「承認風險要附回頭看的條件」,是一次沒有留痕的行為放棄,正對到派工詞的檢查點④(新舊段落有沒有把原本擋得住的行為放掉)。

## F2 新增計劃節點記的「卡點」跟實際程式碼行為對不上——聲稱 doctor 被 Check Y 卡住、測試過不了,但拿本批凍結內容實跑,doctor 已經是 0 issues、測試已經全綠

severity: major
blocking: yes

`docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md` 新增內容裡寫:

引句:「有一條斷言要求 `lumos doctor` 0 issues,現在卡在」
引句:「①解掉卡點讓漂移守衛綠」

這段把「讓 `t_claude_block_matches_template` 通過(doctor 0 issues)」列成續接順序的**第一步、目前未解**,理由是 `Systems/效能檢核目錄.md` 的 Check Y 誤報擋住。但這條斷言測的正是**本輪 patch 自己改動的檔**(CLAUDE.md/AGENTS.md 的紀律區塊 vs 範本)是否同步。

怎麼重現:在唯讀 worktree(HEAD=5981b0df,即本批凍結內容本身)實跑:
`python3 scripts/test_lumos.py -k claude_block_matches_template` → `2 passed, 0 failed`(`claude_block_matches_template: 本 repo doctor Check D 淨(0 漂移)` 與 `本 repo doctor 整體 0 issues` 兩條都過)。
另外直接跑 `python3 scripts/lumos --vault docs/lumos-toolchain-knowledge doctor --ci`,結尾印「✓ 圖譜健康 — 0 issues (546 篇)」,回傳碼 0;`Systems/效能檢核目錄.md` 的 `OpenAsync` 確實還在 Check Y 名單裡出現(`[Y] 筆記點名的方法或類別...⚠ 有 1 個...OpenAsync`),但那一段在 doctor 輸出裡明白標成「提醒,不擋」,不計入 issues 計數,從沒讓 `--ci` 回傳非 0。

為什麼是 bug 不是風格:這正是本批 patch 自己在 CLAUDE.md 裡新定的規矩要處理的情境——「筆記跟程式對不上時…以程式碼為準,並立一篇 Issue 記下那句筆記錯在哪」——但這篇新筆記自己違反了這條規矩:它的敘述(卡住、未解)與可重跑的程式行為(已經 0 issues、測試綠)不符,卻沒有被標成「以程式碼為準」或補一筆 Issue,而是被當成續接計劃的既定事實往下推。下一個接手 session 如果照著「續接順序①」去修 Check Y 或改 doctor,會是在解一個已經不存在的假閘,浪費工時(該篇甚至明寫「選②要改 doctor,得走代碼審」——一個不必要的代碼審);更嚴重的是它也可能因此誤判「這批還沒到能過代碼審的狀態」,而實際上機械證據顯示閘早就是綠的。

## 我另外驗過、沒發現問題的部分

- `test_full_sweep_threshold_covers_real_stock` 的假鐘推進數學:逐一手算並用 `mock.patch.object` 把 `FULL_SWEEP_SECONDS` 改回 60 實跑,確認 `self.assertEqual(len(out2["replayed"]), 134, ...)` 真的會翻紅(`5 != 134`)——即使把前面那條檢查常數值的斷言拿掉、只留行為斷言也一樣翻紅,不是靠巧合過。
- `test_new_always_run_and_rotation_cursor_advances` 已經用 `self.enterContext(mock.patch.object(self.m, "FULL_SWEEP_SECONDS", 1))` 明講把升級全量門檻壓到 1 秒,原本「10 秒×7 包=70>60」的隱含假設已經被拆掉,換成不依賴門檻具體數值的寫法,沒有殘留數字巧合。
- `scripts/scenario_probe.py` 的 `RULE_HEAD`/`RULE_END` 改成 `### 怎麼用` / `### 寫筆記時` 後,在同一份 worktree 對真實 `CLAUDE.md`、`AGENTS.md` 跑 `strip_lumos_first_rule`:兩個標記在兩份檔案裡都恰好各出現一次,`e > s` 順序正確,砍掉的內容正好是「怎麼用」小節(工具查詢表),保留「寫筆記時」的 WHY/RULE/PITFALL/FACT 分類表與「鐵則」——消融實驗「不帶查詢指引、但保留寫筆記規範」的前提沒有被改壞。
- `lumos update` 的紀律區塊注入/偵測邏輯(`scripts/lumos` 裡的 `_CLAUDE_START_PREFIX`/`_CLAUDE_END`/`_reinject_claude_block`)只認 `<!-- LUMOS:GRAPH-DISCIPLINE:START/END -->` sentinel 註解,不依賴區塊內文字(標題從「知識圖譜先行」改成「程式碼為主」),不會因為改標題而找不到注入點。
- `governance/eval/review-evalset/v1.json` 裡「核心題」與「待人工判定」共 199 條路徑引用(凍結材料/席位報告/收貨表/報告)在 worktree 裡全部存在,沒有斷鏈。
