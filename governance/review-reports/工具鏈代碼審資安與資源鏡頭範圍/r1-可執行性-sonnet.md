severity: major

已逐節讀完整份 spec,並對照 scripts/lumos 與 templates.md 查證。〈做法〉5(`loop next`)的插入點與判別函式都能對上程式。主要問題在派工範本與守衛測試:照字面實作會做出「看起來有守、其實沒守到」的測試,以及子代理讀不到的指向。

**〈裁定來源〉、〈現況〉表、〈怎麼分辨〉、〈新規則〉1–3、〈不改〉、〈不做〉**:已讀,無 finding。
- `_is_toolchain_repo` 在 `scripts/lumos:25437`,呼叫處 6 個,與 spec 相符。
- `_roster_kind` 的 `code-` 與無連字號 `code` 判法也與 spec 相符。
- `bound-tests-gate.md` 確有 sitecustomize 那條 WHY。
- `pitfalls-code-loop` 的 d5、d6、d7 都在。

severity: major
blocking: 是 — 不改的話,實作者會做出一個對子代理不產生作用的「刪檔紀律」,也違反使用者在全域 CLAUDE.md 的明文要求
引句:「§1、§3、§7.8 各份派工詞圍欄第二行(寫 `git -C <那個目錄>` 那句)句尾補「刪檔照 §0 那條寫字面絕對路徑」」
〈做法〉9。派工詞圍欄會原樣貼給子代理,子代理看不到 templates.md §0,「照 §0 那條」是它解不開的指向。使用者 2026-10-14 的裁定寫得很明白:派子代理時這條要原文寫進派工詞。這個修法只告訴席位「去照一條你看不到的規矩」,不給「不准 cd 後用相對路徑刪、不准萬用字元、不准變數接路徑」的內容。
- 佐證:本次派工詞自己就是把整條原文寫進去。
- 佐證:全域 CLAUDE.md〈暫存清理〉最後一條:「派子代理時這條要原文寫進派工詞」。
- 佐證:``file: `skills/lumos-design-loop/templates.md:30` ``、`:142`、`:343`、`:418` 的第二行目前都只有 `git -C` 與「不要寫檔」,沒有任何刪檔字樣。

severity: minor
blocking: 否 — 範圍漏列,不會讓已列的部分壞掉,但「所有專案適用」的宣稱與實作對不上
引句:「§1、§3、§7.8 各份派工詞圍欄第二行」
〈做法〉9 與 S10。spec 說規則適用所有派工詞,但實際只補三份。
- §7.5 的圍欄第二行有同樣的 `git -C` 句(`templates.md:343`),沒列入。
- §2、§7.6 的圍欄沒有該句,也沒有任何刪檔處理。
- §0 第一條明列 §1、§2(§4 照它)、§3、§7.5、§7.6、§7.8 都是審查席派工詞,範圍口徑與〈做法〉9 不一致。
- 要嘛補齊,要嘛在 spec 寫明為何只補這三份。

severity: major
blocking: 是 — §7.8 裡加第二個圍欄會讓既有守衛與新守衛都可能空過,改壞了不會紅
引句:「在現有派工詞圍欄之後加一段〈工具鏈本 repo 的範圍〉,說明「`lumos loop next` 印出『鏡頭範圍: 工具鏈本 repo』時,改用下面這份」,附一個獨立圍欄」
〈做法〉2、S3、S4、S10,以及〈做法〉6 的測試清單。spec 沒寫新段落的標題層級、放在「輸出格式照 §7.7 C…」那段之前還是之後、測試要怎麼切第一個與第二個圍欄。
- `t_templates_security_seat_section`(`scripts/test_lumos.py:57856`)用 `split("## 7.8")` 再 `split("\n## ")[0]` 取整節,檢查「攻擊路徑、不報、真能用的憑證、資安-<模型>、推論」。第二個圍欄依 spec 會複製「同樣的席名、攻擊路徑四件、嚴重度錨」。原圍欄這些字被誤刪時,關鍵字仍在新圍欄裡,測試照綠。S3 要求的「原圍欄一字不動」因此沒有被守到。
- 若新段落用 `## ` 當標題,整節會被截斷,原有守衛反而誤紅。用 `###` 才安全。spec 沒指定。
- `t_seat_templates_carry_marker`(`scripts/test_lumos.py:96286`)只取 §7.8 標題後第一個圍欄的第一個非空行驗 LUMOS-SEAT。第二個圍欄的 `LUMOS-SEAT:` 行寫壞,只會讓那一席「整席沒有隔離」(templates §0 自己說的),卻沒有任何測試會紅。
- `t_role_cards_marker_absent_from_arch_and_security`(`:46049`)取整節檢查沒有 `LUMOS-ROLE-CARDS: on`,兩個圍欄都會被涵蓋,這個沒問題。
- S4 要驗「原圍欄的不報含『工具鏈本 repo 歸資源席』」。新圍欄的「不報」也有同一段,測試必須明確只切第一個圍欄,否則新圍欄含這句就會讓它照綠。
- S10 的 `t_templates_rm_literal_absolute_path` 必須對 §7.8 的兩個圍欄第二行都驗,spec 只寫「§7.8 每份」,沒寫新圍欄算不算。
- 建議 spec 補一句:測試按圍欄序號切,第一個圍欄與第二個圍欄各驗各的,第二個圍欄也要納入 S11 同款的 LUMOS-SEAT 格式檢查。

