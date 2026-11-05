severity: blocker

# 高風險測試證據加嚴_計劃 r2:邊界鏡頭審查(邊界-sonnet)

這份計劃把風險高的計劃改成「設計審過後套風險低的先紅檢查」,再加預期值表與整表簽核。我把表解析、表指紋、判定檔、生效時間、簽核事件的極端輸入逐一試過。能實測的都用 `scripts/lumos` 的函式在 `/tmp/lumos-seat-work/高風險測試證據加嚴/邊界-sonnet/` 跑過。

## Findings

### 1. 推送前檢查讀不到 `red_first`,每份先紅計劃在作者本機都會被誤擋

引句:「新增機制前的最小解自問:先紅模式不加新指令、新帳欄只有留痕的 `red_first` 一個」

- 推送前讀審查帳只留 `_SPEC_GATE_PUSH_FIELDS` 這張白名單裡的欄位,`red_first` 不在裡面。
- 該處註解寫明「要讀新欄位就加進來,不然讀到的永遠是 None」。
- 規格閘會把留痕同時寫進審查帳與治理帳,兩筆 `ts` 相同。`_spec_gate_pick` 同秒時讓本機審查帳那筆勝出,而那筆正是被裁過欄位的版本。
- 重現:審查帳放一筆 `plan_risk:"high", red_first:true` 的 spec-gate 留痕,依序跑 `_spec_gate_ledger_index(env, _SPEC_GATE_PUSH_FIELDS)`、`_spec_gate_latest_records`、`_spec_gate_pick(lat, [原筆])`。兩步都回 `red_first = None`,留痕只剩 `clause_sha, kind, loop, plan, plan_risk, tests, token, ts`。
- 後果:
  - S6 判成「最新留痕沒有 red_first」,會寫 `high-red-missing` 並擋下推送。
  - S5 的 `full` 條件不成立,不走全套檢查。
  - S14 的 `by` 也讀不到。
- 計劃第 2 點只說改 `_spec_gate_push_scan` 與 `_spec_gate_push_stale`,沒提這張白名單。
- file: `scripts/lumos:15792`、`scripts/lumos:15508`、`scripts/lumos:15834`

severity: blocker
blocking: 是,先紅模式的主路徑(S5、S6、S14)在單機上必壞,改計劃才能避免。

### 2. 先紅模式沒有「每條條款的測試名互不相同」這道檢查,一支紅測試可以證明所有新行為

引句:「風險高的計劃在設計審過了之後,規格閘與推送前檢查都把它當風險低一樣查」

- 風險低的「各自紅」其實有三塊:靜態檢查、跑後判定,還有 `_clause_check_twoway`。
- `_clause_check_twoway` 擋「兩條條款綁同一支測試」與「測試不存在或懸空」,理由是「十條全綁同一支也能全部存在」。
- `_clause_check_twoway` 只在 `_clause_check(door="low")` 才跑。計劃名詞節列的「雙向檢查」只有前兩塊,先紅模式的 `door` 是 high,這道不會跑。
- 計劃自己的條款就是反例:S1、S2、S4 都綁 `t_spec_gate_high_red_first_mode`,S6、S7 與 S10、S11 與 S13、S14 也各共用一支。我用 `lumos spec-gate 高風險測試證據加嚴_計劃 --no-run` 實跑,印出的綁定表確認了這些共用。
- 照風險低的規則,這份計劃自己過不了關。
- 另一個接縫:`_clause_check` 對 `door != "low"` 才驗回退節。把 `door` 改成 low 去啟用互異檢查,會同時丟掉回退節的要求,計劃沒決定該怎麼取捨。
- file: `scripts/lumos:14162`、`scripts/lumos:14797`、`scripts/lumos:15296`

severity: major
blocking: 是,「每條新行為各自先紅」是本計劃的核心,這裡一支紅測試就能全過。

### 3. 迴圈首筆帳查不到或解不開時,先紅模式開不開沒有定義

引句:「審查帳裡這份計劃的迴圈編號最早一筆非結局帳的時間」

