severity: minor

這輪修補的文件和程式在 d1、d2、d3 三條決策上一致,沒有 major。有 3 條 minor,都是修補只改了程式、漏改舊文字。我讀的是 `/Users/enzo/orca/workspaces/lumos-toolchain/web-ledger` 工作樹。它的程式與 f791d8ba 一致,只多了帳本提交。

## 發現

1. 計劃「不做」節還寫著修前的說法。
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸。修前版 d2da0e8c 的程式確實是這兩句說的樣子,修補把程式改了,這兩行沒跟著改。
   - 同一份計劃的第 1 節(第 77 行)寫「處置閘、`loop status --panel`、`loop next` 都呼叫 `_loop_round_format`,讀側先濾結局帳」。「不做」節第 223 行卻說「不改處置閘(含它那道有的帶輪次、有的不帶守衛的條件與訊息)」,第 226 行說「不動 `loop status --panel` 的混用守衛」。
   - 實際程式已經動了:`scripts/lumos:28397-28407`(處置閘)和 `scripts/lumos:14058-14059`(panel 守衛)都改成先過 `_review_rows` 再呼叫 `_loop_round_format`。
   - 三個月後的接手者讀「不做」節,會誤以為處置閘仍把結局帳算進混用。
   - 引句:「不改處置閘(含它自己那道「有的帶輪次、有的不帶」守衛的條件與訊息)」

2. 計劃做法和圖譜筆記還寫著「結局帳會改變擋下訊息和出路」。
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸。
   - 修前版:`des-n` 帳上有一筆不帶輪次的審查帳加一筆結局帳,再記一筆帶 `--round r2` 的。訊息是「既有 2 筆裡 0 筆帶輪次、2 筆不帶(其中 1 筆是結局帳…)」,出路是「換新編號重記」。
   - 修後版:同一個帳,訊息變成「既有 1 筆裡 0 筆帶輪次、1 筆不帶,這筆帶 --round」,出路是「拿掉 --round 再記」。
   - 沒改的文字有兩處:
     - 計劃第 85 行:「既有 N 筆裡 A 筆帶輪次、B 筆不帶(其中 K 筆是結局帳…)」。第 87 行:「或既有裡有結局帳 → 換新編號重記」。
     - `Systems/loop-convergence-recording.md:206`:「處置帳或既有裡有結局帳時只能換編號」。
   - 程式裡 `_rf_mixed_next`(`scripts/lumos:11366`)和 `_round_format_write_block` 都不再看結局帳。照文件走會白白換編號。
   - 引句:「處置帳或既有裡有結局帳時只能換編號」

3. 兩處「做完」的舊計劃和新規則對不上。
severity: minor
   - blocking: 否
   - 歸因:未判定。這是舊文件本來就沒跟上,不是修補造成的。
   - `Projects/代碼審修正關卡第0步_計劃.md:142`(status: done)寫「`--folded-set` 沒有 `none` 這個值」。d3 之後這句已經過時,`--folded-set none` 現在當空集合。
   - 同一份的 `--regression-set` 段沒有任何指向 d2「只收 `code-`」的指標。
   - 這輪補了循序 tier 錨定那篇和跑滿回顧兩處指標,漏了這篇。
   - 引句:「`--folded-set` 沒有 `none` 這個值,這裡要自己認」

4. 兩處小瑕疵,也算 minor。
   - 計劃的驗收條款順序是 S30、S32、S33、S31,新增的 S32、S33 插在 S31 前面。
   - `loop-convergence-recording.md:35` 引用〈記帳的輪次一條規則〉,實際標題是〈記帳的輪次一條規則與幾個記帳小修〉。
   - 同一句先說「沒有人裁紀錄的迴圈行為不變」,括號又說「審查帳壞改由輪次規則另外擋」,讀起來矛盾。實際是有人裁的迴圈仍落 `cap-ledger-bad`,沒人裁的才改由輪次規則擋(我跑 `_cap_retro_record_block` 和寫側的先後順序確認過)。

