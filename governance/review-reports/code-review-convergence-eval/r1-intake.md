# 首輪收貨與修補

所有八席報告收齊後才改工作目錄。報告原文保留；資源誤報判定與資源席fd實驗衝突，以實際64fd重現折入，不改席報告。各席有未執行項，不把沙箱拒絕當產品失敗。

| ID | 機械重現與處置 |
|---|---|
| smoke | HIT 保存225/11/152但同SHA輸出224/10/151；重產且釘collector、固定歷史來源commit |
| suboutcomes | HIT repair及preserve反向卻同摘要；補分項統計 |
| costcoverage | HIT 缺場及重複slot仍給cost均值；排定分母完整才給均值 |
| globaltoken | HIT 跨loop同token沒衝突；先全帳核對 |
| roundorder | HIT r1,r2,r1給已知輪數；保留未知及異常旗標 |
| costscalar | HIT bool/負數/字串等成本仍有效；拒收並留原因 |
| nulpath | HIT NUL路徑ValueError終止比較；變成單筆invalid |
| unicodeinput | HIT surrogate讓UTF-8 encode崩潰；拒收資料錯誤 |
| fd | HIT 80次讀目錄耗盡64fd；未移轉所有權時確保close |
| limits | HIT 舊1000題百次有效但檔案超限；收緊為100題20次、128字元標識、manifest1MiB，符合初期離線批次範圍 |
| caseindex | HIT 驗證逐筆掃千題；預建case字典及只留統計所需欄位 |
| moc | HIT S6漏項；評測索引加入新Systems |
| pitfall | HIT 測試塞出處括號，lint警告；拆獨立test欄 |
| unicodeoutput | HIT 原始CLI輸出控制符；跳脫且往返資料相同 |
| capability | HIT 常數不存在時AttributeError；旗標採與既有O_NOFOLLOW相同的能力預設寫法 |
| rootanchor | HIT 根相對path不是is_absolute；通用anchor拒絕所有有根或磁碟的參照，不另做Windows驗證 |
| tension | HIT py-memory hint要求記張力；改記bounded parser採用原因及既有對照 |

新20個unit反例在修前有4個failure與4個error；修後20/20通過，正式runner4/4。既有12個保留候選仍綠。Unicode顯示另改為真正CLI往返測試，原件before.log保留其首次結果，不改造成更強證據。

治理帳有10:11:19 bound-tests與10:11:22 blocked兩筆；整合席宣稱由doctor觸發，編排者也有同時在跑的precheck。歸因未判定，保留append-only原帳，不依報告刪事件。Windows完整相容性依使用者指示不在本輪驗證範圍。
