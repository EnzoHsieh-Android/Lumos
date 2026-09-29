severity: minor

# r3 資安-sonnet 報告

## F1 印給人貼的 git add 指令沒關掉 git 自己的萬用字元,檔名帶 * 會多暫存別的筆記
severity: minor
blocking: 否
引句:「print(f"修復帳要跟筆記一起提交:\n    git add {_DRIFT_FIXES} {_drift_git_arg(cx)} && git commit")」
佐證行:file: `scripts/lumos:12188`(_guard_raw_git_path 回 git ls-files 原樣路徑,不做 pathspec 跳脫)
1. 攻擊者:能讓 PR 進來一篇檔名含萬用字元的筆記(例:`Issues/*.md`,Linux/macOS 檔名合法),內容帶 c2/c3/c4 這類可修的漂移發現。
2. 受害者照 `lumos drift scan` 的提示對它跑 `drift fix`,成功後終端印出 `git add governance/drift-fixes.jsonl 'docs/k/Issues/*.md' && git commit`。shell 層的引號沒問題(_sh_quote 有包住),但 git 自己會把 pathspec 當萬用字元展開。
3. 已實測:目錄裡有 `*.md` 與 `a.md`,`git add 'd/*.md'` 會把兩個都暫存(`M  d/*.md`、`M  d/a.md`)。受害者本機還沒準備提交的別篇筆記(在製品、含內部內容)被一起 commit。
4. 拿到什麼:縱深防禦等級——要受害者照貼、要有對應檔名;結果是誤提交本機未完成的筆記,不是任意執行。修法方向:git 指令加 `--literal-pathspecs` 或路徑前綴 `:(literal)`。
5. 同形狀的 `git checkout -- <路徑>`(寫入後驗證失敗那兩處):實測 checkout 遇到「字面檔名存在」時只還原那一個,沒觀察到多還原,所以不列為洞。

## F2 NFC/NFD 兩個同名檔並存時,乾淨檢查看的檔跟實際寫的檔可能不是同一個(推論)
severity: minor
blocking: 否
引句:「    return _nfc_child(parent, Path(plan_rel).name) is not None」
佐證行:file: `scripts/lumos:12188`、`scripts/lumos:27731`、`scripts/lumos:551`(load_vault 以 NFC 當鍵,sorted 後 NFC 拼法後到者勝)
推論,未能重現(macOS 檔案系統不分 NFC/NFD,本機無法造出並存兩檔;Linux 上才有可能)。
1. 攻擊者:PR 同一目錄同時放 `café.md`(NFC)與 `café.md`(NFD)兩個檔,git 兩個都追蹤。
2. `_phys_path` 先試 NFC 原路徑,存在就用它,與 load_vault 的「NFC 後到者勝」一致,所以寫入目標是 NFC 那個檔。
3. 但 `_drift_fix_clean_err` 用 `_guard_raw_git_path` 找 git 路徑,取 ls-files 第一個 NFC 相同者;位元組序 NFD 在前,所以乾淨檢查看的是 NFD 那個檔。
4. 結果:受害者本機對 NFC 檔有未提交的改動時,乾淨檢查照樣放行,drift fix 蓋掉這些改動;寫入後的退回提示也指向 NFD 那個檔。
5. 影響只有覆蓋本機未提交編輯、需要攻擊者刻意造並存檔名,故 minor;`..` 這一路:_phys_path 的 rel 只來自 env.notes 的鍵(rglob 產生,不含 `..`),`_drift_fix_target` 對含 `/` 的節點只認 `in env.notes`,已看,無。

## 逐類

1 注入:`_drift_sh` 建在 `_sh_quote` 上:白名單 `[\w./@%+=:,-]+` 用 fullmatch,含換行、`$`、`;`、空白、反引號、`'`、`"`、`*` 一律進 shlex.quote;`node=True` 對 `-` 開頭補 `./`,`_drift_fix_target` 去掉 `./`,再試一次繞過(`./-x`、`--x`、`$(…)`、含換行)都被單引號包住或補了前綴,未能注入。`_esc_clean` 套在引號之後,只把控制字元換空格,不會拆開引號;截斷(300)之後接的都是固定文字,沒有攻擊者內容,最壞是引號沒閉合、使用者貼了會卡在續行提示,不會執行。已看:非 node 的 `_drift_sh` 呼叫端(計劃收尾「看:」、`_issue_close_revisits`)的值以資料夾開頭,不會被當選項;`=` 開頭在 zsh 只會報錯。唯一發現見 F1(git 層萬用字元,不是 shell 注入)。終端顯示:控制字元(含 C1)已消毒;雙向文字控制字元(如 U+202E)沒擋,只影響肉眼讀到的順序、貼上的位元組不變,說不出實際利用路徑,不列。
2 權限/寫到不該寫的檔:寫入前檢查符號連結與硬連結,rglob 不跟進目錄符號連結,鎖內比指紋,原子寫入;`_plan_file_exists` 改走共用函式:先 `is_file()` 再退到 NFC 比對,比原本沒放寬(仍只做存在性判斷;plan_rel 來自 git 輸出不含 `..`);見 F2。
3 密鑰與個資:已看,無(新增輸出只有筆記路徑與行號,沒有環境變數或憑證)。
4 加密:已看,無(sha256 只用於變更偵測指紋,非安全邊界)。
5 執行邊界:已看,無(git 呼叫都是 argv 列表,沒有 shell=True;`_nodehome_git` 路徑當參數)。
6 行動端:已看,無。

最高等級:minor
