severity: major

## F1 新加的 REVISIT 行把兩件不相干的事黏成一句,doctor 到期唸的時候會被截斷、遺失後半內容

severity: major
blocking: yes

觀測到什麼:patch 把 `Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md` 裡原本掛在「第一階段動到的檔」段落尾巴的一句 FYI(同一個提交還改了回放全量門檻),搬去跟新寫的 `REVISIT:2026-11-21` 黏在同一行、同一句。

引句:「REVISIT:2026-11-21 看這半年有沒有第三次「加字串才收斂」,有就改成注入式單一來源,不要再加清單。另外併在同一個提交的還有回放全量門檻 60→180 秒(`governance/autonomous_loop/replay_weekly.py` + `scripts/test_autonomous_loop.py` + `Systems/autonomous-iteration-loop.md`)。」

CLAUDE.md 鐵則四自己定的格式是「帶日期的寫成獨立一行 `REVISIT:YYYY-MM-DD` 一句要做什麼(緊鄰原句;doctor 到期會唸)」——這行違反了「一句」:前半是真正的回頭條件(加字串才收斂要不要改形狀),後半「另外併在同一個提交的還有回放全量門檻…」是跟這個 REVISIT 觸發條件完全無關的舊 FYI,只是被誤搬過來黏在同一行。

怎麼重現(輸入→錯誤輸出):`scripts/lumos` 的 Check E5(`scripts/lumos:1906-1931`)解析 REVISIT 行時,是整行 partition 一次空白取 `_datev`,**剩下整段(含後面那句 FYI)全部進 `_sumv`**,顯示時再用 `_esc_clean(sm, 60)` 截到 60 字。實際跑一遍解析與截斷:

```
$ python3 - <<'EOF'
rest = 'REVISIT:2026-11-21 看這半年有沒有第三次「加字串才收斂」,有就改成注入式單一來源,不要再加清單。另外併在同一個提交的還有回放全量門檻 60→180 秒(...)。'[len("REVISIT:"):]
datev, _, sumv = rest.partition(" ")
print(sumv.strip()[:60])
EOF
看這半年有沒有第三次「加字串才收斂」,有就改成注入式單一來源,不要再加清單。另外併在同一個提交的還有回放全量門檻 60→
```

到 2026-11-21 這行到期時,`lumos doctor` 的 [E5] 段會印出這個被硬切在「回放全量門檻 60→」處的訊息(`_esc_clean(sm, 60)`,`scripts/lumos:1917`),後面「180 秒」和三個檔案路徑(`governance/autonomous_loop/replay_weekly.py` 等)完全被吃掉、永遠不會出現在提醒裡。

為什麼是 bug 不是風格:這不是排版偏好,是這篇筆記自己(同一份 CLAUDE.md/範本)訂的機械規則被自己違反,而且有具體、可重現的壞後果——doctor 的自動到期提醒(這條紀律鐵則設計出來就是為了「回頭條件要接電」)屆時會印出一句斷在奇怪位置、資訊被砍半的訊息,讀的人看不出後半在講什麼,等於這條回頭條件真正到期時反而傳不到位。file: `scripts/lumos:1906-1931`(Check E5 解析與截斷邏輯)、`docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md:74`(黏在一起的那一行)。

修法建議(不佔篇幅展開,僅供參考):REVISIT 行只留前半那句真正的回頭條件,「另外併在同一個提交的還有回放全量門檻…」那句放回上一段(或獨立成一段散文),不要接在 REVISIT: 後面。

---

## F2 SYMBOL_NAMES / SYMBOL_RE / 新測試斷言:驗過的路徑,沒發現問題

severity: clean
blocking: no

以下路徑實際驗過,均正常,不構成發現:

- `SYMBOL_NAMES` 新增 `WHY/RULE/PITFALL/FACT` 與既有 11 個值之間逐一比對前綴關係,程式化檢查沒有任一個是另一個的前綴(`sorted(..., key=len, reverse=True)` 组出的交替式正則不會有互相吃掉的問題)。
- `_search_region`(`scripts/lumos:2759-2773`)只在 `lineno <= fm_end`(frontmatter/summary 區塊)內才用 `SYMBOL_RE` 分類,body 正文一律回傳 `"body"`;搜過全庫 `docs/lumos-toolchain-knowledge`,沒有既有筆記的 frontmatter summary 裡本來就有正文以 `why:`/`rule:`/`pitfall:`/`fact:`(大小寫皆試)開頭而被新規則誤判的情形。
- 新測試斷言「② 詞彙表含範本新定的四個分類前綴」(`scripts/test_lumos.py`)實測翻紅釘有效:在臨時 worktree 把 `SYMBOL_NAMES` 裡的 `FACT` 拿掉,`t_symbol_vocab_single_source_and_reach` 立刻由綠轉紅(`9 passed, 1 failed`),清 `__pycache__` 後重跑結果一致,不是假斷言。
- 兩支漂移守衛(`_ENTRY_POINT_FILES` 新增 `開發工作流總覽.md`、`_OLD_POSITION_PHRASES` 新增「先查圖譜」「第一步敲 lumos」)目前掃描的 8 個入口檔逐一 grep 過這兩個新片語與既有三句,均為 0 命中,沒有正當內容被誤判成舊定位殘留;`python3 scripts/test_lumos.py -k entry_points` 8 條全線。
- `docs/lumos-toolchain-knowledge/Systems/codex-harness.md` 新加的 `FACT:` 行符合自己定的規範——標了 `[2026-09-21 以程式碼為準]`,結尾附了可重跑指令 `grep -n 'RULE_HEAD\|RULE_END' scripts/scenario_probe.py`,實跑確實有輸出(`RULE_HEAD = "### 怎麼用"`、`RULE_END = "### 寫筆記時"`);內容本身核對過 `scripts/scenario_probe.py:113-122`(`strip_lumos_first_rule` 找不到邊界時 `make_sandbox` 會 `raise RuntimeError(...停手)`,不是靜默略過),與 `scripts/templates/graph-discipline.md` 的實際標題(`### 怎麼用（順序照這個走）`、`### 寫筆記時：先分「程式碼推不推得出來」`)一致。`lumos lint` 對該篇回 0 問題。
- `ARCHITECTURE.md`/entry hook 的收尾措辭改動("先查圖譜"→"去查圖譜補脈絡"、"提醒「第一個動作先查圖譜」"→"提醒「先讀程式碼、圖譜補脈絡」")核對過 `scripts/hooks/claude/lumos-entry-hook.py:284-289` 實際印出的訊息與 `scripts/scenario_probe.py` 量測的內容(是不是有敲 lumos 指令),語意一致,沒有把原本正確的敘述改錯。
- CLAUDE.md/AGENTS.md/範本三處把「照上面第 3 條」改成「照下一條的辦法」:核對範本結構,該段落確實位於「2.」項目內、緊接在「3. 筆記跟程式對不上時…」之前,原文說「上面」方向錯了,改成「下一條」後方向正確。
- `python3 scripts/lumos doctor --ci` 全庫 0 issues,rc=0;`python3 scripts/test_lumos.py -k symbol` `-k entry_points` `-k absence_claim` 均全綠。

全檔級 severity 取最高:major(F1)。
