# 席報告對帳原因更正

本篇更正兩本已封存 intake 的原因判斷，原始報告、派工單、canary 綁定的 intake 與凍結判定都不改。

- code-source-coordinates/r1-intake 把 WHY 引句列入 out_of_scope 解釋成文字被當材料路徑，這句不正確。實際 cmd_seat_check 只對頂層 materials 的內容錨引句，原多席派工單頂層只有兩支源碼，漏掉每席已宣告的 source/graph patch；WHY句本來就在實際凍結graph patch裡。衍生每席視圖使用原 seats 欄位重驗，兩席 out_of_scope 皆空。
- source-coordinates/r1-intake 把 resources 舊句出界解釋成抽取誤報，這句也不正確。原 materials 含活的計劃，折入後舊句已改；派審時的 r1-snapshot 有原句但未列入 materials。視圖補明已供應的不可變 snapshot，重驗 unreported/out_of_scope 皆空。
- unreported 是「報告沒有列材料路徑／檔名」的觀測，不等於已證實沒讀，也不是應直接改工具消掉的誤報。正確性仍缺測試檔與圖譜鏡頭檔名，架構仍缺鏡頭檔名。raw 報告與工具輸出都保留；未以更正原因假稱剩餘提醒通過。
- 這是呼叫材料視圖與封存版本選擇的操作校正，不是引用驗證器缺陷；不增加新 gate、不重開同一設計迴圈、不用改原報告補名掩蓋。下一案派工與收貨採單席材料視圖，明列實際凍結patch/snapshot，派工輸出要求把材料檔名逐項列出。

機械指令與結果：本目錄 command.txt、results.json。全部使用既有 seat-check，沒有更改產品碼或工具返回碼。原始首輪處置仍是設計真資源問題一条折入、編譯误判一条反证；代碼審非阻擋 WHY 欄位一条折入。
