severity: minor

我在臨時 repo 實跑了你列的輸入,共 3 條 finding,都是 minor,沒有 blocking。實驗腳本在 `/tmp/bq/*.py`,用 `scripts/test_lumos.py` 的 `_tail_repo`、`_ns_note`、`_na_repo` 等工具函式組出測試專案。我另外跑了 `-k ns_append`、`note_audit_append`、`notelines_parse`、`note_audit_judge`,共 93 支全綠。

**B1 放寬帳 `pairs` 沒有上限,`_gate_event_fit` 逐筆彈出再重量整行,耗時隨筆數平方成長**
severity: minor
blocking: 否 — 只拖慢大量補括號的推送,判定結果不受影響
引句:「    while rows and size() > 4096:」
1. 輸入:一次推送裡有 N 行都是舊行尾補括號。每篇舊版本在 524288 位元組以內,篇數不限,所以 `pairs` 沒有上限。
2. 走到:`_ns_relaxed_record` 呼叫 `_gate_event_fit`,迴圈每彈一筆就用 `_gate_event_build` 加 `json.dumps` 重量整行,見 `scripts/lumos:1246`。
3. 預期:耗時大致隨筆數線性成長。
4. 實際(`_gate_event_fit` 單獨量測):

| pairs 筆數 | 耗時 |
|---|---|
| 5000 | 2.8 秒 |
| 20000 | 43.6 秒 |
| 50000 | 278.8 秒 |

   端到端(`note-shape --diff`,40 篇各 500 行補括號,共 20000 對)約 49.7 秒,rc 0。
5. 重現:`cd /tmp/bq && python3.14 -u k.py`,量 `_gate_event_fit` 本身跑 `python3.14 -u j.py`。
6. 補充:這個平方迴圈從 `_drift_m1_fit` 原封搬來,舊行為不變。但舊的 `rows` 本來就有 `n` 參數限制,新的 `pairs` 沒有上限,所以才第一次變成問題。

**B2 範圍沒配對成功時,`skip` 略過不了只被「尾巴判定」涵蓋的行,`check` 還把它印成 `[沒判過]`**
severity: minor
blocking: 否 — 重新 prepare 再 record 可繞過,只是「真的來不及」的逃生口失效
引句:「每個內容編號一個判定:同編號下所有範圍(整行與各個只判句尾的)取最重」
1. 輸入:在 base 到 tip 的範圍裡,某行已有「尾巴判 CONTEXT」的判定並提交。之後同一行在配不到舊句的範圍被檢查,例如 CI 用 40 個 0 當起點,或新分支從空樹算。
2. 走到:`check` 用 `_note_audit_class_for`(`scripts/lumos:29397`),只看整行判定,所以這行算「沒涵蓋」。`skip` 卻用不比範圍的 `_note_audit_fold`,`judged = set(fold)`(`scripts/lumos:29995`),把這行當成「判過了」。
3. 預期:`check` 擋下的行,`skip` 能略過,或至少訊息不騙人。
4. 實際:
   - `check --diff 0000…..tip` 回 rc1,印 `A.md:18  [沒判過]`。
   - `skip --diff 0000…..tip --note 來不及了` 先寫出一份略過檔,但它不含 `A.md:18` 這行。
   - 提交後再 `skip` 回「沒有可以略過的行」,`check` 仍擋同一行。
5. 重現:`cd /tmp/bq && python3.14 -u g.py`。
6. 這是上述範圍在空樹與 40 個 0 起點整行查的已知取捨帶來的連帶後果,不是新假設。

**B3 判定檔 `tail` 欄是空字串時,解析器收下,但各處讀法不一致**
severity: minor
blocking: 否 — 只有手改判定檔才會碰到,不是工具自己會寫出來的形狀
引句:「if "tail" in r and not isinstance(r["tail"], str):」
1. 輸入:判定檔某列 `{"id":…,"class":"CONTEXT","tail":""}`,對應一行整行新寫、沒有追加段的項目。
2. 走到:`_note_audit_parse_verdict`(`scripts/lumos:29312`)只要求是字串,空字串通過。`_note_audit_fold_scoped` 把鍵記成 `(id, "")`。`_note_audit_class_for` 只查 `(id, None)`,這筆永遠對不上。寫端 `_note_audit_scoped_row` 則是 `if tail:` 才寫,空字串被當成沒有。
3. 預期:空字串等同沒有 tail(照整行涵蓋),或整份當壞。
4. 實際:
   - `check` 擋下,印 `[沒判過]`。
   - `skip` 說「沒有可以略過的行」,因為不比範圍的 fold 算它判過了。
   - 對照組:沒有 `tail` 鍵時 rc0。
   - `tail` 是 123 或 `null` 時整份當壞檔,印提醒後當作不存在,`skip` 可正常略過,這個行為合理。
   - 另外 `tail:"abc"` 這類字串不是任何項目的舊句雜湊,同樣對不上,這是預期。