## 已驗屬實的主張

- d1:跑 `canary record` 加 `loop next` 實測。
  - 迴圈已有帶輪次的審查帳,先寫一筆結局帳,再記 `--round r2` 照常寫得進。
  - `loop next` 不判混用(停在 gate-pending);處置閘輸出沒有把結局帳當一輪。
  - `--panel` 對新迴圈仍被拒,是退役訊息,不是混用。
  - 零筆帳的第一筆:standard 沒帶 `--round` 被擋,訊息一致。
  - 已有輪次的迴圈再記不帶 `--round` 的一筆,被擋。
- d2:設計審的 `des-c` 和 `codeX` 帶 `--regression-set none` 都被擋,出路是「拿掉 --regression-set」。`canary record --help` 寫「只收 code- 開頭」,和決策一致。
- d3:`canary record --help` 的 none 規則是「`--findings-set` 真有叫 none 的 id 時照字面」「none 不能跟其他 id 並列」,和決策一致。`--folded-set none,f1` 被擋,訊息一致。
- 帳壞範圍:
  - 單一編號有壞列(`round` 為整數 5):該編號被擋,別的編號照常寫入,訊息有「別的編號不受影響」。
  - 整本帳不是 UTF-8:任何帶 `--loop` 的記帳都被擋,訊息是「整本判不了,任何編號都先不記」。
  - 不帶 `--loop` 的記帳照常寫入,與「已知限制」描述一致。
  - 「結局帳寫進去會讓迴圈判不了」「帳壞就擋所有記帳」這兩種修前說法,在圖譜主文裡已經找不到,只留在第 1、2 條提到的幾行。
- 跑完的測試全綠:`cap_retro_only_blocks_decided_loops` 3 個、`cap_retro_bad_ledger_fail_closed` 8 個、`canary_record_round` 19 個、`canary_record_outcome_exempt` 6 個、`dispositions_suggested_evidence` 3 個。
- 計劃、`loop-convergence-recording`、`design-loop`、棧別提問表態閘、跑滿回顧、循序 tier 錨定、`代碼審修正關卡`共 7 篇節點 `lumos lint` 都是 0 問題。
- 改過的筆記裡所有 `[test:]` 名稱,在 `scripts/test_lumos.py` 都各有恰好一支;`t_cap_retro_only_blocks_decided_loops` 也在。
- 白話段的「八個」與列出的八項一致。

## 三問

1. 原問題修好了嗎:有行為證據。結局帳不再讓迴圈卡死,帳壞擋下的範圍分清了,`--regression-set` 只收代碼審。程式側(`scripts/lumos`)和決策文字一致。文字殘留集中在第 1、2 條。
2. 修補處的正常、錯誤、相鄰路徑:
   - 已走過的路徑:結局帳混入、第一筆規則、單編號壞帳、整本非 UTF-8、設計審與 `codeX` 帶 `--regression-set`、`none` 並列。
   - 已知但屬原有問題:整本帳非 UTF-8 時,`--outcome` 記帳和 `loop next` 仍丟 `UnicodeDecodeError` 堆疊。我用修前版 `d2da0e8c` 重跑,同樣丟堆疊,不是修補造成的。計劃的「已知限制」沒有聲稱讀側有好訊息,判為範圍外,不報 finding。
3. 新發現的修前修後對照:第 2 條有兩版訊息輸出對照;第 1 條是兩版程式行為對照加文字沒改;第 3 條屬原有漏查,未判定。

## 未驗範圍

- 沒有逐項核對 `pitfalls-code-loop` 筆記的內容是否仍成立。我只用 `grep 循序` 掃過 Systems 目錄,沒有再發現把新 standard 代碼審說成循序的現行句。`skills/lumos-code-loop/reference.md:611` 的「standard 走循序」在「入口頁舊版全文」歷史段,不算現行。
- 沒有跑全套測試。

最嚴重 severity:minor。blocking:0 條。
