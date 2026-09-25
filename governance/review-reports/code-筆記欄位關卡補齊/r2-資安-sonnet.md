severity: clean

逐類檢查:

## 1. 不可信輸入流到危險操作(路徑注入/命令注入/反序列化/eval)

已看,無。這輪改動只有四塊:①`_note_lint_config` 找 repo 根從 `_repo_root_from_env` 換成 `_vault_repo_root`;②`.lumos/config.json` 整份不是物件時的防呆;③筆記 `type` 寫成非字串時的防呆;④日期欄位空字串的防呆。四塊都只是「讀進來的值拿去跟白名單/型別比對、決定要不要在輸出字串裡報錯」,沒有新的 `eval`/`subprocess`/反序列化/檔案寫入路徑。`about_code` 這種本來就是別人寫得動的欄位,這輪完全沒碰,沿用既有的 `_about_code_path` 檢查。
引句:「值看不懂=當 on」

②的新檢查把攻擊面往下收(壞掉的設定檔以前悄悄被當沒設,現在至少會警告),不是新增風險:
引句:「.lumos/config.json 整份不是物件,筆記欄位新規則用預設(只提醒)」

`_vault_repo_root`(往上找 `.git`)本身是這次審查前就存在的函式,這輪只是把兩個呼叫點從 `_repo_root_from_env` 換過去用。理論上它會往上走到第一個帶 `.git` 的祖先目錄,但那個祖先目錄的位置是使用者把 repo clone 在哪裡決定的,不是 repo 內容(攻擊者可控的部分)能左右的——攻擊者能控制的只有 repo 裡面的檔案,控制不了 repo 被 clone 到磁碟上哪一層,所以不成立「惡意 repo 讓工具讀到 repo 外的設定檔」這條路徑;而且就算讀到別的 `.lumos/config.json`,能改的也只是 `note_lint.gate` 是 on/warn/off,不會被拿去執行或組指令。
引句:「往上找 .git;代碼審 r1:圖譜在 repo 根、巢狀、monorepo 深層都曾讀錯」

## 2. 登入與權限
略(無登入機制,這輪也沒碰)。

## 3. 密鑰與個資:錯誤訊息會不會把磁碟上的內容印出來

已看,無。新增的例外訊息只印 `_ex.__class__.__name__`(例外類別名),不是 `str(_ex)`,不會把檔案內容或例外訊息細節印出來;設定檔讀不了的分支沿用同一慣例。
引句:「lint 讀這篇時出錯({_ex.__class__.__name__})」

## 4. 加密與傳輸
略(無,這輪沒碰)。

## 5. 執行邊界:hook/安裝腳本/CI 會不會執行不可信位置的檔;路徑解析跟著捷徑跑出 repo;讀設定檔時捷徑的處理

已看,無。讀 `.lumos/config.json` 的捷徑檔(symlink)判斷這輪沒改,沿用既有的 `via_link` 檢查,只是包進回傳字典裡:
引句:「via_link = p.is_symlink() or (p.exists() and p.resolve() != Path(repo_root).resolve() / ".lumos" / "config.json")」
沒有新的檔案執行、shell 呼叫或子行程,測試裡新增的 `subprocess.run(["git", "init", "-q", str(root)], check=True)` 用list參數、無 `shell=True`,不吃字串拼接,不構成命令注入。

## 6. 行動端
略(無,這輪沒碰)。

## 補充:try/except 廣義捕捉

`_lint_collect`/`_lint_new_rules` 外層新增 `except Exception` 把單篇壞筆記的例外轉成該篇的錯誤訊息,讓整圖健檢不會被一篇壞筆記整個打斷。這屬於可用性/健壯性修正(避免 DoS 類當機),依規則不報;也沒有吞掉安全相關的錯誤路徑(只吞的是「這篇筆記格式讓 lint 邏輯炸掉」這類,不影響 about_code/設定檔的既有驗證邏輯)。
引句:「一篇讀不懂的筆記不能讓整個健檢當掉——列成那篇的錯」

## 結論

這輪 r2 差異是防呆/重構(repo 根改用既有的 git 感知函式、設定檔非物件防呆、type 非字串防呆、日期空字串防呆),沒有新增不可信輸入到危險操作的路徑,沒有新增會外洩磁碟內容或密鑰的錯誤訊息,沒有新的執行邊界被打開。判定 clean。
