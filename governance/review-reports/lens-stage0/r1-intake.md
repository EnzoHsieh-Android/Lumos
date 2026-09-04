preflight-4: ran

# r1 前置留痕(lens-stage0,code-loop high)

diff=Lumos/main..HEAD(單 commit a39741a):impact-hook 兩處修正+測試、recount.py+README+第一份報表、三篇筆記。pitfalls tier=high(命中 impact-hook.py:93 檔案 handle 一問)。
機械排乾:全套測試 3515 綠(pre-push 跑過);refcheck/lint/doctor 綠。前掃=pitfalls 的架構對齊對照檔(dispatch-lens-hook/ci-status-hook/lumos-entry-hook)。
★派工詞每席帶 `LUMOS-IMPACT: Lumos/main..HEAD`,固定席由 hook 機器附——第一次真實採用;收貨時看席報告有沒有引到「lumos 自動附加」段。★

## 收貨三道(六席)
| 席 | 條數 | 最高 | blocking | quote | refcheck | 鏡頭有用上? |
|---|---|---|---|---|---|---|
| s1 正確性 | 5 | major | 2 | 全錨 | 8/8 | 是(7 篇逐條判) |
| s2 併發資源 | 1 | major | 0 | 全錨 | 1 ok/2 missing(將建) | 是(8 篇逐條判) |
| s3 邊界輸入 | 9 | major | 2 | 全錨 | 11/11 | 是 |
| s4 合約圖譜 | 3 | minor | 0 | 全錨 | 9/9 | 是(13 篇+70 支綁定測試實跑) |
| s5 通才 | 6 | major | 0 | 全錨 | 11/11 | 是 |
| arch 架構對齊 | 4 | major | 2 | 全錨 | 25 ok/2 missing | 報告未提固定席(派工詞未要求) |
合計 28(5+1+9+3+6+4)/blocking 4/major 11——逐檔 grep 數的。★dispatch-lens 第一次真實採用:5/5 主席報告開頭有「固定席逐條判」段★。

## 處置
28 條全折(code 迴圈輪內有 major,accepted 必空):recount 沿用 check-graph-sync 切詞與圖譜定位(arch f1/f2)、重導向偵測(s1-f1/s3-f2)、write_text 就近判(s1-f2)、sed -i 算寫(s3-f1)、stem 撞名→ambiguous(s1-f3/s5)、壞檔跳過(s1-f5)、TTL 先寫後撤(s1-f4/s2-f1)、main 接線測試(s5-f2)、recount 測試(s5-f1/f4)、REVISIT 獨立行(s5-f4)、PIN_LINE 含空白/normpath/heredoc 判定/引號片語(s3 minors)、128 bytes 視窗(s3 minor:保留,128 足夠 `#!/usr/bin/env python3`,列界線)。修正 commit 6bcd0d5;報表數字更正。
