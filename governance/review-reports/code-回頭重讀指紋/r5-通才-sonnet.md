severity: minor

## 範圍與做法
- 讀完 repair patch 全文。
- 重跑 `python3.14 scripts/test_lumos.py -k reread_fp`:180 項全過。
- 把縮排鏈核心(`_note_reread_hunk_nodes`)的新舊版各抽出來,用隨機輸入互相比對。
- 在暫存 git repo 驗證單路徑 diff 的行為。
- 另跑過 `-k reread`(較寬的子集),因逾時中止,沒有結果,不算證據。
- 暫存目錄已刪。

## Finding

severity: minor
blocking: 否 — 只在「檔案換成同名資料夾」這種少見改動才有差別,而且新行為更精確,不會漏判也不會誤放行
引句:「結果跟逐支各開一次逐位元組相同(t_reread_fp_one_diff_for_all_files)」
問題:這句話在一種情形下不成立。`git --literal-pathspecs diff … -- a` 的路徑比對會把 `a/` 底下的檔也收進來。
- 舊的逐檔做法:問 `a` 會同時回 `a`(刪除)和 `a/b`(新增)兩段。`_patch_file_changes` 因此得到兩筆,`" ".join(sorted(got.values()))` 把兩份雜湊都併進 `a` 的指紋。
- 新的批次做法:只切出 `a` 自己那一段。
具體失敗情境:
- 範圍內有一支檔 `a` 被刪掉,同時出現同名資料夾 `a/b`。
- 只有 `a` 在某篇的 `about_code` 裡時,新舊版算出的 v2 指紋不同。
- 實測:暫存 repo 用 `git --literal-pathspecs diff --no-renames HEAD~1 HEAD -- a`,輸出兩個 `diff --git`(`a/a` 與 `a/a/b`)。
- 新版把 `a/b` 的改動排除在 `a` 的指紋外,方向更合理,只是跟註解與測試名宣稱的「逐位元組相同」不符。
- 影響:僅限 v2 指紋。v1 指紋只由物件編號算出,不依賴這段 diff,所以舊紀錄的 v1 指紋不變。
- 建議:把註解的宣稱收窄,或補一支這個情形的測試。
佐證:`scripts/lumos`(`reread-fp` 工作樹)的 `_note_reread_fp_diff` 與 `_note_reread_split_diff`,位置約 `scripts/lumos:36568-36625`。

## 已讀,無 finding

- **一次 diff 取代逐檔 diff**
  - 拆段、檔頭切點、`\n@@ ` 與 `GIT binary patch` 的截斷、重名段刪除、批次切不出來就單支重問,邏輯成立。
  - 批次大小用的 `sizes` 在第一次 `_note_reread_fp_file` 就整批查好,64 MB 與 100 KB 上限有效。
  - 全程帶 `--literal-pathspecs`,檔名裡的萬用字元不會多收別的檔。
- **v1 舊紀錄指紋**:`_note_reread_contrast_fp` 只用物件編號,與 diff 無關,不受影響。
- **`_patch_file_changes` 的其他使用者**:repair 沒改它的簽名與行為,其他呼叫端(`26211`、`26255` 附近)不受影響。
- **縮排鏈核心重寫**
  - 隨機輸入各 3 萬筆比對。
  - 範圍內有非跳過行,或範圍全是空白行時,新舊結果完全一致,0 筆不同。
  - 只有「範圍全是純標點行」時才依設計改變。
  - 分塊切行與整份 split 的行數(含檔尾空行)一致。
- **`_note_reread_own_fps` 的截止時間**:改傳整體截止時間後,指紋那一步逾時不再讓整個集合變空。唯一的測試呼叫端已跟著改。
- **推主線判定與 `_note_reread_fp_base`**
  - 快取 `fpbase` 之前,`push_old` 一定已設好:prepare 在 `_note_reread_scan` 之後立刻設,check 在指紋之前設。
  - 功能分支、新建主線(遠端舊值全 0)、沒有推送參數,都照舊走本機候選。
  - 主線名固定含 `main`、`master`,查候選失敗也不誤判成功能分支。
  - 遠端舊值本機找不到時改成丟 `_NoteRereadStop`。但 `_note_audit_resolve` 對起點找不到的情形本來就會先擋,所以實際上幾乎觸發不到。
- **入口清 git 環境**
  - 實測 `GIT_GRAFT_FILE=/dev/null/lumos-no-grafts` 下 git 2.39 不印警告、`log` 與 `rev-list` 正常。
  - 清掉 `GIT_DIFF_OPTS`、`GIT_EXTERNAL_DIFF` 只影響 `main()` 進入後的子行程。
  - 專案內沒有其他地方依賴這兩個變數。
- **reread-prepare/check 的輸出與 rc**
  - 只有 `LUMOS_SKIP_REREAD_CHECK` 與逾時提示的文字有改,rc 判定(`_note_reread_rc`、`_note_reread_blocking`)沒動。
  - 相關測試全過。

最高等級 minor,blocking 0 條。
