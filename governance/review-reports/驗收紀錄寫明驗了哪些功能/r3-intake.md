# 驗收紀錄寫明驗了哪些功能 r3 收貨紀錄(2026-10-03,4 席,末輪)

機械:四份 report-normalize 已正規;quote-check --spec r3-snapshot.md 四份全錨定;refcheck 四份全 ok。正確性席 F1 原寫 severity major / blocking 否(兩欄矛盾),退回該席重判為 major / 是,並由該席自己更正結論段措辭。

編號:c1–c6 = r3-正確性-opus.md F1–F6;b1–b4 = r3-邊界-sonnet.md F1–F4;i1–i7 = r3-整合-sonnet.md F1–F7;a1–a2 = r3-架構對齊-sonnet.md F1–F2。共 19 條,blocking 1(c1)。

| id | 怎麼試 | 結果 |
|---|---|---|
| c1 | 席位在假圖譜實測:現行 3/4 與 sync 抓得到建檔後正文補的功能;照設計自動寫 system_refs 後兩邊都不報 | HIT |
| c2 / a2 / b1 / i2 | 三席讀碼:build_typed_index 有空字串與空目標兩條靜默跳過,計劃只列四種不合格 | HIT(三席一致) |
| c3 | 推演:每項都寫壞時會多報「讀不出任何一項」 | 採信 |
| c4 / i5 | 讀碼:warn 的 issues += len(lines),封頂後計數對不上 | 採信 |
| c5 | 讀碼:doctor 判 verified_by 走 env.resolve 會退回檔名;計劃「一樣算壞連結」不實 | HIT |
| c6 / i7 | 推演:孤兒宣告全寫壞時推薦落回原本、理由字樣 | 採信 |
| a1 / i6 | 讀碼:其他讀 status 的地方仍分大小寫 | 採信 |
| b2 | 讀碼:鍵名打錯當沒宣告,lint 只提醒 | 採信 |
| b3 | 實驗:null、只有註解、多項行內清單的原因字樣 | 採信 |
| b4 | 實驗:裸名不分大小寫、路徑式分;./、反斜線 | 採信 |
| i1 | 讀碼:回傳要帶字面才能保住索引的去重 | 採信 |
| i3 | 讀碼:--systems 大小寫找回真實路徑 | 隨 c1 改法(不自動寫)消掉 |
| i4 | 編排者查 reference.md 798、950、987 行與 lumos-cli-write LIST_KEYS 計數 | 採信 |
| 驗收 | 正確性席原型:本 repo 與 rtb 索引一字不差、239 條連結全合格、rtb 7 篇都寫得出;整合席臨時副本 append 197、delguard 100、lands_in 10、new_verification 10 全綠 | 前兩輪修正成立 |

處置:19 條全折。c1 改成欄位只在作者主動寫時生效、建紀錄指令不自動寫。迴圈到上限,這輪折入沒有再派新席,交給實作後的代碼審。
