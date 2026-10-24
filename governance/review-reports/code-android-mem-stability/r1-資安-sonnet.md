severity: major

# 資安席審查報告(code-android-mem-stability r1,資安-sonnet)

先講結論:提示注入沒有可用的洞;有兩個「照平常操作就會漏接」的問題。一是 App 崩潰後沒重啟時,崩潰檢查不會判沒達,只會列成「沒判」。二是 logcat 與快照寫進專案目錄,沒有任何機制保證不進版控。

## 三類逐類結果

**① 提示注入:已看,無可利用的洞。**
- `_ms_detail` 印出的文字只有三種來源:程式內固定的類型名、門檻檔的類別名、`java_growth` 從快照取來的類別名。
- 結束紀錄的 `desc` 只存進 stability.json,沒有被印出。
- StrictMode 的類型用 `\w+Violation` 取,只含字母數字。
- `[沒判]` 原因裡會帶驅動輸出的最後 200 字(`driver()` 的 `why`)。這裡能塞自由文字,但要靠被量 App 的 UI 測試輸出,AI 又沒有照著做的理由,不夠開槍。

**② 讀寫與執行越界:除下面第 2 條外,已看,無。**
- 套件名由 `MACROBENCH_PKG_RE` 用 `fullmatch` 擋成只收 `[A-Za-z0-9_.]`,SQL 的 `__PROCESS__` 與裝置 shell 的套件名都安全。
- run-id 只收 `[A-Za-z0-9._-]`,拼進裝置路徑時有 `lumos-stability-` 前綴。
- `run_id=".."` 會讓產物落在 `artifacts/` 而不是 `artifacts/android/`,只是少一層目錄,沒有利用價值。
- `prune_old_snapshots` 有擋捷徑,只刪 `heap-*.pftrace`,看不出跳出專案的路徑。
- `sh -c` 跑 `driver` 是設計上的信賴(repo 自己的設定檔),不是新增的洞。
- mapping 路徑的 `os.path.join(root, path)` 能讀任意檔,但只用 `->` 的正則取對應,沒有印出,不構成洩漏。
- 新寫的程式與範本裡沒有密鑰,也沒有信箱,只有 SPDX 署名。

**③ 非刻意繞過:找到第 1 條。**
- Ctrl-C 發生在 `start_record` 之後、`try` 之前的短窗口時,裝置上的錄製與暫存檔會殘留。這個窗口很小,只算觀察,不開槍。
- 在別的目錄執行時會走到 `die`,不會靜默通過。
- `test_data` 宣告寫錯格式時,`--check-config` 會回 2,不會漏過。

## 發現

### 1. App 崩潰後沒重啟,`exits` 檢查被列成「沒判」而不是「沒達」

引句:「pids = src({"values": pids}, None if all(pids) else "有一次讀不到 pid(App 不在了)")」
severity: major
blocking: 是

- **誰**:照常跑驗收的使用者或 AI。
- **從哪**:`sh scripts/templates/android-stability-collect.sh`,接著 `lumos macrobench --stability`。
- **送什麼**:量測期間 App 崩潰,而且沒有被重啟。這是最常見的崩潰形態,驅動通常也會一起失敗。
- **拿到什麼**:`exits` 這道穩定性守衛被意外繞過。收集端 `pidof` 回 None,所以 `pids` 的 status 變成 failed。`_ms_exits` 一進來就要求 `pids` 是 ok,否則回 `(None, why)`。結束紀錄裡明明有 `crash`,卻只列成 `[沒判]`,而且 rc 為 0。
- **實跑**:用 `lumos macrobench --repo . --stability` 配兩份手寫的結果檔,門檻只放 `exits`。
  - `values:[100,100,null]`、`pids.status` 為 failed、`exits.new` 有一筆 crash。結果是「0 條沒達、1 條沒判」,`[沒判] s1 exits:pids 沒收到(failed)`。
  - `values:[100,100,222]`、`pids.status` 為 ok、同一筆 crash。結果是「1 條沒達」,`[沒達驗收門檻] s1 exits:crash、pid 變了`。
  - 兩者唯一差別是 App 有沒有被重啟。崩潰沒重啟反而逃過判定。
- **修法**:`exits` 的判定不應依賴 `pids` 來源是 ok。`new` 裡有 `MACROBENCH_EXIT_FAIL_TYPES` 的類型時,先判沒達;`pids` 缺值只影響「pid 變了」這一項。
- **對應計劃**:計劃把「崩潰、ANR」當成不過的條件。實作讓最嚴重的崩潰變成跳過。

### 2. logcat 全文與各種原始檔寫進專案目錄,沒有機制保證不進版控,logcat 也不會被清

引句:「lc = subprocess.Popen([ADB, "logcat", f"--pid={pids[-1]}", "-T", t0, "-v", "brief"], stdout=logf, stderr=subprocess.STDOUT) if pids[-1] else None」
severity: major
blocking: 是

- **誰**:使用者本人或照常操作的 AI。
- **從哪**:跑完收集腳本後做 `git add -A` 或 `git add .lumos`,提交後推送。
- **送什麼**:
  - 被量 App 在量測期間的完整 logcat,寫進 `.lumos/artifacts/android/<run-id>/logcat.txt`。
  - 同目錄還有 `heap-*.pftrace`、`cycle.pftrace`、`stability.json`。
- **拿到什麼**:使用者資料進版控並被推送。
  - logcat 在 `strictmode` 沒宣告時也照開串流(`lc` 的建立與 `st.get("strictmode")` 無關)。
  - 腳本只需要 `StrictMode policy violation` 那幾行,卻整份落地。
  - logcat 常含帳號、權杖與網址。
  - 7 天清理只刪 `heap-.*\.pftrace`,`logcat.txt` 永遠留著。
- **缺口**:計劃寫「快照原始檔…不進版控」,但本次 diff 沒有任何 `.gitignore`、也沒有 lumos 端的檢查。我在工作樹用 `grep -n "artifacts" scripts/lumos` 沒有找到任何處理 `.lumos/artifacts` 的程式碼。所謂不進版控只是口頭約定,跟 skill 的「寫入慣例不等於讀取保證」是同一類問題。
- **修法**:
  - 收集腳本沒宣告 `strictmode` 時不串流 logcat。
  - 宣告時只把 `StrictMode policy violation` 那幾行寫檔,或算完就刪 `logcat.txt`。
  - 收集腳本開跑時,若 `.lumos/artifacts/` 沒被 `git check-ignore` 涵蓋就擋下,或自動寫入 ignore 規則。

最嚴重 severity: major,blocking 共 2 條。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/code-android-mem-stability/r1-snapshot-code.patch`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos`(`_ms_exits`、`_ms_src`)
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-stability-collect.sh`

臨時目錄已用字面路徑刪除。
