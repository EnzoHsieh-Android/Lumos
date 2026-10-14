severity: minor

整體判斷:這批文件修補和程式、測試、`.lumos/lint-waivers.json` 的紀錄大致對得上,沒有破壞合約行。下面 4 條都是 minor,沒有一條擋推送。

我做過的核對:
- 新舊版本的複雜度數字用 ruff 重算過:`_codeloop_guard_verdict` 是 35→32,`cmd_code_loop` 是 53→26。計劃那段和兩筆 C901 lint-waive 的理由一致,`code-loop check --diff` 也跑過、新增告警閘顯示沒有新增的告警。
- lint-waive 的紀錄在 `.lumos/lint-waivers.json`,不在你寫的 `governance/lint-waivers.jsonl`,後者不存在。
- 五篇改到的節點 `lumos lint` 全部 0 問題。
- 新的 PITFALL 行格式齊全:有 `[出處:]`、`[根因:]`,另有兩個 `[test:]`。
- `anchor-baseline.json` 記的兩個雜湊值,跟 `a32615f5` 的 `scripts/test_lumos.py`、`scripts/hooks/pre-push` 實際的 sha256 相符。
- 掛鉤、`scripts/lumos`、06 手冊、`INDEX.md`、`SKILL.md` 裡都沒有預演指令(第二批)的句子,第二批只出現在計劃筆記的設計段。
- 驗收條款 S1–S4、S6、S7、S10、S12–S15 綁的測試都存在,且大致驗到條款。

severity: minor
blocking: 否 — 只是筆記裡一句事實說錯,沒有任何行為或守衛因它出錯
引句:「而 git 允許 ref 名帶它們,那一筆會被切成兩段丟掉」
問題:這句說 U+2028、U+0085、跳頁這類字元 git 都允許出現在 ref 名裡,但我用 `git check-ref-format` 試過:跳頁(0x0c)和 0x1c 到 0x1e 都被拒絕,只有 U+2028、U+0085 能過。同一份計劃〈做法〉1 也寫「ref 名照 git 規則不含控制字元」,兩處互相矛盾。測試 `t_push_summary_anchor_note_and_separators` 裡的「跳頁」那一組,測的是 git 根本推不出來的輸入。
具體失敗情境:之後有人讀到 WHY,以為跳頁必須防,或照這條去擴充「git 允許的字元」清單,會被錯誤前提帶偏。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:128` ``,``file: `scripts/test_lumos.py:64658` ``

severity: minor
blocking: 否 — 行為測試仍然抓得到實際的壞回傳,只是條款文字和守衛寬度對不上
引句:「(不帶旗標時 `hit` 回的就是 `fin(v)`)」
問題:S13 與計劃〈做法〉5 仍寫「守衛測試掃這支函式的原始碼,不准有不經收尾函式的回傳」。但 `t_code_loop_keep_going_pass_sites_keep_blocks` 的原始碼掃描現在放行任何 `return <變數>`,只要該變數是從 `.hit(...)` 指派來的。帶旗標時 `hit` 會回 `None`。有人把 `if _stop: return _stop` 改成無條件 `return _stop`,原始碼掃描照綠,要靠逐站點的行為測試才抓得到。計劃條款文字沒跟著放寬,守衛也沒檢查「回傳前有判非空」。
具體失敗情境:新增一道判定時寫成 `return kg.hit(...)`,掃描會擋它;換成先指派給變數再 `return`,掃描放行,帶旗標時整個函式回 `None`,下游的 `.get` 會崩。
佐證:``file: `scripts/test_lumos.py:65088` ``(約此處,`via_hit` 那段),``file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:53` ``

severity: minor
blocking: 否 — 只是條款沒綁測試,行為本身在 `t_prepush_test_logs_inside_tmp` 有被驗
引句:「兩個 log 都放在 `$_PP_TMP` 裡,正常結束、擋下、中斷時都由 `EXIT` 陷阱一起清。」
問題:〈做法〉3 這個行為改動(log 搬進暫存目錄、紅時先複製到外面再印路徑)沒有任何驗收條款,也沒有 `[test:]`。它只在 `bound-tests-gate.md` 的 PITFALL 綁了 `t_prepush_test_logs_inside_tmp`。S10 只寫到「不留 ppid=1 的孤兒、TMPDIR 底下不留東西」,沒涵蓋「紅時印出的路徑在掛鉤結束後還在」。這是這輪新增的使用者可見行為,卻不在計劃的條款清單裡。
具體失敗情境:之後改計劃或撤除收集模式時,照條款清單對測試,會漏掉這支測試和這條行為。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:44` ``,``file: `scripts/test_lumos.py:64880` ``(約此處,`t_prepush_test_logs_inside_tmp`)

severity: minor
blocking: 否 — 表格漂移另有行為測試補位,只是文件的保證說得比測試實際守的寬
引句:「判定函式會產生的每個 `reason_kind` 都要在表上」
問題:這句保證靠 `t_prepush_cl_reason_table_matches_lumos` 的第③項,但它用正規式只抓原始碼裡字面寫出的 `reason_kind="x"` 或 `"reason_kind": "x"`。若某個種類之後經由變數或組字串產生,抓不到,測試照綠。另外 `--json` 的 `blocks[].summary` 欄位寫進了 `pitfalls-code-loop.md` 的輸出契約,也寫了「跟掛鉤的對照表逐字一致」,但計劃〈做法〉5 沒提這個欄位,沒有任何測試讀它,也沒有程式消費它。
具體失敗情境:新增一種 reason_kind 用變數傳入,沒補掛鉤對照表,守衛不紅,彙總退成通用句。
佐證:``file: `scripts/test_lumos.py:65140` ``(約此處,第③項),``file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:232` ``

最高等級 minor,共 4 條,blocking 0 條。
