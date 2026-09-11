severity: major

- 開頭 frontmatter／決策 d1、d2、d3、d5：已讀,無 finding——d3→d4 的取代關係(valid:false/superseded_by/ended)寫法正確;d5 的推送前整段比、新分支起點邏輯與 scripts/hooks/pre-push 現況核對一致(見下方機械重現)。決策 d4 見 F1。
- 為什麼(這批的來源)、世界上怎麼做的(PRIOR-ART):已讀,無 finding——與第 1 輪回滾席已核對過的數字(客人端決策層 about_code=1、mOrangePos/Citrus_KDS 0/40、0/30)這輪重跑 `grep -rl "^about_code:"` 仍為 0/40、0/30,未變動,無新落差。
- 名詞段(需要家的檔、測試檔、node_home.ignore、家、別人的檔、內容有變、讀哪個版本、新違規):已讀,無 finding——對照 scripts/lumos 的 `_nodehome_required`/`_nodehome_homes`/`_nodehome_config`/`_nodehome_is_test` 等函式,定義與實作一致;stale 仍算家、planned/deferred/rejected/superseded 不算,已用真實測試場景複驗(見 F1 之外的驗證)。

### F1 決策 d4 宣稱「兩個舊 Android 專案不會每個提交都擋」與規則一 [S3] 的實際行為矛盾——只要新增一支沒家的檔就擋,不論有沒有動圖譜
severity: major
blocking: 是 — 決策 d4 是這次修訂拿來說服「安全可以推」的理由,若這句話對實際最常見的提交類型(單純加新檔,不碰圖譜)是假的,會讓人誤判舊專案升級的衝擊面、做出錯的推行決定。
引句:「兩個舊 Android 專案不會每個提交都擋」
file: `docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:37` d4 的 why_chosen,只用「沒寫說明的提交照舊只提醒」來支持這句話——但「沒寫說明只提醒」是 [S5] 的範圍(改到*既有*沒家的舊檔),完全不覆蓋 [S3](新增檔案本身沒家)。
file: `scripts/lumos:17750-17752` `_nodehome_evaluate` 的 [S3] 判定對「這次新增且需要家」的檔一律擋,沒有「有沒有動圖譜」這個條件。
我在 /tmp 複製 mOrangePos 後實測:只新增一支全新 `.kt` 檔(未動任何節點、未寫任何說明)`git add` 後執行 `lumos home check --staged`,結果 rc=1、訊息「擋下:這次提交有 1 條『每支檔有家』的新違規」。這正是 d3 想避免、d4 聲稱已解決的那種「每個提交都擋」,只是觸發規則從 [S13b] 換成了 [S3]——對一個仍在正常開發(常態性新增檔案)的舊 Android 專案,這條路徑完全沒被 d3/d4 的討論涵蓋,實務隱患段「舊專案升級的衝擊」也只引 [S5]/[S13b] 兩條、沒提到 [S3]。

### F2 [S39] 的繞過/舊帳分群只做了「沒有家的檔」一種,「別人的檔」與「超過上限沒寫負責範圍」兩種舊帳仍跟第 1 輪回滾席 F2 一樣分不出繞過
severity: major
blocking: 是 — 第 1 輪 F2 的判準就是「沒人能事後判斷這道閘是在擋還是被繞過很久了」,這條路徑對 [S9]/[S18] 兩類擋下規則原封不動地留著,只解了三分之一。
引句:「那段分兩群印:守衛上線之後才新增的」
file: `scripts/lumos:17889-17925` `_nodehome_ledger` 只對 `homeless` 計算 `bypassed`/`legacy` 兩群(用 `after` 集合比對上線點);同一函式裡緊接著算的 `foreign`(對應健檢 [S9] 段)與 `over`(對應 [S10] 段)完全沒有套用 `after` 過濾或任何繞過分群邏輯。
file: `scripts/lumos:2125-2144` 健檢 [S9]、[S10] 兩段(`section("S9", ...)`/`section("S10", ...)`)直接印 `_nhl["foreign"]`/`_nhl["over"]`,沒有像 [S8] 段那樣分「上線後」與「舊帳」兩群。
測試面同樣只覆蓋 [S8]:`scripts/test_lumos.py:36327` `t_doctor_nodehome_splits_bypassed_from_legacy` 只斷言 `[S8]` 區塊的分群,沒有對應 [S9]/[S10] 的繞過分群測試——不是漏測,是規則本身沒做。

