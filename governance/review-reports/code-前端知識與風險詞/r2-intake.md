# code-前端知識與風險詞 r2 修正紀錄

修後版本 f14f6808 的七席報告。編號照各報告順序:正1–正5、邊1–邊7、資1、整1–整4、通1–通5、架1、安1–安2。架1 照編排者裁定附理由放行(四處 e2e 判法用途不同,已在 `_TEST_INFRA_PATH_RE` 旁註解寫明分工),修正紀錄不收;其餘全部折入,其中兩條有部分輸入機械重現不成立(見文末駁回表)。

| 根因組 | 條目 | 修法 | 守它的測試 | 歸因 |
|---|---|---|---|---|
| GA e2e 路徑排除誤殺 e2e 底下的 lib/src | 通1 邊2 正1(major)、通3、安1 | 排除只限 e2e 之上的 src/、lib/(`^(?!(?:[^/]+/)*?(?:src\|lib)/(?:[^/]+/)*?e2e/)`);新增 `_is_test_infra_file`,棧別鍵與 claims 跳過同一支判斷(e2e 底下的 .kt 照掃 claims);安1 的 src/crypto/e2e 已不算,不在 src/lib 底下、名字剛好叫 e2e 的產品資料夾寫成天花板 | t_test_infra_path_e2e_inner_lib_src、t_test_infra_path_tightened、t_test_infra_path_skips_e2ee_source | 通1 邊2 正1:修復回歸;通3:修復回歸(r1 讓棧別鍵看副檔名、claims 沒跟上);安1:原有漏查 |
| GB 送出去處字太寬 | 通2(major)、邊3、正4、正2、安2 | 編排者裁:去處只認「給」與外部名詞(外部、第三方、客戶(不含客戶端)、廠商、供應商、銀行、物流、平台方、partner、vendor、external);單字至、往、向、對、予與「到」黑名單拿掉。前端日常句十四句寫成反例 | t_door_keyword_send_frontend_everyday_not_hit、t_door_keyword_send_dest_each_word_needed、t_door_keyword_send_with_destination_still_hits、t_door_keyword_send_form_data_to_target_still_hits | 通2 邊3:修復回歸;正4:原有漏查(給至往原本就有);正2:原有漏查;安2:原有漏查 |
| GC 80 字範圍與去處詞沒測 | 邊1、正3(major) | 補 80/81 字邊界語意測試(去處在前在後各一組;改成 10 字或 400 字都紅,已實測);S45 的單句多去處改成每個去處詞各一句、只靠那一個詞命中,並釘去處詞表的集合 | t_door_keyword_send_clause_window_80、t_door_keyword_send_dest_each_word_needed | 修復回歸(r1 新加的上限與詞表沒測) |
| GD xargs 帶參數選項與 .kill( | 通4、邊6、正5 | `xargs(?:\s+-\S+(?:\s+[^-\s]\S*)?)*\s+`(選項後可接一個參數);process.kill、child.kill、os.kill 一律用 `\.kill\s*\(` | t_infra_kill_variants | 修復不完整(r1 新加的觸發) |
| GE xargs 二次方 | 資1 | xargs 那一支不再接共用的 `\s*`,兩段不再同時吃空白 | t_infra_xargs_many_spaces_linear(兩萬空白 < 1 秒) | 修復回歸 |
| GF 子句邊界與前端字樣小漏 | 邊4、邊5、邊7 | 點與冒號後面緊接英數或斜線時不切子句(網址、主機名);子句邊界改成 `_PITFALL_SEND_STOPS`:基本邊界字加上 NFKC 後含這些字的全部 BMP 碼位(65 個,測試對全碼位驗);`svelte(?:kit)?` | t_door_keyword_send_url_dots_same_clause、t_door_keyword_send_nfkc_stops_both_paths、t_pitfalls_stage_frontend_sveltekit | 原有漏查 |
| GG 文件 | 整1、整2、整3、整4 | 規格閘金流詞表那列改成新尾碼規則;天花板例句照新規則改(「表單送出後通知客戶」現在會中、拿掉;補 Slack 與下一子句的例子);效能數字照新正規式重量;角色與表態閘的描述補 `.e2e.` 檔名與原本判 node 後端的檔;另把每輪修補差異派工的 SEE 行改成只放連結 | t_door_keyword_payment_suffix_each、t_door_keyword_send_frontend_everyday_not_hit、t_door_keyword_send_long_line_linear、t_stack_key_e2e_path_is_infra | 整1 整2 整3:修復回歸(r1 文件沒同步);整4:未判定 |
| GH 測試檔空行 | 通5 | 兩個函式之間補成兩個空行 | t_disposition_gate_covers_infra_questions | 修復回歸 |

規則指紋跟著變(版本號維持 13,還沒上主線),`t_door_rule_version_pin` 釘值已更新。量法程式改成讀兩個版本當參數(舊版給表、新版給 NEW,不再在計劃裡抄正規式;子句邊界含換行,抄不了),對 357 份計劃重跑:多出命中 0、不做清單略過詞改變 0、改判風險低 0。

新測試:t_door_keyword_send_dest_each_word_needed、t_door_keyword_send_frontend_everyday_not_hit、t_door_keyword_send_clause_window_80、t_door_keyword_send_url_dots_same_clause、t_door_keyword_send_nfkc_stops_both_paths、t_infra_kill_variants、t_infra_xargs_many_spaces_linear、t_test_infra_path_e2e_inner_lib_src、t_pitfalls_stage_frontend_sveltekit(加進來時都紅,t_door_keyword_send_clause_window_80 規則已在,改以把 80 改成 10、400 驗紅)。改寫:t_door_keyword_send_with_destination_still_hits、t_door_keyword_send_form_data_to_target_still_hits(「至客服信箱」改成新規則下仍有去處的句子)。

## 駁回與機械重現(部分輸入不成立,所屬條目其餘照修)

| 編號 | 指令 | 輸出 | MISS |
|---|---|---|---|
| 通2(「form 送出後向後端確認」「按鈕送出後回到列表」)、正4(「表單對話框送出後顯示成功」) | 修後版 f14f6808 載入後 `_door_keyword_hits("form 送出後確認")`、`("按鈕送出後列表")`、`("表單對話框送出後顯示")`(拿掉句中的向、到、對) | 三句照樣回 `[('對外送出', '送出')]` / `[('對外送出', '對話框送出')]` | MISS:命中來自送出前面不是請求或表單的裸字送出,不是去處字;使用者裁定的前端語境只有請求、表單,按鈕、form、對話框不在裡面,照算。測試裡寫成對照組釘住 |
| 邊6(「xargs -r -- kill」) | `_stack_norm_line("xargs -r -- kill")` | `'xargs -r'` | MISS:各棧共用的正規化把 ` -- ` 當成 SQL 行尾註解切掉,kill 在比對前就不見了;改那支會動到所有棧的註解判法,不在本案範圍。`-I {}`、`-n 1`、`-P 4`、`-L 1` 這些照修 |
