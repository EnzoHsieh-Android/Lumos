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
  PITFALL:[2026-10-02 代碼審修正關卡設計審 r2 正確性席]`_ran_count` 只要輸出裡出現 `1 skipped` 這類字樣就判「有跳過」,失敗訊息或測試自己印的字剛好含這串時,規格閘與修正關卡會把一支真的跑了的測試判成弱證據(失敗方向是擋,不是放水)。重現:讓一支 python 測試失敗時印出「1 skipped」,用 `lumos spec-gate` 跑綁它的條款
  REVISIT:2026-11-01 改成只讀測試工具的摘要行(pytest 的最後一行、自家 runner 的「N passed, M failed」那行)判跳過,補一條重現測試
---
# 測試支數把失敗訊息裡的skipped字樣當跳過

白話:判斷「這支測試是不是被跳過」的那段,只要在輸出裡看到某串字就算數,不管那串字是不是測試工具自己的摘要。規格閘([[Systems/規格閘]])與修正關卡([[Systems/代碼審修正關卡]])共用這段。來源 [[Projects/代碼審修正關卡第0步_計劃]]〈範圍〉不做。