- 我實測 `_loop_first_ts_key`:

  | 帳上狀況 | 回傳 |
  |---|---|
  | 沒有 `.canary-log.jsonl` | `None` |
  | 只有沒帶時區的 `ts` | `None` |
  | `ts` 是純日期或數字 | `None` |
  | 舊的一筆沒帶時區(被跳過),新的一筆有時區 | 回傳後者的時間,結果 ≥ 生效時間,舊計劃被誤算成新計劃 |

- 計劃自己說審查帳在消費專案預設被 git 忽略。乾淨 clone、新 worktree、另一台機器上這個函式就回 `None`。
- 現有呼叫端(`_spec_gate_clause_part`)把 `None` 當「新迴圈」,只影響句式檢查。
- 先紅模式是會擋推送的閘,而版控裡有 389 份 `rc 0` 的判定檔:
  - 若 `None` 當「≥ 生效時間」,舊的風險高計劃一碰就被 `high-red-missing` 擋,違反「不回溯」。
  - 若 `None` 當「早於」,換台機器先紅模式就靜默關閉。
- S2、S6 都沒有 `None` 的案例。
- file: `scripts/lumos:14975`、`scripts/lumos:14999`

severity: major
blocking: 是,不回溯與不靜默失效是這個開關的安全前提,卻無規格。

### 4. `_h2_section_lines` 偵測不出「同名節兩次」和「表在圍欄裡」,S8 也沒列這兩項

引句:「同名的節出現兩次、或節裡沒有表、或表在程式碼圍欄裡,都算格式錯」

- 我實測:兩個 `## 預期值表` 會被合併成一串行回傳(中間隔著別的節),沒有任何重複的訊號。
- 圍欄內的行直接丟掉,所以「圍欄裡的表」與「沒有表」從回傳值看不出差別。
- 標題 regex(像 `_HAZARD_H2_RE` 那種)計劃沒定義,例如 `## 預期值表(第一批)` 認不認、尾端零寬字元怎麼辦都不明。實測帶零寬字元的標題會回 `None`,被當成「沒有節」。
- 計劃第 3 點的格式錯清單(重複節、節裡沒表)與 S8 的枚舉不一致:S8 沒列「同名節出現兩次」與「節裡沒有表」。
- 後果:實作者可能直接把合併後的行當成一張表,第二節的列就悄悄併進指紋。
- file: `scripts/lumos:13774`

severity: major
blocking: 是,第 3 點規則自己宣稱的錯誤類別,借來的函式做不到,S8 又不綁。

### 5. 表的範圍與跳脫語法沒定義,表外的列和格會悄悄不進指紋

引句:「格與格之間用沒被反斜線跳脫的 `|` 分開」

- PRIOR-ART 為了「多的那格會悄悄不進指紋」特地不照 GFM,同一類洞在列的層級沒關:
  - 表中間出現空行、表後的散文、第二張表,哪些列算「這張表」沒寫。照 GFM,空行會結束表,後面的 `| S4 | ...` 就不在表內、不進指紋、不被檢查。
  - 「第二列是分隔列」的判法沒寫:分隔列幾格、能不能帶 `:---:`、是否也要四格。
- 跳脫語法沒寫完整:
  - `\\|` 算跳脫管線還是「反斜線加分隔」。
  - 格尾反斜線如 `C:\|`,作者寫不出以反斜線結尾的格值。
  - 條款欄是否先 strip 再比對 `S3`;`s3`、`S03`(程式裡 id 是 `f"S{int}"`,所以 `[S03]` 的 id 是 `S3`)、全形 `Ｓ３` 的取捨。
  - 表頭比對遇到零寬字元,作者看不出哪裡不對。
- S9 只綁 `\|` 一個案例。
- file: `scripts/lumos:14829`、`scripts/lumos:14852`

severity: major
blocking: 是,「整張表一個指紋」的邊界不明,簽核綁內容的前提就不成立。

### 6. 空格子可通過檢查並被簽核

引句:「每條新行為條款至少一列;來源欄去掉空白與標點後至少 4 個字(中文字、英文字母、數字都算)」

- 規則只檢查「剛好四格」、條款存在、來源 ≥ 4 字。
- `| S2 |  |  | 需求文件第2點 |` 輸入與預期都是空的,檢查全過。
- 條款欄空白的列(`|  | a | b | cccc |`)不是「寫了」不存在的條款,字面規則沒有任何一條擋它。
- 只有表頭沒有列時:若計劃全是 `[manual:]` 條款(計劃第 1 點明說放行),沒有新行為條款,0 列的表通過,簽核簽的是空字串的指紋 `e3b0c442…`。
- S8 的枚舉沒有這幾項。

