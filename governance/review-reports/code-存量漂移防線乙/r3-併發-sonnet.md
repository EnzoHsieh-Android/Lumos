severity: major

## F1 不帶路徑條件的候選篩選對「終點全文串接字串」逐行跑正則,迴圈裡完全不看預算
severity: major
blocking: 是 — 預算是這份設計明訂的硬約束(scan 與 check 都傳 deadline),這一段超出後沒有任何機制擋,且成本隨條件行數線性長
引句:「cand = _drift_probe_is_candidate(pr["conds"], ch, pre, tenv, _tip_text) if old else True」

1. 這次推送改到大檔(例:scripts/lumos 2.1MB 加 scripts/test_lumos.py 3.4MB,兩支都只改一行),`_tip_text` 把兩支全文用換行串成約 4.5M 字元的單一字串(只串一次,memo 有效)。
2. `_drift_probe_cond_candidate` 對每一條「不帶路徑的 symbol/test」條件跑 `re.search(rf"(?<![\w]){re.escape(name)}(?![\w])", txt)`。樣式開頭是 lookbehind,引擎無法用字面前綴加速;名稱沒出現在全文時要掃完整個字串。實測單次 0.10 秒(名稱有出現時是微秒級,所以只有「這次推送沒碰到的名稱」這種最常見的非候選情形才貴)。
3. `_drift_probe_candidates` 的 for 迴圈每一行只在「判不了」的訊息裡呼叫 out(),迴圈本身、`_drift_probe_is_candidate`、`_drift_probe_cond_candidate` 都不看預算。預算只在迴圈之後的 todo 迴圈才看。
4. 實測(臨時 repo,兩支大檔各改一行,起點有同一條 → old=True,條件名稱都不在全文;直接呼叫 `_drift_probe_candidates`,deadline 設 2 秒):
   - 10 行:elapsed 1.03 秒
   - 100 行:elapsed 10.19 秒,預算 2 秒,todo 0、unknown 0(沒有任何一行被標成超過預算,靜默超支後結果照樣當成「不是候選」)
   重現腳本:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/bench.py(參數 = 行數,臨時 repo 在其上層 tmp 目錄)。
5. 後果:600 行左右的圖譜(條件行多、名稱都不在這次改動裡)單這一段就超過預設 60 秒預算,pre-push 多等一分鐘以上,而且超支之後 `_out()` 才為真、後面每一行變成「超過預算」判不了——前面的候選篩選卻不受限。舊版篩選對「新增行」小字串跑正則,沒有這個量級。
6. 這是修正差異新引入的成本(舊版 added_text 只有新增行)。

## F2 NFD 重讀用原本的整段逾時,不是扣掉第一次讀花的時間
severity: minor
blocking: 否 — 只在有讀不到的非 NFC 路徑且 git 已接近逾時時才超支,最壞約兩倍預算,不改變判定結果
引句:「again = _nodehome_cat_blobs(root, [f"{where}:{unicodedata.normalize('NFD', paths[i])}" for i in retry],」

1. `_drift_cat_nfc` 的兩次 `_nodehome_cat_blobs` 都傳同一個 `timeout`(呼叫端在第一次讀之前算好的剩餘時間)。
2. 第一次讀花了 T(接近 timeout),路徑清單裡有轉成 NFD 後不同、且第一次讀成 None 的路徑,第二次又拿到完整 timeout,總共可用到 2×timeout,超出 `deadline`。⚠ 未實測(需要讓 git 慢到接近逾時,本機造不出);一般全 ASCII 路徑不會進這條。

## 已看,無 finding
- prefetch 是不是真的一個行程:實測(臨時 repo,5 支 ASCII 檔加 1 支中文+é 路徑檔,6 條帶路徑條件)prefetch 只呼叫 `_nodehome_cat_blobs` 一次(6 個規格),之後逐條 `one()` 評估呼叫次數不變,已看,無 finding。
- NFD 重讀在全 ASCII 路徑不多開行程:同上實測,`retry` 為空、只有一次呼叫;`unicodedata.normalize("NFD", p) != p` 過濾掉不會分解的路徑(含一般 CJK),已看,無 finding。
- `_NotelinesNet`:一次推送最多跑一次 diff(`_m` 在第一次 lines() 就設成 {},失敗時也設 {} 並記 failed,不會重跑);`_notelines_new` 迴圈結束後 `net.failed` 整次回 None,兩個呼叫端(23988 附近 staged 路徑不建 net、range 路徑建)一致。git 失敗傳遞正確。相較舊版(keep_other 就無條件多一次整圖譜範圍 diff)是改善;實測從空樹 diff 整個圖譜 0.17 秒。已看,無 finding。
- 讀檔失敗 / git 失敗 / 部分批次讀失敗:`texts()` 讀不了回 None → `_tip_text` memo None → 候選判 None → unknown(判不了);`one()` 在 `_read` 為 False 時短路、不碰 `_text[path]`;`corpus()` 在 `_read` 成功後才取 `_text[p]`,鍵一定在;樹上有、內容讀 None 的檔進 `_unread`,沒找到定義才判不了。皆是判不了而不是不成立。已看,無 finding。
- `_DriftProbeTree._read` disk 與 git 兩條:兩條都在進入前與(disk)每支檔前看 `_over()`;git 條用剩餘時間。已看,無 finding。
- `_drift_probe_prefetch`、`_drift_probe_scan` 的 prefetch:scan 在 `not _over()` 才做,check 在 `todo and not _out()` 才做;讀不了不記錄,之後逐條各自再試會失敗得很快(git 失敗)或因預算而 False。已看,無 finding。
- 順帶:tip 樹在 `code_touched` 非空時提前列(`ls-tree` 有 `_DRIFT_LS_CACHE` 記憶,之後判定要用同一份),不多算,已看,無 finding。

最嚴重等級 major,blocking 共 1 條。
