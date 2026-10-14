severity: major

**整體看**

- 掛鉤改照 `spec_source` 判,不再手抄代碼清單,方向對。這一段拿掉了 `_RANGE_ONLY_FAIL_CODES` 和 `_SPEC_FAIL_CODES` 兩份抄本,只剩 lumos 的 `_LENS_SPEC_FAIL_CODES` 一份。
- `_repo_walk_lstat` 沒有再多一份逐段 lstat。它把原本分散的 `_spec_freeze_lstat`、`_spec_freeze_out_path` 內嵌的逐段 lstat 和圖譜資料夾檢查收成一支,是減少重複。
- `_events_path_safe` 另有一份逐段走訪,但那是 `.is_symlink()` 加固定相對段,不在這份 diff 裡,所以不列。
- 掛鉤沒有跨層直呼 lumos 內部函式。`_spec_freeze_from_commit` 復用 `_spec_commit_path_bad`、`_spec_commit_blob`、`_lens_full_sha`,分界也沿用 `_LENS_SPEC_COMMIT_RE`,沒有第二套。

severity: major
blocking: 是 — 同一支檔裡已有批次查大小的現成做法,新函式另寫第二套 `cat-file --batch-check` 的呼叫與解析,專案對這種事有被點名的前例。
引句:「blobs = [x for i, x in enumerate(q) if i < len(heads) and ok_line.fullmatch(heads[i])]」
對照:
- file: `scripts/lumos:31333`(`_nodehome_cat_sizes`):已經做了 `cat-file --batch-check` 的批次送入、`surrogateescape` 編碼、逾時與回傳碼處理、逐行解析。
- file: `scripts/lumos:23956` 附近的註解:第四輪架構席抓過「第三輪另寫了一套 cat-file --batch 解析」。
- `_spec_commit_present` 自己跑 `_sp.run(["git","-C",...,"cat-file","--batch-check"])`,又自寫 `ok_line` 正規式,等於再開一套。
- `_lens_git`(`scripts/lumos:47586`)沒有 stdin 參數,所以不能直接用。但可以用 `_nodehome_cat_sizes`,或把它擴成能回型別。

判定理由:

- 新函式要的只是「這些 `<提交>:<路徑>` 存不存在」,`_nodehome_cat_sizes` 的「存在=有大小,不存在=None」已經夠用。
- 它自己的型別是 blob 篩選,後面 `ls-tree` 那段本來就再篩一次(`parts[1]=="blob"` 且 mode 為 100644/100755),所以前面的型別篩選是多餘的。
- 因此沒有理由另寫一套。這是引入第二種做法。

severity: minor
blocking: 否 — 只多一份字元類別常數,沒有新行為分歧,也沒跨層。
引句:「# 計劃路徑(「計劃來源」那行)另用自己的規則,不套節點名的 80 字與字元集(代碼審 code-派工鏡頭可指定目標repo r2 邊界4/通才4:」
對照:
- file: `scripts/lumos:36211`(`_PATH_SPECIAL_CATS = ("Cc","Cf","Zl","Zp","Cs")`)。
- file: `scripts/lumos:7132`,同一支檔已有「`_PATH_SPECIAL_CATS` 再加 Co、Cn」的現成組法。
- file: `scripts/lumos:17174`(`_lens_visible`)。

判定理由:

- `_lens_spec_path_showable` 的 `_LENS_SPEC_PATH_BAD_CATS` 是 `_PATH_SPECIAL_CATS` 加上 Co、Cn 的重新手寫,可以直接寫成 `_PATH_SPECIAL_CATS | {"Co","Cn"}`。
- 分工本身說得通。`_LENS_SPEC_NODE_NAME_RE` 是節點名的白名單,用在只在提交裡的列名和落點;`_lens_spec_path_showable` 是計劃路徑的黑名單,專給「計劃來源」那行。它們管的是不同欄位,這點不算問題。
- 要收斂的只有那份類別集。

severity: minor
blocking: 否 — 執行器那層的存回只涵蓋 main() 入口改的四個變數,有測試守著清單與入口一致,行為上不會漏。但它和既有 fixture 的做法不同,也有維護成本。
引句:「run_with_timeout(lambda t=t: _keep_lumos_entry_env(t), TIMEOUT_OVERRIDE.get(t.__name__, TEST_TIMEOUT_SEC))」
對照:
- file: `scripts/test_lumos.py:995-1008`(`_try` 裡 `old = dict(_os.environ)`,finally 內 `clear()` 後 `update(old)`)。
- file: `scripts/test_lumos.py:67357` 附近,同樣是各測試自己存整份環境再還原。

判定理由:

- 既有慣例是在需要的測試裡存整份環境再還原。新增的是在全域執行器包一層,只存回硬編碼的四個變數。
- 清單與入口是否一致,另靠 `t_lumos_inproc_main_keeps_git_entry_env` 去讀原始碼比對。
- 這個測試自己又手寫了第三份存回邏輯,兩邊可以合成一支。
- 在執行器層統一處理比逐點補丁合理,所以只列 minor。

最高等級 major,blocking 1 條。
