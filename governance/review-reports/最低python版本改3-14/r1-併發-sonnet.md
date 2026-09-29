severity: major

## F1 防重跑環境變數會被子孫行程繼承,子孫裡的舊版 lumos 明明有 3.14 卻被直接報錯
severity: major
blocking: 是 — 照字面實作,只要重跑過一次,整棵子行程樹裡任何用舊版 python3 起的 lumos 都拿到硬錯誤而不是重跑,會做出間歇壞掉的系統
引句:「重跑前設一個環境變數,重跑後的程序若還是舊版就直接報錯,不會無限重跑。」
file: `scripts/lumos:1`
1. spec 只說「重跑前設環境變數」,沒說旗標的值與作用範圍。旗標一旦 export,就跟著 lumos 之後開的所有子行程走(git、codex/claude 席位、測試、hook 裡的 subprocess)。
2. 現況 `scripts/lumos` 第 1 行是 `#!/usr/bin/env python3`,安裝出的 `lumos` 指令走 PATH 上的 python3(本機 /usr/bin/python3 是 3.9.6)。子孫行程只要再打一次 `lumos`,就是「旗標已設 + 直譯器是 3.9」——依 spec 走「還是舊版就報錯」,回 2,但此刻 /opt/homebrew/bin/python3.14 明明存在。
3. 重現:LUMOS_REEXEC=1 /usr/bin/python3 scripts/lumos <任一子命令>(模擬子孫);spec 的分支邏輯無法分辨「我剛被重跑」與「我是重跑者的孫子」。
4. 修法方向(可實測):旗標值存 os.getpid()。os.execv 保留 pid(POSIX 語意),孫行程 pid 不同,旗標與自己 pid 不符就當沒設。實測 python3.14 對 execv 前後 pid 相同(97802)。Windows 走子行程改成旗標存父 pid 比對,或用 argv 私有記號取代環境變數。
5. 這也是 [S2]「重跑後仍是舊版應直接報錯」的條款缺口:測試只會測「一層」,測不到孫行程。

## F2 uv 候選在最壞順序下每次呼叫多付約 190 毫秒,且清單沒有任何快取或短路上限
severity: major
blocking: 是 — Claude/Codex 每次工具呼叫都會啟動 lumos,而舊註冊(仍寫 /usr/bin/python3 的機器)在重新安裝前每一次都走重跑路徑;spec 沒有量測也沒有預算,實作者會做出每次呼叫慢 0.2 秒的系統而不自知
引句:「依序試 `$LUMOS_PYTHON`、`python3.14`、`python3.15`、`python3.16`、`python3`、`python`,有 uv 時再試 `uv python find '>=3.14'`」
file: `scripts/hooks/claude/impact-hook.py:833`
實測(本機,10 次取平均,單次):
1. `python3.14 -c 'import sys'` 約 26 毫秒;`uv python find '>=3.14'` 約 189 毫秒(10 次 1.887 秒),是一般候選的 7 倍。
2. 舊版起 lumos、順序第一個候選(python3.14)就命中的重跑:模擬(3.9 起 + 子行程探測 + execv)10 次 0.95 秒,對照 3.9 直接跑 `-c pass` 10 次 0.30 秒 → 每次呼叫多約 65 毫秒。lumos 本體約 0.4 秒(`scripts/lumos --version` 5 次 1.92 秒),所以重跑多付約 15%。
3. 只有 uv 管的 3.14(無 python3.14 名稱在 PATH,常見於 uv python install 的機器)的最壞情況:前面 5 個候選失敗再加 uv,約 26+190=220 毫秒/次,每次呼叫都付,沒有任何快取。
4. 舊註冊會長期存在:spec 回退節自己承認「設定檔裡寫進去的直譯器路徑…要重跑安裝」,而 Claude 掛鉤(impact-hook 等)用 `[sys.executable, lumos, …]` 呼叫 lumos;掛鉤登記的若是舊 3.9 路徑,則 impact-hook、dispatch-lens-hook、check-graph-sync、lumos-entry-hook 每次都付重跑代價。dispatch-lens-hook 已把 subprocess 上限壓在「天花板 × 0.9」內(`scripts/hooks/claude/dispatch-lens-hook.py:308-318`),重跑吃掉的時間沒有算進去。
5. spec 未說:候選解析結果要不要記在環境變數(例如把找到的路徑放進 LUMOS_PYTHON 讓子孫直接命中),也未規定 uv 只在前面全落空後才呼叫。字面順序「有 uv 時再試」是最後一個,但沒明說命中就短路。要補:命中即停、結果寫入子行程環境(可結合 F1 的 pid 旗標)。
6. ⚠ 快取失效未定義:若採快取檔,uv 搬家(spec 誠實界線已提)後快取指向不存在的路徑,需要「快取路徑驗證失敗 → 重找」;spec 完全沒提快取,所以是缺口而非既有設計。

