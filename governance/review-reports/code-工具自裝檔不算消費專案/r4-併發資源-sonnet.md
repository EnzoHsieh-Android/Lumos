severity: major

### F36 about-code revert 清 about_code_stamp 那步繞過 r3/r4 新加的 vault 鎖
severity: major
blocking: 是 — 繞過鎖,批次撤銷與其他寫入指令可能互蓋成功回報卻遺失資料
引句:「沒有鎖時,回報成功的項目會被同時跑的另一個程序蓋掉」
1. `cmd_about_code_revert` 逐值呼叫走鎖的 `cmd_remove(env, rel, "about_code", v)`,但清 `about_code_stamp` 那步改直接呼叫 `_cmd_remove_scalar(env, rel, "about_code_stamp")`,完全繞過 `_vault_write_lock`。
2. 佐證:file: `scripts/lumos:11364` 直接呼叫 `_cmd_remove_scalar`,對照 file: `scripts/lumos:11087-11092` `cmd_remove` 才是有上鎖的入口。
3. 最小重現(已實跑):另一程序持鎖 5 秒期間,`_cmd_remove_scalar(env, rel, "about_code_stamp")` 0.008 秒內完成寫入並回 rc0;同一場景改呼叫走鎖的 `cmd_set` 則等了 3.7 秒才完成——證明前者確實沒排隊。預期輸出:兩者都應該等待鎖釋放,實測只有後者等了。
4. `scripts/test_lumos.py` 的 `t_about_code_revert_batch` 只驗功能正確性,沒有任何併發用例覆蓋這條路徑,是「測試綠但咬不到」的一例。

### F37 鎖檔開不起來時靜默退回不上鎖,沒有任何提示
severity: minor
blocking: 否 — 只在鎖檔異常(權限/符號連結/共用暫存目錄被搶先建立)時退化回鎖前行為,不是新增的資料損毀
引句:「鎖檔開不起來(暫存目錄不能寫)就不上鎖照做,退回原本的行為」
1. `_vault_write_lock` 的 `except OSError: yield; return` 完全不印任何 stderr,呼叫端(cmd_set/append/remove)也不知道這次寫入其實沒受鎖保護。
2. 最小重現(已實跑):把 `hashlib.sha1(resolved_vault_path)[:16]` 算出的鎖檔路徑預先建成 `chmod 000` 的檔案(模擬共用暫存目錄裡被別的使用者/程序卡位),`with _vault_write_lock(vault):` 照常無異常地跑完,沒有任何警告輸出。
3. `tempfile.gettempdir()` 在 Linux 常是所有本機使用者共用且可寫的 `/tmp`,鎖檔名是 vault 路徑的確定性雜湊,存在被搶先佔位或換成 symlink 的條件(macOS 因 per-user 暫存目錄而風險低很多)。

### F38 _vault_write_lock 同程序巢狀呼叫不可重入,自我卡死 60 秒且錯誤訊息誤導
severity: minor
blocking: 否 — 已窮舉現有呼叫點(僅 cmd_set/append/remove 三個 wrapper 各自呼叫一次),目前沒有任何路徑會巢狀呼叫
引句:「等了 60 秒還輪不到寫入(同一個筆記庫有別的程序一直在寫)」
1. flock 鎖的是「開檔物件」不是行程,同一程序在同一個 vault 上巢狀呼叫 `_vault_write_lock`(例如未來有人在某個已持鎖的 `_cmd_*_locked` 裡又呼叫 `cmd_append`)會自我卡死。
2. 最小重現(已實跑):同一行程內巢狀 `with _vault_write_lock(v): with _vault_write_lock(v): ...`,外層立即拿到鎖,內層等滿 60.03 秒後才拋 `RuntimeError`,訊息卻說「有別的程序一直在寫」——實際上是自己卡自己,除錯時會被導去找不存在的外部程序。
3. 目前 grep 全檔案確認 `_cmd_set_locked`/`_cmd_append_locked`/`_cmd_remove_locked` 只各被自己的 public wrapper 呼叫一次,故此路徑今天不可達,屬未來維護的地雷。

