severity: clean

本輪修補沒有找到能被利用的洞。我讀了 r3-repair-lumos.patch、r3-repair-tests.patch 和 r3-repair-docs.patch,並對照修後 5248791e 的 `scripts/lumos` 逐點驗證。這輪沒有跑程式或實驗,結論來自讀碼。

**①提示注入:已看,無。**
- 擋下訊息裡印給人照抄的迴圈編號,現在走新的 `_rf_qloop`:先 `shlex.quote`,再用 `_esc_clean` 清控制字元,不截斷。
- 單引號包住的內容被清控制字元後,仍在引號內,不會長出換行或第二條指令。
- 編號被截斷後照抄會開出另一個迴圈,這個舊問題也一併消掉了。
- `_none_reserved_lines` 印出的清單內容走 `_esc_clean(repr(...), 120)`,沒有未消毒的自由文字進到給 AI 的訊息。

**②讀寫與執行越界:已看,無。**
- 新增的 `_ledger_tail_needs_newline` 經由 `_regular_own_fd(follow=True)` 開檔。這個函式是既有的,已有非一般檔的處理,讀不到時回 False,不碰檔。
- 追加寫入 `_jsonl_append_verified` 本來就用 `open(path, "a")`,這輪沒有新增捷徑或路徑面。
- 落盤自驗改成只讀 `start` 之後的區段,是同一個檔、同一種開檔法。
- diff 的新增行裡沒有 `shell=True`、`os.system`、`eval`、反序列化,也沒有密鑰或信箱,環境變數覆蓋下載來源也沒有。

**③非刻意、一步繞過守衛:已看,無。** 派工詞點名的三件事,四件攻擊路徑都填不出來。
- **寫一筆結局帳讓處置閘少看到輪次:**
  - 誰是使用者或照常操作的 AI,從 `canary record --outcome` 送進去。
  - 寫側擋住了(`scripts/lumos` 11858–11863):`--outcome` 只收 kind=none,且不能和 `--round`、`--severity`、`--report`、`--snapshot`、`--intake`、`--findings`、`--findings-set` 並用。所以帶輪次的審查列不可能帶 `outcome` 鍵。
  - 讀側 `_is_outcome_row` 只判 `"outcome" in d`,會被濾掉的只有結局帳。要偽造帶 `outcome` 鍵的審查列只能手填帳本,屬範圍外。
- **在別的編號弄壞一列來繞過:**
  - `_canary_ledger_scan` 的 `bad` 仍按編號分開記(`bad[lp]`),`_loop_records_checked_ex` 只回報該編號自己的壞列;帳整本讀不到或不是 UTF-8 時一律擋全部。
  - 帳壞時,`--orchestrator`、`--regression-set` 和輪次規則共用 `_round_format_bad_lines`,不會退回舊的讀法。
  - `_is_outcome_row` 在壞列判斷之前濾掉結局帳,結局帳不會洗掉別列的壞狀態。
- **`--round` 純空白:**
  - `cmd_canary` 開頭(11475)把純空白的 `round_id` 正規化成 None。
  - 之後所有 `if round_id` 判斷、`--outcome` 與 `--round` 的互斥檢查都吃到正規化後的值,沒有純空白滿足「每筆要帶輪次」的路徑。
  - 唯一用到輪次的跑滿回顧擋點改為 `if loop and round_id`。沒帶輪次的列在跑滿且已有人裁的迴圈上,現在不會被跑滿回顧擋。我在被擋的路徑上找不到可利用的入口:不帶輪次的列不計入輪數,而且混用規則會擋。這一條只能算推論,不列為發現。

**保留字 `none`:** `_none_reserved_lines` 和 `_ids` 都只以 `,` 切分,兩邊切法一致,沒有用其他分隔符或大小寫變體躲過檢查的路徑。`--accepted-set none` 這類「整串只寫 none」仍照舊視為空集合,測試也有對照。

最嚴重 severity:clean,blocking 共 0 條。
