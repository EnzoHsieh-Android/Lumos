# code-android-e2e-batch1 r3 收貨

- 修訂輪(標準分級的第 3 輪,也就是上限):修前 73f36793 → 修後 aba0d9cd(r3-repair.patch、r3-repair-binding.json、r3-behavior-cases.json)。兩席都是沒參與過的新代理,派工詞寫明不讀 r1、r2 的席報告與作者因果結論。
- 單審席報告最後一行原寫「max severity: …」被機器當成等級宣告,退回該席自己改措辭,內容沒動;重交後引句全錨。架構對齊席判 clean,沒有發現、也就沒有引句。
- 單審席在自己的 clone 裡跑修前版本留下一份測試暫存(16:12),由編排者確認沒有程序開著後刪掉。
- 編號:s 單審,後接報告裡的條號;架構對齊席 0 條。
- 修正提交:8eea52f7(修正前 aba0d9cd)。

## 修補因果

| id | 歸因 | 依據 |
|---|---|---|
| s1 | 上一輪修補造成 | 席位兩版同一案例:修前 73f36793 rc0 有寫紀錄、修後 aba0d9cd rc1 UnicodeEncodeError 沒寫;r2 為了保住換行把紀錄讀回的清洗整個關掉 |
| s2 | 上一輪修補造成 | 席位兩版同一輸入結果相反:修前兩條讀法都拒收 BOM、修後 _e2e_config_at 收;r2 改走 _lumos_config_at_ref |
| s3 | 上一輪修補造成(文件) | r2 改了 kill_group 的行為,說明沒跟上 |

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| s1 | 紀錄裡有孤立代理字元時 judge 寫回崩潰、回 1、沒寫紀錄 | 先補測試:紀錄的放行理由加一筆含孤立代理字元的,再跑 judge;修前 rc1、UnicodeEncodeError(紅) | HIT | 折(紀錄讀回只把孤立代理字元換成 U+FFFD,其他照原樣;改壞驗證拿掉會紅) |
| s2 | 讀提交裡的設定收 BOM,讀工作目錄那份不收 | 讀 `_json_at_ref`:對內容做 lstrip BOM;讀 `_macrobench_config`:read_text 後 json.loads | HIT | 折(說明寫明這個差異:帶 BOM 的設定在 macrobench --check-config 就擋下、範本開跑前一定先過那一道;下一批的推送檢查那一道要自己再擋一次) |
| s3 | kill_group 說明與範本檔頭還寫「還在才 KILL」 | 讀兩處說明 | HIT | 折(兩處改成寬限結束一律對整組補 KILL) |

修補對照:修正提交 8eea52f7 的差異就是修改前→後。
