severity: major

# 設計審第 1 輪報告:邊界-sonnet(邊界與輸入鏡頭)

實驗在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/kr-r1-work-邊界-sonnet/exp(沒動 repo)。

## F1 平台根是 git 子目錄時,配方 file 的相對基準跟 guard kill 不同,判斷函式會誤報或漏報
severity: major
blocking: 是
引句:「`os.path.realpath(平台根/file)` 不在平台根的 realpath 底下 → `outside`(不讀檔)」
file: `scripts/lumos:13240`
1. guard kill 是 `git -C <平台根> worktree add --detach wt`,再用 `os.path.join(wt, file)`(13248、13266)。我實測:平台根是 git repo 的子目錄(例 `p/app`)時,`git -C p/app worktree add` 檢出的是整個 repo 的頂層(`wt/app/a.py`),所以對 guard kill 來說 `file` 是「相對 git 頂層」。
2. spec 的判斷函式把 `file` 接在「平台根」後面。平台根是子目錄(設定 `root: "app"`、配方 file 寫 `app/a.py`,這種配方 guard kill 跑得動)時,判斷函式去讀 `<根>/app/a.py`,得 `missing`:kill-add 與 doctor P2 對一條健康的配方印假警報;反過來配方寫 `a.py` 時 guard kill 判 drifted、判斷函式回 ok(漏報)。
3. 〈做法 1〉與 PRIOR-ART 都宣稱「同一種讀法、同一種圍欄」,但圍欄的基準物件不同(隔離工作樹頂層 vs 平台根),S5 與 S6 沒有涵蓋「根是子目錄」。要嘛 spec 明寫「file 相對平台根所在 git 頂層」並用 `git rev-parse --show-toplevel` 找基準,要嘛明說只支援「平台根就是 git 頂層」並在根不是頂層時回「沒驗」。

## F2 設定檔 JSON 壞掉時 load_platforms 不會丟例外,「設定檔讀不了」這條路徑對最常見的壞法永遠走不到
severity: major
blocking: 是
引句:「設定檔讀不了,這一段算不出來,先跳過」
file: `scripts/lumos:4516`
1. `load_platforms` 遇到 `.lumos/config.json` 不是合法 JSON,只在 stderr 印「讀不了…先用預設的單一設定跑」,然後 `cfg = {}` 回 legacy 單一條目(平台名 `csharp-xunit`、root=專案根)。我實測:`{bad` → `multiplatform=False`、平台只有 `csharp-xunit`,沒有例外。只有 profile 名未知、缺 default_platform 等 `ValueError` 才會丟。
2. 照 spec 字面(「設定檔讀不了、或平台不在設定裡,不呼叫判斷函式」、S2、S4 的「設定讀不了」)實作:壞 JSON 時 doctor 與 kill-add 都不會走「算不出來/沒驗原文」,而是拿專案根當平台根。沒寫 `platform` 的配方用專案根去找 file,多平台專案(file 在另一個 repo 底下)會整批判 `missing`,doctor 列一長串錯的失配,建議還叫人「先照現在的程式改寫原文」;有寫 platform 的配方則全部「平台不在設定裡」。
3. S4 的「設定檔讀不了時應印『這一段算不出來』」測試只造 ValueError 型的壞設定就會綠,壞 JSON 才是現實事故。spec 要明寫:壞 JSON 也算「設定讀不了」(呼叫端自己先 `json.loads` 判一次,或改用不吞例外的讀法),並在 S2/S4 測試造壞 JSON 這個輸入。

## F3 配方不是物件、platform 或 invariant 型別不對時,呼叫端組平台根與印輸出的步驟會先炸
severity: minor
blocking: 否
引句:「配方的 `platform` 欄有值就用它,否則用設定檔的預設平台」
file: `scripts/lumos:13200`
1. 〈做法 1〉把「配方不是物件」歸到判斷函式裡回 `malformed`,但平台根是在呼叫函式「之前」由呼叫端從配方的 `platform` 取的;配方元素是字串或數字時,呼叫端的 `.get("platform")` 就先 AttributeError,到不了 `malformed`。
2. `platform` 若是 list/dict(手改 JSON 或壞 frontmatter),`plats[平台]` 或 `in` 檢查會 TypeError(unhashable);輸出行要的「配方 invariant 前 30 字」`[:30]` 對非字串也炸。doctor 有整段例外保護,結果是這一段整段「算不出來」,把同節點其他健康/失配的配方一起藏起來,而不是只列那一條 malformed。
3. 建議 spec 寫明:平台名與 invariant 先 `isinstance(…, str)` 檢查,不是字串一律當 `malformed` 單條列出,不要靠整段例外保護兜。

