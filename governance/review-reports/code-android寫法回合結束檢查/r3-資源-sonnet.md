severity: minor

臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/資源-sonnet` 已刪。沒有動 repo,沒有留 gctl-run-*。

審查範圍是 `r3-repair-甲.patch`,也看了 `r3-repair-乙.patch` 的資源面。我用 `git clone --shared` 複製 HEAD 8717114b0,配上假的 `ast-grep` 實跑。

**第二輪資源席 F1–F3 逐條核對**

- **F1(改過的大 .kt 整份讀進記憶體):程式已改,「50 支各接近 5MB」的實測未跑完。**
  - 現在先問大小,超過上限的不讀(`_nodehome_cat_sizes` 加 `_nodehome_cat_blobs_capped`)。
  - 上限是 5MB,一回合最多 50 支,所以讀進來的上限約 250MB。
  - 預期:最大常駐比底線 375MB 多約 500MB,大約 0.9GB。上一輪實測 40 支約 4.3MB 的檔是 996MB,這次的上限邏輯不會比它更差。
  - 未跑完的原因:我造 50 支約 5MB 檔案的實驗卡住,被協調者停掉。
- **F2(SARIF 無大小上限):已修好,實測有效。**

  | 假工具輸出 | 結果 |
  |---|---|
  | 約 36MB(12 萬條告警) | 5.3 秒,最大常駐 846,036,992 位元組 |
  | 約 59MB(13.5 萬條告警) | 6.0 秒,最大常駐 903,888,896 位元組 |
  | 18 萬、22 萬條(超過 64MB 上限) | 2.2 到 2.5 秒,最大常駐 467,812,352 與 566,394,880 位元組,回 `env-unavailable`、`unchecked_kind` 為 failed,不讀內容 |

  - 上一輪 60 萬條是 2GB,現在被上限擋在約 0.9GB。
  - 鉤子端收 34MB 的 `--json` 輸出再解析,實測最大常駐 296,108,032 位元組。
- **F3(暫存 SARIF 殘留):已修好。**
  - 超過上限的路徑結束後沒有殘留暫存檔。
  - 系統暫存區裡有一個 0 位元組、前晚 22:52 留下的舊 `lumos-lint-*.sarif`,不是我造的。它只有幾小時,還沒到一天的清掃門檻,所以沒被掃掉。

**程序群組收尾(用真鉤子、真 lumos、假 ast-grep 睡 300 秒,逐個 pid 查)**
- 鉤子收到 SIGTERM、SIGINT、SIGHUP 各一次:lint-new 與工具程序都在鉤子結束後消失,`.lumos/` 底下沒有快照目錄殘留。
- 記帳檔 `<會談>.pgids` 在信號路徑會留一個空檔,因為只有動用 SIGKILL 才會刪。
  - `_hookshared._cache_dir_under_home` 會清掉超過 7 天的標記,所以不是只增不減。這條不標。

**F1 工具輸出不設寫入上限,失控時一秒多 GB 寫滿暫存區**

這輪只加了讀取上限,工具的標準輸出直接接到暫存檔,寫入端沒有限制。
- 實測:假 `ast-grep` 用 `yes` 一直吐資料,預算 5 秒。暫存 SARIF 在約 3 秒內長到 3.7GB,速率約 1.3GB/秒。
- 預設預算約 28 秒的話,推算約 36GB,會超過這台機器 29GB 的剩餘空間。
- 限制:工具結束後暫存檔會被刪,逾時會殺群組,所以不會永久留下;只有檢查工具本身失控才會發生。
- 修法方向:開程序前用 `RLIMIT_FSIZE` 限制在比 `_LINT_SARIF_MAX_BYTES` 略大的值,或定期看檔案大小。

引句:「stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.DEVNULL)」
file: `scripts/lumos:41190`
severity: minor
blocking: 否

**F2 64MB 的 SARIF 上限仍讓主程式吃到約 0.9GB**

上限是檔案大小的 64MB,解析後約 8 倍的記憶體,最大常駐比底線 375MB 多約 530MB。工作樹模式的 `new` 清單全數放進 `--json`(13.5 萬條時 34MB),鉤子再整份收下並解析。
- 它有上限、不會無限長大,所以不標 major。
- 如果要壓低記憶體,可以把上限降到 16MB 左右,或限制 `new` 的條數。

引句:「content = f.read(_LINT_SARIF_MAX_BYTES + 1)」
file: `scripts/lumos:41210`
severity: minor
blocking: 否

**其他量到的成本**
- 列過濾器設定的 `git config` 每個程序只跑一次(有快取)。
- 一般小檔、3 條告警的整次 lint-new 是 1.5 秒,最大常駐 373,522,432 位元組,主要是 lumos 本身載入的底線。

總結:最嚴重是 minor(F1 寫入端不設上限、F2 上限仍讓記憶體到約 0.9GB),會擋 0 條。第二輪 F1–F3 的程式都已改對,但 F1 的 50 支大檔實測未跑完。
