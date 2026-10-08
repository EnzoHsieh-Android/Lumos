severity: minor

## 逐條裁定

### 〈範圍〉
- 共用判定函式(條件 1–4+淺 clone+git 出錯):已實作。`_merge_side_start`(終點==目標、全零/空樹/找不到不認)、`_codeloop_merge_side`(rev-list --parents 恰 3 欄=兩個母;p1==start;`merge-base --is-ancestor p1 p2`;條件 4 以 `_codeloop_record_valid_ex(p2, 目標)` 判,實查該函式本體用 `git diff --raw --no-renames -z` 並含簿記資料夾放程式照算程式,與 spec「沿用那套」一致;`_git_is_shallow` 回「歷史不全」)。
- 讀帳函式:已實作。`_codeloop_ledger_events` 抽共用篩選;`_codeloop_merge_side_record` 用 `git rev-list --first-parent -n 20 p2`、`git show p2:docs/.governance-log.jsonl`(binary 讀、合併提交本身的行不算)、不看分支名、由近到遠逐筆驗 ①`is-ancestor p1 rec`(含等於)②`_codeloop_record_valid_ex(rec, p2, 剩餘時間)`;判不了視為不有效;帳本以 cache 只讀一次。
- 審查留痕那關:已實作。`_codeloop_review_block` 在「紀錄無效」與「無留痕」兩條路都接,位於 `_codeloop_marker_skipped` 之前;放行理由含「合併提交:合進來那一側的留痕(passed@sha,分支 …)」;認不到把原因接在原 reason 後。
- 表態那關:已實作。`_disp_record_for` 接「沒有」與「過期」兩點(ok 為假即走 merge_side),kind=("dispositions",),有效性對 p2;適用題仍用目標範圍算。
- 原始起點先存:已實作(`raw_range = diff_range` 在 `_codeloop_guard_verdict` 開頭、改寫之前)。
- 時間:已實作 `_DISP_BUDGET` 起算自己的 deadline(cache["deadline"]),每次 git 用剩餘時間;逾時不認。文案見 F1。
- 不做項(章魚、squash、改 CI 腳本/掛鉤範圍算法、簽章):已遵守,diff 未動這些。

### [S1] 實作
已實作(含:放行寫明合進來那側、目標分支有過期紀錄仍放行、第一個母≠起點/全零、沒跟上主線、手改合併結果(含退修補、刪檔,由條件 4 以 `--no-renames` 覆蓋)、三個母(`len(shas)!=3`)、無紀錄/紀錄後改程式、紀錄只在合併提交新帳本行(讀 p2 樹)、還原提交借舊紀錄(①含第一個母)、中文檔名(valid_ex 的 `-z`))。實作面無縮水。

### [S2] 實作
已實作(兩個擋下點、kind=dispositions、對 p2 驗、第一個母≠起點與合進來那側無表態照舊擋)。

### 測試格對照
t_codeloop_check_merge_side_pass(spec 未編號,以實際格 ①–⑨ 對 S1 子情境):
- ① 乾淨放行 ✓;② 目標有過期紀錄 ✓;③ 手改合併結果 ✓;④ 未審分支擺第一個母 ✓;⑤ 沒跟上主線 ✓;⑥ 還原提交+舊紀錄(記在別的分支名下) ✓;⑦ 無紀錄 ✓;⑧ 紀錄後改程式 ✓;⑨ 紀錄只在合併提交新帳本行 ✓。
- S1 列了但沒有測試格:三個母、合併時刪檔(改名偵測)、中文檔名簿記差異、起點全零、skip 類紀錄、淺 clone(spec 守衛面寫「每個條件各有一格測試證明少一個就照舊擋」)。
t_codeloop_check_merge_side_dispositions:① 合進來那側有表態、主線無 ✓;② 合進來那側沒表態 ✓;③ 第一個母非起點 ✓。S2 括號「或有一筆過期表態都一樣」沒有測試格。

## F1 超時文案未逐字
severity: minor
blocking: 否
spec:〈範圍〉「超過期限 → 不認、照舊擋並講「時間不夠判不完」」。diff 的文案是「git 出錯或時間用完」「時間用完,判不完合進來那一側的紀錄」,沒有「時間不夠判不完」;且條件 4 由 valid_ex 判不了(逾時)時,訊息被包成「合併結果跟合進來那一側 … 不只差簿記檔(合併時動過程式),不認:…」,把逾時誤講成動過程式(守衛行為仍是不認、照舊擋,只有說明精度)。
引句:「合進來那一側沒有包含主線頂端、而且之後只動簿記檔的紀錄」

## F2 測試格比 spec 列舉少
severity: minor
blocking: 否
spec:[S1]「三個母、…合併時刪檔(改名偵測不得藏住)…起點全零…中文檔名的簿記檔差異 應 …」與 [S2]「目標分支沒有表態、或有一筆過期表態都一樣」、〈實務隱患〉「每個條件各有一格測試證明少一個就照舊擋」。diff 的兩支測試未含這幾格(實作碼本身有對應分支)。
引句:「print("  ✓ t_codeloop_check_merge_side_pass")」

## 四類清單
- 已實作:〈範圍〉全部做項、[S1]、[S2] 的實作面。
- 縮水:F1(逾時文案)、F2(測試格少於 spec 列舉)。
- 多做:僅一處極小行為變更——共用篩選 `_codeloop_ledger_events` 新增 `isinstance(ev, dict)` 與 `head_sha` 須為字串的條件,同時套到既有兩支讀帳(spec 只說抽共用、不改篩選語意);實務上無影響,不列 finding。其餘為重構(`_codeloop_review_block`、`_disp_record_for` 抽出)與測試。
- 未實作:無。
- ⚠ 交編排者:無。

縮水+未實作共 2 條
