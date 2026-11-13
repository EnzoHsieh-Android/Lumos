preflight-4: ran

# 情境題答案要引規格出處與回寫循環 r1 收貨紀錄

## 首輪前掃(派席前,sonnet 一席照固定四類清單)

- ② 壞引用:0 條(13 支函式、8 篇節點、三筆舊否決出處都驗過存在)。
- ①③ 未定義的詞 5 條、範圍自相矛盾 10 條:直接修真檔,不算 findings。
- ④ 機械宣稱驗語意 9 條,修真檔、逐條留痕如下(本計劃沒有「核心裁定」節,沒有升級成正式 finding 的):

| # | 修改前 | 讀到的實際程式行為 | 修改後 |
|---|---|---|---|
| ④-1 | 「表態當下與推送前核對用同一支 `_spec_gate_push_candidates`」 | 那支要載圖譜(`env.notes`、`_impact_home_map`),而 code-loop 推送前刻意不載圖譜(scripts/lumos 註解自稱 vault-free) | 〈用詞〉對應計劃名單:用 `_drift_tree_env` 從被推版本的樹建記憶體圖譜(`Env.from_texts`)再呼叫;只在有答適用的列時才建 |
| ④-2 | 「條款本文用 `_clause_body_of`(剝掉 `[SN]`、`[test:]`、`[manual:]`)」 | `_clause_body_of` 最後呼叫 `_strip_inline_markup`,連反引號包住的字一起剝掉,引句含 `` `flatMapLatest` `` 永遠比不上 | 〈用詞〉新增「出處本文」:只剝清單記號與三種標記、保留反引號裡的字;預期值表加一列驗這件事 |
| ④-3 | 「條款用 `clause_bindings` 解析」 | 只回定義行行號、不回本文,另要四個測試設定參數 | 〈用詞〉寫明照 `_expected_clause_sets` 傳空值、用行號回原文 |
| ④-4 | 「表態事件的 `written_at` 在生效日之前…」 | `_codeloop_disp_from_event` 只回 head_sha、branch、ts、dispositions,丟掉 written_at | 〈用詞〉生效日:改讀取函式一起回傳、往下傳;明訂判作者表態事件,盲判跟著作者 |
| ④-5 | 「預期值表列用 `_expected_table` 解析」 | 任一格式問題整張回 None;儲存格做 NFC | 〈用詞〉改用 `_h2_section_lines` + `_expected_split_cells` 取列;引句比對兩邊都先 NFC;回寫時 consent 原文的 `\|`、換行先換掉 |
| ④-6 | 範圍 5 只列 material、answer_format、validate | `_KT_BJ_ROW_KEYS`、`_kt_bj_vote_ok`、`_kt_bj_event_ok`、`_kt_bj_cells_add` 不認新欄,帶新欄的盲判折帳時整筆消失 | 範圍 5 列齊四處;新增條款 S12 守來回不丟欄 |
| ④-7 | 「用 guard kill 同一套隔離工作樹與判定」「`--kill-old` 在段範圍內恰好一次」「`killed` 就寫回」 | 判定內嵌在 `cmd_guard_kill`、只吃筆記宣告的配方;隔離樹照 HEAD 建;原文判整檔恰好一次;`killed` 也可能帶弱證據(run_cmd 沒有 {method} 等) | 範圍 4:抽一支跑臨時配方的共用函式(先例 `kill-add --try`)、要求相關檔已提交、改整檔恰好一次、只認沒有弱證據的 killed;配方身分寫明代入計劃與條款編號 |
| ④-8 | 「origin 三種、同錨點簽名的做法」 | 既有 `_waive_origin_tty` 沒終端記 ai 照收,沒有 chat、consent | 〈用詞〉人裁:值只有 human、chat;寫明是新行為不沿用;終端與 consent 都有時記 human |
| ④-9 | 「段身分由 `_kt_sit_text_segments` 這一族算」 | 那支是型錄自檢的薄包裝,推送前走 `_kt_situation_segments` | 改指 `_kt_situation_segments` |

前掃③-7 另有一條設計取捨,一併改:原本「`applies` 不論真假都要有 `spec`」,但候選列大多不適用、而殺傷力的「換寫法」只對適用列有意義;改成只有答適用的列必引出處,不適用列靠既有盲判票面抓(〈天花板〉5 寫明抓不到的情形)。③-4/5/6 一併改:出處比對規則改成「作者的出處要有一位判適用的盲判附和」,票面規則不動,擋優先於提醒。

