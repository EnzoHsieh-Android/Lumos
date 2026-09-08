severity: blocker

# r1 接手的人(sonnet)——審查有沒有用記帳_計劃

立場:三個月後拿這本帳回答 Enzo「審查到底有沒有用」的人。方法:讀完凍結快照全文;對照 `scripts/lumos`(`git show HEAD`)裡 `cmd_canary`/`_report_severities`/`_loop_status_disposal`/`_render_gov_stats`/`cmd_loop_replay` 的現況代碼;對 `docs/.canary-log.jsonl`(1216 筆)跑機械統計;從 `governance/review-reports/` 隨機抽 5 份跨迴圈報告手算 [S1] 演算法,另外對「今天(2026-09-08)」新寫的 8 份報告與「code-clause-bindings 兩個編號」全部 19 筆重算,核對 spec 自己引用的驗證數字。中文模糊措辭類不報。

## 為什麼(1216 筆現狀陳述)

已讀。1216/0/1 三個數字(總筆數/refute_verdicts 填寫數/escape 帳筆數)逐行 parse `docs/.canary-log.jsonl`、`.escape-log.jsonl` 核對過,站得住。

### F1
severity: major
blocking: 是
判準:不改;spec 用來支持「16/18 一致、2 份不一致」的樣本,同一套演算法機械重算後只有 10/19 一致,而且真正的誤差來源(外家否決-codex 席位模板,7/7 mismatch)這節完全沒提到。

佐證:引句「有 16 份跟手填的 `--findings` 一致;不一致的 2 份是驗收輪的架構席報告」(為什麼節)。19 筆全量重算:match=10、mismatch=9,外家否決-codex 7/7 全 mismatch(根因見 F3)。

## [S1] 席位列自動數「報了幾條」

### F2
severity: blocker
blocking: 是
判準:不改;[S1] 演算法對今天(寫側嚴重度硬擋生效日之後)寫出的 8 份現行報告裡 6 份 undercount 到 0 或接近 0,正是 spec 自己點名過、卻沒被 [S1] 規則涵蓋的「嚴重度嵌在標題」格式,即使放寬成前綴比對仍 6/8 mismatch。

