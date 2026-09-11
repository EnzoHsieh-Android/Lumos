severity: major

本篇審的是同一份文件的兩個入口(投稿檔 `每支檔有家-r2.md` 與 LUMOS-SPEC 節點 `Projects/每支檔有家_計劃.md`),已用 `diff` 逐字比對確認兩者完全相同(IDENTICAL),故 LUMOS-SPEC 尾端沒有另一個「被波及節點」需要逐條核對合約——後續判定即針對這份文件本身,跟第 1 輪同一個結論。

## 對第 1 輪本鏡頭(正確性)發現的複核(修到/沒修到/修出新洞)

- G1(正確性 F1,blocker,規則三只驗「某一支」觸碰檔是家):修到——新增 [S13b]、決策 d4,已用 `_nodehome_evaluate`(scripts/lumos:17757-17772)與真實測試 `t_nodehome_write_back_requires_every_changed_file_homed` 覆判,散文塞進同一篇沒家檔的情境會被 `write-back-homeless` 擋下。另用 pos-guest 真實提交 `0cbbdbe`(桌邊點餐首次長歪那個提交)代入現行規則推演:`cart.js`/`CartSheet.vue`/`Receipt.vue`/`SendSheet.vue`/`TablePicker.vue` 五支新檔在該提交後 about_code 仍只列 `src/core/state.js`,照 [S3] 全部會被判 `new-homeless` 擋下,`App.vue`/`core/api.js` 兩支既有檔沒家、節點內容同時有變,照 [S13b] 會被判 `write-back-homeless` 擋下——確認修法對得上原始事故。
- G3(正確性 F2,major,--diff 逐個提交是全新機制):修到——決策 d5 改成整段比,`scripts/hooks/pre-push:187-199` 與 `_nodehome_clamp_base`(scripts/lumos:17683-17696)實作跟文字描述一致,起點採「不在任何遠端分支上的提交」而非空樹兜底。
- G4(正確性 F4,major,三段健檢位置未定):修到——已核對 `scripts/lumos` 的 section 呼叫順序 E1(1737)→E3(1935)→S7(2067)→S8(2109)→S9(2125)→S10(2135)→H(2149),落在 [S28] 寫的「合約條數段之後、[H] 之前」;且 `t_doctor_soft_sections_truncate_by_default` 用的 `[S]`..`[E1]` 切片窗口早於 S8-S10,不會被誤算。
- G5(正確性 F5,major,四份清單其實無第五份可借):修到——`_NODEHOME_CODE_EXTS`(scripts/lumos:17360-17363)已是具名常數,且接進 `t_code_exts_four_lists_agree`(scripts/test_lumos.py:7615-7622),實跑 26 條全過。
- G7(正確性 F6,major,node_home.ignore 語法未定):修到——名詞段明寫字串清單+`_cochange_excluded`(scripts/lumos:18058-18067)的 fnmatch/`**/`補丁語法,`_nodehome_required`(scripts/lumos:17598)直接呼叫同一支函式。
- G19(正確性 F3,major,「內容有變」與既有正文雜湊衝突):修到——名詞段明寫「★不沿用★」,`_nodehome_parse_note`(scripts/lumos:17543-17567)逐欄比對 summary/decisions/body,`t_nodehome_route_content_change_definition` 第⑤條直接斷言 `note_body_hash`/`_body_hash_of_text` 不出現在該函式體內。
- G33(正確性 F7,minor,`-k home` 混進三支無關測試):修到——「驗收怎麼跑」段已全部改成 `-k nodehome` 等具體關鍵字,不再用裸 `home`。

## frontmatter(decisions d1–d5)

已讀,無 finding。d5 新增,內容與 `_nodehome_clamp_base`/pre-push 的實作一致(見上 G3)。

## 為什麼(這批的來源)

已讀,無 finding(已用 pos-guest `0cbbdbe` 重新核對過數字與敘述,見上)。

## 世界上怎麼做的(PRIOR-ART)

