severity: major

D1
severity: major
blocking: 是
引句:「換行也是殼層的指令分隔,先逐行(代碼審 r1 外家 C6)。」
file: `governance/eval/lens-utilization/recount.py:873`
`_search_segments` 修法先把整條指令按真實 `\n` 切成物理行、再逐行找 `lumos search`,但沒有處理 shell 的反斜線續行(`\` + 換行=同一條邏輯指令)。實測餵入 `lumos search \\\n  "作廢 收回"`(agent 常見的多行折斷寫法)只回傳 `[['\\']]`,查詢字串完全消失、只剩一個反斜線;把它接上真實的零命中輸出「(共 0 篇候選,照相關性排序)」,`_search_event` 仍判定 `verdict: zero`,把 `query: "\\"` 這種垃圾字串寫進 S3 明訂要交付的「零命中查詢字串清單」。這是本輪修正(把 C6 的「兩個查詢被黏成一段」修好)過程中新引入的反向錯誤,171 支 lens 相關測試目前全線 PASS 但沒有任何一條覆蓋續行輸入,作者沒看到。

圖譜鏡頭(前 8 篇):design-loop.md / bound-tests-gate.md / canary-audit.md / guard-kill.md / lumos-cli-lifecycle.md / slim-get-一行安裝.md / slim-install-安裝器.md / canary-record未落盤事件.md 這 8 篇分別涉及設計審處置閘、綁定測試機械跑法、canary 落盤與 second telemetry、guard kill rc 優先序、CLAUDE.md 冪等注入、slim 安裝器的 BOM/manifest/攔截守衛——本次改動只動 `recount.py`/`lens_weekly.py`/`autonomous-loop.sh` 的唯讀量測邏輯與對應測試,不寫任何治理帳、不碰 `scripts/lumos` 本體(只讀取借用)、不動 CLAUDE.md 注入或 slim 安裝流程,8 篇 INVARIANT 宣稱的行為都不在改動路徑上,判不影響。

全份最高嚴重度是 major,blocking 共 1 條。
