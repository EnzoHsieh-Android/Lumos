severity: minor

整體看這批測試沒有找到會出錯的問題。我逐行讀完 hunk,追了 `_lint_born_true`、`_drift_probe_tree`、`_drift_disk_list` 的呼叫端,也實跑了 `t_doctor_s8_sees_worktree_home`(3 個檢查全過)。下面是去重後的 4 條,都是清理類。

1. 測試輔助函式 `_sg_records` 重複定義
severity: minor
   - blocking: 否
   - 位置:新增 hunk 在 `scripts/test_lumos.py` 約 98378 行加了 `def _sg_records(kg)`,原本 67177 行已有 `def _sg_records(kg, kind="spec-gate")`。
   - 問題:後者在載入時蓋掉前者,前面 14 個呼叫端(67229 到 68262 行)現在都走新版,舊版的 `kind` 參數成了死碼。
   - 實際影響:我用 grep 確認沒有任何呼叫端傳 `kind=`,新舊行為等價,所以不會翻紅。但之後有人想傳 `kind` 會靜默失效。
   - 佐證:`ruff --select F811` 對這個檔本來就有兩筆舊的重複定義警告,專案沒有強制,所以不會被閘擋下。
   - 改法:新測試直接用舊版,刪掉新版。
   - 引句:「+def _sg_records(kg):」

2. `t_docs_catalog_count_wording` 的檢查 ③ 是恆真式
severity: minor
   - blocking: 否
   - 位置:該測試的 ③。
   - 問題:`_docs_command_count_claims(ref)` 的結果必然包含 `findall(r"(\d+) 個指令的總目錄", ref)`,所以 `claims & findall` 非空,就只等於「`findall` 非空」。這等於把函式內的同一條正則在測試裡重寫一次,沒有獨立判準。
   - 實際影響:把 `_docs_command_count_claims` 裡 `個指令的總目錄` 那條正則拿掉,① 會紅,但 ③ 不會多抓到任何東西。真正守「reference.md 的數字等於 argparse 實數」的是 `t_docs_command_count`。
   - 改法:③ 直接斷言 `"個指令的總目錄" in ref`,語意更清楚。
   - 引句:「check("③reference.md 有總目錄那句", bool(_docs_command_count_claims(ref) & set(__import__("re").findall(r"(\d+) 個指令的總目錄", ref))), "")」

3. `t_doctor_s8_sees_worktree_home` 的檢查 ② 太弱
severity: minor
   - blocking: 否
   - 位置:該測試的 ②。
   - 問題:它只斷言 `"[S8]" in out` 和 `"src/other.py(家" not in out`,而 `(家` 只會出現在 pending 那一行的格式裡。
   - 具體改壞:`src/other.py` 的家(舊節點)在工作目錄被刪、git 裡還在。若實作改成把它錯誤地列進 bypassed 或 legacy 當成沒家,輸出是 `src/other.py` 不帶 `(家`,② 照綠。
   - 實際影響:測試名稱和 docstring 宣稱的「略過、不中斷」只驗到「沒崩」,沒驗到「列成什麼」。
   - 改法:補一條斷言,例如「`src/other.py` 在 S8 段的歸類」,用手寫的預期值。
   - 引句:「check("②工作目錄刪掉的節點略過:這段沒中斷、不出現在「家還沒提交」那行", "[S8]" in out and "src/other.py(家" not in out, out)」

4. `t_set_help_lists_keys` 的檢查 ② 的欄位清單靠 regex 抓,脆弱
severity: minor
   - blocking: 否
   - 位置:該測試的 ②。
   - 問題:用 `[a-z_]{4,}` 從 stderr 撈出「欄位名」,再用一組寫死的字(`lumos`、`append`、`decision`、`supersede`、`add`)排除。擋下訊息只要多一個英文說明詞(例如 `usage`、`field`),它就被當成欄位去對 `--help`,測試會無故翻紅。
   - 方向相反的缺口:欄位名若含中文或數字就撈不到,測試反而少檢查。
   - 實際影響:現況是綠的,風險只在以後改訊息措辭時。
   - 改法:讓擋下訊息和 `--help` 共用同一份欄位常數,測試直接比對那份常數。
   - 引句:「named = set(_re.findall(r"[a-z_]{4,}", r.stderr)) - {"lumos", "append", "decision", "supersede", "add"}」

核對過、沒有問題的部分:
- 被改掉的舊期望:`t_nodehome_check_cli_modes` ② 原本守「沒帶模式 rc2」,現在改成預設照 `--staged`。`t_home_and_note_shape_default_staged` 的前置和 ① 證明預設真的會查暫存區,③ 補回「兩個都帶 rc2」,守衛有補回。
- `t_doctor_escape_by_door` ④ 只是文案換成「規格閘當時」,正則仍有鎖住條款數與紅數。
- 新測試大多有前置斷言證明現場成立,例如 S5、S24、S29、S33、S35;`t_lint_born_old_line_quiet` 的 ① 靠 ② 的正向路徑背書。
- `t_lint_born_no_git_when_empty` 只包住 `_lens_git`,但 `_drift_disk_list` 走 `_nodehome_git` 也會呼叫 `_lens_git`。② 能數到 2 次 `ls-files`,代表包住的是對的位置。
- 第 8 角度(慣例)沒有能逐字引出規則的違反,不報。

最嚴重 severity:minor。blocking 共 0 條。
