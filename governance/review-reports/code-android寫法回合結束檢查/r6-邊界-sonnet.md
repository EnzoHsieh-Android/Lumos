severity: major

第五輪邊界席 F1(子目錄專案鉤子下游接錯路徑)已修好。我在 monorepo 實跑:專案根設在 `sub/`,筆記動過時靜默放行(rc0),筆記沒動時只點名 `sub/a.py`,沒副檔名的 `sub/tool` 也點得到。

這輪我另外查了六項,都沒有問題:
- `ls-files -s -v -z` 的輸出格式能正確解析。skip-worktree(`S`)和 assume-unchanged(小寫)的檔案不會被誤報成改動或刪除,檔名含空格或 tab 也沒事。
- PATH 的 `:`、`.`、`bin`、`""`、`./` 各種形狀,放一支假的 `git` 在 repo 根,檢查、影響分析、停止檢查三支鉤子都沒有執行它。
- `_clean_path_env` 在每支鉤子都排在 `__main__` 的第一句。
- 檔名含反引號、換行、ESC、CR、200 字長名、12 支長檔名時,擋停訊息 1069 字,沒有超過 1500。
- 鉤子 stdin 餵 空字串、`null`、`[]`、`1e999`、型別錯誤的欄位時,八支鉤子都沒崩潰。唯一例外是 `check-graph-sync` 收到 `{"cwd":5}` 或 `{"cwd":["a"]}` 會 TypeError、rc1。rc1 是非阻擋錯誤,真實的 Claude Code 也不會送這種值,所以不列為 finding。
- 這輪沒有動標記檔名和訊號,這兩項沒有可審的差異。

F1. 子目錄專案下,別的子專案裡被刪除的程式碼檔會被點名,甚至誤擋收工(和上一輪 F1 同一族,「專案根」判斷漏了刪除檔這條路)
- 輸入:repo 有 `sub/`(專案根,有 `docs/x-knowledge`)和 `other/` 兩個子專案。`other/b.py` 已提交後被刪除(`sub` 底下沒有程式碼改動)。`CLAUDE_PROJECT_DIR=repo/sub`,餵 `check-graph-sync.py` 一份 Stop 的 stdin。
- 實際:輸出「工作樹上有 1 個程式碼檔還沒提交……• other/b.py(已刪除)」。如果同時有 `sub` 底下的程式碼改動,就變成 `decision: block`,清單裡列 `other/b.py`。實測兩種都出現。
- 預期:`other/b.py` 不在專案 `sub` 底下,不該被點名,也不該算進擋停的檔數。沒被刪的 `other/` 檔會被 `is_code_file` 的「專案底下」檢查擋掉,刪除檔卻不會。
- 原因:`_entry_is_code` 的刪除分支只看副檔名或 HEAD 首行是否為 `#!`,沒有判斷檔案是否在專案底下。「在不在專案底下」只由最後那句 `is_code_file(..., project_root)` 判,刪除檔走不到那裡。`_wt_changed_nofilter` 回的是整個 repo 的改動,所以別的子專案的刪除會混進來。
- 測試只驗了修改過的檔,沒驗刪除檔,所以綠。
- 影響範圍:只有專案根是 repo 子目錄時才會發生。根在 repo 根時,所有檔都在專案底下。舊版 7eaad22 的刪除分支一樣沒判位置,所以不是這輪新造的退步,但這輪改的就是同一個根因。
- 修法:刪除分支也要先判 `(top or project_root) / relpath` 是否在 `project_root` 之下,再看副檔名或 shebang。
引句:「return is_code_file(str((top or project_root) / relpath), project_root)」
severity: major
blocking: 是

總結:最嚴重是 major(子目錄專案下,別的子專案裡被刪除的程式碼檔會被點名並可能誤擋收工),會擋 1 條。臨時目錄已刪除。
