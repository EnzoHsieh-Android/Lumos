severity: major

審查對象是 /tmp/tags/r1.md,對照 repo 為 scratchpad 的 `rw`(下文路徑都相對於它)。固定席筆記我沒收到 hook 附尾,自己讀了 `Systems/存量漂移守衛`、`Systems/hook信任邊界`、`Systems/棧別提問表態閘`、`Systems/筆記內容閘` 四篇,判斷放在最後。

一句人話:這份設計把「擋推送」「教 AI 怎麼寫」「搜尋」三個出口都接在既有零件上,但實際去看,有幾個出口根本沒有線可接。教 AI 的主要管道不會觸發;擋推送沒有任何入口;幾條擋的規則(W6、`[count:]` 的正則)照字面做會誤擋或解析失敗。

**I1 教 AI 的主要管道不存在:impact-hook 不會在改筆記時觸發**
severity: major
blocking: 是 — 照字面實作,速查表不會出現在任何改筆記的時刻,S17 的測試要嘛寫不出來,要嘛測到別的東西。
- 輸入:AI 對 `docs/*-knowledge/*.md` 做 Edit 或 Write。
- 走到:`impact-hook.py` 的 `_decide_one` 先檢查副檔名。`.md` 不在 `CODE_EXTS`,直接回 None。
- 另外 `EXCLUDE_PATH_CONTAINS` 明列 `"/docs/"`,圖譜本身被排除。
- 現有的「棧別檢核題」是改程式檔時才附,不是改筆記時。spec 說「現在已經會附」,指的是改程式檔的情境。
- 要做到 spec 說的事,得新增「筆記路徑」分支,連同冷卻窗、Codex 的 `apply_patch` 路徑和注入框的守衛測試一起改。spec 沒提到這些。
- 引句:「AI 要改一篇筆記時,既有的改檔前提示 hook(impact-hook,現在已經會附棧別檢核題)多附一張六行的速查表」
- 佐證:`scripts/hooks/claude/impact-hook.py:32`、`scripts/hooks/claude/impact-hook.py:49`、`scripts/hooks/claude/impact-hook.py:147`

**I2 擋推送沒有入口:沒說接哪個子指令、哪個掛鉤、哪個 CI 步驟**
severity: major
blocking: 是 — 這些擋(S3 到 S9、S20)沒有任何呼叫端,做出來的是跑不到的函式。
- spec 說「沿用 note-shape 的上線點截斷」,但上線點不是設定,而是 pre-commit 掛鉤文字裡有沒有 `note-shape --staged` 這串字(`_NOTE_SHAPE_GOLIVE_MARK`,用 `git log -S` 找第一次出現)。
- `note_tags` 要自己的標記字串,或明講併進 `note-shape`。spec 兩個都沒講。
- 現有每道閘都有三個接點:pre-commit(`scripts/hooks/pre-commit`)、pre-push(`scripts/hooks/pre-push`)、`.github/workflows/ci.yml` 一步。
- 消費專案的 CI 還要靠 `doctor` 印出步驟讓人貼(`scripts/lumos:25709`)。
- spec 的〈分期〉沒有任何一步改這三處或 doctor,也沒說擋推送是新子指令,還是擴 `note-shape` 的 `_note_shape_eval`。
- 〈實務隱患〉說「這些擋都是新的推送閘」,但沒說閘在哪。
- 引句:「寫法規則只看上線點之後新增的行(沿用 note-shape 的上線點截斷);欄位判過時只看帶欄位的行,而欄位只會出現在新行上。」
- 佐證:`scripts/hooks/pre-commit:227`、`scripts/lumos:24851`、`scripts/lumos:24330`、`.github/workflows/ci.yml:127`

