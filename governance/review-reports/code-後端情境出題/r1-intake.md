# code-後端情境出題 r1 收貨與處置

- 材料:r1-snapshot.patch(sha256 d9cb0dd362c5d999f2d7e23a474849abb136358b17f3696cb9937cd89daa6391),範圍 d919fadf765c27e8ffdc9db228880ccd06145bbe..c960f6de6abbe02b89cb3f97c193515deb1e7931。
- 八席:正確性、併發資源、邊界輸入、合約圖譜、通才回歸、架構對齊、資安(以上同門 sonnet)、外家 codex。全部交回後才一次寫進卷證。
- 引句核對:七席全錨;合約圖譜席 K6 的引句只有 9 字(低於 10 字下限),編排者在驗證紀錄開頭白話段 grep 到原句,判 HIT 採信。
- 修正提交:ed760edd、07313281(修正前 c960f6de)。

## 依根因分組(修之前先分組,每組一條統一規則)

| 組 | 根因 | 發現 | 統一修法 |
|---|---|---|---|
| 甲 | 待決問題解析太脆:看不懂就靜默丟、圍欄與標題變體、全形冒號、題目內文被當欄位、二次方回溯、測試名兩邊正規化不對稱 | B1 B2 B3 B4 B5 C1 C2 C3 K1 K2 | 只讀圍欄外的行;標題放寬、多節全收;像題目卻不合文法的行留下來報、規格閘擋;題目文字只取第一個標記之前;值不收方括號、欄位用切點線性切;測試名兩邊都走 slot_parse + _test_names_of |
| 乙 | 自寫第二份讀檔與條款判定 | A2 A3 | 改用 env_text、_visible_lines、_strip_inline_markup、_CLAUSE_LEAD_RE |
| 丙 | 實驗計分器多一套執行器、最後統計信外部一致率、統計與壞檔處理 | A4 X2 X3 R1 R2 R3 C6 S1 | 拿掉 run 子命令(連帶移除版本紀錄、跳過信任旗標、無逾時外呼);final 用標註當場重算 kappa;壞結果檔列成無效場;不判亂問的題 noise 必須是 0 |
| 丁 | 先寫程式判法誤判形狀(預先登記算法) | B8 B9 B10 C5 | 不事後改已登記算法;拿掉重用路徑(丙組);檔頭列出已知誤判形狀與重用前要換判法;72 場人工逐場核對 0 寫檔,記進驗證紀錄;REVISIT 寫在情境出題筆記 |
| 戊 | 探針只收回答又省略判準欄位會跑完才崩 | X1 | 判分改成欄位不在當空清單 |
| 己 | 新測試抓不到放寬或方向錯 | G1 G2 G3 G4 G6 C7 K3 | 補對照情境與非退化案例;每一條都用審查席的破壞手法驗過會翻紅 |
| 庚 | Kotlin Spring 觸發詞誤觸發與漏觸發 | B7 G5 | 撞 Android 自訂類名的字局部分大小寫加字詞邊界,或只認 Spring 專屬呼叫形狀;補 JdbcClient、MongoTemplate、@get:Transactional、@HttpExchange 等 |
| 辛 | 讀檔錯誤處理不一致 | C4 R4 A1 | 照規格閘:接 UnicodeDecodeError、訊息帶「擋下:」 |
| 壬 | 文件與筆記漂移 | B6 K4 K5 K6 K7 K8 G7 S2 | 逐處改;探針筆記補「題目與受測 repo 要自己審過」RULE 與 REVISIT |

## 重現表(編排者自己跑過;HIT=重現得出現象)

