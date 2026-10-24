severity: major

審查席:資源-sonnet,r2,被審包 r2-pkg-templates.patch。我預設子程序會變孤兒、預算會被撐爆來找洞,結果找到 4 條 finding,最嚴重 major。

用的假工具照 `scripts/test_lumos.py` 的 `_ms_collect` 做法,在我自己的臨時目錄跑,沒碰 adb 連著的裝置。修前 1e47929e、修後 44d93aba 各取出一份 worktree 對跑。收尾已把 worktree 和臨時目錄刪掉,沒有殘留程序。

## Finding 1:逾時後 `p.communicate()` 沒有上限,T_LONG 對有子程序的工具失效

severity: major
blocking: 是
歸因:有證據的修復回歸

引句:「kill_group(p) if group else p.kill()
        p.communicate()」

這兩行取自 `run()` 的 `except subprocess.TimeoutExpired` 區塊。

- **成因**:group=False 時(`java_heap_dump`、`trace_processor`、一般 adb)逾時只殺直屬子程序。它底下的孫程序若還握著 stdout 管線,後面無上限的 `communicate()` 會一直等到孫程序自己結束。
- **修前為什麼不會**:修前用 `subprocess.run`。它在 POSIX 逾時後只做 `kill()` 加 `wait()`,不讀管線,所以會準時回來。
- **場景**:`java_heap_dump` 是 skill 的 shell 腳本(內容見下方命令),它背景起了子程序(如裝置端 perfetto 或 adb)。
- **預期**:逾時後回報「逾時」並繼續往下。
- **實際**:卡在孫程序結束為止,預算形同取消。

命令:`python3.14 t1.py <pre|post>`。假 jhd 內容是 `sleep 25 &` 接 `sleep 25`,`LUMOS_STABILITY_LONG_S=3`。修前版因為沒有這個環境變數,我複製一份把 T_LONG 常數改成 3 來跑。

| 版本 | 工作目錄 | 退出碼 | 總耗時 | heap 結果 |
|---|---|---|---|---|
| 修前(T_LONG 改成 3) | 臨時 worktree | 0 | 12.0 秒 | 逾時(3 秒) |
| 修後(`LONG_S=3`) | 臨時 worktree | 0 | 52.2 秒 | 逾時(3.0 秒) |

修後的兩次快照各多等約 25 秒,等於孫程序的壽命。真實場景是孫程序活 30 分鐘,整個收集就被卡 30 分鐘。

## Finding 2:SIGTERM 落在「日誌串流已從 state 拿掉、還沒收掉」的空窗,`adb logcat` 變孤兒

severity: major
blocking: 是
歸因:有證據的原有漏查(修前也有孤兒),修補留下的洞,另外多了新檔殘留

引句:「died = stop_logcat(state.pop("lc"))」

- **成因**:這行先把日誌串流從 `state` 拿掉,才進 `stop_logcat`。`stop_logcat` 內先 `time.sleep(SETTLE)`(預設 2 秒),之後還有 `lc.wait(10)`,這兩段 SIGTERM 都會打中。此時 `cleanup()` 在 `state` 裡找不到 `lc`,不會殺它。
- **場景**:驅動剛跑完、`stop_logcat` 的 SETTLE 期間送 SIGTERM。
- **預期**:`adb logcat` 被收掉、日誌暫存檔刪掉。
- **實際**:`adb logcat` 繼續活著,而且還握著 `logcat.raw`。

命令:`python3.14 t2.py <pre|post> settle SIGTERM`(SETTLE 設 4 秒,logcat 出現後 1.5 秒送 TERM)。

| 版本 | 退出碼 | 孤兒 | run 目錄殘留 |
|---|---|---|---|
| 修前 | -15 | 有 `adb logcat --pid=100` | `logcat.txt` |
| 修後 | 2,印「裝置上的錄製與暫存已收掉」 | 有 `adb logcat --pid=100` | `logcat.raw` |

修後訊息宣稱收乾淨,但孤兒和原始日誌檔都還在。

## Finding 3:SIGTERM 落在 `stop_record` 的 TERM 還沒送出前,裝置上的錄製沒被停,暫存檔卻被刪

severity: major
blocking: 是
歸因:有證據的修復回歸。修前沒有這條 finally,也沒有 TERM 處理,所以修前是整條路徑沒處理,不是這個形狀。

引句:「rec = state.pop("rec")」

- **成因**:`rec` 被拿出 `state` 後交給 `stop_record`。`stop_record` 的 `finally` 只做 `rm -f`,不補 TERM,而 `cleanup()` 也已看不到 `rec`。
- **場景**:`stop_record` 第一次 `perfetto_alive`(`ps`,慢機器或裝置卡頓最多 120 秒)還沒回來時收到 SIGTERM。
- **預期**:`kill -TERM` 送出,或由 `cleanup` 補送。
- **實際**:`kill -TERM` 沒送,只刪設定檔和追蹤檔。背景 perfetto 繼續錄到 `max_record_s`(預設 600 秒),寫進已 unlink 的檔,佔裝置儲存。

命令:`python3.14 t5.py <pre|post>`(假 adb 讓 `ps -A` 睡 4 秒,第一次 `ps` 發出 1 秒後送 SIGTERM)。

| 版本 | 退出碼 | perfetto 收到 TERM | adb 記錄最後幾筆 |
|---|---|---|---|
| 修前 | -15 | 否 | 停在 `ps` |
| 修後 | 2 | 否 | `ps` 之後是 `rm -f 設定檔 追蹤檔`,沒有 `kill -TERM` |

