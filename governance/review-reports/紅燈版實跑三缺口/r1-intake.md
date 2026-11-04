preflight-4: ran

# r1 收貨紀錄(紅燈版實跑三缺口)

## 前掃(首輪,2026-11-03,sonnet 一席,只讀;實驗 repo 建在 /tmp/lumos-seat-work/紅燈版實跑三缺口/preflight/,完成後已刪)

①②③ 與存在類命中直接修真檔(名詞段、lands_in 補 Systems/room-guard 與 Systems/bound-tests-gate、PRIOR-ART 補借用 `_lens_git` 與判法、回退與實務隱患的措辭、refcheck 一處把消費專案資料夾改成不加反引號)。

語意類命中(修真檔,修改前→後):

| # | 宣稱 | 前掃結果 | 修改前 → 修改後 |
|---|---|---|---|
| P1 | 切參數改照遮罩判,字元常值、三引號、反引號都由同一支掃描處理 | 部分成立:遮罩掃描不認 Kotlin 字串模板裡的巢狀引號,`"${foo("a,b")}"` 現況碰巧切對、只看遮罩會切錯(退步) | 「照那份文字找頂層逗號與括號」→「遮罩那一格是逗號、遮罩與原文兩邊的括號深度都是 0 才當分隔」;S1 加「字串模板切法跟現況相同」 |
| P2 | 舊留痕在實作完成後重跑規格閘不會被重寫(條款沒變、測試綠就不寫) | 部分成立:還要最新留痕風險低、條款指紋與門規則版本相同、沒有別種沒過 | 問題 2 括號補齊條件並指到 `_spec_gate_low_not_red` |
| P3 | 指紋不符且計劃已完成那條路,同名引用找不到就照舊 | 部分成立:完成後條款改綁到別的平台時,照現在條款補平台會補錯 | 「其餘照舊」→「留痕沒過期才看現在條款補平台;指紋不符的已完成那條路不補」;S3 同步 |
| P4 | `_spec_gate_record` 改寫 tests 欄 | 成立但簽名拿不到平台,`names` 又餵給雙向判定 | 做法 2 寫明由呼叫端另傳 `_spec_gate_items` 的(條款、平台、方法),不改 `names` 形狀 |
| P5 | `git check-ignore -v` 列出蓋到的規則 | 部分成立:否定規則 `!` 也會印出、rc 0;已追蹤的檔 rc 1;規則可能在 .git/info/exclude 或全域設定;上層目錄被忽略時加否定規則無效 | 判法改成「先判已追蹤、再 `-q` 判忽略、被忽略才 `-v` 取規則」;改法措辭改成「加 `!docs/.governance-log.jsonl` 或收窄規則;上層目錄被忽略要改那條規則」 |
| P6 | 孤兒提醒改固定身分字、措辭換了指紋不變 | 成立,但會讓既有放行失效一次 | 寫明紅燈版這批還沒上主線、沒有既有放行 |
| P7 | 只修孤兒那句提醒 | 漏同族:「工作目錄有還沒提交的紅燈版檔:請 git add 那支檔與治理帳」在治理帳被忽略時同樣錯 | 做法 3、S4 併入那一句,同樣改固定身分字 |
| P8 | 修補只擋未來的假逃逸 | 考場已寫入的兩筆會污染撤除條件的分子 | 新增做法 4:重跑考場時用 `lumos loop escape --withdraw` 撤回;S6 的人工驗收寫明 |

沒有動到「核心裁定」的命中(本計劃沒有核心裁定節)。

## 收貨(四席)

- 四份席報告從各席逐字稿原樣存檔(不從完成通知抄);四份都已是正規化格式。正確性席首交時第 5 行總結句寫了「沒有 blocker 或 major」,被格式檢查判成總結句藏更高等級,退回該席只改那一句後重交、重存。
- 引句:邊界、整合、架構對齊三席全數錨定;正確性席整份沒有「引句:」格式行(抽不到),只記普通帳、不當載體;它的 6 條都是 minor,且都跟其他席同組。refcheck:整合席一處 `docs/.gitignore` 找不到,那是講消費專案的路徑,不是引用本 repo。
- 四席交回期間 repo 沒被席位改動:`git status` 只有四份新報告、派工單、快照與我自己跑工具寫的兩本帳;`git reflog` 頂端都是編排者自己的提交。邊界席的暫存目錄(/tmp/lumos-seat-work/紅燈版實跑三缺口/邊界-sonnet)收齊後已刪,其餘三席沒留。

