severity: major

# 設計審 r2 整合-sonnet 報告(整合與接手鏡頭)

範圍:逐項對照 `scripts/lumos` 與 `scripts/test_lumos.py`,看照〈做法〉1–11 字面實作時,接線點、兩側內容來源、`git grep`、單次跳過、帳本 `extra`、doctor S20、既有測試、條款夾具各處接得上不。以下 F1–F4 是會讓條款只在某一種實作成立或規則失效的洞,F5–F10 是接手者得自己猜的地方。

## F1 `git grep` 沒定義要搜哪些檔,照字面在平台根是 repo 根時規則永遠不擋
severity: major
blocking: 是
引句:「各平台根下的測試檔用 `git grep -w -F`(提交時 `--cached`、推送時對終點)整字找這個名稱」
file: `scripts/lumos:5084`(`load_platforms` 無 `platforms` 設定時 legacy 的 `root` 就是 `repo_root`;本 repo 的設定檔只有 `test_profile: python`)
file: `scripts/lumos:5416`(`discover_test_methods` 走 `_walk_test_files`:吃 profile 的 `exts`、`file_name_match`、`file_must_match` 與 `CODE_SKIP_DIRS`)
file: `scripts/lumos:4990`(python profile:`exts={".py"}`、`file_name_match=["test_*.py","*_test.py"]`)
1. 〈做法〉3 只說「各平台根下的測試檔」,沒說怎麼從 profile 導出 `git grep` 的路徑限定。`_platform_test_index` 回傳的平台根是絕對路徑(`(repo_root/root).resolve()`),`git grep` 要的是 repo 相對路徑加副檔名與檔名限定;`_walk_test_files` 那套篩選(副檔名、檔名錨、必含標記、略過目錄)沒有任何現成函式轉成 pathspec。
2. 接手者最省事的寫法是只對平台根下 grep,不帶副檔名限定。本 repo 與多數單平台消費專案的平台根就是 repo 根,那樣 grep 會搜到筆記自己。實測(在審查用的複製庫,名稱是計劃自己條款裡還不存在的測試名):
   `git -C <repo> grep -w -F -l t_note_shape_test_refs_new_names HEAD` 只命中 `docs/.../筆記測試綁定要存在_計劃.md`、`governance/review-reports/.../r1-snapshot.md` 這類筆記與報告,沒有任何測試檔。新加進筆記的壞名字一定出現在正在提交的那篇筆記裡(提交時 `--cached` 搜得到索引裡的筆記),複查永遠回「有」,兩邊說法不同就不擋,規則在 repo 根平台上形同虛設。
3. 另一種實作(只搜 `exts` 副檔名)又會搜到非測試的 `.py`(`scripts/lumos` 沒副檔名不受影響,但其他 `.py` 工具腳本與註解會中);第三種(完整照 profile 的檔名錨)結果又不同。三種實作對 S1、S11 的夾具會有不同結果,條款只在其中一種成立。
4. 平台根在 repo 外(`root` 設成上層目錄或兄弟 repo,`build_code_haystack` 註解提過「跨 repo」)時,`git grep` 的路徑限定算不出 repo 相對路徑,計劃沒講這種平台該跳過還是當「沒有」。
5. 要補的規格:明寫「平台根轉成相對 repo 根的路徑,再加 profile 的 `exts` 與 `file_name_match`(以及排除 `CODE_SKIP_DIRS`)當 pathspec;根在 repo 外的平台跳過並印一行原因」,並把「根是 repo 根時不能搜到 `.md`」寫成 S1 的夾具要求(夾具要同時有一篇含壞名字的筆記與 repo 根平台)。

## F2 平台設定從哪一版讀沒定義;`_platform_test_index` 只讀工作目錄,跟「被檢查版本」的承諾對不上
severity: major
blocking: 是
引句:「設定有 `platforms` 時可帶 `平台:` 前綴,沒有時整串當名稱。」
file: `scripts/lumos:12856`(`_platform_test_index(repo_root)` 內 `pdata = load_platforms(repo_root)`,沒有 `cfg` 參數)
file: `scripts/lumos:5084`(`load_platforms(repo_root, cfg=None)` 在 `cfg is None` 時讀工作目錄的 `.lumos/config.json`)
file: `scripts/lumos:28569`(`cmd_note_shape` 的 `note_shape.*` 才是從 `_nodehome_reader(root, tip_where)` 讀被檢查版本)
1. 計劃〈名詞〉說被檢查的版本是「note-shape 讀筆記與 `note_shape.*` 設定都從這裡」,但抽取(名稱怎麼切前綴)、`_classify_test_refs` 的 `split/default`、`git grep` 的「去掉平台前綴」三處都要平台表,這張表只能來自工作目錄(現有函式不接受傳入設定)。
2. 具體失敗:推送一條分支,分支上同一個提交把 `.lumos/config.json` 加了 `platforms` 並寫 `[test:ios:t_x]`,目前簽出的是 main(無 `platforms`)。工作目錄是 legacy,`ios:t_x` 整串當名稱,`resolve_test_refs` 不切分,走 `bad-name`(含冒號過不了 `_KILL_METHOD_OK_RE`)。若抽取那一步改用終點版設定去前綴、`git grep` 搜 `t_x`,兩邊搜的字串不同;若兩邊都用工作目錄設定,搜 `ios:t_x`。實作者各選一邊,S3(前綴寫錯)與 S11(兩邊說法不同)的結果就不同。
3. 要補的規格:明寫抽取與判定一律用同一張平台表,並說是工作目錄的(`_platform_test_index` 現況)還是要改成傳終點版設定(要擴 `_platform_test_index` 加 `cfg` 參數,`load_platforms` 已支援);兩側次數相減用的鍵是原字串還是去前綴後的名稱也要寫。

