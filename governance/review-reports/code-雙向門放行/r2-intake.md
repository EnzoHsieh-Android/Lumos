# r2 收貨(2026-09-17)

複核:r1 四條(F1/F2/A1/E2)通才席逐一重現後確認關上。

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| F1 | 單reviewer-r2-sonnet | major | HIT:正文圍欄裡 [[Systems/Risky]] 被當真連結,合格雙向門判成單向門 | 折:正文連結只看可見行並剝行內程式碼(S26) |
| A2 | 架構對齊-r2-sonnet | major | HIT:push-check 自掃 about_code,既有 _impact_home_map 有 status 過濾與 _nodehome_key 正規化(讀碼即見;席位四句引句引自 patch 外既有碼,錨不到,由編排者機械重現) | 折:改呼叫 _impact_home_map |
