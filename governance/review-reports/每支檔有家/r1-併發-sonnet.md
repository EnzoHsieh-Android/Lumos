severity: major

## 鏡頭:資源與併發(逐類作答,對應審查要求4)
- 併發寫節點時跑檢查:有洞(見 F1)。
- 大 repo 上跑要多久(--staged):無新增風險(見 F5 說明,已用實測數字佐證 S32 可行)。
- 推送前逐個提交重算歷史圖譜:有洞(見 F2、F3)。
- 跟既有寫入鎖/快取/治理帳寫入打架:無(見 F5)。
- 慢到讓人想跳過:F2、F3 若照established慣例naive實作,會踩到這條。

### F1 規則三/一混用時,別的會談正在搬家的檔會被冤枉沒有家
severity: major
blocking: 是 — 照字面實作,一支檔在「移交新家」的過渡窗口會被判成兩邊都沒有,連跟搬家無關的另一次提交都可能被誤擋。
引句:「檢查只讀不寫；讀到半寫的檔以格式檢查那道既有的擋法為準，這道不另外處理」
1. 這條處置只堵到了「單檔寫到一半被讀到」——但寫入用的是暫存檔+os.replace原子換名,本來就不會有半寫檔案被讀到,這條路徑其實不存在。
2. 真正的洞是「跨檔搬家」:`lumos append`/`lumos remove` 各自獨立上鎖(各自 `with _vault_write_lock(...)`),沒有一個指令能把「從 A 節點拿掉 about_code」跟「加進 B 節點 about_code」包成一次操作。
3. file: `scripts/lumos:11064` 與 `scripts/lumos:11103` 分別是 cmd_append/cmd_remove 各自獨立的 `_vault_write_lock` 範圍,兩者之間沒有共同鎖——這正是 spec 自己「驗收/真圖譜」段落要做的「客人網頁拆四篇」那種操作的典型手法,會製造出檔案暫時兩邊都不是家的窗口,若另一會談此時剛好對同一批檔跑 `home check --staged`,S3/S4 會誤判擋下。

### F2 推送前「逐個提交」重算歷史圖譜完全沒有速度驗收,且既有慣例會導出慢路
severity: major
blocking: 是 — 沒有測到的效能缺口,一旦照 established 寫法實作,會讓推送變慢到符合「決策 d1 想避免的情境」(慢到被 --no-verify 繞過)。
引句:「推送前，逐個提交檢查、跳過合併提交」
1. S32 唯一的速度驗收只量 `--staged`(單一狀態),完全沒有涵蓋 `--diff` 的逐提交模式;規則一的「有沒有家」是全域存在性判定(某檔在全部 Systems 節點裡有沒有任一篇列它),不能只看該次提交改到的節點,必須重建「當時」全部 Systems 節點的 about_code。
2. 本 repo 已有先例明確拒絕批次讀取、選擇單檔 `git show` 包裝(file: `scripts/lumos:13444` 註解「讀那個版本的檔用專案既有的 git show 包裝(第四輪架構席:第三輪另寫了一套 cat-file --batch 解析)」);實測在本 repo 對 64 篇 Systems 節點逐檔 `git show <sha>:<path>` 讀一次歷史狀態耗時約 1.1 秒(64 個獨立 git 子行程),而用 `git cat-file --batch` 批次讀同樣 64 篇只要約 28 毫秒——spec 完全沒指定要走哪一條,若跟著本 repo 既有慣例走(單檔 git show),每個提交要讀 2 次(提交前/提交後狀態)就是約 2.2 秒,10 個提交的推送就吃掉 22 秒以上,疊在既有 pre-push 「輕量閘加總約 13 秒」之上。
3. 既有 `impact --diff`/`code-loop check --diff`/`pitfalls --diff` 全部走「端點對端點」單次計算(`scripts/hooks/pre-push` 裡 `impact_once` 只對整個 range 算一次,不逐提交),本 repo 內找不到任何「逐提交迴圈」的既有寫法可重用(`grep` 全檔 `scripts/lumos` 對 "逐個/per-commit/rev-list.*for" 零命中),S24/S26 要求的模式是全新架構,而 spec 在「不新增依賴」的 PRIOR-ART 裁定裡完全沒提到這個成本差異。