**I3 W4/S11 沒有被開關管,違反「舊專案行為完全不變」,而且 lint 是整篇判、不分新舊行**
severity: major
blocking: 是 — 步驟 0 一上線,所有已接入專案的提交都會開始印 RULE 提醒。這跟原則 4、S1、〈相容〉互相矛盾,〈回退〉說的 off 也停不掉它。
- W4 排在步驟 0,明寫「不等本案其他部分」,所以不在 `note_tags.gate` 底下。
- S1 的範圍只寫「新欄位的擋與提醒」。RULE 的 since/retire 不是新欄位,字面上不受 S1 管。
- pre-commit 的 Gate L 現在只在 lint 失敗時才印輸出。
- 要「印出」就得改掛鉤,而且 `lumos lint <篇>` 是整篇、整個 summary 判(`context_marker_warnings` 吃整段 summary)。
- S11 要的是「只對新寫的 RULE 行」,所以得改走 `_notelines_new` 那條新增行路徑。
- 否則舊 RULE 行(本庫 18 條,rtb 與其他專案也有)會在每次碰那篇時一起噴。
- 引句:「提交時對新寫的 RULE 行印出缺 since/retire、until 過期這類提醒(目前 lint 有算、但提交時不印)」
- 佐證:`scripts/hooks/pre-commit:188`、`scripts/lumos:3314`、`scripts/lumos:3370`

**I4 W6「同一行重複事實」的判準會大量誤擋,而且 CI 沒有逃生口**
severity: major
blocking: 是 — 新接入專案是 block 模式,正常寫的脈絡行會被擋,而 CI 不認單次跳過。
- 輸入:任何帶 `[count:…=1]` 或 `=2` 的 WHY/RULE 行,正文寫了「一律」「一個」「兩邊」。
- 「中文數字都算」,而「一」「二」「三」「兩」是中文最常見的虛詞和量詞,這行會被判重複事實。
- 阿拉伯數字同理:`v1`、`4090`、路徑裡的 `s3`、序號都會撞上欄位值。
- 日期也算,而 WHY 規定要有出處日期,RULE 常同時寫 `[since:D]` 與正文裡的事件日期。
- spec 沒說「欄位」是指 v1 的六類,還是也含 `since/confirmed/until`。
- 後果:寫的人被迫刪掉正文裡正當的出處日期。
- 逃生口只有 `LUMOS_SKIP_*` 單次跳過,而 CI 照擋(〈自我治理〉自己寫的),所以只能改寫句子。
- 引句:「同一行裡,欄位的值(數量、字面值、日期)在欄位外又出現一次——阿拉伯數字或中文數字都算——就擋」
- 佐證:`scripts/lumos:25387`(現有欄位清單與遮罩只認舊鍵,說明新鍵得整批補)

**I5 `[count:N re=… in=…]` 的方括號寫法碰到 `]` 就壞,而且「同一個重算器」目前不存在**
severity: major
blocking: 是 — S4 與合約候選第 2 條要求兩種寫法共用一個重算器,現有碼做不到,正則寫法照字面做會解析錯。
- 輸入:正則帶字元集,例如 `re=[A-Z]+Handler`,或 glob 帶 `[ab]`。
- 現有 RULE 欄位解析就是這樣壞的:值裡出現 `]` 會被截斷,碼裡專門有 `rule_field_truncated` 補唸(`scripts/lumos:3300`)。
- 而 doctor N 的 HTML 註解寫法 `<!--lumos:count=N re=(.+?) in=-->` 沒這問題。
- spec 要把正則塞進 `[...]`,卻沒處理這件事,也沒說 `[value:…=字面值]` 遇到 `=[1,2]` 怎麼辦。
- doctor N 的重算邏輯是直接寫在 `cmd_doctor` 內的內嵌程式(`scripts/lumos:3017` 到 `scripts/lumos:3059`),不是函式。
- 它每個標記各做一次全 repo 的 `os.walk`,上限是每個標記 4000 檔、40MB。
- 要「同一個重算器」得先抽成函式,spec 的〈分期〉沒列。
- 推送前每個 `[count:re]` 欄位都 walk 一遍整個 repo,也沒有時間預算。這和 `drift` 閘用的 `_DRIFT_BUDGET_SEC` 預算機制不同。
- 引句:「正則寫法跟 doctor N 段的 HTML 註解標記同一個重算器」
- 佐證:`scripts/lumos:3017`、`scripts/lumos:3059`

