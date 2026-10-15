severity: minor

五組逐一核對,修補大致做到了。G1 的條件語氣與判別邊界、G2 的範本與須知、G3 的記帳說明、G4 的邊界測試、G5 的指標,都與程式行為和範本內容對得上。我讀了 `scripts/lumos` 的 `_is_toolchain_repo`、`_vault_repo_root` 與 `--finding-kind` 驗證段,也核對了 `templates.md` 的節標題與圍欄位置。以下 7 條都是文件或計劃與修補後狀態對不齊,沒有 blocking。

---

severity: minor
blocking: 否 — 只是計劃文字落後測試,不影響程式行為與已綁定測試的結果
引句:「每一個第一行是 `LUMOS-SEAT:` 的圍欄,以及 §5、§6 兩份派工詞,都應含同一句規則原文」
問題:修補把 `t_templates_rm_literal_absolute_path` 擴成 10 份派工詞:6 份 LUMOS-SEAT,加 §5、§6、§3.1 修補鏡頭追加段、§9 跑滿回顧起草者。前置斷言是 `len(labels) == 10`。但綁這支測試的 [S9] 條款字面仍是「§5、§6 兩份」。計劃其他幾處也沒改:做法 6 刪檔紀律那條寫「加 §5、§6 兩份實作與審查派工詞」,現況表第 81 列也寫「§5、§6 兩份」。做法 9 只在實作紀錄寫「原本只列 8 份」。做法 2 還留著「圍欄內只動這三處(兩個填空、一句補充)」,但那句補充已經收回。
具體失敗情境:之後有人讀 S9 當驗收依據,會以為只要 8 份,把 §3.1 或 §9 的規則刪掉也覺得符合條款。測試會紅,條款與測試的說法卻對不上。
file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:211`
file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:155`
file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:81`
file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:135`

---

severity: minor
blocking: 否 — 文字落後,不影響行為
引句:「會印成工具鏈範圍、照它貼就是少審,所以新規則開頭寫明以被審 repo 的根為準」
問題:這是計劃〈版本錯位〉一段。r1 把那一行改成條件語氣後,它不再「照它貼就是少審」。同一份計劃的做法 10 還逐字引用舊字串「`loop next` 印了『鏡頭範圍: 工具鏈本 repo』」,但現行那一行開頭是「鏡頭範圍: 帳本所在 repo 是工具鏈本 repo」。範本與 `t_templates_toolchain_idempotency_scope` 的 ⑤ 已改成「『鏡頭範圍』那一行」。實作紀錄的 r1 段只講了做法 5、做法 2、新規則 1,沒記做法 10 這處改動。manifest 須知還寫「同計劃新規則 2」,但 manifest 那句話在計劃新規則 3,實作紀錄也寫新規則 3。
具體失敗情境:接手的人照做法 10 找「鏡頭範圍: 工具鏈本 repo」這串字,在程式輸出與範本裡都找不到,會以為範本或程式漏改。
file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:160`
file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:194`
file: `skills/lumos-design-loop/templates.md:144`

---

severity: minor
blocking: 否 — 影響的是回退步驟的完整性
引句:「拿掉上面 8 支新測試」
問題:做法 6 與〈回退〉第 3 步都算 8 支新測試。r1 又新增 3 支:`t_loop_next_lens_scope_loose_code_ids`、`t_loop_next_lens_scope_marker_odd_kinds`、`t_toolchain_lens_scope_note_pointers`。計劃正文沒更新數量,也沒列這 3 支。
具體失敗情境:
- 照回退把 `loop next` 那一行與 `lens_scope` 拿掉後,前兩支測試仍留在測試檔,會紅。
- 回退第 4 步把 bound-tests-gate 括號改回「2026-10-14 使用者確認」,`t_toolchain_lens_scope_note_pointers` 的 ①② 會紅。
- `t_toolchain_lens_scope_note_pointers` 沒綁任何驗收條款。S11 仍是 manual,只靠 r1-fix.json 的 G5 提它。
file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:235`

---

severity: minor
blocking: 否 — 違反寫法慣例,不影響行為
引句:「條件語氣是代碼審 r1 改的」
問題:CLAUDE.md〈寫筆記時〉規定「過程紀錄(第幾輪折了什麼)不寫進筆記」。修補把「代碼審 r1」寫進 Systems 節點正文:
- pitfalls-code-loop 該節寫「條件語氣是代碼審 r1 改的」。
- 每輪修補差異派工的兩條 WHY 寫「§3.1、§9 是該案代碼審 r1 補的」與「(該案代碼審 r1)」。
計劃實作紀錄可以寫過程,Systems 節點不該。
具體失敗情境:下一個沒有脈絡的 session 讀到「r1」不知道指哪一輪;而且這類字樣本來是 lint 或審查要擋的過程紀錄。
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:253`
file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:73`
file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:75`

