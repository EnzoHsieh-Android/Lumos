severity: major

驗收
#1 通過:輪次改以最後一句人話為邊界，尾端提醒與中途通知後的動作均有斷言。scripts/test_lumos.py:30592
#2 通過:候選會排除本 session、優先選取提及計劃者、列出候選並支援明確指定。scripts/lumos:19983
#3 通過:逐字稿解析已有最外層例外兜底，異常形狀回不可得而非 traceback。scripts/lumos:20115
#4 通過:反引號路徑可承載空白及非 ASCII，並有實際 git 狀態測試。scripts/test_lumos.py:30563
#5 未通過:仍會執行可變 hook，而測試只檢查輸出及 tmp 留檔，無法鎖住啟程序、網路、讀取資料或寫入 tmp 外路徑，與「不產生任何外部動作」不符。scripts/test_lumos.py:30724

總結:前四條已折實；第五條只加了不完整的副作用偵測，原本的可變 hook 執行風險仍在；未發現其他 blocking 級問題。實際開過 governance/review-reports/接手視圖/r1-外家codex.md、governance/review-reports/接手視圖/r1-intake.md、governance/review-reports/接手視圖/r2-snapshot.diff、docs/lumos-toolchain-knowledge/Projects/接手視圖_計劃.md、scripts/lumos、scripts/test_lumos.py、scripts/hooks/claude/check-graph-sync.py、/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md。
