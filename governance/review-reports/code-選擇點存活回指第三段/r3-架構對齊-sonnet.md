severity: clean

**1. 分層與依賴方向**

沒有新的不對齊。
- 新增的 `_choice_layer_plan_sides`、`_choice_layer_items_md`、`_choice_layer_write_parts` 都留在 `_choice_layer_*` 這一層,依賴方向沒變:`_choice_layer_template` 呼叫 `_choice_layer_split`、`_choice_layer_plan_sides`、`_choice_layer_write_parts`,再往下呼叫 `_choice_layer_render`。
- 旁檔仍然透過 `_choice_layer_side`(`scripts/lumos:81536`)取路徑、用 `_write_lf`(`scripts/lumos:32799`)寫檔、放在 `_NOTE_AUDIT_WORK_DIR` 底下的 `choice-layer/`。這跟 note-audit 的旁檔寫法一致,工作目錄仍由 `_choice_layer_work` 取得,沒有另開出口。
- `_CHOICE_LAYER_SHARED_MAX` 緊接 `_choice_layer_split` 定義,沒有放進檔頂的常數區。`_FOLD_AUDIT_RECORD_RE`(`scripts/lumos:69165`)也是緊鄰使用處,這在本檔很常見,不算第二種做法。

**2. 命名與錯誤處理**

沒有新的不對齊。
- 新函式名全是 `_choice_layer_<名詞>` 或 `_choice_layer_<動詞>`,跟既有的 `_choice_layer_side_write`、`_choice_layer_plans` 同一套。
- 超過上限的提示仍走 `print(f"提醒:…", file=sys.stderr)`,跟 `_choice_layer_template` 其他提醒一致。
- 旁檔寫入沒有加 try,跟舊的 `_choice_layer_side_write` 一樣,不是新增的差異。
- 上一輪的 minor 已處理:`_CHOICE_LAYER_NOT_BODY_RE` 改成搭 `fullmatch`,註解明寫與 `_FOLD_AUDIT_RECORD_RE` 的差別(整行比對、管三種節名、多認大寫代號前綴、後綴只收括號說明)。
- 跟 `_EXPECTED_H2_RE`(`scripts/lumos:14412`)和 `_KT_SIT_ACCEPT_H2_RE`(`scripts/lumos:76215`)比,這支沒寫 `^…$` 錨,而是靠 `fullmatch`。語意等價,而且註解已說明,不算命名或處理方式的分歧。

**3. 第二種做法**

沒有。
- 分份改成「共用材料另存旁檔、份上限只比存活自己的材料」,仍然只有一條分份路徑(`_choice_layer_split`)。舊的 `_choice_layer_over` 和 `_choice_layer_one_part` 一併移除,沒有並存。
- 旁檔寫法沿用 `_choice_layer_side` 加 `_write_lf`,沒有另做一套。
- 判計劃節標題仍用 `_CHOICE_HEAD_RE` 加 `_choice_plan_sections` 的同一條路徑,沒有另寫標題解析。

不對齊共 0 條,其中 major 0 條
