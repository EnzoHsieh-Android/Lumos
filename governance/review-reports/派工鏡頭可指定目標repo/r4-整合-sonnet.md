severity: major

我讀了計劃全文、這輪 diff 和鏡頭附文,並用 grep 對照 lens-repo 的手冊、筆記與程式。計劃〈做法〉第 11 條要改的手冊與筆記,我用 grep 確認過。SKILL.md:26、design-loop 的 reference.md:513、templates.md 的 §1(第 40 行)和 §7.6(第 335 行)、project-notes 的 reference.md:83、05 指令表第 31 行、`design-loop.md:52`、`codex-harness.md:42`、`dispatch-lens-hook.py` 檔頭都列到了,沒有漏列的使用者手冊。`docs/command-reference.md` 的 seat-check、quote-check 也沒收,所以 spec-freeze 不進去不算漏。`lumos lint` 對這份計劃是 0 問題。我沒建實驗檔,scratchpad 沒有要刪的東西。

severity: major
blocking: 是 — 計劃的行為違反一筆仍有效的決策,而新決策 d1 沒有寫翻案
引句:「只記這個寫法的結果,不記注入次數」
問題:計劃第 8 條要在每次提交寫法成功時記一筆 ok 事件,note 字首是 `spec_commit`。這等於每次注入都記一筆,RETIRE-IF 和 REVISIT 也是靠數這個字首判斷。但 `Projects/派工鏡頭注入_計劃` 的 d1(`valid: true`)明寫「不擋不驗不記不量」。`_hookevent.py` 檔頭也寫著「不記注入 N 次……這條分界不要順手加回去」。計劃只在做法裡說「有限鬆綁」,有三處沒補:
- 新計劃的 d1 的 context、alternatives_considered、trade_offs 都沒提這項翻案。
- 注入計劃的 d1 沒標部分推翻,第 11 條也沒要求改 `_hookevent.py` 的檔頭。
- 前例做法不同:`Claude-mod第二批_計劃.md` 的 d2 寫明「推翻派工鏡頭注入計劃開案決策裡的不驗」,並有 `valid` 和 `superseded_by` 欄位。
具體失敗情境:下一個 session 讀到注入計劃 d1 和 `_hookevent.py` 檔頭,看到掛鉤在記注入次數,會照「程式違反有結構的決策」把這筆記帳當成要修的程式問題,或者乾脆拔掉。
佐證:file: `scripts/hooks/claude/_hookevent.py:26`、file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭注入_計劃.md:35`、file: `docs/lumos-toolchain-knowledge/Projects/Claude-mod第二批_計劃.md:19`

severity: major
blocking: 是 — 設計審派工詞新增作者可控的自由文字出口,違反派工鏡頭的零自由文字原則
引句:「只在那個提交裡:列名並標」
問題:計劃第 6 條要把計劃連結的節點名列進派工詞,其中「只在提交裡有」和「兩邊都沒有」兩種都沒經過存在性驗證,第二種更直接是錯字連結。現行 `cmd_dispatch_lens_spec` 只列 `is_file()` 為真的節點(`scripts/lumos:49051`),所以印出來的名字一定是會談目錄裡真實存在的檔。連結的抓法是 `\[\[((?:Systems|Issues)/[^\]|#]+)`,我實測這個字元類別會吃換行、方向覆寫字元和任意長度。`Systems/派工鏡頭.md:15` 的 WHY 寫「設計審從分支工作樹讀,印自由文字等於讓分支作者把話塞進審查員的派工詞」。`hook信任邊界` 也說派工鏡頭定了零自由文字的規矩。計劃對這兩種名字沒寫長度上限、字元白名單或單行化,S7 只驗標籤字樣。
具體失敗情境:被審的計劃寫 `[[Systems/x` 後面接換行加一段偽指令,再接 `]]`。spec-freeze 凍結後,派工詞尾端會逐字印出這段文字,雖然在「機器附加的參考資料」框內,但已是作者可控的多行自由文字。現況下這種連結因為不是真實檔案,不會被印。
佐證:file: `scripts/lumos:49051`、file: `docs/lumos-toolchain-knowledge/Systems/派工鏡頭.md:15`

severity: minor
blocking: 否 — 屬計劃內部矛盾,多數 repo 只有一個 vault 時不會觸發
引句:「連結節點、落點、目標架構段都到計劃所在的那個 vault 找」
問題:第 2 條說目標架構段也走計劃路徑的 slug。但第 4 條寫「宣告與節點照現在從會談 repo 的 HEAD 讀」,而現行 `_arch_target_vault_rel` 取排序第一個 vault,註解寫「同設計審鏡頭」。`arch_targets` 宣告在 `.lumos/config.json`,節點名沒帶 vault。S5 只驗連結和落點,S8 只驗單一 vault,沒有一條驗兩個 vault 時的目標架構段。
具體失敗情境:repo 有 `a-knowledge` 和 `b-knowledge`,計劃在 b。若照第 2 條實作,節點到 b 找而宣告指向 a,輸出「宣告的節點讀不到規則」。若照第 4 條實作,第 2 條的承諾就是假的。
佐證:file: `scripts/lumos:43539`、file: `scripts/lumos:43498`

severity: minor
blocking: 否 — 守衛測試會當場抓到,屬計劃漏寫
引句:「choices 有漂移守衛」
問題:第 11 條說新子命令要改「指令總數」,但現在沒有任何對外文件寫死頂層命令數。`t_docs_command_count` 掃不到任何文件,`t_docs_dont_hardcode_command_count` 反而禁止寫。真正會紅的守衛是 `t_every_subcommand_has_when`,它要求新子命令的 `--help` 有「什麼時候用:」,計劃沒提。`spec-freeze` 還要在 `scripts/lumos:52292` 附近的說明對照裡補一筆。
具體失敗情境:實作者照計劃去找要更新的總數找不到,然後被 `t_every_subcommand_has_when` 紅燈擋下。
佐證:file: `scripts/test_lumos.py:8893`、file: `scripts/test_lumos.py:8918`、file: `scripts/test_lumos.py:27878`

severity: minor
blocking: 否 — 屬同族靜默失敗的漏網,邊界案例
引句:「工作樹那條路對應:不在 repo 裡」
問題:第 7 條的計劃類代碼五個沒有 `not_git`。`cmd_dispatch_lens_spec` 在會談目錄不在 git 專案時(`scripts/lumos:49009` 附近)回 rc 2、不印代碼,和舊裁定要消除的靜默是同一族。掛鉤已經有 `not_git` 的說明句可以重用。
具體失敗情境:會談開在非 git 目錄、派工詞帶 `LUMOS-SPEC:`,掛鉤仍是什麼都不附也不說明。
佐證:file: `scripts/lumos:49005`

severity: minor
blocking: 否 — 屬每支檔有家的說明落差
引句:「在工作目錄(計劃所在的工作樹)建一個不掛分支的提交」
問題:`spec-freeze` 是寫 git 物件、產快照的子命令,程式落在 `scripts/lumos`。目前管這支檔的 `Systems/派工鏡頭` 的 responsibility 只管「附在派工詞尾端的參考資料」,`design-loop` 又沒寫負責範圍。lands_in 四篇沒說 `spec-freeze` 的說明寫進哪一篇、要不要擴寫 responsibility。
具體失敗情境:實作完把說明寫進 `Systems/派工鏡頭`,但該篇 responsibility 寫的不負責這類事,之後的人不知道凍結提交的脈絡該去哪找。
佐證:file: `docs/lumos-toolchain-knowledge/Systems/派工鏡頭.md:24`

已讀,無 finding 的節:
- 第 1、3、4、5 條:提交寫法的辨識、只讀一般檔、`_nodehome_cat_blobs_capped` 的上限比較與回傳語意,都對得上現有程式。
- 第 9、10 條與回退:`_sync_global_hooks` 用 `copy2` 無條件覆寫已確認。`_trusted_lumos` 的找法和計劃寫的一致。`rN-dispatch.json` 多一個鍵沒有嚴格驗證擋它,和 `base_commit` 的前例一樣。
- 舊裁定 `Projects/派工鏡頭跨repo不再靜默_計劃` 的 WHY 引文逐字存在,「不推翻」的說法站得住。
- 新計劃 d1 的 content、context、why_chosen、alternatives_considered、trade_offs 都有,格式沒問題。

最高等級 major,共 2 條 blocking(翻案未記錄、作者可控自由文字進派工詞),另 4 條 minor 不阻擋。
