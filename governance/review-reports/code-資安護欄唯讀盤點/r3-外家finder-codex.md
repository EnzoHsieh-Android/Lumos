severity: major

F1. 全域重複 ID 仍被算成有效入口映射，會讓覆蓋看起來比實際完整

severity: major
blocking: 是

`duplicate_id` 已證明登記不合法，程式卻只用逐列的 `references_valid` 篩映射；兩條同名控制項因此都進入 `mapped_control_ids`，入口狀態成為 `mapped`，而非保守的 `unmapped`。這直接違反「ID 專案內唯一」及「映射限合法控制項」。

file: `scripts/lumos:7290` 重複 ID 只加入全域錯誤與列內 issue。
file: `scripts/lumos:7315` 覆蓋計算沒有排除 `duplicate_id` 等全域登記錯誤。

引句:「    sec = [r for r in rows_here if "security" in r["concerns"] and r["references_valid"]]」

具體重現：

- 輸入：兩篇 Systems 筆記各登記一條欄位、來源、決策及證據引用皆合法的 active security 控制項；兩條都使用 ID `DUP` 並映射入口 `s`。
- 預期：保留兩筆原始登記與 `duplicate_id` 錯誤，但兩筆都不得算合法映射；`s.state=unmapped`、`mapped_control_ids=[]`，另列無效登記 ID。
- 實際：退出碼雖為 2，`s.state=mapped`，且 `mapped_control_ids=["DUP","DUP"]`；直接讀 coverage 的代理會得到錯誤的完整感。

歸因:有證據的原有漏查

同一案例兩版查證：

- before 命令：`python3.14 -c '<載入固定 scripts/lumos、建立上述兩篇 in-memory Systems fixture、呼叫 _secinv_build 的 probe>' /tmp/lumos-seat-work/code-資安護欄唯讀盤點/r3-正確性-sonnet-before/scripts/lumos`
- before 結果：probe rc 0；產品結果 `rc=2`、`errors=["duplicate_id"]`、`registration_complete=false`，但 coverage 為 `state="mapped"`、`mapped=["DUP","DUP"]`。
- after 命令：同一 probe，只將載入路徑換成 `/tmp/lumos-seat-work/code-資安護欄唯讀盤點/r3-正確性-sonnet-after/scripts/lumos`。
- after 結果：與 before 完全相同。

§3.1 同一案例證據：

- claim：F1，重複 ID 不得消除入口缺口。
- input/expected/出處：上述兩筆 `DUP`；計劃第 96 行要求 ID 專案內唯一，第 119 行要求映射限合法控制項。
- case_source：同一份純記憶體 fixture；兩版只替換被載入的固定 `scripts/lumos`。
- comparison：兩版輸入、日期與斷言相同，可比較。
- attribution：修前、修後皆失敗，故為原有漏查，不是本輪修補回歸。

建議修法：重複 ID／重複來源判定後，替相關列標記 registration validity；records 仍原樣保留，但 coverage 必須排除這些列，並像 `invalid_reference_control_ids` 一樣明列無效登記。

三問核對：

1. 原問題修復效果：R3「證據引用非 Verification 節點」有可比行為證據。相同 fixture 在修前得到 rc0、`references_valid=true`、入口 `mapped`；修後得到 rc2、`reference_error`、`references_valid=false`、入口 `unmapped` 並列入 `invalid_reference_control_ids`。此項已修復。R1、R2、R4–R7 的正式測試因唯讀沙箱無可用暫存目錄而無法啟動，維持未判定。

2. 正常、錯誤與相鄰路徑：同一 fixture 把引用換成合法 `Verification/v.md` 後，修前與修後皆為 rc0、`declared_only`、`references_valid=true`、入口 `mapped`，所以 R3 相鄰正常路徑仍成立。錯誤路徑則如上由 mapped 改成 unmapped。另以兩端 CLI 對各自固定圖譜執行零登記案例，兩版皆輸出單一 JSON、rc0、`read_complete=true`、`registration_complete=false`、`security_verdict=not_assessed`。

3. 新 finding 的兩版結果：F1 在修前與修後皆穩定重現，輸出逐欄相同；有證據屬原有漏查，沒有證據屬修復回歸。

未驗範圍：`python3.14 scripts/test_lumos.py -k seclist_r2_nonverif_evidence` 與 `-k seclist_r2_docs_symlink` 在兩端都於 runner 初始化時失敗，原因是唯讀沙箱找不到可寫的 temporary directory；這不是產品測試失敗，也不能據此宣稱其餘修補已通過或無回歸。

最嚴重 severity: major，blocking 共 1 條。
204,627
