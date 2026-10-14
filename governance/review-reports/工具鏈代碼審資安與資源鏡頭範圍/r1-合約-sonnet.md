severity: major

逐節已讀完。已核對的假設:`_is_toolchain_repo` 在 `scripts/lumos:25437`,有 6 處呼叫,屬實。`_TIER_ROSTER` 沒有認「併發」席名,屬實。d6 沒被取代、d7 被占用,屬實。兩條 RULE 的欄位(依據、since、retire:人裁、until、confirmed)符合 `[retire:人裁]` 另必有 `[until:]` 的規則。固定席的 ★INVARIANT★ 不受影響,見末段。

severity: major
blocking: 是 — 實作者照這份寫,遇到範圍外的 major 發現會走不通;這份規則又是為了讓迴圈不被這類發現拖著加輪。
引句:「blocker 照處置閘規則不能放行;範圍外的 blocker 只能走「改文件拿掉保護說法」那條折。」
位置:〈新規則〉第 1 點,連帶 S9 與〈做法〉2 的「看到可以順手提一句,標 minor」。
問題:spec 以為只有 blocker 不能附理由放行,實際上 code 迴圈的 major 也不行。而且判斷是整輪層級,只要同一輪有任何一席是 major 以上,accepted 就必須為空。後果有三個:
- 資安席依 §7.8 嚴重度錨,把範圍外的偽造類發現評成 major,就不能「附理由放行」,只剩「改文件拿掉保護說法」。文件沒宣稱保護時,這條路也不存在。
- 就算範圍外發現被標成 minor,同一輪別席有真 major 時,它也不能放行。
- 使用者記憶 `toolchain-review-lens-scope` 寫的是「major 不能放行時,範圍外的發現改成照實寫文件來折」,與 spec 的 blocker 說法也對不上。
佐證:``file: `scripts/lumos:27976` ``寫著「code 迴圈輪內有 major 以上的席,accepted 必須為空——major 一律折,不得附理由放行」。其來源是 probe 輪退場 d2,見 ``file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:55` ``。spec 沒處理這條(「不改處置閘」與 S9 的「附理由放行」兩處都受影響)。

severity: major
blocking: 是 — 刪檔規則只補一部分派工詞,與〈做法〉9 自己宣稱的「所有專案、所有派工詞共用」不符,無人看顧的子代理仍會卡在刪除保險絲。
引句:「§1、§3、§7.8 各份派工詞圍欄第二行(寫 `git -C <那個目錄>` 那句)句尾補「刪檔照 §0 那條寫字面絕對路徑」」
位置:〈做法〉9 與 S10。
問題:第二行含 `git -C <那個目錄>` 的圍欄一共四份,不是三份。
- 漏掉的 §7.6 架構對齊席,每個分級(light、standard、high)都必派,比 §7.8 出現得更頻繁。
- 還有 §2 辯方、§4 辯方、§7.5 對答案席、§9 回顧起草,它們的圍欄沒有那句 `git -C`,spec 沒說要不要補。
- S10 的測試只驗「§1、§3、§7.8」,漏掉 §7.6 時測試照綠。
- §0 的清單寫的是「§1、§2(§4 照它)、§3、§7.5、§7.6、§7.8」,範圍比〈做法〉9 大。
佐證:``file: `skills/lumos-design-loop/templates.md:30` ``、``file: `skills/lumos-design-loop/templates.md:142` ``、``file: `skills/lumos-design-loop/templates.md:343` ``、``file: `skills/lumos-design-loop/templates.md:418` ``是四份含 `git -C` 的第二行。``file: `skills/lumos-design-loop/templates.md:22` ``是 §0 的清單。

severity: minor
blocking: 否 — 實作者可自行判斷補哪裡,但 S5 的測試形同虛設,reference.md 會留下與 §3 互相矛盾的舊說法。
引句:「`skills/lumos-code-loop/reference.md` 步驟 2 列席位處 | 同上一份鏡頭列 | 改:同一句」
位置:〈現況〉表的 reference.md 列、〈做法〉4、S5。
問題:有三處對不上。
- reference.md 沒有「正確性 / 併發與資源 / 邊界與輸入 / 合約與圖譜一致」那份鏡頭列,「併發與資源」四個字根本沒出現。那份列只在 SKILL.md 第 29 行。
- reference.md 步驟 2(第 587 行)沒有鏡頭名單,「補同一句」的位置不明。
- reference.md 另有三處的鏡頭說法與 §3 第 1 點的 d2 衝突,但 spec 沒盤到,算「漏掉的第五處」。第 74 與 420 行抄了「冪等併發:重跑/同時進來/同次計算讀兩次」;第 293 行的「鏡頭各異」還寫「冪等併發」;第 256 行是同一類舊說法。d2 落地後,這幾處仍教人審「同時進來」。
- S5 的三個詞(工具鏈本 repo、§7.8、消費專案照舊)可以只靠補一句就過,驗不出以上任何一處。
佐證:``file: `skills/lumos-code-loop/reference.md:74` ``、``file: `skills/lumos-code-loop/reference.md:293` ``、``file: `skills/lumos-code-loop/reference.md:420` ``、``file: `skills/lumos-code-loop/reference.md:587` ``、``file: `skills/lumos-code-loop/SKILL.md:29` ``。

severity: minor
blocking: 否 — 交叉引用指到一段不含該內容的位置,實作者得自己補;資源席也沒有可貼的派工詞。
引句:「(工具鏈本 repo 的代碼審:「兩個請求同時進來」「同一次計算讀了兩次、中間被別人改了」這兩問不用答,見 §7.8〈工具鏈本 repo 的範圍〉」
位置:〈做法〉10 對〈做法〉2。
問題:〈做法〉2 描述的〈工具鏈本 repo 的範圍〉只有資安席一個圍欄(三類、範圍外、不報)。冪等與併發那兩問不用答,沒有寫在這段。§3 的括號指過去,會落空。另外「資源鏡頭」只有〈做法〉3 在立場表補了一句姿態,沒有任何派工詞或提問清單寫出孤兒、逾時、大輸入要問什麼。S11 與 S4 只驗字面詞有沒有出現。

severity: minor
blocking: 否 — 內部不一致,實作者可自行取捨,但會有人誤以為「一字不動」而漏改。
引句:「原本那個圍欄一字不動,開頭補一句「消費專案用這份」。」
位置:〈做法〉2 與〈做法〉3、〈做法〉9、S3。
問題:〈做法〉3 要改原圍欄「不報」裡的「歸併發資源席」,〈做法〉9 要改原圍欄第二行,而〈做法〉2 與〈現況〉表又說原圍欄、原六類段「一字不動」。圍欄內部其實會被改兩處。S3 只驗六類還在,不驗這兩處改動。

severity: minor
blocking: 否 — 守衛薄弱,但實作者不一定做錯。
引句:「段內圍欄應含提示注入、讀寫越界、一步就能繞過三類,範圍外清單應含偽造 git 內部、手填帳本欄位、換編號或改檔名」
位置:S3,對照〈做法〉2。
問題:S3 的條款沒有驗〈做法〉2 要求新圍欄「同樣的開頭與 LUMOS-SEAT 行、攻擊路徑四件與嚴重度錨、標 minor、blocking: 否」。S3 沒有逐圍欄分別驗,而且現有 `t_templates_security_seat_section` 把「## 7.8」到下一個「\n## 」整段當一個字串,只要一個圍欄有就過。新圍欄少了第一行 `LUMOS-SEAT:`,審查席唯讀隔離就不生效,但測試仍綠。「刻意設定環境變數」也在〈新規則〉的範圍外清單裡,S3 卻沒列。
佐證:``file: `scripts/test_lumos.py:57847` ``到 57858 行,以 `split("## 7.8")` 取整段後用 `kw in sec` 驗證。

severity: minor
blocking: 否 — 決策紀錄不完整、圖譜讀者可能被帶偏,不影響程式運作。
引句:「trade_offs=工具鏈本 repo 不再有人找刻意偽造與多會談競態。」
位置:〈做法〉1 的 d8 四欄,以及〈做法〉1 末兩行(不動 d6 正文、代碼審資安席_計劃只補 related)。
問題:新三類之外,§7.8 原有的類別在工具鏈本 repo 全部不再被看:登入與權限、密鑰與個資、加密與傳輸、行動端,以及「hook、安裝腳本、CI 會不會執行不可信位置的檔」。最後這項正是 d6 context 的起因(打開陌生 repo 時 hook 執行了對方的程式),也是 d5 當初寫的回頭條件。新「②讀寫越界」的定義不含「執行來路不明的檔」。d8 的 trade_offs 沒記這個代價,alternatives 也沒說明為何不把「執行邊界」納入。此外 ``file: `docs/lumos-toolchain-knowledge/Projects/代碼審資安席_計劃.md:41` `` 仍寫「規則不分專案…不需要分辨是不是工具鏈自己」,只靠 related 連結,讀者會看到兩份矛盾的說法。

severity: minor
blocking: 否 — 回退不完整,但帳本未動,可補救。
引句:「[[Systems/pitfalls-code-loop]] 兩條 RULE 標 `[status:superseded]`、d8 用 decision-supersede 標取代。」
位置:〈回退〉。
問題:回退清單漏掉〈做法〉7(bound-tests-gate 那條 WHY 括號已改成指向這兩條 RULE)和〈做法〉1 的 related 補連結。RULE 被標取代後,那條 WHY 的 `[因:]` 會指向已作廢的 RULE。另外 `decision-supersede` 需要 `--by` 指向新決策(``file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:19` ``),回退沒說要寫哪一條新決策,也沒說過程會開一本連鎖帳。

