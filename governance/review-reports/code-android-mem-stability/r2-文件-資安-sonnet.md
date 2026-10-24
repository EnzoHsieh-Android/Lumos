severity: major

# 資安席報告(文件-資安-sonnet,第 2 輪,被審包 r2-snapshot-tests-docs.patch)

我用假的 adb、trace_processor 和 java_heap_dump 跑過,沒碰實機。修前版是 1e47929e,修後版是 44d93aba,兩版都用 `git archive` 取出,放在我自己的臨時目錄,報告交出前已刪。

## F1 日誌的暫存原始檔在中斷或串流斷線時沒刪,「落地只留違規行」被一個平常動作繞過
severity: major
blocking: 是

引句:「落地的 logcat.txt 只留違規那幾行,原始串流算完就刪(日誌常含帳號、權杖、網址,代碼審 r1 資安席)」

引句:「SIGTERM 時日誌串流沒有變成孤兒」

- 攻擊路徑
  - 誰:使用者本人,或照常操作的 AI。
  - 從哪:跑收集腳本時按 Ctrl-C 或被外層逾時 SIGTERM;或裝置斷線讓日誌串流自己結束。
  - 送什麼:沒有惡意輸入,只是一次平常的中斷。
  - 拿到什麼:`logcat.raw` 留在專案的 run 目錄,裡面是這個 pid 從量測起點之後的完整日誌(含帳號、權杖)。
- 為什麼會漏
  - 只有走完 `strictmode_result` 的正常路徑才 `os.unlink(raw)`。
  - 串流中斷時,函式在 `if not started or died:` 就回 failed,沒刪 raw。
  - 被 SIGTERM 或 Ctrl-C 時,`cleanup()` 只殺程序、不刪 raw。
  - 7 天清理只認 `heap-*.pftrace`,所以這個檔永遠不會被刪。
- 測試沒擋住:`t_android_memstab_collect_logcat_scope` 只在正常路徑檢查 `logcat.txt` 不含祕密,從沒檢查 `logcat.raw`;`t_android_memstab_collect_cleanup` 的 SIGTERM 案例也沒檢查。
- 緩解:gitignore 檢查會擋進版控,檔案只留在本機。
- 程式出處:`file: scripts/templates/android-stability-collect.sh:378` 與 `:440-449` 是上面兩條遺漏路徑。這一包的程式碼在另一席手上,這裡只當佐證。

兩版同一案例的實跑結果(同一組假工具,假日誌含 `token=SECRET123`):

| 案例 | 修前版 1e47929e | 修後版 44d93aba |
|---|---|---|
| 正常跑完 | `logcat.txt` 含 SECRET123(整份日誌都留) | 只有 `logcat.txt`,不含祕密 |
| 串流輸出後自己斷線(假 adb 的 logcat 輸出完就 exit 1) | `logcat.txt` 含 SECRET123 | `logcat.raw` 含 SECRET123,strictmode 記 failed |
| 量測中送 SIGTERM | 沒跑,見下 | rc=2、「擋下:收集被中斷…」,`logcat.raw` 含 SECRET123 |

- 修前版 SIGTERM 案例沒跑。修前版原本就一律把完整日誌寫進 `logcat.txt`,異常路徑只會更糟。
- 歸因:有證據的原有漏查。修補只收了正常路徑,沒涵蓋異常路徑。所以這不算回歸,是修補不完整。
- 建議:異常路徑與正常路徑都要刪 raw(例如放進 `finally`),並在測試裡斷言 `logcat.raw` 不存在。

## F2 reference.md 的照抄範例直接寫好「人裁的測試資料宣告」
severity: minor
blocking: 否

引句:「"test_data": {"value": true, "decided_by": "Enzo", "decided_at": "2026-10-24"},」

- 攻擊路徑
  - 誰:照常操作的 AI。
  - 從哪:照 reference.md「規則單源…這裡只放照抄用的寫法」整段貼進專案的 `.lumos/macrobench.json`。
  - 送什麼:範例原文,沒有人真的做過決定。
  - 拿到什麼:`stability.test_data` 守衛(「沒有人裁的保存規則,不錄 L3」)被一次複製貼上打開,而且署了真人的名字。
- 實跑:把範例原文放進 `.lumos/macrobench.json`,跑 `lumos macrobench --check-config`,回 `macrobench 設定與門檻檔都合格。`、rc=0。
- 我另外把 `decided_by` 換成 `x` 和 `AI`,同樣回 rc=0。`value` 寫成字串 `"false"`、數字 0 或 1、清單,都被擋下,所以型別檢查是嚴的。
- 計劃已承認「AI 改設定檔就能打開宣告」屬信賴範圍,但這裡是不刻意的複製貼上,不是刻意偽造。
- 影響上限:只多錄一份只有類別與大小、本機保留 7 天的快照,所以是 minor。
- 歸因:`test_data` 那行範例在修前版 reference.md 就有(`grep -c test_data` 得 2)。這是有證據的原有漏查。
- 建議:範例改成 `<填入真人姓名>` 這種不合格式的佔位,或加註「不要照抄、要問人」。

