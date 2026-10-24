severity: major

# 代碼審 r3 通才席(測試品質為主)報告:android-mem-stability 的 scripts/test_lumos.py

這次一共報 8 條,3 條 major、5 條 minor。

**驗證方式:** 我把 `scripts/` 複製到臨時目錄,在收集腳本 `scripts/templates/android-stability-collect.sh` 上各改壞一處,跑對應測試,清掉 `__pycache__`。

**基準:** 修後 f0d41453 的 `python3.14 scripts/test_lumos.py -k android_memstab` 是 303 通過、0 失敗,約 3 分 50 秒。

**用的臨時目錄:** `/tmp/lumos-seat-work/code-android-mem-stability/通才-sonnet/`,已用字面路徑刪光,也確認沒有留下孤兒程序。

## 三個回答

**1. 原問題的修復效果有什麼行為證據?**
- 我把修前 44d93aba 的收集腳本取出,環境變數名改成修後的名字,跑新測試。
- 命令:`python3.14 -B scripts/test_lumos.py -k memstab_collect`。結果是 10 條斷言紅。
- 紅的項目:
  - 原始日誌 `logcat.raw` 沒刪(含中斷空窗兩處)。
  - 快照工具逾時整組殺那條(62.7 秒,超過上限 20 秒)。
  - 兩個中斷空窗的日誌串流孤兒。
  - 停錄製之前沒有送 `kill -TERM`。
  - `.gitignore` 只寫 `*.json` 沒擋下。
  - PYTHONPATH 同名模組被載入。
  - 同一個 run-id 已有結果檔沒擋下。
- 修後版本:同一批測試全綠,沒有這些紅。

**2. 修補處的正常、錯誤與相鄰路徑是否仍成立?**
- 修後全綠(303 通過)。
- 針對本輪修補我各做一個故障變體,測試都紅了:
  - `state["lc"]` 改成先拿掉再停:紅在「等日誌跟上」孤兒。
  - `state["rec"]` 改成先拿掉再停:紅在「停錄製之前」缺 `kill -TERM`。
  - `cleanup()` 不再刪原始日誌:紅 3 處。
  - `kill_group` 只殺最外層:紅 5 條(孤兒、逾時時間)。
  - `perfetto_alive` 只看回傳碼:紅在 `ps_no_grep`。
  - `strictmode_result` 的 `finally` 拿掉刪日誌:紅。
  - `cleanup()` 不殺日誌串流:紅。
  - 拿掉 `PYTHONIOENCODING` 與 `PYTHONUTF8`:Big5 那條紅。
- 還有幾處測試走不到,見下面 F1 到 F3。

**3. 新發現的同一案例在修前、修後各是什麼結果?** 見各條「歸因」。
- F1 到 F3 這種測試缺口,修前與修後的測試都放行同一個故障變體,所以是上輪沒人看的角落,不是修補造成的。

## 兩個中斷空窗的時間對齊

- 「等日誌跟上」那條:空窗 4 秒,測試在驅動第二次被呼叫後約 1.1 秒送 SIGTERM。
- 「停錄製之前」那條:假 `ps` 睡 4 秒,測試用日誌裡的 `ps -A` 當標記,同樣約 1.1 秒後送 SIGTERM。
- 兩條都有 2.9 秒以上的餘裕。
- 兩個故障變體都紅,不是現場不成立的假綠。
- 逾時那兩條的 `took < 20`:正常約 4.1 秒(驅動)與 6.1 秒(快照),故障變體 26 秒。慢機器上有約 3 倍餘裕,而且孤兒斷言獨立把關,所以不算誤紅風險。

---