5. 重現:`cd /tmp/bq && python3.14 -u i.py`,看 `tail=''` 那一行。

**沒找到問題的輸入**(括號都用 summary 行實跑,rc0 代表只扣舊行違規):
- 括號群:
  - 能配對:全形半形混用、巢狀 50 層、括號內有行內程式碼、括號群之間零空白、括號前有全形空白。
  - 不配對(偏嚴,整行照查):只開不關、關比開多、括號內反引號本身不平衡、括號後接「。」或其他字。
- 編碼:LF、CRLF、BOM、檔尾有沒有換行(新舊各四種組合)、NFD 與 NFC 檔名、中文檔名、含空白檔名,`--staged` 和 `--diff` 都正常配對。同一組輸入的對照組(舊行整句重寫)都正確 rc1。第二層送審的 prepare、record、check 在 LF、CRLF、無結尾換行下都通。
- git 形狀:
  - 改動段刪 3 加 3 但只有第 2 對是補括號:第 2 行放寬,第 1、3 行照報。
  - 刪 3 加 2:整段都不配。
  - 同一篇補括號又在緊鄰處新增一行:該行被併成「刪 1 加 2」,補括號那行也整行照查。這是偏嚴。
  - 同篇不相鄰的新增行:補括號那行放寬,新增行照報。
  - 改名加補括號:整行照查。
  - 合併提交:正常配對。空樹起點:不配、不記失敗帳。
  - 524288 位元組的起點版本配得上,524289 就整篇不配,也不記帳。
- 長度:
  - 舊行 8 碼點(去頭尾空白)配得上,7 不配。
  - 括號 300 碼點配得上,301 不配。
  - 新行上限是算整行原文,摘要區有 2 格縮排,所以實際摘要行 1998 碼點配得上、1999 不配。這是原文口徑,不是漏洞。
- 其他:含 TAB 的檔名整篇不查。git 會給這種路徑加引號,`_notelines_parse_added` 會略過它。這個行為在改動前就如此,程式註解也寫明引號路徑給 None,所以不列為 finding。

**圖譜固定席逐條判**(只列了內容的節點)

| 節點 | 判定 | 理由 |
|---|---|---|
| `Systems/lumos-cli-read.md` ★INVARIANT★ search 排除 superseded | 不影響 | 這份 diff 沒碰 search 的篩選。 |
| `Systems/bound-tests-gate.md` ★INVARIANT★ code-loop check 逐支真跑綁定測試 | 不影響 | 閘本體沒動。`scripts/lumos` 與 `scripts/test_lumos.py` 都在牽連檔裡,綁定測試仍要在推送前的閘真跑。 |
| `Systems/guard-kill.md` ★INVARIANT★ rc 優先序與 JSON 純度 | 不影響 | guard kill 路徑沒動。 |
| `Systems/授權與歸屬.md` ★INVARIANT★ 主程式檔頭 SPDX 與 MIT | 不影響 | `scripts/lumos` 的第一處改動在 1224 行之後,檔頭沒動。`scripts/templates/note-audit-judge.md` 仍保有 SPDX 兩行,`-k license` 跑 11 支全過。 |
| `Systems/測試假綠形態.md` ★INVARIANT★ 還原翻紅釘要配前置斷言 | 不影響 | 這份 diff 不含測試檔,沒新增違規的釘子。 |
| `Systems/design-loop.md` ★INVARIANT★ 處置閘第五步 | 不影響 | 處置閘沒動。改動只在第二層筆記內容審的涵蓋計算。 |

最高嚴重度 minor,blocking 0 條
