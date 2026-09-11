severity: blocker

本篇審的是同一份文件的兩個入口(投稿檔與 LUMOS-SPEC 節點),經 diff 逐字比對確認兩者完全相同,故不存在另一個「被波及節點」需要逐條核對合約——後續判定即針對這份文件本身。frontmatter 的 `related:` 與正文 `[[Systems/節點範圍與索引守衛]]`、`[[Projects/固定席扇出降權_計劃]]`(2 處)四個交叉引用皆已用 Read/Bash 核對目標檔存在,無壞連結。

## frontmatter(decisions d1–d3)
已讀,無 finding。d3 提到「舊 Android 消費專案 about_code 100% 沒填」的量化陳述未逐一複驗(超出可查證範圍),但推理鏈(擋新增/不擋舊帳)內部自洽。

## 為什麼(這批的來源)
已讀。用 `git -C pos-guest show --stat 0cbbdbe` 與 `docs/pos-guest-knowledge/Systems/客人端決策層.md` 逐項核對「13 支程式檔只有 1 支正式管、3 支靠依賴行順帶連上、其餘 9 支不會推出筆記」——13 支程式檔、about_code 僅 `src/core/state.js`、DEP 行只 backtick 出 4 個目標(3 支檔+1 個目錄)——數字精確對得上,背景陳述屬實,無 finding。

## 世界上怎麼做的(PRIOR-ART)
關聯 F3(見下),其餘部分(about_code/impact 抽取/vendored 指紋/testmap/處置閘 cutoff)皆用 Grep/Read 在 `scripts/lumos` 找到對應實作,「已存在」的陳述屬實。

### F1 規則三只驗「某一支」觸碰檔是家,放行同一交易把其餘檔的說明塞進同一篇
severity: blocker
blocking: 是 — 照字面實作出來的檢查,擋不住這份 spec 自己拿來當動機的那個真實事故重演,等於整個功能沒達成目的。
1. S13 是存在量詞(「某支」),不是全稱量詞:只要這次提交裡有任何一支已在 about_code 的檔被動到,該節點就算「有家」,其餘一起被塞進同一段散文的檔完全不受限。
2. 規則二(S7–S9)只認反引號抓到的路徑;真實案例 `docs/pos-guest-knowledge/Systems/客人端決策層.md` 目前僅在 `DEP:` 一行 backtick 出 4 個目標,KEY/FLOW 行描述 TablePicker/CartSheet/PaySheet/TakeoutReceipt 等 8 支畫面檔全程未曾以反引號出現——這種純散文描述規則二完全看不見。
3. 用真提交推演:若下一次提交同時改 `src/core/state.js`(已在 about_code)與 `src/ui/TablePicker.vue`、`src/App.vue`(皆未在 about_code、也從未被反引號提及),並把兩者的行為說明寫進同一篇 KEY 行——S13 判「有家」(因 state.js 命中)、S9 判「無新增別人的檔」(因從未反引號提及)——兩條規則全過,節點會繼續長成「一篇包全部」,跟這份 spec 自己記錄的事故一模一樣。
4. 回頭條件只追蹤「規則三擋了幾次、其中幾次改 about_code」這個誤擋比例,完全沒有涵蓋這種漏擋(該擋沒擋)的情形,無法靠既定的 REVISIT 機制發現此洞。
引句:「內容有變的每一篇 Systems 節點（含這次新開的），提交後必須是某支改動檔的家」
引句:「節點正文或摘要裡用反引號寫、改檔前推筆記那套抽取會認成某支需要家的檔」
file: `/Users/enzo/harness/pos-guest/docs/pos-guest-knowledge/Systems/客人端決策層.md:7` about_code 僅列 `src/core/state.js` 一支,KEY 行描述的另外 8 支畫面檔全未 about_code 化
file: `/Users/enzo/harness/pos-guest/src` TablePicker.vue/CartSheet.vue/PaySheet.vue/Receipt.vue/SendSheet.vue/TakeoutReceipt.vue/OptionSheet.vue/ModePicker.vue/main.js 共 9 支,節點正文從未以反引號提及其路徑或裸檔名

