---
type: issue
status: open
created: 2026-10-01
updated: 2026-10-01
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  PITFALL:[2026-10-01 殺傷力配方修補體驗代碼審第 1 輪通才席實跑,改動前的版本就重現]Python 專案上,`lumos guard kill` 在同一個隔離工作樹裡一條接一條套壞法、跑測試、還原;前一條壞法改完的檔跟這一條大小一樣、又落在同一秒內時,Python 沿用前一條留下的 `__pycache__` 編譯快取,這一條實際跑的是前一條的壞法。結果:一條根本沒傷害的壞法單獨跑判 survived、回 1;前面先放一條會讓測試紅的,它就變成 killed、整體回 0——★假的「合約有守住」★。重現:同一篇兩條配方指同一支 .py,第一條壞法讓測試紅、第二條壞法無害且改完檔案大小跟第一條相同,跑 `lumos guard kill <節點>`
  REVISIT:2026-11-01 guard kill 跑測試前設 `PYTHONDONTWRITEBYTECODE=1`,或每條還原後清掉工作樹裡的 `__pycache__`;補一條照上面重現的測試(第二條要判 survived)
---
# guard kill在Python專案會沿用編譯快取誤判殺得掉

白話:殺傷力驗證是「故意把程式改壞,看綁定的測試會不會紅」。Python 會把編譯結果快取起來,判斷要不要重編只看檔案大小與修改時間(到秒);同一秒內兩次改出一樣大小的檔,第二次就拿到第一次的快取。所以第二條配方其實沒被真的測到,卻沾了第一條的光被判成殺得掉。這比判錯成殺不掉更糟:它讓人以為合約有守住。來源 [[Projects/殺傷力配方修補體驗_計劃]] 代碼審(範圍外,沒修),程式說明在 [[Systems/guard-kill]];排進 [[Projects/漂移防治路線圖_計劃]]。
