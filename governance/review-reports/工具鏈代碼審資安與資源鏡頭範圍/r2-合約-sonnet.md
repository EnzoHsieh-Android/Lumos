severity: major

**固定席逐條判:**
- `Systems/pitfalls-code-loop` 沒有任何 ★INVARIANT★ 行,`Projects/代碼審資安席_計劃` 也沒有。
- `Systems/bound-tests-gate` 唯一的 ★INVARIANT★ 是 bound-tests 閘那條。本案只改該篇的 sitecustomize 那條 WHY,所以不影響。
- d6「必派、處置閘會擋」不受影響:`_TIER_ROSTER` 的 `資安` 席、`_disposal_security_step` 與 `loop status --disposal` 都不動,收窄的只有派工詞。
- 處置閘規則不被破壞:`scripts/lumos:27976` 在 `code-` 迴圈輪內有 major 以上時要求 accepted 為空,全 minor 輪才允許放行。本案沒改這條,出口設計也有顧到它(細節見 finding 1)。
- `scripts/lumos` 有 `_is_toolchain_repo`,位置在 `scripts/lumos:25437`。`cmd_loop_next` 的「應派」輸出段與「在審材料」的順序也跟 spec 的描述一致(`scripts/lumos:16430-16437`)。

---

severity: major
blocking: 是 — 實作者照這份寫會綁一支守衛測試到不存在的段落,同步守衛要嘛永遠空過、要嘛把歷史段落也改成現行規則
引句:「`skills/lumos-code-loop/reference.md` 裡每一處列出代碼審鏡頭或「冪等併發」的地方(步驟 2 列席位處,以及另外三處抄了「冪等併發:重跑/同時進來/同次計算讀兩次」或「鏡頭各異」的段落)」
spec 段落:〈現況〉表第 79 列、〈做法〉4、驗收 S6。
問題:reference.md 沒有「步驟 2 列席位處」,而且「另三處」的數量與位置對不上現況。
- reference.md 的步驟 2 是「植 bug canary hunk」,已停用。步驟總覽(`reference.md:34`)寫「~~植 bug canary hunk~~ ⛔ 已停用」。
- 該檔提到「冪等併發」或「鏡頭各異」的位置如下:
  - 現行段落:`reference.md:74`(步驟 3 派 reviewer 的 refute framing)、`reference.md:293`(平行 panel 鏡頭各異)。
  - 帶「canary 型別輪替」字樣、協議已停用的段落:`reference.md:255-256`。
  - 歷史區塊內:`reference.md:420`(外家 prompt,在 381 行起「歷史與停用(只供回放舊帳判讀,不是現行規則)」之下)、`reference.md:507`(歷史區塊的 canary 型別表)。
- 照 spec「每一處都補」,等於把現行收窄規則寫進歷史回放區和已停用段落,與該檔頁頭「不是現行規則」的聲明矛盾。
- 反過來,若 S6 照 spec 說的「逐處切段」去切不存在的「步驟 2 列席位處」,測試會切到空字串。
佐證:
- file: `skills/lumos-code-loop/reference.md:34`
- file: `skills/lumos-code-loop/reference.md:381`
- file: `skills/lumos-code-loop/reference.md:420`
- 修法:spec 要逐段列出現行的實際位置(74、293、必要時 255-256),並明講歷史區塊不補。

---

severity: major
blocking: 是 — spec 宣稱「任何時候都走得通」,但有三種常見情況沒有路,實作者會卡住或亂補
引句:「這條路任何時候都走得通,所以不會卡住迴圈。」
spec 段落:〈新規則〉1「範圍外發現的處置」、驗收 S12。
問題:處置閘規則本身沒問題,有漏的是出口細節。
- (a) 文件宣稱的保護落在不能直接拿掉的地方。
  - 「拿掉那句不存在的保護說法」只對散文成立。
  - 若那句話是 ★INVARIANT★ 行(有 `[test:]` 綁定),拿掉要走合約撤除、`guard kill` 或審計流程。
  - 若在 decisions 欄,只能 `decision-supersede`,不能刪字。
  - 若只在程式註解或 docstring,那是改程式碼,不是「改文件」。
  - spec 對這三種都沒交代。
