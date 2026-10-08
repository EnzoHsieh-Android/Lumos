severity: major

# r3 邊界-sonnet 報告(鏡頭:邊界與輸入)

白話:這一版把「驗不了的平台」從樹裡那份設定拿掉,是個很好的修法;但拿掉之後設定檔可能變成「自己讀不進去」的樣子,而這一版同時刪掉了「讀不進去就回 2」那條接球的規則,另外「改寫樹裡的設定不影響主工作目錄」這句話在設定檔是符號連結時不成立。

## F1 拿掉平台後 load_platforms 會丟例外,而這版刪掉了接例外的先決條件,樹裡的設定形狀也沒驗
severity: major
blocking: 是
引句:「拿掉之後一個平台都不剩 → 回 2」
file: `scripts/lumos:4811`(load_platforms:`default_platform` 不在平台清單、多平台缺 default、頂層不是物件、root 型別不對都丟例外)
file: `scripts/lumos:11905`(`_platform_test_index` 直接呼叫 `load_platforms(repo_root)`,沒有 try)
file: `scripts/lumos:38425`(推送前那道閘自己用 try 包住它並記成 no-config;修正關卡第 3、4 項的描述裡沒有這層)
1. 前一版有一條「`load_platforms(樹)` 讀得懂(丟例外就回 2)」,這版換成只做「自己先用 JSON 讀一次」(見 r3-delta 的 99 行)。「拿掉之後一個平台都不剩 → 回 2」是唯一剩下的出口,其餘 load_platforms 會丟例外的情況沒有人接。
2. 最直接的失敗場景:設定 `platforms` 有 web 與 ios、`default_platform` 是 ios,ios 的資料夾沒進版控(正是本機 pos-ios 那種情形)。照規格把 ios 拿掉、`default_platform` 沒動,後面第 3 項 `_platform_test_index(樹)`、第 4 項「在樹裡自己取」、第 5 項 `_bound_tests_check` 都會讀到「預設平台 ios 不在平台清單裡」。實測(用 repo 的 `load_platforms` 讀只剩 web、default 是 ios 的設定):
   `ValueError 預設平台 'ios' 不在平台清單裡(有的是: web)`
   第 5 項推送前那道閘會把它吞成 `no-config`(判不過);第 3、4 項規格沒寫要接,照字面實作就是未處理例外,整次沒寫治理帳事件,`loop next` 永遠提醒。「同一專案別的平台照驗」在預設平台被拿掉時做不到。剩多個平台、`default_platform` 沒寫(原本靠 default 指向被拿掉的那個以外就沒事,但原設定若沒寫 default 本來就是壞設定)同理。
3. 第二個缺口:「讀得懂」只要求 JSON 能 parse。實測頂層是 `[]` 或 `null` 的設定都 parse 得過,但 `load_platforms` 讀到會丟 `AttributeError: 'list' object has no attribute 'get'` / `'NoneType' object has no attribute 'get'`(`_kill_cfg_load` 有加一道 isinstance 檢查,這版的描述沒有)。另外 `root` 是 null 或數字會丟 `TypeError`(實測 `unsupported operand type(s) for /: 'PosixPath' and 'NoneType'`),而「取每個平台根的實際路徑」這步正是要讀 `root`;`platforms.X` 不是物件、`profile` 名工具不認得則丟 `ValueError`。
4. 順序也沒交代:〈樹的準備〉(複製、拿掉平台、連依賴)排在 ④,「樹裡的設定讀得懂」也列在 ④ 但沒說先於拿掉平台;拿掉平台必須先 parse 並走 `platforms`,所以讀得懂的檢查要先做,且要含「頂層是物件、每個平台是物件、`root` 是字串」。
5. 修法方向(給編排者):把 load_platforms 的例外一律在建樹後第一次呼叫處接成回 2;拿掉平台時若 `default_platform` 指到被拿掉的就同步處理(剩一個→刪掉該鍵或改指它;剩多個→回 2 並說明);頂層與 `root` 型別先驗。
最小重現:`cd` 到任一目錄,`.lumos/config.json` 寫 `{"platforms":{"web":{"profile":"node-jest","root":"web"}},"default_platform":"ios"}`,用 `/opt/homebrew/bin/python3` 載入 `scripts/lumos` 後呼叫 `load_platforms(Path(目錄))` 得上述 ValueError(已實測)。