## F4 平台根不存在或在別的 repo(CI 沒 checkout)時,每條配方各印一條「檔開不了」,真因被洗掉
severity: minor
blocking: 否
引句:「開不了或讀不成 UTF-8(`OSError`、`ValueError`)→ `missing`,細節帶原因。」
file: `scripts/lumos:4546`
1. `load_platforms` 對不存在的根只印 stderr 警告、照樣把該根放進回傳值(實測 `root: "../nonexist"` 回 `.../nonexist`)。判斷函式對這種根每條配方都落到 `FileNotFoundError` → `missing`,doctor 與 kill-add 各吐 N 條「file 開不了」。
2. 〈範圍〉點名「平台根在另一個 repo」。pre-push/CI 跑 `doctor --ci` 時另一個 repo 常常沒 checkout,同一份設定在開發機全綠、在 CI 全部 missing,且 `--ci` 視同 verbose 全列,CI 日誌被洗版。spec 沒說這種情況要不要先判根是否存在、只印一條「平台根不存在,沒驗」。
3. 另外 `load_platforms` 每次呼叫都會再印一次「⚠ 平台 root 不存在」到 stderr;doctor 在 P2 呼叫它,輸出會多出 spec 沒預期的行(若有測試比對 doctor 輸出行數會受影響)。

## F5 「跟 guard kill 圍欄同一種判法」的說法在前綴比對與符號連結兩處不成立
severity: minor
blocking: 否
引句:「這跟 `cmd_guard_kill` 的圍欄同一種判法:平台根底下的符號連結,只要解析後還在根內就照讀。」
file: `scripts/lumos:13268`
1. guard kill 的圍欄是 `target.startswith(wt_real + os.sep)`,帶分隔符。spec 只寫「在平台根的 realpath 底下」,沒寫比對要帶分隔符;照字面用字串前綴實作,平台根 `/w/app`、file 寫 `../app2/x.py`(realpath `/w/app2/x.py`)會被當成在根內而去讀。也沒說 file 解析後等於根本身(file 寫 `.` 或空字串)算 outside 還是 missing(IsADirectoryError 是 OSError,實測會落 missing,但 guard kill 會判 error 逃逸)。
2. 符號連結:guard kill 看的是 git 檢出樹裡的連結。根內的絕對路徑連結指回原工作目錄時,在隔離樹裡解析後跑出樹外,guard kill 判「逃逸」error;spec 的判斷函式在工作目錄看,解析後在根內回 ok。兩邊對同一條配方結論不同,spec 沒列為已知差異(〈誠實界線〉只講了未提交改動)。
3. 建議在 S5 測試加:前綴同名的兄弟目錄、file 解析為根本身、絕對路徑連結三個輸入,並把差異寫進〈誠實界線〉。

## 其餘節
- 〈範圍〉〈回退〉〈實務隱患〉:已讀,無 finding。
- 空 `old`(`--old ""`):kill-add 的 `old == new` 檢查不擋(new 非空時),判斷函式 `count("")` = 長度+1 ≠ 1 → hits,與 guard kill 一致;已讀,無 finding。
- `old` 含 CRLF:兩邊都用文字模式(實測 `\r\n` 被正規化為 `\n`),次數一致;原文永遠找不到時細節只寫「0 次」,對使用者的提示不夠,但不構成錯行為,不另列。
- 目標檔是目錄/二進位/非 UTF-8:實測 IsADirectoryError 是 OSError、UnicodeDecodeError 是 ValueError、不是 OSError(guard kill 只接 OSError,會對非 UTF-8 直接炸,spec 的 `(OSError、ValueError)` 反而更完整),已讀,無 finding。
- 符號連結迴圈:`realpath` 不丟例外、`open` 丟 OSError(ELOOP)→ missing,已讀,無 finding。
- 筆記在 Archive:程式碼裡 Archive 只出現在 `Verification/Archive`(type 為 verification,P 段跳過規則已涵蓋),已讀,無 finding。
- 單平台舊式設定/沒有設定檔:`load_platforms` 回 legacy(平台名 `csharp-xunit`、root=專案根);配方沒寫 platform 就用預設平台,與 spec 相容;寫了別的平台名會「平台不在設定裡」,與 guard kill 一致,已讀,無 finding。
- 平台名大小寫:設定與配方比對是精確字串(實測 `ios`/`IOS` 並存),與 guard kill 一致,不另列。

最高等級:major;blocking 共 2 條