- (b) 「沒宣稱就在那支檔的家筆記補一行」沒講這行的形狀。
  - 專案規則要求 RULE 帶 `[依據:]`、`[since:]`、`[retire:]`,人裁另需 `[until:]`。
  - CLAUDE.md 鐵則 4 又規定「不防」這種承認風險的話要搬成帶日期或事件的 `REVISIT:` 回頭條件。
  - 提交前的筆記形狀檢查會擋沒帶欄位的新寫行。
  - 每次範圍外發現都要現場決定這行寫成什麼,第二輪、第三輪的手法會不一致。
- (c) 折入要標 `finding_kind`。
  - 修正關卡規則是:有 `finding_kinds` 時,只有 `code` 的折入發現才要附修正紀錄與測試;沒標則全部折入的都要。
  - spec 沒說這類折入記帳時要帶 `--finding-kind spec`(或 process),否則編排者被要求為文件修補補測試。
- 另外,每個被折的 major 都會產生新的 delta,需要再派全新席掃 delta(SKILL.md 步驟 5),輪數上限是 3。所以「不會卡住迴圈」只在輪數足夠時成立。
佐證:
- file: `scripts/lumos:27976`
- file: `docs/lumos-toolchain-knowledge/Projects/代碼審修正關卡第0步_計劃.md:82`
- file: `scripts/lumos:4464`(`_SLOT_CONDITIONAL` 對 `[retire:人裁]` 要求 `[until:]`)
- 修法:spec 補一條固定寫法(例:一律寫成帶欄位的 RULE,或統一掛在本案那兩條 RULE 下),並寫明折入帳要帶 `--finding-kind spec`。

---

severity: minor
blocking: 否 — 回退時才會用到,但現在寫錯,回退者照抄會被 lint 擋
引句:「兩條 RULE 標 `[status:superseded]`,並另記一條決策說明「回到所有專案同一份資安與併發鏡頭」」
spec 段落:〈回退〉。
問題:CLAUDE.md 規定作廢時 `[status:superseded]` 另必有 `[被取代:]`,回退段沒寫。被取代的對象(那條新決策編號)要在回退時才產生。回退的順序是先記新決策、再標 RULE,spec 寫的順序是反的。
佐證:CLAUDE.md〈寫筆記時〉表最後一列。

---

severity: minor
blocking: 否 — 實作者會發現指令寫不進,改成手改開頭欄位,違反鐵則 2
引句:「四欄:context=上面三句原話;alternatives=①照舊」
spec 段落:〈做法〉1。
問題:`lumos decision-add` 只有 `--decided`、`--context`、`--why` 三個旗標(`scripts/lumos:57512-57517`),寫不進 alternatives 與 trade_offs。`decision-amend` 的註解寫「只改一個文字子欄」,而 alternatives 是清單欄,這條路也不明確。spec 沒說這兩欄怎麼落地。
佐證:
- file: `scripts/lumos:57512`
- file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:114`(d7 帶這兩欄,是手寫或舊版指令的結果)

---

severity: minor
blocking: 否 — 過時引用,不會害實作者做錯,但本案自己的決策編號已經打架
引句:「**§3 代碼審派工詞第 1 點「冪等與併發」那一項**(d2):工具鏈本 repo 只問重跑與對外重試」
spec 段落:新規則 3、做法 10、Q2。
問題:
- d2 已標 `valid: false` 且被 d3 取代,但新規則 3 的標註仍寫 (d2),做法 10 寫「落實 d2」。
- Q2 的 text 仍寫「只留重跑與中途失敗」,而 d3 已更正「中途失敗」其實是另一項「寫一半」。Q2 的 `decision` 指到 `#d3`,內文卻是 d2 的說法。
- 同一份 spec 裡「d6」指的是 `Systems/pitfalls-code-loop` 的 d6,「d1」指的是本計劃的 d1,讀者要自己分辨。
佐證:spec frontmatter d2 `valid: false`、`superseded_by: "#d3"`。

---