結果檔欄位全沒斷言:收集腳本把數字放錯欄位,所有測試照綠
severity: major
blocking: 是
引句:「check("錄製還在跑 → cycle_trace ok", d.get("cycle_trace", {}).get("status") == "ok"」
引句:「print('"cycle",200000,0,40,600')」
- 失敗情境:收集腳本算出的 `total_mem_mb`、`device_model`、`android_sdk`、`native_heap_kb`、`cycle_trace` 各數字,任何收集測試都沒斷言(只看 `status`)。判定端的測試用手寫的 `_ms_result`,所以收集端到判定端的欄位交接沒人驗。
- 我做的變體,`-k memstab_collect` 全部 78 通過:
  - `cycle_numbers` 的 `keys` 換成 `("frozen_frames", "peak_anon_swap_kb", "frames", "max_main_block_ms")`,峰值與凍結幀互換。
  - `res["total_mem_mb"] = -1`。這會讓每次 `peak_vitals` 靜默被跳過(判定端對 -1 的處理是跳過)。
  - `native_heap_kb` 一律回 None。
  - `device_model` 一律是空字串。
- 預期:至少 `total_mem_mb` 與 `cycle_trace` 的值要在收集測試裡對上假工具給的數字。假 trace_processor 回 `200000,0,40,600`,假 `/proc/meminfo` 回 7386728 kB,期望值可獨立算出。
- 對照 CLAUDE.md 引用的測試規則 3「斷言實際行為。觀察輸出、狀態、寫入結果」。
- file: `scripts/templates/android-stability-collect.sh:359-365` 與 `:270-272` 是這兩段產出欄位的程式。
- 歸因:有證據的原有漏查。修前 44d93aba 的測試對 `total_mem_mb`、`device_model` 同樣零斷言(grep 為 0)。

原始日誌「正常結束也刪掉」沒有測試,日誌裡的帳號與權杖可能留在磁碟
severity: major
blocking: 是
引句:「check("落地的日誌只留違規那幾行,不留其他內容", "SECRET123" not in body」
- 失敗情境:S22 寫「原始串流不管串流斷了、被中斷還是正常結束都刪掉」。正常結束路徑只檢查 `logcat.txt` 乾淨,沒檢查 `logcat.raw` 還在不在。
- 我做的變體:把 `strictmode_result` 的 `finally: drop_raw(raw)` 改成 `if died: drop_raw(raw)`。`-k memstab_collect` 全部 78 通過,但正常跑完後 `logcat.raw` 帶著 `token=SECRET123 user=alice@example.com` 留在產物目錄。
- 對照 CLAUDE.md 引用的測試規則 3:斷言要看寫入結果,而這個守衛的目的就是日誌不落地。
- 預期:`logcat_scope` 第一個案例的結尾加一條 `not (run / "logcat.raw").exists()`。
- 歸因:有證據的原有漏查。修前測試裡 `logcat.raw` 零次出現;r2 補了串流斷了與中斷兩條路,正常路徑沒補。
- file: `scripts/templates/android-stability-collect.sh:398-411` 是 `strictmode_result`。

S24「擋下、不碰裝置」只驗回傳碼與沒有結果檔,不驗裝置真的沒被碰
severity: major
blocking: 是
引句:「check("git repo 裡產物目錄沒被忽略 → 回 2 擋下、不寫結果檔", r.returncode == 2 and "gitignore" in r.stderr and not d, r.stdout + r.stderr)」
- 失敗情境:把「git 沒忽略」的擋下延後,先跑完整段量測(錄製、快照、日誌都寫進沒被忽略的目錄),最後寫結果檔前才 `die`。回傳碼是 2、stderr 有 gitignore、沒有 `stability.json`,所有斷言照綠。
- 我實跑:`-k collect_edges` 在這個變體下是 16 通過、0 失敗。
- 這個守衛要防的正是快照與日誌進版控,變體反而把它們寫進去了。
- 另外 run-id 非法、`.`、`..` 與已用過的 run-id 這幾條擋下也一樣,都沒查 `adb.log` 是否不存在。
- 對照 CLAUDE.md 引用的測試規則 4:「宣稱某守衛拒絕,就確認拒絕理由,不能讓另一道更早的守衛代打」。這裡是擋下的位置沒被驗。
- 預期:這幾個擋下案例加一條 `not (fake / "adb.log").exists()`。
- 歸因:有證據的原有漏查。這幾條擋下測試修前就是這個形狀。
- file: `scripts/templates/android-stability-collect.sh:337-355` 是 `preflight`。

清理測試的孤兒收尾只收到最後一組,紅的時候日誌串流孤兒會留 60 秒
severity: minor
blocking: 否
引句:「left = sp.run(["pgrep", "-f", f"{fake}/(driver|sleeper)"], capture_output=True, text=True).stdout.split()」
引句:「for pid in left:   # 測試自己收尾:紅的時候不留孤兒給別支測試」
- 失敗情境:`t_android_memstab_collect_cleanup` 第一段先把日誌串流的 pgrep 結果放進 `left`,接著 `left` 被驅動的 pgrep 結果覆蓋,收尾迴圈只殺後者。
- 我實跑:`cleanup()` 不殺 `lc` 的變體,測試紅的同時,假 `adb logcat`(睡 60 秒)的程序還活著(pid 35315)。我手動殺掉了。
- 對全域 CLAUDE.md 暫存清理規則的代價:紅的時候,逐字稿註解宣稱的「不留孤兒給別支測試」不成立,殘留會被後面用 `pgrep -f adb logcat` 的測試當成自己的孤兒(誤判)。
- 預期:兩次 pgrep 的結果分開存,或收尾時兩組都殺。
- 歸因:有證據的原有漏查。這支測試是 r2 的新增,r3 沒動這段。

`GIT_CONFIG_GLOBAL` 隔離不完整,而且在本套件的 HOME 沙盒下原本就多餘
severity: minor
blocking: 否
引句:「GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",」
- 失敗情境:使用者的全域 ignore 放在 `$XDG_CONFIG_HOME/git/ignore` 且含 `.lumos/` 時,這個隔離擋不住。
- 我實跑:`XDG_CONFIG_HOME=<臨時>` 並寫入 `git/ignore: .lumos/`,`-k collect_edges` 紅 2 條:「git repo 裡產物目錄沒被忽略」與「.gitignore 只寫 *.json」。這正是新增註解說要防的誤紅。
- 反過來,只把 `HOME` 指到有 `~/.config/git/ignore` 的目錄,16 條全綠。測試套件本身已經把 HOME 換成 `gctl-run-*` 沙盒,所以 `GIT_CONFIG_GLOBAL` 這行補丁對 HOME 方式的全域 ignore 沒有增益,對 XDG 方式又擋不住。
- 預期:`env` 再加 `XDG_CONFIG_HOME` 指到空目錄,或註解改寫成它實際擋得住的範圍。
- 歸因:有證據的修復造成(r3 修補新增的那兩個 env 鍵),效果不完整。
- file: `scripts/test_lumos.py:551-568` 是 HOME 沙盒的驗證。

`_ms_root` 預設連跑兩次 lumos,多個表格式測試只用得到一次;整組新測試佔全套閘約一半時間
severity: minor
blocking: 否
引句:「return root, r, d, (_mb_run(root, "--stability", str(sp)) if text else r)」
引句:「check(f"{why} → 不噴例外、回 0", r.returncode == 0 and rt.returncode == 0 and "Traceback" not in r.stderr + rt.stderr, r.stderr + rt.stderr)」
- 效率情境:`-k android_memstab` 是 3 分 50 秒;全套閘約 8 分鐘,這組佔將近一半。最慢的 `t_android_memstab_unreadable_never_passes` 是 27.4 秒,15 個表格式案例各起兩次 lumos(單次約 0.65 秒)。
- `java_growth` 的 `run()`(7 次)、`instance_limit` 的 `run()`(7 次)與 `exits` 的 `run()`(8 次),文字輸出各只在 1 到 2 次用到,其餘都白跑一次。
- 同一個檔裡 `vitals_every_tier` 已示範:表格式案例直接呼叫 `m._macrobench_judge_stability`,命令列路徑留 2 到 3 個案例。照做約省 25 到 30 秒。
- 歸因:未判定(沒有行為錯誤,純成本);本輪只加了 `text=False` 到其中 9 處,其餘沒動。

Big5 語系那條在沒有該語系的機器上只印一行就過,S24 的這句沒證據
severity: minor
blocking: 否
引句:「print("  (略過 Big5 語系那條:這台機器沒有 zh_TW.BIG5 語系,-P 與 UTF-8 輸出這條在這裡驗不到)")」
- 情境:S24 把「主機語系是 Big5 這類非 UTF-8 時輸出照樣是 UTF-8」綁進 `t_android_memstab_collect_edges`。沒有 `zh_TW.BIG5` 的機器(作者自己註明 Linux CI 多半沒有)上測試仍回綠,但這句條款沒被驗證。
- 本機有該語系時它是真紅真綠:我拿掉 `PYTHONIOENCODING` 與 `PYTHONUTF8` 就紅了。
- 預期:跳過時留一個計入「略過」而不是通過的訊號,或在計劃筆記回頭條件寫明「CI 無 Big5 語系時這句未驗」。
- 歸因:有證據的修復造成(這條是 r3 修補新增)。

文字輸出的斷言太鬆:`"5" in rt.stdout`
severity: minor
blocking: 否
引句:「check("文字輸出印出類別名與實例數", "com.sdk.Player" in rt.stdout and "5" in rt.stdout, rt.stdout)」
- 情境:實際輸出是 `com.sdk.Player 有 5 個(上限 1)`。把順序印反成「有 1 個(上限 5)」或把上限當實例數印,斷言照綠,因為只查字串裡有沒有 `5`。
- 預期:斷言寫 `有 5 個`,或同時要求 `上限 1`。
- 歸因:有證據的原有漏查。

## 簡化與重用(合併一條)
severity: minor
blocking: 否
引句:「if isinstance(val.get("after", {}).get("bytes"), float):   # NaN 用 json 的 NaN 字面寫進檔」
- 這 4 行是多餘的:`_ms_root` 收 dict 時用的 `json.dumps` 本來就會寫出 `NaN`,拿掉這個分支結果一樣。
- 重複的樣板:
  - 把假工具旗標檔寫進 `fake/` 的 4 行出現約 10 次。
  - 呼叫 `sp.run(["sh", str(script), …], env=_ms_collect_env(fake))` 約 6 次。
  - `pgrep` 找孤兒再 `kill` 約 8 次。
  - `_ms_collect` 與 `_ms_prepare` 重抄了一整串 11 個關鍵字參數,可以改成 `**kw` 轉傳。
- 中斷空窗迴圈的 tuple 裡,第一個空窗的 `marker` 是用不到的值。
- 已確認不報:`vitals_every_tier` 的官方表(3200/4800/6800/9216/14336/18432 與 2.00/2.25/2.25/3.25/4.25、遊戲 2.25/2.75/3.50/4.00/5.00)與計劃單源一致,不是照抄實作。`cycle_query` 的期望值(160 MB、凍結幀 1、阻塞 650 ms)是從表格手算,獨立。

---

**最嚴重:major,blocking 共 3 條**

**圖譜鏡頭:**
- 固定席節點 `Systems/測試假綠形態` 的 ★INVARIANT★ 要求「還原翻紅釘必須配前置斷言證明現場成立」。
- 本輪兩個中斷空窗的測試前置是 `p.poll() is None` 加驅動日誌行數。我做的兩個故障變體都紅,所以不違反。
- 這條前置不能證明「還在哪個空窗」,只靠 2.9 秒的時間餘裕,不影響結論。
- 其餘固定席節點(`lumos-cli-read`、`bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop`)的合約都是 `scripts/lumos` 與流程類,本席只讀 `scripts/test_lumos.py` 的新增測試,對它們判不影響。
- 殘留那題我沒有證據可答,未判定。

**未驗範圍:**
- 真機與真實 Perfetto 的 SQL 方言。`_ms_sql` 用的是自己照文件建的表。
- 全套 3700+ 案例。
- 在慢機器上的時間斷言實際表現。