## F2 「樹裡那份設定可以被修正關卡改寫、不影響主工作目錄」在設定檔是符號連結時不成立,唯讀時也沒有出口
severity: major
blocking: 是
引句:「樹是用完就丟的,所以樹裡那份設定可以被修正關卡改寫」
file: `scripts/lumos:23630`(`_lint_link_deps` 本身只處理依賴資料夾,沒有任何東西保護設定檔的寫入)
1. 場景一(設定檔是被追蹤的符號連結,指到樹外):`.lumos/config.json` 提交成指向共用位置(絕對路徑,或相對路徑解出來在樹外)的符號連結。`git worktree add` 把連結原樣檢出,樹裡那份設定的寫入會穿過連結改到真檔。實測:提交一個指向 `shared/lumos.json` 的絕對路徑連結、建樹、用一般的 `open(path, "w")` 拿掉平台 a,結果 `shared/lumos.json` 變成只剩 b。也就是改到的是主工作目錄(以及所有共用這份檔的專案)正在用的設定,正好違反規格自己宣稱的「不影響主工作目錄」,而且是在 `fix-check` 這個「只提醒不擋、跑完就丟」的工具裡造成永久改動;每次驗證還會再改一次、讓下一次跑時看到的是被改過的設定。
2. 場景二(設定檔是複製進去的而且主工作目錄那份唯讀,如 0444):用 `shutil.copy` 複製會連模式一起帶過去,之後要寫就 `PermissionError`。實測 `PermissionError: [Errno 13] Permission denied`。規格沒說這種情況怎麼辦,照字面是未處理例外、沒治理帳事件。
3. 第三種:`.lumos` 資料夾本身在樹裡不存在時(設定檔沒進版控的情形)複製前要先建資料夾,規格只寫「直接複製那一份進樹的同一位置」。
4. 修法方向:改寫前先判樹裡那份是不是一般檔(`is_symlink()` 就先刪掉連結、改寫成獨立的檔,或判不過回 2);複製與寫入都用「先寫暫存再 replace」,寫入失敗回 2 並說明;複製時不帶唯讀模式。
最小重現:在臨時 git repo 提交 `.lumos/config.json -> 絕對路徑/shared/lumos.json`,`git worktree add --detach`,用 Python 讀樹裡設定、刪掉一個平台、`open(...,"w")` 寫回,再看 `shared/lumos.json`(已實測,內容被改)。

## 已讀,無 finding 的項目
- 依賴資料夾連結:`_lint_link_deps` 是 `src.is_dir() and not link.exists()` 才連、`symlink_to` 失敗吞 `OSError`;主工作目錄沒有該資料夾、樹裡已有同名受版控資料夾或檔案、樹裡有懸空連結三種情形都直接略過、不丟例外,規格沒有多餘的假設。收樹時 rmtree/`worktree remove` 不會順著符號連結刪主工作目錄的 `node_modules`。
  引句:「依賴資料夾:預設連——repo 頂與每個留下的平台根各用 `_lint_link_deps`」
- `fix_check.link_deps` 的值:字串 `"false"`、`null`、數字(含 0,`isinstance(v, bool)` 為否)都落在「值不是布林就用預設並警告」,規格已涵蓋;照 `_lint_new_config` 寫法頂層不是物件或 `fix_check` 不是物件時直接回預設,不丟例外。
- 測試名格式(實測 `resolve_test_refs`、`_KILL_METHOD_OK_RE`、`TEST_REF_RE`):只有空白 → 規格在解析前就擋;全形逗號 `，`、全形冒號 `：` 不被 `\w` 收,拆出方法名後被白名單擋掉;`]` 或 `,` 在平台前綴裡 → 解析前就擋;內含換行、`[`、反引號、`$` 之類 → 白名單擋;前綴後面是空字串 → 白名單的 `+` 擋。`web:t_x` 這種前綴在多平台下先切分再過白名單,不會被誤擋。已讀,無 finding。
  引句:「其他字元在解析成平台與方法之後,方法名照推送前那道閘過 `_KILL_METHOD_OK_RE` 白名單」
- 平台根:符號連結指到樹外 → `.resolve()` 後落在樹外,規格的「實際路徑底下」檢查會拿掉;指到樹內 → 留著、測試在解析後的路徑跑,可接受;根是 `.` → 等於樹本身,若實作用 `is_relative_to` 就算在底下(規格措辭「底下」對等於樹本身沒明說,屬 minor 措辭,不標)。

最高等級:major,blocking 共 2 條
