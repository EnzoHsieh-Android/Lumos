severity: major

整份讀完,逐節意見在最後。這版新增的第 2、3 步與中斷處理有 4 條 major:`except Exception` 會吞掉 SIGTERM 與 SIGHUP、例外路徑漏收尾、先寫結果檔跟既有合約打架、e2e 逾時會丟掉第一段判定。

### F1 第二段的 `try/except Exception` 會把 SIGTERM、SIGHUP、SIGQUIT 吞掉
severity: major
blocking: 是
引句:「第二段整段包在 try/except Exception 裡,任何意外都寫成 failed 附例外類型」
file: `scripts/templates/android-stability-collect.sh:39`(`class Terminated(Exception)`);同檔 `on_term`、`stop_listening`、`main` 的 `except (Terminated, KeyboardInterrupt)`
1. 既有程式把三種訊號轉成 `Terminated`,它繼承 `Exception`,不是 `BaseException`。`except Exception` 因此會接住它;只有 Ctrl-C 的 `KeyboardInterrupt` 漏得過去。
2. 第二段進行中收到 SIGTERM(e2e 逾時先送的就是 TERM)的結果,照 spec 字面推:
   - `on_term` 先 `stop_listening()`,把所有中斷設成 SIG_IGN。
   - `Terminated` 被第二段的 except 接住,結果檔寫成 failed「Terminated」。
   - 沒有任何程式路徑呼叫 `cleanup`。
   - 腳本照常原子替換結果檔、印路徑、回傳碼 0。
3. 後果:
   - 裝置上的 heapprofd 錄製沒停(最久跑到 `max_record_s`,預設 600 秒)。
   - 設定檔與暫存錄檔沒刪,App 身上還掛著 heapprofd。
   - 後面的中斷全被忽略,腳本不可被 TERM,只剩 e2e 寬限 60 秒後的 KILL。
   - e2e 看到 rc 0,把被中斷當成正常完成。
4. S4 要驗「被中斷」,但 spec 沒寫 except 要排除 `Terminated`,照字面實作會讓這條測試的預期行為本身就是錯的。
5. 應該是:第二段只接 `Exception` 並明確排除 `Terminated`,或讓 `Terminated` 改繼承 `BaseException`。後者是改既有類別,會影響第一段;要寫進 spec。

### F2 第二段自己吞掉例外時沒說要收錄製與停 App
severity: major
blocking: 是
引句:「被中斷時 cleanup 照舊收錄製與裝置暫存,另外停 App(App 身上還掛著 heapprofd)」
file: `scripts/templates/android-stability-collect.sh:516-528`(`cleanup`)、`:543-553`(`main` 的 except 才呼叫 cleanup)
1. spec 只說「被中斷時」cleanup 收尾。第二段被 `try/except Exception` 吞掉的意外(例如 `start_record` 之後驅動、`pidof` 或 csv 解析丟例外)不經過 `main` 的 except,`cleanup` 不會被叫。
2. 具體例:`start_record` 已把 `state["rec"]` 登記、perfetto 已在背景跑,之後 `driver()` 丟 `OSError`。
   - 照 spec 字面:寫成 failed「OSError」,繼續往下。
   - 實際狀況:`state["rec"]` 還在,heapprofd 錄製沒停,裝置暫存沒刪,App 沒停。
3. 條款 S4、S8 把「意外例外」和「被中斷」分開列,S8 只驗被中斷時收尾。
4. 應該是:第二段的 except 與 finally 路徑,自己做一次 `abort_record(state.get("rec"))` 加 `am force-stop`,並清掉「第二段進行中」旗標。S8 要涵蓋意外例外。

### F3 先寫第一段結果檔,跟既有「已有結果檔就擋」的合約與 e2e 對回傳碼的處理打架
severity: major
blocking: 是
引句:「收集腳本先把第一段的結果寫成結果檔(這時 `native_retained` 段寫 failed「第二段沒跑完」)」
file: `scripts/templates/android-stability-collect.sh:381-383`(preflight 的擋重複);`docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md:38`;`scripts/templates/android-e2e-run.sh:478-486`
1. 既有 WHY 寫:同一個 run-id 已經有結果檔就回 2。理由是「沿用時這次被中斷,舊的 stability.json 還在,看起來像這次的結果」,不選的做法是開跑時刪舊檔。
2. 新設計讓「被中斷」本身就留下一份看起來完整的 stability.json,這正是該 WHY 防的情境。
   - 時間點是第二段中被 Ctrl-C 或 SIGTERM。
   - 結果:同一 run-id 重跑被擋,使用者要換 run-id。
   - `main` 的訊息仍寫死「沒寫結果檔」,現在是假話。
