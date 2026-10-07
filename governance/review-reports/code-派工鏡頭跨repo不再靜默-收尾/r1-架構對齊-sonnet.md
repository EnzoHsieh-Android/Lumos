severity: clean

我有看到「lumos 自動附加」段,列了 24 篇:前 8 篇附牽連檔與合約摘要,其餘 16 篇只列名。對照時我沒有讀 governance/review-reports/ 底下的任何檔。

**1. 分層與依賴方向:對齊。** `dispatch-lens-hook.py` 仍只透過子行程呼叫 `scripts/lumos`,沒有跨層直呼。
- 修補後的 `_clean_field` 只往下呼叫同檔的 `_plain_label`(`scripts/hooks/claude/dispatch-lens-hook.py:217`),被 `FAIL_NOTE` 組句(同檔 `:257`)和鎖路徑欄位(同檔 `:463`)呼叫。
- 這跟 `memory-sweep.py` 的 `_clean` 同一層、同一方向:本地清洗函式包住正典 `_plain_label`(`scripts/hooks/claude/memory-sweep.py:269`)。
- lumos 端的 `_dispatch_lens_fail`(`scripts/lumos:45547`)仍是 `cmd_dispatch_lens` 同層的私有輔助函式。

**2. 命名與錯誤處理:對齊。**
- 清洗函式的前綴 `_` 慣例、`-&gt; str` 標註和文件字串寫法與鄰居一致。
- 失敗 JSON 補了 `ensure_ascii=False`,與同一支 `dispatch-lens` 指令其他輸出一致:`scripts/lumos:45376` 的 `row` 列、`:45603` 與 `:45610` 的 `dumps`。修補前整支 `scripts/lumos` 就有 130 處 `ensure_ascii=False`。
- 失敗列用單一鍵 `lens_fail` 帶代碼,跟 `spawn_error` / `lock_error` 的布林旗標列(`scripts/lumos:45373`、`:45401`)形狀不同。文件字串已明寫這是刻意的。
- 領席超時那條路現在有 `_frame_injected`(`scripts/hooks/claude/dispatch-lens-hook.py:369`),與其他掛鉤的做法一致。

**3. 第二種做法:沒有。**
- **★注入框★ 區塊逐字相同。** 我把 `_FRAME_OPEN` 到 `_plain_label` 的區塊從 6 支檔抽出來,逐一算 sha1:`dispatch-lens-hook.py`、`ci-status-hook.py`、`impact-hook.py`、`lumos-entry-hook.py`、`memory-sweep.py` 與 `scripts/lumos` 全是 `b2847cfe`,前五支都是 26 行。我另外把 `ci-status-hook.py` 與 `dispatch-lens-hook.py` 的區塊 diff 過,無差異。
- **`_clean_field` 與 `_clean` 是同一種模式。** 兩者都是先在外層做額外清理(`_clean_field` 去反引號與 U+2028/U+2029/U+0085;`_clean` 去 Cf 類與框線區塊),再呼叫不改動的 `_plain_label(s, cap=…)`。只有清理項目不同,模式相同。
- **守衛新增那條寫法一致。** 它用同一支測試的 `check("★一套慣例★: …", 條件, 訊息)` 格式,訊息前綴也相同,並沿用同一個 `files` 與 `sigs`。新增的 `t_dispatch_lens_hook_claim_timeout_framed` 沿用既有的 `_load_hook_mod` 與 `patch.object` 寫法。

觀察,不列為 finding:守衛的 `files` 清單(`scripts/test_lumos.py:17020`)不含 `memory-sweep.py`,但它有同一個區塊。修補前就是這樣,不屬於這次修補,也沒有造成兩套做法。

不對齊共 0 條,其中重大 0 條
總結:這次修補抄進來的框區塊跟鄰居逐字一樣,路徑清理和守衛測試的寫法也都跟既有做法同一套,沒有引入第二種做法。
