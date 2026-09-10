severity: major

### F19 about_code 正規化邏輯跟同批新寫的 `_is_vendored_path` 重複,沒共用
severity: minor
blocking: 否 — 純重複實作,無行為分歧風險,不影響本次功能正確性
引句:「v = strip_quotes(str(value).strip()).replace("\\", "/")」
引句:「r = posixpath.normpath(str(rel).replace("\\", "/"))」
1. `_about_code_norm`(scripts/lumos:10897-10901)與同一批新增的 `_is_vendored_path`(scripts/lumos:13229-13236)都是「反斜線轉斜線 + posixpath.normpath」這串邏輯,各自 `import posixpath` 一次,沒有互相呼叫或共用小函式。
2. 兩者服務不同資料源(frontmatter 值 vs diff 檔名),`_about_code_norm` 多做了 `strip_quotes`,所以不是逐字搬移可以直接替換,但同一支 diff 裡兩個函式重寫同一小段正規化,是可以抽一個共用 helper 的重複。
3. 沒有觀察到兩者會對同一輸入給出不同答案,不構成「兩套真相打架」,列 minor。

### F20 write 側「同一行清單」判準比 parse_frontmatter 的 lint 寬,兩套定義沒有互相引用
severity: major
blocking: 是 — 讀寫兩側對同一件事(什麼算「同一行清單」)給不同答案,已用指令重現
引句:「(sval.startswith(("[", "{")) and not sval.startswith("[[")) or sval.count("[[") > 1」
佐證:file: `scripts/lumos:264` `parse_frontmatter` 的 list 分支只認 `"]], [[" in item or "]],[[" in item`,不認雙空格、逗號前空格等變體。
佐證:file: `scripts/lumos:277` scalar 分支同一套窄比對,`"]], [[" in sval or "]],[[" in sval`。
1. 重現(已實跑):對 `related: [[Systems/A]],  [[Systems/B]]`(兩個空格)呼叫 `parse_frontmatter`,`lint` 回 `[]`(讀側/`lumos doctor`/`lint` 完全不吭聲);同一個值餵給新寫的 `_list_scalar_value` 卻擲 `ValueError`(訊息「related 寫成同一行的清單…」),append 會 rc2。
2. 這代表 vault 裡可能已經有一批這種「雙空格 / 逗號前多空格」的同一行清單筆記,doctor/lint 從不示警,直到有人對那篇筆記 append 才第一次被擋——擋下訊息也沒說「這是既有的舊資料,不是你剛打錯」。
3. `_list_scalar_value` 的 docstring(scripts/lumos:10641-10650)沒有一句提到它比 parse_frontmatter 的 lint 判準寬,兩套「什麼算一串連結」的定義並存卻互不引用,是本題的「第二套做法」。

## 對齊三問

1. 分層與依賴方向:`_about_code_path`(存值,含檔案存在性+大小寫檢查)與 `_about_code_norm`(純字面比對鍵,append 去重、remove 找項共用)是各司其職——前者要碰檔案系統、後者要在檔案已刪的情況下仍能比對,拆開是對的(file: `scripts/lumos:10897` vs `scripts/lumos:10904`)。但 `_about_code_norm` 的正規化本體跟同批新寫的 `_is_vendored_path`(file: `scripts/lumos:13229`)重複沒共用,見 F19。
2. 命名與錯誤處理:「已經有了,檔案沒動」rc0 早退與既有的 `report-normalize` 「已是正規化格式…不用改」(file: `scripts/lumos:5316`)是同一套白話、同一種 rc0-idempotent 慣例,對齊。同一行清單的 `ValueError` 由 `main()` 的 `except (ValueError, RuntimeError) as e: print(f"擋下:{e}")`(scripts/lumos:24734 一帶)接住,跟 `atomic_write_verify` 的 `RuntimeError` 走同一條路、訊息同樣不帶「擋下:」前綴由上層補,對齊。`(None, 理由)` 回傳是本檔既有慣例(file: `scripts/lumos:549`、`scripts/lumos:8729`-`8739` 等二十餘處同型),`_about_code_path` 沿用得正確,對齊。
3. 「剝等級緊接 0」只加在既有 `_SEV_SUMMARY_LINE_RE` 分支裡,重用同一個 `_lv`/`_top` 比對(scripts/lumos:5220-5228 一帶),是在單一豁免機制裡多剝一層雜訊,不是開第二套規則,對齊。但同一行清單的寫側判準比 parse_frontmatter 的讀側 lint(只認 `]], [[`/`]],[[`,file: `scripts/lumos:264`、`scripts/lumos:277`)寬,兩套「什麼算一串連結」並存且互不引用,見 F20。

