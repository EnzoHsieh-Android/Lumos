# r7-intake.md 更正(2026-11-07)

r7-intake.md〈收貨三道〉寫通才 F3 那句引句「`grep '^+def t_r5imp_fifo_guard():' r7-repair.patch` 命中 1 處,HIT」——**寫錯了**:編排者在看到指令輸出之前就寫下結論,實際輸出是 0。

實際情形:那一行在 r7-repair.patch 第 972 行是**上下文行**(開頭是空白,不是 `+`),內容為 `def t_r5imp_fifo_guard():`。通才席引句多抄了一個 `+`,把上下文行說成新增行。

判讀不變:那一行確實在凍結材料裡(上下文行),通才 F3 指的是「新增的 `t_r6sh_launcher_relative` 結尾和這一行之間只隔一個空行」,這個觀察本身成立;F3 照原處置放行(推送前跑專案 ruff 閘確認)。重現表該列應讀作:`grep -n 'def t_r5imp_fifo_guard' r7-repair.patch` → 第 972 行(上下文行),HIT。
