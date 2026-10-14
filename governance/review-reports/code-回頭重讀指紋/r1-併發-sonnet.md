severity: minor

併發與資源席:共 3 條 finding,最高 minor,沒有 major 或 blocker。實驗目錄已刪。

**實測數字**
- 在本 repo 對分岔點到頂端跑一次 `diff --raw`、單檔 diff 和 `cat-file --batch-check`,各約 20 到 30 ms。逐檔 diff 的次數(每支檔一次,結果按路徑快取)不會是瓶頸。
- 造一個 29 MB 的檔案,約一半的行被改,跑 `_NOTE_REREAD_FP_DIFF_ARGS` 加 `_patch_file_changes`。diff 輸出 45 MB,Python 端約 0.27 秒、峰值約 408 MB RSS。
- 同一個檔案把所有行打亂,單次 `git diff` 要 6 秒,輸出 60 MB。

severity: minor
blocking: 否 — 只多佔時間與記憶體,不會讓判定出錯,而且每次 git 呼叫仍有逾時
引句:「got = _nodehome_cat_sizes(scan["root"], oids, timeout=t) if (oids and t > 0) else None」
問題:32 MB 上限的大小查詢一失敗,上限就整個失效,而且不報錯。`got` 是 None 時,`sizes` 會被快取成空 dict,之後 `sizes.get(o, 0) > _NOTE_REREAD_FP_MAX` 對每個物件都回 0,於是每個大檔都被放行去跑逐檔 diff。
失敗情境:`cat-file --batch-check` 逾時,但整體剩餘時間超過 20 秒(`_git_timeout` 的上限就是 20 秒)。這時上限關掉,後面的逐檔 diff 還有時間去讀任意大的檔。實測 29 MB 的檔案就要 400 MB 以上,更大的檔沒有擋。
建議:查不到大小時直接退回 v1 並標原因「查大小失敗」,不要當成 0。
佐證:file: `scripts/lumos:36391`(`_note_reread_fp_sizes`)與 `scripts/lumos:36424`(`_note_reread_fp_file` 的大小判斷)

severity: minor
blocking: 否 — 只是整體逾時超出幾秒,結果仍然正確
引句:「names = _note_reread_tip_names(root, bp)」
問題:`_note_reread_own_fps` 開頭看過 `dl` 沒過期,接著呼叫的 `_note_reread_tip_names` 走 `_ns_git`。`_ns_git` 用 `_lens_git` 的預設 20 秒逾時,沒有套用 `dl`。這跟補丁其他地方「每次 git 都夾進剩餘時間」的做法不一致。
失敗情境:`dl` 剩 1 秒時進入這個函式,`ls-tree` 卡住會最多多佔 19 秒。`_NOTE_REREAD_FP_RESERVE` 本來保留 3 秒給後面的讀紀錄與第二層,結果被吃光。整體預算 `_NOTE_REREAD_BUDGET_SEC`(30 秒)可能被超出十幾秒。
建議:這裡改用 `_lens_git_dl` 帶 `deadline=dl`。
佐證:file: `scripts/lumos:36769`(`_note_reread_tip_names` 沒有 deadline 參數)

severity: minor
blocking: 否 — 回頭重讀只是提醒、不擋推送
引句:「cache[rel] = {"v1": v1, "v2": v2, "why": why, "fp": v2 or v1, "ver": "v2" if v2 else "v1"」
問題:v2 還是退回 v1,取決於當下剩多少預算。`prepare` 不傳 deadline,所以一定算 v2。`check` 傳 deadline,慢的機器上 v2 會變成「逾時」而退回 v1。
失敗情境:同一個頂端、同樣的 refs,`prepare` 記下的紀錄檔名是 v2 指紋,`check` 逾時用 v1 去比,對不上就再次要求重讀。預算耗盡時,排在前面的候選拿到 v2,排在後面的拿到 v1,同一次執行內口徑也不一致。
建議:這是設計取捨,不算 bug。可以在輸出標明「因逾時用 v1」,別讓使用者以為紀錄壞了。
佐證:file: `scripts/lumos:36345`(`_note_reread_fp_info`)與 `scripts/lumos:36364`(`_note_reread_fp_base` 的 `dl` 計算)

**已讀,無 finding**
- `_git_timeout`、`_lens_git_dl`:`deadline=None` 時退回 20 秒,與原本 `_lens_git` 的預設相同;剩餘時間小於等於 0 就不執行並回 None,與逾時同一條路。
- `_push_rev`、`_push_mainline_full`、`_push_mainlines`、`_push_pick_base`:其他呼叫端沒傳 deadline,行為不變。
- `_lens_default_base` 取代 `_codeloop_default_base`:`tip=None` 時,抽出共用函式前後的 git 呼叫順序相同。
- 逐檔快取鍵是(分岔點、頂端、路徑),`sizes` 與 `fpbase` 一次掃描只算一次。

最高等級 minor,blocking 0 條。
