severity: clean

## 測試結果(在 reread-fp 工作樹原地跑,Python 3.14)

- `-k patch_fingerprint`:7 passed, 0 failed。其中包含新增的 `t_patch_fingerprint_b_in_path_name` 和 `t_patch_fingerprint_binary_and_quoting`。
- `-k security_seat`:67 passed, 0 failed。最慢的是 `t_disposal_security_seat_required`,11.6 秒。
- 我另外跑了 `-k reread_fp`:201 passed, 0 failed,約 4.5 分鐘。這不是全套,只是回頭重讀相關的子集。
- 工作樹 `git status` 乾淨。我的實驗目錄已刪。

## 各項檢查

**`_patch_file_changes` 改動(凍結 patch 指紋、資安席涵蓋判定、修補鏡頭共用)**
已讀,無 finding。
- 指紋雜湊只用 `chg` 的內容,不含檔名。檔名只影響字典的鍵。所以 v2 指紋值和 v1 舊紀錄的比對不受影響;回頭重讀的指紋是 `" ".join(sorted(got.values()))`,也不含檔名。
- 我拿九種檔頭實測 `_patch_file_changes` 與 `_diff_git_same_name`:
  - 一般名、含空格、含 `b/`、中文八進位引號、引號內跳脫的雙引號、尾端 `\r`,結果都合理。
  - 改名(`a/old b/new`)和尾端 `\r` 兩種回 None,退回舊取法,與修補前行為相同。
  - 含 ` b/` 的路徑現在取對:`a/a b/c b/a b/c` 得 `a b/c`,舊寫法會取成 `c`。
- 誤判成「兩半相同」的條件是整行字面上等於 `a/X b/X`,改名或複製不可能滿足。就算有人刻意構造,有 `+++` 或 `rename to` 時會蓋過。
- 資安席的呼叫處在 `scripts/lumos:26221`、`scripts/lumos:26265`,只用檔名做涵蓋比對。檔名只會在含 ` b/`、只改權限或二進位這幾種沒有 `+++` 的段變得更準,不會變嚴。

**`_diff_git_starts` 取代 `re.split`(截斷給判定者的流程)**
已讀,無 finding。新做法用 `{0, 各起點, len(d)}` 加 `itertools.pairwise` 切段,和舊的 `(?m)^(?=diff --git )` 切法等價:空字串得空清單,開頭不是 diff 時第一段保留,`str` 和 `bytes` 都收。

**批次 diff 與單支回退(`scripts/lumos:36575` 起)**
已讀,無 finding。
- `got` 現在是三元組,`base["diffs"]` 只有 `_note_reread_fp_diff` 寫入並消費,沒有遺漏的讀取處。
- `done` 的鍵 `(bp, tip, path)` 和 `_note_reread_fp_file` 的快取鍵一致。
- `wanted()` 用的大小表和 `_note_reread_fp_file` 的退回判斷同一份,不會多排或漏排。
- 只問一支而切不出時整段給它,等於 r4 以前逐支問的行為。同名資料夾的情況由切得出的那條路徑處理,有測試。
- 路徑多時每批重建剩餘清單是 O(n),batch 數有限,可接受。

**reread-prepare / check 的輸出與 rc**
已讀,無 finding。
- 這次只改了「跳過」那句訊息的文字,rc 邏輯(`_note_reread_rc`、`_note_reread_blocking`)沒動。
- 訊息說跳過會記進有進版控的 `docs/.governance-log.jsonl`,屬實:`("note-reread","skipped-env")` 不在 `_GOV_LOCAL_PAIRS`(`scripts/lumos:1368`),`_gov_routes_local` 也要求 `hard is False` 才走本機帳。
- 計劃與筆記裡的對應敘述一致,沒有殘留舊說法的出處。

**v1 舊紀錄**
已讀,無 finding。`-k reread_fp` 裡的 `t_reread_fp_accepts_v1_records` 通過,v1 退回路徑沒被碰到。

最高等級 clean,blocking 0 條。