| id | 席 | 重現方式 | 結果 | 去向 |
|---|---|---|---|---|
| B1 | 邊界輸入 | parse 配 blocking_gate 餵 `[狀態:待查。]`、`[階段:需求/架構]`,修前回空 | HIT | 折(t_backend_qo_parser_robust ⑦、t_backend_qo_gate_fail_closed ②) |
| B2 | 邊界輸入 | `1. [Q1]`、`- [ ] [Q3]`、`### 待決問題`、兩節、圍欄內 `#` 等,修前回 [] 或 None | HIT | 折(parser_robust ①–⑤) |
| B3 | 邊界輸入 | `單元測試:要補嗎` 修前 text='單元' | HIT | 折(parser_robust ⑧⑨⑩) |
| B4 | 邊界輸入 | 條款 `[test: py:t_x]` 與題目 `測試: py:t_x` 修前對不上 | HIT | 折(parser_robust ⑫⑬⑭) |
| B5 | 邊界輸入 | 6 萬空白加 4 萬個沒闔上的標記,修前 70.7 秒 | HIT | 折(parser_robust ⑮,修後兩秒內;大型輸入另量 1 萬題 0.67 秒、峰值 14MB) |
| B6 | 邊界輸入 | 程式註解寫「決策檢查放規格閘與 lint」,實作只在 lint | HIT | 折(註解改正) |
| B7 | 邊界輸入 | `class RestClient(…)`、`DatabaseClient`、`@Lock("x")` 修前亮題;`@get:Transactional` 等修前不亮 | HIT | 折(t_stack_questions_kotlin_spring_triggers ⑤⑥) |
| B8 | 邊界輸入 | heredoc 內文、`sed s/a/b`、字串裡的 `>` 修前判先寫程式 | HIT | 折(丁組:不改登記算法、拿掉重用路徑、檔頭列形狀、72 場人工核對 0 寫檔) |
| B9 | 邊界輸入 | `FOO=1 gradle test` 等修前第 2 版判 False | HIT | 折(丁組,檔頭列為漏算形狀) |
| B10 | 邊界輸入 | `docs/` 套件裡的 .kt、`.MD`、`.txt` 判法偏差 | HIT | 折(丁組,檔頭列為誤判形狀) |
| B11 | 邊界輸入 | `CLAUDE_CODE`、`cd qo-a`、`[甲乙]組` 吃到中文詞 | HIT | 放行(理由見下) |
| C1 | 正確性 | `[狀態:待査]` 錯字修前閘不擋 | HIT | 折(同 B1) |
| C2 | 正確性 | 圍欄裡的 `## 待決問題` 修前被當真節 | HIT | 折(parser_robust ③) |
| C3 | 正確性 | `測試:t_foo。` 修前帶句號 | HIT | 折(parser_robust ⑭b) |
| C4 | 正確性 | 非 UTF-8 計劃 `--stage` 修前吐追蹤 | HIT | 折(t_backend_qo_stage_order_and_cap ⑧) |
| C5 | 正確性 | `grep -rn '=> handler' src/` 修前判先寫程式 | HIT | 折(丁組) |
| C6 | 正確性 | 非亂問題 noise 差 >1 時 merge 要一筆沒人產的仲裁 | HIT | 折(test_check_labels_noise_must_be_zero_outside_noise_scenarios;現有標註都填 0) |
| C7 | 正確性 | 刪掉設上限那行測試照綠;lint 開關沒驗結束碼;⑤ 新版比新版 | HIT | 折(test_answer_max_flag_really_sets_cap、t_backend_qo_lint_gate_rc、stage ⑤ 改寫,各自破壞驗過翻紅) |
| R1 | 併發資源 | cmd_run 呼叫探針沒逾時 | HIT | 折(run 拿掉) |
| R2 | 併發資源 | cmd_run 丟退出碼、沒鎖 | HIT | 折(run 拿掉) |
| R3 | 併發資源 | `{"results": []}` 修前 score 崩 IndexError | HIT | 折(test_load_runs_skips_malformed_result_file) |
| R4 | 併發資源 | 同 C4 | HIT | 折(同 C4) |
| K1 | 合約圖譜 | `1. [Q1] … [阻塞]`、`- Q2 …` 修前回 [] | HIT | 折(同 B2) |
| K2 | 合約圖譜 | 同 C2 | HIT | 折(同 C2) |
| K3 | 合約圖譜 | stage ⑤ 新版比新版 | HIT | 折(⑤ 改成同內容只換節標題比對,破壞驗過翻紅) |
| K4 | 合約圖譜 | 計劃 A 塊寫決策檢查「只放規格閘與 lint」 | HIT | 折(改成只放 lint、規格閘只看狀態) |
| K5 | 合約圖譜 | reference.md 引用不存在的「交付前證據檢查」 | HIT | 折(改寫) |
| K6 | 合約圖譜 | 驗證紀錄開頭仍寫「接線與否等使用者裁」(引句 9 字,grep 命中) | HIT | 折(改寫) |
| K7 | 合約圖譜 | commands/02、05、INDEX 與子命令一句話表沒有 --stage 與新擋因 | HIT | 折(四處補) |
| K8 | 合約圖譜 | 風險面表漏「提交」 | HIT | 折(補) |
| G1 | 通才回歸 | 配對差方向寫反 TestQoAblation 照綠 | HIT | 折(test_final_direction_and_arm_attribution;方向、亂問與先寫程式記錯組都驗過翻紅) |
| G2 | 通才回歸 | 拿掉 blocking 條件、縮成只擋需求、跨篇連結當本篇,測試照綠 | HIT | 折(spec_gate ⑦⑧、gate_fail_closed ③,前兩種破壞驗過翻紅) |
| G3 | 通才回歸 | 拿掉 shuffle、拿掉遮罩三段照綠 | HIT | 折(test_blind_order_is_shuffled_not_sorted、test_mask_covers_arm_paths_and_group_words,破壞驗過翻紅) |
| G4 | 通才回歸 | kappa 換成 2*po-1、交付率算進 absent 照綠 | HIT | 折(非退化案例、test_delivery_rate_excludes_absent,破壞驗過翻紅) |
| G5 | 通才回歸 | `class AppWebClient : WebViewClient()` 修前亮 kt-springhttp | HIT | 折(同 B7) |
| G6 | 通才回歸 | 同 K3 | HIT | 折(同 K3) |
| G7 | 通才回歸 | 效能檢核目錄寫 kt=8 | HIT | 折(改 10) |
| A1 | 架構對齊 | `_pitfalls_stage` 讀檔錯誤沒「擋下:」 | HIT | 折(同 C4) |
| A2 | 架構對齊 | `_env_note_text` 重複 `env_text` | HIT | 折(刪掉改用 env_text) |
| A3 | 架構對齊 | `_pq_clause_tests` 與解析器不走 `_visible_lines` | HIT | 折(改走既有判定) |
| A4 | 架構對齊 | `qo_ablation.py run` 是第二套執行器 | HIT | 折(拿掉,檔頭寫明要重跑去擴充既有那套) |
| A5 | 架構對齊 | 探針 main 改寫模組全域上限 | HIT | 放行(理由見下) |
| S1 | 資安 | cmd_run 無條件加跳過信任旗標 | HIT | 折(run 拿掉) |
| S2 | 資安 | 卷證裡受測 AI 在主機起了容器 | HIT | 折(探針筆記 RULE 與 REVISIT) |
| S3 | 資安 | 卷證含本機絕對路徑 64 行 | HIT | 放行(理由見下) |
| X1 | 外家-codex | collect_only 省略 expect 時 grade KeyError | HIT | 折(test_collect_only_without_expect_key_grades_without_crash) |
| X2 | 外家-codex | run 的版本紀錄沒含題庫與受測 repo 版本 | HIT | 折(run 拿掉,不再有續跑) |
| X3 | 外家-codex | final 採信任意 agree 檔的 kappa | HIT | 折(test_final_recomputes_kappa_and_ignores_stale_agree) |

## 放行理由(都是 minor)

- B11:實驗已結束、盲評包不會再產;兩輪實際發出去的評分包掃過模型名、組別資料夾名與「甲組/乙組」字樣 0 處漏遮(記在驗證紀錄)。遮罩是預先登記的一部分,事後不改。
- A5:模組全域上限只在 main 解析參數後設一次,之後全是讀取;專案已有同形狀先例,席位自己也判 minor。新測試已釘住「旗標真的設進去」。
- S3:只露出本機使用者名稱,沒有憑證;同一個名字本來就在提交作者欄公開。那些檔是外部審查與原始輸出的原文證據,改了等於改證據。

## 辯方

- 沒派。存活的 major(B1 B2 B8 K1 G1 G2 A2 A3 A4 X1 X2 X3)編排者都自己重現過、而且多席獨立一致或有可執行證據,照規則直接折。