**I6 ①②的「讀名稱的成員數、常數值、列舉成員」沒有既有零件,PRIOR-ART 說全部接在既有上不成立**
severity: major
blocking: 是 — 這是 S3、S5 的核心判定,實作者得從零寫,卻被告知可沿用。
- 〈PRIOR-ART〉第 1 點說「本案每一項都接在這些上面,不另起求值器」。
- 現有 Python 抽取只收「名稱」:函式、類別、指派的目標名(`_drift_m1_assigns`、`_py_defs` 一帶,`scripts/lumos:28122`、`scripts/lumos:28133`)。
- 沒有任何地方讀指派的值、數集合成員,或把列舉的成員列出來。
- 表格自己也承認②是「新判定」,但 PRIOR-ART 沒承認。
- 另外 S5/②自己跟〈一個事實只寫一處〉衝突:要判「多或少」得有基準清單,spec 給兩條路。
- 一條是「寫欄位時記下當時的成員清單」,等於把程式事實(列舉成員)複製進欄位。
- 另一條是「句中反引號名稱」,等於要求正文複述成員,違反宗旨和 W2。
- 而且任何無關的反引號識別字(例如 `MODEL_VARS`、函式名)都會被當成成員比對,誤報。
- 引句:「寫欄位時記下當時的成員清單(或句中反引號名稱),跟現在的列舉成員兩邊比,多或少 → 擋」
- 佐證:`scripts/lumos:28122`

**I7 ⑥ `[lives:]`「名稱本體自這行寫下後變了」沒有基準,回頭重讀的候選規則也接不上**
severity: major
blocking: 是 — S9 後半(只列候選、不擋)照字面做不出來。
- 「自這行寫下後」需要基準:要嘛欄位帶指紋(spec 沒設計),要嘛逐行 `git log -S`/blame 追行的寫入提交。spec 兩個都沒講。
- 回頭重讀的候選規則是 `cands = homed & touched_rel`。
- 條件是這篇筆記是範圍內改到的程式檔的「家」(`about_code`),而且這篇筆記在範圍內被碰過。
- 筆記的 `[lives:路徑::名稱]` 指向不是它家的檔、或筆記這次沒被改,都不會成為候選。
- 而「節點只准用反引號寫自己家的檔」的家規,會讓 lives 指向別人檔案成為常態。
- 回頭重讀本身是 LLM 判定者流程(prepare/record、判定紀錄檔),不是可直接「列進去」的清單。
- 引句:「名稱本體自這行寫下後變了 → 列進回頭重讀候選、只提醒」
- 佐證:`scripts/lumos:26971`、`scripts/lumos:26927`

**I8 ③撤除條件「沿用回頭條件探針、成立 → 擋」:探針只認 REVISIT 行,而且判的是「這次推送由不成立變成立」**
severity: major
blocking: 是 — 狀態式(成立就擋)與轉變式(翻成立才擋)是兩種閘,S6 與表格寫成一種,實作者會挑錯。
- `_probe_lines` 只收 `REVISIT:` 行的條件(靠 `_revisit_split`)。RULE 行上的 `[retire-when-*]` 要另寫一條解析與候選路徑。
- `_drift_probe_judge` 的語意是「終點成立、而起點沒有同一條或同一條還不成立」才要處理;起點早就成立就不列。
- 所以規則寫成時條件就已經成立,或條件早就成立後才補上欄位,探針都不會擋。這和 spec 的「成立 → 擋」不同。
- 另外,存量漂移守衛固定席 WHY 定下「判不了算要處理」。spec 對 `[count:]`、`[retire-when-*]`、`[lives:]` 讀不到檔、非字面清單、git 失敗時是擋還是放行,一個字都沒講。〈天花板〉5 只說「認不出來就提示」。
- 引句:「沿用回頭條件探針求值;成立 → 擋;`[expect:]` 指的名稱不在那支檔,條件不算成立」
- 佐證:`scripts/lumos:28062`、`scripts/lumos:28630`、`scripts/lumos:27919`

**I9 ⑤快照:不知道擋在哪一層,「現況類小節」沒定義,而且前案說這個形狀不固定**
severity: major
blocking: 是 — S8 寫「轉狀態應被擋」,〈實務隱患〉寫成推送閘;兩個位置做出來是兩個不同的系統。
- `lumos set` 本體(`_cmd_set_locked`)完全不讀 `.lumos/config.json`,也沒有任何轉 done 的閘。把閘放這裡要新增設定讀取,而且手動改 frontmatter 就繞過。
- 放推送閘則要偵測「這段推送讓 status 變 done」,spec 沒說。
- 「現況類小節」是靠標題字樣、還是靠什麼判斷,沒定義。
- `Projects/筆記形狀擋_計劃` 第 97 行已明寫「done 計劃的現況段,形狀都不固定」,所以才被排除在第一層之外。spec 沒回應這點。
- 引句:「計劃轉 done 時,現況類小節沒有 snapshot → 擋」
- 佐證:`scripts/lumos:15271`、`docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:97`

