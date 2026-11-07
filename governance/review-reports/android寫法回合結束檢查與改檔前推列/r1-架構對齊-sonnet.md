severity: major

**① 模組邊界**

另開一支收工鉤子、回合起點由送出提示鉤子記、決策列放進 `cmd_impact` 棧別題那一段,這三項都對齊既有做法。只有鉤子之間共用程式的方式不對齊。

- **另開收工鉤子,對齊。** 引句:「寫法檢查開新檔 `stop-lint-hook.py`,不塞進既有收工點名那支(預算各算各的)」。
  - 既有註冊表是每支鉤子一筆預算:`scripts/merge-claude-settings.py:110`。`check-graph-sync.py` 的預算是 40,`scripts/merge-claude-settings.py:119`。
  - 新增一個檔名和一個預算值,跟既有結構同形。
  - 檔名要進 `_GLOBAL_CLAUDE_HOOKS`:`scripts/lumos:34136`。
- **決策列併進棧別題通道,對齊。** 引句:「決策列比對併進棧別提問那條通道,不另起剝字串與觸發比對」。
  - `stack_questions_applicable` 本來就是 `cmd_impact` 在這一段算出來的:`scripts/lumos:62519`、`scripts/lumos:65351`。
  - 去重用既有的 `_voice_once`:`scripts/hooks/claude/impact-hook.py:825`。
- **F1 鉤子之間用 importlib 互相載入,對不齊。** 引句:「用 `importlib` 載入同目錄的 `check-graph-sync.py` 取用,不抄第二份」。
  - 現有鉤子共用東西只有一種做法:`sys.path.insert` 加 `from _hookevent import …`。見 `scripts/hooks/claude/impact-hook.py:818`、`scripts/hooks/claude/dispatch-lens-hook.py:346`、`scripts/hooks/claude/bypass-ask-hook.py:28`。
  - `scripts/hooks/claude/` 底下沒有任何一支鉤子用 importlib 載另一支鉤子。
  - 全庫唯一的 importlib 載入掛鉤檔,是主程式的 `_load_hook_file`:`scripts/lumos:72802`。那是 lumos 對鉤子,不是鉤子對鉤子。
  - 載入含連字號的 `check-graph-sync.py` 還會連帶啟動它的模組層全域狀態,例如 `_BUDGET_START`:`scripts/hooks/claude/check-graph-sync.py:685`。
  - 計劃自己得在 `main()` 補一句「先呼叫一次才不會算錯已耗」,等於為這個新做法補洞。
  - 對齊的做法是把 `_cache_dir_under_home`、`_stop_dir_ok`、`_safe_path`、`_inner_budget` 這類共用函式搬進底線開頭的共用模組,再走 `sys.path.insert`。
severity: major
  - blocking: 是

**② 命名與錯誤處理**

標頭、`--json` 最後一行、退出碼、閘名都跟既有一致。

- **標頭,一致。** 引句:「第一行固定 `LUMOS-STOP-LINT:這一回合改的程式有新增的寫法告警`」。既有是 `STOP_BLOCK_HEAD = "LUMOS-STOP:…"`:`scripts/hooks/claude/check-graph-sync.py:765`。
- **`--json` 最後一行,一致。** 引句:「stdout 最後一行是一個 JSON 物件」。
  - 鉤子讀 lumos 機讀輸出,既有做法就是取 `splitlines()[-1]` 再 `json.loads`:`scripts/hooks/claude/check-graph-sync.py:754`。
  - `LUMOS-BLOCKS:` 是推送掛鉤另一條文字通道,只在非 JSON 模式印:`scripts/lumos:72381`。
  - 兩者並存,各管各的呼叫端,計劃沒有硬把它們合成一套。
  - 計劃〈依據來源〉把 `LUMOS-BLOCKS:` 當 `--json` 的前例,說法有點牽強,但不構成第二套。
- **退出碼,一致。** rc1 擋、rc0 乾淨或刻意不查、rc3 沒檢查到、rc2 參數錯,全部沿用現有說明:`scripts/lumos:74320`。
- **閘名 `stop-lint`,一致。** 引句:「`stop-lint` 登記進 `_KNOWN_GATES`」。既有閘名也是這樣登記(`scripts/lumos:16919`),寫帳走 `_gate_event_or_warn`:`scripts/lumos:1925`。
- 這一問沒有不對齊的條目。

**③ 第二種做法**

porcelain 解析、時間戳檔、名額標記檔、JSON 與 `LUMOS-BLOCKS:` 逐項核對如下。

- **時間戳檔與名額標記檔,對齊。** 計劃用同一個 `_cache_dir_under_home` 建 `stop-turn`,再在 `stop-block/` 建 `.lint-<batch>`。這是照 `stop-block`、`stop-printed` 兩個既有目錄的樣子再開一個。`scripts/hooks/claude/check-graph-sync.py:768` 的註解明說參數化就是為了不抄第二份。
- **JSON 與 `LUMOS-BLOCKS:`,不是兩套。** 見第二問:兩條通道早就並存,各有各的呼叫端。
- **F2 porcelain 解析,計劃只盤點了一部分既有解析,對不齊。** 引句:「`_handoff_files` 自己內嵌的那份解析本案不遷移。」
  - 計劃新寫 `_porcelain_v1_entries`,並說「既有 `_porcelain_z_paths` 只回路徑、丟掉狀態碼」。
  - 但庫裡已有至少兩處自己解 porcelain 且保留狀態碼:`_tg_rb_pending`(`scripts/lumos:51031`)和 `_handoff_files`(`scripts/lumos:72987`)。前者的註解還直說「要帶狀態碼所以自己解 porcelain」。
  - 計劃只提 `_handoff_files`、沒提 `_tg_rb_pending`。
  - 新函式只收編 `_porcelain_z_paths`,結果是帶狀態碼的解析從兩份變三份。
  - 比較整齊的做法是新函式同時收編那兩處,或在計劃裡明講為什麼不收。
severity: minor
  - blocking: 否
- **F3 子程序逾時與訊號處理,是計劃新加的一種做法,對不齊。** 引句:「收到 SIGTERM(主程式現在沒有任何訊號處理器,這是新的,只在工作樹模式裝)」。
  - 我查了 `scripts/lumos` 和 `scripts/hooks/claude/*.py`,沒有任何 `signal.signal` 或 SIGTERM 處理。
  - 既有鉤子呼叫 lumos 的逾時是 `subprocess.run(..., timeout=_inner_budget())`:`scripts/hooks/claude/check-graph-sync.py:750`。
  - 本案改成 Popen、程序群組先 SIGTERM 再等 1 秒 SIGKILL,鉤子自己也轉發 SIGTERM。
  - 實驗 E3 的依據成立,`_kill_proc_group`(`scripts/lumos:26640`)也確實直接 SIGKILL,所以這是有理由的新增。
  - 它不是結構錯誤,但是庫裡第一個訊號處理器和第一個「先 TERM 後 KILL」,應記為新慣例,並寫進 `Systems/hook逾時預算`。
severity: minor
  - blocking: 否

**⚠ 交編排者**

計劃依賴的 `_kt_decision_table`、`_kt_trigger_re`、`_kt_toolchain_root` 和 `_strip_c_comments(kotlin=True)`,在這個 repo 裡找不到,據說在 `android-situation-evidence` 工作樹。我無法核對它們的介面與名稱,所以範圍 3 和白名單是否真的沿用既有做法,這一輪判不了。等那條線合進主線後要再對一次。

不對齊共 3 條,其中會擋的 1 條。
