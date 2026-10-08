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
  PITFALL:[2026-10-01 殺傷力配方失配提醒代碼審第 2 輪邊界席順帶回報,編排者重現]`.lumos/config.json` 是合法 JSON、但最外層不是物件(例:`[1,2]`)時,`lumos doctor` 讀符號設定那一步(load_symbol_profile 對它呼叫 .get)丟 AttributeError、整支崩潰,走不到後面各段。重現:空 git repo 放一篇 MOC、設定檔寫 `[1,2]`,跑 `lumos --vault <vault> doctor`
  REVISIT:2026-11-01 讀設定的幾個入口(load_symbol_profile 等)遇到最外層不是物件時,改成印一句「設定檔最外層要是物件」並當成沒有設定,不讓 doctor 崩潰;修完補一條重現測試
---
# 設定檔最外層不是物件時doctor在符號設定段崩潰

白話:設定檔整份寫成清單(而不是「名稱:值」的物件)時,健康檢查會在很前面就當掉。這跟 [[Issues/設定內容讓load_platforms丟例外時doctor整支崩潰]] 是同一族(設定寫錯讓 doctor 整支崩潰),但崩在另一個入口;那篇修的是 Check T,這一處沒修。殺傷力配方失配提醒的新段落自己接得住(先自己判最外層是不是物件),見 [[Projects/殺傷力配方失配提醒_計劃]]〈實作紀錄〉。
