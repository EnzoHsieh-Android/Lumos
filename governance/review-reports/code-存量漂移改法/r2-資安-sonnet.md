severity: minor

## F1 以 - 開頭的參數被 _drift_sh 判成要引號,但 shlex.quote 對它原樣返回,沒加引號
severity: minor
blocking: 否
引句:「return v if v and not v.startswith("-") and re.fullmatch(r"[\w./@%+=:,-]+", v) else _shlex.quote(v)」
佐證行:實測 `shlex.quote("--dry-run")` 回 `--dry-run`、`shlex.quote("-x/a")` 回 `-x/a`(safe 字元集含 `-`,開頭不加引號);`scripts/lumos:27593`
1. 攻擊者:能提交筆記的 PR 作者。入口:圖譜根目錄下(不在子資料夾)取名 `--dry-run.md` 之類的筆記,或子資料夾名以 `-` 開頭。
2. `_drift_fix_hint` 與 27941 行印出 `lumos drift fix --dry-run 3 --kind c4`,被當成選項而不是節點,照貼會改變 lumos 自己的旗標(如翻成 dry-run、或 argparse 報錯)。只影響 lumos 自身旗標,不能帶出 shell 執行,所以是縱深防禦。
3. `git checkout -- …`(28164、28197)有 `--`,`git add` 的路徑以 vault 相對目錄開頭(docs/...),不受影響。
4. 修法方向:開頭是 `-` 時原路徑前補 `./`,或提示指令加 `--`。

## 已看,無(逐類)
1 注入:`\w` 在 Unicode 下匹配的字母/數字(如 `²`、中日韓字)於 bash/zsh 非特殊;全形 `；` 不在 `\w` 內,會被 shlex.quote 包起來;換行與 U+2028 不過原樣判準、被包在單引號內。`=ls` 在 zsh 只展開成 /bin/ls 路徑,沒有執行。
  - `_esc_clean` 與引號的順序:引號包在內層、_esc_clean 只把控制字元換空格(引號內語意不變),超長截斷(300/600)只會留下未閉合引號使 shell 等待續行,尾巴的 `&& git commit` 落在引號內,不會變成可執行片段;我逐個截斷位置(`'"'"'` 序列各點)推過,無法讓截斷後的殘段被當成命令。
  - 別處印照貼指令:本 diff 內新增的 `lumos drift fix`、`git checkout --`、`git add` 共 5 處都經過 `_drift_sh`;`_DRIFT_FIXES` 是常數。
2 權限/寫檔:`_drift_phys` 逐層以 NFC 比對;`load_vault` 用 `rglob`(Python 3.13+ 預設不跟隨目錄符號連結),上層目錄符號連結進不了索引;最後一層符號連結與 nlink 另有檢查。同名不同拼法(NFC/NFD)兩檔並存時 iterdir 順序不定,但兩檔都在 vault 內,不出 repo,而且 `_drift_current_finding` 之後還會重判那一行,所以不能被誘到 repo 外。⚠ 兩檔並存時改到哪一篇不確定,屬正確性而非資安。
  - 連結檢查(is_symlink)與寫入之間有 TOCTOU 時間差,要本機同時能寫檔的對手才能利用,不在 PR 攻擊面內,不報。
3 密鑰與個資:已看,無(waiver 的 reason 與修復帳不含密鑰)。
4 加密:已看,無(只有 sha256 比對指紋,非安全用途)。
5 執行邊界:`.lumos/lint-waivers.json` 以 key 雜湊放行、`rule`/`file` 為空;任何動這個檔的 PR 都能放行任意告警的雜湊,這是既有設計(需審查者看見 PR 差異),本輪 5 筆 reason 相同且指向 date.today,無法證明它們放行的是別的告警,列為推論、不算 finding。
6 行動端:已看,無(與本 diff 無關)。

最高等級:minor