編號:正確性 F1–F6 記 C1–C6;邊界 1–9 記 B1–B9;整合 F1–F12 記 I1–I12;架構對齊 finding 1–7 記 A1–A7、落點那條(bound-tests-gate)記 A8。共 35 條;major 7 條(B1、B2、B3、I1、I2、I3、I4),其餘 minor。

## 編排者重現

| id | 案例 | 結果 | HIT/MISS |
|---|---|---|---|
| B3/I4/C6 | 考場 `ANDROID_SERIAL=NOPE00000 ./gradlew :app:connectedDevDebugAndroidTest …` | rc=1、3 秒,輸出 `DeviceException: Connected device with serial 'NOPE00000' not found!`;Kotlin 棧讀不出支數,照退出碼判紅 → 推送閘會擋並記逃逸 | HIT |
| B2/I1/C1 | `_tg_call_parts('assertEquals(")", lexer.next().text)')` 等(席位已用真函式實跑,編排者讀 `_rg_split_args` 確認只數原文括號) | 一個參數,`_tg_split_first_arg` 回 None | HIT |
| B1/C3/I7 | `_split_test_ref` 遇 `fee: rounds up`(多平台)丟 `_TestRefPrefixError`;`_spec_gate_push_one` 呼叫處沒有接 | 讀碼成立(席位實跑) | HIT |
| I2 | docs/.gitignore 有規則時根目錄的否定行蓋不過去(席位暫存 repo 實測;git 的忽略規則以較深層的檔優先,官方文件同) | 成立 | HIT |
| I3 | 現行孤兒提醒含「不要刪這支檔」,t_tq_guard_redbase_* 有斷言釘它;r1 快照的新措辭沒有 | 讀快照成立 | HIT |

## 根因分組與處置(全數折入,沒有放行,沒有重現不到的)

| 組 | 根因 | id | 處置 |
|---|---|---|---|
| G1 | 切參數只數原文括號;只看遮罩又會在模板巢狀引號、原始字串尾端連續引號讀錯 | B2、I1、C1、C2、B4、I5、A5、A7 | 做法 1 改成照剝過的文字判(兩處切參數都帶,參數叫 stripped,深度算法同 `_rg_bracket_map`),剝字串掃描讀錯的兩種情形(字串沒收尾、`${` 段內不配平)退回現況;S1 補 `")"`、`'('`、`"1) 項目"`、串接寫法與兩種退回案例;相容段寫多列候選;REVISIT 綁漏報回報 |
| G2 | 留痕丟了平台,而且預設平台寫裸名在名字含冒號或預設平台改了時讀錯 | B1、C3、C4、I6、I7、I8、A1、A6、B9 | 做法 2 改成多平台一律寫前綴、清單由 `_spec_gate_prepare` 另產(同 names 集合)、舊留痕照 `_spec_gate_push_stale` 回傳的條款綁定補平台(不另掃正文、不重算)、平台不在設定裡不丟例外;寫明為什麼不用 items 形狀;S2、S3 改寫 |
| G3 | 修好平台後,沒接裝置照退出碼判紅並記假逃逸 | B3、I4、C6 | 新增做法 3:kotlin-junit、java-junit 多一個環境樣式(AGP DeviceException),判弱證據、照擋、不記逃逸;新增 S4;實務隱患加「資源」一條(裝置上會裝移 app);寫「不加它的最小解為什麼不夠」 |
| G4 | 忽略提醒的判法與改法不夠準,新措辭弄丟原本的安全指示 | I2、I3、A2、A3、A4、B5、B6、C5、I9、I10 | 做法 4:共用一支三態判法放比對工具側、`_lens_git_dl` 帶截止時間、判不了照舊措辭、`-v` 那段不拆欄位只清洗、quote=True;改法指到規則所在的檔並附自查指令;保留「不要刪」與「git add 那支檔」;身分字用 ASCII;doctor 多一行(寫最小解為什麼不夠);S5、S6、S7 |
| G5 | 身分字回退方向沒算 | B8、I11 | 回退節寫明回退身分字會讓期間的放行失效一次;實務隱患不可逆條同步 |
| G6 | 人工驗收步驟不能照做、驗不到 S2 | B7、I12 | 做法 5 寫完整撤回指令;S8 列六步,分清哪步驗 S2、哪步驗 S3 |
| G7 | 落點多列一篇 | A8 | lands_in 拿掉 Systems/bound-tests-gate(推送前驗收的描述在 Systems/規格閘) |

