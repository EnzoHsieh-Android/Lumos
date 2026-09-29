# r4 收貨紀錄(code-存量漂移防線乙;上限後破例一小輪)

破例依據:第 3 輪仍有 major,Enzo 2026-09-29 裁「修完再破例審一小輪」。
凍結材料:r4-snapshot.patch(r3 折入的修正差異,git diff -U10;1042 行,sha256 0613c46c…)。4 席全新:正確性 opus;併發、資安 sonnet(Sonnet 5.5);外家 finder Codex(gpt-5.6-sol xhigh,唯讀沙盒)。

## 席位收貨

- 4 席全交,等完成通知、ls 確認後才讀;席位沒動 repo。
- report-normalize 4 份都已是正規化格式;quote-check 4 份全錨定。
- 發現 10 條(正確性 4、併發 2、資安 1、外家 3);major 5(正確性 F1、併發 F1、外家 F1、外家 F2、外家 F3),其餘 minor。
- 同一件事被兩席報到的:SHA-256 repo 記不到內容編號(外家 F2、正確性 F3)。
- 本輪有 major,accepted 必須是空的,10 條全折。
- 當時的處置:其中 4 條(正確性 F1、F2,併發 F1,外家 F1)都出在為了閃避 python3.9 解析崩潰加的事先量測;Enzo 同日裁定先把工具最低版本改成 3.14(另開計劃),乙暫停。3.14 於 2026-09-29 推上主線後,乙接到新主線上續做。

## 機械重現(在審的那一版上跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性 F1(elif 長鏈照樣崩) | 席位附的 17 萬層 elif 輸入給系統 python3.9 | 採信;改 3.14 後以 /opt/homebrew/bin/python3(3.14)實跑同形狀輸入:MemoryError,接得住 |
| 併發 F1 / 外家 F1 / 正確性 F2(事先量測的成本、誤算、門檻) | 讀 _drift_py_too_deep | HIT:讀碼確認;整段刪掉後不再存在 |
| 外家 F2 / 正確性 F3(SHA-256 記不到內容編號) | 讀 _drift_list:`re.fullmatch(r"[0-9a-f]{40}", where)` | HIT:讀碼確認;修完用真的 `git init --object-format=sha256` 加 NFD 檔名釘測試 A1 |
| 外家 F3(一支讀不出就把另一支的命中降成判不了) | 席位附的指令:good.py 定義 target、bad.py 讀不出,呼叫 `_drift_probe_is_candidate` | HIT:修前 candidate=None、tip_condition=True;修完釘測試 B1 |
| 正確性 F4(判不了點名無關的檔) | 讀三處 `_drift_bad_note(tree)`:取整棵樹的 bad_paths | HIT:讀碼確認;修完釘測試 C1 |
| 併發 F2(名稱集合記憶體) | 讀 _DriftNames:全文接起來再 findall | HIT:讀碼確認;席位附的 52.9MB 實測沒重跑 |
| 資安 F1(檔名控制字元) | 讀 _drift_bad_note:路徑原樣接進說明 | HIT:讀碼確認(推論,席位標了未實測);修完釘測試 D1 |

## 處置

- 全部折進程式、測試與筆記:
  - 正確性 F1、F2,併發 F1,外家 F1:工具最低版本改 3.14 後,事先量測(`_drift_py_too_deep` 與門檻常數)整段刪掉,只留接 MemoryError/RecursionError;r3 回歸測試 C1 改驗極長的一行與極長的 elif 鏈在 3.14 上回 None 退回正則、一般大檔照解析。Systems/存量漂移守衛 那條 PITFALL 標成已撤。
  - 外家 F2、正確性 F3:列檔快取認 40 碼與 64 碼提交編號;測試 A1。
  - 外家 F3:名稱集合用讀得出的檔建、標 partial;找到照算候選,找不到而有檔讀不出才判不了;測試 B1。
  - 正確性 F4:新增 `_drift_row_unread`,判不了只點名這一行條件實際碰到的檔或筆記(status 點名指到的筆記);三處呼叫一起改;測試 C1,r3 的 A4 跟著改。
  - 併發 F2:名稱集合逐支檔建,不先接成一大段。
  - 資安 F1:點名的檔名經 `_esc_clean` 把控制字元換成空格;測試 D1。
- 翻紅驗證(每項在乾淨複本改壞一處、清快取後跑對應測試):只認 40 碼 → A1 紅;有檔讀不出就判不了 → B1 紅;點名整棵樹 → C1 紅;不跳脫 → D1 紅。
- refuted 無;accepted 無。