不對齊共 2 條,其中 major 1 條。

## 前兩輪修法驗收
F1:修到 — `_is_vendored_path`+`_VENDORED_ALL` 精確檔名比對,測試①⑤(own-hooks)綠且咬到專案自己的 hook 仍被掃。
F2:修到 — lint_claims 在對齊判斷前先濾 `_is_vendored_path`,測試⑦ aligned=True/False 兩種都綠。
F3:修到 — 刪除行分支已傳 `_stack_changed_ok(cur_file, _skip_vendored)`,測試⑥(delete-only 不觸發棧別題)綠。
F4:修到 — `about_code` 不在 `SCALAR_KEYS`,`cmd_set` 直接擋,測試⑧綠;另見 F19(衍生的重複實作,非功能性回歸)。
F5:修到 — `_about_code_path` 先 resolve 再 `relative_to(root)`,絕對路徑/`../` 都擋,測試⑤綠;另見 F19。
F6:修到 — `about_code` 只剩 append/remove 一套規則,測試⑧驗 set 被擋。
F7:修到 — set 路徑整條拿掉,原本跳過引號處理的問題隨之消失。
F8:修到 — 沿用第二輪三席判讀(事故筆記已寫「不建立波及連結、只做排序」),本輪未再動這篇筆記。
F9:修到 — `_VENDORED_TREE_DIRS` 常數在 `_vendor_toolchain`/`_deinit_remove_vendored`/授權測試三處共用,不再各寫一份。
F10:修到 — `_set_about_code` 整支連同 set 路徑一起拿掉,命名不一致問題隨代碼消失。
F11:修到 — `_stack_ext_counts` 的 `rd = relpath(dirpath, _base)` 改成每個目錄算一次,不再對同層每檔重算。
F12:修到 — `_is_toolchain_repo` 判別鍵在工具鏈本體 repo 永不跳過,測試④綠、方向 fail-closed。
F13:修到 — `_list_scalar_value` 改看「去引號後的值本身」(`count("[[")>1` 或方括號開頭),測試⑨b 四種繞法全擋;另衍生新洞,見 F20。
F14:修到 — `edit_fm_append` 的 scalar 分支值已存在時直接 `return fm` 不改格式,cmd_append 訊息改印「已經有」,測試⑩綠。
F15:修到 — `_about_code_path` 新增磁碟真實檔名逐段比對,大小寫不符即擋,測試⑬綠。
F16:修到 — dedup 改用 `_about_code_norm` 比正規化後的鍵,`src/../src/a.ts` 與 `src/a.ts` 判同一筆,測試⑪綠。
F17:修到 — `cmd_remove` 對 about_code 先用 `_about_code_norm` 找到實際存的字串再刪,測試⑫綠。
F18:修到 — 授權標頭測試改用 `getattr(m, "_VENDORED_TREE_DIRS", ())`,不再手寫第三份目錄清單。

風險掃描清單那 1 條:誤報 — scripts/lumos:17660 是 `_stack_changed_ok` docstring 裡描述舊事故的中文引號引文「命中 open(...)」,不是真的 `open(` 呼叫,附近無檔案 handle。

總結:最高 severity major,blocking 共 1 條