severity: minor
blocking: 否,語意比對本來就列在「不做」裡,但這是格式層級就能擋的空洞。

### 7. 表指紋會碰撞,與「任一格改字就變」矛盾

引句:「一列四格用 `\x1f` 接起來,列與列用 `\n` 接起來,算 sha256」

- 格內容沒有跳脫,也沒有長度前綴。
- 我實測:`("S1","a\x1fb","c","來源四字xx")` 與 `("S1","a","b\x1fc","來源四字xx")` 的指紋相同。
- `\x1f` 不是 `_note_lines` 的換行,可以留在格裡。
- `str.strip()` 會吃掉格頭尾的 `\x1f`,但吃不掉零寬空格或 BOM。看起來一樣的兩張表指紋可以不同,簽核對不上時看不出差在哪。
- 名詞節與 S12 都宣稱「任何一格改了任何一個字就變」。

severity: minor
blocking: 否,碰撞要刻意塞控制字元;修法是格內跳脫或長度前綴。

### 8. S13 與 S7 的處理不一致:被連到的計劃表沒簽也會擋別人的推送

引句:「當推送範圍碰到先紅模式的計劃,而預期值表檢查不過(含整節刪掉),或現在的表指紋不在這份計劃任何一筆 expected-signed 事件裡時」

- S7 與第 2 點第三小點:計劃檔沒改、只因連到同一個 Systems 節點被拉進來的計劃,`high-red-missing` 只印提醒不擋。
- 第 4 點與 S13 對表檢查與簽核沒有這個豁免。
- `_spec_gate_push_scan` 的候選本來就含 `_spec_gate_push_candidates` 拉進來的 doing 計劃。
- 場景:A 的先紅計劃實作到一半、表還在改、未簽,`lands_in` 指向 `Systems/規格閘`。B 為了不相干的事推一個動到 `Systems/規格閘` 的提交,被 A 的 `expected-unsigned` 擋下,B 也簽不了 A 的表。
- 另外 S13 沒寫 status 範圍:`done`、`paused` 的先紅計劃被碰到時要不要查表,沒寫。
- file: `scripts/lumos:16277`

severity: major
blocking: 是,會讓別的會談無端被擋,而且與同計劃內 S7 的原則矛盾。

### 9. 治理帳統計相關的三個宣稱與程式不符

引句:「與一個隨機 token(gov 統計的去重鍵含 token,同一個提交簽兩次不會被折成一筆)」

- `_gov_row` 只對 `canary/blocked`、`code-loop` 的 `dispositions` 與 `recall-miss`、`fix-check` 帶 token,其餘 token 是空字串。
- 去重鍵是 `(commit, nodes, gate, kind, token, check)`。`signoff/expected-signed` 的 token 是 `""`,同一提交內人簽、AI 簽或簽兩次,在統計裡折成一筆。
- RETIRE-IF 看「AI 簽佔 100%」,先 AI 簽後人簽於同一提交時,人簽被吃掉。計劃只說 `_gov_row` 要帶出 `by`,沒提 token。
- 「`gov --stats` 的 signoff 段」不存在:`_render_gov_stats` 沒有按閘分段的 signoff 段(只有 `_KNOWN_GATES` 裡有 "signoff"),要新增。
- 第 195 行的效能宣稱說簽核事件「跟現有的留痕索引同一趟讀」。`_spec_gate_gov_index` 只取 `gate="spec-gate"` 且 `kind="spec-gate-record"`。簽核事件的 gate 是 `signoff`,要改成取兩個 gate,否則多掃一次 21 MB 的治理帳(實測約 0.16 秒)。
- file: `scripts/lumos:16999`、`scripts/lumos:15492`、`scripts/lumos:22229`

severity: major
blocking: 是,「分開統計 human 與 ai」是 S14 的驗收點,計劃寫的前提是假的。

### 10. `signoff --expected` 和現有旗標、前置條件的銜接沒寫

