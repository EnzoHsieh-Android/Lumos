severity: major

## 逐節

先講結論:程式碼現況我都對過。spec 對 `fm_structure`、`parse_decisions`、`_KNOWN_FRONTMATTER_KEYS` 的描述大致屬實。真正的問題在三處:嚴格讀法的文法沒寫死、兩支指令照「決策紀錄那一套」會繼承現有缺陷、規格閘擋不住的繞法。下面逐條列。

---

severity: major
blocking: 是

**〈資料放哪、長怎樣〉對〈指令〉:共用的格式化函式會把 `blocking: true` 寫成 `blocking: "true"`。**

引句:「值的引號與跳脫用同一支格式化函式」

原句的完整位置:〈資料放哪、長怎樣〉最後一條。YAML 範例裡寫的是裸的 `blocking: true`、`irreversible: false`。

我用 `_fmt_decision_value` 實測,輸出如下:
- `'true'` 變成 `"true"`
- `'false'` 變成 `"false"`
- `'12'` 變成 `"12"`

原因是 `_yaml_plain_ok` 把 true/false/null/yes/no 一律排除。

spec 沒說嚴格讀法收不收 `"true"`。兩種讀法都出事:
- 不收:`question-add --blocking` 寫出的檔,自己的嚴格讀法驗證不過。S3 的寫入永遠失敗。
- 收:`"true"` 在 Obsidian 的 YAML 裡是字串,不是布林。「只收 true/false」這條就跟標準 YAML 不一致。

實作者得自己猜。

另外,`_yaml_quote` 對含換行的值也不擋。`'a\nb'` 會被包進雙引號,檔案裡多出一行。這時嚴格讀法驗證才失敗,錯誤訊息是「讀不懂」,不是「問題文字不能換行」。`question-add` 的 `<問題>` 是命令列參數,換行很容易出現。

佐證:
- file: `scripts/lumos:19224` 到 `19232`(`_yaml_plain_ok` 的 true/false 排除)
- file: `scripts/lumos:20332`(`_fmt_decision_value`)

---

severity: major
blocking: 是

**〈讀法〉:「每一行必須認得」的文法有五處沒寫死。** 照字面實作會有人 fail-open,也有人誤擋。

引句:「範圍自己掃:從頂格的 `pending_questions:` 那行開始」

引句:「頂格的清單項、`pending_questions:` 後面直接接值(`[]` 除外)」

原句位置:〈讀法〉第一條,「新的一題(`  - id: Q<n>`)或這一題的一個鍵(比那一題更深一層的 `鍵: 值`)」。

1. **縮排深度。**
   - 「更深一層」是剛好 4 格,還是任何比 dash 深的?
   - 同一題裡鍵的縮排不一致要不要擋?
   - 清單項固定是 2 格嗎?現有的 `decisions_items` 是從第一個 dash 推縮排。
2. **`pending_questions: []` 後面又接題目行。**
   - spec 只說「後面直接接值(`[]` 除外)算讀不懂」。
   - 但 `[]` 後面接 `  - id: Q1` 這種組合,spec 沒講。
   - 寬鬆的 `parse_frontmatter` 遇到 `[]` 就把欄位當空清單,後面的行整個丟掉(`scripts/lumos:625` 到 `628`)。
   - 嚴格讀法若沿用「`[]` 除外」,這時會判成「零題」,等於 fail-open。
3. **欄位存在但沒有任何題。** `pending_questions:` 後面什麼都沒有,算零題還是讀不懂?空清單在 S6 算不算「欄位不存在」?
4. **註解行與行尾註解。**
   - `  # 備註` 和 `status: 待人 # 註` 都沒講。
   - 前者「其他一律算讀不懂」,結果大概是對的,但沒明寫。
   - 後者在標準 YAML 裡會被當註解切掉,嚴格讀法會把 `# 註` 當成值的一部分。
   - 頂格註解落在範圍內也是同理。
5. **引號值的讀法。**
   - 「值夾了讀不懂的引號」沒定義什麼算讀得懂。
   - 若實作者沿用 `strip_quotes`(只剝頭尾、不驗內部),`"say \"hi\""` 會被當合法。
   - 格式化函式明明只產出「單一種引號、內部沒有同種引號」。
   - 這句要寫成一條機械規則。

另外:
- 「新的一題」限定第一個鍵必須是 `id:`。YAML 合法但 `id` 不在最前的寫法,會被當成讀不懂。這是 fail-closed,可接受,但要明講。
- 多行值(`text: |`)會被讀成 `text: "|"`,下一行才報錯。要明列「`|` `>` 開頭的值直接算讀不懂」。