**I10 S19 / 教法驗收的量法跟現有情境探針對不上**
severity: major
blocking: 是 — 驗收條款 S19 與〈怎麼驗 AI 真的會寫〉量不出它說要量的東西,而它是「第一次答對率低於一半就先改速查表」的觸發條件。
- `scenario_probe.py` 的判準是工具呼叫序列,用 `expect` 正則比對。
- 對 Edit/Write 只保留 `file_path pattern path` 的前 200 字,新寫入的內容根本不在比對字串裡。
- `answer_expect` 看的是最後一則回覆文字,不是寫進筆記的句子。
- 也沒有「答對率」這個欄位,只有每題過或不過。
- 每週是 `--sample N` 輪轉抽查,不保證某週有那三題。
- 探針是在臨時 clone 裡跑,那個 clone 的設定若沒有 `note_tags.gate`,I1 的速查表也不會出現。
- 引句:「看寫出來的句子有沒有帶對的欄位;答對率進每週評測紀錄」
- 佐證:`scripts/scenario_probe.py:78`、`scripts/scenario_probe.py:630`

**I11 步驟 0「照程式行為改」對 RULE 三欄那一條方向錯,而且 retire-when 取代 retire 會讓同一條規則有兩份說法**
severity: major
blocking: 是 — 照字面做會把所有專案常駐注入的紀律範本放寬,卻沒人決定要放寬。
- 現況第 4 點的第 3 件:紀律範本說 RULE 要三欄齊且半年內確認才有挑戰程式碼的效力,程式註解說兩欄。
- 註解自己寫著「見紀律範本第 3 條」,表示範本是被引用的政策來源,錯的是註解。
- 「照程式行為改」會把範本改成兩欄,等於拿掉範本講的「弱點補償」(近期確認)。
- 〈欄位不重複〉又宣告「`[retire-when-*]` 的 RULE 不必再寫 `[retire:]`,機器式那條就算數」。
- 這是改了「有挑戰程式碼效力」的條件,但範本第 28 行和第 42 行仍寫 `[retire:]` 必填。
- 範本會注入每個消費專案的 CLAUDE.md/AGENTS.md,再加上本庫 CLAUDE.md,至少三處要同步。
- S21 只改了 lint,範本沒列入要改。
- 範本已超過瘦身基線 1.5 倍(11485 bytes 對 7884),doctor 本來就在提醒。
- 引句:「四處文件矛盾照程式行為改;RETIRE-IF 加進摘要前綴表;W4。」
- 佐證:`scripts/templates/graph-discipline.md:28`、`scripts/templates/graph-discipline.md:42`、`scripts/lumos:3290`

**I12 `lumos search` 的入口指令跑不起來,三個過濾也沒考慮現有輸出路徑**
severity: major
blocking: 是 — skill 與 hook 要印的那條指令 `lumos search --about <檔> --prefix …` 會被 argparse 直接拒絕,因為沒給 term。
- `search` 的 `term` 是必填位置參數,而且命中判定是「行含這個詞」。
- 〈按需載入〉要的是「不給詞、只按檔與前綴篩」。要嘛 term 改可省略,要嘛規定給萬用詞,spec 都沒說。
- 現有輸出每篇最多印 8 行命中,其餘只印「還有 N 處」。要篩「這支檔所有還有效的 RULE/PITFALL」會被截斷。
- `--json` 沒有片段文字。
- ranked、`--legacy`、`--regex`、`--files-only` 是四條輸出路徑。三個過濾要接到哪幾條,spec 沒講。
- `--include-superseded` 已存在,意思是「含已作廢節點」(節點層)。S16 讓同名旗標同時管行層的 `[superseded-by:]` 與撤除成立,同一旗標有兩個範圍。
- `--top` 預設 0 代表不截斷,spec 寫「有 `--top` 上限」。
- 引句:「輸出沿用 search 現有的逐行片段格式,每行帶篇名;有 `--top` 上限。」
- 佐證:`scripts/lumos:40168`、`scripts/lumos:3996`、`scripts/lumos:40184`

