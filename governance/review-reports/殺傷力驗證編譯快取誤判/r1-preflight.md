# 前置掃描:殺傷力驗證編譯快取誤判_計劃(只讀;實驗在 pf-cache-work/)

## ① 未定義的詞
- 命中(輕):「rtb」(計劃全文三處,沒一句說是什麼專案;路線圖才有)。原句:「看 rtb 那邊 guard kill 有沒有因為修改時間在未來而冒出新的警告或錯誤」。改:首次出現補「(rtb=另一個使用 lumos 的消費專案)」。
- 命中(輕):「編排者」「通才席」未定義。原句:「編排者 2026-10-01 重現(改動前版本、本機)」。改:寫成「本 session 的編排者(派席的主會談)」或直接寫「Claude 主會談」。
- 命中(輕):「1a-4 → 代碼審修正關卡 → 1a-3 → 1b」在本篇沒解釋,路線圖表有;已有 related 連過去,可接受,但最好加一句「見路線圖表」。
- 未命中:甲/乙已在「依據」第二條定義;壞法、配方、平台組沿用 guard kill 既有詞。

## ② 壞引用
- 全部存在:Issues/guard kill在Python專案會沿用編譯快取誤判殺得掉、Systems/guard-kill、Projects/漂移防治路線圖_計劃(路線圖確有 1a-4、修正關卡、1a-3、1b)、`cmd_guard_kill`、`_kill_run`、`_mk_kill_env`(test_lumos.py:20339)、`t_guard_kill*`。
- 標 [test:] 但還沒寫(單獨列):`t_guard_kill_no_stale_build_cache`(S1/S2/S3 三條都綁它,test_lumos.py 內 grep 0 筆)。提醒:一個測試名綁三條條款,S3(os.utime 失敗)要在測試裡製造 OSError(mock os.utime 或唯讀),計劃沒寫怎麼造;建議 S3 拆獨立測試名。
- 計劃沒點名但相關:`_kill_run` 實際有 3 個呼叫者,見 ④。

## ③ 範圍自相矛盾
- 不矛盾(範圍/做法/條款一致:只在 cmd_guard_kill 套壞法後設時間)。
- 小張力:〈範圍〉「不改合約測試閘與其他呼叫 `_kill_run` 的地方」,但〈實務隱患〉要求「文件守衛測試…別新增 verdict 字面」,而 S3 要新增 stderr 輸出——不矛盾,只是 S3 的提醒字樣若含 `"verdict": "…"` 才會踩守衛(test_lumos.py:25180 抽 verdict 值域)。OK。
- 與 Issue 不一致:Issue 內文與 REVISIT 把快取寫成「工作樹裡的 `__pycache__`」並建議「清 `__pycache__`/PYTHONDONTWRITEBYTECODE」;本計劃改採乙且說明本機 3.9 快取在 ~/Library/Caches。兩邊說法不同(見④的實測:3.9 確實不在工作樹;3.14 在工作樹)。改:實作時一併修 Issue 的描述,並更新其 REVISIT(那條 REVISIT 建議的是甲,已被本計劃否決)。

## ④ 機械宣稱驗語意(讀程式 + 實跑)
逐句結果:
1. 「cmd_guard_kill 每個平台組開工作樹之後…」——成立。groups 依 platform 分組,每組一個 tempfile.mkdtemp + `git worktree add --detach`(約 13890-13900 行)。多平台時同一支檔不會被不同組各改一次:每組各自一份 worktree 目錄(各組各自 mkdtemp),絕對路徑不同,Python 快取(含 macOS 以絕對路徑為鍵的 pycache_prefix)也各自獨立。「上一次時間初始 0」按組重置是對的。
2. 實際順序——成立,且計劃描述順序對:baseline(每個 cmd 只跑一次,快取在 baselines)→ 路徑圍欄 → 讀檔、old 必須恰出現 1 次 → 寫入壞法 → `_kill_run` 跑測試 → `git checkout -- file` 還原 → 判定。注意:還原發生在判定之前,還原失敗就 break 整組。實作要把 os.utime 放在 `open(target,"w")` 之後、`_kill_run` 之前(別放判定之後)。
3. 「還原後那支檔的修改時間是『現在』」——一般成立(實測 git checkout 重寫檔,mtime=還原當下),★但這句推論不足以支撐「一定更晚」之外的正確性★,見下方 BUG-1。
4. 「下一條壞法一定設得比它與上一條都晚」——成立:max(現在+1, 上一次+1),秒級至少差 1。
5. Python 過期判準——成立:importlib 的時間戳 pyc 只比對 int(mtime) 與 size(32 位元),到秒加大小;PEP 552 的雜湊模式也確有。計劃寫的「秒+大小」正確。
6. macOS 內建 python3 快取位置——成立:本機 python3 = /Library/Developer/CommandLineTools/usr/bin/python3 (3.9.6),`sys.pycache_prefix` = /Users/enzo/Library/Caches/com.apple.python;Homebrew python3.14 則寫工作樹內 `__pycache__/a.cpython-314.pyc`(實測)。計劃只提 3.9 這邊;建議補一句 3.14/Linux CI 寫在工作樹 __pycache__,S1 測試在兩邊都該能重現(CLAUDE.md 規定測試用 3.14 跑,而 `_mk_kill_env` 的 run_cmd 寫死 `python3`,在本機是 3.9)。
7. 「`_kill_run` 是合約測試閘也在用的共用函式」——成立且不只一個:lumos 內 `_kill_run(` 呼叫者共 4 處:cmd_guard_kill 的 baseline(13922)、cmd_guard_kill 的壞法跑(13950)、過濾探針 `_bound_filter_probe` 一帶(38139,跑假測試名)、合約測試閘逐支跑(38192,帶 keep_re)。計劃沒提探針那處。因為本案不改 `_kill_run`,不影響結論。
8. 「不改判法、回傳碼、--json」——成立,新增 stderr 提醒不污染 --json(程式已有 stderr 慣例)。
9. 「文件守衛從 cmd_guard_kill 原始碼抽 verdict 值域」——成立(test_lumos.py:25180-25190 以 `verdict = ` 行與 `"verdict": "…"` 抽字串字面量)。注意:新程式碼若寫 `verdict = ` 以外不受影響;但守衛是用 index 切 `def cmd_guard_kill(`…`def cmd_guard_audit(` 的原始碼,提醒訊息裡別出現 `"verdict": "xxx"`。
10. 「make 以修改時間比較…同一秒內也不會重編」(PRIOR-ART ①)——不準確:GNU make 在支援奈秒時間戳的檔案系統上用奈秒比較,同一秒內較新的來源仍會觸發重編;「同一秒內不重編」只在秒級時間戳檔案系統成立。改:刪掉「同一秒內也不會重編」,或改成「make 以修改時間(精度依檔案系統)比較」。「Python、Gradle、jest、go 不會」印時鐘偏差警告——本掃描未驗證(未跑),屬未驗宣稱;建議標「未驗」或刪。

