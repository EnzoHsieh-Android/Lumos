severity: minor

# 通才席(測試品質)r2 報告:測試補強包 `r2-pkg-tests.patch`

## 結論

這包測試整體紮實。我對收集腳本與判定函式共做了 24 種「改壞一處」實驗,在臨時目錄複製 `scripts/` 後跑對應測試,每次都先清掉 `__pycache__`。其中 20 種被測試抓到。沒抓到的 4 種裡,2 種是我自己的猜測被證實(下面兩條 minor),另外 2 種屬於程式碼本身多餘,不列為發現,見文末。

找不到 blocker 或 major。下面 4 條都是 minor,全屬「有證據的原有漏查」或測試設計缺口。

## 發現

### 1. `classes_seen` 的前後對調抓不到

severity: minor
blocking: 否

引句:「check("正常時 heap 帶兩份快照讀到的類別數", d.get("heap", {}).get("classes_seen") == {"before": 1, "after": 1}, str(d.get("heap")))」

- **失敗情境**
  - 輸入:`_ms_collect` 預設的 heap 是 `({"com.sdk.Player": 1}, {"com.sdk.Player": 6})`,兩份快照都只有 1 個類別。
  - 預期:before 與 after 各自記自己那份的類別數。
  - 實際:把收集腳本改成兩邊都用 after 的類別數,這條斷言照綠。
- **實跑**
  - 命令:把 `"classes_seen": {"before": len(before), "after": len(after)}` 的 before 改成 `len(after)`,跑 `python3.14 test_lumos.py -k collect_never`。
  - 結果:`6 passed, 0 failed`。
- **為何要緊**:這條斷言是用來證明「判定端分得出空快照」的收集端那一半。before 與 after 不分,判定端只要有一份是空的就判錯邊。
- **修法**:這條測試的 heap 改成兩份類別數不同,例如 before 1 個類別、after 2 個。
- file: `scripts/templates/android-stability-collect.sh:300`(`heap_result` 的 `classes_seen`)
- 歸因:有證據的原有漏查。只改壞後版一處,修前版沒有 `classes_seen`,無從比較。

### 2. `ps 只認自己那個 pid` 的對照組根本到不了腳本

severity: minor
blocking: 否

引句:「lines = ["999 surfaceflinger"]   # 別的行程:不能被當成錄製還活著」

- **問題**:假 adb 的 `ps` 自己用 `hit = [x for x in lines if want in x.split()]` 做了 grep 的工作,所以 `999 surfaceflinger` 這行在 pid 不符時根本不會輸出給腳本。
- **失敗情境**
  - 把腳本的 `any(line.split()[:1] == [pid] ...)` 整段拿掉,只靠 `rc == 0`。
  - 實跑:`no_pid_match` 實驗中,memstab 系列測試全部照綠,只有一支早就存在的 `t_scenario_probe_collect_only_and_answer_cap` 紅了。
  - 結果:新測試 `collect_edges` 的「ps 照 pid 過濾時錄製判成還在跑」註明「ps 只認自己那個 pid」,實際只釘住指令字串 `| grep -w {pid}`。
- **與真實裝置的差別**:真實裝置的 `ps | grep -w` 若回了別行,腳本自己的 pid 比對是第二道守衛,這道守衛沒有行為證據。
- **修法**:假 adb 在 `want` 對不上時,仍把 `lines` 整份輸出,模擬沒有 grep 的 ps。
- file: `scripts/templates/android-stability-collect.sh:213`(`perfetto_alive`)
- 歸因:未判定,缺修前證據。r1 時沒有這個斷言,也沒有修前版的對照命令。

### 3. 本機全域 gitignore 會讓 git repo 的兩條測試誤紅

severity: minor
blocking: 否

引句:「check("git repo 裡產物目錄沒被忽略 → 回 2 擋下、不寫結果檔", r.returncode == 2 and "gitignore" in r.stderr and not d, r.stdout + r.stderr)」

- **問題**:`git check-ignore` 會讀使用者的全域排除檔(`core.excludesfile`),測試的 `git init` 沒有隔離。
- **失敗情境**
  - 輸入:使用者全域 gitignore 裡有一行 `.lumos/`。
  - 預期:測試只依賴暫存專案自己的 `.gitignore`。
  - 實際:`GIT_CONFIG_GLOBAL=<指向含 .lumos/ 的檔> python3.14 scripts/test_lumos.py -k collect_edges`,結果 `10 passed, 1 failed`,紅的是這條斷言。
- **慣例對照**:同一檔別處的 git 測試已隔離,例如 `env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", ...)`,見 `scripts/test_lumos.py:98120`。這包新測試沒有照做。
- **代價**:換機器或使用者設定後,推送前的閘會假紅。這台機器的 `~/.gitignore_global` 沒有 `.lumos`,所以現在不紅。
- **修法**:這兩條 git repo 測試的 `sp.run(["git","init",...])` 與 `_ms_collect` 環境加上 `GIT_CONFIG_GLOBAL=os.devnull`。
- 歸因:這包新增的測試造成,修前版沒有這支測試,不屬於「修補回歸」。

