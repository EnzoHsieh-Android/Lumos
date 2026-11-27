severity: major

severity: major
blocking: 是
`scripts/lumos:81077`(常數在 `scripts/lumos:81060`):正文切段用整串相等比對標題文字,規格〈用詞〉計劃正文要排除的是〈驗收條款〉、〈預期值表〉、〈審計修正紀錄〉這幾節。實際計劃的標題常帶後綴,例如 `## 審計修正紀錄(r1)`、`## 審計修正紀錄(lumos-design-loop)`、`## 驗收條款(全部有真測試、綠)`。`docs/lumos-toolchain-knowledge/Projects` 底下我數到約 11 份帶後綴的審計修正紀錄標題、3 份帶後綴的驗收條款標題。這些節因此被當成「計劃正文」。
後果有三個:
- 判讀材料把審計修正紀錄當正文附給判讀代理。
- 第 2 層驗證接受引自審計修正紀錄的引句,理由是「正文寫了、條款沒收」。
- 第 1、4 層的 `deps_sha` 含這幾節,設計審每追加一筆修正紀錄,所有第 1、4 層判讀都變「待複核」。
最小重現(未直接跑 `_choice_layer_basis_errs`,以下只重現切段這一步):用 `importlib.machinery.SourceFileLoader` 載入 `scripts/lumos`,對含 `## 驗收條款(全部有真測試)`、`## 審計修正紀錄(r1)` 的文字呼叫 `_choice_plan_sections`。回傳清單含 `'〈驗收條款(全部有真測試)〉'` 與 `'〈審計修正紀錄(r1)〉'` 兩段;只有標題恰為 `## 審計修正紀錄` 的那段被排除。新測試沒覆蓋帶後綴標題。
引句:「_CHOICE_LAYER_NOT_BODY = ("驗收條款", "預期值表", "審計修正紀錄")」

severity: minor
blocking: 否
`scripts/lumos:81599` 與 `scripts/lumos:81722`:整份驗證只限制 `quote` 的實字數(10 到 200),沒有限制原始長度。`_kt_sit_quote_norm` 比對前把連續空白收成一個空格,所以夾 70KB 空白的引句仍能逐字比對通過,但判讀檔存的是原文,超過 `_CHOICE_LAYER_DOC_MAX`(64KB)。結果是驗證全過,寫檔階段才在「第 N 筆」報「寫不進去」。前面幾筆的判讀檔與 layer 事件已寫入,「全過才寫、不合什麼都不寫」的合約就破了。實際發生機率低(要判讀代理吐出填充空白的引句),未能重現。
引句:「n = _real_chars(_kt_sit_quote_norm(b["quote"]))」

severity: minor
blocking: 否
`scripts/lumos:80715`(自裁 2「多平台混判」):換候選時 `p["rows"]` 只清本平台組的列,前面平台組用舊候選跑出的列保留。收尾判定時 `new_sha` 取新候選,A 組的 killed、survived 卻是對舊候選量的。舉例:A 組用候選 1 跑出 killed,B 組候選 1 編不過、換候選 2,最後帳上寫「候選 2 killed by A 的測試」,但候選 2 從沒在 A 跑過。這只在同一支壞法檔被兩個平台守的測試同時守時才會發生,而且前提是前一組已跑完,我沒有真跑過兩個平台,未能重現。需要明文取捨,或在換候選時把前面平台組的列標弱證據。
引句:「p["x"], p["rows"], p["plats"] = nx, {tk: v for tk, v in p["rows"].items() if tk[0] != plat}, set()」

severity: minor
blocking: 否
`scripts/lumos:81904` 起的 `_choice_kill_survivor_list`:它用跑之前掃出的 `res`,而 `res` 裡的壞法身分是換候選之前的。合批編譯在這次 run 內換過候選的存活行,`new_sha` 與帳上 reach 事件記的新候選不同。`_choice_reach_valid` 比對 `cov_sha` 會失敗,清單印成「未分類」,而不是「<分類> 未判讀」。擋不擋不受影響,只是印出的分類錯。未跑換候選的案例,未能重現。
引句:「segs = _choice_seg_fill(sc, _choice_nsha(xs))」

severity: minor
blocking: 否
`scripts/lumos:81525`:`--template` 印第 1 份時直接 `print(_choice_layer_read_part(...)[0], end="")`。讀回失敗(雜湊不符,例如材料含落單的 `\r`,`read_text` 會做通用換行轉換)時回傳 None,stdout 會印出字面 `None`,同一行指令仍 rc0。實務上落單 `\r` 很少見,未能重現。應該檢查原因並 rc2。
引句:「print(_choice_layer_read_part(wd, lid, 1)[0], end="")」

對照規格,其餘的自裁看起來沒問題:
- 推送閘五個子原因逐行加總等於原本的存活行數,擋不擋與回報上限不看層。沒有其他程式依賴原因字串 `存活`。
- `_choice_push_read` 改回三值,呼叫端都已同步。
- 舊帳沒有 layer 事件時走「未判讀」,不會當掉。
- 判讀檔雜湊、檔名、`deps_sha` 的寫端與讀端用同一套算法,一致。
- 撤回事件的空字串欄位型別通過 `_CHOICE_LAYER_TYPES`,撤回後確實變成未判讀。

總結:最高等級是 major
