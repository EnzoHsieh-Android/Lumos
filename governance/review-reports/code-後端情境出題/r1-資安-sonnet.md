severity: minor

審查範圍:程式部分(`scripts/lumos` 的待決問題規則與 `--stage`、`scripts/scenario_probe.py`、`qo_ablation.py`、測試檔、skills)加上全部檔名清單。沒有找到可直接利用的洞,也沒有真實密鑰外露。以下是縱深防禦類。

逐類結論:
1. 不可信輸入流到危險操作。
   - 已看,無。待決問題的正規式(`_PQ_*`)是寫死的,只拿計劃筆記文字當被比對的資料,筆記內容不會變成程式碼或指令。
   - `_pq_decision_state` 只用 `env.resolve` 和 dict 查表,沒有路徑拼接。
   - `qo_ablation.py` 呼叫子程序都是 list 形式,沒有 `shell=True`,也沒有 eval 或 pickle。
   - `mask_leaks` 只是字串替換。
2. 登入與權限:無相關。
3. 密鑰與個資。
   - 我掃了 `governance/eval/qo-ablation-2026-10/` 和 `governance/eval/mcp-lab-2026-10-12/`。沒有 token、私鑰或帶密碼的連線字串。
   - `compose.yaml` 和 `init.sql.txt` 的密碼已換成佔位字,埠只綁 127.0.0.1。
   - 受測 AI 起的 `orders/orders` 是示範用假帳密,依規則不報。
   - 本機絕對路徑外洩見下面第 2 條。
4. 加密與傳輸:無相關。
5. 執行邊界:見下面第 1 條。對全域設定,我只看到一個動作:`qo_ablation.py` 讀 `~/.codex/config.toml` 算雜湊,是唯讀。診斷用的 `~/.claude/skills` 檢查也只讀。
6. 行動端:無相關。

依賴:本次沒有新增依賴清單。MCP 實驗筆記用 npx、uvx 臨時執行,`compose.yaml` 用 `grafana/grafana:latest`。這些只是實驗紀錄,沒有進入任何執行路徑,所以不單獨列為發現。

severity: minor
blocking: 否
引句:「            cmd += ["--codex-bypass-hook-trust"]」
`qo_ablation.py` 的 `cmd_run` 在 codex 模式下無條件加上 `--codex-bypass-hook-trust`,最後變成 `--dangerously-bypass-hook-trust`。攻擊路徑(推論):誰,是提供受測 repo 的人;從哪裡,是 `--arm-a` 或 `--arm-b` 指到的 repo,像是第三方 clone 或別人 PR 的內容;送什麼,是 `.codex` 底下的 hook;拿到什麼,是跑實驗的人在主機上的任意指令執行,可讀到 `CODEX_HOME` 的登入憑證。實際上兩個 repo 都由操作者自備,而且 `scenario_probe.py` 的註解已寫明這旗標「只准隔離環境」,但呼叫端沒有隔離檢查。縱深防禦的做法是改成需要明確的 opt-in 旗標,或確認 arm 路徑在 `/tmp` 的專用複本之下。

severity: minor
blocking: 否
引句:「docker run -d --name order-pg -e POSTGRES_USER=orders -e POSTGRES_PASSWORD=orders -e POSTGRES_DB=orders -p 55432:5432」
受測 AI 帶著不受限的 `Bash` 工具(claude 加 `acceptEdits`、codex 用 `workspace-write`),沙盒只隔離檔案。這條證據來自卷證 `results-aborted/claude-noplugin/a/qo-P1-r1.json`:受測 AI 真的在主機起了 Docker 容器,並把埠發布到所有網卡,密碼是 `orders`。攻擊路徑(推論):誰,是改 `scenarios.jsonl` 的人;從哪裡,是別人 PR 裡的題目 prompt 或受測 repo 的 CLAUDE.md;送什麼,是要 AI 執行的指令;拿到什麼,是 AI 以操作者身分在主機上跑任意 shell(`env` 全量繼承、可讀 `~`、可連網)。這是儀器的固有性質,不是這次新增的洞。建議在 README 或 skill 寫明「題目和受測 repo 必須是自己審過的」,並考慮把 `scenarios.jsonl` 納入跑之前的雜湊釘住。

severity: minor
blocking: 否
引句:「cat /Users/enzo/.claude/skills/lumos-project-notes/commands/INDEX.md」
這次 diff 新增了 64 行含 `/Users/enzo/...` 的內容:`codex-review-v1.md` 23 行、`v2.md` 17 行、`v3.md` 4 行、`results-aborted/codex-subject/a/qo-P1-r1.json` 15 行、`results-aborted/claude-noplugin/a/qo-P1-r1.json` 3 行、`rating/codex-rater-raw.txt` 1 行、`review-reports/…/r2-回滾整合-sonnet.md` 1 行。攻擊路徑:誰,是任何人;從哪裡,是公開 repo 的歷史;送什麼,不用送,直接讀;拿到什麼,是本機使用者名稱和目錄結構,可用於社交工程或猜測路徑。沒有憑證,所以只算縱深防禦。可以在存檔前把 `$HOME` 換成 `~`,與 `mask_leaks` 在盲評包裡的做法一致。

總結:最嚴重 minor;blocking 共 0 條