### 4. `_ms_root(..., text=True)` 新參數沒人用,註解的耗時說法不實

severity: minor
blocking: 否

引句:「40 個案例直接呼叫判定函式(每案起一次 lumos 要 20 多秒);命令列那條路徑由 t_android_memstab_peak_vitals_floor 走。」

- **問題一:註解數字不實**
  - 實測 `lumos macrobench --check-config` 單次約 0.6 秒,不是「每案 20 多秒」。
  - 實際是 40 案 × 2 次呼叫(`--json` 一次、文字一次)約 50 秒,仍然值得避開,但數字要寫對。
- **問題二:新參數沒有呼叫端**
  - `_ms_root` 新加了 `text=True` 參數,全檔沒有任何地方傳 `text=False`。
  - `peak_vitals_floor` 與 `source_not_ok_skipped` 都用 `_, r, d, _ = _ms_root(...)` 丟掉文字那次輸出,白跑一次。
  - 實測:`-k peak_vitals_floor` 單支 11.3 秒,只因為每案多起一次 lumos。
- **效率與簡化代價**
  - 把這些呼叫改成 `text=False`,peak_vitals_floor 省下約一半時間,`source_not_ok_skipped` 也省約一半的子行程。
  - 或把沒人用的參數刪掉。
- 歸因:未判定。

## 其他

- **假綠與時間斷言**
  - `took < 20`:實測驅動逾時情境約 3 到 5 秒,餘裕大。
  - 實驗 `kill_outer_only`(只殺最外層)會讓 `communicate()` 等 `sleep 30`,確實紅,不是裝飾性斷言。
  - 風險:Linux CI 若環境慢到逼近 20 秒會誤紅,這點只是推測,不列發現。
- **Big5 那段**
  - 這台 Mac 有 `zh_TW.BIG5`,段落會跑。實驗 `no_utf8`(拿掉 `PYTHONUTF8=1`)讓 `collect_edges` 紅,所以段落本身有殺傷力。
  - 沒有該語系的機器(多半是 Linux CI)靜默跳過,沒有任何「跳過」輸出,這個覆蓋差異看不出來。
  - 註解寫「-I 會關掉 UTF-8 模式」已經是過時敘述:腳本現在用 `-P` 不用 `-I`,測試本身沒錯。
- **哪些實驗被抓到(20 種)**
  - 腳本:`-P` 拿掉、`-T` 拿掉、`kill -KILL` 拿掉、`lc.kill`、`abort_record`、SIGTERM handler、`run()` 的 `BaseException` 收尾、`ps` 不 grep、`deobfuscate` 的 `Class<>`、git 忽略檢查、捷徑目錄不刪、run-id 只有點、錄製開不起來也要 `rm -f`、`stop_logcat` 的 `died`。
  - 判定函式:vitals 表的一格、exits 判定的 pid 優先序、`pid 前後不同` 跳過。
  - 其他:`FAILURES!!!` 分支、「INSTRUMENTATION_CODE 必要」的過嚴判定,由既有的 `t_android_memstab_collect_driver_status` 抓到,不是新包的功勞。
- **沒抓到但不列發現的兩種**
  - `no_tp_rm`:把 `stop_record` 的 `finally` 刪裝置暫存檔拿掉,測試全綠。這是修前就有的漏查(修前 245 行已存在,新包沒有補)。屬「正常路徑沒有刪暫存的斷言」。
  - `no_groups_cleanup`:拿掉 `cleanup()` 裡的 `GROUPS` 整組殺。因為 `run()` 的例外處理已經先殺過了,這段在程式碼上是多餘的,測試抓不到是結果而不是原因。
- **三問**
  - ①②:原問題的修復效果(vitals 每級、unreadable 統一規則、收集腳本不假 ok、清理)都有行為斷言,上述實驗已逐項紅綠。
  - ③:新發現的 4 條都沒有修前版跑法,見各條歸因,證據不足的寫「未判定」,不寫整體無回歸保證。
  - 未驗範圍:沒有碰實機與 adb 連著的平板;`LUMOS_STABILITY_*` 環境變數縮短的行為,與預設值(2、30、1800)的差異沒有逐一實驗。
- **圖譜鏡頭**:固定席節點 `Systems/測試假綠形態.md` 的 ★INVARIANT★ 是「還原翻紅釘必須配前置斷言證明現場成立」。這包的 `t_android_memstab_collect_cleanup` 用 `driver.log` 計行數等量測輪開始,其餘有前置斷言,不影響合約。

清理:我的實驗暫存已刪,分別是 `/tmp/lumos-seat-work/code-android-mem-stability/通才-sonnet` 與 5 個我確認屬於自己的 `gctl-run-*` 現場。`/private/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 底下 13:28 以後還有約 20 個空殼 `gctl-run-*`,可能混有我其他實驗留的,也可能是別的會談的。我無法逐一確認歸屬,所以沒有刪,留給編排者處理。

最嚴重 severity:minor,blocking 共 0 條。