---

severity: minor
blocking: 否 — 效力邊界問題,沒有程式後果
引句:「判別只看根目錄那一支檔、不往上找:沒有 .git 的副本、子目錄、從 repo 外跑都判成消費專案,方向是多審」
問題:這條 RULE 掛 `[依據:人]` 與 `[confirmed:2026-10-14]`,內文卻被 AI 在 2026-10-15 擴寫。新增的內容是「判別邊界」,以及「任何 repo 放一支空檔就會被判成工具鏈,屬刻意手法、範圍外」。使用者 10-14 裁的只有三類與刻意偽造不防,沒有裁「放空檔算範圍外」。CLAUDE.md 規定 RULE 效力來自近期人確認,擴寫的字句沒有確認,日期卻沿用。
具體失敗情境:空檔手法被排除出審查,依據卻掛在人裁上,之後有人引用這條 RULE 挑戰程式碼時,以為這句也是使用者裁的。
建議:把邊界說明移到 d8 決策或正文,RULE 維持人裁原文;或重新取得確認並更新 confirmed。
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:58`

---

severity: minor
blocking: 否 — 說法略過頭,補一句條件即可
引句:「記帳時整輪每一條都要標 `--finding-kind`(程式會擋缺漏)」
問題:程式只在「有給 `--finding-kind`」時才要求涵蓋全部發現(`if finding_kinds:` 之後檢查全集)。完全不給就不擋;不給時的後果是折入的發現全都要修正紀錄。所以「程式會擋缺漏」要加上「給了就必須全標」。這句出現在 Issue 與範本〈工具鏈範圍外〉,又被 `t_templates_toolchain_lens_scope` 的 ⑦b 逐句釘住。
具體失敗情境:編排者以為不標也會被擋,實際什麼都沒發生,範圍外發現被當成要補修正紀錄的程式缺陷。
file: `skills/lumos-design-loop/templates.md:493`
file: `scripts/lumos:11502-11516`

---

severity: minor
blocking: 否 — 只是一處引用編號
引句:「★工具鏈本 repo 的 manifest 併發題★(同計劃新規則 2)」
問題:這條新須知的來源在計劃新規則 3 的第二句。新規則 3 是 §3 冪等,它自己寫「照新規則 2 判範圍外」。模板指到新規則 2,實作紀錄指新規則 3,兩處不一致。這條須知與 `t_templates_toolchain_idempotency_scope` 的 ⑥ 也沒有對應的驗收條款:S10 只講冪等那一條。
具體失敗情境:這條須知只剩測試守著,條款沒寫,之後有人改它時找不到驗收依據。
file: `skills/lumos-design-loop/templates.md:144`

---

已讀,無 finding:
- **`scripts/lumos` 的 `_LENS_SCOPE_TOOLCHAIN_LINE`** 與 S1 條款、測試常數 `_LENS_SCOPE_LINE` 逐字一致。
- **判別範圍**:`_is_toolchain_repo` 用 `is_file()`,目錄與壞符號連結落 default;沒有 `.git` 時 `_vault_repo_root` 退到 `vault.parent`,也落 default,與「方向是多審」一致。
- **`t_templates_toolchain_lens_scope`**:`③b` 的「除了填空不提工具鏈」與圍欄內容對得上;DoS 那句改回原文也有逐句斷言。
- **`bound-tests-gate`** 的 WHY 括號、兩條 KEY 句尾指向 d8,以及 `每輪修補差異派工` 的 `about_code` 補 reference.md,都與 `t_toolchain_lens_scope_note_pointers` 的字串對得上。
- **`templates.md`** 的 §3.1 與 §9 圍欄位置,和測試的 `### §3.1 `、`## 9. 跑滿回顧起草` 判法對得上,刪檔規則在第 2 行。

最高等級 minor,blocking 0 條。
