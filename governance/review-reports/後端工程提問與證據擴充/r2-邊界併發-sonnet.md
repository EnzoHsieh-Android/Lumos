severity: major

我只看修正差異,並對 `scripts/lumos` 逐項查證。以下七條是找到的問題。邊界與併發類沒列出的項目:隨機編號撞名重試(`rel_cascade_create` 的 `O_EXCL` 先例已證明可行)、「判定先於截斷」、cochange 預設排除清單(要新增項目,規格已寫要對照),我都看過,沒有具體失敗場景,所以不標。

severity: major
blocking: 是,原始檔「位元組原樣」與「遮蔽」互相矛盾,S4 與 S6 不可能同時通過。
引句:「stdout 與 stderr 各自以位元組原樣串流寫進本機的 `.lumos/evidence/<證據編號>/`(不解碼,二進位與非 UTF-8 都不壞)」
同一份文件的遮蔽節又寫「帳上的指令與摘要,以及原始檔都套」。S4 要求「位元組完全相同」,S6 要求原始檔不得出現原值。兩者只能擇一,而且完整串流雜湊對不上遮蔽後的檔案,CI 也無法驗檔。遮蔽若在串流中做,秘密跨過寫入區塊邊界就會漏網。

severity: major
blocking: 是,「單列小於 4KB」在規格寫的截斷方式下不成立。
引句:「單列保證小於 4KB(既有追加寫法 `_ledger_append` 的上限),超過的欄位只留在原始檔目錄」
file: `scripts/lumos:20557` 的 `_ledger_append` 用 `ensure_ascii=False` 編碼,超過 4096 位元組直接丟 `ValueError`,不截斷。指令「截到 1000 字」是字元數,1000 個中文字就是 3000 位元組;含大量 `\u0000` 之類控制字元的指令,JSON 逸出後每字最多 6 位元組。再加上工作目錄、20 多個欄位和兩個 sha256,上限可能被突破。「超過的欄位只留在原始檔目錄」也沒說哪些欄位、依什麼規則。另外,C 節舊稿有「實際摘要」欄,新欄位清單沒有,遮蔽節卻仍寫「帳上的指令與摘要」,兩處不一致。

severity: major
blocking: 是,「帳檔不存在時建立」與規格宣稱沿用的寫法不相容,Windows 上的併發保證也不成立。
引句:「追加用單次寫入,帳檔不存在時建立。」
file: `scripts/lumos:20557` 的 `_ledger_append` 刻意不加 `O_CREAT`,註解寫明「confirm/prune 永不建檔」,還加了 `O_NOFOLLOW`。要建檔得另寫路徑,並處理兩個程序同時建檔的競態。同函式的 docstring 又承認 Windows「best-effort、預期單寫者」,S7 的雙程序同寫測試在 Windows 上沒有保證。

severity: major
blocking: 是,Windows 上「整群殺掉」與「退出碼為負=被訊號殺掉」做不到,規格沒有降級說明。
引句:「直接執行參數清單、不經 shell;stdin 接空裝置;開新的程序群組,逾時(預設 600 秒)整群殺掉。」
file: `scripts/lumos:17187` 的 `_kill_run` 在 Windows 沒有 `killpg`,會退回只殺直接子程序(註解也這樣寫)。孫程序(例如 gradle、docker 起的子程序)在逾時後仍會存活,下一次執行可能撞到佔住的埠。Windows 的退出碼是正數(例如 `0xC000013A`),「被訊號殺掉(退出碼為負)」永遠抓不到。不經 shell 時,Windows 的 `CreateProcess` 找不到 `gradlew` 這類 `.bat` 墊片。repo 有原生 Windows 支援(`file: `scripts/lumos:66` 的 `_IS_WIN`)。

severity: major
blocking: 是,Ctrl-C 與其他終止訊號時,子程序群組會被丟下變孤兒。
引句:「Lumos 自己被 Ctrl-C 中斷——一律記一列 BLOCKED(中斷時先寫帳再以 130 結束)」
子程序用新程序群組啟動(`file: `scripts/lumos:17181` 的 `start_new_session=True`),終端的 SIGINT 不會送到它。規格只寫了先寫帳再結束,沒寫要殺子群組,所以 k6 壓測或 Docker 指令會在 Lumos 結束後繼續跑。SIGTERM(CI 取消、關終端的 SIGHUP)完全沒處理,不會有 BLOCKED 列,留下沒有帳目的原始檔目錄。

severity: major
blocking: 是,「串流時逐行比對」沒定義超長行、二進位輸出、編碼與跨行規則。
引句:「比對在串流時逐行做,判定先於截斷。」
輸出是位元組串流,規格沒說正規式比對位元組還是解碼後文字,也沒說單行長度上限。沒有換行的 2GB 二進位輸出會讓行緩衝無上限成長,把「50MB 只留頭尾」的記憶體保護繞掉。跨行規則(`--expect-match` 能否跨行)未定義,使用者寫的正規式沒有逾時保護,可以卡死整個擷取。

severity: major
blocking: 是,`.lumos/evidence/` 的忽略清單沒有可行的落點,原始檔可能被提交進版控而收不回。
引句:「`lumos init` 與 `lumos update` 把 `.lumos/evidence/` 加進忽略清單。」
file: `scripts/lumos:23117` 的 `_ensure_docs_gitignore` 只操作 `docs/.gitignore`,內容是固定的本機帳清單;`.lumos/evidence/` 在 repo 根目錄,放進 docs 底下的忽略檔不會生效。file: `scripts/lumos:22927` 的 `cmd_update` 整段沒有任何 gitignore 處理,所以既有消費專案升級後不會自動加上。d4 要保護的「原始檔不離開本機」因此沒有機制保證。

總結:最嚴重 major;blocking 共 7 條

**固定席判定(不影響)**:設計沒有破壞圖譜節點 `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md` 宣稱的行為或合約。我沒有查到任何現行合約被這份修訂稿直接違反,上面七條都是新設計自身的缺口。
