severity: major

### F19 about_code 大小寫比對在目錄讀不到時 fail-open,放行未驗證過的錯字大小寫
severity: major
blocking: 是 — 直接讓 r2 F15 要擋的那類錯誤在特定情境下復發,寫入的值永久對不上排序加分要比對的 git 路徑
引句:「names = os.listdir(cur)」
1. `except OSError: names = [part]`(scripts/lumos:10931-10932)把「讀不到目錄」fallback 成「只有這個字面值存在」,於是 `part in names` 恆真、不會被判 `off=True`。
2. 親自重現:`chmod 111 src`(可穿透但不可 `os.listdir`)後 `append about_code src/SUB/a.ts`(真實磁碟是 `src/sub/a.ts`)→ rc0、`✓ append ... 多了一項 src/SUB/a.ts`,寫進去的就是錯字大小寫,沒有被擋下。
3. `is_file()` 只需要 ancestor 目錄的搜尋權限即可通過,`os.listdir` 需要讀權限,兩者權限模型不同,不是純理論邊界(受限共享磁碟、部分網路掛載常見這種「可執行不可讀」設定)。

### F20 工具自裝檔跳過只比對路徑字串,不驗內容——把風險程式碼放在那 15 個精確路徑就能讓 pitfalls --diff 完全看不到
severity: major
blocking: 是 — 直接影響 pre-push/CI 的風險分級,tier 判 high 才會要求代碼審
引句:「return r in _VENDORED_ALL」
1. `_is_vendored_path`(scripts/lumos:13235)只做「正規化後的路徑字串在不在白名單集合裡」,不比對內容雜湊或跟工具鏈來源 diff。
2. 親自重現:在消費專案的 commit 裡把 `scripts/lumos`、`scripts/test_lumos.py`、`scripts/hooks/claude/impact-hook.py` 三支內容全部換成帶 `open()` 無 `with` 的風險寫法後 `pitfalls --diff --json`,結果是 `{"claims": [], "tier": "standard"}` ——三支檔的變動完全不進風險報告。
3. r1/r2 已把這條路徑從「目錄前綴」收斂成「精確檔名清單」,但收斂後仍是純路徑比對,只要改動落在那 15 個精確路徑上(不論是工具自己的更新還是消費專案自己對這幾支檔動手),risk 分級與代碼審門檻就一起被繞過。