已讀。額外查證③「不另寫批次讀取」的內部先例:`_vendored_state`(scripts/lumos:13522)的註解「讀那個版本的檔用專案既有的 git show 包裝(第四輪架構席:第三輪另寫了一套 cat-file --batch 解析)」確實存在,PRIOR-ART 陳述屬實。但這個先例只證成「單一版本要不要批次讀」這一半;名詞段「讀哪個版本」另外宣稱的「起點那一側只讀範圍內變動節點、其餘跟終點共用」沒有對應的實作或先例可查,見 F2。

## 名詞

已讀「需要家的檔」「測試檔」「node_home.ignore」「家」「別人的檔」「內容有變」「新違規」,均已逐條查證(見上 G1/G5/G7/G19 與下方規則段落),無新 finding。

### F1 「新開的」用檔案新舊判定,漏接「既有節點從 planned/deferred 升格為家」這個真實會發生的路

severity: major
blocking: 是 — 一篇節點可以完全不寫負責範圍就變成某支檔的家,直接落空規則四想保護的「出生時就要講清楚負責什麼」,而且是本專案自己圖譜裡已經在用的模式。
1. `_nodehome_evaluate` 判定「是不是新開的節點」只看 `b = B.notes.get(src_rel)` 是否為 `None`(scripts/lumos:17730、17742),也就是「這個提交前這支 .md 檔案是否已經存在」;只要檔案本身在提交前就存在(不管當時狀態是不是家),就會被當成「既有節點」,走 [S18] 的「超過上限才擋」分支(scripts/lumos:17745-17748),而不是 [S17] 的「一律要」分支。
2. 但「家」的定義是狀態 doing/done/stale(scripts/lumos:17367),一篇 status: planned/deferred 的節點本來就不是家、可以合法沒有 about_code、沒有 responsibility 地存在;等它被 `lumos set status doing` 加上 `about_code` 升格為家時,如果新加的檔案數沒超過 `node_home.max_files`(預設 3),[S18] 的門檻就不會觸發,節點就在完全沒寫負責範圍的情況下正式變成某支檔的家。
3. 已用 `/tmp` 下自建的乾淨 git 專案實測(root 已清除):建一篇 `status: planned`、`about_code: []`、無 responsibility 的節點,下一個提交把 status 改成 doing、about_code 加 1 支新檔(`src/x.py`)、責任範圍仍不填,`lumos home check --staged` 回 `rc=0`,訊息只有一句「提醒:…行為有變的話說明要寫進去」,完全沒有擋下;同一份節點若這次 about_code 一口氣加到 4 支(超過上限 3)才會被擋(已同機實測,`rc=1`、訊息「這幾篇要先寫一句負責範圍」)。
4. 本專案圖譜裡已有這種節點的真實先例:`docs/lumos-toolchain-knowledge/Systems/nested-agent-permission-scope.md` 現在就是 `status: planned`、還沒有 about_code——它未來被實作、升格為家的那個提交,只要一次加進的檔案數不超過 3 支,就會依上述路徑漏接;`lumos append about_code`(`cmd_append`,scripts/lumos:11113 起)本身也沒有另外檢查 responsibility,不構成補位。
5. 既有測試 `t_nodehome_check_blocks_new_node_without_responsibility`(scripts/test_lumos.py:36005)與 `t_nodehome_check_blocks_growth_past_limit_without_responsibility`(scripts/test_lumos.py:36024)都只覆蓋「檔案本身就是這次新增」與「既有節點單純超過上限」兩種情境,沒有覆蓋「既有節點、狀態升格為家、檔案數仍在上限內」這第三種,所以這個縫隙不會被現有驗收擋紅。

引句:「這次新開的 Systems 節點沒寫 responsibility。出生時就要講清楚負責什麼」
引句:「既有的某篇 about_code 這次變多、之後超過上限、而它沒寫 responsibility」
file: `scripts/lumos:17730` `b = B.notes.get(src_rel)` 只問檔案在提交前是否存在,不問它當時是不是「家」(status 是否在 doing/done/stale)
file: `scripts/lumos:17742-17748` `if b is None:`(一律擋)/`else:`(僅超過上限才擋)兩分支,既有節點升格為家一律落入後者
file: `docs/lumos-toolchain-knowledge/Systems/nested-agent-permission-scope.md:3` `status: planned` 且無 about_code,是本專案自己會實際踩到這條縫隙的節點

