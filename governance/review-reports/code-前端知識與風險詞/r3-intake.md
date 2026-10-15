# code-前端知識與風險詞 r3 修正紀錄(high 上限最後一輪)

修後版本 20df2187 的七席報告。編號照派工:正1–正4、邊1–邊5、資1、整1–整4、通1–通4、架1–架2、安1–安2。全部折入,無駁回。r1、r2 的 intake 已記帳,本輪沒動。

編排者裁定:「送出」的前端例外整條撤回、回到裸字一律算對外送出(推翻使用者原裁「加前端與識別字例外」的前端那一半,記在 d1,計劃加了 REVISIT);PAYMENT 參數名例外保留;e2e 樣式內只有 kt、java 這類有自己語言題的程式檔照掃產品型樣;架2 照上一輪裁定以註解為折入。

| 根因組 | 條目 | 修法 | 守它的測試 | 歸因 |
|---|---|---|---|---|
| GA 送出前端例外 | 安1 通1 架1(三個方向的 major)、正1 邊2 通2 正2 邊5 通4 | 撤回:`PITFALL_CLASSES` 對外送出類回到裸字 `送出`;拿掉 `_PITFALL_SEND_WHEN`、`_PITFALL_SEND_DEST`、`_PITFALL_SEND_CLAUSE`、`_PITFALL_SEND_STOPS`;d1 用 decision-amend 記撤回、計劃加 REVISIT(前端計劃因送出判高且確認誤判累積 5 份才重議);做法 9、規格閘、雙向門放行同步 | t_door_keyword_send_always_hits、t_pitfalls_check_shares_send_exemption、t_door_rule_version_pin | 安1 通4 正2:修復回歸(r2 收窄去處讓詞表外的真送出漏判);通1:修復不完整(r2 留下「給」);架1 正1 邊2 通2:修復回歸(r2 新加的標點表與網址點號);邊5:修復回歸 |
| GB e2e 非程式檔被掃 | 邊1(major)、通3、正3 | claims 跳過拆成 `_skip_product_claims`,一句話規則:e2e 樣式內的檔都不掃產品型樣,唯一例外是 kt、java、cs、swift、dart 照掃 | t_test_infra_e2e_non_code_no_claims、t_test_infra_path_e2e_inner_lib_src | 修復回歸(r2 把 claims 改成看副檔名) |
| GC xargs 二次方 | 資1(major) | xargs 選項抽成 `_INFRA_XARGS_OPT`,最多看 8 個 | t_infra_xargs_option_chain_linear(xargs -a 重複四千次 < 1 秒)、t_infra_xargs_many_spaces_linear | 修復回歸 |
| GD xargs 旗標吞指令名、killpg | 邊3、邊4 | 只有會帶參數的選項(-I -i -L -l -n -P -d -a -E -s 與 --max-args 等長選項)能吃下一個字;其他旗標不吃;`.kill(?:pg)?\s*\(` | t_infra_xargs_flag_no_swallow、t_infra_kill_variants、t_infra_killpg | 邊3:修復回歸;邊4:原有漏查 |
| GE 文件 | 整1(major)、整2、整3、整4 | d1 改寫成撤回後的現況(不再寫舊去處字);做法 7 寫法換成程式現值並寫明 claims 的一句話規則;效能檢核目錄 infra 表補 xargs 與 .kill(/.killpg(、綁定測試補齊;S45 等十五條條款隨撤回刪除,由 S63 取代 | t_door_keyword_send_always_hits、t_test_infra_path_e2e_inner_lib_src、t_infra_xargs_option_chain_linear | 整1 整2 整4:修復回歸(r2 改程式沒同步);整3:原有漏查 |
| GF 其他 | 正4、安2 | 前端字樣收 `svelte(?:kit\|js)?`(@sveltejs/kit);名字叫 e2e、不在 src、lib 底下的產品資料夾仍算 e2e,寫進計劃天花板 | t_pitfalls_stage_frontend_sveltejs_kit、t_test_infra_path_e2e_inner_lib_src | 正4:原有漏查;安2:原有漏查(r2 已寫在註解) |
| GG 四處判法分工 | 架2 | 照上一輪裁定:樣式旁註解改寫成棧別鍵問 `_is_test_infra_file`、claims 問 `_skip_product_claims` | t_test_infra_path_tightened、t_test_infra_path_e2e_inner_lib_src | 未判定 |

拿掉的測試(隨送出例外撤回):t_door_keyword_send_request_context_exempt、t_door_keyword_send_second_request_exempt、t_door_keyword_send_form_exempt、t_door_keyword_send_with_destination_still_hits、t_door_keyword_send_plain_still_hits、t_door_keyword_send_second_notice_still_hits、t_door_keyword_send_form_data_to_target_still_hits、t_door_keyword_send_destination_variants_still_hit、t_door_keyword_send_fullwidth_comma_both_paths、t_door_keyword_send_long_line_linear、t_door_keyword_send_dest_each_word_needed、t_door_keyword_send_frontend_everyday_not_hit、t_door_keyword_send_clause_window_80、t_door_keyword_send_url_dots_same_clause、t_door_keyword_send_nfkc_stops_both_paths。改寫:t_pitfalls_check_shares_send_exemption(只留共用詞表的 PAYMENT 部分,加送出兩條路都命中)。

新測試(加進來時都紅):t_door_keyword_send_always_hits、t_test_infra_e2e_non_code_no_claims、t_infra_xargs_option_chain_linear、t_infra_xargs_flag_no_swallow、t_infra_killpg、t_pitfalls_stage_frontend_sveltejs_kit。

規則指紋跟著變(版本維持 13,還沒上主線),`t_door_rule_version_pin` 釘值已更新,推送擋下訊息裡版本 13 的說明改成只講 PAYMENT。量法(cd1f9619 對修後版)重跑:357 份計劃,多出命中 0、不做清單略過詞改變 0、改判風險低 0。

駁回:無。
