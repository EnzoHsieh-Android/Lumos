severity: minor

我只審了 r2-snapshot.patch 裡 `scripts/lumos` 的合批編譯檢查段(`_KillCompile`、`_choice_task_swap`、`_choice_compile_cmd`、`_choice_compile_errors`),沒有跑實驗。派工詞要我檢查的 dispatch-lens 鎖檔我沒動,也沒刪。

**infra 題**

- **新的 `.git` 判法擋不擋得住 `..`、捷徑:擋得住。**
  - 判法是先 `os.path.realpath`,再看 `Path(relpath(target, wt_real)).parts` 裡有沒有 `.git`。
  - 指向 `.git` 的捷徑和 `..` 組合,都會先被解開成真實路徑才比對,所以抓得到。
  - 指到工作樹外的,被前一道 `startswith(wt_real + os.sep)` 擋掉。
- **大小寫:擋不住,但要多步偽造才走得到,標 minor。**
  - 比對是區分大小寫的字面 `.git`,macOS 的 APFS 預設不分大小寫,`os.path.realpath` 也不會把大小寫統一。
  - 理論上,repo 內若有捷徑指向 `.GIT/hooks` 之類的路徑,`realpath` 後的 parts 是 `.GIT`,會被放行;寫入時實際落在 `.git/hooks`。
- **換任務共用函式組出的指令:沒有新的 shell 插值面。**
  - `_choice_task_swap` 用 `re.escape` 處理模組名與任務名,再用 `lambda` 當 `re.sub` 的替換,沒有反斜線展開的問題。
  - 換進去的任務名是 `compile{變體}UnitTestKotlin`,變體限定 `[A-Za-z0-9]*`,不含 shell 特殊字元。
  - 指令其餘部分一律來自 `.lumos/config.json` 的 `run_cmd` 本身,走既有的 `_kill_run(shell=True)`;這份設定本來就是使用者自己的指令,不是新增的不可信輸入。
  - 編譯器輸出只做比對(`realpath` 後比是否在工作樹內),沒有拿去讀、寫或執行。
  - 還原用 `git checkout -- :(literal)<相對路徑>`,有 `--` 和 `:(literal)`,檔名不會被當成選項或萬用字元。

**發現**

severity: minor
blocking: 否
引句:「if not target.startswith(self.c.wt_real + os.sep) or ".git" in Path(os.path.relpath(target, self.c.wt_real)).parts:」
- 誰:能讓 repo 帶一個指向 `.GIT/...` 的捷徑的人(例如惡意分支)。
- 從哪:choice-kill 的合批編譯檢查。
- 送什麼:一個指向 `.GIT/hooks/...` 且該檔存在、檔內含壞法 `old` 恰好一次的配方。
- 拿到什麼:在不分大小寫的檔案系統上,`.git` 判法被繞過,合批編譯前的寫入會落在真正的 `.git` 底下。
- 為什麼只是 minor:
  - `restore` 的 `finally` 會寫回原文並比對,寫入只維持編譯那幾秒。
  - git 在 macOS 上不會追蹤 `.GIT` 路徑,捷徑要自己偽造。
  - 這屬於刻意多步偽造,在範圍外。
- 若要順手補:比對前先把路徑轉小寫,例如 `p.lower() == ".git"`。

**三類**

- **① 提示注入:已看,無。** 本段沒有新增把自由文字送進給 AI 的派工詞或 hook 附加段;編譯輸出只用來算嫌疑行,不回顯成指令。
- **② 讀寫與執行越界:只有上面那一條。** 寫入目標有 `realpath` + 工作樹前綴 + `.git` 三道把關,還原走字面路徑。沒有新增下載網址、環境變數覆蓋或密鑰。
- **③ 非刻意一步繞過:已看,無。**
  - 被 Ctrl-C 收掉時,`apply_compile` 的 `finally` 會先還原,還原後內容對不上就丟 `_KillPrepAbort`。
  - 檔名帶空白或中文:相對路徑走 `:(literal)`,錯誤輸出用 `urllib.parse.unquote` 解碼 `file://`。

總結:最高等級是 minor