## 規則一(S1–S6、S34)

已讀,無新 finding。實測確認 [S3]/[S34] 對真正新檔與首次出生提交的判定正確(見上 F1 附帶實測)。

## 規則二(S7–S10)

已讀。`_node_code_ref_tokens`(scripts/lumos:16147)確認被 `_nodehome_refs`(scripts/lumos:17627-17642)與既有推筆記路徑(scripts/lumos:16180)共用同一支函式,[S7]「重用」的陳述屬實,無 finding。

## 規則三(S11–S15、S35、S36)

已讀,無新 finding。用多組手推情境覆判過:改名(視同新增,about_code 未跟著改會被 [S3] 正確擋下;about_code 同一個提交跟著改則正確放行)、複數家同時聲稱同一支檔(正確共存,[S4] 不誤擋)、node 從有家降級成散文提到但沒 about_code(正確擋)、單一提交裡刪檔同時改節點內容(刪除的檔不進 `changed_new`,不會被誤判成 legacy-homeless)——這幾種「順手建家/改名/刪檔/從 about_code 拿掉」的交互都對得上規則文字,沒有找到誤判的具體提交。[S36] 自陳的「散文講另一支也有家的檔驗不出來」天花板仍然存在且已被 spec 自己承認,不重複計分。

## 規則四(S16–S19)

見 F1。其餘(--code/--responsibility 全驗完才建檔、issue 也能帶 --code)已用 `cmd_new`(scripts/lumos:12385-12487)核對過,行為與文字一致。

## 規則五(S20–S23)

已讀,無 finding,跟第 1 輪(架構對齊 G31 修到)結論一致,不在本鏡頭重複深挖。

## 在哪裡檢查(S24–S27、S37、S38)

### F2 「讀哪個版本」宣稱的「起點那一側只讀範圍內變動節點、其餘跟終點共用」沒有對應實作

severity: minor
blocking: 否 — 不影響任何一條擋/放判定的對錯(每個版本各自讀到的內容仍然正確),只是文件對讀取機制的描述跟程式碼實際行為不符,屬於「與程式碼現況不符的宣稱」。
1. `cmd_home_check` 的 --diff 分支對 B、N 兩側各自獨立呼叫 `_nodehome_side(root, base_where, vault_rel)` 與 `_nodehome_side(root, tip_where, vault_rel)`(scripts/lumos:17975-17976),兩次呼叫之間沒有任何共用快取或「只讀變動節點」的過濾。
2. `_nodehome_side`(scripts/lumos:17570-17585)對每一側都會把 `vault_rel/Systems/*.md` 底下**所有**存在的節點各自呼叫一次 `_reader(p)`;`_nodehome_reader`(scripts/lumos:17512-17540)在 `where` 不是 `"index"` 也不等於目前 `HEAD` 時(--diff 模式下的歷史提交必然如此),對每一支都會落到 `git show {spec}:{p}`,B、N 兩側等於把整批節點各用 `git show` 讀一次。
3. 這正是「實作時對計劃的修訂」段落改寫這句話所在的那個名詞(讀哪個版本),而該段落另一半「跟磁碟一樣的直接讀、不一樣的用 git show 包裝」確有內部先例(`_vendored_state`,scripts/lumos:13522)撐,但「其餘跟終點那一側共用」這半句沒有實作、也沒有測試覆蓋(`t_nodehome_reads_index_not_worktree` 只驗 staged 模式讀索引不讀工作目錄,沒有驗 --diff 模式的 B/N 共用)。