## F3 驅動逾時或被中斷時,裝置上的 Java 快照暫存檔可能留下
severity: minor
blocking: 否

引句:「裝置上的暫存檔錄完就刪」

引句:「中途失敗也刪暫存檔與裝置上的暫存檔」

- 路徑:`file: scripts/templates/android-stability-collect.sh:238` 把 `java_heap_dump` 當一般子程序跑,逾時或 SIGTERM 時直接 `p.kill()`,它沒在 `GROUPS` 裡。
- 為什麼會留:`/Users/enzo/harness/perfetto-tools-v57.2/java_heap_dump` 的 `rm -f` 只在 `adb pull` 成功後才執行。被殺時,`/data/misc/perfetto-traces/java-profile-<uuid>` 和背景的 perfetto 會留在那台共用裝置上。`cleanup()` 只清自己的 `lumos-stability-<run-id>.*`。
- 這一條只靠讀程式碼,沒實跑,因為要實機。快照不含字串與位元組內容,所以洩漏面小;重點是文件與 S23「收到 SIGTERM 時應停掉裝置上的錄製並刪暫存」的字面不符。
- 歸因:未判定。兩版的 `snapshot()` 都沒有裝置端清理,我沒有逐版對照。

## 三類逐項結論

- 類別一,提示注入:已看,無可利用路徑。
  - skill 只教 AI 看 `check` 欄位選層,以及到快照和 `logcat.txt` 找留住的欄位。
  - 類別名、結束紀錄描述只是被讀取和寫進收據的資料,沒有任何一句叫 AI 照著它們行動或執行。
  - 範例指令(`am instrument`、`maestro test`)都是固定樣板。
- 類別二,讀寫與執行越界:除 F1、F3 外已看,無。
  - 7 天清理只刪 `heap-*.pftrace`,會跳過 symlink,我跑過整套 `android_memstab_collect` 測試,59 通過、0 失敗。
  - `mapping` 只讀,而且只取 `->` 行。
  - `run-id` 和套件名都先驗過字元。
  - 驅動命令來自設定檔,文件已標明信賴等級同建置腳本。
  - 測試本身:所有寫入都在 TemporaryDirectory 內;`pgrep -f` 的樣式是自己臨時目錄的絕對路徑(每次隨機,不會打到別的會談);`kill` 只殺 pgrep 回來的自己那批。
  - 測試跑完臨時目錄是 0 個,沒有孤兒。我 `pgrep` 時看到的一個 `gctl-ms-` 程序屬於另一席。
- 類別三,非刻意繞守衛:7 天刪除、gitignore 檢查、`test_data` 型別檢查、沒宣告不錄 L3,都照步驟走過;除 F1、F2 外沒找到一步繞過。
  - 小缺口:gitignore 檢查在沒有 git 或不在 repo 時靜默略過。這是設計範圍,不列。

## 三問回答(含兩版證據)

1. 原問題修復效果:資安席 r1 的「完整日誌落地」在正常路徑確實已修。同案例修前版 `logcat.txt` 含 SECRET123,修後版只有違規行(上表第一列)。異常路徑沒修好,見 F1。
2. 修補處的正常、錯誤、相鄰路徑:
   - 正常路徑:成立。
   - 串流斷線與 SIGTERM:不成立,見 F1。
   - 相鄰的 SIGTERM 清理:驅動與日誌串流確實不留孤兒,測試通過;驅動逾時有整組殺掉。
   - 相鄰的 `java_heap_dump` 逾時:未覆蓋,見 F3。
3. 新發現的同案例兩版結果:F1 已列兩版對照;F2 只有修後版證據,修前版 reference.md 的範例同樣存在;F3 未判定。

## 圖譜鏡頭與殘留

- 本包的測試改動只新增、沒有刪改既有斷言(測試檔差異是 `-18071,20 +18071,961`,整段都是新增)。
- 固定席節點(`lumos-cli-read`、`bound-tests-gate`、`guard-kill` 等)牽連的是 `scripts/lumos` 與 `test_lumos.py`,這一包沒改它們宣稱的行為。
- 「這次新增的殘留」派工鏡頭自己說算不出來,我沒去翻 `governance/residual-index.json`,這部分未驗。

最嚴重:major,blocking 共 1 條(F1)。
