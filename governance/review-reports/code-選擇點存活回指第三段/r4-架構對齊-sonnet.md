severity: major

**1. 分層與依賴方向**

這份改動沒有跨層直呼。新增的 `_choice_layer_split_groups` 只呼叫同層既有的 `_choice_layer_groups`、`_choice_layer_plans`、`_choice_layer_plan_sides` 和 `_choice_layer_split`,依賴方向跟原本一致。`_CHOICE_LAYER_INTRO` 和 `_CHOICE_LAYER_ANSWER` 一樣放在渲染函式旁邊,位置不突兀。

這一問沒有不對齊。

**2. 命名與錯誤處理**

命名跟鄰居一致:`_CHOICE_LAYER_*` 前綴、`_choice_layer_*` 函式前綴,且各常數上方都有「跟 `_FOLD_AUDIT_RECORD_RE` 的差別」註解。這一輪沒有新增吞例外或漏判錯誤的寫法。

重複一小段:`list(dict.fromkeys(p for x in items for p in _choice_layer_plans(...)[1]))` 在 `_choice_layer_split_groups` 和 `_choice_layer_render` 各寫一次。這屬風格,不列。

**3. 第二種做法**

標題判段出現了第二套判法(major)。

- 既有寫法:預期值表那一節用 `_h2_section_lines(text, _EXPECTED_H2_RE)` 找。`_EXPECTED_H2_RE` 是 `^##\s+預期值表\s*$`,整行精確比對(`scripts/lumos:14412`、`scripts/lumos:81150`)。驗收條款節的 `_KT_SIT_ACCEPT_H2_RE` 也是同樣的精確寫法(`scripts/lumos:76215`)。
- 本次新增:`_choice_layer_not_body` 加 `_CHOICE_LAYER_NOT_BODY_RE`,讓「驗收條款」「預期值表」的標題可以帶前綴記號、括號說明或冒號說明。
- 對不起來的地方:`_choice_plan_view` 的 `expected` 只認精確標題,卻用 `_choice_plan_sections` 去排除寬鬆標題。
- 後果:標題若是「T3 預期值表」或「預期值表(說明)」,正文會把它排除,`expected` 又讀不到它,內容兩邊都不出現在判讀材料裡。
- 專案現有規則:`_h2_section_lines` 的 docstring(`scripts/lumos:13973-13977`)明寫「找節邏輯不准長出第三套」。

標題比對規則因此有兩套各自演化。建議讓 `expected` 與正文排除共用同一個判斷。

審計修正紀錄那條規則同樣不跟 `_FOLD_AUDIT_RECORD_RE`(`scripts/lumos:69165`,錨在行首的 `##`、只認 `§數字` 前綴)共用。這點註解已承認是取捨,而且那支本來就是另一種用途,所以我只算附帶。

另有兩個小處對齊良好:旁檔路徑仍走 `_NOTE_AUDIT_WORK_DIR` 加 `_choice_layer_side`;介紹文字「只看這份材料」與 `scripts/lumos:81635` 的措辭一致。

severity: major
blocking: 是
引句:「exp = "\n".join(ln for _no, ln in _h2_section_lines(text, _EXPECTED_H2_RE) or [])」

這行引句不在 r4-repair.patch 裡,是從 `scripts/lumos:81150` 逐字複製的,屬審材外對照;補丁本身的對應引句是:

引句:「_CHOICE_LAYER_NOT_BODY_RE = re.compile(r"(?:\S+\s+)?(?:驗收條款|預期值表)\s*(?:[(（][^\n]*[)）]\s*|[:：][^\n]*)?")」

不對齊共 1 條,其中 major 1 條
