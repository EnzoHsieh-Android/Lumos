severity: major

整合、回退與知識同步這一輪有 8 條 major、5 條 minor。已逐節讀完整份 spec。內部交叉引用都存在:`[[Projects/後端工程提問與證據擴充_計劃]]` 與其決策 d10、`PQ_STAGES`、`_KNOWN_FRONTMATTER_KEYS`、`cmd_decision_add`、`parse_decisions`、`clause_bindings` 都對得上。我另在 `/tmp/lumos-seat-work/待決問題改存開頭欄位/整合回退-sonnet/r` 造了臨時庫,實際驗過一份帶 `pending_questions` 的計劃。

**實驗結果**
- `lint`、`spec-gate`、`decision-add` 遇到這個欄位都不崩。
- `set` 與 `append` 對它都回「擋下」。
- 現行 lint 只回「沒見過的鍵」這條提醒。

## 逐節結論
- 〈緣起〉、〈外部做法〉:已讀,無 finding。
- 〈資料放哪、長怎樣〉、〈讀法〉、〈三個消費端〉、〈指令〉、〈舊寫法〉、〈驗收條款〉、〈回退〉:有 finding,見下。
- 〈實務隱患〉:見最後的實務隱患逐類。
- 〈不做〉、〈待決問題(已答)〉:已讀,無 finding。
- 〈順手處理〉:有 finding,見 minor 的第 13 條。

## Findings

**1.**
severity: major
blocking: 是
spec 段落:〈資料放哪〉「寫法照決策紀錄那一套」,以及 S3。
引句:「給下一個編號(現有最大號加 1)」
問題:沿用 `cmd_decision_add` 的寫法,等於沿用它沒有寫入鎖的缺口。`question-add` 先讀檔、算「最大號加 1」、再整檔寫回,中間沒有 `_vault_write_lock`。同一個 repo 常有多個 Claude 會談並行,兩邊同時 `question-add` 會拿到同一個編號,或後寫的蓋掉先寫的。
後果:編號重複在這份 spec 的規則下是「讀不懂」,整份清單無法判定,規格閘會對那份計劃一律擋下。spec 沒要求加鎖,也沒有並行測試。
佐證:
- file: `scripts/lumos:20439`(`cmd_decision_add` 全程沒有鎖)
- file: `scripts/lumos:52416`(dispatcher 直接呼叫,沒包鎖)
- file: `scripts/lumos:19697`(`cmd_set` 有包 `_vault_write_lock`,決策指令沒有,兩者不一致)
- file: `scripts/lumos:19501`(`atomic_write_verify` 只管原子換名,不管讀改寫的互斥)

**2.**
severity: major
blocking: 是
spec 段落:〈資料放哪〉的範例與「值的引號與跳脫用同一支格式化函式」。
引句:「值的引號與跳脫用同一支格式化函式」
問題:兩句互相矛盾。範例寫 `blocking: true`,但共用的格式化函式會把 `true`/`false` 一律加引號。
實測:`fmt_scalar('x','true')` 輸出 `"true"`,`"false"`、`"10"`、`"#d1"` 同理。照 spec 做,`question-add --blocking` 寫出來是 `blocking: "true"`。
後果:
- 嚴格讀法若不剝引號,規格閘會把自己剛寫的題判成「布林寫錯」,指令把自己鎖死。
- 若剝引號,就得明說讀法接受哪些引號形式。目前「值裡夾了讀不懂的引號」沒有定義,單引號、雙引號、Obsidian 重寫後的形式都沒講。
- 若布林走特例不經格式化函式,又違反「共用同一支」。
佐證:
- file: `scripts/lumos:19216`(`_yaml_plain_ok` 把 true/false 排除在裸寫之外)
- file: `scripts/lumos:19238`(`fmt_scalar`)

