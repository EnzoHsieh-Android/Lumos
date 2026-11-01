severity: minor

審查範圍只限 r4-delta.patch。對照過 `scripts/lumos` 的實際程式,沒有發現第二種做法。有兩條小的命名與用法不一致。

**1. 分層與依賴方向:對齊**
- 版本號拆開(steps.json 與查證紀錄各一個版本)是專案已有的做法。每種產物各自一個 `*_SCHEMA` 常數,例如 `_LENS_SCHEMA`、`_DRIFT_M1_DEFS_SCHEMA`、`_FILTER_PROBE_SCHEMA`。file: `scripts/lumos:63161`、`scripts/lumos:54915`、`scripts/lumos:65803`
- 現況是 `E2E_SCHEMA` 一個常數同時管兩種檔。steps.json 的版本檢查要求完全相等,查證紀錄的檢查是範圍。file: `scripts/lumos:42640`、`scripts/lumos:40854`
- 讀檔仍走 `_e2e_load_json`、`_e2e_tree_json` 和 `_e2e_record_err`,沒有新寫一套讀法。file: `scripts/lumos:40972`、`scripts/lumos:41684`、`scripts/lumos:40849`
- 新規則放在放行判斷之後、整套通過宣告之前,跟現行順序一致。現行是先 `waived` 回傳,再 `_e2e_gate_full_note`,最後 `_e2e_gate_done("pass")`。file: `scripts/lumos:42073`、`scripts/lumos:42033`
- 放行指令確實是 `_cl_say_e2e_block` 外層用 `fp`、`bad_record`、`newer_schema` 這個條件另外印的,不在 `_cl_say_e2e_next` 裡。delta 的描述屬實,改條件沒有跨層。file: `scripts/lumos:68467`

**2. 命名與錯誤處理:有兩條不對齊**

severity: minor
blocking: 否。命名與用法跟鄰居不一致,但結構是對的。
引句:「另開查證紀錄自己的版本號,升到 2」
- delta 只列了 `_e2e_record_err` 的範圍和寫紀錄時的版本(新建與更新一律寫 2)。
- 它沒提 `_e2e_gate_load` 裡判斷「較新版本」的那一行,現在是拿 `E2E_SCHEMA` 比。file: `scripts/lumos:42005`
- 新常數沒有名字,也沒說這一行要改用它。沒改的話,版本是 2、但別處有毛病的紀錄,會被誤判成「較新版本」,訊息變成「更新 lumos」而不是「修好或刪掉」。
- 另外,`E2E_SCHEMA` 的行內註解寫著「查證紀錄與 steps.json 的格式版本」,拆開後也要跟著改。file: `scripts/lumos:40433`

severity: minor
blocking: 否。大小上限的放法跟鄰居不一致,但沒有另寫讀法。
引句:「給它加兩個選填參數:巢狀層數(預設維持 20)與檔案大小」
- 現有的大小上限有兩種放法:`_e2e_record_update` 在呼叫 `_e2e_load_json` 之前自己用 lstat 擋;`_e2e_tree_json` 則用 `limit=` 參數。file: `scripts/lumos:41112`、`scripts/lumos:41684`
- delta 把第三種放法(讀取函式內建的大小檢查)加進 `_e2e_load_json`,參數沒有命名。
- 建議:參數名沿用 `limit`,並寫明 `_e2e_record_update` 那處 lstat 維持不動。⚠ 這條不是結構問題,只是命名與用法要先說清楚。

放行紀錄的 `by` 已經改成 `human/ai`,跟 `_e2e_waiver_ok` 一致。file: `scripts/lumos:41713`
- `accept_review.who` 寫模型名,放行紀錄的 `who` 在 AI 放行時固定寫 `ai`。file: `scripts/lumos:42342`
- 這個差異 delta 有明講理由(要看出是哪個代理審的),不算第二種做法。

**3. 第二種做法:沒有**
- 治理帳的 `extra` 新增 `accept_classes` 鍵,跟現有 `extra` 是同一個字典、同一個出口,`gate_code` 仍記單一值。file: `scripts/lumos:67856`
- 擋下訊息的分派沿用既有的旗標做法(`bad_record`、`newer_schema`)。file: `scripts/lumos:68478`
- 放行時不印提醒:`_cl_say_e2e_notes` 現有的 `pending_ai` 行本來就在 `waived` 時印,delta 說的「放行本身已被列出」屬實。file: `scripts/lumos:68512`

**4. 落點:對齊**
- 兩處改動(`_e2e_load_json` 加參數、judge 寫版本)都落在 e2e 區段既有函式,沒有新開檔案或另立模組。file: `scripts/lumos:40972`、`scripts/lumos:41120`

不對齊共 2 條,其中 major 0 條
