severity: major

# 合約與圖譜一致(整合)第 2 輪報告

- 審查對象是 `r2-pkg-docs.patch`,工作樹為 `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability`,HEAD 為 44d93aba。
- 我讀完整包文件,再對照 `scripts/lumos`、`scripts/templates/android-stability-collect.sh`、`scripts/test_lumos.py` 的真檔。
- 沒有碰 adb 或裝置。收集腳本的行為是用測試檔裡的假 adb 與假驅動,在自己的臨時目錄重現,暫存已用字面絕對路徑刪除。

## 發現

### 1. 日誌串流中斷或收集被中斷時,未過濾的原始日誌 `logcat.raw` 會留在磁碟上,與「原始串流算完就刪」不符
severity: major
blocking: 是
引句:「落地的 logcat.txt 只留違規那幾行,原始串流算完就刪(日誌常含帳號、權杖、網址,代碼審 r1 資安席)」
- 失敗場景:專案宣告 `strictmode: true`,日誌串流在量測中途斷掉(或收集腳本被 SIGTERM),run 目錄會留下完整的 `logcat.raw`。
- 預期:計劃 S22(只留違規那幾行)與上面這句話都說原始串流不留。
- 實際:`strictmode_result` 在「串流沒開成或中途斷了」時先 return failed,沒有執行後面的 `os.unlink(raw)`。
  - file: `scripts/templates/android-stability-collect.sh:377-380` 是 early return 在 `os.unlink(raw)` 之前。
  - file: `scripts/templates/android-stability-collect.sh:440-449` 的 `cleanup()` 也沒刪 raw。
  - 自動清理只刪 `heap-*.pftrace`(同檔 `:92-107`),所以這份檔不會被自動清掉。
- 重現(`44d93aba`):用 `_ms_collect` 的假 adb,放 `logcat_dies` 旗標跑一次。
  - `strictmode` 為 `failed`,run 目錄檔案為 `['cycle.pftrace','logcat.raw','record.pbtxt','stability.json']`。
  - 正常路徑只剩 `logcat.txt`。
  - 假 adb 串流一開就結束,所以 raw 為空檔。真實串流中途斷掉時,檔裡會有已收到的內容。這部分是讀程式碼推得,沒有實跑。
- 修前(`1e47929e`):整份日誌直接寫進 `logcat.txt`,正常與異常路徑都留,沒有 `logcat.raw`。
- 測試缺口:`t_android_memstab_collect_logcat_scope` 與 `t_android_memstab_collect_cleanup` 都沒有斷言「串流中斷」或「SIGTERM」之後 run 目錄裡沒有 raw。
- 歸因:有證據的原有漏查。修補只修了正常路徑,但新寫進文件的「算完就刪」承諾在異常路徑不成立。

### 2. S18 的人驗說明還寫「呼叫行」,同一條後半卻寫只到函式;驗收紀錄聲稱已改
severity: minor
blocking: 否
引句:「收據 L3 那筆寫明留住的欄位或 .so 位移與呼叫行」
- 同一條 `[manual:]` 後面寫「App 那層到函式(heapprofd 不記 Java 行號)」,前後自相矛盾。
- `Verification/2026-10-24_Android記憶體與穩定性實驗室驗收.md` 寫「計劃 S18 與 skill 都改成『到 App 的函式』」,但 S18 這一行仍留著「呼叫行」。
- 修補確實改過 S18 那一行(`r2-repair-docs.patch` 第 143、144 行),但把「呼叫行」留下了。
- 歸因:有證據的修復漏改。兩版 S18 都含「呼叫行」,修前 `git grep` 與修後 `r2-repair-docs.patch` 計數皆可見。

### 3. 計劃「資料怎麼流」的收集腳本回傳碼與步驟已跟腳本對不上
severity: minor
blocking: 否
引句:「其餘情況都寫出結果檔並回 0,哪一段沒收到寫在那個來源的 status」
- 實際上還有四種情況回 2,且不寫結果檔:
  - run-id 不合法。
  - `.lumos/artifacts/` 沒被 git 忽略。
  - `stability.mapping` 指的檔不存在。
  - 收到 SIGTERM 或 Ctrl-C。
  - file: `scripts/templates/android-stability-collect.sh:325,335,198,467`。