**3.**
severity: major
blocking: 是
spec 段落:〈回退〉。
引句:「已經寫進計劃開頭欄位的清單留著,舊版當不認得的欄位忽略,不會因它擋。兩支指令一起拿掉。」
問題:回退只說「兩支指令一起拿掉」,漏了驗收條款本身。S1–S6 都綁 `t_qfm_*`,回退後這些測試不存在,條款變懸空綁定。
對照:同一族的原計劃已經有處理規則——回退時對應條款改成 `[manual: …]`,不留指向已刪測試的綁定。
後果:本篇回退後 `spec-trace` 與 doctor 的 S5 會報懸空。另外「已寫進開頭欄位的清單留著」,而〈舊寫法〉已把原計劃正文那一節換成一句指路,所以只回退程式的話:
- 原計劃的 7 題會變成沒人讀的資料。
- 人看正文也看不到題了。
- 留著的待人阻塞題看起來像在擋,其實不擋。
spec 沒說這種狀態怎麼收尾。
佐證:
- file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:277`
- file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:272`

**4.**
severity: major
blocking: 是
spec 段落:frontmatter 的 `lands_in`(只列規格閘、情境出題)與整份的知識同步範圍。
引句:「正文那一節改成指向開頭欄位的一句話」
問題:上線那天會對不上的既有文字沒有列入,而且 lands_in 漏了 `Systems/pitfalls-code-loop`。各處原文都是「目前不擋/工具不讀」,上線後全部變成錯的:
- 技能說明的情境出題第 4 步:還在教 AI 寫正文 `- [Q<n>] …`,並說「工具不讀」。
- `reference.md` 對「不做模板化盤問」那條的註記(「工具不讀」)。
- `Systems/pitfalls-code-loop` 的 `--stage` 一段:說題目清單已撤出,並帶 REVISIT。
- `Systems/規格閘` 的「待決問題的擋法」一節,與 `Systems/情境出題` 對應段落:各有 WHY、REVISIT 與「目前不擋」。
- 原計劃:
  - 開頭 REVISIT。
  - 關卡表第 1 列。
  - S1。
  - S3(「不列題」「JSON 只有階段與風險面」)。
  - 〈回退〉。
  - 合約候選那兩行(註明「另案上線時換掉」)。
- 測試 `t_backend_qo_question_section_not_parsed` 的 docstring:寫「新做法上線時換掉這支」。spec 沒說保留還是換。該測試只用正文版的計劃,新做法下仍成立。

另外 `Systems/情境出題` 的 responsibility 明寫「不負責〈待決問題〉的資料格式與擋法」,與 lands_in 把它列為落點直接衝突,spec 沒要求改負責範圍。
佐證:
- file: `skills/lumos-project-notes/SKILL.md:44`
- file: `skills/lumos-project-notes/reference.md:854`
- file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:212`
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:84`
- file: `docs/lumos-toolchain-knowledge/Systems/情境出題.md:6`
- file: `docs/lumos-toolchain-knowledge/Systems/情境出題.md:41`
- file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:154`
- file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:221`
- file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:223`
- file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:293`
- file: `scripts/test_lumos.py:56027`

**5.**
severity: major
blocking: 是
spec 段落:〈三個消費端〉的 `pitfalls --stage`,與 S5。
引句:「清單無法判定時不列題,印原因並回 2。」
問題:`--json` 輸出沒有定義。現行測試 `t_backend_qo_stage_facets_only` ③ 斷言 JSON 的鍵恰好是 `{stage, facets}`。S5 要列題,但沒說 JSON 要不要多一個鍵、叫什麼、題的欄位是哪些、無法判定時 `--json` 輸出什麼。
連帶:原計劃 S3 的「JSON 只有階段與風險面」在有欄位的計劃上會變成假的(見第 4 條)。
另外,`_pitfalls_stage` 是「不需要筆記庫」的路徑,收的是檔案路徑而不是節點。spec 沒說嚴格讀法要吃原始文字、不依賴 `Env`,也沒說在沒有筆記庫的情況下怎麼讀。
佐證:
- file: `scripts/lumos:42891`(`_pitfalls_stage` 只讀檔案文字,JSON 只輸出 stage 與 facets)
- file: `scripts/test_lumos.py:56040`