## F3 單次跳過路徑兩條各在哪算沒講清,現有跳過分支與推送範圍解析的順序會讓「推送時也記」做不出來
severity: major
blocking: 是
引句:「單次跳過時,提交與推送兩種都先算一次記進去(不靠 `--slots`)。」
file: `scripts/lumos:28569`(跳過分支在解析 `--diff` 範圍、淺層檢查、`_lens_push_base`、`_nodehome_clamp_base` 之前就 `return 0`)
file: `scripts/lumos:28089`(`_ns_skip_slot_extra` 只有提交時、`staged and slots_flag` 才被呼叫;`smode == "off"` 或 `sv is None` 時回 `None`)
1. 提交那條:`_ns_skip_slot_extra` 目前整個包在 `smode == "off" → return None` 與 `sv is None → return None` 之後。照計劃「帳本 `extra` 多一個 `test_refs` 鍵、併在同一個 `extra` 字典」做,格子那段回 `None`(格子關了、掛鉤沒帶 `--slots`)時 `test_refs` 鍵會一起掉,而計劃要求「不靠 `--slots`」。要重構成兩段各自算再合併,計劃沒講。
2. 推送那條:跳過分支在算出 `tip`、`base` 之前就返回。要算 `test_refs` 就得把範圍解析搬到跳過之前或複製一份;搬動會改變既有行為(範圍寫錯原本跳過後 rc 0,搬後變 rc 2;淺層 clone 原本在跳過之後才記 `skipped-env` shallow,搬後可能記兩筆)。計劃沒指定,S16 的「推送時被單次跳過」夾具在兩種做法下行為不同。
3. 「逃生口不能因此失效」(現有註解的原則)沒被提:跳過時要建索引並對每個名稱跑 `git grep`,每次 `_lens_git` 預設逾時 20 秒,計劃沒要求整段包 `try`、逾時就略過 `test_refs` 鍵。
4. 要補的規格:推送時跳過在哪一行算、重用哪些既有函式(`_lens_range_ok`、`_lens_push_base`、`_nodehome_clamp_base`)、範圍算不出來時記不記、算失敗時帳照寫只缺 `test_refs`。

## F4 推送時「兩側總次數相減」把合進來的主線改動也算成這次新加,而既有規則刻意排除了這類
severity: major
blocking: 是
引句:「這次改到的筆記(含新增、刪除、改名的兩端)裡,某個名稱在終點版本的總次數多於起點版本的總次數,多出來的那幾次就是新加的。」
file: `scripts/lumos:27220`(`_ns_exclusions`:已在主線上的提交不重查)
file: `scripts/lumos:27250`(`_notelines_range_added` 對合併提交只算它自己寫的行 `_merge_new_lines`,並排除遠端主線)
file: `scripts/lumos:38535`(`_lens_push_base` 的說明自己寫了「合過主線時會算錯」,推送前漂移檢查改走 `_push_range_start`)
1. 〈做法〉2 用 `git diff 起點 終點` 的淨差異。分支合過主線(`git merge origin/main`)後,起點到終點的差異包含隊友在主線新加的筆記行。隊友若用沒升級的 lumos、或用 `--no-verify`/跳過推上主線,他們的壞名字會被算成「你這次新加的」,擋在不相干的人身上。
2. 既有的新寫行機制(`_notelines_range_added`)正是為了這個問題做了主線排除與合併提交只算自己寫的;計劃〈範圍〉的 PRIOR-ART 說「全部沿用既有零件」,但抽取起點用的是 `_lens_push_base`(同一支說明承認合過主線會錯),沒沿用排除主線那套。
3. 條款沒有任何一條在測「分支合過主線」,S2 只測「搬動/改字/筆記改名」。
4. 未實測,依據是讀碼(上述兩支函式的說明與實作)。要補的規格:起點改成「跟主線的分岔點」或明寫對合併提交怎麼處理,並加一條夾具:主線有人新加壞名字、分支合進來後推送不應被擋。