### F39 _write_lf 新檔分支用 os.umask(0)/還原讀權限,非執行緒安全
severity: minor
blocking: 否 — scripts/lumos 目前沒有任何 threading/ThreadPoolExecutor 使用,今天不可達
引句:「_um = _os.umask(0); _os.umask(_um)」
1. `os.umask()` 是行程層級全域狀態,`umask(0)` 到 `umask(_um)` 之間若同行程其他執行緒建立檔案/目錄,會拿到未套用使用者 umask 的寬鬆權限。
2. 最小重現(已實跑):用執行緒在該窗口期間建立另一支檔案,該檔權限落在 0o666(process umask 是 0o077,預期應是 0o600 左右),證明視窗確實可被外部建檔動作穿透。
3. `_write_lf` 自身文件字面寫「vault 唯一寫入原語」,若日後被其他多執行緒情境（例如測試框架、未來平行化的 git 子行程呼叫)引入,這個窗口會變成可達的真實 race。

## 第三輪修法驗收

F19:修到 — 讀側 parse_frontmatter 的 lint 與寫側 `_list_scalar_value` 現共用 `_multi_link_value`,兩套規則已合一
F20:修到 — `_SEV_SUMMARY_LINE_RE` 改成錨定行首(容許標題/清單/引用/編號/粗體前綴),正文中間提到等級字不再誤判成總結句
F21:修到 — `_about_code_path` 開頭 `.replace("\\", "/")` 已收 Windows 反斜線寫法
F22:修到 — `_about_code_key` 用 `_disk_spelling` 解磁碟真實大小寫與 NFC 當比對鍵,不再靠字面比對造成重複
F23:修到 — `_disk_spelling` 讀不到目錄清單時回 unreadable,`_about_code_path` 明確擋下而非放行
F24:修到 — `_vendored_state` 改比對內容指紋(`_vendored_digest`),不再只比檔名路徑
F25:修到但另有新洞 — mkstemp 唯一暫存名與 `_vault_write_lock` 解掉了原本檔名互搶問題,但 `cmd_about_code_revert` 清 `about_code_stamp` 那步繞過鎖,見 F36
F26:修到 — `_about_code_key` 對存在的檔案先 `.resolve()` 解 symlink 再取真實路徑當鍵,別名與正路徑歸一
F27:修到 — 測試驗證 `[a]` 缺逗號時訊息只講「同一行」,不再講「看不懂逗號」
F28:修到 — 三處路徑正規化收斂成單一共用函式 `_posix_norm`
F29:修到 — 排序加分讀側改用 `_posix_norm`(含 normpath 解 `..`),不再只剝開頭 `./`
F30:修到 — new verification 側掛失敗時 except 同時接 ValueError/RuntimeError,訊息仍以「筆記建好了」開頭
F31:修到 — `_list_key_scalar_to_list` 對原本帶引號的值原樣保留不重新加引號;append/remove 自我檢查新增「原本每一項都還在」
F32:修到 — `_list_scalar_value` 用 fullmatch 排除多值陣列開頭、對值先 strip 再比對排除引號內前導空白兩種繞法
F33:修到 — `_cmd_remove_locked` 對 about_code 蒐集同一支檔的所有拼法逐一 remove,不再只拿掉一筆
F34:修到 — 漂移測試以 `_need_src` 守門,只在能取得工具鏈來源時才跑,消費專案不會假紅
F35:修到 — 安裝改成只複製 `_VENDORED_TOOLKIT` + `_VENDORED_TREE_FILES` 精確清單,不再 rglob 整個目錄

## 風險掃描清單驗證
scripts/lumos:10902(`_vault_write_lock` 裡的 `open(...)`):誤報 — 包在 try/finally,finally 一律 `fh.close()`,例外也會釋放
scripts/lumos:17884:誤報 — 命中的是 `_stack_changed_ok` docstring 裡舉例用的文字「命中 open(...)」,不是真的 open() 呼叫

總結:最高 severity major,blocking 共 1 條