**I13 ④取代鏈的錨點和成對檢查有未定義項**
severity: minor
blocking: 否 — 這是欄位語法的精度問題,實作者可以自行補完,不會造成錯誤行為,只是會各自發明。
- 「合約編號」在碼裡不存在:合約行(★INVARIANT★ 等)沒有編號,只有決策有 `id: d1`,`[id:]` 是新欄位。
- `[id:短名]` 的唯一範圍(全庫還是同一篇)沒定。
- 成對檢查要解析 `節點#錨` 的目標節點是否存在、改名後怎麼辦,也沒定。
- 被取代的舊決策或舊規則是舊行,要加 `[superseded-by:]` 就得改舊行,舊行一改就成了新行,要重新過所有新行規則(例如 W6)。這不是問題的核心,但值得一句。
- 引句:「錨可以是合約編號、決策編號或 `[id:]`」
- 佐證:`scripts/lumos:4170`

**I14 推播 hook「多印一行這個指令」含檔案路徑,跟 hook 信任邊界 RULE 的做法對不上**
severity: minor
blocking: 否 — 輸出可做成合規,spec 只是沒指明印在框內還是框外、路徑有沒有過消毒。
- `Systems/hook信任邊界` 的 RULE 定下:框內只放專案讀出來的值,工具寫死的指示放框外。
- `t_all_injection_paths_are_framed_and_unified` 與 AST 守衛盯這件事。
- `lumos search --about <檔>` 裡的 `<檔>` 是專案路徑,檔名可帶換行或偽造框線(測試裡有這個攻擊樣本)。
- 放框外就得過 `_plain_label`,放框內就變成「不是指令」,失去它想給的提示作用。
- 速查表若是寫死的固定字串,放框外沒問題。
- 引句:「推播 hook 維持只印篇名(防注入),改成多印一行這個指令」
- 佐證:`scripts/hooks/claude/impact-hook.py:498`、`scripts/hooks/claude/impact-hook.py:510`

**I15 〈回退〉和〈分期〉對不上:S21 沒落在任何一步,步驟 4 不受 off 影響**
severity: minor
blocking: 否 — 不影響行為對錯,影響的是交付與回退的說法能不能成立。
- 〈回退〉說「第 1 到 4 步」把 gate 設 off 就全停。
- 步驟 4(search 過濾)按〈不溯及既往〉明寫「不受開關影響」,設 off 停不掉它。
- 步驟 0 的 W4 也不受 gate 影響(見 I3)。
- S21(`[retire-when-*]` 滿足 retire)在〈分期〉沒有歸屬步驟。S13 與 S11 在步驟 0,S21 改的是 lint 全域行為。
- 驗收條款 S19 排在 S20、S21 之後,順序亂,屬於整理問題。
- 引句:「把專案設定的 `note_tags.gate` 改成 `off` 就停掉所有擋與提醒,不用改程式」

**I16 RETIRE-IF 與誤報量測的「從這裡量」,量得出的只有次數**
severity: minor
blocking: 否 — 不會做出壞系統,但 RETIRE-IF 的兩個撤除條件(誤報多過真報、search 過濾 8 週零次)在現有帳上量不出來。
- `lumos gov --stats` 只彙總每道閘的筆數、節點、提交與起訖日(「每道閘的筆數/nodes/commit/起訖日」),不分真報誤報。
- `note-shape` 的帳也只記擋下、warn、跳過,放行不寫。
- 「search 的過濾使用次數」要記在 `.usage-log.jsonl`。那是版控檔,記的是 `{ts,node,cmd}`,沒有旗標欄位,而且 `search` 現在不寫它。
- 要量就得改帳的格式,並接受讀指令在工作樹留 diff(`scripts/lumos:18064` 附近記過這個症狀)。
- 引句:「`lumos gov --stats` 看得到次數,RETIRE-IF 的誤報比例就從這裡量」
- 佐證:`scripts/lumos:39899`、`scripts/lumos:13695`、`scripts/lumos:18064`

