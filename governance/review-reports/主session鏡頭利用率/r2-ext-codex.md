## 第 1 輪六條驗收

r1-f1: 已解——時間窗已改為「推送 ts 之後、到回合結束」，不再要求同一次 Edit 前讀取剛注入的內容。  
r1-f2: 已解——明定另寫 `collect_turn_touches`，不再沿用不支援 cat/sed/grep 的 `extract_bash_file_paths`。  
r1-f3: 已解——改從同一份逐字稿取得 UTC 時戳、有序 tool_use 與 session，足以判定推送前後。  
r1-f4: 已解——改用 gitignored 的獨立 `.lens-log.jsonl`，不再宣稱「被追蹤即每次 commit 自動納入」或跨分支不衝突。  
r1-f5: 已解——第二段明定攔截點是 `commit-msg`，並明說 pre-commit 拿不到訊息檔。  
r1-f6: 已解——取消命中率及數字成效門檻，改報逐筆分佈、session 數並人工抽樣判讀。

## 重寫版 findings

### f1

severity: major  
blocking: 是  
引句:「payload 拿 `session_id`+`transcript_path`,subprocess `lumos lens tally`」  
file: `governance/review-reports/主session鏡頭利用率/r2-snapshot.md:73`  
`SubagentStop` 雖確實存在，但 `transcript_path` 是主 session 逐字稿，子代理自己的檔案在 `agent_transcript_path`；照 spec 傳前者會拿主 session 動作替子代理對帳，主／子分佈與 touched 結果都會錯。[Claude Code 官方 hook 文件](https://code.claude.com/docs/en/hooks)

### f2

severity: major  
blocking: 是  
引句:「放在任何判斷之前、不與 check-graph-sync 合體」  
file: `governance/review-reports/主session鏡頭利用率/r2-snapshot.md:73`  
第一次 Stop 先寫 tally 後，既有 `check-graph-sync` 可以擋停並令模型繼續，下一次 Stop 會對相同 user turn 與 push 再寫一次；spec 沒有 push ID、upsert 或已 tally 去重規則，分佈會把同一推送重複計數。

### f3

severity: major  
blocking: 是  
引句:「每次真的注入時,把推送事件一列一次寫下」  
file: `governance/review-reports/主session鏡頭利用率/r2-snapshot.md:71`  
`inject_ranked_context` 在 pinned 為空、但 top-8 自由席或 lane 非空時仍會真的注入；若照字面記成 pinned 空集合的推送，它必然得到 `any:false`，會把「沒有固定席可碰」量成「固定席被忽略」。現行輸出條件見 `scripts/hooks/claude/impact-hook.py:384`。

### f4

severity: major  
blocking: 是  
引句:「回滾:移除兩支 hook 登記+兩個子命令+帳檔」  
file: `governance/review-reports/主session鏡頭利用率/r2-snapshot.md:111`  
本案只新增 `lens-tally-hook.py`，`impact-hook.py` 是現役既有注入 hook；照此回滾移除兩支登記，會連原有 impact 鏡頭一起停用。現役登記可見 `scripts/lumos:11017`。

## 已讀，無 finding

- 逐字稿抽驗：`timestamp` 為 UTC `Z` 格式，tool_use 依 JSONL 行序保存。
- `hook_decide` 的無副檔名漏樣宣稱，與 `scripts/hooks/claude/impact-hook.py:84` 現況相符。
- `inject_ranked_context` 的實際輸出位置與空集合判斷。
- `cmd_gov` 現有七源及新增第八源的同步方向。
- `_BOOKKEEPING_FILES` 加入新帳的要求。
- `dispatch-lens-hook.py` 所代表的薄殼加 lumos 子命令形態。
- 本機 `~/.claude/settings.json` 尚未註冊 SubagentStop；這不否定事件存在，官方文件已確認事件及 payload。
- 樣本數不足即改題的規則本身不再用命中率導出自動成效裁定。

最高 severity：major；blocking 4 條。
