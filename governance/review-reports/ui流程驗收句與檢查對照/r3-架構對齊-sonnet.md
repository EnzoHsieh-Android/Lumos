severity: minor

我對照了 `r3-snapshot.md` 和 `scripts/lumos` 的現況。r3 沒有引入第二套放行語意,也沒有跨層直呼。我找到 5 條命名或版本常數跟鄰居不一致的 minor。

**1. 分層與依賴方向:對齊**
- 先判放行再判新規則,跟現況同一個順序。`_e2e_gate_body` 先看放行就回 `waived`(file: `scripts/lumos:42060`),再進 `_e2e_gate_full_note`,最後才是 `_e2e_gate_done("pass")`(file: `scripts/lumos:42035`)。d3 說「放行蓋得過新規則」,跟這個順序一致。
- judge 只記事實,推送檢查才判擋不擋,跟現況一致。judge 本來就沒有主線可用,`_e2e_judge_ui(e2e, steps)` 只吃 run 目錄資料(file: `scripts/lumos:40920`)。主線與分岔點在 `_e2e_gate_body`/`_e2e_gate_full_note` 才有(file: `scripts/lumos:42045`)。
- 單向門關鍵字掃描走既有的 `_door_keyword_hits`,再用 `_DOOR_CLASS_ZH` 換回英文鍵(file: `scripts/lumos:13974`、`scripts/lumos:13747`)。這沒有另寫第二份掃描,只是規格閘多了一個消費者。
- 讀 JSON 沿用 `_e2e_load_json`,讀提交樹沿用 `_e2e_tree_json` 加 `_e2e_record_err`(file: `scripts/lumos:40972`、`scripts/lumos:41684`、`scripts/lumos:40849`)。

**2. 命名與錯誤處理:有 4 處不一致**
- 放行語意、擋下代碼分派、技能檔的家這三項已對齊,見第 3 問。
- 執行紀錄找不到或讀不懂時記 `checks: null` 加原因,跟 `_e2e_judge_stability` 這類「讀不到就記 unjudged 加 reason」同一種做法(file: `scripts/lumos:41007`)。
- `_e2e_gate_out` 已統一清外來文字(file: `scripts/lumos:41633`),r3 說的「走 `_out_clean`」是經由這裡,對齊。
- 不一致 A:`E2E_SCHEMA` 升到 2 沒處理 steps.json。這個常數同時管查證紀錄和 steps.json。judge 要求 `steps.get("schema") != E2E_SCHEMA` 就報錯(file: `scripts/lumos:42640`),範本腳本把 steps.json 的 schema 寫死成 1(file: `scripts/templates/android-e2e-run.sh:427`)。照 r3 只升常數,每次 judge 都會報「steps.json 的 schema 是 1,只認 2」。r3 沒提要拆成兩個常數,也沒提要改範本。
- 不一致 B:`accept_review.by` 的值寫「human 或 agent」,但放行紀錄的值是 `human`/`ai`(file: `scripts/lumos:41715`、`scripts/lumos:42342`)。r3 卻說「形狀跟放行紀錄同一套」。`who` 的意思也不同:放行紀錄的 AI 放行固定寫 `"ai"`,r3 寫「人名或模型」。
- 不一致 C:讀檔上限說法不一。做法第 4 條只說給 `_e2e_load_json` 加巢狀層數參數,但 S3 和〈實務隱患〉都寫了「大小上限」。`_e2e_load_json` 現在沒有大小參數(file: `scripts/lumos:40972`)。提交樹那條路才有 `limit=E2E_RECORD_FILE_MAX`(file: `scripts/lumos:41684`)。r3 沒說本機 commands.json 的大小上限放哪,⚠。
- 不一致 D:提醒出口沒說放行路徑算在哪。`_cl_say_e2e_notes` 只讀 `rep`(file: `scripts/lumos:68512`)。放行的情況在 `_e2e_gate_body` 提早回傳,不會經過 `_e2e_gate_full_note`(file: `scripts/lumos:42060`)。第 8 條要求放行時也印舊項目和檢查變少的行,但沒說這些清單在哪算。若放行路徑另算一份,會變成兩個呼叫點,⚠。

**3. 第二種做法:沒有引入,上一輪提的各項大致已對齊**
- 放行語意已對齊:d3 沿用「人或 AI 皆可放行」(file: `scripts/lumos:41713`),沒有另立只准人放行的規則。
- by/who 形狀只部分對齊,見 B。
- 擋下代碼分派已對齊:用新旗標給 `_cl_say_e2e_next` 分派,跟 `bad_record`、`newer_schema` 同一種做法(file: `scripts/lumos:68478`)。`gate_code` 目前只有兩個 `evaluation_*`(file: `scripts/lumos:42083`、`scripts/lumos:42093`),新增三類沿用同一欄。
- 擋下代碼有一處待補。現況 `extra` 只有固定四個鍵(file: `scripts/lumos:67855`),「另記全部類別」要新增鍵,但 r3 沒講鍵名,⚠。
- JSON 讀法已對齊,見第 1 問。
- 提醒出口已對齊:擴充既有的 `_cl_say_e2e_notes`,沒有另開一支。只剩 D 的位置問題。
- 技能檔的家已對齊:列進 `android-e2e-acceptance` 的 about_code。查過這兩份技能檔目前沒有任何 Systems 節點的 about_code 列到,而且別的節點也有把 `skills/` 檔放進 about_code 的先例(`每輪修補差異派工.md`)。
- 另有一處小漏:第 5 條說「其他各條不附放行指令」,但放行指令是外層呼叫端印的,條件是「有 fp 且非 bad_record、非 newer_schema」(file: `scripts/lumos:68470`)。要少印就得改那個條件,不是改 `_cl_say_e2e_next`。r3 把這件事寫成只在 next 函式裡處理。

**4. 落點:對齊**
- `lands_in` 兩篇和〈落點〉三項一致。`Systems/android-e2e-acceptance.md` 已存在,responsibility 本來就含 judge、推送判定和 e2e 段格式。
- 規格閘只補一行 KEY,不增程式檔。
- 技能檔放進 android-e2e 節點的 about_code,算是補上目前沒有家的檔。

以下 5 條是不一致的明細。

severity: minor
blocking: 否,這是版本常數兩用的不一致,沒有引入第二種做法也沒有跨層直呼,實作時拆常數或改範本即可補上。
引句:「紀錄格式版本 `E2E_SCHEMA` 從 1 升到 2」

severity: minor
blocking: 否,值名稱和 `who` 內容跟放行紀錄不同,結構本身一致,補一句對照即可。
引句:「形狀跟放行紀錄的 `by`、`who` 同一套」

severity: minor
blocking: 否,只是上限放哪沒講清楚(⚠),結構沒錯。
引句:「讀檔沿用 `_e2e_load_json`,給它加一個巢狀層數參數」

severity: minor
blocking: 否,放行路徑的清單在哪算沒講,實作時容易變成第二個呼叫點(⚠)。
引句:「要擴到整套通過與放行」

severity: minor
blocking: 否,放行指令的有無由外層呼叫端決定,不是 `_cl_say_e2e_next`,補寫要改的位置即可。
引句:「不附放行指令(放行照樣有效,只是不推薦)」

不對齊共 5 條,其中 major 0 條
