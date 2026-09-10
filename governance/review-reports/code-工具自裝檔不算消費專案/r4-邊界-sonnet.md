severity: blocker

### F36 消費專案工具檔權限異常時,`_vendored_state` 逐檔 read_bytes 沒包例外,doctor/pitfalls 直接崩潰
severity: blocker
blocking: 是 — 未捕捉的 PermissionError 讓指令以未設計的方式中斷(非「擋下:」訊息),三個呼叫點(doctor [S3]、pitfalls --diff/push 閘)全部會斷
引句:「data = {p: ((Path(root) / p).read_bytes() if (Path(root) / p).is_file() else None) for p in paths}」
1. 最小重現:consumer repo 裡在 `_VENDORED_ALL` 任一固定路徑(例如 `scripts/lumos`)放一支未加入 git 的檔並 `chmod 000`,跑 `lumos pitfalls --diff HEAD --repo .` 或 `lumos doctor`;本機實測(macOS)兩者都印出未捕捉的 `PermissionError: [Errno 13] Permission denied` 完整 traceback、rc=1,而不是本輪其餘失敗路徑一致採用的「擋下:...」訊息。
2. 同一段緊鄰 3 行外,指紋清單本身的讀取有 `except OSError: man_raw = None` 保護,逐檔內容讀取(引句那行)卻完全沒包 try/except,兩者處理方式不一致。
3. `_stack_ext_counts`(scripts/lumos:13967)與 `_pitfall_diff_collect`(scripts/lumos:17923-17924)都在 `ref=None`(工作目錄)時直接呼叫到這行,分別餵給 `lumos doctor` 與 push 閘會跑的 `lumos pitfalls --diff`。

### F37 Windows 鎖檔從不寫入,msvcrt 鎖 0 位元組檔可能讓 set/append/remove 每次都失敗
severity: major
(★未能重現,本機是 macOS,fcntl 分支蓋不到 msvcrt 那條路,已依規則降一級★)
blocking: 是 — 若命中,Windows 上每一次 set/append/remove 都會卡 60 秒才以 RuntimeError 失敗,判準:寫入指令整支失效
引句:「msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)」
1. `_vault_write_lock` 用 `open(path, "a+b")` 開鎖檔後,從 `fh = open(...)` 到 `fh.close()` 之間查無任何 `fh.write(...)`,鎖檔對每一次呼叫永遠是 0 位元組(scripts/lumos:10902-10924)。
2. `msvcrt.locking` 鎖一個 0 位元組檔是常見會丟 `OSError`(Permission denied)的邊界情況;這裡的 `except OSError` 只會當成「鎖在別人手上」重試,不會分辨真正拿不到鎖與檔案太小鎖不了。
3. 未能重現(找不到 Windows 環境跑 `msvcrt.locking`);`grep msvcrt scripts/test_lumos.py` 零命中,這條分支目前完全沒有任何自動測試覆蓋。

## 第三輪修法驗收
F19:修到 — `_multi_link_value` 讀寫共用,`t_multi_link_list_value_one_rule` 逐一驗證兩側一致
F20:修到 — `_SEV_SUMMARY_LINE_RE` 錨行首 + 只剝「等級字後面緊接 0 條」,「0/1」「0day」「0 台」三種都仍判殘留,對應測試齊全
F21:修到 — `_about_code_path` 先 `replace("\\","/")` 再驗,反斜線寫法收下且存成正斜線
F22:修到 — `_about_code_key` 用磁碟真實拼法比對,大小寫錯字項與正確項判同一支
F23:修到 — `_disk_spelling` 目錄讀不到時回 unreadable,`_about_code_path` 據此擋下(append 路徑);唯 `_about_code_key` 對同一情況是靜默退回字面比對而非擋——經查對 append/remove 現有呼叫序不構成可觀察錯誤,不足以獨立開新單
F24:修到但修出新洞 — 內容指紋機制本身正確(改過的工具檔仍會被掃、無清單時不跳過),但新寫的 `_vendored_state` 對工作目錄逐檔 `read_bytes()` 沒包例外 → 見 F36
F25:修到 — mkstemp 動態暫存檔名 + `_vault_write_lock` 序列化,8 程序併發測試通過;但鎖機制本身在 Windows 路徑有未驗證的失效風險 → 見 F37
F26:修到 — symlink 別名與真實路徑經 `_about_code_key` 解析後判同一支檔,append/remove 兩側都測了
F27:修到 — 訊息改成「同一行」不再講「逗號」,`[a]` 案例測試通過
F28:修到 — `_posix_norm` 共用,`_about_code_key`/`_is_vendored_path` 不再各寫一份
F29:修到 — `_impact_mark_about` 改用 `_posix_norm`(解 `..`),⑮ 新測試驗證
F30:修到 — `except (OSError, ValueError, RuntimeError)` 擴大,新增 `t_new_verification_backlink_blocked_still_says_note_created` 專測
F31:修到 — `_list_key_scalar_to_list` 對已加引號的原值原樣搬,append/remove 自我檢查補「其他項目都還在」
F32:修到 — `_list_scalar_value` 判準改「去引號後值本身」而非列舉寫法,`[[A], B]`、引號內前導空白都測了(⑨b QG/QH)
F33:修到 — remove 迴圈對同一 want 的每種既有拼法逐一 `edit_fm_remove`,⑫測試驗證一次拿掉兩筆
F34:修到 — `t_vendored_file_list_matches_what_install_ships` 加了 `_need_src("skills/lumos-project-notes/SKILL.md")` 守衛,且已納入消費端模擬回歸清單
F35:修到 — 安裝改成只複製 `_VENDORED_TOOLKIT + _VENDORED_TREE_FILES` 精確清單,`t_update_resyncs_claude` 驗證未登記的來源檔不會被裝進去

## 風險掃描清單判讀
- scripts/lumos:10902(`_vault_write_lock` 的 `open(...)`):誤報 — try/finally 涵蓋所有路徑必定 `fh.close()`,不是缺 close(該函式真正的問題是 F37,跟這顆掃描規則命中的原因無關)。
- scripts/lumos:17884:誤報 — 命中的是 `_stack_changed_ok` docstring 裡描述「命中 open(...)」的說明文字,不是可執行程式碼。

總結:最高 severity blocker,blocking 共 2 條