### F3 [S27] 承諾留給回頭條件用的(檔,節點)配對,寫進了治理帳但 `lumos gov` 讀不出來
severity: major
blocking: 是 — 回頭條件段 REVISIT:2026-10-11 明講要「用擋下事件的(檔,節點)配對列出那批 about_code 給人逐項判」,但人唯一會用的唯讀治理帳指令看不到這欄,執行 REVISIT 時會撲空、只能繞過工具手剖 jsonl。
引句:「擋下事件的（檔，節點）配對留著，給回頭條件分析」
file: `scripts/lumos:17994` `cmd_home_check` 寫入 `extra={"pairs": [...]}`;`scripts/lumos:920` `_gate_event` 的 `ev.update(extra)` 把 `pairs` 併進事件 JSON 的最上層鍵。
file: `scripts/lumos:4991-4999` `cmd_gov` 讀 `.governance-log.jsonl` 的 mapper 只抓 ts/commit/gate/kind/hard/nodes/detail/token/dispositions/candidates/recall_miss,沒有 `pairs`。
我在 /tmp 的 mOrangePos клон上實測:製造一筆 `nodehome-check`/`blocked` 事件後,`tail docs/.governance-log.jsonl` 能看到 `"pairs": [["app/.../Constants.kt", "Systems/品項語系顯示_菜單側.md"], ...]`,但 `lumos gov --full` 只印出「品項語系顯示_菜單側,constants  這次提交:新違規 2 條」,配對資訊完全不見。`scripts/test_lumos.py:36259` 那條驗收也只讀原始 jsonl 檔驗 `pairs`,沒有一條測試驗過 `lumos gov` 能不能查到它。

- 規則一其餘([S1][S2][S4][S5][S6][S34]):已讀,無 finding(除 F1)——[S4] 的 stale 排除已用真實測試 `t_nodehome_check_blocks_home_removal` 案例③複核,rc0 正確;[S34] 出生規則與 [S3] 是同一段程式碼,行為一致沒有另外落差。
- 規則二([S7]–[S10]):已讀,無 finding——[S9] 只在 Systems 節點正文新增反引號時觸發,不影響一般改碼提交,跟 F1 講的常態新增檔案是不同觸發面。
- 規則三([S11]–[S15][S35][S36]):已讀,無 finding(除 F1/F2 已涵蓋部分)——`t_nodehome_route_skips_docs_only_commit`、`t_nodehome_touched_legacy_homeless_warns_without_write_back` 兩支測試通過,跟名詞段「讀哪個版本只讀索引」一致。
- 規則四([S16]–[S19]):已讀,無 finding——mOrangePos/Citrus_KDS 因 about_code 全空,`cnt_now` 恆為 0,不會觸發 [S18],跟兩專案實測「0 支管超過上限」吻合。
- 規則五([S20]–[S23]):已讀,無 finding——不在回滾鏡頭範圍內,未發現跟升級/退場相關的落差。
- 在哪裡檢查([S24][S25][S26][S37][S38]):已讀,無 finding(除 F3 涵蓋 [S27])——`node_home.gate` 三值、壞值退回 on、健檢開頭印警示,均已用 `t_nodehome_gate_switch` 與 `scripts/lumos:976-978` 核對通過;pre-push 的新分支起點與上線點夾取邏輯(`scripts/hooks/pre-push:183-208`、`scripts/lumos:17683-17692`)跟 [S26] 文字一致。
- 舊帳段([S28][S29]):已讀,無 finding(除 F2 涵蓋 [S39])——插入位置核對 `scripts/lumos` 的 `section(...)` 呼叫順序,[S7]→[S8]→[S9]→[S10]→[H] 確實排在 `[S]`(1355 行)…`[E1]`(1737 行)這個舊測試窗口之後,不會誤觸 `t_doctor_soft_sections_truncate_by_default`。
- 讓規則被看見([S30])、邊界([S31][S32][S40]):已讀,無 finding——不在回滾鏡頭核心關切內,未發現升級/退場相關問題。
- 範圍外、落點:已讀,無 finding——範圍外段「不回頭整理別的專案」那段隱含的安全感正是 F1 指出的落差來源,已在 F1 說明,不重複列。
- 驗收怎麼跑、合約候選、審計修正紀錄:已讀,無 finding。

