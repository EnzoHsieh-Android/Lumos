severity: blocker

# r2 通才席審查報告(推播miss量測_計劃)

立場聲明:逐條驗證後,以下 6 條發現(F1–F6)是照 r2 快照字面實作會算錯或洩漏隱私的具體場景,其中 F1–F5 判 blocking。其餘段落逐節讀完、沒有另外的 finding,已在對應段落註記。

## 逐節審查

### frontmatter / summary / 白話 / 緣起 / PRIOR-ART

已讀,無 finding。summary 三顆 KEY 與正文條款(S1–S6)內容一致;緣起提到的「既有儀器 scan_file 把讀取跟推播清單取交集」「只解析必看段」兩點,對照 `governance/eval/lens-utilization/recount.py` 現況屬實(現版只有 `parse_pins` 解「必看」,`scan_file` 的 `bucket = row["touched"] if j > anchor[0] else row["pre_touched"]` 沒有 miss 概念)。PRIOR-ART 三點內部自洽。

### S1 推播清單解析四段

已讀,四段標頭文字與 `scripts/hooks/claude/impact-hook.py:build_ranked_context` 的實際輸出(必看/可能相關/另外/守衛面參考四個標頭字串、截斷行兩種文字)逐字核對相符,PIN_LINE 誤吃種類詞的描述也用非貪婪 regex 手算驗證屬實。但 S1+S2 共用的「一次編輯呼叫=一份注入文字=四段」心智模型,在 Codex 多檔 apply_patch 場景下不成立,見 F1。

### S2 miss 偵測與分類

錨點、讀取窗口、分三類判準（規則內兩條子規則、about_also 重複標記、事後才有)逐句對照 `_impact_reverse_lookup`(`scripts/lumos:19819`)與 `about_code` 欄位規則(`scripts/lumos:11035` `_about_code_path`)大致相符,唯獨兩處會在實作後算錯:F1(多檔 apply_patch 的錨點/內容歸屬)、F3(about_code 比對的路徑格式)、F5(事後才有的 git 判斷未提 --follow)。

### S3 搜尋零命中

已讀,三種零命中輸出格式與 `scripts/lumos` 的實際列印逐字核對相符(`共 0 篇候選`、`--json` 的 `candidates` 鍵、`0 處 / 0 篇`)。無新 finding。

### S4 每週留存

位置、週戳慣例、fail-open、`local/` 目錄與 `.gitignore` 的描述跟 `governance/autonomous-loop.sh` 的 `run_replay`(422–447 行)、`governance/autonomous_loop/replay_weekly.py` 的「先印 JSON 再印 LOG:」慣例逐項核對相符。但「版控那份不存逐字稿原文、不存查詢字串」這句隱含的隱私保證,在 F 的路徑格式沒被正規化時會被繞過,見 F4。

### S5 測試守門

已讀「本案新增的測試與既有 `t_lens_recount_classify` 都先 `_need_src`」這句本身沒錯,但守門測試的掃描範圍(「掃 `scripts/test_lumos.py` 裡提到 `lens-utilization` 的測試函式」)比這句話涵蓋的既有測試清單更大,見 F2。

### S6 README 同步

已讀,無 finding。`[manual:...]` 標記是本 repo 既有的人工檢核慣例(非機械擋),範圍描述(四段解析/miss三類與事後才有/零命中三種輸出/週跑與本機查詢檔)跟 S1–S4 條款一一對應,沒有遺漏項目。

### 邊界與不做

已讀,無 finding。「不動 impact hook」與 F1 不衝突——F1 是 recount.py 讀 hook 既有輸出時漏掉的解析範圍,不要求改 hook 本身。

### 承認的限制

「零推播分不出原因」「量不到 Bash 改檔」「零命中判法靠輸出字樣」三條已讀,回頭條件具體、無 finding。「用現在的圖譜判當時的推播」一條只討論 F(程式檔)改名的方向,沒討論筆記(N)改名的方向,見 F5。

### 實務隱患