### BUG-1(語意缺口,已實測)
計劃「還原不動」的前提是還原後 mtime=現在、一定與壞法留下的快取不同。實測:壞法與原檔同大小(`LIMIT = 5`→`LIMIT = 9`)、壞法 mtime 設為未來 M(=現在+3),測試跑完、等到 ≥M 再 `git checkout -- prod.py`,還原後 mtime == M(整數秒相同),大小也相同,結果還原後的原始碼再跑測試仍然 AssertionError,吃到壞法的 pyc(實測重現)。
- 觸發條件:壞法與原檔同大小,且「從設時間到還原」這段(測試時間)≥ 偏移量。偏移只有 +1 秒,所以測試跑超過 1 秒就可能發生(常態)。
- 影響:同一組後面「另一支檔」的配方,若其綁定測試 import 這支被還原的檔,會吃到前一條壞法的 pyc(假 killed),或整套跑的測試吃到舊壞法。同一支檔的下一條壞法不受影響(被新的未來時間蓋掉)。baseline 不受影響(只在最前面跑)。
- 改法(擇一寫進做法與條款):還原後也用 os.utime 把該檔設成 `max(現在+1, 上一次+1)` 並記錄(讓還原後的 mtime 同樣與任何先前快取都不同);或每次還原後把「上一次」記成 max(上一次, 現在) 並確保還原後 mtime ≠ 任何曾出現過的壞法 mtime。再加一條條款:S4 還原後的修改時間不得等於任一條壞法設過的時間。〈做法〉第 3 點「還原不動」要改寫,〈實務隱患〉也要補。
- 另一個說明缺口:計劃寫「至少比現在晚 1 秒」+「記 per 組一個值」,但 Python 判準取 int 秒,若用 float,`last+1` 與 `now+1` 取 int 後仍至少差 1(已推演成立);建議在做法寫「用 float 秒、至少差 1.0」避免實作者用 int 加錯。

### 其他語意小點
- S3「設時間失敗…照常跑測試」:程式在 `with open(target,"w")` 之後,現有 except 結構只包讀檔;新增 try/except OSError 要只包 os.utime,別包到寫檔(寫檔失敗目前會直接拋出,維持原樣)。
- 計劃說「兩條改完檔案大小相同是必要條件」:對 Python 3.9/3.14 成立(pyc 比 size);但 BUG-1 顯示「與原檔同大小」也是另一個必要條件的變體(還原那一側),計劃只描述了壞法對壞法。
- 「S2 直接檢查修改時間」:測試要能在 cmd_guard_kill 跑完前看到 mtime——工作樹跑完即刪,測試得靠在 run_cmd 裡印 mtime(例如測試腳本自己 os.stat 並比對)或 --keep-worktree;計劃沒寫怎麼取。建議在〈做法〉或條款補:S2 用 run_cmd 讓測試腳本輸出 `os.stat(prod.py).st_mtime` 並由測試讀 tail,或用 `--keep-worktree` 事後量(但那是還原後的時間,量不到壞法時的),前者可行。
- 時序假綠:〈實務隱患〉說 CI 較慢跨秒會「照綠(假綠)」——這是測試 S1 在「未修」程式下也綠的意思,方向正確;S2 能補。但修好後的 S1 不靠時序也成立。OK。

## 結論
必修:BUG-1(還原後時間缺口,有實測重現)、PRIOR-ART make 句不準、S2/S3 測試怎麼造未寫、Issue 與計劃快取位置說法不一致。其餘為措詞級。
