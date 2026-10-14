severity: minor

整體判斷:這份修補多半往既有寫法收斂。`_contract_locate`、`_pq_decision_target`、`_strip_test_comments` 都是把重複的樣板併成一份,沒有跨層直呼。`_residual_tier_hits` 仍然不載入筆記庫,只讀 git 和 JSON,守住了 `_pitfall_tier` 的 vault-free 約定。不對齊只有下面 3 條,都是 minor。

- **`_contract_locate`**:原本 `guard audit` 和 `kill-add` 各內聯一份,現在三個呼叫者加上殘留系列共用一份。`_kill_find_contract` 的 docstring 寫明 `guard bind` 的定位判法不同,不併是刻意的,所以不算第二種做法。
- **`_pq_decision_target`**:原本 `_residual_decision` 另寫一份路徑解析,現在和 `_pq_decision_state` 共用,方向對。
- **`_strip_test_comments`**:`discover_test_methods` 和殘留索引找測試檔現在共用同一份剝註解邏輯,沒有第二套。

severity: minor
blocking: 否 — 不影響行為,只是同一件事(決策指標身分)在檔案裡有兩套比對函式
引句:「st, node, did = _pq_decision_target(env, "", ref, cache=cache)」
對照:file: `scripts/lumos:22557`(`_dref_norm`,用 `env.resolve` 解節點,同名取第一篇)
判定理由:`_residual_ref_key` 另造一個指標正規形。它是字串,走 `_pq_decision_target`,撞名時回原文。專案原有的 `_dref_norm` 是 tuple,走 `env.resolve`。兩者撞名時的行為刻意不同,這點有寫在 `_pq_decision_target` 的 docstring 裡。但 `_dref_norm` 和 `_dref_same` 的 docstring 沒有提到殘留這條路徑會比對出不同結果。建議在其中一處註明兩者的分工。

severity: minor
blocking: 否 — 同族已有回傳 (值, 原因) 的先例,且理由寫得出來
引句:「寫不進去(捷徑、不是一般檔、建資料夾失敗、磁碟錯)一律回原因,不丟例外」
對照:file: `scripts/lumos:21023`(`WriteBlocked` 註明為寫入被拒的唯一信號,由派發層接住印「擋下」)
判定理由:`_residual_index_write` 接住 `WriteBlocked` 和 `OSError`,改回 `(None, 原因)`。既有的寫入錯誤慣例是丟 `WriteBlocked`,但 `_drift_fix_load`(`scripts/lumos:40752` 附近)和 `_signoff_append`(`scripts/lumos:9262`)已經有轉成 `(值, 原因)` 的先例。這裡的理由也站得住:合約行已寫入後,索引才失敗,要照實講「合約行已改、索引沒更新」。因此是同族已有的第二種寫法,不是新發明。

severity: minor
blocking: 否 — 位置問題,不影響行為
引句:「測試檔內容去註解(語言感知):discover_test_methods 與殘留索引找測試所在的檔共用這一份」
對照:file: `scripts/lumos:6193`(`discover_test_methods`,測試探索一帶)
判定理由:`_strip_test_comments` 是通用的測試檔工具,卻放在殘留區段(`scripts/lumos:19036`),離它的主要呼叫者 `discover_test_methods` 約 1.3 萬行。往後有人要找剝註解邏輯,可能會去測試探索那一帶找,找不到。建議搬到 `discover_test_methods` 旁邊。

另外確認兩點,都不構成不對齊:
- `_residual_case_key` 和 `_residual_claim_fp` 的 NFKC 與 casefold 正規化,和 `_pq_key_norm`(`scripts/lumos:7183`)做的是不同的事(只留字母數字、去標點),專案內也慣用內聯 `unicodedata.normalize`。
- 索引讀取回 `"ok" / "missing" / "bad"` 三態,是新寫法,但沒有既有的同類函式可對照,也沒有和誰衝突。

不對齊共 3 條,major 0 條。
