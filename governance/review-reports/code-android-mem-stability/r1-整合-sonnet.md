severity: major

整合席報告:合約與圖譜一致。審材是 r1-snapshot-tests-docs.patch,對照程式包 r1-snapshot-code.patch。

我在自己的臨時副本跑過 `python3.14 scripts/test_lumos.py -k android_memstab`,164 項全綠。`lumos spec-trace` 顯示 S1–S16 綁了測試、S17–S19 靠人、懸空 0。`lumos lint` 對兩個家節點都是 0 問題。接下來四個發現,是「綠燈守不住文件寫的行為」,或文件跟程式對不上。臨時副本已用字面絕對路徑刪除,工作樹沒動。

## 發現

### 1. 崩潰後 App 沒被重啟時,exits 被跳過,崩潰沒被判出來
引句:「App 在量測輪中崩潰時驅動一定跟著失敗」
severity: major
blocking: 是
- 計劃 S19、S5 和 r3 設計審的 WHY 都說「驅動失敗時 exits 照判」,並特別提到「全部跳過會讓崩潰變成沒判」。
- 實際上收集腳本在最後一次讀不到 pid 時,會把 `pids` 記成 failed。file: `scripts/templates/android-stability-collect.sh:336`
- 判定端 `_ms_exits` 一開始就要求 `pids` 來源是 ok,不是 ok 就回「跳過」。file: `scripts/lumos:39912`
- 重現:用 `_ms_root` 造一份結果檔,`driver=failed`、`pids=failed`、`exits.new` 有一筆 crash。
  - 實際:`exits` 列成 `threshold_skipped`,原因是「pids 沒收到(failed)」;`strictmode` 反而列成通過,rc 0。
  - 預期:`exits` 判不過。
- 測試守不住:`t_android_memstab_source_not_ok_skipped` 的「driver 失敗」案例,`pids` 都是 ok,沒蓋到這條路徑。
- 計劃那句因果也被驗收紀錄打臉。驗收紀錄列的缺陷是「中途崩潰後 App 被重啟,前後兩次量的是不同行程」,才加了 pid 變動跳過。可見驅動不一定失敗,計劃與 `macrobenchmark-adapter` 的 WHY 都還寫著「一定」。

### 2. S18 的「App 哪一行呼叫」拿不到,驗收卻記 pass,skill 還要求寫出來
引句:「heapprofd 對 Java 那幾層只記函式不記行號」
severity: major
blocking: 是
- 驗收紀錄自己承認有落差:條款要「App 哪一行呼叫的」,實際只到函式。但 S18 條款本文沒改,驗收紀錄 `status: pass`。
- SKILL.md 新增的 L3 第 3 步要求報告寫到「哪支 .so、哪個位移、App 哪一行呼叫它」為止。
- 同一節第 1 步又寫「只到函式,沒有行號」,兩處自相矛盾。三個月後的 AI 照 skill 做,要嘛找不到行號,要嘛編一個。
- 修法:改條款與 skill 成「只到 App 函式」,或把驗收改記 pass 但註明落差。

### 3. 「結果檔標明類別名未還原」沒有實作,R8 還原路徑也沒有任何測試
引句:「這類一起編進 App 的函式庫會被改名」
severity: major
blocking: 是
- 計劃 WHY 說沒給 mapping 時,結果檔標明「類別名未還原」,這是設計審 r2 要的補償。
- 程式只寫一個布林 `"mapping": bool(mapping)`。file: `scripts/templates/android-stability-collect.sh:344`
- 全 repo 沒有「未還原」字樣,判定端也不讀 `mapping`。
- 後果:混淆建置沒給 mapping 時,排除清單擋不到被改名的 androidx、kotlin 類別,java_growth 可能誤報,輸出卻沒有任何提示。
- `load_mapping`、類別名還原、陣列後綴都沒有測試。`stability` 段的 `adb_serial`、`max_record_s` 在 S1–S19 裡也沒有條款或測試。