## 派工與收貨

- 六席(正確性、邊界、整合、資源、簡化、架構對齊),sonnet,審 `r1-snapshot.md`(166 行,spec-freeze c919111b7603)。圖譜鏡頭:正確性、邊界、資源、簡化、整合都回報有附到 [[Systems/guard-kill]] 的兩條合約,其餘節點只附名。
- 報告從逐字稿原樣存檔。report-normalize --write:正確性 13 處、整合 12 處、資源 9 處、架構對齊 6 處(純格式搬移);邊界、簡化原本就是正規化格式。架構對齊席第一次交的結尾用了「- major:」「- minor:」列表標籤,退回該席,只改結尾成散文後重交(其他內容未改)。
- quote-check(對 r1-snapshot.md):正確性、邊界、資源、簡化、架構對齊全數錨定;整合 11 句有 1 句錨不到(g2 的引句內層又包了「」,被截在「答」),見下表機械重現。
- 席位都沒動 repo(`git status` 只有本輪卷證與治理帳)。

finding 編號:正確性 c1–c13、邊界 b1–b12、整合 g1–g12、資源 z1–z9、簡化 s1–s9、架構對齊 a1–a6(照各席報告的條目順序)。

## 機械重現

| 發現 | 命令 / 讀的程式 | 結果 | 判定 |
|---|---|---|---|
| c6、b3、g4、z1、a1(名單讀磁碟) | 讀 `_spec_gate_push_candidates`:正文用 `(env.vault / prel).read_text` | 屬實 | HIT |
| c2、b1、g1、s2(段放行不解新擋) | 讀 `_kt_sit_check` docstring 與 `_kt_bj_check` 的 waived 用法 | 屬實 | HIT |
| c3、b2(出處不同取不到仲裁材料) | 讀 `_kt_bj_pick_rows`:票面相同就略過 | 屬實 | HIT |
| c4、g5(人裁後盲判格子凍結) | 讀 `_kt_bj_cells_add`:每格只認第一筆 | 屬實 | HIT |
| c1、g7(人裁條款過不了風險低規格閘) | 讀 `_spec_gate_twoway_static`:keeps 要測試早於計劃第一次提交;沒標 keeps 要紅 | 屬實 | HIT |
| c7、b5(單一反引號吞掉 [test:]) | 兩席各自跑 `clause_bindings` 探針得 untagged | 屬實(引兩席輸出) | HIT |
| g2(答不適用是捷徑) | 讀 `_kt_bj_arbitrate`、`_kt_bj_check`:多數判適用只進 notes | 屬實;引句被截是格式問題,原文「答「不適用」靠的是盲判獨立判一次」在快照〈範圍〉1 | HIT |
| g3、c9、b8(形狀函式被型錄自檢共用) | 讀 `check.py` `_sit_first_pass` 呼叫 `_kt_sit_row_check` | 屬實 | HIT |
| g8(不抽共用的註解) | 讀 scripts/lumos `_kill_recipe_judge` 一帶的「不改它的判法」註解 | 屬實 | HIT |
| z2(Ctrl-C 不收程序群組) | 讀 `_kill_run`:只接 TimeoutExpired | 屬實 | HIT |
| z6(材料大小) | 席位實測 177 份計劃、19 萬字 | 採信席位實測 | HIT |
| b6(空白湊字數) | `re.sub(r"\s+"," ","　"*10)` 得單一空白 | 屬實 | HIT |
| a3、s7(origin 第二套) | 讀 `_waive_origin_tty`:回 human/ai/None | 屬實 | HIT |
| 其餘(c5、c8、c10–c13、b4、b7、b9–b12、g6、g9–g12、z3–z5、z7–z9、s1、s3–s6、s8、s9、a2、a4–a6) | 讀計劃快照對應段落 | 屬實(設計缺口,不需跑) | HIT |

## 分組與處置(61 條:折入 61、放行 0)

