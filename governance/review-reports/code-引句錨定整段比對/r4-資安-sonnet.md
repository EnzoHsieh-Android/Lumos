severity: major

1. 比較模式印出帳上路徑沒過消毒,可操控終端
severity: major
blocking: 是
引句:「        print(f"  舊判過新判不過:{rp}({why})")」
file: `scripts/lumos:26782`
- 誰、從哪:能往 `docs/.canary-log.jsonl` 塞帳列的人,例如 PR 作者。這份帳列是不可信輸入。
- 送什麼:`report_path` 設成 `"\x1b]0;PWNED\x07\x1b[2J\u202e/../rep.md"`,而且 repo 裡有 `rep.md`。
  - `_read` 用 `.resolve()` 把 `..` 吃掉,所以這個路徑能讀到檔,也過得了「在 repo 內」檢查。
  - 報告內容用 `引句:「frozen snapshot text line」」`,舊判準過、新判準判格式不合,進 `old_only`。
- 拿到什麼:我用 `quote-check --compare-rules --repo <實驗目錄>` 實測。輸出原樣含 `^[]0;PWNED-TITLE^G^[[2J` 和 U+202E。
  - 維護者的終端被改標題、清螢幕,顯示方向也被反轉。
  - 同一輪修補把診斷行改過 `_esc_clean`,但這行的 `rp` 沒有。
  - `_read` 的路徑檢查沒有拒絕控制字元,所以前面的防線擋不住。
- 修法:把 `rp` 過 `_esc_clean` 再印。

2. 報告 4 MB 上限擋不住二次方時間,單份小報告可卡住比較模式
severity: major
blocking: 是
引句:「_QUOTE_COMPARE_REPORT_MAX_BYTES = 4 * 1024 * 1024」
file: `scripts/lumos:25789`
- 誰、從哪:同上,在帳上掛一份報告。
- 送什麼:報告內容是 `引句:「` 重複許多次,每個都不閉合。
- 實測:我直接呼叫 `_quote_rows` 比較兩版判準。
  - 舊判準 20000 個標籤(約 160 KB,比帳上真實最大報告 229 KB 還小)耗 4.6 秒。
  - 新判準同樣輸入只要 0.024 秒。
  - 走完整的 `quote-check --compare-rules`:5000 個標籤 0.83 秒,20000 個 5.0 秒,時間成長是二次方。
  - 3 MB 的檔案(30 萬個標籤)我等了 60 秒以上沒跑完。依二次方外推約要十幾分鐘,4 MB 約要半小時以上。
- 拿到什麼:這個上限本來要解決「一份壞報告拖住整本報表」,實際沒解決。
  - 一份遠低於上限的報告就能讓比較模式卡很久,而且不能用 Ctrl-C 以外的方式跳過。
  - 瓶頸在 `_quote_rows_legacy`,所以舊判準的二次方沒修掉。
  - 處置閘對報告完全沒有大小上限,也走這條路,但那是舊判準既有行為,不算這次新增。
- 修法:上限改到約 256 KB,或把舊判準的搜尋改成線性。

3. 片段過濾後仍能留下人眼看不見的字元
severity: minor
blocking: 否
引句:「unicodedata.category(c) not in ("Cf", "Co")」
file: `scripts/lumos:25846`
- 只濾 Cf 和 Co。Hangul filler(U+3164、U+115F、U+1160、U+FFA0,類別 Lo)、點字空白 U+2800(So)、變體選擇符(Mn)都不在其中。
- 審查席可以把這些字放進引句開頭,讓治理帳的 `quote=` 片段看起來是空的,或看起來和別的片段一樣。
- 這些字不會操控終端,也不會破壞欄位結構,片段仍排在 note 最後。我只讀了程式碼,沒實測帳的呈現。

沒找到問題的部分(都實測或讀碼確認過):
- `_read` 的繞過:
  - 解析後限 repo 內,再用 `O_NOFOLLOW`、`O_NONBLOCK` 加 `S_ISREG` 開檔。
  - 符號連結指到 repo 外會被擋,管線和裝置檔也擋得住。
  - 最後一段被換成符號連結時,`O_NOFOLLOW` 擋得住。
- 診斷行經 `_drift_sh` 和 `_esc_clean`,沒有注入。
  - 有控制字元的路徑會被 `shlex.quote` 包起來,`_esc_clean` 清掉 ESC 和 C1。
  - 引號內的換行被換成空格,照抄的路徑會和實際路徑不同,但只會指到別的檔或找不到檔,不會執行東西。
  - 方向標記 LRM、RLM、ALM(Cf)沒清,但它們在引號內,照抄的還是原路徑。這是顯示上的瑕疵。
- 判準本身:我沒有找到能讓編造引句錨定的繞過。

實驗目錄 `/tmp/lumos-seat-work/code-引句錨定整段比對/r4-資安-sonnet/` 已刪除。我沒有改 repo。

總結:最高等級 major,blocking 共 2 條
