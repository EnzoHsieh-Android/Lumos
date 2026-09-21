severity: blocker

## F1 開發工作流總覽.md 是計劃筆記自稱被守衛釘住的「七處」之一,但守衛名單裡沒有它,而它自己的摘要行跟這次改的內文正在打架

觀察到什麼:這次的計劃筆記改寫段落明講,同一句進場規矩散在七處,其中一處就是 `Systems/開發工作流總覽.md` 的流程圖,並且宣稱兩支漂移守衛已經把七處都釘住。但 `scripts/test_lumos.py` 新增的 `_ENTRY_POINT_FILES` 掃描名單只有七個項目,裡面沒有 `Systems/開發工作流總覽.md`(名單是 lumos-entry-hook.py / INDEX.md / 01-進場查脈絡.md / AGENTS.md / CLAUDE.md / ARCHITECTURE.md / README.md)。而這批 diff 同時把 `開發工作流總覽.md` 的 mermaid 內文改成「先讀程式碼」新定位,卻沒動它 YAML frontmatter 裡的 `summary:` → `FLOW:` 那一行——那一行至今仍是「①寫計劃(先查圖譜三步...)」。`lumos search`/`lumos context --brief` 對外顯示的正是這段 FLOW 摘要,不是 mermaid 圖本身,所以一個下一個 session 的 AI 用 `lumos search` 或 `context --brief` 查這篇節點,看到的第一手結論仍是「先查圖譜三步」,跟同一篇節點被這次 patch 改掉的內文互相矛盾——而「同一篇筆記內部也會新舊打架,查不到就去程式碼裁」正是這次 patch 自己新加進 CLAUDE.md/AGENTS.md/範本的規則,結果自己編輯的節點先犯了這條。

怎麼重現:
1. `python3 scripts/test_lumos.py -k entry_points_agree` → 7 passed, 0 failed(名單裡沒有這篇,所以測不到它)。
2. `grep -n "先查圖譜三步" docs/lumos-toolchain-knowledge/Systems/開發工作流總覽.md` → 命中第 17 行(frontmatter `summary:` 的 `FLOW:` 行,patch 沒有動過這行)。
3. 對照同一篇被這次 patch 改掉的內文(見下方引句)——同一個節點,兩種定位並存,doctor / 這兩支守衛都不會叫。

為什麼是 bug 不是風格:這正是計劃筆記自己宣稱「由兩支漂移守衛釘住」的七處之一,守衛名單卻漏了它,而漏掉的這一處剛好是真的還在互斥的一處——不是理論上的漏洞,是已經發生的內部矛盾,而且是被 lumos search/context 優先端出去的那段文字。這條 PR 兩輪修正的核心訴求就是「消滅入口檔的新舊定位互斥」,結果自己編輯的檔案裡就留了一個,守衛卻回報全綠。

引句:「Systems/開發工作流總覽.md 的流程圖——同一句規矩散在七處,漏掉任何一處就會有兩套互斥的第一步」(出自 `docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md` 那段改寫,patch 第 142 行)

引句:「① 動手前先寫計劃<br/>規矩:先讀程式碼得出現況,再翻圖譜補程式碼看不出的脈絡」(出自 `docs/lumos-toolchain-knowledge/Systems/開發工作流總覽.md` 的 mermaid A 節點,patch 第 197 行——跟下面外部查證的 frontmatter 摘要行矛盾)

外部查證:`docs/lumos-toolchain-knowledge/Systems/開發工作流總覽.md:17`(FLOW 摘要行,patch 未觸碰,仍寫「①寫計劃(先查圖譜三步...)」)、`scripts/test_lumos.py:17550`(`_ENTRY_POINT_FILES` 定義,七項裡沒有這篇節點的路徑)

severity: blocker
blocking: yes

## F2 三句白名單擋不住第四種舊定位措辭,連已經在掃描名單裡的檔案都漏

觀察到什麼:守衛測試 `_OLD_POSITION_PHRASES` 只有三句(「第一個工具呼叫」「圖譜先行」「唯一真相來源」),但至少有兩個已經被列進 `_ENTRY_POINT_FILES` 掃描名單的檔案,現在還留著沒被這三句涵蓋的舊定位措辭,測試照樣全線:
1. `ARCHITECTURE.md` 第 163 行,mermaid 節點原句是「提醒「第一個動作先查圖譜」」——用引號直接宣稱 SessionStart 訊息在講「先查圖譜」,但這批 patch 已經把 `lumos-entry-hook.py` 的 `msg` 改成「先讀程式碼」開頭,這句話現在是錯的,而且措辭是「先查圖譜」不是「第一個工具呼叫」,白名單抓不到。
2. `scripts/hooks/claude/lumos-entry-hook.py` 自己第 7 行的 module docstring 寫「提醒「第一步敲 lumos」」,第 254 行註解寫「連核心「先查圖譜」提醒都被吃掉」——這兩處都在同一支被這次 patch 改過 `msg` 內容的檔案裡,措辭跟改動後的訊息本體(「程式碼是現況的依據,圖譜補程式碼看不出的脈絡...先讀程式碼」)對不上,但因為不含三句白名單裡的任何一句,測試不會紅。