3. e2e 只檢查 `st.step(...) is None`(逾時或跑不起來)才中止。收集腳本被單獨 TERM 後回 2 時,e2e 照樣跑 `stability_judge`,把這份半成品當正常結果判。舊行為是檔不存在、judge 讀不到。
   - 第一段數字本身有效,但「被中斷」的訊號從檔案層消失了。
   - spec 的「回退」與「實務隱患」都沒處理這個合約變化。
4. 應該是:寫明被中斷時的回傳碼語意與訊息、結果檔是否帶「收集被中斷」標記。run-id 擋重複的 WHY 要改寫或補例外,不能只靠 S17。

### F4 e2e 單步 3600 秒逾時會連第一段已量好的判定一起丟掉
severity: major
blocking: 是
引句:「e2e 的收集步驟單步上限是 3600 秒,長情境打開前先估一次。」
file: `scripts/templates/android-e2e-run.sh:58`(`T_LONG`)、`:411-422`(`step`)、`:478-482`(逾時就 `device_stuck` 並 `break`)、`:59`(`GRACE` 預設 60 秒)
1. 打開 `native_retained` 的情境,收集總時間多一整段 W+N 輪,加停錄與查詢。收集腳本每次驅動呼叫的上限各自是 `T_LONG`(1800 秒)。
2. e2e 的收集步驟逾時時會:
   - 回 `None`。
   - 標 `device_stuck`。
   - `break`,不跑這個情境的 `stability_judge`。
   - 後面所有情境與效能測試都不跑。
3. 結論:一旦第二段把總時間推過 3600 秒,第一段早就量好的結果不被判,還拖累其他情境。這違反 spec 的「既有數字與判定不受影響」(實務隱患的量測干擾一條)與 S4,而且風險只用「先估一次」交給人。
4. TERM 之後的 GRACE 只有 60 秒,收尾最久約 4 分鐘(既有訊息)。cleanup 再多一個 `am force-stop`(每次 adb 呼叫上限 120 秒),更容易超過 GRACE。超過就被 KILL,F1、F2 的殘留變成必然。
5. 應該是:spec 要有可機械算的時間預算(例如 `T_LONG` 在第二段另設或縮短),或第二段開始前先確認剩餘預算,不夠就直接寫 unsupported 或 failed 而不跑。cleanup 順序要寫明:先停錄、後停 App。

### F5 「原子替換」只講替換,首次寫入、暫存檔位置與各中斷點的結果沒定義
severity: minor
blocking: 否
引句:「跑完原子替換結果檔:停 App → 啟動 → 讀結束紀錄與 pid → 暖機 W 輪」
file: `scripts/templates/android-stability-collect.sh:556-559`(現行 `open(out, "w")` 直寫)
1. 現行寫檔是直接 `open(out,"w")` 加 `json.dump`,被 SIGTERM 打在寫到一半會留下截斷的 JSON。spec 只對第二次說原子,第一次寫入沒寫。
   - 截斷檔會讓 preflight 判定「已有結果檔」而擋住重跑。
   - lumos 讀到會回「JSON 格式壞了」。
   - 時間點是「寫第一份之前、寫完之後、第二段中、替換當下」中的第一份寫入當下。
2. 替換需要同目錄的暫存檔(例如 `stability.json.tmp`)。它不在 `ARTIFACTS`,不會被 git 忽略檢查看到;cleanup 與 prune 也不會刪它。
   - `.gitignore` 只寫 `*.json` 時,它會進版控。
   - 在寫暫存檔與 `os.replace` 之間被打斷,會留下孤檔。
3. 寫第一份與替換的位置要在 `try` 裡還是外面,spec 沒寫。現在 `main` 的寫檔在 try 之外,替換後、`print` 前收到 TERM 會是未捕捉例外。
4. 應該是:兩次寫都走「同目錄暫存檔 → fsync → `os.replace`」,暫存檔名登記進 `ARTIFACTS`、被中斷時由 cleanup 刪,並寫明四個時間點各留什麼。

