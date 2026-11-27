severity: major

審查範圍:`r1-pack-code.patch` 全文逐 hunk 讀過,另跑了四支最小重現(臨時庫已用 `_ck_cleanup` 清掉)。已知過關、不報:`layer` 為 True、"3"、5 都被拒;`--part 0` 與超過份數會 rc2;引句不足 10 實字、全是標點、全形空白都被擋;`--withdraw` 指到沒判讀的行 rc2;事件含空字串欄位不會被帳寫入器丟掉。

severity: major
blocking: 是
`scripts/lumos:81724`(`_choice_layer_write`)。驗證階段只限制了 before、after、question、reason 的原始字元數,沒限制 `basis[].quote` 的原始長度。`_kt_sit_quote_norm` 會把連續空白收成一格,所以 70000 個空白夾在 quote 中間,照樣過驗證。寫入階段才發現判讀檔超過 64KB,於是在第 2 筆停下並回 rc2。第 1 筆的判讀檔與 layer 事件已經寫了,違反〈範圍〉9 的「整份驗過、不合什麼都不寫」。重跑同一個指令會在同一筆再死一次,每次還多寫一個重複的第 1 筆事件。

最小重現(`/tmp/lumos-seat-work/code-選擇點存活回指第三段/r1-邊界-sonnet/rep1.py`):`_ckl_setup(4, {}, record=False)` 之後,記錄兩筆(第 1 層一筆、第 3 層一筆),後者 quote 為 `"當使用者開啟頁面,系統" + " "*70000 + "應 顯示輸入框"`。

實際輸出:
- 第一次:rc2、「這份紀錄有 70489 位元組,超過…停在第 2 筆」,layer 事件 1 個、判讀檔 1 份。
- 重跑:rc2,layer 事件變 2 個。

修法方向:寫之前先算好每份判讀檔的大小並整份預檢,或給 quote 加原始字元上限。
引句:「停在第 {wrote + 1} 筆;已寫的事件照留,重跑同一個指令會補齊」

severity: minor
blocking: 否
`scripts/lumos:81060` 與 `:81073`(`_choice_plan_sections`)。排除段只認標題字面等於「驗收條款」「預期值表」「審計修正紀錄」,帶括號或前綴的變體都當計劃正文。repo 現有計劃裡 `## 審計修正紀錄(r1)` 有 5 份、`## 審計修正紀錄(lumos-design-loop)` 有 6 份,其餘如 `## T3 審計修正紀錄`、`## 驗收條款(全部有真測試、綠)` 也有。repo 自己的別處(`scripts/lumos:68266`)是容前綴比對。

實測(rep2.py):輸入 `## 審計修正紀錄(r1)` 與 `## §5 審計修正紀錄`,輸出段名是 `〈審計修正紀錄(r1)〉`、`〈§5 審計修正紀錄〉`,都沒被排除。後果有兩個:
- 這些段的文字進了判讀材料,第 2 層引句也能引它。
- 第 1、4 層的 deps_sha 把它算進去,審計紀錄一追加判讀就誤標「待複核」。

只影響提示,不影響擋不擋。
引句:「_CHOICE_LAYER_NOT_BODY = ("驗收條款", "預期值表", "審計修正紀錄")」

severity: minor
blocking: 否
`scripts/lumos:81073`。初始段名 `〈前言〉` 沒登記進 `seen`,之後遇到一級標題又產生一個 `〈前言〉`。frontmatter 與 `# 標題` 之間有文字、一級標題底下也有文字時,會出現兩個同名段(rep2.py 輸出兩個 `'〈前言〉'`)。判讀材料兩段都列,但 `_choice_layer_basis_errs` 和 `_choice_layer_deps` 用 `dict(v["sections"])`,同名只留後一段。結果是引前一段的 quote 被誤拒「引句不在 〈前言〉 裡」,改前一段也不會讓第 2 層判讀標待複核。
引句:「stack, name, buf, out, seen = [], "〈前言〉", [], [], {}」

severity: minor
blocking: 否
`scripts/lumos:81552`、`:81651`。份清單檔被改過時,只驗了最外層型別,內層形狀不驗。`parts` 含非 dict 時,`--part 1 --list <編號>` 在 `p.get("n")` 丟 AttributeError、rc1。`items` 的值不是 dict 時,記錄那條路在 `.get("plans")` 丟堆疊。預期是 rc2 加「清單不在了」。實測(rep3.py)兩條都印堆疊。清單在 gitignore 的工作目錄,屬本機單人檔,所以只算 minor。
引句:「part = next(p for p in d["parts"] if p.get("n") == n)」

severity: minor
blocking: 否
`scripts/lumos:17994` 對 `:18125`。gov 的 `layer_last` 只檢查 `type(layer) is int`,但讀側 `_choice_ledger_aux` 只收 0 到 4。帳上有 `layer: 5` 或 `-1` 的事件時,該行在 gov 被算成已判讀:實測兩個存活行各帶一筆 5 與 -1,輸出「第 1 層 0、第 2 層 0、第 3 層 0、第 4 層 0;存活裡未判讀 0」,四層加未判讀對不起來(rep4.py)。
引句:「c["layer_last"][(ck.get("file"), ck.get("fp"))] = ck["layer"]」

severity: minor
blocking: 否
`scripts/lumos:81220`(`_choice_layer_text`)。顯示用的 basis 項是「第一個符合形狀的」,不是通過驗證那一項。第 3 層的驗證只要求至少一項是有綁測試的條款,顯示卻取第一個條款號形狀的項。basis 為 `[S3(manual), S1(bound)]` 時,推送閘會印「在條款 plan#S3 補一支…測試」,指到 manual 條款。第 2 層同理,可能取到引句其實也在條款裡的段。`b` 取不到時 `show(_choice_plan_short(None))` 會印出字面的 "None"。
引句:「b = next((x for x in d.get("basis") or [] if isinstance(x, dict) and (n != 3 or _KT_SIT_CID_RE.fullmatch(str(x.get("where") or "")))」

總結:最高等級是 major。
