# r1 收貨紀錄(code-筆記內容審)

凍結材料:r1-snapshot.patch(2686 行,超過 1800,拆成 r1-snapshot-a.patch 主程式與範本 1528 行、r1-snapshot-b.patch 測試筆記文件 1158 行分席看;架構對齊席看整份);分級 standard(pitfalls:有程式檔改動、沒命中風險型樣),沒有要表態的效能檢核題。圖譜鏡頭:主工作目錄的 main 落後,派工 hook 附不上,改在 clone 手算 `lumos dispatch-lens` 存成 r1-lens.txt 貼進派工詞。

## 席位收貨

- 4 席全交(正確性A opus 看 a 半、測試文件B sonnet 看 b 半、架構對齊 sonnet 看整份、外家否決 Codex 看 a 半);等完成通知、ls 確認在,全交回才搬進卷證、才讀、才動工作目錄。
- report-normalize:測試文件B、架構對齊各有一行總結或說明句夾了嚴重度字樣,退回該席自己改那一行(措辭,不改宣告);其餘兩份已正規化。
- quote-check:正確性A、外家、架構對齊全錨定;測試文件B 乾淨報告沒有引句(0 條 finding)。
- 測試文件B 乾淨,但不是空泛交差:自己在臨時複本把三條規則改壞、確認對應測試會紅,文件逐條對過程式。

## 編排者重現(每條都寫成回歸測試 t_note_audit_code_review_r1_regressions,修前紅)

| 發現 | 重現 | 結果 |
|---|---|---|
| a3、x1 同編號多處只列第一處 | 回歸 ①:同小標題下兩行「理由同上」,清單只出現一次 | HIT(修前紅) |
| a1 已收尾計劃只改名被當收尾 | 回歸 ②:起點已 done、範圍只有 git mv | HIT(修前紅) |
| a2 CRLF 筆記清單指紋對不上 | 回歸 ③:CRLF 筆記全判脈絡,record 一行都收不下 | HIT(修前紅) |
| x2 範圍終點找不到就放行 | 回歸 ④:終點寫錯 rc0 | HIT(修前紅);淺層 clone 部分照第一層 S4 設計維持跳過+記帳,改由 doctor 唸 CI 沒抓完整歷史(回歸 ⑩) |
| x3 略過開關設 0 也略過 | 回歸 ⑤;第一層 LUMOS_SKIP_NOTE_SHAPE 同族 | HIT(修前紅) |
| a4 有空行的多行值只換一半 | 回歸 ⑥ | HIT(修前紅) |
| x5 清單欄被壓成一句 | 回歸 ⑥b | HIT(修前紅) |
| x4 還沒提交的改名繞過遠端比對 | 回歸 ⑥c | HIT(修前紅) |
| a7、x7 證據驗證太鬆 | 回歸 ⑦、⑦c | HIT(修前紅) |
| a8、x6 非 UTF-8 報告噴 traceback | 回歸 ⑧ | HIT(修前紅) |
| a5 設定不是物件沒提醒 | 回歸 ⑨ | HIT(修前紅) |
| a6 doctor 刪除次數讀本機、CI 提醒條件沒寫進規格 | 回歸 ⑩b;S16 措辭與實作紀錄已改 | HIT(修前紅) |
| g1 decision-amend 註冊位置離家族遠 | 讀碼:argparse 與說明表移到 decision-* 旁 | HIT |

- 16 條(合併重複後 13 件)全折(輪內有 major,不得放行);refuted 無。
- 同族掃:略過開關「有值就略過」全檔還有 LUMOS_SKIP_LINT_NEW 一處(新增告警閘),不在這次範圍,記在收尾報告。
