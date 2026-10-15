severity: minor

整體做法大致沿用專案既有的東西:判別函式、`loop next` 的附加欄位、以及逐檔列舉的文件同步測試。沒有跨層直呼,也沒有自造已有的工具函式。有三處偏離既有做法,都不到 major。

**Finding 1:§7.8 用「同一節兩份圍欄」,範本裡沒有先例**
severity: minor
blocking: 否 — 屬範本形式選擇,spec 在〈承認的限制〉已誠實寫出「靠編排者選派工詞」並附回頭條件。
引句:「再附一個獨立圍欄:同樣的開頭與 LUMOS-SEAT 行、同樣的席名」
對照:
- file: `skills/lumos-design-loop/templates.md:412-448`。§7.8 目前只有一個圍欄,整份 templates.md 沒有「依情境選一份圍欄」的先例,也沒有「改用另一份」「二選一」這類句型。
- 既有的情境差異靠兩種寫法。一是圍欄內的 placeholder,由編排者代入,例如 §7.8 的 `這個技術棧慣例 skill 裡的資安條款:{…其他棧沒有就寫「無」}`。二是圍欄外加一句括號,例如 spec 自己的〈做法〉10 對 §3 就用括號。
- file: `skills/lumos-code-loop/SKILL.md:16`。「工具鏈本 repo 的五次修復試行…其他專案照原流程」也是句子級分流,不是複製一份範本。

判定理由:
- 複製整個圍欄,會讓攻擊路徑四件、嚴重度錨、席名規則這些共用內容有兩份,日後容易單邊漂移。
- spec 用 `t_templates_toolchain_lens_scope` 守衛,但沒有守兩份共用段落一致。
- 同一份 spec 內,§3 用括號、§7.8 用雙圍欄,做法也不一致。
- 建議二選一:改成單一圍欄加「範圍」placeholder,例如 `{範圍:消費專案=六類;工具鏈本 repo=三類+範圍外清單}`;或保留雙圍欄,但加測試斷言兩份的共用段(四件、嚴重度錨、席名)逐字相同。

**Finding 2:鏡頭範圍靠編排者手動選,沒用既有的派工時機械附段掛點**
severity: minor
blocking: 否 — spec 已把它列為已知取捨,REVISIT:2026-12-14 寫了「議把範圍做成派工鏡頭自動附」。
引句:「理由:派工範本是整台機器共用的 skill,編排者在消費專案也讀得到工具鏈那段」
對照:
- file: `scripts/lumos:25448-25456`。`_vendored_skip` 已經用 `_is_toolchain_repo` 分流,供推送前分級與代碼審角色鏡頭共用。
- file: `scripts/lumos:46852`、`scripts/lumos:50912`。這兩處呼叫它的路徑,就是派工鏡頭自動附段的路徑。
- file: `skills/lumos-design-loop/templates.md:124`。LUMOS-LENS 說明行是掛鉤機械附段的先例。
- 派工鏡頭掛鉤與 `_is_toolchain_repo` 本來就接在一起,spec 卻另開 `loop next` 印一行,再靠編排者選圍欄。

判定理由:
- 這是「用既有掛點」和「新增提示行」的取捨,不是自造第二套判別,判別仍是同一個 `_is_toolchain_repo`。
- 資安席一步看不出用了哪份派工詞(spec 自承),所以機械附段才是更穩的位置。
- spec 已有回頭條件,列 minor 提醒即可。

**Finding 3:`loop next` 新增程式缺 fail-open 包裝,根路徑算式再多一份複本**
severity: minor
blocking: 否 — 屬實作細節,可在實作時順手補。
引句:「root 取法照 `loop next` 既有那支:`Path(repo).resolve() if repo else _vault_repo_root(env)`」
對照:
- file: `scripts/lumos:16153` 起的 `cmd_loop_next`。同一函式內該算式已出現兩處,分別在 reviewed_spec 與 gate-pending 補指令。
- file: `scripts/lumos:1074`。這一處同樣有該算式。
- 同函式內所有「只附加」的提示都包 `try/except Exception`,例如 fix_check、cap_hint、related_nodes,並註明 fail-open,不改 rc 與既有輸出。
- spec 的〈實務隱患〉只寫「多一次 `is_file()`」,沒提 `_vault_repo_root` 可能丟例外,也沒說 `lens_scope` 欄位要放進 `emit` 的同一個 fail-open 區段。

判定理由:
- 沿用算式本身符合既有慣例,spec 在這點正確。
- 若新程式不包 try,vault 找不到 repo 根時,附加提示會變成讓 `loop next` 整個崩潰。
- 建議在實作說明裡寫明:包 try、失敗時 `lens_scope` 取 `default`、不印那一行。

**已讀,無 finding 的項目**
- `_is_toolchain_repo` 沿用:已讀,無 finding。
  - file: `scripts/lumos:25437`。spec 寫的「現有 6 處呼叫」屬實,我數到 6 個呼叫點(25451、26178、33030、33036、33457、33591)。
  - 判別鍵與 `_self_repo_origin` 同一個,沒有第二種判法。
- 「code- 開頭」判法:已讀,無 finding。
  - file: `scripts/lumos:14035-14042`(`_roster_kind`)。
  - spec 寫「跟修正關卡提醒同口徑」,即 `str(loop_id).startswith("code-")`,與 `_roster_kind` 對 `code-` 的判法等價。
  - 沒連字號的舊 `code…` 編號不印,與 `_roster_kind` 回 None 的區分一致。
- `lens_scope` 欄位命名:已讀,無 finding。
  - 既有 JSON 欄位是 snake_case(`scope_cap`、`cluster_hint`、`fix_check`、`roster_note`),`lens_scope` 一致。
  - 文字行用中文「鏡頭範圍:」,與「圖譜:」「帳上…」的縮排與中文鍵風格同類。
- 規則落點用 RULE 行加 `decision-add`:已讀,無 finding。
  - `Systems/*.md` 內有 `RULE:… [依據:人] [since:] [retire:人裁] [until:] [confirmed:]` 的格式先例,見 `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:46` 與 `codex-harness.md:198`。
  - 兩條 RULE 欄位齊全且帶 `[until:]`,符合 CLAUDE.md 的 RULE 寫法。
- 測試逐檔列舉:已讀,無 finding。
  - file: `scripts/test_lumos.py:57812-57844`。`_SEC_SEAT_DOC_FILES` 加 `t_security_seat_doc_sync` 就是該照的先例,含 `_SrcOnly` 來源專屬標示。
  - spec 的 `t_toolchain_lens_scope_doc_sync` 三份檔案,與該常數中已有的三份重疊,應當複用該常數並確保提醒 `_SrcOnly` 守衛。
  - `t_templates_toolchain_*` 與 `t_templates_security_seat_section`(`scripts/test_lumos.py:57847`)形狀一致。

最高等級 minor,blocking 0 條。
