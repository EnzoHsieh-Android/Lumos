severity: clean

r2 的 F1、F2 兩條都照方向修好了。本輪新增的函式都走既有的圍欄與讀表判定,我沒找到第二種做法或跨層直呼。

**① 模組邊界**

沒有跨層直呼。所有新增都留在 `scripts/test_lumos.py` 的 t_kotlin_* 資料測試這一層;`check.py` 與型錄讀法沒被碰。

- 圍欄區段仍呼叫 `m._fence_regions`,對照 `configs/ast-grep/kotlin-android/check.py:239`。
- 檔頭改成用 `m._visible_lines` 找第一個圍欄外的 `## `,對照 `configs/ast-grep/kotlin-android/check.py:264`,不再手切字串。
- r2 F1 已修:T9、T11、T12 開頭都取自 `_kt_template_sections` 的組開頭段。`"\n## T9 "` 這類 `.index` 手切字串已消失。

引句:「first_h2 = next((no - 1 for no, ln in m._visible_lines(lines) if ln.startswith("## ")), len(lines))」

**② 命名與錯誤處理**

命名與錯誤處理跟既有一致。

- `_kt_t12_freeze_rows_problems`、`_kt_instr_records_problems` 都回傳問題字串清單,跟 `_kt_instr_template_problems`、`_kt_turbine_problems` 同形。
- 缺格、缺節的訊息格式與既有守衛相同。
- `_kt_template_sections` 多出的 `""` 鍵,現有消費端都不受影響。
  - `scripts/test_lumos.py:126878`、`scripts/test_lumos.py:126884` 的迴圈用 `name == "測試"` 與 `startswith("測試:")` 比對,`""` 不會命中。
  - `scripts/test_lumos.py:126890` 的矩陣檢查用 `startswith(("好寫法:", "壞寫法:"))`,也不會命中。
  - `t9.values()` 會多帶開頭段,但開頭段只是散文,不影響判定。

引句:「intro = t9.get("", "")」

**③ 第二種做法**

沒有另起一套。

- `_kt_lang_fences` 的圍欄區段取自 `m._fence_regions`,只在這一處取 info string 第一個字。
- r2 F2 已修:`_kt_kotlin_blocks` 縮成對 `_kt_fence_blocks(m, body, "kotlin")` 的薄包裝,凍結設定比對與改壞輔助 `_in_t12_fence` 也都走它,原本三份各寫一套的語言標籤取法收成一份。
- `_kt_t12_freeze_rows_problems` 與 `_kt_instr_records_problems` 讀表時用 `strip("|").split("|")` 切欄,這跟 `scripts/test_lumos.py:126890` 一帶既有的矩陣欄解析同一種寫法,不算新套路。
- `_kt_lang_fences` 只用嚴格模式,不像 `_visible_lines` 在圍欄沒關時退回寬鬆讀法。這點是原 `_kt_kotlin_blocks` 就有的行為,不是本輪新增。

引句:「return _kt_fence_blocks(m, body, "kotlin")」

不對齊共 0 條,其中會擋的 0 條。
