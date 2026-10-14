severity: minor

這輪修補我讀完了,也在臨時目錄跑了幾個實驗(已刪)。沒有找到會讓「改動變了、指紋卻沒變」的路,也沒有「該擋的沒擋」的缺口,只有一條範圍不全的小問題。我沒有跑測試:沙盒沒有 `timeout` 指令,也沒有拿這個工作樹去跑 `scripts/test_lumos.py`。

## Finding

severity: minor
blocking: 否 — 只在特定組合下少一道核對,最後還有 CI 補驗,不會讓指紋算錯。
引句:「被推的是算分岔點用的那條主線(refs/remotes/<--push-remote>/<被推分支> 是主線候選之一)、遠端值不是全 0 而且本機找得到時」
問題:`_note_reread_bp_vs_remote` 的核對有三個靜默放行的條件。
- 遠端舊值在本機找不到(`_lens_full_sha` 回 None)就直接 return。
- 推送遠端跟 `_lens_default_remote` 選出的遠端不同(例如推 `fork` 的 main、分岔點卻取自 `origin/main`)時,`target` 對不上任何候選,整段不核對。
- 推功能分支時完全不核對。
這三種情形下,本機把遠端追蹤 ref 改到藏了改動的提交後,新版指紋就看不到那段改動。程式註解已說明功能分支靠 CI 補驗,但前兩個靜默放行的條件沒有寫進註解。
具體失敗情境:
- 輸入:本機 `refs/remotes/origin/main` 被改指到含有隱藏改動的提交 F,作者再把一個指向同一頂端的分支推到 `fork` 的 main。
- 結果:`target` 是 `refs/remotes/fork/main`,不在候選裡,不核對;分岔點取 F,新版指紋看不到那段改動。
- 補充:`bp == tip` 時 `base["bp"]` 是 None,會退回舊版指紋,舊版比較嚴格,所以不會放行。
佐證:``file: `scripts/lumos:37635-37680` ``(`_note_reread_bp_vs_remote`)。

## 已讀,無 finding

- **跳過純標點行後的縮排鏈**:
  - 在 `_note_reread_hunk_chains` 實測。
  - Python 多行簽名(`):` 收尾)的兩個函式,鏈各自是 `def a(` 與 `def b(`,不再撞鏈。
  - C# Allman(單獨一行的 `{`)的 `F` 與 `G`,鏈是 `class A` → `void F()` 與 `class A` → `void G()`,有分開。
  - Ruby 的 `end` 是有字的行,兩個 `def` 的鏈有分開。
  - JS 陣列裡的 `{`、`},` 被跳過後,鏈都變成 `const arr = [`,但修補前它們的原文也都是 `{`,兩個元素本來就同鏈,沒有新增碰撞。
  - 只改 `}` 的 hunk 會落在「無限深」位置,鏈含前一行(例如 `a();`),各函式仍因函式名不同而分開。
  - Go 與 JS 箭頭函式的簽名行都有字,不會被跳過。
- **指紋不會因此漏掉改動**:標籤只決定位置,diff 本文仍進指紋,所以改動變了指紋一定會變。
- **內聯熱迴圈與 `_note_reread_indent`**:兩邊的跳過規則一致。`not k & 8191` 的優先序正確。
- **效能與逾時**:40 萬行約 0.24 秒;逾時後回 None,`fp_tags` 轉成「逾時」,整支檔退回舊版。
- **逾時照擋**:
  - block 加 `--gate`:`left` 非空就 rc 1,清單講明「照舊版判」並給 `LUMOS_SKIP_REREAD_CHECK=1`。
  - warn:`hard` 為假,rc 0,不印跳過提示。
  - 記帳的 `blocked` / `reminded` 判斷跟著 `_note_reread_blocking` 走。
- **批次讀順序**:`_note_reread_fp_walk_keys` 在 v2、v1 以外的 prefetch 都用同一個排序集合,順序一致。
- **`GIT_NO_REPLACE_OBJECTS`**:在 `main()` 開頭設定,子行程繼承。lumos 裡沒有用到 git replace 的功能。
- **祖先核對在各種 ref 狀態下的行為**:
  - 新分支首推:遠端值是全 0 就直接 return。
  - 刪除 ref:範圍終點是全 0,在 `_note_reread_range` 就提早結束,不會走到核對。
  - 強推主線:舊值不是分岔點的後代就丟 `_NoteRereadStop`,block 加 `--gate` 擋(rc 1);warn 時 rc 0。
  - 核對本身 git 失敗或逾時:分岔點改記算不出,退回舊版。
  - 正常快轉推主線:分岔點必是舊值的祖先,不誤擋。
- **資料狀態五問**:
  - 空 `about_code`:`walk_keys` 回空串列,v2 回「全部未改」。
  - 空資料與零行數 hunk:`data=None` 時回 `[None]*n`。
  - 舊紀錄:v1 紀錄仍然有效,帳的欄位沒有改。
  - 重複的 `about_code` 項目:`walk_keys` 用 set 去重。
  - 同批次兩篇候選的順序:`blob_order` 照候選順序算,跟 v2 走訪一致。

最高等級 minor,blocking 0 條。
