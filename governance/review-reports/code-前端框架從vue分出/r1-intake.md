# code-前端框架從vue分出 r1 收貨與處置

七席收齊(資安 clean 0 條),共 28 條:major 6 條(資1、資2、架1、架2、架3、整1;架2 與架3 是同一根因的兩面)、其餘 22 條 minor。全部折入,駁回 0 條。每個程式根因先寫會紅的測試再改(改前跑紅、改後跑綠,另做一輪「把修法拿掉」的翻紅,見下表)。修正的範圍:base 600d7b02 → 本輪提交。

## 根因組

| 根因組 | 條目 | 修法 | 守它的測試 |
|---|---|---|---|
| (A) 判 Android 的建置檔樣式二次方回溯 | 資1 | `_KT_BUILD_ANDROID` 行首改 `^[ \t]*android[ \t]*\{`(不吞換行) | t_kt_build_android_regex_blank_lines_fast |
| (B) 角色路重掃建置檔、迴圈不看預算、批次無總量上限、快取無上限 | 資2、資3、資4 | 新增 `_kt_build_verdict`(以建置檔文字記憶判定,lru 64 份,每份受 512KB 讀檔上限管);`_review_roles` 分類迴圈超過預算就停用讀到的內容、剩下退回只看副檔名並標 timed_out;批次讀取帶 `_ROLE_MAX_TOTAL_BYTES`(16MB);工作樹讀檔改用共用的 `_worktree_text`,快取每筆一份檔、呼叫端各有檔數上限(資4 以註明處理) | t_review_roles_kt_build_verdict_memo、t_review_roles_classify_loop_respects_budget、t_review_roles_batch_total_bytes_capped、t_worktree_text_shared_reader |
| (C) 第二套讀檔與快取、出題後再過濾、vitest 自己讀檔、兩份 eslint 清單沒守衛 | 架1(3a)、架2(3b 第一條)、架3(3b 第二條)、架4(3c)、架5(eslint 清單) | 照編排者裁定:①`_node_pkg_text` 那套擴成 `_worktree_text(head=, max_bytes=)` 兩邊共用,拿掉 `_kt_worktree_text`/`_KT_BUILD_CACHE`;②android_only 照 shape_only 的做法在 `_stack_applicability`(exclude 參數)與唯一的整組派生 `_stack_whole_group`(`_STACK_PERF_QUESTIONS` 也由它派生)裡消化,拿掉 `_stack_drop_excluded`、`_tension_drop_excluded`、`_stack_perf_questions`;張力候選改收 `applicable_ids` 只出適用題;③`_uses_vitest` 改走 `_worktree_text`;新增兩份 eslint 檔名清單的同步守衛 | t_stack_android_only_inside_applicability、t_worktree_text_shared_reader、t_eslint_config_names_in_lint_globs,以及既有 t_kt_spring_android_questions_gone_on_triggers、t_pitfalls_stack_questions_kt_spring、t_impact_stack_questions_kt_spring |
| (D) 跑過證據樣式 | 通1、邊2、正1、正2 | 改成 `Tests\b[^\n]{0,200}?(?<![0-9])[1-9]\d*[^\S\n]+passed`:數字前只要求前一個字不是數字(色碼的 m 緊貼數字時字詞邊界不成立)、空白不跨行;仍限長 | t_ran_evidence_colored_per_line_reader(含 _kill_cap 截斷保留帶色碼摘要)、t_ran_evidence_no_cross_line_match、既有 S4–S7、S35 |
| (E) Kotlin 判法 | 正3、正4 | 比對前剝註解(`_kt_strip_comments`,區塊註解用 find 逐段跳、線性);伺服端只認外掛宣告:拿掉 `ktor-server`,收版本目錄 alias `libs.plugins.spring.boot`/`springBoot`/`ktor` | t_kt_build_comments_and_ktor_dependency_not_server、t_kt_spring_alias_is_server |
| (F) vitest 判定 | 通2、邊4 | 依賴有 vitest → 是;依賴有 jest 沒有 vitest → 不換;依賴看不出才看設定檔,而且只認確切副檔名(`.bak` 不算) | t_init_skeleton_vite_with_jest_stays_jest、既有 S1–S3 |
| (G) 其他 | 邊1、正5、邊3、邊5、通3 | 邊1:`min_lines` 改數增行(pitfalls 傳 `added_by_stack`;改檔前推播沒有增刪之分,照舊數全部);正5:張力候選只出適用題(同 C②);邊3:根 package.json 的 `eslintConfig` 算舊式設定;邊5:測試檔判定加認檔名本身是 `test.*`/`spec.*`,`_scan_diff_for_irreversible_hints` 改用同一個 `_PITFALL_DIFF_TEST_PAT`;通3:註解移回 `_tension_candidates_into` 那行 | t_react_parallel_same_line_edit_quiet、t_tension_candidates_respect_applicability、t_eslint_package_json_eslintconfig、t_test_pat_bare_names_and_irreversible_shared |
| (H) 文件 | 整1–整6 | 整1:分支名已在 23c8c68b 改正(本輪收進 fix.json 的 G10);整2:計劃交界節補「`_review_role_for` 保留 infra 回 None」;整3:代碼審前後端角色鏡頭計劃三處舊說法加註、arch-alignment-lens 的 KEY 行(用 summary-line 改)、`_stack_key_for_file` 的舊註解;整4:表態閘「八棧」那句加註現況;整5:計劃〈現況〉標題註明改動前、實作紀錄補 S43;整6:兩個壞連結指向另外兩支分支上的計劃,合併後就有,不改 | 文件條目沒有自己的測試;fix.json 把它們跟同組的程式註解修正收在 G10(`scripts/lumos:_stack_key_for_file`,t_react_stack_key_from_package_json) |

