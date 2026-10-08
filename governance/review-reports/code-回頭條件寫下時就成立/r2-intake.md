# r2 收貨(code-回頭條件寫下時就成立)

收齊兩席(正確性-sonnet、架構對齊-sonnet)才動工作目錄;兩席都沒動 repo(git status 只多編排者自己的凍結材料與派工單,reflog 沒有新動作)。
兩份報告 report-normalize 不用改;quote-check 全數錨定(正確性 3/3、架構對齊 1/1);refcheck 正確性 4/4、架構對齊 2/2;seat-check vacuous。
這輪 hook 沒有接上(雲端環境沒裝派工鏡頭 hook),圖譜鏡頭的固定席由編排者先跑 `lumos dispatch-lens` 再把結果手貼進派工詞。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| F1 | 跑席位留的 /tmp/born-r2-work/e6.py(測試金鑰簽一個提交 S 寫下條件、下一個提交 P 讓條件成立;再設 log.showSignature=true 重跑 scan --json) | HIT:沒設時 born=S、state=false;設了之後 born=P、state=true(簽章提交被吃掉,把寫下時不成立的說成成立) |
| F2 | 讀 t_note_versions_stop_at_copy:①②③ 沒有「git 真的認成複製」的前提斷言,同檔 t_drift_born_identity ⑤ 有 | HIT:缺前提斷言 |
| Z1 | 讀 `_note_versions` 說明:寫「_note_status_seq 與 _drift_born_annotate 共用」,實際呼叫端是 `_DriftBornHistory._text` | HIT |

## 依根因分組

- 甲「git 輸出被本機設定汙染」(F1):版本清單與取日期兩個 git 呼叫都加 `--no-show-signature`;解析碰到認不得的片段整份判不了(回 None),不再跳過後沿用上一個提交編號——跳過一樣會漏掉一版、追錯寫下那一版;日期不是 YYYY-MM-DD 就不給。
- 乙 測試前提(F2):補 git log --follow 那一筆是 C 的前提斷言。
- 丙 說明指錯(Z1)。