**6.**
severity: major
blocking: 是
spec 段落:〈三個消費端〉lint「條款那邊取條款綁定(`clause_bindings`)每一列認得的測試名」。
引句:「條款那邊取條款綁定(`clause_bindings`)每一列認得的測試名」
問題:`clause_bindings(text, split, default, methods_for, hay_for)` 要先建「平台測試索引」,也就是掃整個 repo 的測試檔。lint 的設計是單檔快檢、不掃 repo,而且 doctor 會對全圖每一篇都跑 `_lint_new_rules`。
spec 沒回答三件事:
- 索引只在「有已驗題」時才建嗎?
- `Env.from_texts`(推送前讀提交樹的記憶體 Env)沒有磁碟檔時怎麼辦?
- 比對 `[test:]` 名字只需要解析引用,為何需要整個索引?

佐證:
- file: `scripts/lumos:7375`(`clause_bindings` 的簽名)
- file: `scripts/lumos:6840`(`_lint_new_rules` 只拿 `env` 與 `rel`)
- file: `scripts/lumos:6497`(`cmd_lint` 的 docstring 寫「node-local,不掃 repo」)

**7.**
severity: major
blocking: 是
spec 段落:〈三個消費端〉規格閘與 lint 的分工,以及 S1/S3。
引句:「標不可逆不得自答、標阻塞不得延後」
問題:守衛有繞道。規格閘只擋「阻塞 + 需求/架構 + 待查/待人」。`question-set <計劃> Q1 status=延後 reason=…` 對阻塞題來說,指令的「必附」檢查是齊的(有 reason),規格閘也放行。「標阻塞不得延後」「不可逆不得自答」只在 lint 檢查,而 lint 新規則預設只提醒不擋(`note_lint.gate` 預設 warn)。
後果:一句 `status=延後` 就能繞過規格閘,而 spec 在〈實務隱患〉聲稱「誤擋會訓練人繞過」,卻沒顧到這條直通的繞道。
建議:指令寫入時就拒絕(S3),或規格閘把「阻塞 + 延後」也算擋。
佐證:
- file: `scripts/lumos:6776`(`note_lint.gate` 預設 warn;本 repo 設 on,消費專案預設 warn)

**8.**
severity: major
blocking: 是
spec 段落:〈舊寫法〉與要求的「7 題遷移怎麼驗」。
引句:「這次用新指令重建、正文那一節改成指向開頭欄位的一句話」
問題:遷移只說「用新指令重建」,沒有驗收方式。實際有四個坑:
- `question-add` 沒有 `--id`,只會「最大號加 1」。原計劃正文的順序是 Q1、Q2、Q3、Q4、Q6、Q7、Q5,必須照編號順序呼叫才能保住編號。
- 7 題裡的資料有長文,例如 Q3、Q4 的 `source` 含全形標點、`——`、括號和 `[[連結]]`,這是第一個真實輸入,spec 沒指定拿它們當圓整往返(round-trip)測試。
- 四個已決題要指向 `#d5/#d6/#d8/#d9`。我查過這四條現在都有效,但 spec 沒要求遷移後跑 `lint`,也沒要求前後逐題比對(id、階段、狀態、阻塞、決策)。
- 沒有說明遷移完成後正文那句指路,以及其他筆記引用「原計劃 Q7」等字樣要不要同步。

建議:寫成 `t_qfm_*` 之外的一次性核對步驟——7 題逐題比對、`lint` 無錯、`spec-gate` 與 `pitfalls --stage` 在原計劃上的輸出符合預期。

---

**9.**
severity: minor
blocking: 否
spec 段落:S1–S6 的測試覆蓋。
引句:「阻塞在前、不可逆其次、同級照編號、不截斷」
問題:行為都寫得進會翻紅的測試,但以下行為沒有條款守:
- 兩個程序併發 `question-add`(第 1 條)。
- 值的圓整往返:含 `:`、`#`、引號、`true`、純數字的 `text`,以及 `[[節點]]#dN` 這種跨篇決策連結(第 2 條)。
- `pending_questions: []` 這個合法空清單,以及欄位不存在與空清單的行為是否一致(S6 只比「不存在」)。
- 編號排序:`同級照編號` 要用數值比,否則 Q10 會排在 Q2 前面。
- 現有清單本身讀不懂時,`question-add`/`question-set` 拒不拒寫(spec 沒寫,和「不提供刪題、靠編輯器」是同一條路,應明說)。
- CRLF 與 BOM 的檔案:逐行讀法下每行尾多一個 `\r`,可能整份被判讀不懂。
- S2 一條測試塞了十種讀不懂,翻紅時只知道有一種沒擋,應該每種獨立斷言。

