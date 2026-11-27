severity: clean

我逐 hunk 讀完修補差異,對照 `scripts/lumos` 主程式現況,沒有找到會做出錯行為或損壞資料的輸入。下面是查證過、判為沒問題的路徑,以及測試獨立性的判斷。

**「沒驗」與「全綠」分開(`_KillCompile.apply_compile`、`one_batch`、`probe`)**
- `_CHOICE_COMPILE_UNVERIFIED` 是 tuple 常數。`apply_compile` 的全部呼叫端(`scripts/lumos:29454`、`29470`、`29508`、`29516`)都用 `is` 判它,沒有哪個地方會把它拆成 `rc, out, to`。
- `apply_compile` 無法套任何一筆時回 `(0, "", False), {}, later`。這是「全綠但 `ranges` 為空」,探針迴圈 `for g in ranges` 不會記任何補償,所以不會有補償被誤記。
- 探針整批紅時改逐個單獨編,條件是 `g in rg and one[0]==0 and not one[2]`。
  - 只有一筆進得了 `ranges` 時不單獨編,這是對的,因為整批紅就是它自己紅。
  - 整批逾時(`got[2]`)也走單獨編的路徑,耗時由 `cap()` 預算限住。

**`units()` 新增的過濾**
- `os.path.join(wt, "/etc/x")` 的絕對路徑會被 `startswith(wt_real + os.sep)` 擋掉。
- `.git` 判斷用的是 `relpath` 切出來的 parts,`.github` 之類的目錄不會被誤擋。
- `_kill_old_issue` 與 `_kill_new_issue` 是現成函式,簽名吻合。`invalid()` 換候選後重算 `units()`,換不到時回 False 的舊路徑沒變。

**編譯旗標與指令共用(`_platform_compile_flag`、`_choice_compile_cmd`)**
- 我拿 10 種怪形狀的 `run_cmd`(未成對引號、`None`、非字串、無 `{method}`、兩段 Gradle、`:testDebugUnitTest` 無模組、帶 `{python}` 前綴等)跑 `_choice_compile_cmd`,都不丟例外,只回指令或 None。把它搬進 `load_platforms` 的載入階段因此安全。
- 尾段殘留 `--tests`(`--tests '*{method}' --tests`)會讓編譯指令末端多出 `--tests`,但這是上一輪就有的行為,不是修補引入的,也不影響判斷。

**套件讀法(`_choice_cov_pkg_of`、`_choice_cov_req`)**
- 改用 `_strip_c_comments(kotlin=True, keep_length=True)`。行註解內的 `/*` 不再吃到檔尾,巢狀區塊註解與沒收尾的註解都有處理。
- `_choice_cov_req` 在 `text == ""` 時,`"".encode()[:N].decode(...)` 仍是合法的空字串。檔頭截在多位元組字元中間時用 `replace` 解碼,不會丟例外。
- 長檔頭(超過 32KB)時,壞法行與掃主程式兩邊一起讀不到 package,行為一致,測試有釘。

**覆蓋抽查(`audit_done`、`_resolve`)**
- 抽到的 none 行 no_result 時,`finish` 已先把 `p["done"]` 設為 True,所以 `_resolve()` 的「是否等完」條件會成立,`audit_unsure` 因此會生效,其餘 none 行改照跑。
- 抽 clause 行 no_result 時不設 `audit_unsure`,只是不算抽查完成,不影響別行。
- 全部抽查都 no_result 時 `audit_seen` 維持 0,收尾就不印抽查摘要行,不會誤報「都一致」。

**exhausted 讀者**
- 我 grep 了 `status` 的讀取點。`scripts/lumos:79955`、`81352`、`81509`、`81229` 都是用 `in ("mutant","not_unique")` 的形式,exhausted 會自然落到「不擋」。
- `scripts/lumos:81608` 與 `81661` 兩處查表已補上 exhausted。
- `scripts/lumos:79581` 與 `80960` 的 `points` 計數仍把 exhausted 算進去,這是設計意圖,不是漏洞。

**新測試獨立性**(依 `03-寫回圖譜.md`〈實作測試品質〉)
- 各測試都有對應的翻紅點:
  - `t_choice_exhausted_status_readers`:拿掉錯誤表的 exhausted 項,訊息會變成「挑不到壞法」而紅。
  - `t_choice_compile_probe_split`:有 6 個案例,分別釘整批紅逐個編、沒驗不補償、合批沒驗不記無效、單獨確認沒驗不記無效,另有修改時間正常的對照案例。判準是外部腳本實際編到的檔內容與 `calls.log`,不是把實作重寫一遍。
  - `t_choice_compile_units_guards`:替身字元、old 非字串、`.git` 底下各一案,對照案例是一般的 A。
  - `t_choice_compile_flag_same_source`:覆蓋分析指令的字串是逐字比對。
  - `t_choice_cov_pkg_comments`:行註解帶 `/*`、真區塊註解、長檔頭三種情境都有。
  - `t_choice_cov_audit_noresult`:斷言沒有任何 `via cov` 事件,且三行 none 都記 no_result。

**鎖與圖譜鏡頭**
- `/Users/enzo/.cache/lumos/dispatch-lens/fe8210c6a7155973d05bfe7e6742bb3f59576f66d67be7d2e0694ba1f759e30d.json.warming` 不存在,沒有鎖要處理。
- 固定席範圍為 3 檔(`scripts/lumos`、`scripts/test_lumos.py`、`scripts/test_quality.py`)。`lens-r2.txt` 我只讀了前 2500 字元;可見部分(guard-kill、lumos-cli-read 等 INVARIANT 節點)我沒看到修補與其合約相衝的地方。
- 修補 diff 本身沒動 `scripts/test_quality.py`;`lens-r2.txt` 把它列為受影響檔,是因為審的範圍是 `37510bf..ac5203b`。
- 第一段進度節文件的 diff 我只讀了預覽,沒逐行對照;文件類內容我沒查出與程式的矛盾。

總結:最高等級是 clean