佐證:
- file: `scripts/lumos:19168`(`fm_structure`)
- file: `scripts/lumos:19221` 到 `19230`(`[]` 的特例)
- file: `scripts/lumos:618` 到 `628`(`parse_frontmatter` 的 `[]` 處理)

---

severity: major
blocking: 是

**〈指令〉對〈資料相容〉:`question-add` 在 `pending_questions: []` 上會失敗,而 spec 把 `[]` 列為合法。**

引句:「寫法照決策紀錄那一套(`cmd_decision_add` 加 `atomic_write_verify`)」

我實測 `decisions: []` 加 `decision-add`,結果是:

    擋下:寫完讀回來檢查,decisions 的值跟要寫的不一樣,這次寫入不算成功

原因是 `decisions_items` 把 `[]` 當成長度 1 的 list 區塊,新項目插在 `decisions: []` 之後,變成不合法的 YAML。

spec 一邊說 `[]` 合法,一邊說照決策紀錄的寫法,卻沒寫「遇到 `[]` 要先把那一行改成 `pending_questions:`」。新欄位的第一題也沒說插在哪(`decisions` 是接在 fm 末尾)。

佐證:
- file: `scripts/lumos:20439` 到 `20470`(`cmd_decision_add`)
- file: `scripts/lumos:19415`(`decisions_items`)

---

severity: major
blocking: 是

**〈指令〉對〈回退〉與〈實務隱患〉:`question-add` 的「最大號加 1」沒有寫入鎖,同時多個會談會寫出重複編號。重複編號在新設計下會讓整份清單卡死。**

引句:「給下一個編號(現有最大號加 1),回印全域編號」

引句:「用嚴格讀法驗過整份清單讀得懂、且這一題內容相符才寫檔,沒過就不寫」

引句:「不可逆:寫入走改哪行動哪行、寫完重讀、失敗還原,壞了用 git 還原」

我用 6 個程序同時對同一篇跑 `decision-add`:

    id: d1、id: d2

最後只剩 2 條(丟失更新)。

原因有兩個:
- dispatcher 對 `decision-add` 不上 `_vault_write_lock`。`set`、`append` 才有鎖(`scripts/lumos:19697`)。
- `atomic_write_verify` 的檔頭註解自己承認「其他寫入指令仍是 last-write-wins」。

spec 要求「現有最大號加 1」,又是讀、改、寫三步,而且寫入前驗證是在記憶體裡用舊內容做的。兩個會談算出同一個 `Q4`,或後寫的蓋掉先寫的,都會發生。

- 前者:嚴格讀法判「編號重複」,規格閘對該計劃全部回 1。這是新設計自己造出來的卡死。
- 後者:題目無聲消失。

CLAUDE.md 明寫同 repo 可能有並行會談。

另外有一處前後不一致:
- 〈做法〉說「寫檔前先在記憶體組好…驗過…才寫檔」。這是寫前驗證,現有 `atomic_write_verify` 就是這樣做的。
- S3 說「重讀確認後才回 0」。
- 〈實務隱患〉說「寫完重讀、失敗還原」。現有機制沒有寫後重讀,也沒有還原。

實作者無法判斷要做哪一種。

佐證:
- file: `scripts/lumos:52377` 到 `52420`(decision-add 的 dispatcher,沒有上鎖)
- file: `scripts/lumos:19473` 到 `19480`(`_write_lf` 的併發註解)
- file: `scripts/lumos:19501`(`atomic_write_verify`)

---

severity: major
blocking: 是

**〈三個消費端〉與〈指令〉:規格閘只看狀態,而「不得延後」、「不得自答」只在 lint 檢查。lint 預設還是 warn,所以一行指令就能繞過規格閘。**

引句:「只看狀態,不查決策存不存在(那是 lint 的事)」

引句:「寫入前先驗這一題改完是否讀得懂、必附是否齊」

繞法有三條:
- 阻塞題 `status=延後 reason=x`。spec 說「標阻塞不得延後」,但寫入端只驗「延後要有 reason」,所以過關。規格閘不擋延後,放行。
- `status=已決 decision=#d99`。寫入只驗「有給 decision」,規格閘不查是否存在,放行。
- 阻塞又不可逆的題 `status=自答 source=x`。寫入端同樣不擋「標不可逆不得自答」。

這些只有 `lumos lint` 會報。本 repo 的 `note_lint.gate` 是 warn(實測 lint 輸出寫「先提醒不擋」),設成 off 則完全不跑。

這與 spec 自己的守衛面邏輯矛盾:守衛面強調要避免誤擋,但真正想擋的組合,AI 一個指令就能讓規格閘變綠。

至少要把「阻塞題不得延後、不可逆不得自答、`decision` 必須指到存在且有效的決策」放進 `question-set` / `question-add` 的寫入前驗證。或者讓規格閘對這幾種組合也回 1。

