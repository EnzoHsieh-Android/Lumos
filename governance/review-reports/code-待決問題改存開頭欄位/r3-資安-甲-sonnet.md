severity: minor

我逐類看過,沒有可直接利用的洞,只有一條縱深防禦類的小發現。

**發現 1:`_pq_renames` 把範圍字串拆出的 base、head 直接當 git 引數**
severity: minor
blocking: 否
引句:「r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "-M", "--name-status", "--diff-filter=R", base, head, "--"],」
- file: `scripts/lumos`(patch 第 461 行,`_pq_renames`);`_pq_push_remind` 的 base 來自 `_range_base`。
- 攻擊路徑(推論):誰需要能控制 `lumos spec-gate --push` 的範圍字串,例如一個包住 pre-push 的惡意包裝腳本。送 `--output=/某路徑..HEAD`。`_range_base` 用 `split("..")` 取左端,`--output=...` 原樣成為 `git diff` 的選項,git 會把 diff 輸出寫進那個檔案。
- 為何只算 minor:正常 pre-push 傳進來的是 sha,陌生 repo 的檔案內容改不了範圍字串。要控制範圍字串就已經能直接執行任意程式,所以沒有權限提升。
- 修法:`-M` 後加 `--end-of-options`,或先檢查 base、head 不以 `-` 開頭。同一個形狀在既有的 `_range_base` 的 `merge-base` 呼叫(`a`、`b` 同樣未隔離)也有,可一起處理。

**逐類結論**
1. 不可信輸入流到危險操作:已看,除發現 1 外無。
   - 改名輸出的路徑含 tab 或換行:`core.quotePath=false` 時 git 仍會把 tab 與換行加引號轉義,`len(parts)==3` 對不上就略過。含 tab 的路徑只會被跳過,不會被誤解析。
   - 路徑含換行:`_nodehome_cat_blobs` 本身整批拒絕,不會注入 `cat-file --batch` 的輸入流。
   - 決策連結讓重讀跳出圖譜:已看,無。重讀用的 `node` 只來自 `env.notes` 的鍵或索引命中,連結字串從不直接進 `Path`。帶 `..` 的連結只做字典比對,對不上就回 missing 或 bad。
   - 終端注入:題目文字、決策連結等值先過 `_pq_bad_char`(涵蓋 Cc、Cf、Zl、Zp、Cs),所以 ESC、C1、雙向覆寫都進不來。錯誤訊息裡的原始片段都用 `!r` 或 `ascii()` 輸出,鍵名受 `[A-Za-z_]` 限制,題號格式不對時用 `ascii()` 跳脫。無。
   - 命令列兩支寫入指令:值經 `_pq_fmt` 再驗一次控制字元,並走 `_yaml_plain_ok` 或 `_yaml_quote`,不能換行就不能偽造新鍵。無。
2. 權限與守衛繞過:已看,無。
   - 惡意 repo 讓規格閘放行:讀不懂的清單走「無法判定」並回 1,不會放行。
   - 重複鍵、頂格旗標、tab 縮排、`[]` 後接題這些繞法都被擋。
   - `_vault_locked` 加上 `atomic_write_verify` 的檢查是「任一把鎖被持有」(`any(_VAULT_LOCK_HELD.values())`),不是「本筆記庫的鎖」。這只是漏包時的保險網,不是安全邊界。鎖位置的決定與鎖檔信任是既有邏輯,這次沒改。
3. 密鑰與個資:已看,無。沒有新增 log 或環境變數輸出。
4. 加密與傳輸:已看,無。
5. 執行邊界:已看,無。
   - 新增的 git 呼叫都是 list 形式,沒有 `shell=True`;`_pq_renames` 有逾時,錯誤時回空。
   - 沒有 eval、pickle、yaml.load。
6. 行動端:不適用。
- 新依賴:無。

severity: minor
——只有 `_pq_renames` 的引數隔離一條縱深防禦建議(推論,blocking: 否),其餘各類已看,無。