1. 對應計劃名單(c6、b3、b4、g4、z1、z5、a1):改 `_spec_gate_push_candidates` 讀 `env_text`、`_impact_home_map` 快取鍵加版本;名單算不出一律擋;同一次核對只建一次圖。新條款 S6、S7。
2. 出口(c2、b1、g1、s2):段放行也蓋過本案新增的出處擋;缺段缺列照擋。新條款 S5。
3. 盲判出處比對(c3、c4、b2、g5、g10、s1、s4、c10、c11):拿掉「作者出處要有盲判附和才放行」——兩個模型投票擋違反表態閘既有裁定(g10),仲裁材料挑不到(c3)、人裁後格子凍結(c4)。改成出處不同只提醒;盲判只填 `spec` 不填引句(s4)。
4. 誘因反向(g2、c13a):新增捷徑擋——作者答不適用、盲判判適用並填了機器驗過存在的出處就擋。S15。
5. 預期值表(s3、c5、c10、c11、b7、g12 部分、z9):預期值表列不當出處、人裁不寫預期值表;連帶拿掉 consent 跳脫與 variant 欄的問題。a4 那半(另一套表格讀法)隨之消失。
6. 規格閘認人裁條款(c1、g7):規格閘讀治理帳,條款文字雜湊對得上的人裁條款當既有行為。S13。
7. 寫回機制(c7、c8、b5、z3、z4、b11、g6、z7):條款文字禁字與反引號成對、`_clause_grammar`、寫入前全文重跑 `clause_bindings`;殺傷力後才拿鎖、鎖內重讀算號(全文最大號加一);先寫計劃再記帳、帳失敗回 1 不叫重跑;只查簿記以外的未提交改動;記驗證時 HEAD;`--branch`、確認畫面內容、出處剖析規則寫明。S11、S12。
8. 殺傷力(z2、g8、g9、b10、s9、c13b、a2 旗標名):不抽共用,改 `cmd_guard_kill` 加選用參數 `recipes_override`;`--old` 要在這一段起訖行內、新舊兩邊是同一列不同觸發字;Ctrl-C 收程序群組、開殘骸清理;kill-log 帶 source、兩個讀者略過;一次性證明寫進天花板;旗標改 `--file/--old/--new`。S9、S10、S19。
9. 生效日與形狀共用(c9、b8、g3、z8 時區):形狀與核對函式加 `spec_rules` 參數預設舊制;取 written_at 日期部分、缺就用 ts、都缺當新制。S18。
10. origin 與指令位置(a2、a3、s7、z8 逾時):人裁改頂層指令 `lumos situation-rule`;沿用 `_waive_origin_tty`,ai 要帶 consent,不另加 origin 值。
11. 引句(b6):正規化後用 `_real_chars` 數實字。
12. 材料大小(z6):`specs` 只放相關計劃、上限 80,000 字、超過拒絕產材料。
13. 文件、登記、統計(g11、g12、c12、s5、s6、s8、a4 落點、a5):`未寫` 值拿掉(空=沒出處);擋下訊息不查帳;統計改成對得上 RETIRE-IF 的四個數;situation-rule 登記進 `LOOP_NOT_CLOSE_EVENTS` 與 `_GOV_FIELD_TYPES`;手冊、子檔、表態閘筆記、docstring 列進範圍 8;lands_in 加 guard-kill、表態閘補負責範圍。
14. 新舊版本(b9):寫進〈實務隱患〉,推上主線後 `lumos update`。

15. 測試涵蓋(b12):原想附理由放行,但同輪整合席報 blocker、整輪不准放行,改折:計劃新增範圍 9,列出條款以外各拒絕情形與邊界由實作時的單元測試覆蓋。

## 先查世界

- PRIOR-ART(組 3、4,盲判出處比對):本 repo [[Systems/棧別提問表態閘]] 既有裁定「盲判是模型判斷,先提醒、量過誤報才升擋」;外部 CiteGuard(https://arxiv.org/pdf/2510.17853v3 )顯示 LLM 判引用對錯召回低。採用:出處只由機器驗存在與逐字、兩模型不一致只提醒;捷徑擋的依據是機器驗過的條款原文。
- PRIOR-ART(組 6,人裁條款不要求先紅):Michael Feathers 的特性測試(characterization test)是替既有行為事後寫、一寫就綠的測試(https://en.wikipedia.org/wiki/Characterization_test );本案人裁條款描述的是已實作行為,用殺傷力證明取代「先紅」。採用。
- PRIOR-ART(組 8,殺傷力):沿用 [[Systems/guard-kill]] 宣告式壞法與七態;Google 變異測試只在審查改到的程式上變異(https://research.google/pubs/pub46584/ ),對應「`--old` 要在這一段」。
- 其他組(名單、出口、寫回機制、生效日、origin、引句、材料、文件):內部口徑對齊既有函式與慣例,沒有另外上網查。
- 這是第一輪,沒有連兩輪出現的根因組,不查方向。