## 名詞
### F6 `node_home.ignore` 的樣式語法未定義
severity: major
blocking: 是 — 同一個設定值,不同語法解讀(glob/regex/前綴)會排除不同檔案集合,同一次提交在兩種實作下可能一個放行一個擋下。
1. 全文檔只出現一次 `node_home.ignore`,未說明是 glob(且是否處理 `**/` 前綴,如既有 `_cochange_excluded` 要額外補一次比對才吃得下根層檔案)、正則,還是純字串前綴比對。
2. 既有的 `.lumos/config.json` 其他排除類設定(`_cochange_excluded` 的 exclude pattern)已有一套 fnmatch+`**/`前綴補丁的具體寫法可援引,但 spec 未指向它,也未寫自己的語法。
引句:「排除 docs/ 與建置輸出夾、測試檔、lumos 自己裝進去而且內容沒改過的檔、專案設定 `node_home.ignore` 列的樣式」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/lumos:17263` `_cochange_excluded` 是本專案唯一「排除樣式」的既有實作,含 `**/` 前綴補丁,spec 未參照

## 規則一(S1–S6)
### F5 「同一份清單」其實是四份靠測試釘住一致的獨立清單,scripts/lumos 裡沒有可直接借用的那一份
severity: major
blocking: 是 — 若比照措辭直接在 `lumos home check` 裡再抄一份副檔名清單,會製造第五份未受 `t_code_exts_four_lists_agree` 保護的清單,這正是本專案已真實踩過的漏洞形狀(見下 file 證據)。
1. 「改程式要動圖譜」這道閘的判準實際上分散在 4 個檔案、以 bash 正則+2 份 Python 常數存在,靠 `t_code_exts_four_lists_agree` 這支測試逐一比對一致,不是單一常數。
2. `scripts/lumos` 裡唯一同名的 `CODE_EXTS_T`(3278 行)是 Check T 的測試符號掃描表,跟「要不要動圖譜」的判準用途不同、內容也不同(例如前者無 `.sh`/`.ps1`,shebang 規則也不同)。
3. spec 沒有提到要把「需要家的檔」清單也接進 `t_code_exts_four_lists_agree`(或擴成五份一致),而這支測試的 docstring 本身就記錄了一次「新增一個消費者但沒接漂移守衛」導致 `.sh` 溜過同步閘的真實事故。
引句:「那道閘同一份清單，測試檔判定沿用測試地圖那一支」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/hooks/pre-commit:124` `CODE_EXTS_RE` 是四份清單裡被測試當基準(`ref`)的那一份,不在 `scripts/lumos`
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/lumos:3278` `CODE_EXTS_T` 是 Check T 專用清單,與「要不要動圖譜」判準不同源
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/test_lumos.py:7591` `t_code_exts_four_lists_agree` docstring 記錄 `.sh` 曾因新增消費者未接漂移守衛而溜過同步閘

## 規則二(S7–S10)
已讀,無獨立 finding(問題已併入 F1——規則二只認反引號、不認純散文,是 F1 漏擋鏈的一環)。

## 規則三(S11–S15)
### F3 「內容有變」涵蓋摘要與決策,但既有可借用的「正文雜湊」明確只算 body、排除全部 frontmatter
severity: major
blocking: 是 — 若實作者依 PRIOR-ART「不新增依賴、接既有的尺」的措辭直接沿用 `note_body_hash`,規則三會對「只改 summary/decisions、不改 body」的提交完全不觸發——而這正是 `客人端決策層.md` 實際成長的主要方式(KEY 行全部住在 frontmatter 的 `summary:` 區塊)。
1. `note_body_hash`/`_body_hash_of_text` 的 docstring 與實作明寫「回 frontmatter 之外正文的 sha256」,呼叫 `split_frontmatter` 後只對 body 取雜湊,summary 與 decisions 都在 frontmatter、被排除在外。
2. 全庫沒有第二個「summary+決策+正文一起雜湊、其餘 frontmatter 排除」的既有函式可援引,S12 描述的比較邏輯是全新機制,不是重用。
3. PRIOR-ART 段把「about_code 過期守衛的尺」列為零依賴可直接接上的既有件,這個框架性陳述會誤導實作者以為 S12 判準可以照抄同一把尺。
引句:「＝摘要、正文、決策有變；只動 verified_by、plan_refs、related、tags、aliases、updated、status 這些簿記欄位的不算」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/lumos:11219` `note_body_hash` 明寫只雜湊 frontmatter 之外的正文
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/lumos:11235` `_body_hash_of_text` 呼叫 `split_frontmatter` 後只對 `body` 取雜湊,summary/decisions 不在範圍內