### 4. S7 收集腳本那半沒有綁到會守它的測試
引句:「收集腳本只收量測開始之後的日誌」
severity: minor
blocking: 否
- S7 只綁 `t_android_memstab_strictmode`,那支只測判定端,用手寫的 `status`。
- 突變實驗:把收集腳本的 `"-T", t0` 拿掉,`collect_driver_status` 與 `strictmode` 兩支測試仍 11/11、4/4 全綠。
- 原因是假 logcat 不管 `-T`,一律印整份檔。
- 「沒宣告 strictmode 時記 unsupported」「串流中斷記 failed」在收集腳本端也沒測試。

### 5. S4 的官方分級表只守到兩個級距
引句:「依結果檔的 total_mem_mb 與 category 照官方區間查前景上限」
severity: minor
blocking: 否
- 把 `MACROBENCH_VITALS_FG` 後三級改成跟前一級同值,`t_android_memstab_peak_vitals_floor` 仍全綠。file: `scripts/lumos:39779`
- 沒測到 9216–14336 與 14336–18432 兩個級距,遊戲也只測 4800–6800 一級。
- 計劃 WHY 逐字列了這些數字,卻沒有測試守它們。

### 6. S16 與程式對不上:沒有 INSTRUMENTATION_CODE 一律當成功
引句:「UI Automator 輸出沒有 INSTRUMENTATION_CODE: -1」
severity: minor
blocking: 否
- 程式只在輸出裡已經出現 `INSTRUMENTATION_CODE` 時才檢查 -1。file: `scripts/templates/android-stability-collect.sh:151`
- 實測:driver 輸出 `INSTRUMENTATION_FAILED: …` 或 `INSTRUMENTATION_RESULT: shortMsg=Process crashed.`,且回傳碼 0,結果是 driver `ok`。
- 我不能碰實機,不確定 `am instrument` 啟動失敗時回傳碼是不是 0。若是 1,這個洞就被回傳碼擋住,所以只列 minor。
- 這是為了讓 Maestro 輸出(沒有標記)判成功而做的取捨,但計劃寫的是「要看到」。

### 7. S15 條款字面與實作不同
引句:「當設定的 test_data 宣告不是帶署名與日期的 true 時」
severity: minor
blocking: 否
- 條款說「不錄快照、heap 是 unsupported」。實際上只有不寫 `test_data`、或寫 `value:false` 才是 unsupported。
- 寫成 `test_data: true` 這種格式不對的值,是 rc 2 擋下、不寫結果檔。
- rc 2 比較保守,行為合理,但條款要照實改,測試名也該說明。

### 8. 家節點與計劃有幾處過期或自相矛盾
引句:「有 stability 段時 results_dirs 可以不填,沒有 macrobench.json 也照判 check 條目」
severity: minor
blocking: 否
- `Systems/macrobenchmark-adapter` 本文第 43 行還寫 `results_dirs` 必填(引句「(必填,結果目錄清單)」,patch 裡是未動的 context 行),跟同篇新增的 WHY 相反。frontmatter 的 `updated` 也沒更新。
- `Projects/Android效能判定統計化_計劃` 的白話、REVISIT(引句「照下面五條開設計」)、S1 都說五條,清單卻有六條。
- 驗收紀錄寫「四條人驗條款(S16–S19)」,實際人驗只有 S17–S19,S16 是綁測試的。引句:「四條人驗條款(S16–S19)在測試專案」
- 計劃 WHY 說預設排除清單含基本型別陣列、門檻檔可改。實際上 `exclude_prefixes` 只換前綴清單,基本型別陣列永遠排除。引句:「預設不算 java.、javax.、kotlin.、android.、androidx.、dalvik.、libcore.、sun. 開頭的類別與基本型別陣列,門檻檔可以改排除清單」

