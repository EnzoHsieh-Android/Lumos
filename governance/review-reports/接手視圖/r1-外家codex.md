severity: major

### 1 / major / 系統提醒會截斷「最後一輪動作」，測試卻只驗人話
引句:「尾端是系統提醒:人話照抓、不抓提醒」
位置:scripts/test_lumos.py:30581
為什麼是問題:輸入順序為「真實 user → Edit → tool_result → isMeta user」時，`collect_turn_actions` 會在尾端的 meta 訊息立即停止，回傳空的 `turn_files`；現有測試只檢查 `last_user == "改 f2"`，完全沒有檢查 Edit 是否仍被抽出，所以測試綠但接手視圖會漏掉實際改檔。
建議:讓輪次解析器排除 system/meta/compact user，並在此測試斷言 `turn_files == ["scripts/f2.py"]`。

### 2 / major / 自動選逐字稿可能把另一個並行 session 當成待接手者
引句:「自動挑逐字稿:~/.claude/projects/<slug>/ 下 mtime 最新的 .jsonl」
位置:scripts/lumos:19976
為什麼是問題:同一 checkout 同時有 A、B、接手者三個 session 時，只排除接手者 ID 後會直接選 mtime 較新的 B，即使真正留下目前計劃改動的是 A；程式沒有比對逐字稿內的 `cwd`、branch、計劃路徑或 git 狀態，會以肯定語氣展示錯人的意圖。測試只造「自己＋唯一另一份」，沒有覆蓋兩份候選。
建議:多候選時以逐字稿 cwd 與計劃檔/工作樹線索篩選；無法唯一判定就回「意圖不可得」並列候選，要求 `--transcript`。

### 3 / major / fail-open 沒包住最後一句人話的解析
引句:「任何一步失敗都回原因,不炸、不猜。」
位置:scripts/lumos:20074
為什麼是問題:逐字稿含合法 JSON `{"type":"user","message":{"content":null}}` 時，`_is_real_user_input` 會接受它，隨後第 20086 行對 `None` 迭代而拋 `TypeError`；這段在 `collect_turn_actions` 的 try/except 外，因此整支命令 traceback，而不是 rc0 的「意圖不可得」。類似地，形狀異常但合法的 `session_meta.payload` 也可能在第 20062 行 `.get` 時炸掉。
建議:把逐字稿形狀解析整段納入 fail-open 邊界，並對 `message/content/payload` 做明確型別檢查。

### 4 / major / 宣稱支援的路徑集合先被 ASCII 無空白正則砍掉
引句:「計劃點名的程式檔:重用派工鏡頭的路徑正則與過濾」
位置:scripts/lumos:19197
為什麼是問題:計劃點名 `scripts/資料 處理.py` 時，正則只接受 `[A-Za-z0-9_./\\-]+`，候選會被截成 `scripts/` 或根本不收；因此後面的 `git status --porcelain -z` 即使能正確承載空白和 UTF-8 路徑也永遠看不到它。現有 fixture 全是 ASCII、無空白，未驗使用者要求的路徑形狀。
建議:不要用派工鏡頭的窄正則當檔名解析器；新增空白、非 ASCII、rename/copy 及子目錄 root 的真 git 測試。

### 5 / major / 唯讀命令會執行工作樹中的 Python hook
引句:「importlib 匯入收工 hook 的逐字稿解析器」
位置:scripts/lumos:20011
為什麼是問題:執行 `lumos handoff` 會透過 `exec_module` 執行 `scripts/hooks/claude/check-graph-sync.py` 的所有頂層程式碼；`__main__` 守衛只能保護主入口，不能阻止 import、常數初始化或未來新增的頂層副作用。第三方投稿或未提交改動只要改這支 hook，就能在看似唯讀的查詢中寫檔、啟程序或讀取其他資料。
建議:把共享解析器移到無副作用的專用模組並正常 import，且用測試鎖定「載入模組不產生任何外部動作」。

總結:核心 git 狀態思路可用，但目前有錯 session、漏動作、可 traceback、漏常見路徑及執行可變 hook 五個重大洞；實際開過 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/398a22b5-f103-42bd-b8b1-1e3ff2ac1f8d/scratchpad/handoff.diff`、`docs/lumos-toolchain-knowledge/Projects/接手視圖_計劃.md`、`scripts/lumos`、`scripts/test_lumos.py`、`scripts/hooks/claude/check-graph-sync.py`、`/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md`。