- S24 與 reference.md 有寫其中幾種,但計劃的流程段沒寫。
- 流程段步驟 1 到 2 也漏了「先 `am force-stop`,而且在讀前一次結束紀錄之前」(腳本 `:401-402`,collector 節點的 PITFALL 有寫)。
- 三個月後的人照計劃的步驟寫驅動或接 CI,會以為腳本永遠回 0。
- 歸因:有證據的修復回歸(文件漂移)。擋下類回傳碼(git 忽略檢查、run-id 驗證、SIGTERM)是 `9c67b337` 加的,腳本修前沒有 `check-ignore`,但計劃那句沒跟著改。

### 4. 計劃的 `--update-baseline` 訊息引文與實際輸出不同,而且沒有 macrobench.json 時文字會說錯
severity: minor
blocking: 否
引句:「有 `stability` 段時 `results_dirs` 可以不填(這時 `--update-baseline` 印」
- 文件寫「印『沒有 results_dirs,不更新基準』」。
- 實際輸出是「這個專案的 macrobench.json 沒有 results_dirs,沒有 Macrobenchmark 結果可以更新基準。」(file: `scripts/lumos:40070`)。
- 我另外跑了一個完全沒有 `.lumos/macrobench.json` 的專案加 `--update-baseline --stability`,同樣印這句,說「macrobench.json 沒有 results_dirs」。檔案其實不存在,訊息誤導。
- 回傳碼 0 與測試的斷言不受影響。
- 歸因:未判定。這份計劃是新增的,我沒有逐字比對修前版本。

### 5. 收據那段自相矛盾:快照查詢「驗得到」與「expect=-(不比對)」
severity: minor
blocking: 否
引句:「收據只驗得到每份快照單一類別的實例數」
- 同一段又說快照那兩條查詢寫 `expect=-`(只記錄、不比對)。
- `android-heap-classes.sql` 檔頭也寫「expect 寫 -:快照 7 天後會被刪,寫了 expect 重跑會誤報」。
- 實際是收據對快照什麼都驗不到(file: `scripts/templates/android-receipt-rerun.sh:52`,`expect=-` 直接 continue)。
- 實際只有追蹤檔那條 `cycle` 查詢會比對。
- 歸因:未判定,這份文件是新增的,修前沒有可比版本。

### 6. SKILL 與 reference 的保留規則寫得比實況寬
severity: minor
blocking: 否
引句:「檔名照 `heap-*.pftrace`,7 天後才會被刪」
- 實際上只有「有人再跑收集腳本」時才刪,而且只刪 `.lumos/artifacts/android/<run-id>/` 底下一層(file: `scripts/templates/android-stability-collect.sh:92-107`)。
- 計劃 WHY 的「代價」有寫「專案不再跑收集腳本時舊快照不會被刪」,SKILL 沒帶這個但書。
- reference.md 的保留清單寫「`cycle.pftrace`、`logcat.txt`、`stability.json` 不自動刪」,漏列兩個會留下的檔:
  - `record.pbtxt`(腳本 `:263` 寫進 run 目錄,從未刪除,我在重現的 run 目錄看到它)。
  - 發現 1 的 `logcat.raw`。
- 引句同樣取自 SKILL。
- 歸因:未判定。

### 7. `frozen → L1` 沒說 L1 要用哪份追蹤檔,L1 的步驟對這條路徑不適用
severity: minor
blocking: 否
引句:「`frozen` → L1;`exits` → 看 `stability.json` 的 `exits.new`」
- SKILL 的 L1 段寫「用 L0 那次執行留下的 Trace,不另錄」,主要對象用結果檔的 `sampledMetrics.frameOverrunMs.runs[i]` 挑「超時格最多的那一輪」,基準 Trace 取自 Macrobenchmark 結果檔。
- `stability.json` 路徑只有一份合併的 `cycle.pftrace`(約在 `reference.md:119` 才被提到),沒有逐輪 Trace,也沒有 `frameOverrunMs`,也沒有基準 Trace。
- 逐層診斷計劃說「frozen 沒過照原本 L1」,但跳不過去。
- 歸因:有證據的原有漏查,屬 skill 新寫的跳層規則,修補前後都沒補。

### 8. 驗收紀錄沒有釘到被驗的版本,修補後沒有重跑證據
severity: minor
blocking: 否
引句:「收集腳本與判定為 2026-10-24 android-mem-stability 分支版本」
- 同一份紀錄的 `revalidate_when` 寫「收集腳本的步驟順序或判定規則改動」要重驗。
- `9c67b337`(13:14)在實機驗收之後又改了:
  - 判定:崩潰類不靠 pid、`classes_seen`、欄位嚴格。
  - 收集腳本:`python3 -P`、驅動獨立程序群組、日誌改走暫存檔再過濾、`ps` 判錄製。
- 紀錄沒有 commit 或重跑時間,S17 到 S19 的「全過」無法對到現在的版本。
- macrobench-lab 工作樹不在本機可讀路徑,我驗不了。
- 歸因:未判定。

### 9. S24 的 Big5 語系條款在沒有 Big5 語系的機器上整段不跑,也不出聲
severity: minor
blocking: 否
引句:「主機語系是 Big5 這類非 UTF-8 時輸出照樣是 UTF-8」
- 綁定測試 `t_android_memstab_collect_edges` 把這段包在 `if big5 == "big5":` 裡,沒有語系就整段不執行,沒有 skip 標記。
- file: `scripts/test_lumos.py:18946-18948`。
- 這台 macOS 有 `zh_TW.Big5`,所以本機會跑。CI 的 Linux 多半沒有,這條款在 CI 沒有守衛。
- 歸因:有證據的原有漏查。

## 已查證成立

- **S1 到 S26 綁定**:
  - `spec-trace 'Projects/Android記憶體與穩定性驗收_計劃'` 在 44d93aba 顯示 26 條款、綁了 23、靠人 3(S17 到 S19)、懸空 0、壞名 0。
  - 另外,collector 節點裡引到的 9 個 `t_android_memstab_*` 測試名我逐個比對,全部存在。
  - 我抽讀 S4、S5、S7、S8、S11、S13、S16、S20、S23、S25、S26 的測試,除發現 1 與 9 外,斷言對得上條款句。
- **`lumos lint`**:六篇改動節點都是 0 問題。
- **reference.md 的範例**:
  - 把 stability 設定與三條門檻 JSON 原樣貼進臨時專案,`lumos macrobench --check-config` 回 0。
  - 再貼一份含 `adb_serial`、`mapping`、`max_record_s` 的設定,同樣回 0。
  - 修前版本沒有這份範例,「照抄能過」的修前證據為未判定。
- **欄位、環境變數與預設值**:
  - 吻合:`CYCLES` 與 `ANDROID_SERIAL`、`{{CYCLES}}` 替換、`TP`、`JAVA_HEAP_DUMP`、`ADB`。
  - 吻合:`heap-before.pftrace`、`heap-after.pftrace`、7 天保留、`max_record_s` 預設 600 與範圍 1 到 86400、`SETTLE` 預設 2。
  - 吻合:run-id 字元規則(含不能只有點)。
  - 吻合:官方分級表與區間(`scripts/lumos:39772-39773`)。
  - 吻合:exits 五種判不過類型(`MACROBENCH_EXIT_FAIL_TYPES`)。
  - 一個小提醒:`LUMOS_STABILITY_SETTLE_S` 是環境變數名,文件只寫「SETTLE 秒」。
- **`--stability` 相對路徑**:在 `sub/` 下用 `--repo .. --stability stab.json`,照目前目錄解,輸出 `exits:crash` 並回 0,與計劃一致。
- **Python 版本**:
  - 「python3 要 3.11 以上」成立。腳本沒有版本守衛,低版本會直接吃 python 自己的用法錯誤(同為 rc 2、無「擋下:」)。
  - 腳本用同一個直譯器叫 lumos。lumos 要 3.14,找得到 3.14 會自動重跑(`scripts/lumos:243-262`),找不到就擋下。實際下限是「同一台機器要有 3.14」,reference.md 的「工具鏈本身要求 3.14」有帶到,但沒說明這個連動。
- **跳層與沒授權**:`逐層診斷_計劃` 與 SKILL 對 L0 到 L3 的跳層、沒有 `stability.test_data` 時停在 L0 並記 `[GAP] L3 未授權`,彼此一致。四種記憶體類 check 直達 L3,frozen 走 L1,exits 與 strictmode 看現場檔。
- **WHY/PITFALL 與既有決定**:
  - 沒有矛盾,「只提醒不擋」承襲 2026-10-23 的裁決。
  - 「每次都錄」那條否決被明講保留並說明例外。
  - 統計化計劃對 step fitting 的引用,與 `Macrobenchmark退步提醒_計劃` 的「第一版先不做」一致,只是統計化計劃寫成「否決」,字眼稍重。

## 三問

1. **原問題的修復效果有何行為證據?**
   - 本席只審文件,行為證據只有自己跑的:
     - 日誌過濾:正常路徑只留 `logcat.txt`,修前整份留下,有改善。
     - 其餘修補(崩潰類不靠 pid、`classes_seen`、欄位嚴格)的行為,我只用 `spec-trace` 與測試名核對綁定,沒有逐條重跑。
   - 發現 1 證明異常路徑的承諾沒有守住。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 正常路徑與範例設定檔仍成立。
   - 相鄰的異常路徑:日誌串流中斷、SIGTERM 時 raw 殘留(發現 1)。
   - 文件相鄰處:回傳碼敘述(發現 3)、S18 說明(發現 2)有漂移。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - 發現 1:修前整份日誌恆落在 `logcat.txt`,修後正常路徑只留違規行、異常路徑留 `logcat.raw`。
   - 發現 3:修前沒有那四種擋下,修後有但計劃沒更新。
   - 發現 2:兩版 S18 都含「呼叫行」。
   - 其餘發現是文件內部或文件對程式的不一致,沒有可對照的修前行為。

## 修復案例與保留案例

- **修復選例(日誌過濾)**:修前整份日誌落地;修後正常路徑只留違規行,證據是 `_ms_collect` 假 adb 重現(`normal` 組只有 `logcat.txt`)。修後異常路徑殘留,見發現 1。
- **保留選例(`--check-config` 合法範例、`--stability` 相對路徑)**:修後成立,證據同上。修前沒有 `--check-config` 範例,未判定。
- **案例檔**:我沒有讀 `r2-behavior-cases.json`,沒有補案例。

## 圖譜鏡頭(固定席)

- **Issues/vendored測試套件在消費端假紅**:不影響。新的 `t_android_memstab_*` 只讀 `scripts/templates/`(會被 vendored),不碰 `docs/` 或 `skills/`。對這點的 grep 沒找到來源專用路徑。
- **Systems/lumos-cli-read**(search 預設排除 superseded):不影響,diff 沒動 search。
- **Systems/測試假綠形態**:不影響合約本身。順帶指出發現 9 就是這類「條款有綁定,但那段測試在某些環境不跑」的缺口。
- **Systems/bound-tests-gate**:不影響。`spec-trace` 綁定 23 條,懸空 0。
- **Systems/guard-kill**:不影響,這包沒動守衛殺傷力。
- **Systems/lumos-cli-lifecycle**(re-inject 只覆蓋 sentinel 之間):不影響。
- **Systems/design-loop**(`[SN]` 條款必須有 `[綁定測試:有]`):驗收計劃有綁;統計化計劃只有 `[manual:]`,是 todo 且未進設計審,現在不觸發。
- **表態記錄**:`infra-path` 與 `infra-pid` 聲稱的行號大致對得上。`sql-nplus1` 背書「沒有」,不算行為證據。
- **殘留問答**(編號、改字、checker 是否為另一個代理):未驗。我沒有讀 `residual-index.json` 與治理帳,此題未判定。

## 未驗範圍

- `scripts/lumos` 判定邏輯與兩支 SQL 查詢的完整正確性,屬程式與測試包。
- 真機上的 `dumpsys` 輸出格式。
- macrobench-lab 實機是否在修補後重跑。
- 計劃 PRIOR-ART 引用的外部網址內容。

最嚴重 severity: major,blocking 共 1 條(發現 1)。其餘 8 條皆 minor、blocking 否。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-stability-collect.sh`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/test_lumos.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/skills/lumos-android-evidence/SKILL.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/skills/lumos-android-evidence/reference.md`
