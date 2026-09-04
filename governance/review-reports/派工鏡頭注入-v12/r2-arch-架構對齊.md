# r2 架構對齊審查——派工鏡頭注入 v1.2(固定席 0 篇備援段,第 2 版)

審查範圍:凍結審材 `派工鏡頭注入-v12-r2.md` 的「## v1.2」節(第 184-203 行)。只判這節設計跟本 repo 既有做法一不一樣,不找 bug、不評風格。

## r1 驗收(三條,查證後皆已改)

r1 架構對齊席(`r1-arch-架構對齊.md`)判出的三條在 r2 這版逐一核對:

1. **grep 子行程 → 已改製程內正規式**:r1 f3(major/blocking)判「呼叫者」格寫 `grep -F -w` 是在既有 `build_code_haystack`/`discover_test_methods` 的 `os.walk`+製程內 `re` 慣例之外另立一條叫外部二進位的路。r2 第 192 行改成「★製程內 `\b名\b` 正規式,不開 grep 子行程★(架構席:沿 `build_code_haystack` 慣例;正確性席建議 `git grep -F -w`,兩席相反——採既有慣例,記留痕)」——已回到製程內 Python `re` 的既有形態(掃描來源改成等價的 `git ls-tree`,見〈問題1〉),f3 消解。
2. **測試格取數機制 → 已改讀 base 測試檔**:同一批 v1.2 r1 全折的 blocker 記載「三格資料來源全讀工作樹……全部違反 v1.0『只信 base』原則」。r2 第 190 行改成「在 base 樹的測試檔……裡找內容提到該檔 stem 或模組名的測試方法……檔內容用 `git show <base>:<路徑>`」,不再碰 `.lumos/testmap.json`,方向已對齊 v1.0 的 base-only 原則(演算法本身另有問題,見〈問題3〉)。
3. **fallback → fallback_status**:r1 f2(minor)判 `fallback` 沒跟上同一個輸出字典裡 `bound_status` 的 `_status` 字尾慣例。r2 第 199 行改成「`fallback_status: none|attached|attached-empty|skipped-timeout`(命名沿 `bound_status`)」,f2 消解。

三條驗收通過,可以往下看新結構。

## 問題 1:讀 base blob 的 os.walk 等價物有先例嗎

v1.2「呼叫者」格要在 base 樹的 code 檔裡找識別字引用,做法是「`git ls-tree -r <base>` 依 CODE_EXTS_T/CODE_SKIP_DIRS 過濾,內容 `git show`」(第 192 行)。這正是 dispatch-lens v1.0 自己已經在用的組合,不是新發明:`cmd_dispatch_lens` 算固定席清單時就先 `lt = _lens_git(root, "ls-tree", "-r", "--name-only", base_sha, quote=True)`(scripts/lumos:16665)——這次呼叫沒帶路徑參數,回來的是 base 樹**整棵**檔案清單,不只是 docs/;取到清單後才在 Python 裡篩出 `docs/*-knowledge` 的節點路徑(scripts/lumos:16668-16671)。內容則用 `sh = _lens_git(root, "show", f"{base_sha}:{it['rel']}", quote=True)`(scripts/lumos:16702)逐篇讀 base 版全文。CODE_EXTS_T/CODE_SKIP_DIRS 這組過濾條件也不是新造的:是 `build_code_haystack`(scripts/lumos:2886-2898)與 `discover_test_methods`(scripts/lumos:2902-2933)既有在用的常數(定義於 scripts/lumos:2447-2449),只是這兩支函式原本用 `os.walk` 掃工作樹,不是掃 base 樹。

v1.2 這格是把「dispatch-lens v1.0 已經在用的 ls-tree+show 讀 base 組合」跟「build_code_haystack 已經在用的 CODE_EXTS_T/CODE_SKIP_DIRS 過濾」直接拼起來——兩塊都各自有先例,拼法本身沒有另立新機制。結構對齊,不列不對齊。

## 問題 2:`_cochange_mine(upto=base)` 對齊,但「設定讀 base 版」沒有機制先例

先看 `cmd_cochange_check`(scripts/lumos:13519-13566)實際怎麼做:①一律呼叫 `_cochange_load_config(root)`(scripts/lumos:13372-13400)拿設定——這支函式寫死讀 `Path(repo_root) / ".lumos" / "cochange.json"`(scripts/lumos:13380),用 `.read_text()` 直接讀「當前簽出的工作樹」那份檔案,沒有接受 git ref 的參數;②只有「挖掘範圍」依 `--diff` 改:`base = diff_range.split("..")[0].strip()` 後 `upto = base`(scripts/lumos:13548-13552),再傳進 `_cochange_mine(root, cfg, upto=upto)`(scripts/lumos:13553)。

