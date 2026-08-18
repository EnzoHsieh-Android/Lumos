作為獨立審計席，針對《精簡版 CLI 增加 update 指令》設計文件，審計結果如下：

### Finding 1: 錯誤碼靜默丟失漏洞 (Major)
引句：「產物 def main(): 行後插入 argv 前置攔截(len(sys.argv) > 1 and sys.argv[1] == "update" → return _slim_update()——攔在 argparse 前,免動子命令註冊手術;★長度守衛是硬規格,r1 light blocker:裸打 lumos 若直讀 argv[1] 會 IndexError traceback,取代原本 argparse 的友善 usage★)」
**風險描述**：照字面實作會導致 `update` 的失敗狀態被作業系統忽略。Spec 指明在 `main()` 內 `return _slim_update()`，但在 Python 慣例中，若 `if __name__ == "__main__": main()` 呼叫處未包裝 `sys.exit(main())`，則 `main` 的回傳值會被丟棄，進程將以 rc 0 (成功) 結束。這與 S1 要求的「rc2 fail loud」以及「回其 rc」合約矛盾，自動化腳本將無法偵測更新失敗。

### Finding 2: 全域旗標導致指令失效 (Major)
引句：「產物 def main(): 行後插入 argv 前置攔截(len(sys.argv) > 1 and sys.argv[1] == "update" → return _slim_update()——攔在 argparse 前,免動子命令註冊手術;★長度守衛是硬規格,r1 light blocker:裸打 lumos 若直讀 argv[1] 會 IndexError traceback,取代原本 argparse 的友善 usage★)」
**風險描述**：判準邏輯漏洞。硬編碼檢查 `sys.argv[1]` 是否為 `"update"`，將導致所有帶有全域旗標的指令失效。例如使用者執行 `lumos --debug update` 或 `python -m lumos update` 時，`sys.argv[1]` 分別為 `"--debug"` 或模組路徑，攔截器將跳過並進入 `argparse`。由於 `update` 未註冊於 `argparse`，系統會報錯「未知指令」，導致功能在合法 CLI 組合下不可用。

### Finding 3: 執行期路徑與更新目標脫鉤 (Major)
引句：「①定位固定落點 Path.home()/".lumos-slim"(兩平台同,與 get.sh/get.ps1 契約一致);②.git 不存在→rc2 fail loud+指路(手動 clone 安裝者→自己 pull+重跑 install;或重跑一行安裝)」
**風險描述**：邏輯漏洞。指令實作僅檢查「固定落點」是否存在，而非檢查「當前執行的 lumos 程式碼」是否位於該落點。若使用者同時存在手動 clone 版與一鍵安裝版，並在手動版目錄下執行 `lumos update`，程式會偵測到固定落點的 `.git` 並更新該處，但使用者當前運行的程式碼完全沒變。這會造成「更新成功」的假象，實則產生「影子更新 (Shadow Update)」。

### Finding 4: Windows 自我覆寫引發程序崩潰 (Major)
引句：「Windows 自我覆寫(install.py copyfile 蓋住執行中的 lumos.py)理論上可行(python 編譯後不鎖檔)但本輪無真機 Windows 驗證,README Windows 驗證表如實標未驗。」
**風險描述**：照字面實作會做出錯誤行為。雖然 Python 解釋器可能不鎖定 `.py` 原始碼，但若精簡版是以 `pip install -e` 或封裝後的 `.exe` 形式運行，Windows 核心會強制鎖定執行檔。當 `_slim_update` 啟動 `install.py` 嘗試 `copyfile` 覆蓋父進程正在使用的檔案時，會觸發 `PermissionError` 導致更新中斷，且可能留下毀損的半截檔案。Spec 雖標註「未驗證」，但其設計路徑在 Windows 標準環境下具備高確定性的失敗邏輯。

### Finding 5: 攔截器描述與邏輯前後矛盾 (Minor)
引句：「產物 def main(): 行後插入 argv 前置攔截(len(sys.argv) > 1 and sys.argv[1] == "update" → return _slim_update()——攔在 argparse 前,免動子命令註冊手術;★長度守衛是硬規格,r1 light blocker:裸打 lumos 若直讀 argv[1] 會 IndexError traceback,取代原本 argparse 的友善 usage★)」
**風險描述**：內部不一致。Spec 宣稱此攔截器「取代原本 argparse 的友善 usage」，但實作邏輯 `len(sys.argv) > 1` 確保了在「裸打」(無參數，長度為 1) 時會跳過攔截，進而**回退**到原本的 `argparse` 邏輯。這與「取代」一詞矛盾，且會導致 `t_slim_update_behavior` 案 ⑦ 的預期行為 (rc2) 必須依賴外部 `argparse` 的配置，而非本設計的攔截器。

### Finding 6: 安裝器存在性預檢缺失 (Minor)
引句：「⑤跑 [sys.executable, dest/install.py, "--force", "--tool-only"], 回其 rc。」
**風險描述**：判準邏輯漏洞。Spec 僅預檢了 `.git` 資料夾與 `git` 指令，但未預檢 `dest/install.py` 是否存在。若 git pull 成功但倉庫結構異常（如 install.py 被誤刪或更名），`subprocess` 將拋出 `FileNotFoundError` 導致 Traceback 崩潰，違反 Spec 要求的「rc2 fail loud」優雅報錯合約。

max severity: major