severity: minor
blocking: 否 — 程式與條款輕微的覆蓋缺口。
引句:「代碼審編號(編號以 `code-` 開頭,跟同一支指令裡修正關卡提醒的判法同一口徑;沒連字號的舊 `code…` 編號不印)」
位置:〈做法〉5、S1、S2、`lands_in`。
問題:
- 「沒連字號的舊 code… 編號不印」與「編制表算不出來時也照印」兩個行為沒有任何條款或測試;S2 只驗設計審。
- S1 的「其餘人讀輸出應與改動前逐字相同」要拿改動前輸出比對,需要預錄的基準字串,條款沒說。
- `lands_in` 只列 `Systems/pitfalls-code-loop`。cmd_loop_next 的輸出與 `--json` 欄位(新增 `lens_scope`)在 `Systems/design-loop` 那一帶也有敘述,但 spec 沒有補 lens_scope 說明的落點。

severity: minor
blocking: 否 — 屬寫法規範,不影響執行。
引句:「範圍要靠編排者照 `loop next` 那一行選派工詞;資安席一步只看席名與留痕,看不出派工詞用的是哪一份。」
位置:〈承認的限制〉。
問題:規則四要求把會過期的承認句搬成獨立一行回頭條件、原行刪掉那一句。這裡承認句仍留在原行,REVISIT 另開一行。RETIRE-IF 行末還帶了 `[retire:人裁] [until:2027-04-14]` 的欄位標記,這兩個標記只該在 RULE 行,放在 RETIRE-IF 行容易被誤當格子解析。

