severity: major

## F1 讀「起點版本的設定檔」自己拼一套,沒用既有的 _json_at_ref
severity: major
blocking: 是
引句:「cf = _lens_git(root, "show", f"{base}:.lumos/config.json")」
說明:專案已有「從 git 版本讀 JSON、只信 base 的設定」的專用函式,它自己的說明寫「只信 base 的設定要靠它,不讀工作樹」。新碼在 _review_roles 裡改成手動 git show、再在 _review_roles_config 另做 json 解析與去 BOM,等於第二種讀版本設定檔的做法。若因為 _json_at_ref 把「沒有檔」和「壞掉」都回 None、分不出要不要警告而不能直接用,正確做法是擴充那支(或加參數),不是在旁邊另寫一套。另外設定讀取鄰居是「回 dict 含 warnings」(見 _stack_questions_config),新碼回 (rules, warnings) 二元組,形狀也不同(併入 F3)。
file: `scripts/lumos:30809`(_json_at_ref);`scripts/lumos:20741`(_stack_questions_config)

## F2 _node_flavor 內長出第二條找 package.json 的路
severity: minor
blocking: 否
引句:「return _node_flavor_at(file_rel, reader)」
說明:有 reader 時整個繞過原本「往上走 Path.parents + _NODE_FLAVOR_CACHE」的走法,改由 _package_json_candidates + _node_flavor_at 另走一遍,同一個函式裡兩套往上找 package.json 的實作。解析那半有抽成共用的 _node_flavor_of,結構是對的,所以只判 minor;也順帶把舊路徑「壞 package.json 當沒依賴判 node」改成 None(行為改動,不是對齊問題)。
file: `scripts/lumos:20655`(_node_flavor 現有的 parents 走法,以該函式所在處為準)

## F3 警告的印法與回傳形狀跟設定讀取鄰居不同
severity: minor
blocking: 否
引句:「print(f"角色鏡頭 ⚠ {_w}")」
說明:鄰居把設定警告印到 stderr、前綴「提醒:」(pitfalls 內同一段 _sq_cfg 的處理);新碼在同一個函式旁印到 stdout、前綴「角色鏡頭 ⚠」,派工段又用「(角色鏡頭)⚠」,同一批新碼裡就有兩種前綴。錯誤處理方式(壞值整份退預設+回一句警告)本身跟鄰居一致。
file: `scripts/lumos:27540`(print(f"提醒:{w}", file=sys.stderr))

## F4 ⚠ 又手寫一份 git diff --name-status -z 的解析(鄰居本身就不一致)
severity: minor
blocking: 否
引句:「r = _lens_git(root, "diff", "--no-ext-diff", "--name-status", "-M", "-z", base, head)」
說明:⚠ 交編排者:專案裡已有 _nodehome_changes、_nodehome_name_status、以及 _pitfall 那條 name-status 解析各自手寫,本身就沒有統一做法,新碼是第四份。_nodehome_changes(repo, base, tip) 形狀最接近,但會把路徑 NFC 正規化(拿去 git 查會對不上 NFD),可能是不用它的原因。不硬判 major。
file: `scripts/lumos:23218`(_nodehome_changes);`scripts/lumos:21730`

## 三問
1. 分層與依賴方向:對齊。角色計算全在 lumos 端(_review_roles 等),掛鉤只做「認標記行(ROLE_RE 比照 MARKER_RE/SPEC_RE)、多傳 --role-cards、失敗時讀 role_text 照附」,沒有掛鉤自己判角色;失敗分支附文字的做法與既有超時分支一致。_vendored_skip 從 _pitfall_diff_collect 抽出共用,方向正確。cmd_dispatch_lens 外包一層、原本體改名 _dispatch_lens_graph,沿用同函式內 io+contextlib 捕捉輸出的既有寫法(scripts/lumos:31590),arm/claim 走的仍是原路徑。無跨層直呼。
2. 命名與錯誤處理:大致對齊(_ROLE_* 常數、_review_role_* 函式、壞設定整份退預設)。不對齊在 F3(警告前綴與輸出通道)。測試造 repo 的 helper _role_git_repo 與 _mk_lens_repo(scripts/test_lumos.py:34712)同型:各測試檔內自帶臨時 repo 小工具,是專案慣例,不算。
3. 第二種做法:F1(讀起點版本設定檔)判 major;F2(package.json 雙路徑)、F4(name-status 解析,⚠)為 minor。路徑樣式比對 _glob_first_match 直接包 _cochange_excluded,批次讀取用既有 _nodehome_cat_blobs,讀 git 用 _lens_git,這幾處都是復用,對齊。

總結:不對齊共 4 條,其中 major 1 條。
