# r2 收貨紀錄(code-筆記形狀擋)

凍結材料:r2-delta.patch(r1 修正差異);r2-snapshot.patch 是 r1 修正後的全量快照(供參照)。分級 standard。

## 席位收貨

- 3 席全交(通才 opus、架構對齊 sonnet、外家否決 Codex);等完成通知、ls 確認在,才讀。所有席收齊前沒動工作目錄。
- 獨立性:Claude 席派工詞禁讀卷證目錄與別席報告;外家席過程紀錄(r2-外家否決2-codex.stdout)沒有別席報告路徑。
- report-normalize 3 份皆已正規化;quote-check 3 份全錨定(對 r2-delta.patch)。
- refcheck:外家席 4 個 missing(`scripts/run@v2`、`scripts/run`、`MOC/index.md@HEAD:5`)是它在臨時目錄造的例子檔,不在 repo 裡;照它的做法寫成回歸測試重現(下表 r2g-F3、r2g-F6)。
- seat-check:派工單的材料欄格式判成 vacuous(與 r1 同形),不判漏查。
- 編排者重現(回歸測試 `t_note_shape_code_review_r2_regressions`,修前 12 條紅):
  | 發現 | 重現 | 結果 |
  |---|---|---|
  | r2a-F1 一般筆記用 [src:] 夾帶行號 | 回歸 ①一般筆記正文的 [src:] 照擋 | HIT(修前紅) |
  | r2a-F2 @ 後面帶點(@v1.2.3、@origin/main)不當釘版本 | 回歸 ①@ 標籤帶點、①@ 遠端分支名 | HIT(修前紅) |
  | r2a-F3 doctor 200 上限退到上線點之前 | 回歸 ⑨(上線點前主線造 205 提交) | HIT(修前紅) |
  | r2a-F4 指路行別名夾帶、全形逗號誤擋 | 回歸 ①別名夾帶現況、①全形逗號、①FACT 不吃指路豁免 | HIT(修前紅) |
  | r2a-F5 同名判定先讀每支沒副檔名的檔 | 讀碼:by_name 建表迴圈對每支 kind 非 None 的檔呼叫 _ns_is_code | HIT(讀碼確認) |
  | r2a-F6 CI 註解與計劃做法段仍寫「排除其他遠端分支」 | 讀碼:ci.yml 註解與計劃〈做法〉CI 那條 | HIT(讀碼確認) |
  | r2a-F7 doctor --ci 跳過事後掃描、200 上限沒測試 | 回歸 ⑧ ⑨ 補上 | HIT(缺測試屬實) |
  | r2f-F1 _ns_mainline_refs 平行於 _mainline_ref | 讀碼:兩支各自找主線 | HIT(讀碼確認) |
  | r2f-F2 _NS_SRC_MARK_RE 重複 SRC_REF_RE | 讀碼 | HIT(讀碼確認) |
  | r2g-F1 改名過來的程式檔不喚醒舊引用 | 回歸 ④ | HIT(修前紅) |
  | r2g-F2 新程式檔喚醒漏單一檔名 | 回歸 ⑤ | HIT(修前紅) |
  | r2g-F3 真檔 scripts/run@v2 被拆成釘版本 | 回歸 ①真檔名含 @ 當一般引用、③refcheck | HIT(修前紅) |
  | r2g-F4 合併時改名把上一版帶入的行當新寫 | 回歸 ⑥(斷言合併結果真的在新檔名裡有那行) | HIT(修前紅) |
  | r2g-F5 新增行全域文字回配誤擋別篇舊行 | 回歸 ⑦ | HIT(修前紅) |
  | r2g-F6 .md 的壞釘法誤擋 | 回歸 ①.md 的壞釘法不擋 | HIT(修前紅) |
- 編排者修的時候自己另抓到一個(不是席位報的,不進 findings-set,交 r3 審 delta):CI 上本地 main 追蹤的 origin/main 就是這次推上來的頂端,只認 upstream 當主線會把整批排除、一行不查;改成頂端已在主線裡就不拿它排除。回歸 ⑩,拔掉修法會紅(已實測)。
- 修法改動既有測試 4 處(抽取器預設不切釘版本、[src:] 豁免只給 regen 筆記、主線要設 upstream),都是 r2 修法刻意推翻 r1 的前提,理由見計劃〈代碼審修正紀錄〉r2 段。
- 15 條全折(輪內三席皆 major,不得放行);refuted 無。