固定席逐條判(依 `lumos impact` 的固定席與相關節點):
- `Systems/bound-tests-gate` 的 ★INVARIANT★(第 24 行,code-loop check 逐支跑合約綁的測試):不影響。本案只改文件、派工範本與 `loop next` 的一行輸出,不碰綁測試的判定。唯一關聯是第 149 行那條 sitecustomize WHY 的括號文字(見〈做法〉7)。該行沒有 `[test:]` 綁定,改括號不會動到任何合約或測試。
- `Systems/design-loop` 的處置閘第五步 ★INVARIANT★(條款綁測試、回退節 ≥20 字含實字):不影響。本 spec 的 S1 到 S11 皆帶 `[test:]` 或長度足夠的 `[manual:]`,回退節也夠長。
- d6「高風險代碼審一律必派資安席」:不影響其「必派、處置閘會擋」。spec 不改 `_TIER_ROSTER` 與 `_disposal_security_step`,席名 `資安-<模型>` 不變。但 d6 context 寫的「所有專案、不需要分辨工具鏈」與新的派工範圍分工並存,spec 稱「不 supersede」成立,摩擦在上面第 7 條的文字說明。
- `Systems/pitfalls-code-loop` 的 `required-gated` 席(第 57 行的 KEY):不影響。處置閘只驗席名、報告 sha、看過的檔涵蓋最後一版,兩種 repo 一樣。

散落各處的說法對照:`templates.md` §3、§7、§7.7、§7.8、`SKILL.md` 第 29 行、`reference.md`(多處,見第 3 條)、`06-代碼審與推送.md` 第 5 行,其中 `templates.md` §7.9 通才席(鏡頭5)沿用 §3,不受影響。`skills/lumos-project-notes/reference.md` 與 `docs/methodology/圖譜即合約.md` 只提「資安席」,與新範圍不衝突。

實務隱患逐類:
- 注入:`loop next` 多印的一行是固定字串,無新風險。
- 併發:只多一次 `is_file()`,無風險。
- 資源:不開子程序、不讀大檔,無風險。
- 對外送出:不送任何東西出本機。
- 金流:不碰。
- 不可逆:帳本格式不變,回退可行。
- 守衛面:真正的風險是第 1 條(處置閘不讓 major 放行)。這是規則本身會卡住,不是漏擋。

最高等級 major,blocking 2 條。
