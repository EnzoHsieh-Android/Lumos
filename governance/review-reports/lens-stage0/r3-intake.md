preflight-4: ran

# r3 前置留痕(lens-stage0,上限輪)

只審 r2 修正 delta(310c8f3+補 1 筆);所有 lens/hook 測試綠。

## 收貨三道(六席,delta=310c8f3+cb02f42)
| 席 | 條數 | 最高 | blocking | quote | 鏡頭 |
|---|---|---|---|---|---|
| s1 正確性 | 4 | major | 3 | 全錨 | 是 |
| s2 併發資源 | 6(2 真+4 clean) | major | 0 | 全錨 | 是 |
| s3 邊界輸入 | 5 | blocker | 3 | 全錨 | 是 |
| s4 合約圖譜 | 6(5 clean+1 minor) | minor | 0 | 全錨 | 是 |
| s5 通才 | 3 | blocker | 2 | 全錨 | 是 |
| arch | 0 | clean | 0 | — | — |
合計 24 條/blocking 8/blocker 2(同一條:空標記檔 IndexError 讓現役 hook 當掉)。r2 修復驗收:六席皆真修。
## 處置(上限輪)
24 條全折(輪內有 major,accepted 必空):hook 接 IndexError(s3-f4/s5-f3 blocker)、token=None 不撤(s2-f2)、舊註解(s4-f6);★結構性折法★=recount 證據分兩層(高信心/啟發式),解析器殘餘不精確只落啟發式欄——回應 s1-f1..f3、s3-f1/f2/f3、s5-f1/f2 的「修法自己種新洞」形態;個別 bug 也修(1>/&>/>|、with open、重新賦值、先拆子殼再切段、切詞回空退回)。★上限到:r3 折入的 delta(30f2ac4)沒有第四輪;殘餘風險=啟發式欄的解析仍會有邊角誤差,已明標低信心;hook 側改動由 12 支測試+全套綠背書。★
