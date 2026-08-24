## f1 — blocker

spec 段落：§2 派工、PRIOR-ART、實務隱患「守衛面」

引句:「審計/複審 agent `--allowedTools "Read,Grep,Glob,Bash"`(沙盒內 Bash 自由,主樹零風險)」

問題：`make_sandbox` 並非可承載「Bash 自由」的安全容器。三層中只有移除 remote 是初始狀態；agent 可重新加入 remote，並以 `git push --no-verify` 跳過 pre-push hook。第三層假身分只提供事後辨識，完全不阻止推送。更嚴重的是，spec 明訂「認證 env 照 orchestrator」，現行 orchestrator 會把 `CLAUDE_CODE_OAUTH_TOKEN` 注入程序；`make_sandbox` 沒有網路、HOME、`gh`/`curl` 或憑證隔離。被引用的事故筆記也明載只能擋一般 git push、擋不了 `gh`/`curl`，spec 卻僅靠 prompt「明禁對外」便推導主樹零風險，正是散文守衛。現有測試也只測普通 `git push`，未測 `--no-verify` 或 API 出口。

查證：`scripts/scenario_probe.py:80-109`、`scripts/test_lumos.py:417-455`、`governance/autonomous-loop.sh:197-203`、`docs/lumos-toolchain-knowledge/Issues/探針沙盒能推到真遠端.md:37-49`

## f2 — blocker

spec 段落：§4 處置「PASS」

引句:「PASS → 蓋章 `auto-<model>` ★+commit★」

問題：回寫柵欄只放在「FAIL→修復→複審 PASS」路徑，直接 PASS 沒有任何快照比對。agent 審的是 `make_sandbox` 建立時的內容；若派工後主樹該篇被另一 session 修改，系統仍會替未被審過的新內容蓋 `auto-<model>` 並 commit。這不一定覆蓋人的文字，卻會產生更危險的假認證，直接破壞 self-audit 戳記語意。測試⑦只覆蓋修復回寫，沒有 PASS 派工後主樹變更的案例。

查證：`scripts/scenario_probe.py:94-109`、`scripts/lumos:7578-7593`、`docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:17-18,50-57`

## f3 — blocker

spec 段落：§4 回寫柵欄、實務隱患「併發」

引句:「copy 回主樹前比對「主樹該篇現況 sha256 == 派工快照 sha」——不等=主樹已變,放棄回寫」

問題：單次「比對後再 copy」仍有典型 TOCTOU 窗口：另一 session 可在 sha256 比對成功後、copy 前修改同檔，隨後被自動 copy 覆蓋；也可在 copy 後、蓋章或 commit 前修改，造成提交內容未經複審或混合。事故筆記明確指出同工作區沒有 session 維度，git、hook、doctor 都不會攔截；spec 沒有檔案鎖、compare-and-swap、原子 rename 前的再次比對，或以 index blob/pathspec 建立隔離 commit。測試⑦只在「派工後、柵欄前」改檔，無法讓「拿掉 check-copy 間原子性」翻紅。

查證：`docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:32-40,50-57`、`governance/autonomous-loop.sh:377-381`

## f4 — major

spec 段落：§4 週帳、測試⑩

引句:「配額只數 kind∈{done,fail,abort,stale}(=真派工),nag 不佔額」

問題：週帳 schema 只有終局 kind，沒有派工前的 durable reservation／started 記錄，也沒有 loop-level lock。程序若在 agent 已派出後、終局列 append 前中斷，帳上無法得知這次「真派工」，下次會再次消耗配額；兩個並行 session 也能同時讀到剩餘額、各自派工，突破 N=2。測試聲稱覆蓋「中斷補殘」，但憑 `{week,stem,kind,ts}` 終局帳本沒有足夠狀態可重建 crash 發生在派工前或後，因此該測試沒有可實作的 oracle。

查證：`governance/autonomous_loop/gap_select.py:25-38,59-70`、`governance/autonomous-loop.sh:139-166`、`docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:50-57`

## 已讀，無 finding

- §1 `_self_audit_lists` 與 Check S／`_graph_pagerank`
- §1 CLI 出口與 query 參數形狀：現行 `query` 無 positional，採旗標 AND 疊加；新增模式旗標仍須明訂與既有篩選旗標互斥，但目前不足以單獨升為 major
- 沙盒 rsync 未提交現況：`rsync` 全工作樹後 `git add -A`、commit，確實包含一般未提交及未追蹤現況
- 報告目錄隔離：同一沙盒在建立後刪 self-audit reports/pending，可隔離本輪 wrapper 落在主樹的報告；未發現另一個確定會把本輪 verdict 洩給複審的既有路徑
- `governance/pending/selfaudit/` 子目錄與 `gap_select`：現行只 glob pending 根層 `*.md`，子目錄不會連坐
- 成本：repo 約 172 MB，其中 `.git` 約 144 MB；每篇建立一份沙盒會造成相應短暫磁碟與 rsync 成本，但 N=2/週尚不足以否決

最嚴重 severity: blocker