## 規則四(S16–S19)
已讀。`0~3 支`、`責任句 ≥N 字含實字`(對照既有 `[manual:]` 的 ≥4 字含實字判準)、`lumos new` 目前只有 `--plan`/`--systems`(`--code`/`--responsibility` 確為新增,非誤稱既存)三項皆已逐一查證屬實,無 finding。規則四本身不強制拆篇(spec 於「範圍外」已自陳),與 F1 是同一個機制縫隙的兩面,不重複計分。

## 規則五(S20–S23)
已讀。「架構對齊」席已是既有派工範本裡的真實席位(`scripts/lumos:7610` 等處 `_rseat("架構對齊", …)`),「只看首筆帳在上線日之後的迴圈、不回溯」與既有 `_CLAUSE_GATE_SINCE`(`scripts/lumos:4388`)同構,兩者皆有堅實既有慣例可循,無 finding。

## 在哪裡檢查(S24–S27)
### F2 「--diff 逐個提交檢查」與本專案既有 --diff 語意(累積整段 range、非逐提交)不一致
severity: major
blocking: 是 — 兩個實作者若照 pre-push 既有慣例(全部既有 `--diff` 消費者都吃單一 range)實作,會直接違反 S3「同一個提交裡順手建家就過」隱含的逐提交粒度判斷;若照 spec 字面做真正逐提交走訪,則是這個 hook 裡從未出現過的新機制,且與同一支 hook 明文寫的「一次推送只算一次波及」成本考量衝突。
1. pre-push 對每個 ref 只算一次 `_range="$_rsha..$_lsha"`(或空樹兜底),`pitfalls --diff`、`code-loop check --diff`、`bound-tests --diff`、`test-layers --diff`、`impact --diff` 全部拿這同一個「整段」range 當單位,沒有任何逐 commit 走訪的既有寫法可援引。
2. `_pitfall_diff_mode`(cmd_pitfalls 的 --diff 分支)把 `diff_range` 當一個 git diff range 字串處理,不解析成多個 commit。
3. pre-push 註解明白寫「一次推送只算一次波及」、「不是便宜的計算」——若 home check 真的逐 commit 重新讀圖譜,會是這支 hook 唯一一個違背此成本原則的檢查,S32 的 2 秒基準也只針對 staged 單一提交量測,未覆蓋多提交推送情境。
引句:「推送前，逐個提交檢查、跳過合併提交」
引句:「推送前掛鉤對這次要推的提交逐個再查一次，接住跳過提交前檢查的」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/hooks/pre-push:179` `_range="$_rsha..$_lsha"` 是整段累積 range,不是逐 commit
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/hooks/pre-push:186` `pitfalls --diff "$_range"` 拿同一個累積 range 當單位,佐證既有慣例非逐提交
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/lumos:18076` `_pitfall_diff_mode` 把 diff_range 當一段 git diff range 解析,無逐 commit 走訪邏輯

## 舊帳(S28–S29)
### F4 三段新健檢提醒未指定插入位置,本專案已有同類事故留在姊妹節點的圖譜記錄裡
severity: major
blocking: 是 — 這是本專案自己已經發生過、且被明文記錄「插入位置本身就是一種改動」的事故形狀;spec 的 `related:` 直接連到記著這個教訓的節點,卻沒有把教訓套用到自己新增的三段。
1. `t_doctor_soft_sections_truncate_by_default` 用固定的 `[S]`/`[E1]` 字串切片計算軟提醒條數;若新三段的輸出被插入這個窗口內(而非窗口之後),會被誤算進既有的「預設只印 3 條」斷言,導致該測試翻紅。
2. spec 本身連結的姊妹節點 `Systems/節點範圍與索引守衛.md` 已明文記載必須插在 `[E3]` 之後、`[H]` 之前,並強調「純新增沒刪行推不出不影響既有行為」——這正是同一個插入-順序風險。
3. S28 只說「健檢多三段提醒」,完全沒有指定這三段該插在既有段落序列的哪個位置,把已知風險留給實作者重新踩一次。
引句:「健檢多三段提醒（不擋、rc 不變、照既有軟提醒的截斷）：沒有家的檔、寫了別人檔名的節點、管超過上限卻沒寫負責範圍的節點」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/test_lumos.py:6116` `sect` 用 `[S]`~`[E1]` 字串切片計數軟提醒,插入該窗口內的新段落會被誤算
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/docs/lumos-toolchain-knowledge/Systems/節點範圍與索引守衛.md:19` 明文記錄「這三段必須排在 [E3] 之後、[H] 之前」的既有教訓,spec 的 `related:` 連到此節點卻未沿用

## 讓規則被看見(S30)
已讀,無 finding。

## 邊界(S31–S32)
已讀。`-z` 分隔本身比本專案既有到處使用的 `core.quotePath=off`(15+ 處)更嚴謹(`-z` 不受 quotePath 設定影響,原生略過 C 式跳脫),兩者不衝突,查不到會導致錯判的具體場景,依抑噪紀律不單獨列 finding。S32 的「60 幾篇節點、2 秒內」量測基準僅覆蓋 `--staged` 單提交情境,多提交推送的效能缺口已併入 F2。

## 範圍外(刻意不做)
已讀,無 finding。「不偵測篇內新舊打架」「不回頭整理別的專案」的排除範圍陳述清楚,且都各自帶 REVISIT 或替代處置。

## 落點
已讀。`Systems/每支檔有家` 目前不存在(已用 `ls docs/lumos-toolchain-knowledge/Systems/` 核對,無同名或近似檔),無節點名衝突;更新目標 `Systems/節點範圍與索引守衛` 存在。無 finding。

## 實務隱患(對照補漏)
- 誤擋:spec 自陳「規則三在一句說明同時講兩支檔時會擋」,已知且有 REVISIT——但該 REVISIT 只量「擋了幾次」,量不到 F1 這種完全不擋的漏擋,兩者是互補風險,spec 只顧了一半。
- 漏擋/繞道:無獨立小節,已併入 F1,最高風險。
- 效能:S32 只覆蓋單提交 staged 場景,多提交推送的效能缺口見 F2,不重複列。
- 繞過(`--no-verify`):已讀,無新 finding——spec 的 S26(推送前逐提交再查)與既有天花板一致,且 `--no-verify` 零留痕是全庫既有已知限制,非本案新增缺口。
- 舊專案升級衝擊:已讀,無新 finding——決策 d3 與既有軟提醒截斷機制(`t_doctor_soft_sections_truncate_by_default`)一致。
- 併發:已讀,無新 finding——檢查只讀不寫,與既有格式檢查擋法邊界劃分清楚。
- 合併/改基底(rename 交互):已讀,無新 finding——改名後舊路徑的殘留反引號提及(F1 場景之外的「舊檔名已死但筆記還在講」)由既有的 `cmd_delguard_check`(code 側刪除傳播守衛)覆蓋,不需要本案重造。
- 兩家一致:已讀,無 finding——不涉各家 hook 協定,陳述正確。
- 不可逆/金流/對外送出:已讀,無 finding——本案只讀圖譜與 git,排除理由成立。

## 驗收怎麼跑
### F7 `-k home` 子集指令會連帶跑到 3 支既有、與本案無關的測試
severity: minor
blocking: 否 — 不會造成錯誤判定,只是驗收子集不夠精準、混進無關輸出,不影響系統本身的擋/放邏輯。
1. `test_lumos.py` 裡已有 `t_runner_isolates_real_home_and_tmp`、`t_hook_cmd_home_resolved`、`t_slim_install_guard_rejects_home_dir` 三支既存測試,函式名含 `home` 但與「每支檔有家」無關,`-k home` 會一併跑到。
2. 其餘列出的關鍵字(`lands_in`/`disposal_gate_requires_landing`/`new_system_with_code`/`precommit_runs_home`/`prepush_runs_home`/`doctor_home`)逐一查證皆無既存同名碰撞。
引句:「子集：`python3 scripts/test_lumos.py -k home`」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/test_lumos.py:339` `t_runner_isolates_real_home_and_tmp`,與本案無關但會被 `-k home` 選中
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/test_lumos.py:24980` `t_slim_install_guard_rejects_home_dir`,同上

## 回頭條件
已讀。兩條 REVISIT 都有明確日期與可執行指令(數治理帳/重看真圖譜分佈),形式合格;唯規則三那條的量測口徑只涵蓋誤擋方向,未涵蓋 F1 描述的漏擋方向,已在上方「實務隱患」段落點出,不重複計分。

## 審計修正紀錄
空(「設計審後補」),無 finding。

總結:最高 severity blocker,blocking 共 6 條