修後多印「收集被中斷,裝置上的錄製與暫存已收掉」,與事實相反。

## Finding 4:`logcat.raw` 在串流中斷或被打斷時不刪,原始日誌永久留在磁碟

severity: minor
blocking: 否
歸因:有證據的修復回歸。修前沒有原始檔,日誌直接寫成保留的 `logcat.txt`;修後新增了「原始串流會刪」的承諾。

引句:「if not started or died:
        return {"status": "failed", "reason": "日誌串流沒開成或中途斷了"}」

- **成因**:`strictmode_result` 在這個提早回傳之前沒有 `os.unlink(raw)`。`cleanup()` 也不刪 `raw`。
- **清不掉的原因**:`prune_old_snapshots` 只清 `heap-*.pftrace`,所以這份檔永遠留著。
- **場景**:串流中途斷線,或收集被打斷。
- **預期**:不含只留違規行的承諾被破壞,不該留下未過濾日誌。
- **實際**:`logcat.raw` 整份留在產物目錄。

命令:`python3.14 t3.py <pre|post>`(假 adb 的 logcat 立刻退出)。修後 run 目錄有 `logcat.raw`,strictmode 為 failed。SIGTERM 與 SIGINT 兩個情境(`t2.py post driver ...`)也都留下 `logcat.raw`。

## 修補差異必答三問

**① 逾時、SIGTERM、SIGINT、例外時的收尾,新的程序群組與 on_term 是否每條路都有效**

驅動(`group=True`)這條確實修好了:

| 命令 | 修前 | 修後 |
|---|---|---|
| `t2.py <pre|post> driver SIGTERM` | 驅動、sleeper、`adb logcat` 全成孤兒;錄製沒收;退出碼 -15 | 無孤兒,錄製收了(`termed: True`),退出碼 2 |
| `t2.py <pre|post> driver SIGINT` | `sleeper` 成孤兒 | 無孤兒 |

SIGINT 我只送給 python 一個程序,沒測真實終端機。真實終端機的 Ctrl-C 會一併打到同一前景群組的 `adb logcat`,所以結果只可能更乾淨。

修補沒蓋住的路徑:
- 非群組子程序逾時後的 `communicate()` 卡住(Finding 1)。
- `state.pop` 之後、清理責任交接前的空窗(Finding 2、3)。
- 第二個 SIGTERM 落在 `cleanup()` 或 `finally` 內。`on_term` 沒有被重置也沒有防重入,會中斷收尾。這條我沒實跑,不列 finding,範圍未驗。

**② 時間預算在大輸入、慢機器上的行為**
- **T_SHORT = 120 秒**:裝置離線時每個 `shell()` 都等滿 120 秒。收集有數十次呼叫,打斷時 `cleanup` 的兩次 `shell` 也各 120 秒。修前修後相同,未列 finding。
- **T_LONG**:修後可由環境變數縮短,且驅動群組逾時有效。但 Finding 1 證明非群組工具實際上不受它約束。
- **STOP_WAIT**:新版補 KILL 的邏輯正確。
- **SETTLE**:固定秒數,未量化「串流跟不跟得上」。

**③ 大檔進記憶體、二次方工作**

- **日誌**:`logcat.raw` 約 223MB(300 萬行)的情境下,修後峰值 RSS 19MB(修前 20MB),是逐行串流,正常。
- **驅動輸出**(`t4.py <pre|post> driver`):200MB 輸出,修前峰值 688MB、修後 701MB。整份存進記憶體約 3.5 倍,兩版相同。
- **快照查詢輸出**(`t4.py <pre|post> tp`):150 萬個類別,修前 997MB、修後 975MB,相同。這兩項我認為場景不夠真實,只當觀察,不列 finding。
- **峰值查詢**:改成 LEAD 加範圍 JOIN 仍然是二次方,只是係數小了。我用 sqlite3 建同名的表跑同一支 `android-stability-cycle.sql`(`python3.14 q.py`)。

| 取樣數 | 修前 | 修後 |
|---|---|---|
| 1 萬 | 2.23 秒 | 0.94 秒 |
| 2 萬 | 8.89 秒 | 3.80 秒 |
| 4 萬 | 35.88 秒 | 15.19 秒 |

每加倍約 4 倍。預設 600 秒錄製約 2400 個取樣點,不受影響,所以不列 finding。檔內註解寫「不隨錄製長度平方成長」是不實的。若 `max_record_s` 設成數小時,這是退化邊界。

## 其他說明

- 圖譜鏡頭:`dispatch-lens` 的固定席節點(`lumos-cli-read`、`測試假綠形態`、`bound-tests-gate` 等)連到的是 `scripts/lumos` 與 `scripts/test_lumos.py`。這包只動範本檔,沒有觸及它們宣稱的合約,判不影響。
- 表態記錄裡 `infra-signal satisfied`(`collect.sh:33`)與 `infra-timeout satisfied`(`collect.sh:17`)的宣稱,被 Finding 1 到 3 反駁。
- 未驗:SIGTERM 疊 SIGTERM 的重入;真實 `java_heap_dump` 與 adb server 是否真的留下握管線的孫程序(我用假腳本構造);真實終端機的 Ctrl-C。

## 結論

最嚴重 severity:major,blocking 共 3 條(Finding 1、2、3),minor 1 條(Finding 4)。

<br>

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-stability-collect.sh`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-stability-cycle.sql`
