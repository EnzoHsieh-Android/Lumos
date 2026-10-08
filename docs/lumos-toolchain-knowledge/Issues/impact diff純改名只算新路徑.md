---
type: issue
status: open
created: 2026-10-02
updated: 2026-10-02
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  PITFALL:[2026-10-02 代碼審修正關卡第0步設計審 r1 邊界席實測]`lumos impact --diff` 取改動檔用 git 預設的改名偵測,純改名的檔只列新路徑——寫著舊路徑的合約節點牽連不到,推送前合約測試閘與修正關卡第 5 項都會漏跑那些合約測試(實測:改一行時牽連 26 篇,純改名後 0 篇)。重現:把一支被合約節點用反引號寫到的程式檔 `git mv` 改名、提交,跑 `lumos impact --diff HEAD~1..HEAD --json` 看 pinned
  REVISIT:2026-11-01 在 cmd_impact_diff 取檔清單時加 --no-renames(舊路徑也算改到),補一條純改名的重現測試;修正關卡第 5 項的「改名只提醒」那段同時拿掉
---
# impact diff純改名只算新路徑

白話:改程式檔的名字時,寫著舊檔名的合約筆記會被當成沒受影響,它綁的測試就不會在推送前被跑到。修正關卡目前只印一行提醒(見 [[Systems/代碼審修正關卡]]),推送前那道閘([[Systems/bound-tests-gate]])沒有任何提醒。來源 [[Projects/代碼審修正關卡第0步_計劃]]〈實務隱患〉。
