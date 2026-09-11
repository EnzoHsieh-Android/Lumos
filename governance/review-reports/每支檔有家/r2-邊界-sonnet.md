severity: major

## 逐節審查

### frontmatter / 決策 d1–d5
已讀，無 finding。d4 取代 d3、d5 新增，敘述與正文 [S13b][S26] 一致；decided/valid/superseded_by 欄位形式合法。

### 為什麼（這批的來源）
已讀，無 finding（r1 已抽樣核對過，本輪內容未變）。

### 世界上怎麼做的
已讀，無 finding。

### 名詞
已讀。「家」段落「比對用 about_code 既有的比對鍵（解連結、大小寫與 Unicode 寫法照磁碟）」的宣稱本身屬實，但見 F1——這條比對鍵的「照磁碟」跟同段「讀哪個版本」承諾的「推送前讀範圍兩端的提交、不讀工作目錄」在 `--diff` 多提交範圍時會打架。其餘定義（需要家的檔、測試檔、node_home.ignore、別人的檔、內容有變、新違規）逐一查證，無新 finding。

### 規則一：每支檔都要有家（S1–S6, S34）
- [S1] 五份清單一致：`_NODEHOME_CODE_EXTS`（`scripts/lumos:17356`）與 `t_code_exts_four_lists_agree` 已查證存在且接進去。
- [S34] 新專案出生：以空樹 diff 測試過（我方 `_lens_full_sha` 對無 HEAD 的首次提交回 None，`_nodehome_changes` 正確落到 `_EMPTY_TREE_SHA`），行為與敘述一致。
- [S40] 連結檔/子模組：`_nodehome_list`（`scripts/lumos:17470`）只收 `100644`/`100755` 模式，已修好 r1 F6/G13。
- 其餘無新 finding。

### 規則二：節點只准用反引號寫自己家的檔（S7–S10）
已讀，無新 finding；[S7] 重用 `_impact_reverse_lookup` 屬實。

### 規則三：寫回要落在改動檔的家（S11–S15, S35, S36）
- [S15] 「提交前不再呼叫反引號種子那一套」屬實（Gate 3 註解已改）；但見 F2——同一種反引號＋文字相似度算法在推送端另一條路徑（pre-push 的 `sync_nudge`）原封不動地活著，spec 沒有交代。
- 其餘（S11–S14, S35, S36）無新 finding。

### 規則四：每篇要寫負責範圍（S16–S19）
已讀。[S17]/[S18] 與段落標題的矛盾（r1 F4/G9）已修：標題改成「新開的一律要，舊篇管超過上限才要」，[S17][S18] 現在互不矛盾。`_nodehome_config`（`scripts/lumos:17375`）對 `max_files` 的 bool/非整數/<1 全擋、`ignore` 非清單/非字串項逐項略過並出聲，均與 r1 F7/F9（G7/G8）折入的敘述一致；[S18]「只數還存在的檔」在 `_nodehome_evaluate`（`scripts/lumos:17698` 一帶，`cnt_now = len({k for k in ownN.get(rel, set()) if k in N.files})`）確實過濾掉已刪檔。無新 finding。

### 規則五：規格寫明落點（S20–S23）
已讀。[S21] 的生效日常數 `_LANDING_GATE_SINCE = "2026-09-12T00:00:00+08:00"`（`scripts/lumos:14988`）與正文一致；[S22] `_nodehome_landing_sizes`（`scripts/lumos:22414`）確實印出掛幾份計劃/幾行 KEY/幾條合約/管幾支檔/有沒有寫負責範圍；[S23] 派工範本「## 7.6」節確有「落點合不合理」一題（`t_nodehome_rules_in_hint_skill_and_discipline` 驗到）。無新 finding。

### 在哪裡檢查（S24–S27, S37, S38）
- [S25] Gate 佈線順序（r1 F1/G10）已修：`scripts/hooks/pre-commit:115-125` 的 Gate H 確實排在 Gate 2/3（改程式沒動圖譜）之前。
- [S26] 新分支起點（r1 F3/G3）已修：`scripts/hooks/pre-push:178-193` 用 `git rev-list --topo-order --reverse "$_lsha" --not --remotes` 取代空樹回退，`_nodehome_clamp_base`（`scripts/lumos:17683`）補了上線點夾取。機制本身查證屬實，**但見 F1**——這個「整段比多提交」的模型正是 F1 誤擋的觸發條件，是 d5 這個補丁本身帶出的新洞。
- [S24][S27][S37][S38] 無新 finding。