### F21 併發對同一篇筆記 append 會撞上 atomic_write_verify/_write_lf 共用且不含 PID 的暫存檔名,rc0「成功」不保證真的落盤
severity: major
blocking: 是 — 錯誤處理裂開裸 traceback,且觀測到「回報成功的那幾筆反而不在檔案裡、回報失敗的那幾筆倒進去了」這種成功旗標與磁碟內容對不上的情況
引句:「atomic_write_verify(path, new_lines, key,」
1. `atomic_write_verify` 的 `tmp = path.with_suffix(path.suffix + ".lumos-tmp")`(scripts/lumos:10841)與 `_write_lf` 內層再包一次的暫存檔名(scripts/lumos:10819-10821)都是同一篇筆記的固定字面路徑,不含 PID/隨機字尾,也沒有檔案鎖。
2. 親自重現:6 個 process 同時對同一篇筆記 `append about_code <各自不同的值>`,多次試驗裡穩定出現 `FileNotFoundError: [Errno 2] No such file or directory` 於 `_write_lf` 內的 `os.replace(tmp, path)`(scripts/lumos:10821),此例外不是 `ValueError`/`RuntimeError`,不被 dispatcher 的 `except (ValueError, RuntimeError)` 接住,rc 變成 1、印出裸 Python traceback;同一次試驗裡最終檔案內容是 `g0.ts`/`g4.ts`(這兩支恰好是回報 rc1 失敗的),而回報 rc0 成功的 `g2/g3/g5` 反而不在檔案裡。
3. ★誠實補充★:同一支 crash 用既有欄位 `tags`(非本輪新增,append 邏輯 r1 之前就有)一樣能重現,根因 `atomic_write_verify`/`_write_lf` 不是本輪改動;但 about_code 這個新功能的使用情境(多位審查者/多個 session 各自認領不同程式檔往同一篇筆記加)比舊欄位更容易把這個既有缺陷從「機率低」推成「常態會撞到」,而 `_write_lf` 現有的接受注記只承認「last-write-wins」這種軟性覆蓋,沒有承認會裸 crash 這一種。

## 前兩輪修法驗收
F1:修到 — `_VENDORED_ALL` 精確清單+`_is_vendored_path` 整名比對取代目錄前綴,測試⑤驗證專案自己放在 scripts/hooks/scripts/templates 的檔仍被掃到、tier 仍判 high(但同一支修法留了 F20 那個殘餘洞,方向相反)。
F2:修到 — lint_claims 在對齊/未對齊兩條路徑判斷之前就先濾掉 vendored 命中,測試⑦兩種 aligned 值都驗過。
F3:修到 — 刪除行那條路改呼叫 `_stack_changed_ok(cur_file, _skip_vendored)`,測試⑥確認純刪行不再觸發棧別題。
F4:修到 — about_code 拿掉 set 專用路,只剩 append/remove,測試⑧確認 `set about_code` 直接被擋 rc2、原值沒被動。
F5:修到 — `_about_code_path` 依序擋絕對路徑、`relative_to` 的 ValueError 擋跳出 repo、`is_dir()` 擋目錄,測試⑤四種壞路徑全 rc2 且檔案不動。
F6:修到 — set 分流整條移除後只剩 append/remove 依 LIST_KEYS 走同一套規則,不再有純量/清單雙軌。
F7:修到 — 含冒號空白的路徑走 append(`fmt_list_item` 自動加引號),測試④確認讀回來一字不差。
F8:修到 — 依 r2 三席核對事故筆記已改成「只做排序、不建連結」,本輪快照未再變動這篇筆記。
F9:修到 — `_VENDORED_TREE_DIRS` 常數同時餵給 `_deinit_remove_vendored` 與 `_vendor_toolchain`,不再各寫一份。
F10:修到 — 隨 F4/F6 移除 set about_code 分流,原本命名不一致的 `_set_about_code` 已不存在。
F11:修到 — `_stack_ext_counts` 的 `rd = relpath(...)` 只在每個目錄算一次(os.walk 外層),不在檔案迴圈內重算。
F12:修到 — `_is_toolchain_repo` 判別鍵由測試④釘住:工具鏈本體 repo 裡 `scripts/lumos` 照樣要掃。
F13:修到 — `_list_scalar_value` 改成「去引號後的值本身」判準,測試⑨b 對整串加引號、逗號前後多空白兩種繞法都擋下。
F14:修到 — `edit_fm_append` 純量早退與 `cmd_append` 的「new_fm==原值」早退都不寫檔、訊息改成「已經有」,測試⑩確認不再印「多了一項」。
F15:修到,但同一支修法另開新洞(見 F19) — 目錄可正常讀取時大小寫比對正確擋下(SRC/sub/A.ts 被判「跟磁碟不一致」),唯 `os.listdir` 讀不到時整段驗證 fail-open。
F16:修到 — `cmd_append` 頂層用 `_about_code_norm`(posixpath.normpath)比對,測試⑪確認 `src/../src/a.ts` 與 `src/a.ts` 判成同一筆。
F17:修到 — `cmd_remove` 對 about_code 先用 `_about_code_norm` 找出原始寫法再丟給 `edit_fm_remove`,測試⑫兩種舊寫法(`src/../src/c.ts`、`./src/gone.ts`)都清得掉。
F18:修到 — 授權標頭測試改用 `getattr(m, "_VENDORED_TREE_DIRS", ())`,不再手寫第三份目錄清單。

風險掃描清單那 1 條:誤報 — `scripts/lumos:17660` 的 `open(` 命中是 `_stack_changed_ok` docstring 裡描述「命中 open(...)」這個坑本身的中文說明文字,不是真的檔案 handle,該行前後沒有任何 `open()` 呼叫。

總結:最高 severity major,blocking 共 3 條