**I17 要跟著改的文件、範本、測試、設定沒列全;`lands_in` 一個是還不存在的節點**
severity: minor
blocking: 否 — 不會做錯行為,但三個月後的人會發現規則有兩份說法。
- `lands_in` 列了 `Systems/筆記標籤`,這篇不存在,spec 沒寫「新開」。
- `note-shape` 的 Systems 家是 `Systems/筆記內容閘`,不是 `存量漂移守衛`。它的 WHY 寫著「這一層只擋兩種形狀」,W6/S3 到 S9 一上線就不成立。
- 同篇脈絡的 `Projects/筆記形狀擋_計劃` 第 97 行也有「要等第二層」的說法。
- W2 想辦的「程式推得出的事實別寫」,正是 `Systems/筆記內容審` 與筆記內容閘的職責(判定者逐行判)。W2 的「N 個、只有」句型比對,在 `Systems/筆記內容閘` 實測準度約三分之一,spec 沒給新的準度。
- 其他要同步:
  - `skills/lumos-project-notes/reference.md:408` 的 RULE 範例。
  - `commands/03-寫回圖譜.md` 以及 skill 的查詢表那一檔。
  - `Systems/lumos-cli-read` 的 search 旗標。
  - `scripts/test_lumos.py` 的紀律範本大小測試。
  - 已發出的消費專案 CLAUDE.md 會因範本變動出現「紀律區塊跟來源不一樣」的提醒。
- `lumos init` 只在 `.lumos/config.json` 不存在時才寫骨架(「既有設定不碰」)。
- 所以預先有手寫設定的新接入專案,拿不到 `note_tags.gate: block`,會靜默維持 off。
- 骨架另有 blank、單語言、多平台三種形狀,測試要釘三處。
- 引句:「`lumos init` 對新接入的專案寫入 `block`(六類欄位的機械判準擋、寫法規則提醒)」
- 佐證:`scripts/lumos:18678`、`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:20`

### 逐節覆蓋
- frontmatter、依據、PRIOR-ART、現況:已讀。現況第 1、3 點(提交時不印、`applies` 無消費者)我查過,屬實。第 4 點的四件文件矛盾也屬實,但第 3 件的修正方向是錯的(見 I11)。
- 設計原則 0 到 6、前綴表:已讀,表格的「篩選」欄受 I12 影響,「判過時」欄受 I8、I9 影響。
- 欄位 v1:見 I5 到 I9、I13。
- 寫法規則 W1 到 W5:W1、W3、W5 已讀,無獨立 finding;W2 見 I17,W4 見 I3。
- 一個事實只寫一處:W6 見 I4,欄位不重複見 I11。
- 讓 AI 知道該寫什麼:見 I1、I10、I14。
- 按需載入:見 I12、I14。
- 不溯及既往:見 I2、I17。
- 分期、已裁、天花板、不做:見 I15;其餘已讀,無 finding。
- 驗收條款、合約候選:見 I5、I10、I15。
- 回退:見 I15。

### 實務隱患逐類
- 併發:spec 說「不碰、不新增寫入點」,但〈自我治理〉要每次擋下與跳過都寫治理帳,I16 又要在使用帳加記錄。這些是新的 append 寫入點,兩處說法互相矛盾。治理帳寫入沿用 `_gate_event_or_warn`,風險可接受,但要改「不新增寫入點」這句。
- 效能:見 I5(每個 `[count:re]` 欄位各做一次全 repo 的 walk,沒預算)和 I12(search 的 8 行截斷)。
- 資源:無。沒有新的長駐程序或連線。
- 回滾:見 I15。
- 相容:見 I3(W4)、I17(init 骨架)。
- 注入:見 I14。
- 自我繞過:閘的開關讀被推送頂端提交裡的設定,推的人能在同一個提交把 `note_tags.gate` 改成 `off`。`Systems/存量漂移守衛` 的 RULE 已為 `drift_check.gate` 承認這點。spec 的 `off`/`warn` 逃生口是同一個形狀,應補一句「只防疏忽」並附回頭條件。
- 金流、對外送出、不可逆:同意 spec 的「已排除」,理由成立。

### 固定席判讀
- `Systems/存量漂移守衛`:不破壞既有行為。spec 沒碰 `drift` 的 c1 到 c5 與乙探針的判定,但 I8 提醒「判不了算要處理」這條決策,新閘要明講自己的取捨。
- `Systems/hook信任邊界`:有潛在衝突,見 I14。速查表若是寫死字串,放框外合規。
- `Systems/棧別提問表態閘`:不影響。它的棧別題只在改程式檔時附,spec 的速查表若改走同一個 hook,要確認 `t_impact_hook_stack_*` 的「沒題就不注入」判空邏輯不被新分支破壞。
- `Systems/筆記內容閘`:會被改寫(見 I17)。它「這一層只擋兩種形狀」的 WHY 與 S3 到 S9 衝突,要同步,否則同一個閘有兩份說法。

最高嚴重度:major,blocking 12 條