### 舊帳（只提醒）（S28–S29, S39）
已讀，無新 finding。

### 讓規則被看見（S30）
已讀，無 finding。`t_nodehome_rules_in_hint_skill_and_discipline` 列的五處（教寫節點的說明、節點還原 SOP 快查表/完整版、紀律區塊範本、架構對齊派工範本）與開新節點提示，逐一 grep 確認都含「每支檔有家」字樣，屬實。

### 邊界（S31, S32, S40）
- [S31] 已用 `/tmp` 實驗驗證：非 UTF-8 檔名不會讓 `lumos home check` 崩潰（Python `sys.stderr` 預設 `errors=backslashreplace`，不是 strict），也確實只提醒不擋——r1 F5/G12 修正屬實，且比我原本擔心的還安全。
- [S32] 效能宣稱（60 幾篇節點、staged 一次/diff 十個提交一次、各 2 秒內）沒有涵蓋「幾百支檔的單一大提交」在多節點都改動時的 `_nodehome_refs` 全文本掃描成本；抑噪紀律下沒有具體翻紅場景，不獨立開 finding。
- [S40] 已於規則一小節查證。

### 範圍外（刻意不做）
已讀，無 finding。

### 落點
已讀，無 finding。`Systems/每支檔有家.md`、`Systems/design-loop.md`、`Systems/節點範圍與索引守衛.md` 三個落點節點均已存在（實作已完成），`Systems/每支檔有家.md` 的 `about_code`/`responsibility`/摘要與計劃「落點」段描述一致。

### 實務隱患（spec 自己的段落）
已讀。八類（誤擋/漏擋/變慢/繞過/舊專案衝擊/併發/合併改基底/不可逆）沒有一類提到 F2 講的「push 端反引號種子點名沒有被這次改動觸及」——這是遺漏，見 F2。

### 驗收怎麼跑 / 回頭條件 / 審計修正紀錄
已讀，無 finding。四條回頭條件都帶 `REVISIT:2026-10-11` 與具體要數的數字，符合鐵則四。

### LUMOS-SPEC 節點比對
LUMOS-SPEC 指到的節點檔（`docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md`）與本次被審的 spec 檔案逐位元組相同（`diff` 確認 IDENTICAL）——沒有另一篇「已宣稱行為/合約」的既有節點需要比對；判「不影響」：這篇本身就是待審的計劃，不是被波及的既有系統。

---

## Findings

### F1 about_code 的比對鍵讀的是呼叫當下的磁碟，不是被比對那一側的提交快照，推送端整段比會誤判「家」
severity: major
blocking: 是 — 對照計劃自己承諾的「同一個提交裡順手建家就過」，實測會把同一提交內完成改名並登記 about_code 的檔案判成沒家而擋下推送。
引句:「同一個提交裡順手建家就過」
file: `scripts/lumos:17613-17625` `_nodehome_homes(repo_root, side)` 對 B、N 兩側一律呼叫同一支 `_about_code_key(Path(repo_root), v)`（`scripts/lumos:11062`），而後者用 `Path.resolve()`＋`os.listdir` 讀「呼叫當下」的真實磁碟拼法，不吃 `side` 是哪個提交；這跟「家」名詞段同一段裡「讀哪個版本」講的「提交前不讀工作目錄…推送前讀範圍兩端的提交」不是同一套規則，S38 只管到「讀筆記/程式檔內容」，沒管到「about_code 比對鍵怎麼算」。
file: 已在 `/tmp` 自建 repo 重現（未動任何 wt-nodehome/消費專案檔案）：commit A 有 `src/foo.py`（about_code 同名），用純 git 物件操作（不 checkout）造出 commit B 把它改名成 `src/Foo.py` 並在同一提交把 about_code 也改成 `src/Foo.py`；工作目錄仍停在 A（磁碟實體是小寫 foo.py）時跑 `lumos home check --diff A..B`，結果把 `src/Foo.py` 判成「這幾支程式檔沒有家」而 rc1 擋下。
⚠ 重現用的是「推送時 checkout 的分支不是被推那個 ref」（例如在 main 上 `git push origin feature-x`、或一次推多個 ref 只有一個跟目前 checkout 一致）——這是決策 d5 把單提交比改成整段比之後才變得容易踩到的觸發條件（多提交範圍內只要有一次改名/大小寫變動，就可能跟現場 checkout 對不上）；是否也要覆蓋「checkout 剛好等於 tip 但工作目錄有未提交改動」這種更弱的版本，交編排者判斷。