引句:「推送前的起點那一側只讀這段範圍裡有變動的節點，其餘跟終點那一側共用」
file: `scripts/lumos:17975-17976` B、N 兩側各自獨立呼叫 `_nodehome_side`,無共用機制
file: `scripts/lumos:17570-17585` `_nodehome_side` 對每一側的每一篇 Systems 節點都各自呼叫 `_reader(p)`,不分「這篇有沒有在範圍內變動」

## 舊帳(S28–S29、S39)

已讀,無 finding(位置紀律已於上方 G4 覆判;S29「跟 home check 共用同一套函式」已用 `_nodehome_ledger`(scripts/lumos:17889-17925)核對,`_nodehome_required`/`_nodehome_homes`/`_nodehome_refs` 三支確實共用)。

## 讓規則被看見(S30)

已讀,無 finding。`t_nodehome_rules_in_hint_skill_and_discipline` 實跑 11 條全過,五個地方(開新節點提示、教寫節點說明、節點還原 SOP 兩處、紀律區塊範本、架構對齊派工範本)都已核對存在。

## 邊界(S31–S32、S40)

已讀,無新 finding。[S32] 的「10 個提交範圍 2 秒內」manual 驗收沒有找到會讓它翻紅的證據,但如 F2 所述,達成方式跟文件描述的機制不同;效能數字本身不在本鏡頭覆判範圍(已於 r1 邊界/整合鏡頭收斂)。

## 範圍外(刻意不做)

已讀,無 finding。

## 落點

已讀。`Systems/每支檔有家` 已在 repo 裡實際存在(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md` 或等價路徑,規則段落引用的 about_code/責任範圍寫法與計劃一致),`Systems/design-loop`、`Systems/節點範圍與索引守衛` 均存在,無 finding。

## 實務隱患(對照補漏)

- 誤擋:規則三/[S13b] 的誤擋範圍其實比「一句話同時講兩支檔」更廣——只要這個提交裡任何一篇 Systems 節點內容有變,**跟那篇內容完全無關**的其他改動檔只要沒家就會一起被擋(commit 層級,不是節點內容關聯層級)。這是 [S13b] 條文本身寫的「只要有任何 Systems 節點內容有變」的字面結果,不是實作誤差,但「實務隱患」段與回頭條件的「一句說明同時講兩支檔」措辭把誤擋範圍講得比實際窄,判不準,不單獨計分(標 ⚠ 交編排者判斷措辭要不要放寬)。
- 漏擋:規則四的漏擋見 F1(既有分析未覆蓋這個方向,是本輪新找到的)。
- 效能:見 F2。
- 其餘(繞過、舊專案升級、併發、合併改基底、規則撤回、兩家一致、不可逆金流)已讀,跟第 1 輪結論一致,無新 finding。

## 驗收怎麼跑

已讀,無 finding(見上 G33 覆判);另外實跑 `python3 scripts/test_lumos.py -k nodehome` 與 `-k code_exts_four_lists_agree`,分別 123 passed/0 failed、26 passed/0 failed。

## 回頭條件

已讀。規則三那條 REVISIT 的量測口徑仍只涵蓋誤擋方向(治理帳數 [S13b] 擋了幾次、改 about_code 的比例),見上「實務隱患」的措辭落差;規則四(責任範圍)完全沒有對應的 REVISIT,F1 這種漏擋不會被任何既定的回頭機制發現。

## 實作時對計劃的修訂

逐條核對:①讀版本(部分修到,見 F2)、②測試檔判定(修到,`t_nodehome_required_files_definition` ④b)、③規則三只管能當家的節點狀態(修到)、④推送前上線點 clamp(修到)、⑤提交前點名改用 about_code(修到,pre-commit:170 註解與 [S15] 呼應)、⑥生效日/放行條件/事件種類與上限/健檢段名寫死、--code 給 issue 用(修到,見上 F1 分析與 cmd_new 核對)。

## 合約候選

已讀,無 finding。

## 審計修正紀錄

已讀,無 finding;r1 收貨表格與本輪覆判結果一致(見上逐條複核)。

總結:最高 severity major,blocking 共 1 條
