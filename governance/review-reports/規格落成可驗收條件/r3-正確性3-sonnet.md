severity: blocker

## 逐節審查意見

**開頭 metadata(decisions/d1–d12 鏈、tags、lands_in)**
已讀,無 finding。decisions 的 superseded 鏈(d3→d11、d5→d10→d12、d6→d8→d9)首尾一致,沒有懸空引用。

**為什麼(數字表)**
已讀,無 finding。r2 訂正過的口徑(538 篇 34 篇掛標籤、迴圈 128/159、分級 622/96/12)已寫死量法,本輪未再變動。

**兩層要分開**
已讀,無 finding。

**一、門怎麼判**

finding 1
severity: blocker
blocking: 是——判準:B1/S16/S23 的整個補丁建立在「實務隱患節內」這個範圍限定上,但這個「節」的邊界演算法(從哪一行算節的開頭、到下一個 `##` 為止還是到 `###` 為止還是到檔尾)全篇沒有定義,而且 `scripts/lumos` 現有程式碼裡也沒有任何「抽取某個 `##` 節的內容範圍」的既有函式可借用——`cmd_pitfalls --check` 只用 `re.search(r"(?m)^##\s+.*實務隱患", text)` 驗**存在**,不驗**邊界**(`scripts/lumos:21545`)。r2 邊界席已經抓到「縮排/引用塊/全形冒號」這類行內變體,但沒人問「節」本身怎麼圈,這正是 r1 和 r2 兩輪補丁共同的盲點(都在修「這一行算不算已排除」,沒人修「這一段算不算實務隱患節」)。
引句:「類名不在四類、或不在實務隱患節 → 不是合格行,照掃」
spec 哪一節:一、門怎麼判,第 133 行。問題:`_excluded_line(line)` 宣稱能判「不在實務隱患節」,但全篇沒有給出節邊界的判定演算法,也沒有對應的驗收條款(S16/S23 只驗「行本身」的格式,不驗「節邊界抓對了沒」)。

**二、條款句式**

finding 2
severity: minor
blocking: 否——判準:失敗模式是明確報錯(閘印「句首『在…』被當觸發詞,不是觸發請改寫或用主體開頭」),不是靜默吃掉,作者看得到、改得掉,代價只是要重寫一句話,不構成繞過或資料損失。
引句:「停用詞   = 當然|當下|當前|在此|在於|若干|若是   (句首命中停用詞 → 視為無條件型,不當觸發詞)」
spec 哪一節:二、條款句式,第 151 行。問題:停用詞表只列 7 個詞,「若不」「在場」「當機」「當初」等常見中文詞不在表內;照文法推演,這些詞句首無逗號時落在「有 當/在/若 開頭但配不出觸發子句、又不算無條件型」的真空地帶,結果是被判「格式看不懂」而不是被正確識別成無條件句——但 spec 自己已經把這條訊息路徑寫死成報錯而非靜默放行,所以只是誤判率偏高、不是安全洞。

**三、綁定規則**

finding 3
severity: blocker
blocking: 是——判準:這個檢查機制本身可以被繞過,而且繞過的成本極低(改一個字串),直接重開 B3 想堵死的那個洞(全標 keeps 免紅)的等價效果——換成「單條 keeps 也能靠假造既存性矇混過關」。
引句:「`git log -S"def <測試名>" --diff-filter=A --format=%ad` 的首次出現日期 < 計劃 `created`),剛寫的樁測試標不了 keeps」
spec 哪一節:三、綁定規則,第 165 行。問題:`git log -S"<字串>"` 是對**字串內容**做 pickaxe 搜尋,不限定檔案路徑、不驗證這個符號是否連續存活到現在,也不驗證它現在是否仍在同一支測試檔裡。作者只要把新寫的樁測試命名成任何一個**曾經在 repo 歷史裡出現過、後來被刪掉**的舊測試函式名(哪怕是完全不相干模組的實驗性程式碼),`git log -S"def <名>" --diff-filter=A` 就會撈到那個古老的「首次新增」commit,日期必然早於計劃 `created`。因為 spec 沒有要求路徑限定(`-- <測試檔>`)也沒有要求該符號至今仍連續存在,這條既存性檢查名不副實。

