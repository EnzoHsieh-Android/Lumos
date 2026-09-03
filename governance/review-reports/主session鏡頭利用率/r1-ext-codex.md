### f1

severity: blocker  
blocking: 是  
引句:「同一回合裡、那次 Edit 之前,session 對 P 裡任一節點做過」  
file: `governance/review-reports/主session鏡頭利用率/r1-snapshot.md:44`  
`impact-hook` 是該次 Edit 的 PreToolUse，直到 Edit 已被提出才計算並注入 P；session 不可能在同一次 Edit 執行前收到 P 後再另做 Read/context，因此字面定義量不到它聲稱的因果行為。`additionalContext` 正是在 hook 輸出階段才產生，見 `scripts/hooks/claude/impact-hook.py:384-391`、`scripts/hooks/claude/impact-hook.py:419-430`。

### f2

severity: major  
blocking: 是  
引句:「既有 `extract_bash_file_paths` 已能從 Bash 指令抽檔案路徑」  
file: `governance/review-reports/主session鏡頭利用率/r1-snapshot.md:52`  
現函式只接受 `rm/mv/cp/git rm/git mv`，遇到 spec 指定的 `cat`、`sed`、`grep` 全部跳過；直接沿用會把主要閱讀途徑量成未碰。佐證見 `scripts/hooks/claude/check-graph-sync.py:218-264`。

### f3

severity: major  
blocking: 是  
引句:「收工時把本回合 pushed 事件對上「Edit 之前的 Read/Bash 路徑/context/show」」  
file: `governance/review-reports/主session鏡頭利用率/r1-snapshot.md:58`  
`collect_turn_actions` 把 Edit 路徑與 Bash 指令拆成兩份清單，沒有保留事件次序；現有 usage-log 的 context/show 又只有秒級 `ts,node,cmd`，沒有 `session_id`，故無法可靠判定同 session、本回合及 Edit 前後。佐證見 `scripts/hooks/claude/check-graph-sync.py:107-146`、`scripts/lumos:7382-7392`。

### f4

severity: major  
blocking: 是  
引句:「每次 commit 帶著走;append-only 行級合併,多機合併不衝突」  
file: `governance/review-reports/主session鏡頭利用率/r1-snapshot.md:53`  
被追蹤不等於每次 commit 自動納入：pre-commit 只讀 staged 名單，而 `.usage-log.jsonl` 本身不是 code 或圖譜 `.md`，未 stage 時會留在工作樹；不同分支同時在檔尾追加也沒有「不衝突」保證。佐證見 `scripts/hooks/pre-commit:36-40`、`scripts/hooks/pre-commit:140-154`。

### f5

severity: major  
blocking: 是  
引句:「commit message 帶一行「鏡頭確認」」  
file: `governance/review-reports/主session鏡頭利用率/r1-snapshot.md:64`  
spec 指定由 pre-commit 提醒並統計，但該 hook 沒有 commit-message 檔案參數，現況只取得 staged diff；照字面落在 pre-commit 無法可靠讀到待提交訊息，應是 commit-msg 類攔截點。佐證見 `scripts/hooks/pre-commit:1-22`、`scripts/hooks/pre-commit:36-40`。

### f6

severity: major  
blocking: 是  
引句:「命中率 ≥50% → 鏡頭已在被用,第二段不做;<20% → 推到眼前幾乎無效」  
file: `governance/review-reports/主session鏡頭利用率/r1-snapshot.md:60`  
此裁定把缺 session/順序而可能串錯的事件直接彙成命中率，且只用「推送次數 ≥30」控制樣本，沒有處理同 session、同檔及同節點重複觀測的相依性；即使累積 30 次，也可能由一個長 session 重複產生而導出錯裁定。樣本門檻見 `governance/review-reports/主session鏡頭利用率/r1-snapshot.md:74`，TTL 允許同 session 同檔反覆注入見 `scripts/hooks/claude/impact-hook.py:127-171`。

## 已讀，無 finding

- 「現況」中 usage-log 目前為 371 筆、僅含 context/show 的宣稱。
- impact-hook 的 code 副檔名、排除路徑、預設 20 分鐘 TTL 與 fail-open 描述。
- 「誠實界線」中不量理解程度、跨回合早讀造成假陰性的承認。
- 鄰居計劃對 hook 分工與固定席裁定的描述。

最高 severity：blocker；blocking 6 條。