## F5 〈做法〉2 的 `git diff 起點 終點` 寫不出「終點是索引」;路徑還有 NFC、非 `.md`、非 UTF-8 三處接手要猜
severity: minor
blocking: 否
引句:「這次改到的筆記清單用 `git diff --name-status -z --no-renames 起點 終點 -- 知識庫`(提交時起點是 HEAD、終點是提交索引)」
file: `scripts/lumos:27344`(`_notelines_new` 提交時用 `_ns_diff(repo_root, "--cached", "--", vault_rel)`;`b = reader(p)` 失敗與 UTF-8 解碼錯誤各有處理)
file: `scripts/lumos:26093`(`_nodehome_list(..., oids)` 才是處理 NFD 檔名的既有辦法)
1. `git diff` 不能把索引當第二個提交位置,提交時必須是 `git diff --cached HEAD`(或 `--cached`),推送時才是兩個 sha;起點為 None(首次提交)要換成空樹。照字面寫會在提交時出錯並被 fail-open 吞掉,規則整個沒跑。
2. 路徑拿去 `_nodehome_reader` 讀時,既有程式碼的作法是 `norm=False` 保留 git 原樣路徑再給 `reader`(`_notelines_new` 的 `reader(p)` 收的是原樣路徑),否則存成 NFD 的中文檔名讀不到,整篇漏查。計劃只說「讀兩側」。
3. 筆記清單沒限定 `.md`(`-- 知識庫` 下有 `.jsonl`、圖檔),也沒說讀不成 UTF-8 的怎麼辦(`_notelines_new` 回 `errs`)。

## F6 違規行號靠「這次新寫行」,但〈做法〉7 又說不靠新寫行容器
severity: minor
blocking: 否
引句:「它只看這次改到的筆記,不靠新寫行容器,也就不靠格子的 `--slots`」
引句:「行號(這次新寫行上第一次出現的位置;只是次數變多、找不到新寫行時,報終點裡第一次出現的位置)」
file: `scripts/lumos:27344`(`_notelines_new` 才有「新寫行」:提交時是 `--cached` 的新增行號,推送時是逐提交文字集合並受上線點、主線排除影響)
1. 〈做法〉5 要「新寫行」位置,〈做法〉7 又說不靠新寫行容器。接手者得決定:重用 `_notelines_new`(會帶進上線點與主線排除,跟〈做法〉2 的淨差異口徑不一致,可能出現「名稱算新加但找不到新寫行」)、或自己再跑一次 `git diff -U0` 解析。S1 只要求列出行號,兩種做法都過,但報出的行號會不同。

## F7 帳本「違規種類欄」其實是 `extra["check"]`,只有兩種值,計劃的「再多列一項」沒定形狀
severity: minor
blocking: 否
引句:「事件既有的違規種類欄照既有寫法再多列一項 `test_refs`」
file: `scripts/lumos:28368`(`_ns_slot_extra` 回 `{"check": "shape+slots" if mixed else "slots", ...}`,只在有格子違規時才帶 `extra`;只有形狀違規時事件根本沒有 `check`)
file: `scripts/lumos:28685`(`_note_shape_report`:`blocked` 只看 `mode`/`smode`,`nodes` 只收 `viol`、`errs`、`sviol` 的筆記,`count` 字串也只有兩項)
1. 目前沒有「違規種類欄」,是 `check` 單一字串。`test_refs` 加進來後的值是 `"shape+slots+test_refs"` 一類組合、還是改成列表,計劃沒講;單獨只有 `test_refs` 違規時 `check` 該填什麼也沒講。
2. `_note_shape_report` 的 `blocked`、`nodes`、`count`、warn 模式的 `warned` 帳都要跟著加這組,計劃只講了 `extra`。S16 只驗 `test_refs` 鍵,所以條款綠但 `nodes` 欄不含這組筆記時 `lumos gov` 的逐篇統計會漏。