佐證:
- file: `scripts/lumos:6523` 到 `6528`(lint 新規則在 warn 模式下只是警告)
- file: `scripts/lumos:6840`(`_lint_new_rules`)

---

severity: major
blocking: 是

**〈三個消費端〉:跨篇決策連結寫成 `[[節點]]#dN`,但 repo 現有的全域決策編號是 `<節點路徑>.md#dN`,spec 也沒定義如何解析。**

引句:「指到存在且有效的決策(可跨篇 `[[節點]]#dN`)」

我實測 `decision-add` 印出的是 `全域編號 Projects/b_計劃.md#d1`。repo 內既有的解析是 `re.fullmatch(r"(.+?)#(d\d+)", s)` 加 `env.resolve`,另有 `_dref_norm` 做正規化。

spec 既沒說沿用這套,也沒說如何解析下列寫法:
- `[[X|別名]]#d1`
- `[[X#d1]]`
- 帶不帶 `.md`
- 短名撞名

使用者會把 `decision-add` 印出的全域編號直接貼進 `--decision`,而那不是 spec 的格式。

〈外部做法〉聲稱「借用決策紀錄那個模式」,連結格式卻自創一套。

另外,`question-add` 印的 `<計劃>#Q<n>` 沒說 `<計劃>` 是檔名、節點名還是 `.md` 路徑。

佐證:
- file: `scripts/lumos:2851` 到 `2858`(E3 的解析)
- file: `scripts/lumos:20740`(`_dref_same`、`_dref_norm`)

---

severity: minor
blocking: 否

**〈三個消費端〉:`tests` 比對。**

引句:「題目的 `tests` 照原字串比對(含平台前綴)」

- 條款一側取的是 `invariant_test_refs` 回的原字串。比對的方向是一致的,但沒說 `t_x` 和 `py:t_x` 不等價。`resolve_test_refs` 會把無前綴的歸到預設平台,所以兩者其實指同一支測試,卻會被報「不在本篇條款」。
- 「每一列認得的測試名」沒說要看列的狀態。`dangling`(檔裡沒有這支測試)、`bad-name` 的 `refs` 也在列裡。已驗的測試名只要出現在任何一條條款的 `[test:]` 就過,不要求測試存在或已綁定。
- `tests` 用半形逗號切。沒定義:空元素、尾端逗號、重複、前後空白。含逗號的測試名(參數化名稱)會被切壞。
- 條款綁定是對整份 `text` 算(含 frontmatter)。這裡沒出問題,因為子鍵行不是行首的 `[SN]`,但 spec 沒說明。

佐證:
- file: `scripts/lumos:5901` 到 `5935`(`invariant_test_refs`、`resolve_test_refs`)
- file: `scripts/lumos:7375`(`clause_bindings`)

---

severity: minor
blocking: 否

**〈指令〉`question-set <鍵>=<值>` 切分與鍵的邊界。**

引句:「一次可改好幾個鍵(例如 `status=已決 decision=#d3`)」

- 值含 `=` 時要說「只切第一個 `=`」。
- `tests=t_a, t_b` 沒加引號時,shell 會切成兩個參數。第二個沒有 `=`,是報錯還是併入,要寫明。
- 沒說能不能改 `id`。照「只收這幾個鍵」字面,`id=Q9` 會被接受,編號就亂了。
- 沒有清掉選填鍵的辦法。`decision=` 空值要不要允許,也沒定義。
- 選填鍵不存在時要插在哪一行,沒寫。
- `--decision #d3` 在互動式 bash 裡會被當註解截掉(`interactive_comments` 預設開啟)。範例用 `decision=#d3` 不受影響,但 `question-add --decision #d3` 受影響。

---

severity: minor
blocking: 否

**〈指令〉:編號可重用,與決策紀錄的「永不重用」合約相反。**

引句:「不提供刪題:題目改成延後(附理由)或已決;真的寫錯就用編輯器刪」

spec 說題目寫錯就用編輯器刪,而新號是「現有最大號加 1」。刪掉最後一題後,下一題會重用同一個 `Q<n>`。

`_max_decision_id` 的文件明寫:「翻案後永不重用」。`question-add` 又會回印全域編號給人貼到別處。

另外:
- `Q01` 和 `Q1` 的重複判定看字串還是看數值,沒定義。
- 排序要明講用數值(`Q10` 不能排在 `Q2` 前面)。

佐證:
- file: `scripts/lumos:20428`(`_max_decision_id`)

---

severity: minor
blocking: 否

**〈三個消費端〉頂格鍵的拼寫變體會被靜默略過。**

引句:「當計劃沒有 `pending_questions` 欄位時,規格閘、lint、`pitfalls --stage` 的判定與輸出應跟現行相同」

