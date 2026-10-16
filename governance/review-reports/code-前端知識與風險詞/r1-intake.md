# code-前端知識與風險詞 r1 收貨與修正紀錄

七席(正確性、邊界、資源、整合、通才、架構對齊、資安)全數交回,引句全錨定。編號照各報告順序:正1–正7、邊1–邊5、資1、整1–整7、通1–通3、架1–架3、安1–安3。共 29 條:major 2(正1、通1)、minor 27。28 條折入修掉;整7 是另一個工作樹(web-react)的檔,本輪不改,交編排者(見文末)。無駁回。

| 根因組 | 條目 | 修法 | 守它的測試 |
|---|---|---|---|
| GA 送出例外漏判 | 通1 邊1 正5 安3 | 統一規則:前端語境的送出只在同一子句(半形或全形標點為界)前後 80 字內都沒有去處時才放行;去處字「給 至 往 向 對 予」、去處詞「外部 第三方 客戶(不含客戶端) 廠商 銀行 物流 partner external」、後面的「到」(收到、拿到…不算)。去處寫在前後都算 | t_door_keyword_send_destination_variants_still_hit、t_door_keyword_send_with_destination_still_hits、t_door_keyword_send_form_data_to_target_still_hits、t_door_keyword_send_second_notice_still_hits、t_door_keyword_send_request_context_exempt |
| GB PAYMENT 尾碼太寬 | 安2 邊3 通3 正6 | PAYMENT 要緊接時間或重試尾碼(_TIMEOUT _TTL _DELAY _INTERVAL 可再接單位、單位本身、_RETRIES _RETRY_COUNT _MAX_RETRIES);拿掉 _LIMIT _COUNT _WINDOW,中間不能夾別的段 | t_door_keyword_payment_suffix_each(每個尾碼各測一次)、t_door_keyword_caps_identifier_payment_exempt、t_door_keyword_payment_api_key_still_hits |
| GC 路徑分流太寬 | 安1 通2 邊4 整4 整5 | `_TEST_INFRA_PATH_RE` 只認 e2e 資料夾(不在 src/、lib/ 底下)、`.e2e.` 檔名、e2e 字樣的 .sh;seeds、fixtures 不收;樣式內非 sh/py/ts/js 家族的副檔名照原棧(kt、java、sql 不變成沒題);計劃與 arch-alignment-lens 改寫 tests/e2e 與角色影響的說法 | t_test_infra_path_tightened、t_test_infra_data_files_no_stack_key、t_test_infra_path_skips_e2ee_source |
| GD 觸發字漏接 | 正2 正3 邊5 正4 邊2 | 埠變數允許底線前綴(E2E_PORT=);指令位置多認 xargs 之後;infra-pid、infra-signal 多收 process.kill(;前端字樣框架名後面可緊貼數字、多認 reactjs、vuejs、nextjs、solidjs 與 front-end/frontend | t_infra_trigger_variants、t_infra_word_boundary_no_false_trigger、t_infra_no_trigger_on_unrelated_shell_lines、t_pitfalls_stage_frontend_version_glued |
| GE 正則效能 | 資1 | 子句前後只看 80 字(`_PITFALL_SEND_CLAUSE` 的 {0,80}) | t_door_keyword_send_long_line_linear(十萬字兩萬個送出 < 2 秒) |
| GF 一致性 | 正7 架1 架2 架3 | 子句邊界列全形標點(兩條路不再分岔);字串常數改名 `_PITFALL_SEND_WHEN`、`_PITFALL_PAYMENT_WHEN`;`_INFRA_CODE_EXTS = {"sh","py"} \| _NODE_EXTS`;加守衛測試要求 `_NODE_FRONTEND_MARKERS` 每個框架名都被前端字樣認得 | t_door_keyword_send_fullwidth_comma_both_paths、t_door_rule_version_pin、t_test_infra_path_tightened、t_req_fe_when_covers_node_frontend_markers |
| GG 文件 | 整1 整2 整3 整6 | 規格閘節點 KEY 改成版本 13 並補 13 的沿革;規格閘不做節計劃 [S5] 改成 13;效能檢核目錄全表題數補 infra=6;計劃交界段 S11 改成 S16;templates.md 家節點「三個」改「四個」、補 SEE 指到 design-loop | t_door_rule_version_pin、t_stack_question_triggers、t_stack_key_e2e_path_is_infra、t_templates_security_web_frontend_class |
| GH `.sh` 規則沒人守 | 正1 | 補一支只用檔名不含 e2e 的 .sh(scripts/setup.sh、deploy.sh、tools/run-backend.sh)測棧別鍵;拿掉 `.sh` 那條規則它會紅(已實測 3 條紅) | t_stack_key_plain_shell_is_infra |

門規則指紋跟著變(版本號維持 13:13 還沒上過主線),`t_door_rule_version_pin` 的釘值已更新。修正後照計劃做法 9 的量法重跑(old=cd1f9619 版):357 份計劃,多出命中 0、不做清單略過詞改變 0、改判風險低 0。

新寫的測試(都在加進來時先紅):t_door_keyword_send_destination_variants_still_hit、t_door_keyword_send_fullwidth_comma_both_paths、t_door_keyword_send_long_line_linear、t_door_keyword_payment_suffix_each、t_stack_key_plain_shell_is_infra(規則已在,改以拿掉規則驗紅)、t_test_infra_path_tightened、t_infra_trigger_variants、t_pitfalls_stage_frontend_version_glued、t_req_fe_when_covers_node_frontend_markers;改寫的:t_test_infra_data_files_no_stack_key(seeds 那幾條移到 t_test_infra_path_tightened)。

駁回:無。

交給編排者(不在本工作樹):整7——web-react 工作樹的 `Projects/前端框架從vue分出_計劃.md` 把本計劃稱為「web-notes 分支」,實際分支是 `EnzoHsieh-Android/web-fe-knowledge`,合併時請那篇的作者更正。修正紀錄沒收這一條(沒有本工作樹的檔可改),記帳時請標成 process。

照實寫的天花板(計劃做法 9 已寫):前端語境、同一子句沒有去處字詞的句子仍不算(「將重試請求送出」「送出請求,包含客戶資料到外部」去處在下一個子句);安3 的第三個例子屬這一類。