引句:「帶計劃、迴圈編號、表指紋、列數、`by`(human 或 ai)、簽的人(環境變數 USER,同端到端驗收放行)」

- 現有 `signoff` 已有 `--by`(誰確認的,自由字串)與 `--ref`,`cmd_signoff(env, node, note, by, ref)` 也吃它們。
- 新事件的 `by` 是 human 或 ai 的枚舉。`signoff P --expected --by Alice` 該忽略、拒絕還是當簽核人,沒寫。
- `.signoff-log.jsonl` 的列用 `by` 當人名,同一個欄名兩種語意。
- `--expected` 對下列節點要不要擋沒定義,對低風險計劃簽核會是無意義的事件:
  - 非先紅模式的計劃
  - 非計劃的節點
  - 設計審判定檔不存在的計劃
- `env.find(node)` 對任何筆記都找得到。
- file: `scripts/lumos:16533`、`scripts/lumos:72899`

severity: minor
blocking: 否,實作時會撞到,補一行規格即可。

### 11. 表格檢查、指紋計算、印出三步要用同一份讀到的文字,計劃只保證指紋早於印出

引句:「表指紋在印表之前算好,寫進事件的就是印出來的那一版」

- 計劃寫「先跑表格檢查」再算指紋再印表,沒要求三步共用一次讀檔。
- 檢查讀 v1、指紋讀 v2,就可能簽到沒檢查過的版本。多會談共用工作目錄時(全域規則有提)這是真實場景。
- 專案已有教訓,`_retro_read_bytes` 的文件註解寫「驗與算指紋都用這一份……若各讀一次,中間被換掉會記到沒驗過的內容」。
- file: `scripts/lumos:22289`

severity: minor
blocking: 否,修法是讀一次文字傳給三步。

### 12. 簽核事件的 `--note` 與簽核人沒有長度上限

引句:「比照規格閘留痕,不走 `_gate_event_fit` 裁長度」

- 規格閘留痕的免裁理由是 `tests` 清單不能被裁,這裡的欄位都是固定小欄位。唯一無界的是 `--note` 與 `USER`。
- `_gate_event_build` 把 `note` 同時寫進 `note` 與 `detail`,每個字寫兩次。
- 一筆幾百 KB 的備註會長期留在 21 MB、12 萬行的版控治理帳,每道讀帳的閘都要掃它。
- 端到端驗收放行有先例:`note.strip()[:200]`。
- file: `scripts/lumos:43521`、`scripts/lumos:1595`

severity: minor
blocking: 否,抄既有的 200 字截斷即可。

### 13. 互動簽核:表印在標準輸出、提問走 /dev/tty,而且 30 秒預設逾時會把人記成 AI

引句:「沒有互動終端或逾時,記 ai 並印一句」

- `_waive_origin_tty(prompt)` 只把提示字串送到終端。在 Claude Code 這類代理人跑的指令裡,標準輸出被擷取,但 `/dev/tty` 仍可能開得起來(⚠ 取決於環境,我沒在代理人環境實測)。人看不到表,卻在提問時按 y 記成 human。現有呼叫端(`scripts/lumos:38425`、`scripts/lumos:43517`)都把資訊放進 prompt 字串。
- `LUMOS_TTY_TIMEOUT` 預設 30 秒。表很大時人來不及讀完,也沒有按 n,事件被寫成 ai。人沒同意,卻被寫進統計的 ai 欄。
- file: `scripts/lumos:34193`、`scripts/lumos:34220`

severity: minor
blocking: 否,影響的是 human 與 ai 的歸屬統計,不影響放行。

### 14. 在先紅模式下重跑規格閘,「已做完」的快捷出口對 red_first 留痕不成立

引句:「沒過交給 `_spec_gate_low_not_red` 印同一套補紅燈做法」

