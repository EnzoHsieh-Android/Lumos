severity: major

**未發現問題的邊界(各一句):**
- 第一次導入 features 表時,混合、空清單與改名三種情境,第 5 條、S10 和第 6 條的字面彼此一致:有任一新流程或沒有 flows 就算新情境,改名就算新情境。
- accept 有、accept_review 沒有,會被「沒有 accept_review」擋下。
- one_way 是 `[]` 但詞表命中,命中的類別併進宣告,合起來就是單向門。
- 三類同時成立時,訊息全列,`gate_code` 記最前面那類,`extra` 記全部類別。
- 各次嘗試的 debug 目錄是獨立的。
  - file: `/Users/enzo/harness/lumos-auto-device/scripts/templates/android-e2e-run.sh:494`:每次嘗試的現場是 `{name}.try{attempt}`,debug 在它底下。第一次失敗、第二次通過時,兩個目錄各有各的 commands.json,不會出現「兩個子目錄」。

1. labels 的上限截斷會讓被截掉的句子被誤擋,spec 沒說截斷時怎麼辦。
引句:「是去重後的清單、上限沿用同一級」
   - file: `/Users/enzo/harness/lumos-auto-device/scripts/lumos:40481`:`E2E_PATH_LIST_MAX = 200`。
   - 重現:一支流程有 201 個不同的 label,最後一個是 `驗收:x.y#A201`(共用流程帶別的情境 label 就會多到這個數)。照字面截成 200 個後,這個 label 不在聯集裡,擋下訊息印「A201 沒有檢查對到」,但流程裡實際有這個檢查。
   - spec 沒寫截斷時要記旗標、記 `checks: null`,還是改成上限內不截。
   - 處方「改設定或流程再跑整套」也指不出真因。
severity: major
blocking: 是——照字面實作會對已經做好的新情境誤擋。

2. 「舊情境自己補了 accept 就照第 5 條判」和第 5 條的範圍互相矛盾。
引句:「舊情境自己補了 `accept`,就照第 5 條判」
   - 第 5 條只判「新的項目」。
   - 重現:主線已有的舊情境(flows 全是舊流程)補寫 `accept`,沒寫 `one_way`、沒寫 `accept_review`。
   - 照第 5 條範圍字面實作:它是舊情境,所有規則都不套,補的 `accept` 沒有任何效果。
   - 照第 8 條字面實作:要逐句對照。但沒說舊情境要不要 `one_way`(只說新情境必填)、要不要 `accept_review`、要不要人點頭。實作者會各猜各的。
   - 這同時決定舊情境補了壞的 `accept` 會不會擋(S6 沒覆蓋)。
severity: major
blocking: 是——合約沒定,兩種實作會一個漏擋、一個誤擋。

3. 第 7 條在分岔點沒有 e2e 段時,字面實作會崩潰。⚠ 第 7 條有沒有被第 5 條的「主線沒有 e2e 段就不跑」涵蓋,spec 沒說。
引句:「用分岔點那棵樹的 e2e 段算指紋(`_e2e_fingerprint` 現成)」
   - file: `/Users/enzo/harness/lumos-auto-device/scripts/lumos:40741-40744`:`_e2e_scope_dirs` 第一行 `e2e["flows"]`,收到 None 會 TypeError。
   - 重現:分支切出時,分岔點還沒有 e2e 段;主線之後才加上,所以推送判定會跑。第 7 條拿分岔點的 e2e(None)去算指紋。
   - S11 只寫「找不到、讀不懂」印「這次不比」,沒寫分岔點本身沒有 e2e 段。
severity: major
blocking: 是——字面實作會在推送檢查內部出例外,規格卻要求不准這樣。

4. 「通過的那次嘗試」只寫在 S1、S3,〈做法〉第 4 條沒寫。
引句:「範本腳本每次嘗試的現場目錄已經記在 steps.json 那次嘗試的 `evidence.dir`」
   - 〈做法〉第 4 條沒說「那次嘗試」是通過的那次。
   - 第一次紅、第二次過時,只讀正文的實作者可能取第一次(或最後一筆)的目錄。
   - 第一次的 debug 目錄有紅的現場,算出來的檢查數就不是通過那次的。
severity: minor
blocking: 否——S1、S3 已寫明,屬措辭未同步。

5. 超過巢狀或大小上限會記成 `checks: null`,用的是「升級 Maestro」那個處方,對這種輸入是錯的。
引句:「超過記 `checks: null`」
   - 重現:一支新流程 repeat 很多次,commands.json 超過大小上限。這時 Maestro 版本沒問題,新流程仍被「讀不到執行紀錄」擋下。
   - 印出來的處方「升級 Maestro 2.x、跑 lumos update」解不開;放行指令是附上的,所以不會卡死。
severity: minor
blocking: 否——訊息誤導,有放行出口。

最嚴重 severity:major;blocking 共 3 條(第 1、2、3 條)。
