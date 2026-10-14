severity: minor

整合/知識同步席報告。範圍:對照 `spec-gate-nondo` 的 `scripts/lumos`、`scripts/test_lumos.py`、圖譜與 skills。只讀,未執行任何會寫檔的指令。

**已核對,和前掃一致**
- `_door_judge` 的呼叫者只有兩處:`scripts/lumos:8659`(規格閘本身)和 `scripts/lumos:8996`(`_spec_gate_push_stale`)。
- `_h2_section_lines` 的呼叫者有三處:`_rollback_section_chars`、`_door_exclusions`、`_door_judge` 取得跳過區間的新路徑。加選配參數、預設不變,不會動到前兩處。
- `t_door_rule_version_pin` 是唯一釘死 `door_rule=1 ` 與指紋值的測試(`scripts/test_lumos.py:59431`)。
- 其他讀到 `door_rule` 的測試(`scripts/test_lumos.py:59422`、`:59424`)只比對「等於程式常數」,不用改。
- `Systems/規格閘.md` 沒有 ★INVARIANT★ 合約行,所以沒有合約行跟著錯。
- skills 目錄沒有「掃全文」的句子。`skills/lumos-project-notes/commands/05-設計審查迴圈.md:12` 只提 `--door-rule`,不用改。
- 雙向門放行計劃裡沒有「不跳過任何節」這類裁定。只有「掃描範圍=計劃全文,只跳過實務隱患節內合格已排除行」這一句(`Projects/雙向門放行_計劃.md:183`),見 F1。

---