併發/效能/資源三類已讀,r1 已用 `/usr/bin/time -p` 實測 27 秒與 1.7 秒、有具體逾時與快取設計,無新 finding。隱私類的具體風險見 F4。金流/對外送出/不可逆:不適用判斷成立(唯讀分析+可重跑檔案),無 finding。

### 驗收 / 審計修正紀錄

已讀。驗收清單覆蓋 S1–S5 的主要案例,但沒有任何一條測試涵蓋「一次 apply_patch 呼叫改多個檔」的情境(對照 `scripts/test_lumos.py:30285` 的 `t_codex_s1_impact_apply_patch` docstring 明寫「main 多檔合併成一個 additionalContext」,已是 hook 側現行且已測試的行為),這正是 F1 沒被攔下的原因。審計修正紀錄只是歷史記帳,無 finding。

## 發現

F1
severity: blocker
blocking: 是
引句:「逐字稿裡每一次 Edit/Write/MultiEdit(Codex 是 apply_patch)呼叫都是一列」
file: `scripts/hooks/claude/impact-hook.py:61`
file: `scripts/hooks/claude/impact-hook.py:756`
file: `governance/eval/lens-utilization/recount.py:273`
S2 把「一次 apply_patch 呼叫」當成「一次編輯=一個檔 F=一份四段注入」,但 `impact-hook.py` 的 `APPLY_PATCH_MAX_FILES=5` 與 `main()` 的 `for i, fp in enumerate(paths): ... chunks.append(ctx)` 證實一次 apply_patch 可以合併多個檔的 `build_ranked_context` 輸出成一份 `"\n\n".join(chunks)`(`t_codex_s1_impact_apply_patch` docstring 明寫「main 多檔合併成一個 additionalContext」)。既有 `_patch_target()` 只取 patch 標頭第一個路徑當錨,S1 描述的四段解析器若照現有 `parse_pins` 的「找到第一個標頭就處理、其餘略過」寫法沿用,會讓檔案 2–5 的推播內容整段消失、卻只在檔案 1 的一列裡報告完整,沒有任何驗收案例涵蓋這個場景。

F2
severity: major
blocking: 是
引句:「守門測試:掃 `scripts/test_lumos.py` 裡提到 `lens-utilization` 的測試函式,每支都要有 `_need_src(`」
file: `scripts/test_lumos.py:30577`
file: `scripts/test_lumos.py:30647`
S1(第 70 行)只點名既有 `t_lens_recount_classify` 需要補 `_need_src`,但 `scripts/test_lumos.py` 裡同樣用 `SourceFileLoader` 載入 `lens-utilization/recount.py`、同樣沒有 `_need_src` 的既有測試還有 `t_codex_s3_recount_codex`(30577 行起)與 `t_codex_s3_r1_fixes`(30647 行起)。照 S5 字面實作 `t_lens_recount_tests_guarded` 這支新守門測試,它自己在導入的當下就會抓到這兩支漏網測試而翻紅,S1 給的修復清單不完整。

F3
severity: major
blocking: 是
引句:「關於欄:該筆記開頭的 about_code 欄位含 F。」
file: `scripts/lumos:11045`
file: `governance/eval/lens-utilization/recount.py:384`
Claude Code 的 Edit/Write/MultiEdit 工具規定 `file_path` 一律是絕對路徑,既有 `scan_file` 的 `target = anchor[2].get("file_path")`(384 行)因此對主/子 session 的列都是絕對路徑;而 `about_code` 欄位被 `_about_code_path` 強制要求是 repo 相對路徑(「about_code 要寫 repo 相對路徑,「{v}」是絕對路徑」是它的擋錯訊息)。S2 沒有提到要把 F 轉成相對路徑才能拿去跟 about_code 比對,照字面直接比對(`F in about_code清單`)會讓「關於欄」這一類對絕大多數 Claude 主/子 session 的列永遠比不中(Codex 因為 patch 標頭本身就是相對路徑而僥倖不受影響)。