**四、新閘 `lumos spec-gate`**

finding 4
severity: major
blocking: 是——判準:S27 只定義了「0 支跑到」這一種弱證據情形並綁了測試,完全沒定義「跑到 2 支以上」(參數化測試、跨類別同名方法)這種同樣會讓退出碼失真的情形,也沒有對應驗收條款或測試,是一個沒人接住的分支。
引句:「看測試工具說「跑了幾支」,恰好跑到 1 支且失敗才算紅;0 支被跑到(匯入錯、檔名錯、環境缺)是弱證據,擋下並印原因,不當紅也不當綠」
spec 哪一節:四、新閘,第 175 行。問題:「恰好跑到 1 支」暗示 2 支以上不算紅,但沒寫清楚 2 支以上要當弱證據擋下、還是當「部分紅部分綠」直接判非紅、還是當例外拋錯——三種實作選擇後果完全不同(擋下最安全;若實作者偷懶寫成「只要有一支失敗就算紅」,就重蹈本文自己在 guard-kill 那條記憶裡警告過的 `killed_unattributed` 弱歸因覆轍),而 S27 的測試 `t_spec_gate_red_needs_one_ran` 從名字看只覆蓋「一支都沒被跑到」,不覆蓋這個分支。

**五、逃逸自動記**
已讀,無 finding。代碼審逐條嚴重度(`_precision`/`--finding-severity`)、CI 切詞(`_ci_step_is_test`)、推送閘只認「tier=high 且」開頭這三處都已在 `scripts/lumos:6199-6211`、`scripts/lumos:22360-22363`、`scripts/hooks/pre-push:245` 落地且與 spec 文字一致,已用 Bash/Read 核對過。

**六、退場條件**

finding 5
severity: major
blocking: 是——判準:B9/S22 剛把「輪級判準」標成粗、不精確的證據(`precision: round`),但第六節計算退場門檻(blocker/major 逃逸筆數)時完全沒有把這個精度欄位接回去——一份「退回輪級判準記到的 major」與一份「逐條嚴重度精確記到的 major」在退場門檻的分子裡是等權重的,等於前面才承認的雜訊沒有被隔離,直接可能讓「前 30 份 major ≥3 份」這個撤除門檻被粗判準的假陽性(或假陰性)污染,卻無人知道要不要打折。
引句:「健檢加一段:雙向門放行了幾份、逃逸幾筆(按階段分:code-loop / CI / push-gate / push-gate-unreviewed)、單向門同樣(只當描述)」
spec 哪一節:六、退場條件,第 205–207 行。問題:分組只按「階段」(code-loop/CI/push-gate/push-gate-unreviewed),不按「precision」(round/finding),第 207 行「major 以上逃逸 ≥ 3 份」也未區分;S13 的驗收條款(`t_doctor_escape_by_door`)只講「按門與階段分開印」,同樣沒提 precision。

**進度(2026-09-17)**
已讀,無 finding。用 Bash 核對過 `_ci_step_is_test`、`cmd_canary --finding-severity`/`_precision`、`_auto_escape`、`push-gate-unreviewed`、pre-push 的 `grep -q "tier=high 且"`、`_door_for_loop` 六處程式現況,皆與這段文字宣稱一致。

**要動什麼**
已讀,無 finding。`_CLAUSE_GATE_SINCE`(`scripts/lumos:4599`)、`_LANDING_GATE_SINCE`(`scripts/lumos:15805`)確實存在,`_SPEC_GATE_SINCE` 確實尚未落地,與文字「三條不回溯常數」的現況描述一致。

