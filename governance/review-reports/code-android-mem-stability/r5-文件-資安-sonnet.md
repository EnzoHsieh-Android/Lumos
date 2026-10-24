severity: minor

# 第 5 輪資安席(文件包):報告

我讀完整包 r5-pkg-docs.patch,對照工作樹真檔(`scripts/templates/android-stability-collect.sh`、`scripts/lumos` 的 macrobench 段)。第四輪修補差異(5fc4e715 到 cacb4d3f)我也單獨看過。結論是文件側沒有 blocker 或 major,只有三條 minor。三條都屬於「照 skill 平常操作就會踩到」的類型,不是外部攻擊。

## 三類逐類結論

**①提示注入:已看,無。**
- skill 叫 AI 讀的外部可控文字只有三處:`stability.json` 的 `exits.new[].desc`、`logcat.txt`、`lumos macrobench --stability` 的文字輸出。
- `logcat.txt` 只留含 `StrictMode policy violation` 的那一行,堆疊後續行不收。
- 文字輸出已過 `_events_clean`(控制字元與 U+2028 換成空白、截長)。
- `desc` 來自系統的 ApplicationExitInfo,不是 App 能自由寫的欄位,我想不出一條「誰送什麼、AI 照做」的路。
- 另外 SKILL.md 與 reference.md 會讓 AI 執行 `macrobench.json` 的 `driver`(`sh -c`)。但這份檔是使用者自己專案的檔,跟同專案的 Gradle 腳本信任等級一樣,在單人模型下不算洞。
- 套件名進 adb 指令和 SQL 前都有 `[A-Za-z0-9_.]+` 檢查,run-id 也有限制。

**②讀寫與執行越界:有一條,見 finding 1。**
- 收集腳本自己的路徑沒問題:
  - 產物目錄對 7 個檔名各問一次 `git check-ignore`。
  - 7 天清理只刪 `heap-*.pftrace`,遇到捷徑就跳過。
  - `logcat.raw` 在正常、串流斷掉、被中斷三條路都會刪。
  - 裝置上的 `lumos-stability-<run-id>.*` 會刪,`java-profile-*` 的殘留也已明寫要自己 `ls` 後再刪。

**③非刻意的守衛繞過:有一條,見 finding 2。**
- `test_data.value` 我實跑了 `--check-config`,字串 `"true"` 被擋,只有布林 `true` 通過,跟 SKILL 的「value 是 true 才錄」一致。
- `stability_unjudged` 和 `threshold_skipped` 都有明寫不能記成 L0 通過。判定程式對來源 `status` 不是 ok 時一律列成跳過,不會變成通過。
- 7 天清理只在收集腳本下次開跑時才執行,reference.md 已寫「不再跑就不會刪」,所以不算守衛被繞過。
- 有一點屬於非 diff 的既有狀況:`SKILL.md` 收尾第 4 步叫 AI 把「收據目錄與原始檔」交給沒脈絡的子代理。原始檔包含 L3 快照,而「不准做的事」寫了不上傳記憶體檔到公共模型。子代理只透過 trace_processor 回傳查詢結果,且 L3 只在 `test_data=true` 才錄,所以我不列為 finding。

## 圖譜鏡頭與殘留

- 固定席節點(`lumos-cli-read`、`bound-tests-gate`、`guard-kill` 等)講的是 `scripts/lumos` 與 `scripts/test_lumos.py` 的合約。文件包只動筆記與 skill 文字,不會破壞它們宣稱的行為。
- 殘留問答:派工詞說算不出來,我也沒有去翻 `governance/residual-index.json`。這包是文件,看不到問答編號或 checker 變動,這題無法回答。

## Findings

### 1. L3 用 heap_profile 會在系統暫存目錄留一份完整轉檔,文件沒提
severity: minor
blocking: 否
引句:「放在產物目錄底下才會被 git 忽略」
- 攻擊路徑:
  - 誰:照 SKILL.md L3 第 1 步操作的 AI 或使用者。
  - 從哪:`heap_profile -n <套件> --heaps com.android.art -d 10000 -o .lumos/artifacts/android/<run-id>/heap-profile-<名>/`。
  - 送什麼:完全照文件做的正常執行。
  - 拿到什麼:文件宣稱只有這個目錄要自己刪,其他都在產物目錄裡。
- 證據(我取 Perfetto v57.2 的 `tools/heap_profile` 實際讀過):
  - `process_trace` 呼叫 `traceconv profile`。traceconv 把 pprof 轉檔寫進它自己的暫存目錄 `heap_profile-*`(binary 裡 `heap_profile-`、`Wrote profiles to %s`、`TMPDIR` 相鄰)。
  - 腳本把檔案複製到 `-o` 目錄後就結束,全檔沒有 `rmtree` 或 `os.remove`。所以系統暫存下的那份永遠留著,不在 `.gitignore`、7 天清理和文件的「自己刪」清單裡。
  - 裝置端 `/data/misc/perfetto-traces/profile-<UUID>` 只在成功拉回後才 `rm`。adb 中途斷線時殘留,文件只提了 `java-profile-*` 的殘留。