## 先查世界(r1 修補前,2026-11-03)

- G1:Kotlin 官方文法認字串模板靠模式堆疊(`${` 推進一層,https://kotlinlang.org/spec/syntax-and-grammar.html);ANTLR 版 Kotlin lexer 也是 mode stack。本案不另寫有堆疊的掃描(那是第二套詞法),只在單層掃描會讀錯的情形退回現況。
- G3:Bazel 的測試狀態把 REMOTE_FAILURE、FAILED_TO_BUILD、BLAZE_HALTED_BEFORE_TESTING 跟 FAILED 分開(https://bazel.googlesource.com/bazel/+/HEAD/src/main/protobuf/test_status.proto),基礎設施沒跑起來不算測試失敗;本案照這個分法。
- G4:git 的忽略規則以較深層目錄的檔優先、同檔內後面的規則蓋前面(gitignore 官方文件);所以改法要指到蓋到的那支檔,不能一律叫人在根目錄加否定行。
- G2、G5–G7:本專案內部的格式、回退與文件同步,沒有外部做法要比。

## 折入後鏡像核對(sonnet 一席,只讀;暫存實驗 repo 已刪)

35 條都找到對應改動,A7 只處理一半;另點出鏡像段沒跟上 7 處、折入自帶的未查證宣稱 9 處、條款可判性 3 處,共 20 處,全數改進計劃:

- A7:`stripped` 路徑不另數深度,直接照 `_rg_bracket_map(stripped)` 的配對跳過括號內部(配括號只剩一套)。
- 最小解改成五項、白話段補「修好後才浮現的那件事」;RETIRE-IF 改用做法編號並分清哪些跟著撤;名詞補「弱證據」「環境沒跑起來」;PRIOR-ART 補 gitignore 優先序出處;lands_in 補 doctor 那段的家 Systems/reversibility-governance-ledger。
- 自查指令改看 `git check-ignore -q` 的退出碼(席位實測:照否定規則改完,`-v` 仍印那一行 `!` 規則)。
- 「只在真有孤兒時問、一次最多問一次」改成傳「第一次用到才問」的取值函式,`_tg_rb_metas` 新參數預設 None。
- 孤兒提醒改成重要指示放前面、規則放最後(席位實算:全域忽略檔路徑時 304 字,超過 `_tg_cand` 的 300 字上限,原措辭會砍掉「不要刪」);S7 加 150 字規則的案例。
- `_TG_WHY` 的「該確認」改成不分情形都說得通。
- `_spec_gate_push_stale` 回傳計劃文字與綁定列,`_spec_gate_push_one` 用手上的 split/default 呼叫 `_spec_gate_items`。
- 舊留痕名字整串先逐字比現在條款,含冒號的舊名字才不會卡在「平台不在設定裡」(那種留痕重跑規格閘也不會重寫)。
- doctor 另起一段、措辭分開「CI 讀不到代碼審留痕與表態」與「乾淨 clone 推送前找不到規格閘留痕」(席位確認 CI 不跑 --push-check)。
- 環境樣式放 `TEST_PROFILES` 的新欄位 `env_missing_re`,不放 `_RAN_EVIDENCE`(那張表另有讀者)。
- 做法 3 寫明判法的四個呼叫端(規格閘、相依回歸、推送前、修正關卡第 4 項)各自的影響。
- 實務隱患「資源」寫明為什麼不加機械擋,附 REVISIT。
- S2 補懸空引用與 manual_only 不變;S1 改成可觀察的列出結果,退回案例拆成 S2;S3 拆成 S4、S5;S5 拆成 S7、S8(照做後 `-q` 回 1)。條款由 8 條改 11 條,S11(人工)的六步對應新編號。
