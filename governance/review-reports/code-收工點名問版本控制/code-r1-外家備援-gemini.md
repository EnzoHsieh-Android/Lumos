severity: blocker

severity: blocker
blocking: 是
敘述: `_git_status_entries` 未設定 `core.quotePath=false`。Git 預設會將含中文字元或特殊符號的檔名轉義為引號包圍的八進制字串，僅靠 `strip('"')` 無法還原路徑，導致後續 `is_code_file` 因路徑錯誤而誤判。
引句: 「rest = rest.strip().strip('"')」

severity: major
blocking: 是
敘述: 解析 `git status` 改名格式時使用 `split(" -> ")` 極其危險。若檔名本身包含該字串（合法路徑字元），解析結果會被截斷，導致取得錯誤的目標檔名。
引句: 「if "R" in code or "C" in code:      # 改名/複製那一列是「舊路徑 -> 新路徑」,要的是新的」

severity: minor
blocking: 否
敘述: 在尚未有任何提交的空倉庫（Initial commit 前）執行時，`git show HEAD:relpath` 會因找不到引用而失敗。這導致在此階段刪除無副檔名程式檔時，無法正確判斷其類型。
引句: 「r = subprocess.run(["git", "-C", str(project_root), "show", "HEAD:" + relpath],」

severity: minor
blocking: 否
敘述: 抑制重複邏輯依賴 `session_id`。若外部傳入的 payload 缺少此欄位，`sid_for_dup` 將為空字串導致 `_printed_mark_path` 回傳 `None`，進而使去重機制完全失效，退化回每輪刷屏。
引句: 「sid_for_dup = str(payload.get("session_id") or "")」

severity: minor
blocking: 否
敘述: 安全檢查從寫死路徑改為比對 `d.name`。雖然仍有家目錄解析錨定，但這放寬了在快取目錄下建立任意名稱目錄的限制；若環境中存在同名的敏感路徑，防範連結繞路的意圖可能被削弱。
引句: 「if d.resolve() != (Path.home().resolve() / ".cache" / "lumos" / d.name):」

severity: minor
blocking: 否
敘述: `_head_shebang` 僅檢查前兩個位元組。若檔案包含 UTF-8 BOM 或開頭有空行，即使是有效的腳本檔也會被判定為 False，且 `git show` 讀取二進位檔時可能產生非預期的比對結果。
引句: 「return r.returncode == 0 and r.stdout[:2] == b"#! "」

最嚴重等級、blocking 共 2 條