- 限制:我沒有實跑 traceconv,暫存位置是由字串和腳本邏輯推出來的。heapprofd 的內容是呼叫堆疊加大小,不含記憶體內容,所以敏感度低,列 minor。
- 建議:L3 第 1 步補一句「跑完另刪系統暫存下的 `heap_profile-*`,中斷時 `adb shell ls /data/misc/perfetto-traces/` 看過再刪 `profile-*`」。
- 歸因:有證據的原有漏查。5fc4e715 的舊文字也是 `-o <目錄>` 而且沒提暫存。這輪只是把 `-o` 寫實,把「放在底下才會被 git 忽略」說得更滿。

### 2. SKILL.md 的 test_data 範本寫成 `decided_by: 誰`,字面的「誰」能通過 --check-config
severity: minor
blocking: 否
引句:「{"value": true, "decided_by": 誰, "decided_at": YYYY-MM-DD}」
- 攻擊路徑:
  - 誰:照常操作的 AI(或趕時間的使用者)。
  - 從哪:要錄 L3 時編輯 `.lumos/macrobench.json`,照 SKILL.md 那一行把它補成合法 JSON。
  - 送什麼:`"decided_by": "誰"` 加今天日期。
  - 拿到什麼:保存規則(人裁的 test_data)被意外繞過,收集腳本照錄 Java 快照,沒有人裁過。
- 實跑(用 `lumos macrobench --repo <臨時專案> --check-config`):
  - `decided_by` 為 `<裁定的人>`:被擋。
  - `decided_by` 為 `誰`、`TBD`、`AI`,`value` 為 `true`:都印「macrobench 設定與門檻檔都合格」。
  - `value` 為字串 `"true"`:被擋。
- 第 4 輪的修補只擋角括號佔位。reference.md 也承認「改成別的假名字它分不出來;真正的防線是先問人」。但「先問人」只寫在 reference.md 的範例旁。SKILL.md 的「不准做的事」只描述格式,沒有「AI 不得自己寫這個宣告、一定要先問人」的句子;只有第 8 步在 check 沒過時才說「請人裁要不要宣告」。
- 建議二選一:
  - 把 SKILL.md 範本改成跟 reference.md 一樣的 `"<裁定的人>"`(這樣會被擋)。
  - 或在 SKILL.md 補上「這個欄位只能照使用者的回答填,AI 不能自己寫」。
- 歸因:有證據的原有漏查。5fc4e715 的 SKILL.md 就是 `decided_by: 誰`;第 4 輪修補沒回歸,只是沒補到這個寫法。

### 3. 計劃筆記說 java_hprof「不含字串與位元組內容」,沒有證據,而且與釘住版本的結構矛盾
severity: minor
blocking: 否
引句:「快照可能含個資:java_hprof 不含字串與位元組內容;只准在宣告了測試資料的專案錄」
- 攻擊路徑:
  - 誰:照這句話判斷敏感度的後續 AI 或使用者。
  - 從哪:讀這份計劃(同樣的句子也在「用到的詞」那一段)。
  - 送什麼:無,是事實斷言本身。
  - 拿到什麼:低估快照的敏感度。在 L3 步驟查詢和收據 `report.md` 寫入時,不會特別避開字串欄位。
- 證據:
  - 專案釘住的 trace_processor v57.2 結構裡,`heap_graph_object` 有 `value_string`,註解是「Decoded string value for java.lang.String instances」。
  - 另外有 `heap_graph_primitive` 和 `array_data_id`,是原始型別欄位與陣列內容。
  - repo 內搜不到這句話的實測依據(`Verification` 和 `skills` 都沒有)。
- 限制:我不能碰裝置,也沒有樣本快照。所以不知道 Android 16 的 ART `java_hprof` 實際有沒有填這些欄位,結論只是「這句沒有證據,而且與工具結構相悖」。
- 保存規則(test_data 閘、本機 7 天)本身不依賴這句話,所以只是 minor。
- 建議:改寫成「是否含字串與陣列內容未驗,一律當含個資處理」。或讓實驗室拿 `heap-after.pftrace` 跑一次 `select count(*) from heap_graph_object where value_string is not null`,把結果寫回。
- 歸因:未判定。5fc4e715 的舊版本就有同樣句子,不是修補回歸。

最嚴重 severity:minor,blocking 共 0 條。

相關檔案:
- /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/code-android-mem-stability/r5-pkg-docs.patch
- `file: /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos`:`_macrobench_signed_err`、`_macrobench_stab_optional_err`(只擋角括號佔位)
- `file: /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-stability-collect.sh`:`prune_old_snapshots`、`preflight`

我的臨時目錄 `/private/tmp/lumos-seat-work/code-android-mem-stability/文件-資安-sonnet` 已刪,刪前 `lsof +D` 沒有程序開著。