v1.2 第 191 行說「沿 `cmd_cochange_check` 那條路(`_cochange_mine(repo_root, cfg, upto=<base>)`……挖到 base 為止」——這段完全對齊:`_cochange_mine` 是純函式(scripts/lumos:13450-13469,只吃 `cfg`+`upto`,內部用 `git log`/`git show` 挖歷史,不碰工作樹檔案系統),照 `cmd_cochange_check` 的呼叫方式重用沒有問題。

但同一句話接著要「設定 `.lumos/cochange.json` 讀 base 版(base 沒有→用既有預設)」,這件事在全檔裡沒有任何既有函式做過。查過所有 `.lumos/*.json` 設定讀取路徑:`_cochange_load_config`(cochange)、`load_test_profile`(scripts/lumos:2622-2660,test_profile)、`_platform_test_index` 內部的多平台設定讀取(scripts/lumos:2665 起)、CI 設定讀取(scripts/lumos:14779),全部是「`Path(repo_root)/".lumos"/...`+`.read_text()`」這一種讀法,一律讀工作樹,沒有一個支援讀某個 git ref 的版本。v1.2 沒寫清楚要怎麼落地——改造 `_cochange_load_config` 讓它能吃 base 版內容,還是另外新寫一套(那會重複 `_cochange_load_config` 裡 min_support 硬底線、型別守衛那些既有驗證規則)。這一步判不準,列 f4。

## 問題 3:測試格是第二種「stem 命中」做法

`cmd_testmap_build` 判斷檔↔測試關係的邏輯在 `_testmap_mine`(scripts/lumos:14455 起),分三路訊號:訊號一 naming(scripts/lumos:14465-14475)用 `_testmap_stem`(scripts/lumos:14365)/`_testmap_strip`(scripts/lumos:14405-14432)算出「剝掉 Test/_test/.spec 等後綴的 stem」再互相比對;訊號二 content(scripts/lumos:14480-14504)用同一個 stem 建 `\b(...)\b` 的 alternation regex(依長度排序防止前綴互相吞噬),對測試檔全文找「內容有沒有提到這個 stem」。這兩路合起來就是「測試內容或名字有沒有提到來源檔的 stem 或模組名」——跟 v1.2 第 190 行要做的事(「找內容提到該檔 stem 或模組名的測試方法」)是同一個問題。

v1.2 沒有講要重用 `_testmap_stem`/`_testmap_strip`/訊號二的 alternation regex,而是另外寫一套:靠 test_profile 的 `file_name_match`/`dirs`(既有 `load_test_profile` 提供的欄位,scripts/lumos:2606-2617)找出 base 樹裡的測試檔,再用 `PYTHON_TEST_RE` 等 `method_re` 抽測試方法名——`method_re` 在既有程式裡的工作是「抽出測試方法名字」(discover_test_methods 用它做這件事,scripts/lumos:2932),不是「判斷 stem 有沒有被提到」;stem/模組名比對這個核心判定在 v1.2 裡完全沒有落到既有的 `_testmap_stem` 家族,是自己重新設計一套規則。這不是「不用 `.lumos/testmap.json` 這個地圖檔」的問題(那一步方向對,見〈r1 驗收〉第 2 條),而是連「怎麼判定 stem 命中」這個演算法本身都另立了一條——跟既有 testmap 的 naming+content 訊號是兩套獨立邏輯做同一件事。列 f5。

## 問題 4:三格排序規則有沒有既有慣例可沿

全檔排序呼叫——`cmd_cochange_rules` 的 `out.sort`(scripts/lumos:13497)、`cmd_cochange_check` 的 `warnings.sort`(scripts/lumos:13561)、testmap 的 `suggests.sort`(scripts/lumos:14706)、dispatch-lens 自己的 `free.sort`/`dropped.sort`/`lane_raw.sort`(scripts/lumos:16203/16233/16242)——無一例外都是「主鍵(分數/信心度)+至少一個決定性收尾鍵(名字/節點/測試名)」的多鍵排序,scripts/lumos:16242 那行甚至直接寫「# 同 free/rescued 三鍵慣例」,是本 repo 明講的慣例,用來保證同分時排序穩定、可重現。

v1.2 三格各自只給一個鍵:受影響測試「排序:提到次數多者先」(第 190 行)、共改夥伴「排序:confidence 高者先」(第 191 行——既有 `cmd_cochange_rules` 對同一份 `rules` 資料排序其實用三鍵:confidence 降冪+support 降冪+lhs 名字,scripts/lumos:13497)、呼叫者「排序:被引次數多的識別字先」(第 192 行)。三格都沒有寫收尾的決定性鍵。結構(依分數排序)是對的,只是少了本 repo 排序慣例裡「同分時怎麼定序」那一段,跟既有慣例不完全一致。列 f6。

## 不對齊清單

### f4

分層與資料源:共改夥伴格「設定讀 base 版」沒有既有機制可循。`_cochange_load_config`(scripts/lumos:13372)與其他所有 `.lumos/*.json` 讀取函式(`load_test_profile` 等)都寫死讀工作樹路徑,沒有一個支援讀 git ref 版本;spec 沒寫清楚要改造既有函式(對齊)還是另寫一套(等於重複 `_cochange_load_config` 的驗證邏輯,算第二種做法)。

引句:「設定 `.lumos/cochange.json` ★讀 base 版★(base 沒有→用既有預設)」

severity: ⚠
blocking: 否

### f5

第二種做法:「受影響測試」格自己重新設計「stem/模組名命中」判定,沒有沿用 `cmd_testmap_build` 既有的 `_testmap_stem`/`_testmap_strip`(scripts/lumos:14365-14432)+訊號二 content alternation regex(scripts/lumos:14480-14504)——這兩支函式解決的正是同一個問題(測試內容/名字有沒有提到來源檔 stem)。

引句:「找內容提到該檔 stem 或模組名的測試方法」

severity: major
blocking: 是

### f6

命名與結構不一致:三格排序規則只給單一鍵,沒有沿用本 repo 明講的「三鍵慣例」(scripts/lumos:16242 註解;`cmd_cochange_rules`/`cmd_cochange_check`/testmap `suggests` 等排序一律「主鍵+決定性收尾鍵」)——結構(依分數/次數排序)沒問題,缺的是同分時的收尾定序鍵。

引句:「排序:confidence 高者先」

severity: minor
blocking: 否

## 小結

不對齊共 3 條,其中 major 1 條。
