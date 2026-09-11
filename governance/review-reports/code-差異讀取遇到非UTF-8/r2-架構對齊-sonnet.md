severity: major

### F3 共用泛用包裝 `_sp_run_text` 沒補 `errors=`,直接可重現 UnicodeDecodeError;新守衛的啟發式抓不到這種間接呼叫,「每一個」的完整性宣稱不成立
severity: major
blocking: 是 — 上一輪 F1/F2「宣稱涵蓋、實測有漏」的同一種失效模式,在這輪「機器保證」裡原樣重演,且可當場重現崩潰,不是臆測
引句:「★工具裡每一個用文字模式讀 git 輸出的呼叫★」
file: `scripts/lumos:940-942` `_sp_run_text(cmd)` 用 `_sp.run(cmd, capture_output=True, text=True)` 讀輸出,沒有 `errors=`
file: `scripts/lumos:884` 唯一呼叫處 `_sp_run_text(["git", "-C", str(root), "rev-parse", "HEAD"])`,git 指令包成變數傳進去
file: `scripts/test_lumos.py:9880` `_text_git_calls_missing_errors` 只認「第一參數字面上有 "git"」或「所在函式原始碼裡出現 "git" 字串」——這兩條 `_sp_run_text` 都不成立(git 字面值只在呼叫端 884 行,不在函式體 940-942 行內)
1. 重現(已實測):對真實 `scripts/lumos` 跑守衛函式,回傳的缺漏行號清單裡沒有 942,守衛測試本身回報綠燈,但 `_sp_run_text` 明明沒補。
2. 直接重現崩潰(已實測):另建一個 repo,提交一支內容非 UTF-8 的檔,呼叫 `m._sp_run_text(["git","-C",root,"show","HEAD:a.py"])`,結果 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 5: invalid start byte` 當場丟出——跟本次 PR 要修的錯誤同一種。
3. 逐一核對全檔 8 處「第一參數是變數/串接」的文字模式 git 呼叫:其餘 7 處(`cmd_cochange_check`、`_delguard_confidence`、`_testmap_git`、`_lens_git`、`_scan_diff_for_irreversible_hints`、`_pull_source_or_abort`,以及本就不歸類的 `_ci_gh` 跑 `gh` 而非 `git`)都已補上,只有 `_sp_run_text` 漏掉;今天唯一呼叫處讀的是 `git rev-parse HEAD`(SHA 全 ASCII)所以還沒炸,但這是泛用工具函式,名字就是鼓勵之後拿去包別的 git 呼叫,屆時會複製同一顆雷且守衛不會叫。

F1:修到 — 這輪新測試 `t_git_readers_survive_non_utf8_filenames` 用 Big5 檔名觸發 `cmd_test_layers` 的 `--name-only` diff;實測拿掉 `scripts/lumos:18360` 的 `errors="replace"` 會讓「test-layers 照樣給提醒」翻紅(改前 9 passed 0 failed,改後 5 passed 1 failed)。
F2:修到 — `_delguard_confidence`(scripts/lumos:17544)已加 `errors="replace"`;實測拿掉它會讓 `t_diff_readers_survive_non_utf8_content` 裡「刪除守衛的全域搜尋讀得動非 UTF-8 內容」翻紅(8 passed 1 failed)。

你的鏡頭(三問,逐問答):

1. 既有 git 包裝的分工是「多支各管一種指令的小函式」(`_git_commit_exists` scripts/lumos:3869、`_git_is_shallow` scripts/lumos:3880、`_git_tree_has`/`_git_tree_text` scripts/lumos:22666/22672)+ 兩支真正跨多處呼叫端共用的通用包裝(`_testmap_git` scripts/lumos:18490、`_lens_git` scripts/lumos:20643)+ 大量沒包裝、直接 inline `subprocess.run(["git",...])` 的一次性呼叫,本來就沒有單一 central「讀 git 文字輸出」函式。逐處補 `errors=` 跟這個既有慣例一致,不是另立門派。但既有的通用包裝裡漏了一支:`_sp_run_text`(scripts/lumos:940,唯一呼叫處 scripts/lumos:884)這次沒補到——是既有做法裡漏了一個節點,不是引入第二種做法,依鏡頭錨判 minor(即 F3)。
2. 完全一致。既有掃原始碼型守衛已有固定套路:`ast.parse` + `ast.walk` + 「餵一段壞的、一段好的證明守衛會翻紅」的自我驗證,例如 `t_no_zero_assertion_return_paths`(scripts/test_lumos.py:31483,自我驗證在 31532 行起)、hook import 清單守衛(scripts/test_lumos.py:32155)。新守衛 `_text_git_calls_missing_errors` + `t_every_text_mode_git_call_tolerates_undecodable_output`(scripts/test_lumos.py:9880/9915)完全照搬這套既有套路。0 條不對齊。
3. 頂層判別函式的擺法不是新做法——test_lumos.py 本來就有幾十支只服務單一測試、定義在模組頂層的 `_xxx` helper(如 `_mk_git_vault` scripts/test_lumos.py:5950、`_codeloop_read` scripts/test_lumos.py:12716),`_text_git_calls_missing_errors` 完全對齊,不判不對齊。用 `hash-object -w --stdin` + `update-index --add --cacheinfo`(scripts/test_lumos.py:9843-9844)直接寫進索引、繞過檔案系統造非 UTF-8 檔名,確實是先前沒出現過的技巧(既有唯一的 `hash-object` 先例在 scripts/test_lumos.py:12937,只是算空樹雜湊,沒人拿它造過檔名)——但這是這台 Mac 檔案系統不收非 UTF-8 檔名之下唯一可行的路,不是在已有可行做法之外另立第二種,不判不對齊。

不對齊共 1 條,其中 major 0 條。

總結:最高 severity major,blocking 共 1 條
