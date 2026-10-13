severity: minor

邊界-sonnet 席的結果:上一輪對比較模式路徑防線、事件片段濾控制字元、處置閘診斷指令的修補,我實測後沒有找到 major 以上的問題。以下兩條是新發現,都是小問題。

比較模式實測:我用複本 `scripts/lumos` 在實驗目錄造了 23 種帳上路徑,實際跑了 `--compare-rules`。
- 通過防線:符號連結指到 repo 外、符號連結迴圈、FIFO、目錄、`/dev/zero`、`/dev/null`、權限 000、非 UTF-8、空檔、`../` 逃出 repo、Windows 反斜線、5000 字元長路徑、含 NUL、孤立代理字元、`/etc/passwd`、`/dev/zero` 絕對路徑。
- 這些路徑全部歸入「讀不到」或「非 UTF-8」,沒有 traceback,也沒有卡死。
- repo 本身是符號連結或路徑含 `..` 時,結果都一致。
- 大型輸入:20MB 單條引句、200000 條引句、30 萬層巢狀引號、100 萬個零寬字元,新判準都在 0.6 秒內、約 244MB 以內。

事件片段實測:雙向控制字元 U+202E、零寬字元、組合字、全形空白、emoji、U+2028/2029 都能正確處理,片段排在 note 最後,偽造的 `report=` 或 `id=` 只會出現在尾端。

1. 片段全是控制字元時,note 尾端變成空的 `quote=`
severity: minor
blocking: 否
引句:「snippet = "".join(c for c in re.sub(r"\s+", " ", first) if unicodedata.category(c) not in ("Cc", "Cf")).strip()[:60] if first else "-"」
file: `scripts/lumos:25830`
- 輸入:引句內容整段是 U+202E、U+200B、ESC、BEL 或 NUL。
- 走到:`first` 為真,濾掉 Cc/Cf 後得到空字串,寫成 `quote=`。
- 壞在:沒有引句時的占位是 `-`,現在「沒有引句」和「引句被濾光」會分不出來。目前沒有程式讀 `quote=`,只有人讀帳會困惑。
- 同一行的順序也不理想:先對整條引句逐字元濾過再切 60 字。legacy 判準(目前寫側用的)的引句不設上限,實測一條 1000 萬字元的引句,單單這個函式就花 2.7 到 4 秒、峰值記憶體約 0.9GB。先切再濾會便宜很多,但全控制字元的情況會變成更常出現空值,所以兩件事要一起改。

2. 診斷指令的路徑用 shlex.quote,但開頭是 `-` 的路徑仍會被當成選項
severity: minor
blocking: 否
引句:「_qdiag = f"    診斷:lumos quote-check {_shlex_q.quote(str(rp))} --spec {_shlex_q.quote(str(sp))} --rule {_qrule}"」
file: `scripts/lumos:26521`
- 輸入:報告或快照的相對路徑以 `-` 開頭。
- 走到:`shlex.quote` 對 `-x.md` 原樣輸出,印出的指令照抄貼上後,argparse 會把它當選項而報錯。
- 壞在:報告路徑實際上都以 `governance/` 或絕對路徑開頭,觸發機率極低。若要修,在位置參數前加 `--`,或把相對路徑補成 `./`。我標 ⚠(沒實際跑處置閘端到端)。

附帶觀察,不算本次問題:
- legacy 判準的 `「([^」]+)」` 遇到大量沒閉合的「會變成 O(n²)。實測 5000 行未閉合約 1.6 秒、20000 行約 22 秒,100000 行超過 2 分鐘。新判準同樣輸入只要 0.03 秒。這是舊判準原有的行為,但比較模式現在會對帳上每份報告都跑一次 legacy,且 `_quote_compare_rules` 沒有防線。對真實報告不構成威脅。
- 比較模式的 `old_only` 清單會把帳上的 `rp` 原樣印到終端。只有該檔真的存在於 repo 內才會走到,風險低。

實驗目錄 `/tmp/lumos-seat-work/code-引句錨定整段比對/r2-邊界-sonnet/` 已刪除,過程中沒有改動 repo 內任何檔。

總結:最高等級 minor,blocking 共 0 條
