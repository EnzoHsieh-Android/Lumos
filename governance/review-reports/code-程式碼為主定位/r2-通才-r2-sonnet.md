severity: blocker

## F1 AGENTS.md 緊接在新 sentinel block 之後,還留著跟它互斥的「圖譜先行/唯一真相來源」舊句,漏抓的第四份同族副本
severity: blocker
blocking: yes

r1 為了修「同一句進場規矩還有三份硬編副本沒跟著改」,把 `_ENTRY_POINT_FILES` 鎖定三個檔(`lumos-entry-hook.py`、`INDEX.md`、`01-進場查脈絡.md`),並把範本/CLAUDE.md/AGENTS.md 的 sentinel block 改寫成「程式碼為主」。但 AGENTS.md 裡緊接在 `<!-- LUMOS:GRAPH-DISCIPLINE:END -->` 之後、屬於「本 repo 的規矩與現況單一來源」清單的那兩行,是**同一份 AGENTS.md 自己的內容**,完全沒被這輪動到,現在跟它正上方(patch 改寫過)的 sentinel block 直接矛盾。

引句:「先讀程式碼得出現況,再用 `lumos` 補程式碼看不出的脈絡」

重現:
1. 對本 repo 套用 `governance/review-reports/code-程式碼為主定位/r2-snapshot.patch`(`git apply`)。
2. `sed -n '1,90p' AGENTS.md`。
3. 第 4 行(sentinel block 內、patch 改過)寫「## 程式碼為主，知識圖譜補脈絡（必讀）」+「程式碼是「現在是什麼」的最終依據」。
4. 往下讀到第 85–86 行(sentinel block 結束後、patch 完全沒碰的舊內容):
   - `AGENTS.md:85`:`1. **專案規矩**：讀 \`CLAUDE.md\`（圖譜先行、零依賴家規、合約鏈、寫入規範）。`
   - `AGENTS.md:86`:`2. **系統現況**：讀 \`docs/lumos-toolchain-knowledge/MOC/index.md\`...圖譜是唯一真相來源，與 code 衝突以圖譜的合約（★INVARIANT★）為準。`

為什麼是 bug 不是風格:這正是 r1 自己要修的那個病灶——「一個 session 會同時收到兩套互斥的『第一步』」——只是這次兩套矛盾說法擠在**同一個檔案**裡相隔 4 行,比原本分散在三個不同檔案更容易被同一次閱讀直接撞見。而且新加的 `t_entry_points_agree_with_code_first` 守衛完全抓不到它:①`_ENTRY_POINT_FILES` 清單裡沒有 `AGENTS.md`;②就算把它加進清單,守衛只比對字面「第一個工具呼叫」這一種措辭,「圖譜先行」「唯一真相來源」是完全不同的字串,守衛的斷言 `"第一個工具呼叫" not in txt` 對這兩行永遠是 True(通過)。這是派工詞明確要查的「換個字串寫法就躲掉」的實例,而且不是假設情境——它現在就在 repo 裡。「圖譜是唯一真相來源」这句話也直接跟新定位「程式碼是『現在是什麼』的最終依據」相反(即使後半句「與 code 衝突以圖譜的合約為準」還算跟新規則 3 的例外條款相容,前半句的斷言本身就是舊定位)。

## F2 補回的「查不到不等於沒有」段只救回原四點裡的兩點,第三點(單篇筆記內部新舊打架的裁決規則)仍然遺失,而新守衛測試沒有能力發現這個缺口
severity: major
blocking: yes

r1 的背景說法是「改版時整段刪掉『查 0 筆不等於沒有、宣稱不存在前先派乾淨 agent 驗』的守衛...修法:那段補回範本」,聽起來像是完整復原。但用 `git show 5981b0df -- scripts/templates/graph-discipline.md` 看刪除前的原文,那一整段其實是 ①②③④ 四點合一段:①0 筆不是沒記(換同義詞、換三次) ②大節點先 `--brief` ③單篇筆記內部可能新舊打架,doctor 驗不出——摘要裡有日期的 KEY 行比正文段落新,衝突又影響決策就去 code 裁,再回頭修圖譜 ④宣稱不存在前先派乾淨 agent 驗。r1 補回的段落只等於 ①+④(②已被新範本的表格「這篇全文」那行涵蓋,算合理省略,但③在新版任何地方都沒有出現)。

引句:「判斷錯本來就要重查一次，這一步只是提前付；**只有這個場合要派，其他查詢照常**。」

重現:
1. 套 patch 後,`grep -rn "新舊打架\|KEY 行比正文\|比正文段落新" scripts/templates/graph-discipline.md CLAUDE.md AGENTS.md docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md` → 無任何命中。
2. 對照 `git show HEAD~1:scripts/templates/graph-discipline.md`(被刪之前的版本,commit 5981b0df 是刪除者)第 22 行,能看到第③點原文完整存在:「③ 單篇筆記內部可能新舊打架，doctor 驗不出——摘要裡有日期的 KEY 行比正文段落新，衝突又影響決策就去 code 裁，再回頭修圖譜」。
3. 新守衛測試 `t_template_keeps_absence_claim_guard`(`scripts/test_lumos.py:17593-17598`)只斷言兩個子字串存在:「換三次」與「乾淨 agent」——分別對應被刪段落的①與④,測試綠燈時完全不代表③也還在。