佐證:引句「今天早上的 8 份(嚴重度嵌在標題破折號後,如」(為什麼節)。file: `governance/review-reports/code-enforcement-obs/r1-通才.md:1,3,33,67`(帳面 `findings=3`,重算=0);帳列 `loop=code-enforcement-obs round=r1 auditor=通才 ts=2026-09-08T12:24:55+08:00`。

### F3
severity: major
blocking: 是
判準:不改;「排除第一行的檔級 severity」假設檔級摘要必在實體第 1 行,但「外家否決-codex」席位模板第 1 行固定是 HTML 註解、摘要在第 2 行,今天下午兩個編號共 7 筆該席位帳自動數 100% 比帳面 `findings` 多 1,系統性偏誤非隨機誤差。

佐證:引句「排除第一行的檔級 severity」([S1] 節)。file: `governance/review-reports/code-clause-bindings/r1-外家否決-codex.md:1`(HTML 註解)、`:2`(真正檔級 `severity: major`);帳面 `findings=4`,重算=5。

## [S2] 載體列多一組「駁回清單」

### F4
severity: major
blocking: 是
判準:不改;[S2] 靠模板讓 `--refuted-set` 被填的策略,跟 `--refute-verdict` 已在用、已證明 0/1216 失敗的機制幾乎同構,spec 沒解釋這次會不一樣的理由。

佐證:引句「refute_verdicts 就是前科」(實務隱患節)。file: `skills/lumos-design-loop/templates.md:77`、`skills/lumos-design-loop/reference.md:145`(`--refute-verdict` 早已在模板與參考文件裡,結果仍是 0/1216)。

## [S3] 讀側:每輪一行、全庫一段,兩本帳分開

### F5
severity: minor
blocking: 否
判準:不擋;「駁回 R」這個數字沒有機制區分「審查員誤判(可信)」與「編排者不想承認自己駁錯(利益衝突)」,是資訊揭露設計缺口,非措辭精度問題。

佐證:引句「編排者機械重現後判 MISS、沒折也沒放行的發現」([S2] 節)。

### F6
severity: major
blocking: 是
判準:不改;「兩本帳不可混算」固定句只擋人記帳與機器擋帳互相冒充,沒擋在人記帳內部拿 Σ折/Σ報 當「審查有用率」算——F2/F3 已證明 Σ報分母本身系統性不準,拿它算比率比不算更危險。

佐證:引句「不要拿這裡的數字去算那裡的比率」([S3] 節)。

### F7
severity: major
blocking: 否
判準:不擋(spec 已誠實用「?」標缺值),但沒講全庫彙總數字要多少筆有 `reported` 才有意義;全庫 227 個相異迴圈裡 102 個(45%)14 天內無新帳、按「不回填」政策永久印「報 ?」,而 `loop status --disposal` 逐迴圈讀法不吃 `since_days` 窗口。

佐證:引句「尾端(觀測,不進合取)每輪印一行」([S3] 節)。統計:近三月月增量 301/544/369 筆,相異迴圈 227,14 天內無新帳 102。

### F8 ⚠
severity: major
blocking: 否
判準:⚠ 判不準,待實作前澄清——「每輪印一行」若讀成「單次呼叫吐出全部歷史輪」,現有 `_loop_status_disposal` 只取 `next(reversed(groups.items()))`(僅最新一輪)不支援,需新開對 `groups` 的迭代;若讀成「每次問這一輪印這一輪」,現有結構直接夠用,spec 沒說是哪一種。

佐證:引句「讀側:每輪一行、全庫一段,兩本帳分開」([S3] 節標題)。file: `scripts/lumos`(`_loop_status_disposal` 內 `rid, latest = next(reversed(groups.items()))`)。

## [S4] 逃逸的當下就記

已讀,無 finding。`skills/lumos-code-loop/SKILL.md:31` 已有 escape 提醒句;`skills/lumos-design-loop/SKILL.md:39`(步驟 10)確實缺、補位置對。

引句:「紅燈的收尾訊息加一句:修完若可歸因到某次已放行的審查」([S4] 節)。

## [S5] 範圍刀

已讀,無 finding。每條限制都對應既有代碼裡確實存在的機制,沒發現自相矛盾或漏列。

引句:「不新開帳本(全部加在既有 canary 列與 gov --stats 上)、不回填舊卷證」([S5] 節)。

## 實務隱患

### F9
severity: minor
blocking: 否
判準:不擋;2026-10-08 REVISIT 明講是「人工對」而非機械指令,符合專案既有慣例不算缺陷;但 2026-11-08 那條(refuted-set 填寫率)是現成結構化欄位、跟 `_render_gov_stats` 既有「辯方表態分布」段同構,理應直接進 [S3] 新段而非等兩個月人工查。

佐證:引句「REVISIT:2026-10-08 拿一個月的席報告抽 20 份人工對一次自動數」(實務隱患節)。file: `scripts/lumos:4345`(`_render_gov_stats` 既有同構前例)。

## PRIOR-ART

已讀,無 finding。借用既有記帳原語與世界既有量測概念對應清楚,borrow-design 站得住。

引句:「PRIOR-ART: 世界=code review analytics 的」。

## 牽連節點合約檢查(圖譜鏡頭)

### F10
severity: minor
blocking: 否
判準:不擋;`_loop_status_disposal` 現有觀測尾巴(roster/severity)都用 `if not readonly:` 包住,呼應該節點「回放唯讀…無觀測尾巴」的約定,[S3] 新讀側行沒提到要不要比照,實作者字面加在既有 print 旁不會自動繼承;`loop replay --golden` 比對只吃 `result_out` 結構化字典不比對印出文字,故不影響邏輯漂移判定,傷害僅止於 replay 模式多印噪音。

佐證:file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:39`(摘要 KEY「回放唯讀(治理帳零寫入、無觀測尾巴)」)、`scripts/lumos`(`_loop_status_disposal` 內 `if not readonly: _roster_tail(); _severity_tail()`)。

另查 `docs/lumos-toolchain-knowledge/Issues/流程自產工作量未量測.md`:已讀,無 finding。該節點 `--finding-kind` 要求全集對得上 `findings_set`,[S2] 的 `--refuted-set` 明文與 `--findings-set` 不重疊,兩集合互斥不衝突。

file: `docs/lumos-toolchain-knowledge/Issues/流程自產工作量未量測.md:18`。

---

## 總結

最嚴重 severity:blocker(F2,[S1] 演算法對今天寫側硬擋生效後的現行報告仍 6/8 undercount 到 0 或接近 0,可重現、非邊緣案例;F1/F3 為另外兩條 major 級系統性問題)。blocking 條數:5(F1、F2、F3、F4、F6)。