LUMOS-SPEC 落點檢查:這次派工詞的 LUMOS-SPEC 標記尾端沒有附加節點名(跟第 1 輪回滾席報告對到 `Systems/節點範圍與索引守衛` 不同,那應是當輪派工詞另外指定的),本輪按規則不適用「逐條判會不會破壞該節點合約」。仍順手覆核一次:計劃「範圍外」段保留 `Systems/節點範圍與索引守衛` 的 ★INVARIANT★(範圍判準只看合約條數、不看檔數)不變,規則四是另立的獨立判準,不影響該節點合約。

## r1 回滾席發現六組,這輪核對結果

- G24([S37] 專案開關):**修到**——`node_home.gate` on/warn/off 已實作,`t_nodehome_gate_switch` 5 案例全過,健檢開頭會印警示行。
- G25([S39] 繞過分群):**部分修到、留新洞**——只對「沒有家的檔」分了繞過/舊帳兩群,「別人的檔」「超過上限沒責任」兩類舊帳仍跟原 F2 一樣分不出繞過(見 F2)。
- G17([S4]/[S12] status 矛盾):**修到**——stale 明確不觸發 [S4],用測試案例③複核 rc0。
- G5(「同一份清單」名不符實):**修到**——`_NODEHOME_CODE_EXTS` 具名常數已接進 `t_code_exts_four_lists_agree`,五份互相比對,測試通過。
- G4(doctor 插入位置未定):**修到**——[S28] 寫死位置且跟 `[S]`–`[E1]` 舊測試窗口核對不衝突。
- G26(規則撤回無清理路徑):**部分修到、留新洞**——(檔,節點)配對確實寫進治理帳,但唯一的讀取指令 `lumos gov` 不會顯示它,回頭條件執行時會撲空(見 F3)。

## 實務隱患鏡頭(回滾與升級衝擊)

- **誤擋(升級當下)**:有——F1;新增檔案這個最常見的日常提交類型,在 0% about_code 覆蓋率的舊專案上會被 [S3] 立即擋,決策 d4 的安全宣稱不成立。
- **繞過偵測不完整**:有——F2;`--no-verify` 對 [S9]/[S18] 兩類擋下規則繞過後,健檢永遠把它們跟舊帳混在一起印,無法像 [S8] 那樣抓出「上線後才新增卻沒家」。
- **開關與逃生路**:無新 finding——`node_home.gate` on/warn/off 三態、壞值退回 on、健檢開頭可見,三個問法(退得掉嗎/只能 --no-verify 嗎/推送前又擋一次怎麼辦)都有對應且已用測試核過。
- **規則撤回的資料可用性**:有——F3;寫進帳的資料因為讀取工具沒接,實質上不可查詢,回頭條件執行會落空。
- **升級當下的規模感**:無新 finding(數字已機械量出,供編排者參考)——mOrangePos 實測:337 支沒家的舊檔、29 篇節點寫了別人家的檔、0 篇超過上限;Citrus_KDS:81 支沒家、18 篇寫別人家、0 篇超過上限;兩者都是 `lumos update` 後第一次 `lumos doctor` 就會印出的既有落差,不是這次修訂造成的新增風險。
- **不可逆、金流、對外寄送**:無——這道閘只讀圖譜與 git、只往本機治理帳附加事件,不寫正式環境、不發外部請求,跟計劃本文的排除一致。

總結:最高 severity major,blocking 共 3 條