F4
severity: major
blocking: 是
引句:「版控裡只有推導列(節點名、檔名、計數),工作階段代號存雜湊」
file: `governance/eval/lens-utilization/recount.py:385`
延續 F3 的根因:若實作時沒有額外把 F 正規化成 repo 相對路徑就直接寫進每週留存檔,`ftype` 計算式(385 行)證實現有 `target` 對 Claude 主/子 session 就是本機絕對路徑(如 `/Users/<使用者>/...`)。這樣一來每週一份、進版控的推導檔就會把機器使用者名稱與本機目錄結構永久公開進這個公開 repo,直接牴觸本節「不存逐字稿原文」想避免的那種永久外洩,而且 S4/驗收都沒有一條測試斷言「F 在輸出裡是 repo 相對路徑」。

F5
severity: major
blocking: 是
引句:「那篇筆記在那次編輯之後才新建(git 第一次加入的時間晚於編輯,或還沒進版控)」
file: `/tmp/lumos-r2-review-git-test`(本席臨時實驗:`git mv` 改名後,`git log --diff-filter=A -- <新路徑>` 若不加 `--follow` 回傳的是改名那次的時間,不是原始建立時間;加 `--follow` 才回傳原始時間)
「用現在的圖譜判當時的推播」那條限制只討論程式檔 F 改名的方向,沒討論筆記本身被改名/搬移的方向。S2 若照字面用「git 第一次加入的時間」(不指定 `--follow`)判斷筆記是否「事後才有」,任何在編輯之前就存在、但之後被改名或搬移過的筆記,都會被誤判成「事後才有」而被排除出 miss 統計,而且這是本案自己已經知道要防的同一類問題(F 改名)在 N(筆記)身上的鏡像,驗收清單沒有任何一條案例涵蓋筆記改名。

F6
severity: minor
blocking: 否
引句:「讀取窗口:從那次編輯之後,到同一個工作階段的下一次編輯為止」
file: `governance/eval/lens-utilization/recount.py:364`
既有 `is_sub = "/subagents/" in str(path)`(364 行)證實 subagent 逐字稿是獨立檔案、獨立跑 `scan_file`,S2 的讀取窗口只在同一份逐字稿內比對,若主 session 派子代理去讀圖譜筆記再回來編輯(本 repo 常見工作模式),那些讀取落在另一份檔案裡、沒有自己的編輯錨點,會被整段丟失、不進任何一類統計,「承認的限制」沒有列出這個天花板。

## 圖譜鏡頭固定席逐條判定

- Systems/canary-audit.md ★INVARIANT★ 兩條(canary record/second 落盤驗證、second 為純 telemetry):不影響——本案明寫「lumos 不新增任何寫帳」,weekly archive 是獨立報表檔,不呼叫 `lumos canary record`/`second`,不共用也不宣稱滿足這兩條合約。
- Systems/retrieval-ranking.md:不影響——本案不改排序演算法本身,`edit_universe`/`lumos impact --file` 只被當唯讀查詢用,排序邏輯與命中判準未變動。
- Issues/vendored測試套件在消費端假紅.md:相關但非破壞——S5 本身就是為了防這個已結案事故的同型態重演而設的守門,但 F2 指出守門範圍字面上沒蓋到 `t_codex_s3_recount_codex`/`t_codex_s3_r1_fixes`,若不修等於同一支檔案裡留了兩個未堵的洞。
- Issues/canary-record未落盤事件.md:不影響——本案不寫入 canary 帳本,跟這個事故的落盤驗證機制無交集。
- Issues/code-loop守衛main-direct盲區.md:不影響——這是分支直推繞過代碼審 guard 的問題,本案是唯讀量測工具,不涉及推送守衛路徑。
- Issues/hook卸載殘留註冊.md:不影響——本案不改動 hook 的安裝/卸載邏輯,只讀 hook 產生的既有輸出文字。
- Issues/init-force-slug誤用basename.md:不影響——跟 `lumos init --force` 的 vault slug 邏輯無關聯,本案未觸碰 init/slug 路徑。
- Systems/known-pitfall-refresh-token.md:不影響——它連結進來只是因為它是 `retrieval-goldset.json` 裡的樣本題目節點,跟本案的技術內容(OWASP session/refresh-token)完全無關。

## 總結

全份最高嚴重度是 blocker,blocking 共 5 條。