severity: minor
blocking: 否 — 兩處 KEY 與新 RULE 並存時,以後的 session 會讀到互相矛盾的字面
引句:「新增決策 d8(d7 已被「擋推鏈改成會跑檢查工具」占用)與兩條 RULE 行」
spec 段落:〈現況〉表第 83、84 列。
問題:這是「散落各處同一件事」的一致性問題。
- `Systems/pitfalls-code-loop` 的 d6 KEY 行寫「(所有專案,工具鏈自己也算)」。
- `Projects/代碼審資安席_計劃` 的 KEY 寫「工具鏈自己也納入」,正文第 41 行寫「規則不分專案…不需要分辨是不是工具鏈自己」。
- spec 只在 41 行句尾補括號,兩個 KEY 行與 d6 內容一字不動。
- 照 CLAUDE.md,KEY 是「線索」、有 `[confirmed:]` 的 RULE 才有效力,所以不會真的推翻 RULE。但下一個讀 KEY 的 AI 要多繞一步。
- 建議在 pitfalls-code-loop 的 d6 KEY 行尾加一個指向 d8 的指標。

---

severity: minor
blocking: 否 — 條款文字與綁的測試範圍錯位,不是行為錯
引句:「當工具鏈本 repo 的高風險代碼審沒有資安席帳列時,處置閘應照舊判不過(退出碼 1、訊息含「資安席」)。」
spec 段落:驗收 S7。
問題:綁的 `t_disposal_security_seat_required` 用的是 `mkvault()` 臨時庫與假的 `app/login.py` 檔(`scripts/test_lumos.py:57466-57479`),沒有放 `skills/lumos-project-notes/SKILL.md`,沒走到「工具鏈本 repo」這個前提。處置閘本身沒有分 repo 的分支,所以結論成立。但條款寫「工具鏈本 repo」而測試沒驗,屬於條款字面比測試強。
建議:條款改成「與 repo 種類無關」,或在新測試裡放一個含該檔的夾具再跑一次。

---

severity: minor
blocking: 否 — 邊界案例,資安席遇到時可能分類不一致
引句:「刻意設定環境變數讓閘提早回 0。」
spec 段落:〈新規則〉1 的範圍外清單與類③的對照。
問題:類③「非刻意、一步就能繞過」包含「舊版工具」「新分支首推」這類環境差異,範圍外又排除「刻意設環境變數」。「非刻意」的環境變數,例如 shell 殘留的 `LUMOS_SKIP_*`、`FORCE_COLOR`、被別的程序帶進來的 `PYTHONPATH`,沒說歸哪一邊。sitecustomize 那條 WHY 是用「刻意設定環境」判範圍外,但意外殘留的環境變數應不應審,spec 沒寫判準。

---

**逐節結論:**
- 白話、裁定來源、怎麼分辨工具鏈本 repo:已讀,無 finding。
- 現況表:第 79 列有 finding 2,第 83、84 列有 finding 6。
- 新規則 2、3、4:已讀,無 finding;d3 的措辭與 `templates.md:158` 的實際文字相符。
- 做法 2、3、5:已讀,無 finding。
  - §7.8 的 `###` 子節不會被 `t_templates_security_seat_section` 的 `split("\n## ")` 截斷。
  - `loop next` 的插入位置與現行程式一致。
- 做法 9(刪檔紀律):已讀,無 finding。§0 第 22 行列的 §1、§2、§3、§7.5、§7.6、§7.8 與實際 6 個 `LUMOS-SEAT:` 圍欄(行 29、79、141、322、342、417)一致。§7.9 沒有圍欄,不需補。
- 兩條新 RULE 的欄位:已讀,無 finding。`[依據:人]`、`[since:]`、`[retire:人裁]`、`[until:]`、`[confirmed:]` 都齊,`[until:]` 剛好等於 confirmed 加半年。
- 不改的部分、不做:已讀,無 finding。
- 實務隱患:已讀,無 finding。
- 驗收條款:S1 到 S6、S8 到 S10 的條款與綁定測試名對得上;S6 有 finding 2,S7 有 finding 7。
- 回退:有 finding 4。

最高等級 major,blocking 2 條。
