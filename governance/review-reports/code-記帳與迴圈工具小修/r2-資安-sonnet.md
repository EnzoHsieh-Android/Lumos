severity: clean

已逐行讀完 r2-repair-lumos.patch 與 r2-repair-tests.patch 的相關段落,並用 r2-snapshot.patch 對照上下文。docs patch 只用 grep 掃過信箱與密鑰字樣,沒有逐行讀。沒有可利用的洞。

**三類逐項**

- **①提示注入:已看,無。**
  - 唯一把使用者可控字串(審查編號)放進「接下來」指令範本的地方,是 `_round_format_write_block` 的 `q`。
  - 它現在先過 `_esc_clean(str(loop), 80)`,再過 `shlex.quote`,控制字元、ESC 與換行都清掉,`;` 之類的 shell 字元被引號包住。
  - `_RF_RENUMBER` 與 `_rf_mixed_next` 的其餘文字是固定字串,不含外來內容。
  - 超過 80 字會截斷並加「…」,只會讓範本失準,不會變成注入。
- **②讀寫越界與執行:已看,無。**
  - 這批差異沒有新增檔案寫入、路徑解析、subprocess、環境變數覆寫或下載。
  - `_ledger_rel_path` 只是上下文,沒有被改動。
  - 測試補丁只寫臨時帳本,沒有看起來真能用的憑證。測試裡 `"token": "BAD"` 是假資料。
- **③非刻意繞過守衛:已看,無。** 逐項回答你點名的三問:
  - **靠結局帳讓處置閘少看到輪次:不成立。**
    - `_review_rows` 以「有 `outcome` 鍵」濾列。
    - `cmd_canary` 在寫入 `--outcome` 時,若同時帶 `--round`、`--findings-set`、`--severity`、`--report`、`--snapshot`、`--intake` 或 `--findings` 就 rc2。
    - 所以用 CLI 寫出的結局帳不可能帶輪次或發現,被濾掉的只有不含審查資料的列。
    - 手填帳本欄位屬使用者裁定的範圍外。
    - 結局帳混在帶輪次的迴圈裡,從原本的 rc2 卡死變成被忽略,沒有任何一筆審查輪因此消失。
    - 全是結局帳時,處置閘回「無記錄」rc1,仍是未過。
  - **在別的編號弄壞一列繞過:不成立。**
    - 壞列只影響該編號的 `bad` 對照。
    - 整本不是 UTF-8 時 `whole_ledger_bad` 讓所有編號的寫入都擋下(fail closed)。
    - 讀側 `_loop_records` 在整本壞帳時照舊丟例外而不是放行。
    - `--regression-set` 路徑在壞帳時走 `_loop_records`,會直接崩潰而不寫帳,同樣沒有繞過。
  - **`--round` 純空白:已堵。** `round_id` 純空白先被正規化成 None,之後「每筆要帶輪次」的規則照常擋下。
  - **`--outcome` 搭純空白的 `--round`:無影響。** 正規化後這種組合不再被「結局帳不能帶 round」的檢查擋下,但寫出的仍是不帶輪次的結局帳,沒有可拿到的東西。
  - **`--regression-set` 與 `--folded-set` 的 none 判法:** 改用 `_ids` 和 `_set_or_none`(切法與折入、放行同一支)。我沒在這批裡找到能因此偽造放行的輸入,只對照了判法一致。
- **帳壞語意:** `_review_rows` 與 `_loop_round_format` 現在給 `_cap_hint_scope`、`cmd_loop_next`、`cmd_loop_status` 和 `_loop_status_disposal` 共用同一個判法,沒看到哪條讀側路徑還各自數、能被矛盾判定利用。

最嚴重 severity:clean,blocking 共 0 條。
