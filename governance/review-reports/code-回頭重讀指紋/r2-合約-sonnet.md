severity: major

我讀了三份修補檔和圖譜裡的計劃、筆記內容審、手冊,再對照 `scripts/lumos` 與 `scripts/test_lumos.py`。我沒有跑整套測試,只用 `_note_reread_hunk_tags` 實測了幾種語言的原始碼。計劃〈驗收條款〉S1 到 S19 的 `[test:]` 名字都找得到對應函式,S9 的 NUL 內容也真的造出二進位檔。逾時說明、`_note_reread_own_fps`、`_note_reread_tip_names` 的截止時間、`_nodehome_cat_blobs_capped` 改用 `_git_timeout`、`core.attributesFile` 與 `attr.tree` 這些說法,跟程式一致。

severity: major
blocking: 是 — 手冊與計劃保證「搬到另一個函式裡」會重判,但程式只對 def/class/function/func/fn 這幾個關鍵字成立,對沒有這些關鍵字的語言,這個保證不成立。這是上一輪資安席 major 想堵的洞,在這些語言裡仍然開著。
引句:「或你那段改動落到另一個函式裡(所在函式的名字也算,參數列不算)」
問題:`_note_reread_hunk_tags` 在頂格行沒有 def/class/function/func/fn 時,退而取「第一個識別字」當名字。縮排的定義行也只認這幾個關鍵字。所以 Kotlin 的 `fun`、TS/JS 的 `export const x = () =>`、C 系的 `int a(...)`、Java/C# 類別裡的方法,名字都退化成語言關鍵字或型別名。計劃〈做法〉1 只寫「都沒有就取第一個識別字」,沒說這等於放棄分辨;手冊和筆記內容審也沒講。
具體失敗情境:我用 `_note_reread_hunk_tags` 實測,輸出如下:
- Kotlin 兩個 `fun a/fun b`,各有同一段 `check(u)`:回傳 `['fun','fun']`。
- TS 兩個 `export const a/b`:回傳 `['export','export']`。
- Java 的 `public class H` 裡兩個方法:回傳 `['H','H']`。

這就是資安席 major 的情境:同一段 `-check(u)/+allow(u)` 從公開端點搬到管理員端點,前後三行一樣,v2 指紋不變,先前記的 v2 紀錄照樣算「已對照」。v1 看到 blob 變了會擋,這裡不擋。專案的 skills 清單有 kotlin、java、csharp、dart、swift、node 這些棧,這不是範圍外。
測試也沒守住這點:`t_reread_fp_hunk_ident_rule` 與 `t_reread_fp_hunk_moved_between_functions` 只用 Python 的 `def` 和 `class H:`。
修法:要嘛補關鍵字(`fun`、`const x =`、有括號的方法簽名),要嘛把「第一個識別字」這條退路改成整行去掉參數列後當名字。至少要把限制寫進計劃、手冊與筆記內容審,並補 Kotlin 或 TS 的搬移測試。
佐證:file: `scripts/lumos:36237`(`_NOTE_REREAD_DEF_RE`)、file: `scripts/lumos:36580`(`_note_reread_hunk_tags`,頂格行退路 `_NOTE_REREAD_IDENT_RE.match(s).group(0)`)、file: `skills/lumos-project-notes/commands/06-代碼審與推送.md`(「回頭重讀」第一層那條)

severity: minor
blocking: 否 — 只是計劃的現況句過時,不影響行為。
引句:「本計劃給它加兩個參數,預設都不變(資安席照舊),回頭重讀這邊都打開」
問題:這段是這次修補沒改到的上下文句。`_patch_file_changes` 現在有 `headers`、`lf_only`、`hunk_tag` 三個參數,回頭重讀這邊也不是「不算函式名標頭」,而是用 `hunk_tag` 換成我們自己算的名字。同一句後面還寫「它現在連 `@@` 後面的函式名標頭一起算」,跟下面新加的「但段落所在函式的識別名要算」讀起來互相打架。
具體失敗情境:下一個 session 只讀這一條,會以為 v2 完全不看函式標頭,把 `hunk_tag` 當多餘的東西拿掉,又重新開出上一輪那個 major。
佐證:file: `scripts/lumos:26033`(函式簽名與 docstring 已寫三個參數)

severity: minor
blocking: 否 — 條款帳面不全,不是行為錯。
引句:「十九條條款各一支測試(名字照條款),夾具是「有遠端、`refs/remotes/origin/main` 指在分支起點、分支開在上面」」
問題:這次修補新增了標 `[G1]` 到 `[G6]` 的十二支測試,涵蓋識別名、兩邊同口徑截斷、不讀屬性檔、查大小失敗。〈驗收條款〉仍停在 S19,這些新行為在合約層沒有任何對應的 `[S]` 條款。最重要的「同一段改動搬到另一個函式要不同指紋」只存在於測試的 docstring。
具體失敗情境:日後有人刪掉或改寫這幾支測試,沒有任何條款會要求補回。上一輪 major 的守衛就只靠測試名,不在條款層。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/回頭重讀指紋不因主線前進失效_計劃.md`〈驗收條款〉,以及 file: `scripts/test_lumos.py:70920`(`t_reread_fp_hunk_ident_rule` 起)

severity: minor
blocking: 否 — 耗時基準過時,REVISIT 日期是 2026-12-15。
引句:「指紋這一步 5 次中位數 0.24 秒(v1 只要 ls-tree 已經讀好的編號,幾乎是 0)」
問題:這個基準是 r1 修補之前量的。修補後每篇用 v2 的候選多跑一次 0 行上下文的截斷判斷 diff(同一份筆記自己寫「大檔約 0.8 秒」),又多了頂端內容批次讀取。下面的 REVISIT 卻拿 0.24 秒當「多一個數量級就查」的門檻。
具體失敗情境:2026-12-15 重量時,新程式本來就比 0.24 秒慢,門檻要嘛誤報,要嘛因為基準太低而失去意義。
佐證:file: `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md`(「回頭重讀指紋不因主線前進失效:實作紀錄」一節)

最高等級 major,共 4 條 finding,其中 blocking 1 條。