- `_spec_gate_low_not_red` 的出口 (a) 要求 `_rec_plan_risk(rec) == "low"` 才會「測試現在綠 = 已做完,不用重跑」。
- 先紅留痕的 `plan_risk` 是 high,出口 (a) 永遠不成立。
- 實作完成後再跑一次規格閘(推送前遇到條款指紋過期也會要求重跑),測試全綠時,會落到 rc1 加「實作後才跑」的補空殼流程,即使同一個 `clause_sha` 的 `red_first` 留痕早已存在。
- 另一個接縫:設計審重審期間判定檔暫時 `rc != 0`,先紅模式關閉。這時重跑規格閘寫出的新留痕是「風險高、無 red_first」,會成為最新一筆,蓋過先前的 `red_first` 留痕。判定檔恢復 `rc 0` 後,S6 要求重新補紅。
- 計劃的判定檔讀法「照形狀檢查」,沒有比對 `all_row_shas`,凍結後再加審查輪也不會失效。
- file: `scripts/lumos:15361`、`scripts/lumos:68468`

severity: minor
blocking: 否,有補空殼的出口,只是繞遠路。

### 15. `_HIGH_RED_SINCE` 的值取「合併上主線那一刻」,寫程式時無法得知

引句:「值取本計劃合併上主線那一刻」

- 程式常數要寫在被審查、被代碼審綁版本的提交裡,合併那一刻在提交之後。
- 要嘛合併後再多一個提交(代碼審通過後只准再提交帳本,會與留痕綁版本的規則衝突),要嘛先猜一個時間。
- `_SPEC_GATE_SINCE` 的先例是事先訂好的日期。
- file: `scripts/lumos:13714`

severity: minor
blocking: 否,事先訂一個明確日期即可。

## 其餘各節

- frontmatter、decisions d1–d5、`pending_questions`:已讀,無 finding。
- 名詞:除上列幾條外已讀。
- 問題與最小解第 1 點的數字:我對審查帳重數,459 筆(原稿 458,帳今天又長了一筆)、134 份計劃(原稿 133)、最新留痕風險高 103 份(原稿 102)、跑出過紅 13 份、最新一筆紅 7 份。差一筆是今天新增的留痕,無 finding。
- 調研結論、第二批(第 7–9 點)、不做:已讀,無 finding。
- 回退:除第 14 條外已讀。
- 實務隱患:已排除三行與守衛面照實;天花板一到六都標明了,第 6 與第 14 條是它們之間的銜接。
- 審計修正紀錄:已讀,無 finding。

## 實務隱患逐類

- **併發**:有。
  - 簽核事件是 `open("a")` 追加到治理帳,與現有 `_gate_event` 同一模式,同機並行追加沒有新風險。
  - 多會談共用工作目錄時,表被另一個會談改動的競態見第 11 條。
  - 並行簽同一計劃兩次的統計折疊見第 9 條。
- **效能**:無嚴重問題。
  - `_loop_first_ts_key` 每份候選計劃整本讀審查帳,6 MB 約 0.08 秒;推送前有 N 份先紅候選就是 N 次,而 `_nogo_ctx` 已有現成索引可用。
  - 判定檔 395 份,最大約 108 KB。
  - 治理帳 21 MB,掃一次約 0.2 秒,簽核事件再掃一遍的說明見第 9 條。
- **資源**:
  - 治理帳增長,備註無上限見第 12 條。
  - 表列數、格長度也沒有上限,簽核時整張印到終端。
- **回滾**:
  - `_HIGH_RED_SINCE` 設遠未來的回退路徑,與已寫 `red_first` 的留痕的互動,計劃已寫明。
  - 回退後重跑規格閘會寫出無 `red_first` 的新留痕,與第 14 條同源,無額外風險。
  - 新事件追加進帳、回退後無害,同意。

## 圖譜節點牽連

- `Systems/guard-kill` 的兩條 ★INVARIANT★(rc 優先序、`--json` 純淨)不影響:計劃第一批不碰 `guard kill`,第二批才提到 guard-kill,而且只引用它的否決理由。
- `Systems/lumos-cli-lifecycle` 的 re-inject 不變量(sentinel 外的內容 byte-equal)不影響:計劃第 5 點只改注入範本裡 sentinel 之間的一句話,不改 sentinel 外的內容。
- `Systems/test-quality-evidence`、`Systems/test-quality-cli`、`Verification/測試品質第四輪修補驗證` 不影響:計劃只借 `_secev_junit_facts` 的概念,並明寫「只借不改」。

最嚴重 severity: blocker;blocking 條數:第 1、2、3、4、5、8、9 條,共 7 條(其中 blocker 1 條、major 6 條)。
