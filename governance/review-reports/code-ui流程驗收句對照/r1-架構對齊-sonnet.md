severity: minor

我只讀了 diff 和鄰居程式碼,沒跑測試。整體結構跟鄰居一致,只有一條不對齊(minor)。

**1. 分層與依賴方向:對齊**
- judge 層:`_e2e_flow_checks` 讀 Maestro 的 `commands.json`,在 `_e2e_judge_ui` 內呼叫。judge 讀盤上檔案是既有做法,`_e2e_junit_ok` 也在 judge 層讀報告。file: `scripts/lumos:41015`(diff `_e2e_flow_checks`)對照 file: `scripts/lumos:40946`(`_e2e_junit_ok`)。
- judge 只記事實,不碰主線。`_e2e_checks_preview` 只寫 notices,註明新舊要比主線,由推送檢查判。這跟鄰居 `_e2e_judge_stability` / `_e2e_judge_visual` 的分工相同。
- 推送檢查層:`_e2e_accept_gate` 掛在 `_e2e_gate_full_note` 的「放行之前」。它只讀紀錄(`rec`)、主線與分岔點的設定,以及 `_e2e_tree_json` 取的 git 樹,不碰裝置。放行(waiver)那一步在它之前,所以放行不受新規則影響。file: `scripts/lumos:42070`(`_e2e_gate_done`)、file: `scripts/lumos:41891`(`_e2e_tree_json`)。
- 呼叫鏈跟鄰居相同:判定函式丟 `_E2eGateStop`,`_codeloop_e2e_step` 寫治理帳(`_gate_event_fit`、`_gate_event_or_warn`),`_cl_say_e2e_*` 印訊息。新增的 `_cl_say_e2e_accept` 掛在 `_cl_say_e2e_next` 的 elif 鏈裡,跟 `_cl_say_e2e_cases` / `_cl_say_e2e_full` 同位階。
- 規格閘:`_e2e_one_way` 呼叫 `_door_keyword_hits`,沒另寫關鍵字比對。file: `scripts/lumos:13974`。
- 沒有跨層直呼:judge 不讀主線,推送檢查不碰裝置。

**2. 命名與錯誤處理:對齊**
- 命名:`_e2e_*` 前綴、`E2E_*` 常數、`*_err` 回「錯誤訊息或 None」,跟 `_e2e_relpath_err` / `_e2e_record_err` / `_e2e_case_err` 一致。`_e2e_case_err` 尾端接 `_e2e_case_accept_err` 的串法跟既有做法相同。
- 型別驗證:`_e2e_record_checks_err` 和 `_e2e_record_fr_err` 沿用「判定會讀到的欄位,型別在 `_e2e_record_err` 先驗」的慣例,放進 `_e2e_record_err` 的同一個驗證鏈,並用 `_secev_int`、`_e2e_strs`。
- 錯誤訊息:`_E2eLoadErr(str)` 加 `code`,舊呼叫端照舊當字串用,回傳形狀仍是 `(值, 錯誤)`。file: `scripts/lumos:41128`。
- 外來文字:全走 `_e2e_gate_out` 統一清。
- 擋下訊息:三段式(發生什麼、為何在意、指令獨立一行)。`rep.get("accept_items")` 的分支加在「在意的原因」那個 if/elif 鏈裡,放行指令的條件也只是加了一個旗標。file: `scripts/lumos:68829`(`_cl_say_e2e_block`)。
- 提醒:以「提醒」開頭,並加進 `_cl_say_e2e_notes`。
- 治理帳:`accept_classes` 走既有 `extra`,跟 `gate_code` 並列。
- 測試:`check(...)` 帶訊息、`print("  ✓ t_...")`、`t_android_e2e_*` 命名、`_e2ea_*` helper 前綴對應 `_e2eg_*`。測試重用 `_e2e_proj`、`_e2eg_proj`、`_e2eg_rec`、`_e2eg_check`、`_e2eg_cl`、`_e2eg_events`、`_e2e_steps`、`_e2e_judge`、`_e2e_set_cfg`,沒另寫一套。

**3. 第二種做法:有一條不對齊(minor)**

`_e2e_cap` 是「名字清單最多列 n 個、其餘寫 `等 N 個`」的新工具函式。專案裡已有同功能的:
- file: `scripts/lumos:7228`(`_secinv_names`):`"、".join(ks[:limit]) + (f" 等 {len(ks)} 個" if len(ks) > limit else "")`
- file: `scripts/lumos:14195`(`_nogo_words`)是同一形狀的另一份。
- 同在 e2e 擋下訊息層的 `_cl_say_e2e_cases` 則是行內寫 `(另有 N 個,看 lumos android-e2e check)`。

新的 `_e2e_cap` 輸出跟 `_secinv_names` 同格式,等於又多一份。它放在 e2e 家族內,屬於鄰居式的就地小函式,所以我只標 minor。判斷依據是 `_secinv_names` 在安全證據閘的領域,e2e 沒有現成的同層 helper,所以不算跨層重用該有而沒用。⚠ 編排者如果認定「專案已有兩份同形狀 helper,第三份就是第二種做法」,可以升 major。

severity: minor
blocking: 否(輸出格式與既有 `_secinv_names` 一致,只是多一份拷貝,結構沒有偏離)
引句:「return "、".join(xs[:n]) + (f" 等 {len(xs)} 個" if len(xs) > n else "")」

其餘幾項我都確認過,沒有第二種做法:
- 讀 JSON:全走 `_e2e_load_json`,只擴充 `depth`、`limit` 兩個參數,沒另寫一套。
- 讀主線 / 分岔點:走 `_e2e_tree_json`、`_e2e_config_at`、`_e2e_fingerprint`,新舊集合用 `_e2e_norm` 正規化,跟既有 `_e2e_runs_missing` 的比對同一套。
- 紀錄版本:另開 `E2E_RECORD_SCHEMA` 與 steps 的 `E2E_SCHEMA` 拆開。所有讀寫紀錄版本的地方(判定、寫入、推送前讀取)都改了,`E2E_SCHEMA` 只剩 steps.json 的檢查,沒有遺漏。
- 治理帳:沿用 `_gate_event_fit` / `_gate_event_or_warn`,沒另開寫法。
- 放行 `by` 的值:`("human", "ai")` 跟 `_e2e_waiver_ok` 同一組。file: `scripts/lumos:41922`。
- 單向門類別:`E2E_ONE_WAY` 是 `_DOOR_CLASS_ZH` 的子集,在 diff 裡有說明為何不收守衛面。

不對齊共 1 條,其中 major 0 條

相關檔案:
- /Users/enzo/harness/lumos-auto-device/governance/review-reports/code-ui流程驗收句對照/r1-snapshot.patch
- /Users/enzo/harness/lumos-auto-device/scripts/lumos
- /Users/enzo/harness/lumos-auto-device/scripts/test_lumos.py

LUMOS-IMPACT: b406a2656c536335f227540ca9ace88278016d76..74d6c9df358898d2a14203df84aa70624181b079
LUMOS-ARCH-TARGET: on