### F6 停錄欄位名寫錯,pull 與查詢的上限沒算進預算
severity: minor
blocking: 否
引句:「上限 stop_timeout_ms 預設 5000 毫秒,既有 stop_record 最多等 30 秒,夠」
file: https://raw.githubusercontent.com/google/perfetto/v57.2/protos/perfetto/config/trace_config.proto
1. TraceConfig 的欄位叫 `data_source_stop_timeout_ms`(註解「Wait for this long for producers to acknowledge stop requests. Default 5s.」)。我查 v57.2 的 trace_config.proto,找不到 `stop_timeout_ms`。實作者照字面寫進 pbtxt 會被 perfetto 拒絕。
2. 「夠」的結論本身站得住:`STOP_WAIT` 是 30 秒,大於 5 秒預設。但 `LUMOS_STABILITY_STOP_TIMEOUT` 可縮短,測試縮成 1 到 2 秒時會誤判成「停不下來」,spec 沒提這個前提。
3. `adb pull` 沿用 `T_SHORT`(120 秒)。64 MiB 緩衝在慢連線(wifi adb)可能超時。
   - 超時後本機留下半份 `heap-native.pftrace`(含個資),只靠 7 天清理。
   - 這是已知的 pull 代價,沒寫進實務隱患。
4. 查詢上限直接用 `T_LONG`(1800 秒)。spec 沒要求先對 callsite 去重再做 WITH RECURSIVE 走鏈。以每筆 `heap_profile_allocation` 列各走一遍的寫法,成本是列數乘堆疊深度。
   - 這跟 e2e 的 3600 秒步驟上限衝突,見 F4。
   - 建議寫明先對 distinct callsite 算呼叫位置、再 join 回列。

### F7 正常路徑尾端改成停 App,改變收集後的狀態
severity: minor
blocking: 否
引句:「停錄(heapprofd 在停錄時一定補最後一次傾印」
file: `scripts/templates/android-stability-collect.sh:480-512`(`measure` 現行結束時 App 仍在跑)
1. 現行收集結束時 App 仍在執行。第二段在尾端「停 App」後,後續 e2e 步驟(效能測試、`installed_sha256_after`)面對的是已停止的 App。spec 沒說這是有意的狀態變更。
2. 「第二段進行中」旗標何時清除也沒寫。停錄之後、停 App 之前被中斷,cleanup 仍會停 App,結果一致;但旗標清除的位置要寫死,否則 S8 無法寫出紅燈。

### 與 heapprofd、perfetto 併發
- 同行程已有別的 heapprofd 工作階段時,stats 的 `heapprofd_rejected_concurrent` 會被抓到並寫 failed。第 4 步已涵蓋,無 finding。
- 其他工具的 perfetto 追蹤可與 heapprofd 並存。第一段錄製在第二段開始前已停,不互撞。
- 前一次被 SIGKILL 的收集留下的 perfetto 仍佔著同行程時,新一輪會被拒絕並寫 failed,行為正確。

### 逐節意見
- frontmatter 與 decisions:已讀,無 finding。
- 白話、PRIOR-ART、實驗室實測、排行怎麼算:已讀,無 finding;`stop_timeout_ms` 的欄位名見 F6。
- 打算怎麼做第 1、2 步:已讀,無 finding。
- 打算怎麼做第 3 步:見 F1、F2、F3、F5、F6、F7。
- 打算怎麼做第 4 步:見 F6 的第 4 點。
- 打算怎麼做第 5、6、7 步:已讀,無 finding。
- 跟舊否決的差別:已讀,無 finding。
- 實務隱患:「時間」與「中斷」兩條見 F4、F3,其餘已讀,無 finding。
- 條款:S4、S8、S17 見 F1 到 F4;其餘已讀,無 finding。
- 回退與審計修正紀錄:已讀,無 finding。

### 固定席逐篇判
- `Systems/android-stability-collector.md`:會破壞合約。「同一個 run-id 已經有結果檔時回 2」的 WHY(F3)與 SIGTERM、SIGHUP 轉例外走收尾的 PITFALL(F1)都被這份設計弄破。這兩條要在實作前一起改。
- `Systems/macrobenchmark-adapter.md`:不影響。它只讀 `stability.json`,按每個來源的 status 跳過非 ok 的;新增的 `native_retained` 段不進判定。但 F3 的半成品結果檔會讓它在被中斷的情況下收到「完整但其實沒跑完」的輸入。
- `Systems/android-e2e-acceptance.md`:會破壞。「被中斷記成 unjudged」與「逾時就剩下的不跑」都假設收集腳本單步時間有界、被中斷時不留結果檔(F3、F4)。
- `Projects/Android記憶體與穩定性驗收_計劃.md`:不影響其判定條款(S1 到 S20 全看 `stability.json` 既有欄位,新段不進)。但「中途失敗也刪暫存檔與裝置上的暫存檔」那句被 F2 的漏收尾打到,屬於同一個 F2。

總結:整份最高嚴重度為 major,blocking 共 4 條(F1、F2、F3、F4)
