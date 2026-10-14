severity: minor

審的是掛鉤修補與主程式修補。重點項逐項看過,沒有引入第二種做法或跨層直呼。下面三條是同一族習慣沒對齊的小處,都不擋。

先交代重點項的結論:

- **`_CodeloopKg`**:這不是 `scripts/lumos` 裡第一個這種類別。同樣「帶狀態加方法」的寫法已有多個,例如 `_BtProcs`(50011 行)、`_DriftNames`(38483 行)、`_DriftM1Run`(41555 行)。修補前的收尾是巢狀 `_fin` 加 `seen` 字典,原地只有一份;改成類別是換掉它,不是新增並存。
  - 判定函式裡已沒有殘留的 `blocks.append` 或 `seen[...]`,所有擋下都走 `kg.hit` 和 `kg.fin`。
  - `_codeloop_pitfalls_tier` 是把原內嵌段落原樣抽出的。
- **兩份對照表加漂移測試**:專案既有同一種做法,有先例。例如 `scripts/lumos:48192` 的 hook 信任邊界複本、`scripts/test_lumos.py:17472` 的逐字相同守衛、`:3994` 的 post-commit 對 pre-commit。這次 `t_prepush_cl_reason_table_matches_lumos` 比對表內容、通用句,以及 `reason_kind` 的產出集合,比既有先例多驗一層。對齊。
- **`--keep-going` 版本探測**:改成讀 `$GRAPHCTL` 找字樣,跟 `pre-push:769`、`:775`、`:785` 探 `--shard`、`--suite`、`--graph` 同型。lumos 原始碼裡確實有這個字面(53804 行),探得到。對齊,而且比原本執行 `--help` 更一致。
- **`cmd_push_summary` 的 repo 根**:改用 `_note_audit_root`,是 `push-range` 等多處(35916、47576 等)共用的找法。對齊。
- **`pp_keep_log`**:刻意在 `$_PP_TMP` 外面 `mktemp`,跟 `pre-push:155` 的「別另外 mktemp」看似相反。但那條的理由是讓陷阱收得到,這裡是要讓檔案活過陷阱,註解有講明。樣板寫法跟 `impact_once` 一致。對齊。
- **`run_group` 的 TERM 陷阱**:它只在 `( run_group ... ) &` 的子殼裡設,不會蓋掉主掛鉤的 TERM 陷阱。跟 `_pp_kill_jobs`(`pre-push:302`)的差異見第一條。

severity: minor
blocking: 否 — 只是同一個「收掉子行程」的動作出現第二種寫法,效果相同,不影響行為
引句:「不收的話被砍或按 Ctrl-C 之後各片變孤兒繼續跑」
對照:file: `scripts/hooks/pre-push:302`(`_pp_kill_jobs`,供 `:304-305` 的 INT/TERM 陷阱用)
判定理由:`run_group` 裡新寫了一條內嵌的 `trap 'kill ${_pids...}' TERM`,而掛鉤已有 `_pp_kill_jobs` 這個收子行程的 helper。`( run_group ... )` 是子殼,`jobs -p` 在子殼裡看得到它自己起的各片,所以 `trap '_pp_kill_jobs; exit 143' TERM` 就夠,不必另寫一套 `_pids` 展開。這是第二種寫法,但範圍小、語意等價,不到 major。

severity: minor
blocking: 否 — 多出的 `summary` 欄位在倉內沒有讀它的地方,只是讓 lumos 側那份表有存在理由,不影響擋不擋
引句:「掛鉤要能配舊版 lumos 跑,不向這裡要表」
對照:file: `scripts/lumos:51924`(`_kinds` 只取 `reason_kind`)、`scripts/hooks/pre-push:586-590`(掛鉤只讀 `LUMOS-BLOCKS:` 的種類字串,自己用 `pp_cl_reason` 查句子)
判定理由:這份先例做法本身對齊。但 `_CODELOOP_BLOCK_KIND_REASONS` 在 lumos 側唯一的用途,是填進 JSON blocks 的 `summary`,而 `summary` 沒有任何消費者。掛鉤依設計不讀它,印人看的訊息走 `_cl_say_block` 也不用它。既有先例(hook 信任邊界等)的兩份複本,兩邊都各自在用。這裡 lumos 那份是為了給守衛測試一個比對對象而存在。建議要嘛有程式消費 `summary`,要嘛這份表只留一份(在掛鉤),守衛改去比對判定函式產出的種類。

severity: minor
blocking: 否 — 同族寫法只改了一處,另一處的差別只是開檔失敗時多印一行雜訊,判斷與擋下不受影響
引句:「重導向包成一組:2>/dev/null 寫在 >> 後面時,開檔失敗的訊息在 stderr 被導走之前就印出來了」
對照:file: `scripts/hooks/pre-push:169`(`git diff ... >> "$_f" 2>/dev/null || _ok=0`,同樣的「`>>` 之後才導走 stderr」寫法,未同步)
判定理由:修補在 `pp_record_block` 改成大括號整組導向,並把這種寫法當成「暫存檔寫不進去不印雜訊」的慣例,還在 `spec-gate` 的 `tee` 那行引用。但同檔 `pp_touched_file` 的追加寫入仍是舊寫法。同一個缺陷形狀在同一支檔裡出現兩種寫法。這一處失敗時有 `_ok=0` 接住,後果比 `pp_record_block` 輕,所以只列 minor。

共 3 條不對齊,全部 minor,major 0 條。