**10.**
severity: minor
blocking: 否
spec 段落:S1 與〈三個消費端〉。
引句:「只看狀態,不查決策存不存在(那是 lint 的事)。」
問題:擋法只在 `lumos spec-gate` 當下生效。
- 規格閘的留痕用條款區塊的指紋判新舊,與開頭欄位無關。計劃通過後再新增阻塞題,推送閘不會因此變紅。
- 處置閘第五步(共用條款檢查器)與設計迴圈 pass 也不看這個欄位。
- `decision-add` 之後沒有提醒「對應的待決題還沒改成已決」。擋是寧可多擋的方向,但會留下過期的阻塞題。

**11.**
severity: minor
blocking: 否
spec 段落:〈實務隱患〉「資料相容」與〈回退〉。
引句:「舊版 lumos 讀到這個欄位會當成不認得的開頭欄位,照它既有的處理(不擋)」
問題:回退後,每篇帶這個欄位的計劃,在舊版 lint 會多一條「沒見過的鍵」提醒(實測會出現)。spec 說「舊版當不認得的欄位忽略」是對的,但漏了這條噪音。本 repo 的 gate 是 on,仍然只是警告,不擋。

**12.**
severity: minor
blocking: 否
spec 段落:〈指令〉與「寫入前先驗…」。
引句:「寫入前先驗這一題改完是否讀得懂、必附是否齊,不齊就不寫並說缺什麼。」
問題:兩處小不一致。
- `question-set` 只驗「必附齊」,不驗「阻塞不得延後」「不可逆不得自答」,指令放行的狀態 lint 之後才報(與第 7 條同源)。
- 沒說 `question-add`/`question-set` 要不要同步更新計劃的 `updated`。`decision-add` 不更新,`decision-supersede` 會,規則不一致。

**13.**
severity: minor
blocking: 否
spec 段落:〈資料放哪〉「錯誤訊息的欄位名改成可傳入」。
引句:「錯誤訊息的欄位名改成可傳入」
問題:與現況不符,對象指錯了。`_yaml_quote(v, what)` 已經接受欄位名,寫死「決策內容」的是 `_fmt_decision_value`。spec 的〈順手處理〉另提 `PQ_STAGES` 改名,沒提這個函式。

**14.**
severity: minor
blocking: 否
spec 段落:技能與指令索引,spec 沒提。
引句:「不提供刪題:題目改成延後(附理由)或已決」
問題:
- 新增兩個頂層子指令後,`t_command_index_complete` 要求 `skills/lumos-project-notes/commands/*.md` 提到它們。`INDEX.md` 現在是 4498 字,上限 4500,只剩 2 個字元,新列只能放到分冊,不能放 INDEX。
- `t_every_subcommand_has_when` 要求每個子指令的 `--help` 第一段有「什麼時候用:」。
- 指令一句話表(`scripts/lumos` 約 50572 行那份)要補兩條。

這些測試會在實作時擋住,但 spec 的同步清單沒列。

## 實務隱患逐類
- 守衛面:有隱患。誤擋與繞道見第 2、7、9 條。
- 資料相容:有隱患。見第 3、11 條。
- 並行會談:有隱患。見第 1 條。
- 不可逆:有隱患。spec 的〈不可逆〉說「壞了用 git 還原」,但回退後殘留的清單和條款綁定怎麼收尾沒寫(第 3 條)。
- 金流、對外送出:無。本功能只改本機筆記,不碰付款或外部服務。

總結:最嚴重 major;blocking 共 8 條。
