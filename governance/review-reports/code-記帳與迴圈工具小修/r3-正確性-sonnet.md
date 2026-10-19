severity: major

查證範圍:我逐段讀了 `r3-repair-lumos.patch`,並從 git 匯出修前(69ee6d76)與修後(5248791e)兩份 scripts,在臨時 repo 跑同一條指令比對。臨時目錄是 `/tmp/lumos-seat-work/code-記帳與迴圈工具小修/正確性-sonnet/`。

**1. `_jsonl_append_verified` 讀回自驗改用 `splitlines()`,筆記含 U+2028 / U+2029 / U+0085 時,明明寫進去了卻回報「落盤自驗失敗」rc2**
severity: major
- blocking: 是
- 歸因:有證據的修復回歸
- 位置:`_jsonl_append_verified` 的新讀回段,`tail = fb.read().decode(...)` 之後接 `for line in tail.splitlines():`。
- 問題:`json.dumps(ensure_ascii=False)` 不跳脫 U+2028、U+2029、U+0085。`splitlines()` 會在這三個字元處把剛寫的那一列劈成兩段,兩段 `json.loads` 都失敗,讀回就判「找不到這一筆」。
- 這支檔自己就規定了切行規則。`_ledger_lines` 的 docstring 寫:「不用 splitlines(它還認 U+2028/U+2029/U+0085 …… 一列會被劈開丟掉)」。修前的 `for line in f`(文字模式)不會在這三個字元處切開,所以修前沒有這個問題。
- 具體例子:
  - 輸入:`lumos canary record none --loop L1 --note $'a\u2028b' --token T1 --severity minor`
  - 預期:rc0,記下來。
  - 修前:`✓ 這筆審查結果(none)記下來了`,rc=0,帳檔 1 列。
  - 修後:`canary record: 落盤自驗失敗——系統說寫成功了,但讀回來找不到這一筆,這筆不算記成功`,rc=2,帳檔卻已有 1 列。
  - 後果:呼叫端以為沒記成功。照提示重記,帳本只能追加,會多一列重複的。
- 影響面:所有共用這支的寫入端,包含審查帳 `canary record` 與 `canary second`、規格閘留痕(8465 行附近)、`dedup_key` 的 CI 帳、drift 帳。凡是 note 或欄位能帶這三個字元的,都會誤報。從網頁貼進來的文字有時會帶 U+2028 或 U+0085,不算極端輸入。
- 測試缺口:`t_cap_retro_r3_ledger_lines_everywhere` 守的原始碼掃描,只抓「`.read_text(...).splitlines()` 直接接在帳檔路徑上」這種寫法。這裡的路徑是函式參數、用的是 bytes 的 `decode` 再 `splitlines`,掃不到。`scripts/test_lumos.py` 裡也沒有任何測試對 `_jsonl_append_verified` 餵含這三個字元的內容(我 grep 該函式名,測試檔沒有命中)。把修法換成 `_ledger_lines(tail)` 之類的呼叫,現有測試不會紅。換回 `splitlines` 照綠。
- 引句:「        for line in tail.splitlines():」
- 修法方向:改走 `_ledger_lines(tail)`,它對 str 與 bytes 都能用。再補一條測試,note 含 `chr(0x2028)` 時 `canary record` 要 rc0。

**三問**

1. **原問題的修復效果**
   - 結局帳濾除、none 保留字、每筆只讀一次帳、`_rf_qloop`、帳壞訊息抽共用,這幾項我逐段讀過,沒找到新的錯誤。
   - 另外讀過的 `_is_outcome_row` 呼叫端:
     - 規格閘留痕索引、loop replay 的讀帳、`_loop_status_read`、`_canary_ledger_scan`。
     - `_loop_round_format` 的各個呼叫端:`_cap_hint_scope`、loop next、`loop status`、`_disposal_judge`。
     - `_fix_round_rows` 這條路徑,它透過 `_loop_records` 讀帳。
     - 這些拿到的列都已經是濾過的審查列。
   - T6 定錨檢查改用共用的那一次讀帳,結果跟修前語意一致:帳壞時由前面的輪次規則先擋下。
   - `_none_reserved_lines` 的 refuted-set 只在 `id=理由` 的 id 恰為 none 時才擋;本來就會被原解析器擋下的畸形項,不會因此多擋合法輸入。
   - 正向證據只有讀碼,沒有跑出修前修後的對照。我沒有跑 `t_outcome_row_*` 與 `t_canary_record_*` 測試子集,測試是否真能抓到這些修復,我沒有證據。
2. **修補處的正常、錯誤與相鄰呼叫路徑**
   - 讀帳只讀一次,而且只在寫入前讀,沒找到讀到舊資料的路徑。
   - 相鄰路徑出事的只有第 1 條:`_jsonl_append_verified` 的所有呼叫端。
   - 我沒查 `_ledger_tail_needs_newline` 與 `_drift_ledger_append` 補換行的重複補丁。第二次呼叫會因為尾端已有換行回 False,不會多補。
3. **新發現在修前與修後的結果**
   - 只有第 1 條,結果如上:修前 rc0、修後 rc2。
   - 另外在不改分類的前提下,我沒跑到其他修前修後差異。

**未驗範圍**
- 沒跑測試套件。
- 帳壞只壞一列時,各編號被擋的範圍只讀碼確認:有壞列的編號擋,別的編號不受影響。
- `_rf_qloop` 對控制字元的處理,沒做可複製貼上的實測。
- 沒檢查結局帳濾除對老凍結判定(golden)的相容性。

最嚴重 severity:major,blocking 共 1 條。