## F3 git 掛鉤的解析次數:每個掛鉤各解析一次,pre-push 內 22 個叫 lumos 的點必須共用同一次結果,spec 只說「source 共用檔」沒說解析發生在檔案載入時還是每次呼叫時
severity: minor
blocking: 否 — 只要共用檔載入時解析一次並給 PY 變數,實作者很難做錯;否則最壞也只是 22 倍探測,可從實測看出
引句:「`pre-commit`、`pre-push` 改 source 共用檔;找不到 3.14 時擋下(rc 1)並印同一段說明」
file: `scripts/hooks/pre-push:70`
1. 現況 `scripts/hooks/pre-push` 有 22 處 `"$PY"`,全部讀第 70 行一次算出的 `PY`。實測 shell 解析(python3.14 命中)10 次 0.27 秒 → 約 27 毫秒/次;最壞(只有 3.9、5 候選全走完+uv)10 次 2.08 秒 → 約 208 毫秒/次。
2. 若實作者把「找直譯器」寫成函式而在每個呼叫點呼叫,pre-push 最壞多 22×208≈4.6 秒。spec 沒明文要求「載入時一次、結果放 PY」。
3. 每次提交 = pre-commit + post-commit 兩次解析,推送 1 次;正常路徑各 27 毫秒,可接受。
4. 補一句「共用檔在被 source 時解析一次並設定 PY,呼叫端不重找」即可。

## F4 候選探測沒有逾時也沒有隔離 stdin,卡住的候選會拖死掛鉤或吃掉 stdin 內容
severity: major
blocking: 是 — 掛鉤與 Claude 工具呼叫都在有上限的預算內跑,一個不回的候選會讓整批提交/推送卡死,或吃掉 lumos 要讀的 stdin
引句:「每個候選跑一次「版本 ≥ 3.14 嗎」,挑第一個過的。」
file: `scripts/hooks/pre-push:26`
1. spec 沒有任何探測逾時。候選裡有已知會不回的形態:Windows 應用程式商店的 `python`/`python3` 別名 stub(會開商店或等待)、pyenv shim 卡在鎖、網路磁碟上的直譯器、`uv python find` 在含 `.venv`/`.python-version` 的專案目錄下額外掃描(⚠ 未在本機重現,依 uv 行為推論)。
2. shell 端(macOS 沒有 `timeout` 指令)沒有可攜的逾時手段,spec 要求兩處清單一致,但沒說 shell 端怎麼防卡。
3. stdin:pre-push 第 26-30 行先把 stdin 整批讀完(注釋寫明「後段 subprocess 會吃掉 fd0」),所以 source 共用檔的位置必須在 stdin 讀完之後,spec 沒寫這個順序;impact-hook 用 `input=` 送 payload、`curl … | python3 scripts/lumos sqlfluff-sarif` 這類管線給 lumos 的 stdin 是資料,Python 端探測若用預設 stdin,遇到會讀 stdin 的候選(例如被別名成互動殼的 `python`)就吃掉資料。
4. 補:探測一律 `stdin=DEVNULL`(shell 用 `</dev/null`)、Python 端 `subprocess.run(timeout=…)` 逾時視為該候選失敗並記進「找過的候選」清單。
5. 重跑的 execv 端無此問題(fd 原樣繼承,舊直譯器解析檔案時不讀 stdin);但要在 execv 之前不能有未 flush 的輸出,spec 也未提。

## F5 並行下的環境變數與每次重跑的候選探測是否對子行程共享,spec 未定
severity: minor
blocking: 否 — 多個 git 行程/掛鉤並行時各自解析、不共享可變狀態,互不干擾,最壞只是重複探測
引句:「重跑前設一個環境變數」
file: `scripts/hooks/pre-commit:50`
1. git 掛鉤是各自獨立行程,PY 是 shell 區域變數,並行的 commit/push 不會互相污染;環境變數只往下傳、不往同層傳,所以並行本身安全。
2. 唯一的共享風險就是 F1(往下傳);沒有寫入檔案的快取,也就沒有並行寫入競態。若後續為 F2 加快取檔,需照 CLAUDE.md 記憶條目「共用檔原子寫入」的慣例(暫存→自驗→replace),spec 目前無此設計,故此點只在採快取時成立。

## 各節
- 範圍:已讀,無 finding。
- 做法第 1、2 點:見 F1、F2、F4。
- 做法第 3 點:見 F3。
- 做法第 4 點(merge-claude-settings 寫 sys.executable):已讀;掛鉤註冊後絕對路徑固定為執行者直譯器,執行期不再重跑,效能面反而更好;舊註冊的代價見 F2 第 4 點。
- 做法第 5、6、7、8、9、10 點與條款 S3-S7、回退、實務隱患、誠實界線:已讀,資源與併發面無 finding。

總結:最嚴重等級為 major,blocking 共 3 條(F1、F2、F4)。