### F3 首推/淺 clone 的既有 fallback 會把「逐個提交」擴大成整段歷史,量級可達近兩千個提交
severity: major
blocking: 是 — 沒有上限或跳過機制,遇到這個既有已存在的 fallback 分支,推送時間會從秒級變成小時級,而 spec 對此完全沒討論。
引句:「推送前掛鉤對這次要推的提交逐個再查一次，接住跳過提交前檢查的」
1. S24/S26 沒有另外定義 `<範圍>` 怎麼算,唯一講得通的接法是插進既有 pre-push hook 本來就在算的 `_range` 變數(S25/S26「提交前掛鉤呼叫它…推送前掛鉤對…逐個再查一次」暗示同一支腳本共用範圍)。
2. 這支既有腳本已經有明確的「保守掃全部引入內容」分支:新 ref(首推)或本地拿不到 remote_sha(淺 clone/force-push 分岔未 fetch)時,`_range` 會退回 `$_EMPTY_TREE..$_lsha`(file: `scripts/hooks/pre-push:172-173` 與 `scripts/hooks/pre-push:176`)。
3. 本 repo 實測 `git rev-list --no-merges "$EMPTY..$HEAD" | wc -l` 結果是 1913(整段非合併提交數);若「逐個提交檢查」套用同一個 fallback 範圍,搭配 F2 量到的每提交秒級成本,首次幫任何消費專案裝上這支 hook 後的下一次「首推」或淺 clone 推送,理論上可能吃掉超過一小時,而三個 POS 消費專案與兩個舊 Android 專案正是 spec 自己點名即將裝上這支 hook 的對象。

### F4 S28 新增的三段健檢沒有指定插入位置,而它更新的姊妹節點有一條剛踩過雷的硬合約要求特定順序
severity: major
blocking: 是 — 照 spec 字面(只講「健檢多三段提醒」)實作,插入位置若沒對齊既有合約,會重演同一份合約自己記錄過的翻紅事故。
引句:「健檢多三段提醒（不擋、rc 不變、照既有軟提醒的截斷）」
1. spec「落點」段明講要更新 `Systems/節點範圍與索引守衛`,但完全沒提這三段新提醒該插在 doctor 輸出的哪個位置。
2. 該節點自己的合約寫死了位置規則且註明是實踩過的教訓:file: `docs/lumos-toolchain-knowledge/Systems/節點範圍與索引守衛.md:23`「★INVARIANT★ 這三段★必須排在 [E3] 之後、[H] 之前★:既有那支「軟段預設只印三條」的測試切的區段是「[S] 到 [E1]」,插在中間會讓它把新段的內容也數進去而翻紅…★插入位置本身就是一種改動★」。
3. 這條合約講的是它自己的三段(S5/S6/S7),但 S28 的三段跟它們是同一份 doctor 輸出裡的相鄰新增內容,若沒沿用一樣的位置紀律,直接復現同一份筆記已經記過的那次翻紅。

### F5 沒有跟既有圖譜寫入鎖/快取/治理帳寫入衝突(無,附理由)
severity: clean
blocking: 否 — 讀寫路徑跟既有機制天然分流,沒有具體失敗場景可指。
引句:「擋下與放行都記進治理帳，閘名登記進已知閘名單」
1. `home check` 自陳只讀不寫,不會呼叫 `cmd_set`/`cmd_append`/`cmd_remove`,因此不會跟 `_vault_write_lock`(file: `scripts/lumos:10895`,鎖鍵是 vault 的 realpath sha256)搶鎖。
2. 治理帳寫入是另一支獨立函式的純 append(file: `scripts/lumos:945` `_append_governance_log`,單一 `open(path,"a")` 逐行 `write`),既有 `doctor --ci`/`anchor approve`/`code-loop pass` 早就共用同一份 `docs/.governance-log.jsonl` 做同款寫入(本 repo 實測該檔已有 780 次提交碰過、目前 31666 行),S27 只是多一個既有模式的呼叫方,沒有新增衝突面。
3. 全圖 about_code 反查已有現成、行程內快取的函式可重用(file: `scripts/lumos:19857` `_ABOUT_COUNTS_CACHE`,「--diff 多檔共用 env 免重掃」),`--staged` 單次檢查若走這條路,S32 的 2 秒預算是可達的(本 repo 469 篇全圖 `load_vault` 實測僅 0.11 秒、`Env()` 建構共 0.19 秒)。

## 逐節閱讀確認(資源與併發鏡頭下無額外 finding 的段落)
- 為什麼(來源)/世界上怎麼做的(PRIOR-ART):已讀,無 finding——不涉及執行期資源。
- 名詞:已讀,無 finding。
- 規則四(S16-S19,上限與 responsibility):已讀,無 finding——上限管的是單節點 about_code 條數,不影響本鏡頭關注的讀取成本。
- 規則五(S20-S23,設計審流程):已讀,無 finding——發生在設計審迴圈而非提交/推送時。
- 讓規則被看見(S30):已讀,無 finding。
- 邊界 S31(路徑編碼):已讀,無 finding。
- 範圍外/回頭條件/審計修正紀錄:已讀,無 finding(審計修正紀錄該段目前空白,無內容可核)。

## LUMOS-SPEC 節點合約檢查
LUMOS-SPEC 指向計劃節點本身(`Projects/每支檔有家_計劃.md`),核對後與 repo 內版本逐字相同、無漂移。該計劃另外明講會更新的合約節點是 `Systems/節點範圍與索引守衛`——判定:**會影響**,已在 F4 具體列出(插入順序合約沒被 spec 繼承)。

總結:最高 severity major,blocking 共 4 條
