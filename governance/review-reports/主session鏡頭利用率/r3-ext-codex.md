### f1

severity: major
blocking: 是
引句:「錨點=toolUseID 對到的那次 Edit tool_use 的行序」  
file: `governance/review-reports/主session鏡頭利用率/r3-snapshot.md:78`  
樣本宣稱的 44 次明確「含 Write」，但演算法只准對到 Edit；照字面實作會讓 Write 注入找不到錨點，卻仍拿含 Write 的 44 判斷是否達到 20 筆，可能錯裁「樣本夠」。

### f2

severity: minor
blocking: 否
引句:「子代理推送與主 session 分開報(60% 推送在子代理)」  
file: `governance/review-reports/主session鏡頭利用率/r3-snapshot.md:118`  
本 repo 附件重數是主 44、子 0，且 spec 自己說全機 42 筆子代理結果在本專案無法重現；因此「60% 推送在子代理」與目前限定範圍的逐字稿現況不符。

最高 severity：major；blocking 1 條。