### F2 push 端仍在用 spec 自己點名的「反引號種子」演算法做同一種點名，沒有被這次改動觸及也沒有被揭露
severity: major
blocking: 是 — 「為什麼」段第 3 條把「以反引號命中的節點為種子…工具在把人往那篇推」列為根因之一，[S15] 只講「提交前掛鉤不再呼叫它」，但同一套機制在推送端另一條路徑上原封不動繼續運作，八類實務隱患、範圍外、回頭條件都沒有一處提到這件事。
引句:「提交前掛鉤不再呼叫它」
file: `scripts/hooks/pre-push:67-70` `sync_nudge()` 呼叫 `impact --sync-only --from-json`，其資料來自 `impact_once()`（`scripts/hooks/pre-push:44-56`）跑的 `impact --diff <range> --sync-check --json`；`scripts/lumos:21357-21367` 顯示 `sync_check` 的 `missing` 清單就是拿 `cmd_impact` 的 ranked 結果（固定席直查相依、自由席靠 `_impact_reverse_lookup` 的反引號/裸檔名種子＋連結擴散＋文字相似度排序，`scripts/lumos:20360` 起）去跟「這次動過的節點」做差集——跟「為什麼」第 3 條描述的演算法是同一套，推送時仍會把使用者導向被反引號提到最多次的大雜燴節點。

## 實務隱患鏡頭（邊界與可執行性）

- **push 端與 commit 端點名機制不同步**：有隱患，見 F2——[S15] 只換掉 commit 端，push 端的舊機制沒被同一份 spec 檢視過。
- **多提交範圍內的改名/大小寫變動**：有隱患，見 F1——decision d5 把比對單位從「單一提交」擴大成「整段範圍」之後，範圍內任何一次改名都可能讓比對鍵跟現場 checkout 對不上。
- **併發（另一工作目錄的會談在改磁碟）**：有隱患，跟 F1 同一個根因——`_about_code_key` 讀的是呼叫當下的磁碟，S38「別人還沒加進索引的東西讀不到」這句話對 about_code 比對鍵不成立，只對筆記/程式檔內容成立；沒有獨立開 finding，因為根因與修法跟 F1 相同。
- **非 UTF-8 檔名**：無新隱患——已用 `/tmp` 實驗驗證印出提醒訊息不會讓 Python 因編碼例外而中斷（stderr 預設 `errors=backslashreplace`）。
- **連結檔與子模組**：無新隱患——`_nodehome_list` 用索引/提交樹的檔案模式過濾，不靠副檔名判斷，已查證。
- **剛接上 lumos 的專案（全部新增）**：無新隱患——S34 與 `_nodehome_changes`/`_lens_full_sha` 對無 HEAD 的首個提交行為一致，走空樹 diff。
- **一次提交幾百支檔（訊息可讀性）**：無新隱患——`_NODEHOME_MSG_CAP=10` 與 r1 修正的分組截斷邏輯查證正確。
- **大小寫只差一個字（非 push 整段比場景）**：跟 F1 同根因；staged 模式下磁碟通常跟索引一致，實際觸發機率遠低於 push 整段比，併入 F1 不單獨開。
- **git 設定 core.quotePath**：無新隱患——`_nodehome_git` 全程用 `-z`，git 對 `-z` 輸出一律吐原始位元組、不受 `core.quotePath` 影響。
- **合併、改基底、cherry-pick**：無新隱患——MERGE_HEAD 偵測與 [S26] 整段比查證行為與敘述一致；改基底/cherry-pick 產生的都是一般提交，走一般路徑。
- **lumos 來源 repo 自己**：無新隱患——`_is_toolchain_repo` 在 `cmd_home_check` 與 `_nodehome_ledger` 兩處都正確跳過 vendored 檔案豁免。
- **不可逆、金流、對外寄送**：不碰，跟 spec 自己「實務隱患」段的結論一致，本輪查證沒有推翻。

總結：最高 severity major，blocking 共 2 條
