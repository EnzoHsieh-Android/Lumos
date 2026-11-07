severity: major

這輪修補多數真的沿用了既有做法,r1 點名的第二種做法已收掉:讀表只剩 check.py 一套,diff 解析走既有解析器,載入掛鉤檔共用同一支函式,快取走既有的家目錄快取函式。但有一處新的第二種做法:同一個時間預算,在這題逾時會擋下,在表態閘其他地方逾時卻是放行。其餘是命名、依賴方向與預算傳法上的小偏差。我只讀不改,沒有改 repo,也沒有用到目標架構規則,因為派工詞說算不出固定席。有一點要先講:`/Users/enzo/orca/workspaces/lumos-toolchain/android-situation-evidence` 的工作樹已經是修補後的樣子,我拿它對照 patch,行號以它為準。

## ① 分層與依賴方向

lumos 借 check.py 讀表的方向對,也是 r1 建議的方向。`_kt_pack_check` 走共用的 `_load_hook_file`,載入時要求必備函式 `dt_table`;lumos 端舊的 `_kt_dt_*` 與 `(停用)` 字面量都已刪光(`scripts/lumos` 裡 grep 不到)。`_load_hook_file` 只是從 handoff 區搬到型錄區,內容逐行相同,兩個舊呼叫端(`scripts/lumos:69490`、`:73475`)沒動,載入順序也正確(它定義在模組載入時讀型錄之前)。

**F1** 依賴變成雙向,而且 check.py 另有第三種載入 lumos 的寫法。
severity: minor
blocking: 否
⚠ 判不準:反向邊只在自測時才走。這個方向是 r1 自己建議的,是否算「跨層」請編排者裁。
引句:「借用規則包自檢程式(讀表那幾支)→ (模組或 None, 原因或 None);走共用的 _load_hook_file。」
引句:「把旁邊的 scripts/lumos 當模組載入(不寫 __pycache__)→ (模組或 None, 原因或 None)。」
- lumos 每次載入都會執行 check.py(`scripts/lumos:38186`、`:38225`)。
- check.py 的 `load_lumos`(`configs/ast-grep/kotlin-android/check.py:351`)為了跑情境樣本自測,又反過來載入整支 lumos。
- 載入 lumos 這件事現在有三種寫法:`_load_hook_file`(`scripts/lumos:38122`,用 `spec_from_file_location`)、`scripts/scenario_probe.py:918`(`SourceFileLoader` 搭配 `spec_from_file_location`),以及 `load_lumos`(`SourceFileLoader` 搭配 `spec_from_loader`)。
- `_load_hook_file` 沒辦法直接載入沒有副檔名的 lumos,這是有理由的,但三種寫法的錯誤句和關 bytecode 的寫法各自維護。

**F2** 判斷「這支 lumos 是不是工具鏈來源」的條件,在 `version` 指令裡已有一份,`_kt_toolchain_root` 又抄了一份。
severity: minor
blocking: 否
引句:「這支 lumos 就在來源 repo 裡(有 skills/lumos-project-notes,同 version 指令的判法)」
- 既有的在 `scripts/lumos:297-301`,沒有共用函式可呼叫。
- 這個判斷現在複製到第二處,只用註解保證兩份一致,沒有守衛。

## ② 命名與錯誤處理

段放行這部分是對齊的。
- 放行檔、理由、origin、ack、`_waive_origin_tty` 與帳事件(`lint-new` 的 `waived`)全部共用(`scripts/lumos:39877`、`:39780`)。
- 指紋是前綴 `kt-situation:` 加 16 位十六進位,跟 lint-new 的 `sha256(...)[:16]`(`scripts/lumos:40768`)同形,不會互撞。
- 只多了帳事件 extra 的 `scope` 一欄,不算不一致。
- 「無法驗證(…)——擋下不放行」的句型也跟 `scripts/lumos:72062` 的既有句型一致。

**F3** 環境不可用時的 fail-open 記帳,跟它宣稱沿用的新增告警閘先例不一樣。
severity: minor
blocking: 否
引句:「_gate_failopen(repo_root, "code-loop", _cat[1][:200])」
- 這個記帳呼叫放在判定函式 `_dispositions_verdict` 裡面(`scripts/lumos:71931`)。既有的表態閘 fail-open 都由呼叫端記(`scripts/lumos:72397`、`:72399`)。
- 閘名用 `code-loop`,不是 lint-new 先例用的 `lint-new`。
- lint-new 的自動放行有專屬計數,會進健檢(`scripts/lumos:41222`、`:4182`),理由是「沒有人去數,承認風險那句話就是空頭支票」。這條新的帳沒有對應的計數,混在其他 `code-loop` 的 fail-open 裡分不出來。