## 翻紅驗證(把修法拿掉,確認對應測試紅;每次都還原並比對原檔一致)

| 拿掉的修法 | -k | 結果 |
|---|---|---|
| Android 樣式改回 `^\s*android\s*\{` | blank_lines_fast | 1 紅 |
| 拿掉 `_kt_build_verdict` 的 lru 記憶 | build_verdict_memo | 1 紅(⚠ 這一支是因為測試呼叫 `cache_clear` 丟例外而紅,不是斷言紅;斷言本身要靠 `cache_info().misses == 1`,拿掉記憶時這個屬性也一起消失) |
| 分類迴圈不看預算 | classify_loop | 1 紅 |
| 不剝註解 | comments_and_ktor | 1 紅 |
| 伺服端樣式改回收 `ktor-server`、不收 alias | spring_alias | 3 紅 |
| 數字前改回 `\b`、空白改回 `\s+` | colored_per_line | 3 紅 |
| vitest 判定不看 jest | vite_with_jest | 1 紅 |
| min_lines 改回數全部改動行 | same_line_edit | 1 紅 |
| 張力候選不看適用題 | respect_applicability | 1 紅 |
| 不收 eslintConfig | eslintconfig | 1 紅 |
| 不可逆掃描改回舊副本 | bare_names | 1 紅 |
| `_LINT_CONFIG_GLOBS` 拿掉 `*.config.mts` | config_names_in | 1 紅 |

## 駁回與機械重現

駁回 0 條。席位的觀察都在 600d7b02 上重現得出來(改前跑新測試的紅燈即是重現:資1 6.5 萬空行、資2 60 支慢判定不停、資3 沒帶 max_total_bytes、D 帶色碼逐行與跨行、E 註解與 ktor-server、F vite+jest、邊1 同一行改動、正5 候選、邊3 eslintConfig、邊5 test.tsx 與舊副本)。

## 沒做到的部分

- 邊1 只在推送前分級那條路數增行;改檔前推播送來的內容是舊字串加新字串接在一起,分不出增刪,照舊數全部——只會多問、不漏問。
- 整6 的兩個壞連結不改,合併順序交給編排者。