### 9. 逐層診斷計劃沒標出新的跳層路徑與例外
引句:「直接進 L3,不先走 L1、L2」
severity: minor
blocking: 否
- 逐層診斷計劃的「四層與往下條件」表(35–37 行)沒寫 L0 可以直接跳到 L3。
- 它的 WHY(第 20 行)「不選:每次都錄 Trace+CPU 取樣+記憶體」也沒指到新計劃的例外。例外只寫在新計劃那一側(引句:「那條照留;這裡是例外」)。
- S6 的條件被改成 `stability.test_data`,但佐證仍是 2026-10-23 的 s05,當時這個機制還不存在。S9 的「人裁的 L3 授權」也沒跟著改。
- 缺分支:沒有 `test_data` 的專案,native_unreachable 沒過時,skill 說「直接進 L3」,L3 又被鎖,L1、L2 又看不到記憶體。skill 沒說這時怎麼辦。

### 10. skill 與參考文件的缺口
引句:「看 run 目錄裡的結束紀錄與」
severity: minor
blocking: 否
- 「run 目錄裡的結束紀錄」不存在。run 目錄只有 `stability.json`(內含 `exits.new`)、`logcat.txt`、`cycle.pftrace`、`record.pbtxt` 和兩份快照。
- `peak_vitals → L3` 是 skill 加的,計劃第 5 點沒有。
- `logcat.txt` 與 `cycle.pftrace` 不受 7 天刪除規則管,也不受 `test_data` 宣告管。
- 收集腳本會呼叫 `lumos macrobench --check-config`,所以實際需要 Python 3.14 以上(`scripts/lumos:76`)。reference.md 沒寫,只有收據重跑腳本寫「python3.7 以上」。
- `run-id` 只收英數字、點、底線與連字號,參考文件沒寫。
- 門檻檔的 `check` 條目只有欄位表,沒有可抄的 JSON 範例。
- reference.md 的 Maestro `repeat times: ${CYCLES}` 已在文中與計劃 REVISIT 坦承沒實測,這點誠實,不列為缺陷。

### 11. 棧別效能表態記錄不是這次改動的
severity: minor
blocking: 否
- 表態寫的是「待決問題解析、受測場次、回答保存上限」,對應 file: `scripts/scenario_probe.py:1077`。
- `git diff --stat 7d17bd73..1e47929e` 沒有 `scenario_probe.py`。這次改動是 Android 收集腳本與 lumos macrobench,表態記錄拿到的是另一批改動。
- 這次新增的收集腳本會一次讀完整份 `logcat.txt`。沒有任何一題是針對它作答的。

## 固定席逐條判斷
- `lumos-cli-read` 的 ★INVARIANT★(search 預設排除 superseded):沒碰到 search,不受影響。
- `pitfalls-code-loop`、`loop-convergence-recording`:這次只動 `scripts/lumos` 的 macrobench 與 `_VENDORED_TREE_FILES`,沒動它們的規則,不受影響。
- `guard-kill`、`測試假綠形態`、`bound-tests-gate`:沒碰 guard kill,也沒改 bound-tests 閘。新測試的「還原翻紅釘」多半有前置斷言(例如 kill -0、force-stop 順序),但發現 4、5 顯示仍有突變存活。
- `design-loop` 第五步(.md 計劃、條款有 [SN] 時任一條款要有 [綁定測試:有]):計劃是 .md,S1–S16 有綁測試,符合。
- `lumos-cli-lifecycle`:我跑了 `t_vendored_file_list_matches_what_install_ships` 和 `t_reinject_preserves_outside`,都綠。

最嚴重 severity:major,blocking 共 3 條(發現 1、2、3)。

相關檔案(絕對路徑):
- /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos
- /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-stability-collect.sh
- /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md
- /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/docs/lumos-toolchain-knowledge/Projects/Android逐層診斷_計劃.md
- /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md
- /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/skills/lumos-android-evidence/SKILL.md
