# 標籤、漂移檢查與檢索盤點(negguard 工作樹,2026-10-01)

盤點對象:`/private/tmp/.../scratchpad/negguard`(頂端 0f1e68ea)。全程唯讀:只讀檔、只跑 `--help`、`search`(search 不寫使用帳)。工作樹裡 `docs/.governance-log.jsonl` 的改動是 16:00 別人提交時留下的,不是這次盤點造成的。

一句話總結:**標籤的「寫」大多有人檢查,「讀」幾乎沒有。** 行內 `[鍵:值]` 認得約 25 種,其中硬擋推送的只有合約那一族(test/audit/rollback/guard/due)、`[來源:]` 與 REVISIT 條件。RULE 生命週期那 6 個欄位只在手動跑 `lumos lint <篇>` 時才看得到提醒。檢索端除了 `search --regex` 逐行比對,沒有一個指令能「按前綴或行內標籤過濾、只回片段」。

---

## 1. 摘要行前綴與行內 `[鍵:值]`:認得哪些、誰在讀、讀了做什麼

### 1.1 摘要行前綴

- **單一來源**:`scripts/lumos` 的 `SYMBOL_NAMES` 與 `SYMBOL_RE`(在「階段二:讀側」開頭;依據 `Projects/標籤系統精簡_計劃` S10,2026-09-15 收成一份)。
  - 認得 15 個:`KEY FLOW DEP TEST AUTH FLAG DECISION VERIFY CORE PRIOR-ART REVISIT WHY RULE PITFALL FACT`。
  - **不在表內**:`RETIRE-IF`。`SYMBOLISH_RE`(`^([A-Z][A-Z-]*[A-Z]):`)會抓到它,寫進 summary 會被 lint 當成打錯字;實務上 37 行都寫在正文,所以沒人踩到。
- **讀前綴的地方**