怎麼重現:
1. `grep -n '先查圖譜\|第一個動作' ARCHITECTURE.md` → 命中第 163 行「提醒「第一個動作先查圖譜」」。
2. `sed -n '7p;254p' scripts/hooks/claude/lumos-entry-hook.py` → 兩行都出現「先查圖譜」/「第一步敲 lumos」。
3. `python3 scripts/test_lumos.py -k entry_points_agree` → 仍是 7 passed, 0 failed,不會對這兩處反應。

為什麼是 bug 不是風格:r2 把守衛擴大到七個入口檔、白名單擴到三句的理由(patch 裡的守衛註解)明講是要抓「換個說法就繞過去了」這種案例;但實際上「先查圖譜」這個更常見、更口語的舊說法本身就沒被收進白名單,即使檔案已經在掃描名單裡也一樣抓不到。這不是還沒輪到掃描的檔案,是已經在掃描名單裡卻因為措辭沒對齊而漏網,證明「守衛已經釘住七處」的宣稱本身站不住腳。

引句:「_OLD_POSITION_PHRASES = ("第一個工具呼叫", "圖譜先行", "唯一真相來源")」(patch 第 326 行,`scripts/test_lumos.py`)

引句:「msg = ("本專案用 lumos 知識圖譜。程式碼是現況的依據,圖譜補程式碼看不出的脈絡:為什麼這樣決定、」(patch 第 247 行,`scripts/hooks/claude/lumos-entry-hook.py` 改後的訊息本體,跟下面外部查證的舊措辭對不上)

外部查證:`ARCHITECTURE.md:163`(「提醒「第一個動作先查圖譜」」)、`scripts/hooks/claude/lumos-entry-hook.py:7`(module docstring「第一步敲 lumos」)、`scripts/hooks/claude/lumos-entry-hook.py:254`(註解「先查圖譜」)

severity: major
blocking: yes

## F3 補回範本裡「照上面第 3 條」指的方向錯了,三份檔案(範本/CLAUDE.md/AGENTS.md)都一樣

觀察到什麼:r2 補回的「同一篇筆記內部也會新舊打架」那一段,結尾寫「衝突又影響決策時,照上面第 3 條去程式碼裁」,但這段文字在文件裡的實際位置是插在項目 2(「動手改之前…」的查詢表)之後、項目 3(「筆記跟程式對不上時…」)宣告之前——也就是說,讀者讀到「上面第 3 條」這句話的當下,項目 3 根本還沒出現在上文,它是在下面才出現。這個方向錯誤在範本、CLAUDE.md、AGENTS.md 三份檔案裡是同一段文字,三份都錯,而且這段話正是 r2 這一輪新補回去的內容,兩輪審查都沒挑出來。

怎麼重現:
1. `grep -n "^[0-9]\.\|照上面第 3 條" CLAUDE.md` → 「照上面第 3 條」出現在第 24 行,而「3. **筆記跟程式對不上時…」出現在第 28 行——引用的條目在下面,不在上面。
2. 同樣的結構在 `AGENTS.md`(第 25 行 vs 第 28 行)與 `scripts/templates/graph-discipline.md`(第 22 行 vs 第 26 行)各重演一次。

為什麼是 bug 不是風格:CLAUDE.md 開宗明義寫「讀者主要是下一個 session 的 AI(偶爾是人),寫的時候以『沒有脈絡的人讀得懂』為準」——一個沒看過全文的讀者讀到「上面第 3 條」,合理反應是往上找,但上面只有項目 1、2,找不到「第 3 條」,只會先困惑再繼續往下讀才發現。這不是文字風格問題,是這份文件對自己編號位置的指涉寫錯方向,而且這份範本是 `lumos update` 灌進每個消費專案 CLAUDE.md/AGENTS.md 的單一來源,錯誤會原封不動複製到九個專案。

引句:「衝突又影響決策時，照上面第 3 條去程式碼裁，再回頭修那篇筆記。」(patch 第 16 行,`AGENTS.md`;同一句在 patch 第 89 行的 `CLAUDE.md`、第 275 行的 `scripts/templates/graph-discipline.md` 重複出現)

外部查證:`CLAUDE.md:24`(引用句所在行)對照 `CLAUDE.md:28`(「3. **筆記跟程式對不上時…」實際宣告行,在引用句下方而非上方)

severity: major
blocking: yes