**F4** 「只在測試執行器裡生效」是用 `TMPDIR` 的目錄名前綴來判斷,這是全庫第一次這樣做。
severity: minor
blocking: 否
⚠ 判不準:可能是刻意避開正式路徑被環境變數影響。
引句:「執行器的 _isolate_environment 把 TMPDIR 換成這一輪的 gctl-run-* 根目錄」
- 既有的覆寫(`LUMOS_HOME` 見 `scripts/lumos:33059`,`LUMOS_HIGH_RISK_EVIDENCE_SINCE` 由 test_lumos 在檔頭用 `setdefault` 凍結)都是正式程式永遠認的環境變數,測試端只負責設值。
- `scripts/lumos` 裡其他地方沒有用 `gctl-run-` 判斷過(僅此一處,`:38170`)。
- 測試執行器改了暫存目錄命名時,這個條件會靜默失效。

## ③ 第二種做法

快取沿用了既有做法。
- 讀寫走 `_home_cache_read` 與 `_home_cache_write`(`scripts/lumos:66892`、`:66922`),目錄是 `~/.cache/lumos/<子目錄>/<sha>.json`,跟 `_lens_cache_path`(`:66889`)同形。
- 有 TTL 常數和 schema 常數,跟 `_LENS_SCHEMA`(`:67362`)的做法一致。

`(換列)` 標記也是單一解析。只有 check.py 的 `_SWITCH` 解析(`configs/ast-grep/kotlin-android/check.py:95`、`:185`),lumos 只讀 `row["switch"]`。以下是 lumos 讀到的列結構:

引句:「列:{id, situation, standard, alt(不適用時), triggers, evidence{main, alt}, retired(停用列), switch(換列的列), checks}。」

字面預篩(觸發字開頭那段英數底線的集合)是新機制,但我在庫裡沒找到可借的同類預篩函式,不算第二種做法。

**F5** 同一個 `deadline` 逾時,在這一題的處置跟表態閘其他地方相反。
severity: major
blocking: 是
⚠ 判不準:「任何計算失敗都判無法驗證擋下」是 r1 的裁決(D3),可能就是刻意的。但那條裁決講的是計算失敗,沒有明講時間預算逾時。
引句:「deadline 到了 raise _KtSitUnverifiable」
- 推送前表態把共用的 20 秒 `deadline`(`_DISP_BUDGET`)傳進 `_kt_sit_verdict_one`。切段與核對途中逾時會 raise,最後判成擋下。
- 表態閘的既有規則是:逾時就停、標 `over_budget`、已查出問題才擋,沒問題就放行並記帳。見 `scripts/lumos:71918` 的 docstring、`:72049-72057` 的迴圈頂端檢查,以及呼叫端 `:72397`。
- 結果是同一個預算有兩種逾時語意。同一次推送裡,別的題逾時放行,這題逾時擋下。
- 這是會擋人的行為差異,不是文字差異。要擋的話應該在 `over_budget` 這一條統一處理,或者把理由寫進筆記,說明為什麼這題要例外。

**F6** 讀被推分支的檔,用了沒有大小上限的批次讀取,單次 git 的逾時也沒帶剩餘預算。
severity: minor
blocking: 否
引句:「blobs = _nodehome_cat_blobs(repo_root, [f"{at_sha}:{r}" for r in rels], timeout=_disp_git_timeout())」
- 既有的批次讀取有加大小上限的版本 `_nodehome_cat_blobs_capped`(`scripts/lumos:46104`)。它的 docstring 寫明「上限放在批次讀取這一層,不另起查法」,是 r2 架構席要求的。
- 剩餘時間轉單次逾時,既有的是 `_git_timeout(deadline, cap)`(`:66342`)。
- 新函式用固定的 `_disp_git_timeout()`(8 秒)。時間預算只在迴圈頂端查,單次 git 卡住攔不住。
- `_kt_sit_hunks` 走 `_ns_diff` 也一樣,但那是既有函式的限制。

**F7** 快取鍵除了 schema 常數,另外掺進 lumos 檔案自己的大小與修改時間,這是庫裡第一次這樣做。
severity: minor
blocking: 否
引句:「me = f"{st.st_size}:{st.st_mtime_ns}"」
- 既有快取(`:66889` 的鍵、bound-filter 的 `schema{_FILTER_PROBE_SCHEMA}`)都只靠版本常數失效,不看檔案時間。
- 這裡 schema 常數存在,又多一層 mtime。每次 checkout 或重新安裝工具鏈都會讓快取整批失效,而 schema 本來就負責這件事。

**F8** 識別字字元集又多拼一次,詞界寫法的重複比 r1 時更多。
severity: minor
blocking: 否
引句:「_KT_ID_RE = r"[A-Za-z0-9_]+"」
- `_kt_trigger_re` 的前後界(`scripts/lumos:38216`)加上這個新常數,是同一個字元集的又一份。
- r1 已經以「庫裡沒有共用詞界函式」放行過這類,所以只列為提醒,不擋。

不對齊共 8 條,其中會擋的 1 條。