為什麼是 bug 不是風格:這是「修得不夠乾淨」的直接案例——r1 的說法(「那段補回範本」)給人「整段復原」的印象,守衛測試的名字（`t_template_keeps_absence_claim_guard`）和 docstring 也只講「這道守衛不得隨改版被整段刪掉」,沒有交代它只覆蓋原四點裡的兩點。結果是:③這條「筆記內部新舊資訊衝突時,以日期較新的 KEY 行為準、有分歧且影響決策要去 code 裁定」的規則,靜靜地從整個 repo 消失,而且沒有任何機制會再讓它翻紅——因為現在唯一盯著這段內容的測試,斷言範圍本來就沒包含它。

## F3 ARCHITECTURE.md 的架構圖仍把範本標成「圖譜先行紀律範本」,是漏掉的第五份同族殘留
severity: minor
blocking: no

引句:「先讀程式碼得出現況,再用 `lumos` 補程式碼看不出的脈絡」(新定位在 patch 裡的措辭,對照下方殘留)

`ARCHITECTURE.md:19`:`TPL["scripts/templates/graph-discipline.md<br/>(圖譜先行紀律範本)"]`——這是架構圖裡替 `scripts/templates/graph-discipline.md` 這個節點下的標籤,套 patch 後範本本身的定位已經是「程式碼為主」,但這行圖說明還停在舊名詞。跟 F1 同一族問題(散落副本没跟上),但這裡只是對外解說用的圖說明文字,不是會被兩套矛盾指令直接誤導行為的入口檔,而且 `t_entry_points_agree_with_code_first` 本來就沒把 `ARCHITECTURE.md` 列進檢查對象,不算守衛「該擋卻沒擋」,所以定為 minor、不視為擋門項,但建議跟 F1 一起清。

## F4 計劃筆記裡「這一批已改、尚未提交的檔」清單沒有跟著 r1 這輪新增的改動更新,五支被動到的檔沒列進去
severity: minor
blocking: no

引句:「這一批已改、尚未提交的檔**:`scripts/templates/graph-discipline.md`(開頭兩節改寫 + 分類表)、`CLAUDE.md`、`AGENTS.md`(用 `lumos update --no-pull` 同步,不要手改)。」

這行是 patch 裡的 context 行(hunk `@@ -61,19 +64,19` 範圍內,未被 r1 改動)。r1 這輪實際多動了 `scripts/hooks/claude/lumos-entry-hook.py`、`skills/lumos-project-notes/commands/INDEX.md`、`skills/lumos-project-notes/commands/01-進場查脈絡.md`、`docs/lumos-toolchain-knowledge/Systems/開發工作流總覽.md`、`scripts/test_lumos.py`(兩支新守衛)共五支檔,但這份「已改清單」完全沒提到它們(`docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md:72`)。

為什麼是 bug 不是風格:CLAUDE.md 鐵則一要求「改了會影響行為/決策/驗證的 code,同一次工作內寫回圖譜」,這份清單本身就是那次寫回的產物,現在清單本身沒跟上同一輪的改動範圍,下一個接手的 session 讀這篇計劃會誤以為這批只動了三個檔,漏看 lumos-entry-hook.py 等五個檔其實也在同一批未提交變更裡。不算擋門項,因為它不影響機制運作、只影響下個 session 讀筆記時的完整度。

---

## 已驗過、確認沒問題的部分(供收貨對照)
- 兩支新守衛測試(`t_entry_points_agree_with_code_first`、`t_template_keeps_absence_claim_guard`)在套 patch 後的 worktree 裡實際跑:`python3 scripts/test_lumos.py -k entry_points_agree` 3 passed,`-k template_keeps_absence_claim_guard` 6 passed。
- 翻紅釘實測:把 `INDEX.md` 一段改回舊句式「第一個工具呼叫...」→ `t_entry_points_agree_with_code_first` 真的紅;把 `CLAUDE.md` 的「查不到不等於沒有」整段砍掉 → `t_template_keeps_absence_claim_guard` 真的紅(兩條斷言都紅)。兩支守衛對它們宣稱要擋的事故形狀是有效的。
- `lumos update --no-pull` 同步後,`lumos doctor --ci` 在 worktree 裡回 0 issues、rc=0,Check D 沒有「不同步」警告——CLAUDE.md/AGENTS.md 的 sentinel block 確實跟範本一致(用 `_reinject_all`/`_expected_claude_body` 走同一份字串來源,機械上不會漂)。
- 「曾經以為的卡點,實際沒卡」那段改寫,逐句核對過:`python3 scripts/test_lumos.py -k claude_block_matches_template` 2 passed,`lumos doctor --ci` rc=0;`Systems/效能檢核目錄.md` 的 `OpenAsync` 確實還在 doctor `[Y]` 檢核裡,而該檢核標頭確實寫「提醒,不擋」——這段重寫是真的比原本的「卡在 Check Y 誤報」更貼近程式實際行為,不是又一次沒驗證就下筆。
- 「續接順序」重新編號(①→⑤)連續無斷號,也沒有殘留指向已撤銷三條解法(改關鍵字格式/改 Check Y/加註來源)的句子——撤銷句本身就在同一段明講撤銷,沒有散落到別處的殘留引用。
- 兩篇新計劃筆記(`Lumos定位_程式碼為主脈絡為輔_計劃`、`審查評測集_計劃`)的 `lands_in` 格式符合 `_lands_in_bad` 的驗證規則(純字串、`Systems/<名>`、不帶 `.md`),`lumos lint` 兩篇都 0 問題,指向的三個 Systems 節點(`開發工作流總覽`、`hook信任邊界`、`loop-convergence-recording`)在 repo 裡都真實存在。`Systems/hook信任邊界` 作為 lands_in 落點稍嫌鬆(這輪實際沒動到那篇正文,選它主要因為它既有 DEP 行點名 `lumos-entry-hook.py`),但格式與存在性都合規,未列為獨立發現。