嚴格讀法只認字面的頂格 `pending_questions:`。下列寫法在 YAML 合法或常見,但全部會被當成「沒有這個欄位」,也就是 fail-open:
- `pending_questions :`(冒號前有空格)
- `"pending_questions":`
- `pending_question:`(少一個 s)

S6 還明定「沒有欄位 = 跟現行相同」。只有 lint 的「沒見過的鍵」軟提醒會提到(`scripts/lumos:6570` 到 `6577`),規格閘不會。spec 的「寧可擋」只管欄位內部。

---

severity: minor
blocking: 否

**〈三個消費端〉`pitfalls --stage` 的 `--json` 與無法判定時的輸出沒寫。**

引句:「清單無法判定時不列題,印原因並回 2」

- 現有 JSON 只輸出 `{stage, facets}`,測試 `t_backend_qo_stage_facets_only` ③ 還釘死 key 集合。有欄位時 JSON 要不要加題目?沒有欄位時必須保持原樣(S6)。
- 清單無法判定時:要不要先印需求風險面再報錯?文字上寫「不列題,印原因並回 2」,但 `_pitfalls_stage` 在 JSON 分支會提早 return,錯誤路徑放在哪都沒定。
- lint 的「行號」是相對於 frontmatter 的行號,還是檔案行號,沒說。

佐證:
- file: `scripts/lumos:42891` 到 `42921`(`_pitfalls_stage`)

---

severity: minor
blocking: 否

**〈舊寫法〉重建現有 7 題時,`question-add` 沒有指定編號的辦法。**

引句:「用新指令重建、正文那一節改成指向開頭欄位的一句話」

後端那份計劃的正文順序是 Q1、Q2、Q3、Q4、Q6、Q7、Q5。正文第 196 行和第 255 行引用了 Q3、Q4。`question-add` 只給「最大號加 1」,所以只有按數字順序 Q1 到 Q7 加進去才能保住編號。spec 沒寫這個要求,照檔案順序加會把 Q5、Q6、Q7 的編號全部改掉。

佐證:
- file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:242` 到 `248`

---

severity: minor
blocking: 否

**一個與程式碼不符的小宣稱與兩處落點問題。**

引句:「lint 規則只拿到開頭欄位,正文用既有的 `env_text` 讀」

- 「lint 規則只拿到開頭欄位」不準:`_lint_new_rules(env, rel)` 拿得到 `env` 和 Note(含 `fm_lines`),不需要特別繞。
- `lands_in` 列了 `Systems/情境出題`,但該節點 responsibility 寫明「不負責〈待決問題〉的資料格式與擋法」。
- S5 改的是 `pitfalls --stage`,它的家 `Systems/pitfalls-code-loop`(第 210 到 213 行有 REVISIT)沒列進 `lands_in`。
- 兩支新指令和 lint 規則的落點也沒指定。

---

## 固定席逐條判

**Systems/規格閘**(20 行 KEY,無合約行)

- 「條款判定同源」(`_clause_check` 與處置閘第五步共用):不影響。新檢查放在 `_spec_gate_front` 判門之後、`_spec_gate_clause_part` 之前,沒碰 `_clause_check`。
- 「風險高半套:紅綠只印不擋」:不影響這條,它講的是測試紅綠。但新擋法不分風險高低都回 1,節點應補一行寫明。
- 留痕與 `spec-gate-run` 帳(只在「跑完沒被擋下」才寫):不影響。新擋法在跑測試之前就回 1,不寫帳,與既有語意一致。
- `--push-check`(推送前路徑):沒影響,但新擋法也不在 pre-push 路徑上。`_spec_gate_front` 的唯一呼叫點是 `cmd_spec_gate`(`scripts/lumos:7810`),所以只有手動 `lumos spec-gate` 會擋,spec 沒說這是設計。
- 「規格閘不讀正文〈待決問題〉」的 WHY 與測試 `t_backend_qo_question_section_not_parsed`:S2 的「正文怎麼寫都不影響」跟它相容。

**Systems/情境出題**(0 條合約)

- 不影響評分器與盲評包:只動 `scripts/lumos`,沒動 `qo_ablation.py`。
- 責任範圍有衝突,見上面的 `lands_in` 問題。

## 實務隱患鏡頭

- 併發與共用寫入:有隱患,見 `question-add` 的鎖與編號問題(major)。
- 守衛面:有隱患,見規格閘繞法(major)。
- 資料相容:無隱患。舊版對未知鍵只給軟提醒,已實測。
- 金流、對外送出:無,spec 的排除理由成立。
- 不可逆:spec 稱「失敗還原」,但實際機制是寫前驗證,沒有還原。這個說法不成立,但實際風險小(失敗即不寫)。

總結:最嚴重 major;blocking 共 6 條。