severity: minor
blocking: 否 — 守衛會變弱但不會做出壞系統;補上「切到步驟 2」就能修
引句:「各補一句「工具鏈本 repo:資安席只看三類、併發與資源改資源鏡頭,見 templates.md §7.8〈工具鏈本 repo 的範圍〉;消費專案照舊」」
〈做法〉4、S5。照 `t_security_seat_doc_sync` 逐檔列舉、整檔 `in` 判斷的寫法,S5 會空過。
- `skills/lumos-code-loop/SKILL.md` 現在就各有 1 處「工具鏈本 repo」與「§7.8」。
- `commands/06-代碼審與推送.md` 現在就有 1 處「§7.8」。
- `skills/lumos-code-loop/reference.md` 現在已有 3 處「§7.8」。
- 只有「消費專案照舊」現在是 0 處,是唯一真有鑑別力的檢查。
- 測試要像 `t_skill_code_loop_mentions_security_seat` 那樣切到 `2. **派審查員**` 到 `\n3. ` 之間,06 檔切到第一列。
- 另外,reference.md 在 `:256`、`:293`、`:420` 還有另外三份鏡頭列(「鏡頭各異:… 冪等併發」),spec 只改 `:587` 的步驟 2。編排者讀到那三處會看到沒有標註工具鏈例外的舊鏡頭列,這是一致性缺口。
- 06 檔「第一列」實際上沒有「併發與資源」字樣,補的那句「併發與資源改資源鏡頭」在該處沒有可指的對象。

severity: minor
blocking: 否 — 輸出行本身能做對,是驗收手段與觸發條件的細節沒寫清楚
引句:「在「應派」段後印(編制表算不出來、印「目前算不出該派誰」時也照印)」
〈做法〉5 與 S1。
- 插入點:程式裡「應派」是 `scripts/lumos:16431` 的 `if out.get("roster")` 加 `elif out.get("roster_note")`。實作者必須把新行放在 `elif` 結束之後、`reviewed_spec` 印出之前,才算兩種情況都印到。spec 沒寫「無條件、緊接 if/elif 之後」,實作者可能不小心塞進其中一支分支。
- `_root` 取得:現有的 `_root = Path(repo).resolve() if repo else _vault_repo_root(env)` 在 `try` 裡面,而且只在帳上有 `spec_path` 時才會算到(`:16399` 附近)。新行要自己再算一次 root,不能重用那個區域變數。spec 說「照那支取法」,但沒說要獨立算,也沒說要包 try。`emit` 在 converged 路徑已經寫過 `_loop_gov_mark`,在這裡丟例外會改掉 rc。
- 開頭:S1 說「以『鏡頭範圍: 工具鏈本 repo』開頭」,但規格給的行有兩格縮排,測試要 `strip()` 才比得過。
- 「消費專案輸出逐字不變」:改動前的版本拿不到。測試只能在同一夾具裡跑兩次,一次放 `skills/lumos-project-notes/SKILL.md`、一次不放,斷言「去掉那一行之後兩份完全相同」。spec 的測試名稱沒寫這個做法。
- 夾具 `_mk_roster_fixture`(`scripts/test_lumos.py:40481`)的 vault 在臨時目錄,必須帶 `--repo` 指向放了 SKILL.md 的目錄才會成立。
- 分級:spec 說代碼審編號一律印,沒限 tier。`code-` 的 light 與 standard 沒有資安席,也沒有「併發與資源席」(standard 是循序單審),印「資安席照 §7.8、併發與資源席改資源鏡頭」在那裡會誤導。建議限 `tier == high`,或把句子改成與 tier 無關的說法。
- S2 的反例缺漏:只測設計審編號。沒有測無連字號的 `codestage9` 型(`_roster_kind` 回 None),而 spec 明講那類不印。

severity: minor
blocking: 否 — 位置模糊,實作者很可能放對,但放錯不會被測試抓到
引句:「第 1 點句尾補「(工具鏈本 repo 的代碼審:「兩個請求同時進來」「同一次計算讀了兩次、中間被別人改了」這兩問不用答」
〈做法〉10 與 S11。§3 的「第 1 點」是「正確性」,底下有六個子項。「冪等與併發」是其中一項,在 `templates.md:158`,它不是第 1 點的結尾。「句尾」指哪一句必須寫成「補在『冪等與併發』那一項句尾」,否則可能補到最後一項「寫一半」之後,離被限縮的問題很遠。
- 括號內文直接寫進會貼給所有專案子代理的派工詞圍欄。消費專案的審查席也會讀到「工具鏈本 repo 不用答…見 §7.8〈…〉」,它看不到 §7.8,而且那句對它沒有作用。這需要編排者在消費專案派工時自己刪掉,與「靠 `loop next` 那一行機械判別」的主張相違。
- 若其他鏡頭席依 §7 規則刪掉第 1 點,這個括號的存在條件也要順帶說明。

severity: minor
blocking: 否 — 屬於驗收可執行性,不影響做出來的東西
引句:「[manual:跑 lumos lint Systems/pitfalls-code-loop 與 lumos decisions Systems/pitfalls-code-loop,核對兩條 RULE 欄位齊、d8 在、d6 仍有效;grep bound-tests-gate 那條括號]」
S8 與〈做法〉7 都是 manual。改壞了不會紅。`lumos lint` 能檢查 RULE 欄位是否齊全,但「bound-tests-gate 的括號指向 RULE」只用 grep 看,沒有測試。可以接受,但這是〈承認的限制〉沒列的一項。

**實務隱患鏡頭**
- 注入:`loop next` 新增的是固定字串,無風險。templates 新段落是範本,無風險。唯一的注入面是上面第二條 finding 的「派工詞貼進去的括號」,內容固定,不是自由文字。
- 併發:`loop next` 只多一次 `is_file()`,無風險。
- 資源:不開子程序、不讀大檔,無。
- 版本錯位:spec 已寫,方向是多審不是少審,無新增。

最高等級 major,blocking 2 條。
