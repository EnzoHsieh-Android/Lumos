severity: major

**1. 分層與依賴方向:對齊。**
- 讀取端 `_events_*` 與 `cmd_events` 放在 `enforcement_status` 之前,`main()` 裡也在 `enforcement` 分派之前,位置與鄰居一致。
- r1 的 F1、F2 已改成呼叫既有的 `_anchor_repo_root`(`scripts/lumos:22378`)與 `_lens_git`(`scripts/lumos:41812`),不再另寫 repo 根解析,也不再借 `_testmap_git`。
- `_sync_global_hooks` 現在只有一個呼叫點,放在合併器之前;不併進回傳字串的理由有寫在註解裡。
- `enforcement_status` 的 ⑪ 層不呼叫外部指令,自己用 try 包住,與其他層一致。
- 拆除仍留在 `cmd_uninstall` 而不是 `_teardown_global_hooks`(`scripts/lumos:18890` 一帶),這是 r1 F4 的殘留,見驗收節。

**2. 命名與錯誤處理:一處小差異(F2),其餘對齊。**
- `_plugin_sync_msg` 的狀態字串與 `_sync_msg`(`scripts/lumos:22214` 附近)同一路。
- 例外只接 `(RuntimeError, ValueError, OSError, TimeoutExpired)`,失敗時附手動指令,風格一致。
- `_events_prune` 的 `rmtree` 現在包在 `try/except OSError`,與 `_note_audit_work_dir` 的寫法一致。
- 不一致:neighbors 的「擋下」一律印到 stderr(`cmd_ci_status` 在 `scripts/lumos:39809`,`cmd_handoff` 在 `scripts/lumos:45927`、`45935`、`45943`,`_anchor_repo_root` 在 `scripts/lumos:22383`),`cmd_events` 的三處「擋下」都印到 stdout(見 F2)。

**3. 第二種做法:有兩處(F1、F3)。**
- 新增 `_events_clean`,在專案已有三套控制字元清理時又長出第四套(見 F1)。
- `_EVENTS_SESSION_RE` 用 `__import__("re").compile`,但檔頭 `scripts/lumos:58` 已經 `import re`,其餘 `re.compile` 都是直接寫(見 F3)。
- `_events_path_safe` 逐層檢查符號連結。我在 `scripts/lumos` 沒找到同功能的鄰居函式(`_disk_spelling` 在 `scripts/lumos:18051` 是拼寫對照,不是安全檢查),不算第二種做法。
- `_same_local_path` 用 `os.path.realpath(os.path.expanduser(...))`,檔內已有 `os.path.realpath` 的用法,沒有同功能的現成函式,不算。
- 測試的環境變數還原已改成 `mock.patch.dict(os.environ, ...)`(HEAD 版測試檔有 29 處這種用法),與主流一致。
- 假 `claude` 的寫法同 r1 的判斷,不算第二種。

### F1 新增 `_events_clean`,專案已有 `_esc_clean` 與 `_note_reread_show` 兩套控制字元清理
severity: major
blocking: 是 — 鄰居已有同功能的終端消毒函式,新碼另寫一套,規則還比它們窄。
引句:「return "".join(ch for ch in str(text) if ch in "\t" or (ord(ch) >= 32 and ord(ch) != 127 and not 0x80 <= ord(ch) < 0xA0))」
- `_esc_clean`(`scripts/lumos:10873`)做同一件事:控制字元(含 ESC 與 C1)換成空格,還可以截斷長度。
- 另有 `_PATH_SPECIAL_CATS` 與 `_path_special_chars`(`scripts/lumos:31680` 附近),再加 `_note_reread_show`(`scripts/lumos:31706`)。這幾個是 Unicode 類別式的清理,涵蓋 Cc、Cf、Zl、Zp。
- 新函式有三處和既有做法不同:
  - 是剝除,不是換空格。
  - 保留 `\t`。
  - 不處理 Cf 與 Zl/Zp,所以 U+202E 雙向覆寫與 U+2028 仍會原樣印出。這個差異正是 `_note_reread_show` 註解裡記過的資安缺口(代碼審 r2 資安席 F1)。
- 這已經是同一個缺口的第二次重蹈,不是純風格差異。
- 修法是改呼叫 `_esc_clean`,或把 `_note_reread_show` 的類別式清理抽成共用。

### F2 `cmd_events` 的「擋下」訊息印到 stdout,鄰居一律印到 stderr
severity: minor
blocking: 否 — 三段式內容對,只是輸出流與 `cmd_ci_status`、`cmd_handoff`、`_anchor_repo_root` 不一致。
引句:「print(f"擋下:--days 要是 1 到 {_EVENTS_MAX_DAYS} 的整數,收到 {_events_clean(days)!r};什麼都沒刪。")」
- 同函式內 `擋下:事件帳路徑` 與 `擋下:找不到會談` 兩處也是 stdout。
- 呼叫端若用 `2>/dev/null` 或只看 stderr,會漏掉擋下原因。
- 同一函式先呼叫 `_anchor_repo_root`,那一步印 stderr,同一支指令因此混用兩種輸出流。

### F3 用 `__import__("re")` 編譯正規式,檔頭已 `import re`
severity: minor
blocking: 否 — 結構對,只是匯入寫法與檔內其他正規式常數不同。
引句:「_EVENTS_SESSION_RE = __import__("re").compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")」
- `INLINE_CODE_RE`、`WIKILINK_RE`、`TOP_KEY_RE` 等(`scripts/lumos:364`、`415`、`417`)都是直接寫 `re.compile`。

### 前輪修復驗收(r1 本鏡頭)
- F1 `_events_repo_root` 重複且壞 `--repo` 沒擋:已修好。`cmd_events` 呼叫 `_anchor_repo_root`,不是目錄時回 2。我只對照了 `cmd_events` 的呼叫,沒實跑壞 `--repo` 的案例。
- F2 借用 `_testmap_git`:已修好,改用 `_lens_git`,失敗與逾時回 None 的處理也寫對了。
- F3 `--prune` 刪檔沒處理例外:已修好。`rmtree` 包在 `try/except OSError`,失敗名單會回報;docstring 仍標註「唯讀;`--prune` 例外」。
- F4 外掛拆除位置與回報:修一半。重複呼叫已消掉,成功時也會印「已移除」;但拆除仍在 `cmd_uninstall`、不進 `removed` 清單、不進 `_teardown_global_hooks`。這個設計取捨在程式註解裡有交代。
- F5 `_with_env` 還原寫法:修一半。helper 內部改用 `mock.patch.dict`,與主流一致;但 `t_enforcement_ledger_row` 仍用行內 PATH try/finally 還原,同一份 diff 裡還是兩種寫法並存。

不對齊共 3 條,其中 major 1 條