| 讀的人(函式) | 讀什麼 | 做什麼 | 擋/提醒 |
|---|---|---|---|
| `_lint_collect`(`lumos lint` 與 doctor L 段) | 用 `SYMBOLISH_RE` 比對 `SYMBOL_NAMES` | 不在表內就說「非標準符號行」 | 提醒 |
| `context_marker_warnings` 加 `_CONTEXT_MARKER_RULES`(lint 用) | `WHY:` 要有出處(`_CTX_SRC_RE`:日期、#d、`[[`、`[src:`、像 sha 的字串);`PITFALL:` 要有 `[test:`、「重現」或 repro(`_CTX_REGRESS_RE`);`FACT:` 要有 `[來源:…]`;`RULE:` 交給 `rule_lifecycle_warnings` | 加進 warns | **提醒,不影響回傳碼** |
| `_ns_check_line` 加 `_NOTE_SHAPE_PREFIX_RULES`(`lumos note-shape`,提交前與推送前) | 只看**新增的**摘要行裡的 `FACT/FLOW/DEP`;要有 `[來源:部署\|資料庫\|生產\|外部\|人工]`。骨架留的空前綴、只放連結的 FLOW/DEP 指路行豁免(`_NS_POINTER_ONLY_RE`) | 列入違規 | **擋**(note_shape.gate 預設 block;CI 也跑) |
| `_lint_collect` 的 Check U | 只看 `KEY:` 行:「分配式量詞+程式實體+義務語氣」三者同現,而且沒有 `[test:]` | 「疑似通則」 | 提醒 |
| `_lint_collect` | `FLAG:` 值只收 TECHNICAL/DECISION/ORIGIN(`_FLAG_ENUM`,有日期切點) | error | 擋(新筆記) |
| `INVARIANT_RE`、`DEBT_RE`、`CHECKPOINT_RE`、`IRREVERSIBLE_RE`、`PLANNED_RE` | 只認 `KEY:` 行首的 ★…★ | 合約抽取 | 見 1.2 |
| `_search_region`(search 輸出) | 命中行在 summary 時標 `[RULE]`、`[KEY]`… | **只顯示標記**,不能拿來過濾 | — |
| `_revisit_split`、`_revisit_lines` | `REVISIT:` 行(正文與摘要都算;表格與圍欄不算) | E5、乙探針、note-shape 格式檢查 | 見第 2 節 |
| `_ns_negation_hits` | `RETIRE-IF:` 行、`為什麼還不做:` 行、REVISIT 行不看 | 否定現況句提醒 | 提醒 |

- **lint 判 FLOW/DEP 的範圍刻意只到 FACT 為止**(`_NOTE_SHAPE_PREFIX_RULES` 上方的註解):本庫有 277 行舊的 FLOW/DEP,lint 一接上就會噴出幾百條警告。新寫的 FLOW/DEP 交給 note-shape 擋。程式註解裡有一行 `REVISIT:2026-11-21`:看觸發統計,決定要不要延伸。
- **本庫用量**(grep,行首前綴):KEY 2103、DEP 188、WHY 169、PRIOR-ART 168、PITFALL 106、FLOW 91、RULE 18、FACT 12;REVISIT 249(其中條件式 10);RETIRE-IF 37;`[來源:]` 18 個。

### 1.2 行內 `[鍵:值]` 標籤全表

`_NS_NEG_FIELD_KEYS`(否定現況句提醒要遮掉的欄位清單)剛好就是一份「工具認得的鍵」總表:`since retire until confirmed status applies test audit kill rollback guard src git manual by 來源`,外加 `when-*`。再補上清單外的 `watch due keeps [S數字]`,以及 HTML 註解 `<!--lumos:count=…-->`。

| 鍵 | 正則/函式 | 用在哪種行 | 誰讀、讀了做什麼 | 擋/提醒 |
|---|---|---|---|---|
| `[since:]` `[retire:]` | `SINCE_REF_RE`、`RETIRE_REF_RE` → `parse_rule_fields` → `rule_lifecycle_warnings` | `RULE:` | 缺任一個就提醒;值裡含 `]` 會被截斷,也提醒(`rule_field_truncated`) | **只提醒**,而且只在 `lumos lint` 看得到(見 1.3) |
| `[until:]` | `UNTIL_REF_RE` | `RULE:` | 不是合法日期就提醒;過期還是 active 也提醒 | 同上 |
| `[confirmed:]` | `CONFIRMED_REF_RE`、`_RULE_CONFIRM_STALE_DAYS=180` | `RULE:` | 寫了但超過 180 天也提醒。**沒寫則完全不唸** | 同上 |
| `[status:]` | `STATUS_REF_RE` | `RULE:` | 只收 active/superseded;superseded 提醒「已失效、刪掉」 | 同上 |
| `[applies:]` | `APPLIES_REF_RE` | `RULE:` | **只解析、沒有任何消費者**(只參與截斷檢查) | — |
| `[來源:部署\|資料庫\|生產\|外部\|人工]` | `_CTX_SOURCE_RE` | `FACT/FLOW/DEP` | lint(FACT)提醒;note-shape 對新增的 FACT/FLOW/DEP 擋 | **擋**(新行) |
| `[test:]` | `TEST_REF_RE`、`invariant_test_refs` | `KEY:★INVARIANT★`、`PITFALL:`、計劃條款 `[S數字]` | doctor T:合約要綁存在的測試(擋);K:★COMBO★ 只綁一條就提醒;PITFALL 只要「有」`[test:`,**不驗存在**;spec-gate、S5 驗計劃條款的測試名;U 段看到 `[test:` 就不唸 | 合約擋,PITFALL 只看形狀 |
| `[audit:]` | `AUDIT_REF_RE` | ★INVARIANT★ | lint error「未獨立審計」;推送擋 | 擋 |
| `[kill:recipes]` | `KILL_REF_RE` | ★INVARIANT★ | `guard kill`;doctor P2「配方原文對不上程式」 | P2 提醒 |
| `[rollback:]` `[guard:]` | `ROLLBACK_REF_RE`、`GUARD_REF_RE` | ★IRREVERSIBLE★/★CHECKPOINT★ | doctor R、lint:IRREVERSIBLE 缺回退就 error;CHECKPOINT 只提醒 | IRREVERSIBLE 擋 |
| `[due:]` `[watch:]` | `DUE_REF_RE`、`WATCH_REF_RE` | `KEY:★INVARIANT-PLANNED★`(預告合約) | `context` 印「預告」段;doctor S15:逾期擋、7 天內先唸 | 逾期擋 |
| `[src:路徑:行]` `[git:sha]` `[manual:]` | `SRC_REF_RE`、`GIT_REF_RE`、`MANUAL_REF_RE`、`INV_TAG_RE` | regen 筆記的 KEY 行;計劃條款 | Check J(`check_regen_provenance`)分級出處;spec-trace 認 `[manual:]` | J 有 error |
| `[keeps]` | `_KEEPS_RE` | 風險低計劃條款 | 雙向門「維持既有行為」 | — |
| `[when-file:]` `[when-test:]` `[when-symbol:路徑::名]` `[when-status:節點=值]` `[by:日期]` | `_PROBE_TOKEN_RE`、`_PROBE_KEYS`、`_probe_parse`、`_drift_probe_*` | `REVISIT:` 行 | note-shape:新寫的條件式缺 `[by:]`、文法錯、或條件寫在表格/欄位裡就擋;`drift check`:推送讓條件從不成立變成成立就擋;E5 照 `[by:]` 日期唸到期 | 擋 |
| `<!--lumos:count=N re=… in=glob-->` | doctor N 段的 `_CNT_RE` | 正文任意處 | 重算 repo 裡正則的命中數,不符就列出 | 提醒(本庫 22 處,含範例) |

### 1.3 讀到但「送不到人眼前」的地方(重要)

- `cmd_lint` 只有 error 時回 1,warning 回 0。
- 提交前掛鉤 `scripts/hooks/pre-commit` 的 Gate L 是 `if ! out="$(lumos lint …)"`,**只在 lint 失敗時才印輸出**。所以 WHY/PITFALL/FACT 缺配件、RULE 缺 since/retire、`[until:]` 過期、`[confirmed:]` 逾 180 天這些提醒,提交時一律看不到。
- doctor 的 L 段呼叫 `_lint_collect`,但只取 `_e`(錯誤),**丟掉 `_w`(提醒)**。全庫也就沒有任何一處會唸「RULE 過期」「RULE 半年沒確認」。
- `rule_lifecycle_warnings` 的唯一呼叫者是 `context_marker_warnings(rules=None)`,而那支只被 `_lint_collect` 呼叫。
- 這件事 `Projects/Lumos定位_程式碼為主脈絡為輔_計劃` 的〈檢討〉第 3 點已經記過(「提醒送不到」),`Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋` 的 d5 背景也寫了。後來修的方式是改用 note-shape 硬擋;**RULE 生命週期那一塊沒有跟著修**。

---

## 2. 判定「筆記敘述過時」的既有檢查

### 2.1 doctor(`cmd_doctor`)

doctor 用 `section()` 分段,`warn` 計入問題數,`warn_soft` 不計。推送前掛鉤跑 `doctor --ci`,CI 也跑。

| 段 | 判準 | 擋/提醒 |
|---|---|---|
| **N** 可重算數字宣稱 | `<!--lumos:count=N re=正則 in=glob-->` 在 repo 重算(上限 4000 檔、40MB),跟 N 不符就列出;先剝掉圍欄 | 提醒 |
| **P** 失效檔案路徑 | 筆記行內程式碼裡像 `頂層目錄/…` 的路徑,檔案不存在就列出。跳過 Verification、superseded/stale 節點、URL、萬用字元、大括號展開 | 提醒(已知誤報:指令字串 `scripts/lumos impact --file`,見 `Issues/rtb接上漂移檢查後回報的四個小改進` ④) |
| **P2** 殺傷力配方失配 | `_kill_p2_scan` 拿 `_kill_recipe_judge` 判配方原文對不對得上程式 | 提醒,`--ci` 才寫帳 |
| **Y** 被點名的符號存在性 | 只掃 Systems;用 `symbol_profile` 認「方法/類別形狀」的行內程式碼,repo 找不到就列出;同一行有否定字眼就豁免(`NEG_LEXICONS`) | 提醒 |
| **V** valid_under 過期 | 帶 `valid_under` 的節點 >90 天沒更新 | 提醒 |
| **S2** about_code 過期 | about_code 標了之後正文又改過 | 提醒 |
| **E1/E2/E3** | 引用失效的驗證、建立在被推翻的決策上、驗證引用被翻案的決策 | 提醒 |
| **E5** REVISIT 到期 | `_revisit_lines`:日期式 ≤今天就算到期;條件式看 `[by:]`;日期格式壞的另外計數;已結案的 Issue 加註 | 提醒,`--ci` 寫帳(nags 週報會升級) |
| **Z** 存量漂移 | `_drift_doctor_lines` 也就是 `_drift_state_findings` 的 c1–c5,加上探針;沒有發現就整段不印、不寫帳 | 提醒 |
| **S15** 預告合約 | `[due:]` 逾期 | **擋**(不准延期) |
| **T/R** | 合約沒綁測試或審計、不可逆動作沒寫回退 | 擋 |
| **L** | 每篇跑 lint 的 **error 級**(note_lint.gate=on 才擋;本 repo 是 on) | 擋/提醒依開關;**warning 丟掉** |
| (沒有 RULE 效期段) | — | **找不到**。搜過 `UNTIL_REF_RE`、`CONFIRMED_REF_RE`、`_RULE_CONFIRM_STALE_DAYS`、`rule_lifecycle_warnings` 的所有呼叫點,doctor 都沒有用到 |

另外 `cmd_context` 進場時會跑 `_stale_status_claims`:表格某一格只寫待辦詞、而那格連到的節點已經 done,就警告。判準刻意收得很窄,實測只命中 1 處真案例。

### 2.2 存量漂移守衛 `lumos drift`(家:`Systems/存量漂移守衛`;計劃:`Projects/存量漂移防線_計劃`、`存量漂移改法_計劃`、`漂移修法補強_計劃`、`舊句檢查_計劃`)

- **甲:狀態一致**(`_drift_state_findings`,scan、check、doctor Z 共用)

| 種類 | 判準 |
|---|---|
| c1 | 守衛驗證已經 pass,還留著工具寫的預告句(`_guard_planned_prose`)。這是**唯一會擋的一種**:範圍內轉成 pass 的那篇才擋 |
| c2 | Issue 還 open/doing,但連著已收尾的計劃 |
| c3 | 驗證還 pending,但 plan_refs 指的計劃全部已收尾 |
| c4 | `valid_under` 含「未提交/還沒提交/uncommitted」 |
| c5 | 轉正做了一半(家筆記已經有正式合約行) |

c2–c5 只列出,範圍內有碰到的才列。
- **乙:探針**(`_drift_probe_check`):REVISIT 的 `[when-*]` 條件在這段推送從「不成立」變成「成立」就要處理,也就是擋。
- **m1 舊句檢查**(`_drift_old_sentence_check`,只有 `drift check` 會跑):這段推送裡消失的程式名稱(Python 用 ast,其他語言用文字)筆記裡還在講。開關 `drift_check.old_sentence`,預設 warn,先提醒兩週。scan、doctor 不跑 m1,因為只有一棵樹判不出「消失」。
- **開關**:`drift_check.gate` 預設 **block**(2026-09-30 決策 d1);判不了的情況算「要處理」(strict)。CI 與推送前掛鉤都有接。
- **處置**:`drift fix --kind c1..c5`(c4 只給證據加一條預填好的 `lumos set` 指令)、`drift ack`(要寫理由、要提交;c2/c3 會綁住當時連著的計劃清單)、`drift exam`(拿考卷考)。
- **覆蓋率**(`Issues/存量筆記漂移三種機制_rtb根因回饋` 的〈工具覆蓋率比對〉):rtb 的 20 處真漂移,存量抓到 7 處;如果當時就有推送前檢查,約可抓到 13.5 處;抓不到的有四種形狀:①新增了 X,舊句說還沒有 X;②回頭條件是散文;③數值變了但名稱沒消失;④同一段推送裡先加後刪。

### 2.3 note-shape(提交前 Gate NS、推送前、CI;`cmd_note_shape`、`_note_shape_eval`;計劃 `Projects/筆記形狀擋_計劃`,done)

- **擋**(note_shape.gate 預設 block;`LUMOS_SKIP_NOTE_SHAPE=1` 可單次跳過,會留帳,CI 照擋;上線點之前的舊帳不追):
  - 新寫的程式行號引用 `路徑:行`(要釘版本得寫 `路徑@≥12碼sha:行`,`_ns_pin_ok` 會驗);
  - 新增的 FACT/FLOW/DEP 沒帶 `[來源:]`;
  - REVISIT 格式壞、條件式缺 `[by:]` 或文法錯、條件寫在不評估的地方(`_ns_revisit_violations`);
  - 新出現的程式檔讓舊筆記裡原本不算數的行號引用「醒過來」(`_ns_became_code`)。
- **否定現況句提醒**(`_ns_negation_hits`、`_ns_negation_format`;計劃 `Projects/否定現況句配回頭條件_計劃`):新寫的行出現窄表字眼(還沒、尚未、目前沒有、未實作、TODO、not yet…)時,扣掉引號、修飾語、規則句、歷史句、REVISIT 行、RETIRE-IF 行、`[鍵:值]` 欄位,剩下的才提醒,並教人改寫成 `REVISIT:[when-…][by:…]`。開關 `note_shape.negation` 只收 warn/off,**不提供 block**。
- **不管的**:「目前沒有 / 只有 N 種」這類句型、貼錯標籤的 WHY、done 計劃的「現況」段。`筆記形狀擋_計劃` 第 97 行明寫這些形狀不固定,要等第二層。

### 2.4 note-audit

- **筆記內容審**(`prepare/record/check/skip`;`Systems/筆記內容審`、`Projects/筆記內容審_計劃`):推送前派判定者逐行判新寫的筆記「是不是程式碼推得出來」。`note_audit.gate` 預設 block,但**目前還沒接進推送前掛鉤與 CI**(`Systems/筆記內容審` 第 65 行;`REVISIT:2026-10-12` 校準)。它只判「該不該寫」,不判「寫得對不對」。
- **回頭重讀守檔筆記**(`reread-prepare/record/check`;`_note_reread_check`;`Projects/守檔筆記對照改動_計劃`,2026-10-01 上線):這段推送改到程式檔的家、而且那篇家筆記也被改過時,把程式 diff 加上全文交給判定者,問「哪幾行不成立了」。reread-check **只提醒、永遠回 0**,推送前掛鉤與 CI 都有接。`REVISIT:2026-10-15` 抽 30 行量準度。

### 2.5 其他

- **delguard**(提交前,`delguard --staged`):被刪掉的符號,筆記還在講就提醒;只看前 40 個刪除名。
- **`stale --match/--candidate`**:列出 `valid_under`/`revalidate_when` 含某字串的驗證(人主動查)。
- lint 的 Check U(KEY 通則宣稱沒綁測試)提醒。

---

## 3. 能依標籤或欄位過濾的檢索

| 指令 | 能過濾什麼 | 輸出形狀 | 能不能按前綴或行內標籤過濾 |
|---|---|---|---|
| `lumos search`(`cmd_search`) | `--path` 資料夾前綴;預設排除 superseded(`--include-superseded`);`--code`;`--regex` | **逐行片段**:行號 + `[區域]`(`_search_region`:★INVARIANT★、★DEBT★、摘要前綴、`fm:欄位`、body)+ 那一行;`--files-only` 只列篇名加命中數;`--json` 只有 node/score/hits/match_lines,**沒有片段文字** | **只能靠 `--regex`**:例 `search --regex '^\s*RULE:'` 實測得 18 處/15 篇,片段帶 `[RULE]`;`--regex '\[來源:'` 5 處/4 篇。但 regex 會自動走 legacy(字母序、不排名);沒有 `--prefix`、`--type`、`--status`、`--tag` 旗標;區域標記只拿來顯示 |
| `lumos query`(`cmd_query`) | frontmatter `tags` 家族:`--tag` 可重複、AND;`--no-tag`;`--active`(status 不在收案值);`--contract`(有 ★INVARIANT★);`--linked`(一層鄰居);`--json` | **只列篇名** + status + 標籤,不給片段 | 只認 frontmatter 標籤。type/status 靠鏡像標籤(`type/x`、`status/x`)才篩得到;`Projects/標籤系統精簡_計劃` 想刪鏡像、改成讀取時合成,那案目前排隊中。scope/ 九值可篩。**不讀摘要前綴、不讀行內 `[鍵:值]`** |
| `lumos context`(`cmd_context`) | 單篇 | 頭部列 type/status/日期加其他標籤家族;依序印 `_stale_status_claims` 警告、valid_under、合約、預告合約、完整 summary(`--brief` 只印前兩行)、verified_by/plan_refs/core_refs、鄰居;`--recommend` 印相關推薦 | 不能按前綴篩;`--brief` 是「前兩行」不是「某類行」 |
| `lumos contracts` | 全庫或單篇 | 只列 ★INVARIANT★/★DEBT★ 行加綁的測試 | 等於寫死的「合約行」過濾器 |
| `lumos decisions [--superseded]` | 單篇決策 | 決策條目 | 只看 decisions 欄位 |
| `lumos impact --file/--diff/--node`、`--incidents-only`、`--ranked`、`--json` | 改檔波及的節點 | 篇名、種類(direct/hop/incident/home)、合約類別;**沒有片段** | 沒有 |
| 推播 hook(`scripts/hooks/claude/impact-hook.py`) | 包一層 `impact --ranked` | `build_ranked_context`:必看(家、合約、事故)加分數清單,只印**篇名與合約類別**;`_contract_label`、`_match_label` 刻意不印圖譜原文(防注入) | 沒有;`Projects/按需檢索_計劃` 想改成目錄式推播,目前 doing |
| `dispatch-lens` | 代碼審派工 | 只貼合約行 | 寫死的合約行 |
| `stale --match` | valid_under/revalidate_when 子字串 | 篇名 | 只看這兩個欄位 |

**結論:找不到**「按摘要前綴(WHY/RULE/PITFALL/FACT)、按行內 `[鍵:值]`(例:`[status:active]` 而且 `[confirmed:]` 在半年內的 RULE 行)、或按 type 加前綴組合篩,並且只回片段」的指令。最接近的是 `search --regex`,但它不排名,篩不了 type/status 組合,也不認欄位語意。

搜過的詞:`prefix`、`--prefix`、`SYMBOL_RE` 的呼叫點、`_search_region`、`cmd_query`、`cmd_context`、`build_ranked_context`、`按需`;圖譜裡搜了「前綴 過濾」「片段 輸出」「按 標籤 檢索」。

---

## 4. 寫法規範寫在哪,哪些被機械擋

### 4.1 寫在哪

- **單一來源**:`scripts/templates/graph-discipline.md`,注入到每個專案的 CLAUDE.md 與 AGENTS.md 的紀律區塊。〈寫筆記時〉那張前綴表、RULE 欄位規則、`[來源:]`、鐵則四的 REVISIT 寫法都在這裡。
  - doctor D 段比對注入的內容是否一致;SessionStart hook 的 `_discipline_lag` 不一致會提醒一行。
- **skill**
  - `skills/lumos-project-notes/reference.md`〈摘要區塊〉:兩張符號表,宣稱「不重寫範本那張表」;測試 `t_note_convention_single_source` 擋第二份定義。另有〈標籤家族〉值域表、★INVARIANT★/`[test:]`/`[kill:]`/`[audit:]`/`[rollback:]` 各節。
  - `SKILL.md`:承認風險的鐵則。
  - `commands/03-寫回圖譜.md`:note-shape、條件式 REVISIT 四種鍵的寫法。
  - `commands/INDEX.md`。
- **派工詞範本**:`scripts/templates/note-audit-judge.md`、`note-audit-reread.md`。

### 4.2 已被機械擋(硬擋)

| 規範 | 擋在哪 |
|---|---|
| FACT/FLOW/DEP 新行要帶 `[來源:]` | note-shape |
| 程式行號引用(新行) | note-shape |
| REVISIT 格式;條件式要帶 `[by:]` | note-shape |
| REVISIT 條件成立 | drift check |
| c1 轉正後留著預告句 | drift check |
| ★INVARIANT★ 必須是 KEY 行首,要綁 `[test:]` 與 `[audit:]` | lint、doctor T、推送 |
| ★IRREVERSIBLE★ 要寫回退 | lint、doctor R |
| 預告合約逾期 | doctor S15 |
| FLAG 三值;status、priority、risk 值域(新節點) | lint error |
| frontmatter 指紋、decisions 結構 | lint error |
| 每支檔有家;節點只准寫自己家的檔 | home check |
| 改 code 沒動圖譜 | pre-commit Gate 3 |
| type、summary 必填等新欄位規則 | 依 note_lint.gate;本 repo 是 on |

### 4.3 只有文字或只提醒

- **WHY 要出處、PITFALL 要防回歸**:lint 提醒,而且提交時看不到(見 1.3)。PITFALL 的 `[test:]` **不驗測試存不存在**(`漂移防治路線圖_計劃` 1b:目前只查計劃)。
- **RULE 的 since/retire 必填、confirmed、until、status、applies**:只有手動 lint 時提醒;doctor 不看;沒有任何程式讀它們來決定「這條能不能挑戰程式碼」。這件事純靠 agent 照 CLAUDE.md 自己判斷。
- **「同一事實只寫一處」「改原句不追加」「現在式只寫在 Systems」「撤除用節級指令」**:只出現在 `漂移防治路線圖_計劃` 機制 8 的排隊清單裡,紀律範本與 skill 都還沒寫(找不到)。
- **done 計劃的現況段收成一句**(Issue d4):寫在 Issue 決策裡,note-shape 不擋(計劃第 97 行),內容審也還沒接線。
- **否定現況句改寫成 REVISIT**:只提醒(note_shape.negation 不收 block)。
- **scope 一篇一個主類**:lint 只提醒。
- **WHY/RULE/PITFALL 是不是其實在講現況**:沒有形狀檢查。`Lumos定位` 計劃〈檢討〉第 1 點記了 rtb 有約一半是在講現況;要靠內容審,但它還沒接線。

### 4.4 文件與程式對不上(發現,未改)

1. `reference.md` 長表的 RULE 範例是 `[2026-09-21 起，退場:改用新閘後撤]`,不是 `[since:][retire:]` 欄位寫法;照抄會被 lint 唸缺 since/retire。
2. `reference.md` 底下「2026-08-22 搬入版」的精簡表仍寫 `FLOW:` 是「核心流程 a→b→c」、`FACT:` 是「現況描述(能查到的別抄)」,跟新規範(FLOW 只指路、FACT 要帶 `[來源:]`)相反;兩版並存。
3. 紀律範本(CLAUDE.md)說 RULE 要「同時寫齊 since、retire、confirmed,而且最近半年確認過」才有挑戰程式碼的效力。但程式註解(`_RULE_FIELD_RES` 上方)寫的是「since 與 retire 寫齊、不是 superseded 就有效力」,lint 也不要求 confirmed。兩者口徑不同,而且都沒有程式真的執行這個判斷。
4. `Projects/按需檢索_計劃` 摘要裡還有 `FACT:[以程式碼為準]…查:` 的舊寫法(2026-09-27 起不算數),而且沒有 `[來源:]`。這是舊帳,lint 會提醒,note-shape 不追。
5. `RETIRE-IF` 不在 `SYMBOL_NAMES` 裡。寫進 summary 會被當成打錯字。

---

## 5. 圖譜裡跟「標籤提案、寫法規範、依標籤檢索」有關的計劃、調研與否決

### 5.1 直接相關

- **`Projects/漂移防治路線圖_計劃`**(doing,2026-10-01):rtb 全讀約 310 處漂移,整理出八項機制加一份標籤提案。
  - rtb 提了約 15 種標籤:count、value、enum、retire-when-*、expect、id、supersedes、superseded-by、retired、test-gone、snapshot、from、same-as、lives、deliver、recheck。
  - 試標結果(rtb 9b0af3e):`[count:]` 能標的只有 18%,但標上的全判得出,抓到 6 句過期、誤報 0;`[retired:]` 加 `[test-gone:]` 只有 3/19 節能誠實整節標;挑對集合最費工;count 加 value 約可覆蓋四成。
  - 編排者裁定:準但涵蓋有限,**排在 1a 殺傷力配方、1b/1c 測試綁定存在性、機制 3 條件化之後,另開一案**。
  - 機制 8「寫法規範」排隊;機制 3 想收的 `[expect:]` 用來防觸發代理錯位;`REVISIT:2026-10-15` 決定標籤要不要另開案。
- **`Issues/存量筆記漂移三種機制_rtb根因回饋`**(open):三種機制(①只追加不回頭改 9 處 ②計劃/Issue 的「目前沒有 X」沒人通知 5 處 ③狀態指令只改欄位 6 處),三條候選防線,覆蓋率比對;`REVISIT:2026-10-12` 決定三條防線各自怎麼走。
- **`Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋`**(open):
  - d1:目標是「不留存程式碼推得出來的東西」;
  - d2:舊帳不回頭清;
  - d3:FACT 收窄成程式碼答不了的(否決整條收掉、否決照舊);
  - d4:done 計劃的現況段收成一句(**否決「只加快照標語」**);
  - d5:要機械擋;
  - d6:形狀擋加 AI 審兩層;
  - d7/d8:拆分。
  - 候選修法①②③就是寫法規範加工具提醒。
- **`Projects/Lumos定位_程式碼為主脈絡為輔_計劃`**(doing):前綴分類的起源。〈檢討〉五點:①只檢查標籤的配件,不檢查內容;②正文不在管轄內;③提醒送不到;④「以程式碼為準」只綁在 FACT 上;⑤零觸發不等於成功。
- **`Projects/標籤系統盤點_調研`**(doing,2026-09-14):盤點各家族的消費者:
  - flag/ 零消費;
  - scope 意外進了 BM25F;
  - type 鏡像漂移沒人擋;
  - 摘要前綴表跟紀律文件不一致(後來 S10 已修)。
  - PRIOR-ART:K8s labels、Obsidian properties、JSON Schema 驗 frontmatter。
- **`Projects/標籤系統精簡_計劃`**(todo):鏡像標籤退場、改成讀取時合成。S10、S9、S13、S14 已做;S1–S7、S12 等 `Projects/檢索核心重建_計劃`,**但那案 2026-09-16 已收案、不落地**,前置條件等於懸空。
- **`Projects/標籤結構收編_計劃`**(done,2026-08-05):值域 lint、context 頭部攤出標籤家族、risk/ 接 impact;**否決:topic/domain 分類稅**;2026-09-08 後記:scope 只當 query/MOC 的索引軸。
- **`Projects/檢索訊號三件_計劃`**(todo):[A] 別名欄回填(移交後隨檢索核心重建收案);[B] 記錄查詢字串當點擊回饋;[C]「導覽樞紐 vs 答案」新家族。**否決:技術棧標、主題分類標、新鮮度標**(新鮮度用既有旋鈕)。
- **`Projects/圖譜結構化查詢_計劃`**(done):`lumos query`;**明確不做 OR、範圍比較、排序、查詢語言**(YAGNI)。
- **`Projects/檢索核心重建_計劃`**(done,不落地):**否決持久化索引(d1)、否決候選收斂(d2)**;復活要帶新數字。
- **`Projects/GraphRAG對節點關聯_調研`**(doing):Graph RAG 幫助有限(PPR 擴散已被消融實驗砍掉)。建議量推播用上率、零命中時用詞共現改寫,待 Enzo 裁。
- **`Projects/按需檢索_計劃`**(doing):推播改成目錄式;RULE:事故與合約那一層永遠無條件推。

### 5.2 漂移檢查相關(含否決)

- `Projects/存量漂移防線_計劃`(doing):定義甲乙兩種與 c1–c5,d1 改預設 block。
- `Projects/存量漂移改法_計劃`(doing)、`Projects/漂移修法補強_計劃`(doing):`drift fix`。c4 曾試「工具改 YAML」,**四輪都漏一種形狀,否決**,改走 `lumos set`。
- `Projects/舊句檢查_計劃`(doing):m1。
- `Projects/否定現況句配回頭條件_計劃`(doing):寫法守衛;**升級成擋不在範圍內**。
- `Projects/新增名稱否定句檢查_計劃`(doing):**量完結論是不做成檢查**(122 行 0 真),改走寫法守衛,要 Enzo 確認。
- `Systems/存量漂移守衛` 的 WHY(2026-09-30):「段落提到的程式在段落寫完後被改過,就標可能過時」**不做**(rtb 20 處只標到 3 處、抽 30 段只有 2 段真);只做「提到的名稱已被刪」的一次性清單。
- `Projects/筆記形狀擋_計劃`(done)、`Projects/筆記內容審_計劃`(doing,未接線)、`Projects/守檔筆記對照改動_計劃`(doing,只提醒)。
- `Projects/回訪掃描_計劃`(done):E5。

### 5.3 相關 Issue

- `Issues/lint把RULE行裡提到的合約記號當成放錯位置`(open):lint 的 ★ 位置檢查比合約抽取寬,RULE 行裡「提到」★INVARIANT★ 就會被報 error;先記著。
- `Issues/rtb接上漂移檢查後回報的四個小改進`(open):doctor P 段把指令字串當成失效路徑。

---

## 給下一步的觀察(只是線索,不是結論)

- 想讓標籤「被機械讀」,現成的接點有兩個:
  - `_NS_NEG_FIELD_KEYS` 加 `_PROBE_TOKEN_RE`:新鍵要同時登記進否定現況句的遮罩,不然欄位值裡的「還沒」會誤觸發提醒。
  - `parse_rule_fields` 加 `_RULE_FIELD_RES`:一個欄位一個正則的慣例。
- RULE 生命週期要送得到人眼前,可以參照當初「提醒送不到」的修法:接進 note-shape(只管新行)或 doctor(需要新的一段)。目前兩邊都沒有。
- 檢索端想要「只回某類行」,最小改動是讓 `search` 用 `_search_region` 的結果過濾(那個區域標記已經算好了);`query` 不碰行層。`--regex` 是目前唯一可用的權宜做法。