## F8 照計劃教人寫的改法會讓 `lumos lint` 把舊 PITFALL 當新文法唸出缺出處與根因
severity: minor
blocking: 否
引句:「舊寫法的行改寫成 `[test-gone:]` 時不該因此被當成新文法、被要求補齊新格子」
file: `scripts/lumos:3750`(`_SLOT_NEW_ONLY` 含 `防回歸`)
file: `scripts/lumos:3932`(`context_marker_warnings`:行內有任一新文法鍵就改走格子表)
1. 計劃擋下訊息叫人「`[防回歸:無 理由]`」。`防回歸` 在 `_SLOT_NEW_ONLY` 裡,所以 note-shape 的格子規則(靠 `_ns_slot_key` 的舊行比對)放行,但 `lumos lint` 的 `context_marker_warnings` 走 `slot_is_new` 分支。實測(`import` 該腳本):`PITFALL:[2026-09-05]邊跑邊改腳本會從舊位置續讀 [test-gone:t_x] [防回歸:無 測試已刪]` 回 `筆記格子『PITFALL:』缺 [出處:]、[根因:]`;只寫 `[test-gone:t_x]` 時回 `脈絡標記『PITFALL:』缺防回歸`。
2. 這兩個是 warning、不擋,但 rtb 要改的 42 行舊 PITFALL 照訊息改完,`lint` 會一次噴 42 條要補出處、根因的提醒,跟 S20 與〈做法〉9 的「不被要求補齊」互相矛盾。要不接受(寫進〈實務隱患〉),要不明寫 lint 這側怎麼處理。

## F9 doctor S20 的「複查」對哪一版、索引壞了怎麼辦沒講;條款編號與 doctor 段名撞號
severity: minor
blocking: 否
引句:「列出所有筆記指不到的測試名(過了複查還指不到的)」
file: `scripts/lumos:2538`(S19 段;S18 以 `try` 包住並印 fail-open 一句)
file: `scripts/lumos:7545`(軟段截斷測試的視窗是 `[S]` 到 `[E1]`,S16–S19 與 S20 位置在視窗之外,計劃的「實作時確認」可以放心)
1. doctor 沒有「被檢查的版本」:複查的 `git grep` 該對工作目錄、索引、還是 HEAD?三者在未提交的測試檔上結果不同,影響 S13 夾具。
2. `_platform_test_index` 丟例外(設定壞)時,doctor 段要像 S18 一樣 fail-open,計劃只在 note-shape 的 S12 講了 fail-open。
3. 計劃自己的條款 `[S20]`(格子鍵)與 doctor 段 `S20` 撞名,而計劃內多處寫「S20」指 doctor 段,讀者(含條款綁定的 `lumos spec-trace`)容易讀錯;建議 doctor 段在計劃內一律寫「doctor 的 S20 段」。

## F10 1c「一模一樣」的比較沒定正規化,與名稱次數那邊「折行不算新加」口徑不一致
severity: minor
blocking: 否
引句:「接回後的整條在起點那一側——這次改到的所有筆記合起來——找不到一模一樣的」
file: `scripts/lumos:28148`(`_ns_summary_logical` 用 `" ".join` 接回續行,只去掉各行頭尾空白)
1. 計劃對名稱次數宣稱折行重排不算新加,但 1c 比的是接回後整條的字串。把一條舊的作廢條目在中文詞中間重新折行,接回後多一個空格,字串不同,照計劃字面就被判「新寫」而擋(只要它掛著活測試)。既有格子規則用 `_ns_text_key` 把中日韓字旁的空白整個去掉才解決同一個問題。要不沿用 `_ns_slot_key`/`_ns_text_key`,要不寫明這種情況會擋。
2. 摘要之外的正文行沒有「接回」,「整條」就是單一實體行,計劃的 1c 定義沒說正文行適不適用。

## 其餘節
- 〈設定與開關〉(做法 6):照 `_note_shape_slots_parse`/`_ns_slots_mode` 的形狀接得上(`_NS_SLOT_MODES` 可重用),已讀,無 finding。
- 〈doctor S20 位置〉:接在 S19 之後、`S8` 之前,與既有「避開 `[S]`–`[E1]` 視窗」的位置紀律一致,既有測試 `t_doctor_soft_sections_truncate_by_default` 與 31384 行附近檢查 `[S19]` 的測試不會因它變紅;已讀,無 finding。
- 既有測試變紅面:`_ns_repo` 系列 note-shape 夾具(`scripts/test_lumos.py:50110`)預設沒有 `test_profile`,筆記裡的 `[test:` 只在 `t_slots_*` 單元級(直接呼叫 `slot_check`,不經 note-shape)出現,所以新規則本身不會讓既有 note-shape 測試變紅;會變紅的候選是 `_SLOT_KEYS` 加 `test-gone` 後的 `t_slots_single_table`(計劃已說明只比必有鍵,不受影響),已讀,無 finding。
- 條款夾具:S1、S2、S4–S10、S14–S19 都能用 `_ns_repo` 加 `.lumos/config.json` 的 `test_profile: python` 與一支 `tests/test_x.py` 造出;S3 要多平台設定、S11 要「已改未暫存」的測試檔、S12 要不存在的平台根;三者的夾具與 F1、F2 的選擇綁在一起,F1、F2 沒定之前 S3、S11、S12 的預期輸出不唯一。

最高等級:major,blocking 共 4 條
