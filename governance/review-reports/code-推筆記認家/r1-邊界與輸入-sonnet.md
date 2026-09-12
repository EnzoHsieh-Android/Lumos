severity: minor

1. 完整路徑若沒用反引號、只是直接寫在摘要或正文裡,且路徑含非 ASCII 字元(中文目錄/檔名很常見),新加的全文掃描規則抓不到,「確認過的家」會漏判成沒確認——只會少推,不會多推,但等於白寫一段文字。已用 `_node_code_ref_tokens_all` 實測:純文字 `scripts/測試檔.py` 掃出 `full=[]`,同一路徑改成反引號 `` `scripts/測試檔.py` `` 就抓到 `[('scripts/測試檔.py', '')]`。
引句:「[A-Za-z0-9_.@+\-]+(?:/[A-Za-z0-9_.@+\-]+)+」
file: `scripts/lumos:21476`
severity: minor
blocking: 否

2. 「確認過的家」的比對是逐字元完全比對(`nfc(_posix_norm(...))`,不做大小寫正規化),body 裡寫的路徑或裸檔名跟實際受版控路徑只要大小寫不同就判不確認。實測:git 記錄路徑 `scripts/Foo.py`,正文寫成小寫 `scripts/foo.py`(無反引號)判 False;正文用反引號但裸檔名大小寫不同(`` `foo.py` `` vs `Foo.py`)一樣判 False,只有完整路徑+大小寫都對才判 True。
引句:「if nfc(_posix_norm(path)) in {nfc(t) for t, _l in full}:」
file: `scripts/lumos:21512`
severity: minor
blocking: 否

3. 新掛進 about_code 的檔案,判「摘要/正文有沒有提到檔名」用的是 Python 字串 `in`(子字串比對),不是整詞比對:若新掛檔的裸檔名剛好是筆記裡另一個較長檔名的子字串(例如新掛 `a.py`、正文只提到 `xa.py`),「連檔名都沒提到」的提醒會被吃掉、不會出現。已直接驗證同款判斷式:`base="a.py"` 對 `scan="這篇管理 xa.py 這支檔。"` 回傳 True(誤判成有提到)。同一段判斷式在提交前檢查([S15] 的 `_nodehome_evaluate`)與健檢新段(doctor S11 的 `_nodehome_ledger`)各出現一次,兩處都受影響。
引句:「if base and base not in scan:」
file: `scripts/lumos:18646`
severity: minor
blocking: 否

4. 大檔門檻旋鈕 `LUMOS_IMPACT_ABOUT_MAX` 設成 0 或負數時,`int(knob)` 變成 `<=0`,而 `big = len(mine) >= int(knob)` 對「任何家數 ≥1」的檔案恆為真——不是只讓真正的大檔(≥8 篇)被排除,而是讓所有有家的檔案整批被當大檔、家這條入口對全 repo 靜默停用。實測 `_impact_knob` 搭配 env=`0`/`-1`/`-100`:即便家只有 1 篇,`big` 都判 True;env=`8`(預設)或非數字 `abc`(安全退回預設)才維持「只有 ≥8 篇才算大檔」的原意。此旋鈕文件上寫「僅供 goldset 網格消融,非使用者旗標」,一般使用者不會踩到,故只判 minor。
引句:「big = len(mine) >= int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8))」
file: `scripts/lumos:21530`
severity: minor
blocking: 否

5. ⚠ 未能重現(降權):新增的 `_impact_repo_files` 讀 `git ls-files` 用 `text=True, errors="replace"` 解碼,非 UTF-8 檔名的位元組會被替代字元污染;同一支程式檔裡既有的 `_nodehome_git` 特別寫明「輸出照位元組回,不能先被文字模式換成替代字元」並用 `binary=True`+`os.fsdecode` 避開這個問題,`_impact_repo_files` 沒有沿用這套作法。這份共用快取同時餵給裸檔名唯一性判斷與新的「確認過的家」機制,理論上非 UTF-8 檔名會被污染成錯誤 key、永遠比對不到自己;但本機 macOS/APFS 檔案系統拒絕建立非 UTF-8 位元組檔名(`OSError: Illegal byte sequence`),無法在此沙盒即時造出翻紅案例,只能以程式碼比對佐證,故降為 ⚠、不列 major。
引句:「capture_output=True, text=True, errors="replace", timeout=10)」
file: `scripts/lumos:21148`
severity: minor
blocking: 否