severity: minor
blocking: 否 — 只是文件漏改。程式行為、測試、推送閘都不受影響。
引句:「[[Systems/規格閘]] 兩行要改:講門怎麼判、「掃全文可見行,只跳過實務隱患節內合格的已排除行」那行補」
問題:計劃說 `Systems/規格閘` 只要改兩行,實際講「只跳過實務隱患節內合格已排除行」的句子不只這兩行。
- `Systems/規格閘.md:65` 的「硬訊號 ①」寫「只跳過實務隱患節內合格的已排除行;引用塊、圍欄、行內程式碼不算」。
- `Systems/規格閘.md:31` 是計劃改的那一行。
- `Systems/規格閘.md:38` 是計劃改的版本號那一行。
- `Projects/雙向門放行_計劃.md:43` 寫「關鍵字表命中(掃全文可見行,跳過實務隱患節內合格已排除行)」。
- `Projects/雙向門放行_計劃.md:48` 寫「`_DOOR_RULE_VERSION=1`」。
- `Projects/雙向門放行_計劃.md:183` 是「掃描範圍=計劃全文」的詳細裁定,內容很長。
- `scripts/lumos:7974` 的 `_door_judge` docstring 同一句。
- `scripts/lumos:8003` 的 `_door_rule_fingerprint` docstring 列出指紋輸入。
具體失敗情境:改完只動兩行,下一個 session 讀 `Systems/規格閘.md:65` 會以為不做節仍照掃,讀 `scripts/lumos:7974` 的 docstring 也一樣。計劃裡的「改 Systems 兩行」驗收沒有機械檢查,doctor 查不出這種內部矛盾。
建議:改成「`Systems/規格閘` 內凡寫掃描範圍或版本號的句子」,並加一條 grep 當驗收,例如搜「只跳過實務隱患節」要零命中舊句。`雙向門放行_計劃` 是歷史計劃,可在 `:183` 補一句「2026-10-14 起另跳過 `## 不做` 節,見某計劃」,而不是留著矛盾。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:65` ``

---

severity: minor
blocking: 否 — 只影響健檢數字的口徑,不影響放行。
引句:「所以放寬之後舊留痕照舊成立,不用重跑。」
問題:計劃只講「推送前不讀版本號,舊留痕不用重跑」,沒處理版本 +1 對撤除條件計數的連帶影響。
- `Projects/雙向門放行_計劃.md:220` 裁定「門判定規則改版 → 從零重數 30 份,舊帳留著不重分類」。
- 程式裡沒有任何地方讀留痕的 `door_rule`。我 grep `scripts/lumos` 只看到寫入(`:8135`)和印出(`:3229`、`:53706`)。
- `Systems/規格閘.md:37` 的 doctor S14 撤除條件②「前 30 份 major 以上 ≥3 份退回」也沒有按版本篩選。
具體失敗情境:版本 1 改 2 之後,舊裁定要求重數,但 doctor 不會自己切分。「前 30 份」會混著 v1 與 v2 的留痕,放寬後變多的逃逸可能被舊樣本稀釋,或被誤算成 v1 的帳。計劃的 `REVISIT:2026-12-15` 要查逃逸帳,也沒說樣本怎麼切。
建議:在計劃裡明講兩件事。一是這次放寬要不要視為「改版重數」。二是 S14 要不要補按 `door_rule` 篩,或在 REVISIT 那條寫明人工只數 `door_rule=2` 的留痕。

---

severity: minor
blocking: 否 — 屬於測試設計沒寫清楚,實作時可補。
引句:「把不做節的標題規則換掉時,門判定規則的輸入指紋應跟著變(動態比較,不是只釘一個值)。」
問題:S6 要動態驗證「換掉標題規則,指紋跟著變」,但現有 `--door-rule` 和 `t_door_rule_version_pin` 都是起子行程跑 CLI(`run(mkvault(), "spec-gate", "--door-rule")`),在行程外沒法換掉模組全域的 `_NOGO_H2_RE`。
同時,「遇三級標題也停」是函式參數,不是資料,放不進 `_door_rule_fingerprint` 現有的 `parts` 清單(那裡只收 pattern 字串和 dict)。
具體失敗情境:實作者很可能退回「釘一個固定值」,正是計劃想避免的做法。又或者只把 `_NOGO_H2_RE.pattern` 放進指紋,卻漏掉「停在三級標題」這個選項。之後有人把那個選項改成不停,指紋不變、版本不 bump、測試不紅,等於 S7 的守衛會悄悄失效。
建議:計劃寫明 S6 用 in-process 方式(例如 import `scripts/lumos` 後 monkeypatch)。再寫明三級標題行為怎麼進指紋,例如把它做成具名常數,指紋 `parts` 加上該常數的值。

---

severity: minor
blocking: 否 — 計劃有承認這個取捨,只是對照結論說得太滿。
引句:「所以不做節的詞在那邊照算沒有實際成本。」
問題:`lumos pitfalls <計劃> --check`(`_pitfall_strip_spec`,`scripts/lumos:44108`)的剝節黑名單是 `("方案評比", "canary 相容性", "誠實天花板", "審計修正紀錄")`(`scripts/lumos:27898`),不含「不做」。
具體失敗情境:一份計劃被規格閘判風險低、直接實作,但設計審 skill 第 24 行要求的 `pitfalls --check` 仍會因「## 不做」裡的「退款」反問金流。使用者看到兩支工具對同一份計劃的金流判斷不一致,會懷疑閘壞了。計劃說這是「要求回答、不影響門」的成本,但沒在 skill 或規格閘節點補一句說明這個差異。
建議:在 `Systems/規格閘` 或 `skills/lumos-design-loop/SKILL.md:24` 補一句「pitfalls --check 仍掃不做節,不影響判門」。

---

**無 finding 的部分**
- 「`_door_judge` 只有兩個呼叫者」的說法成立。
- `_h2_section_lines` 加選配參數不破壞回退節與實務隱患節。
- 不做節的 `[[連結]]` 仍算訊號 ②,這和 `_door_linked_signals` 的實作一致。
- `lumos doctor` 只在 `scripts/lumos:3229` 印版本號,沒有版本比對邏輯。

**總結**:最高等級 minor,共 4 條 finding,blocking 0 條。沒找到會讓閘失效的洞。要補的是文件同步的涵蓋面(F1)和版本號重數的口徑(F2)。