**實務隱患(逐類確認)**
- 金流/對外送出/不可逆/守衛面:spec 自己第 237–238 行已答。
- **並行**:寫側 `_vault_write_lock` 已在第五節交代,且已排除:多人並行一行已在第 241 行寫。
- **效能**:已排除:效能一行已在第 240 行寫(閘只跑綁定測試不跑全套)。
- **資源(磁碟滿/寫不進)**:REVISIT(2026-10-17)已交代 fail-open 雙重失敗要事後查,已讀無新 finding。
- **回滾/遷移**:回退節第 277 行有交代(sha 待填,已誠實標「待填」而非假裝已定)、生效範圍第 231 行有交代不回溯。
六類都已讀,均已在文中處理或誠實承認殘餘,無新增 finding。

**驗收條款 S1–S28**
已讀。S6/S25 對應 finding 3,S27 對應 finding 4,其餘 22 條逐條核對過與對應設計段落一致,無新 finding。

**回退 / 誠實界線 / REVISIT / 審計修正紀錄**
已讀,無 finding。與 r2-intake.md 的 B1–B30 去重表核對過,本輪 r3 spec 內容與該表宣稱的折法一致;`governance/review-reports/規格落成可驗收條件/r2-intake.md` 記載的程式改動(`scripts/lumos`、`scripts/hooks/pre-push`、`scripts/test_lumos.py` 三處)也用 Bash grep 核對過確實落地。

## 固定席節點影響判斷

- **Systems/design-loop ★INVARIANT★**:本案明確要改處置閘第五步的合約行(呼叫 `_clause_check(plan, door)`),spec 已把新合約文字草稿(第 179 行)與綁定測試(`t_disposal_clause_gate`、`t_disposal_step5_shares_checker`,對應 S8)都寫清楚——這是「計畫中的合約變更」不是「意外破壞」,判斷:不算破壞,因為變更有明確的新合約文字與測試綁定,符合鐵則一「同一次工作內寫回」的要求。
- **Systems/bound-tests-gate ★INVARIANT★**:本案第四節「紅的判準」直接借用這支的「跑了幾支」邏輯,但目前只是設計引用、未動 `code-loop check` 本身的判定路徑(`scripts/lumos` 裡 bound-tests 相關函式本輪未改)。判斷:不影響,因為 spec-gate 是新指令、新資料流,沒有修改 bound-tests-gate 既有的 `_kill_run`/`_RAN_EVIDENCE` 邏輯,只是「借做法」不是「改實作」。
- **Issues/code-loop守衛main-direct盲區**:本案未涉及 main 分支直推路徑,pre-push 改動只在 `tier=high` 缺留痕句與 unreviewed 分支上。判斷:不影響,場景不重疊。
- **Systems/anchor-integrity ★RISK★、每支檔有家**:`scripts/hooks/pre-push`、`scripts/lumos`、`scripts/test_lumos.py` 皆是錨點檔,本輪已改且 spec 第 216 行已交代要 `lumos anchor approve`;`Systems/規格閘` 也已規劃承接 `cmd_spec_gate` 等新函式的「家」。判斷:不影響既有合約,因為兩個機制(錨點核准、每支檔有家)都在 spec 裡被主動配合,不是被動繞過。
- **Systems/lumos-cli-read、lumos-cli-lifecycle、測試假綠形態 ★INVARIANT★**:三者分別管 search 過濾 stale/superseded、CLAUDE.md re-inject 邊界、翻紅釘紀律。本案未碰 search 邏輯與 re-inject 機制本身(只改 graph-discipline.md 模板的 sentinel 內文字);已落地的三處程式改動也確實各配了翻紅釘(`r2-intake.md` 記載「釘 a/b/c」)。判斷:不影響,理由同上——只是共用檔案被列為「牽連檔」,沒有觸及這三條 INVARIANT 各自守的行為。

## 結論

severity: blocker
blocking: 4 條(finding 1、finding 2、finding 4、finding 5);與正文逐條 blocking 欄一致。
